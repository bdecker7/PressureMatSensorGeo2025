from email.errors import HeaderMissingRequiredValue
import tkinter as tk
import tkinter.ttk as ttk # themed Tkinter
from tkinter import Tk, messagebox
from tkinter import filedialog
from PIL import Image, ImageTk
from scipy.ndimage import zoom
from matplotlib import cm # colormaps
import numpy as np
import time
import threading
import os

from DataFromSerial import DataFromSerial

# UPDATE_INTERVAL = 0.01 / 2  # Update interval in seconds
UPDATE_INTERVAL = 0
HEATMAP_SIZE = (16, 16)  # Size of the heatmap

class HeatmapGUI:
    """GUI for displaying a heatmap based on data from a serial port."""

    def __init__(self, root: Tk, data_getter: DataFromSerial | None = None, vmin=0, vmax=1023):
        if data_getter is None:
            self.debug_mode = True
            # vmin=0
            # vmax=2
        else:
            self.debug_mode = False
            self.data_getter = data_getter
        
        # Save the input values
        self.root = root # Tkinter root
        self.vmin = vmin # Minimum value for the heatmap
        self.vmax = vmax # Maximum value for the heatmap

        # Set up the GUI
        self.setup_gui()
        self.heatmap_canvas.bind("<Configure>", self.on_resize)

        # Choose GUI visual style
        # call ttk.Style().theme_names() to get a list of available themes
        s = ttk.Style()
        s.theme_use('vista')

        # Initialize variables
        self.paused = False
        self.record_mode = False
        self.recorded_data = np.zeros((0, 4))
        self.record_start_time = 0
        self.folder_path = None

        # Start the data update thread
        self.data_thread = threading.Thread(target=self.gui_update_loop)
        self.data_thread.daemon = True
        self.threading_lock = threading.Lock()
        self.data_thread.start()

    def start(self):
        self.root.mainloop()

    """ GUI Setup (create the visual GUI components) """

    def setup_gui(self):
        """Set up the GUI components."""
        self.root.title("GEO Pressure Mat")  # Set the title of the window
        self.root.configure(bg='dimgrey')

        # Create a frame for the heatmap
        # self.main_frame = tk.Frame(self.root, bg="dimgrey", border=0, relief=tk.FLAT)
        self.main_frame = ttk.Frame(self.root, style='TFrame', border=0, relief=tk.FLAT)
        self.main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.build_gui_frame_heatmap()
        self.build_gui_sidebar()

        # Handle window closing event to properly terminate the program
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Set up the window size
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = int(screen_width * 2 / 3)
        window_height = int(screen_height * 2 / 3)
        self.root.geometry(f"{window_width}x{window_height}")
    
    def build_gui_frame_heatmap(self):
        # Build a canvas for the heatmap, to hold the heatmap canvas and a legend/colorbar for the heatmap

        # Create a canvas for the heatmap, this is where the heatmap is actually drawn
        self.heatmap_canvas: tk.Canvas = tk.Canvas(self.main_frame, bg="dimgrey", border=0, relief=tk.FLAT)
        self.heatmap_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    def build_gui_sidebar(self):
        # Create a sidebar frame
        self.sidebar = ttk.Frame(self.main_frame, style='TFrame', border=0, relief=tk.FLAT, width=200)
        self.sidebar.pack(side=tk.RIGHT)

        # Create a pause button that dyanmically changes size based on the window size
        self.pause_button = ttk.Button(self.sidebar, text="Pause", style='TButton', command=self.toggle_pause, width=10)
        self.pause_button.pack(side=tk.TOP)  # Pack the pause button

        # Add space for displaying statistics
        self.build_gui_frame_stats()

        # Create a frame for data recording, saving, and exporting (inside the sidebar)
        self.build_gui_frame_record_export()

        # Create a frame for holding a "zoom" slider (inside the sidebar)
        self.build_gui_frame_zoom()

    def build_gui_frame_stats(self):
        # Create a frame for related stats (inside the sidebar)
        self.stats_frame = ttk.Frame(self.sidebar, style='TFrame', border=0, relief=tk.FLAT)
        self.stats_frame.pack(side=tk.TOP)
        self.data_label = ttk.Label(self.stats_frame, text="Stats:", style='TLabel', font=("Arial", 14, "bold"))
        self.data_label.pack()
        self.stats_text_box = tk.Text(self.stats_frame, height=5, width=10, bg="dimgrey", fg="white")
        self.stats_text_box.pack()

    def build_gui_frame_record_export(self):
        self.record_frame = ttk.Frame(self.sidebar, style='TFrame', border=0, relief=tk.FLAT)
        self.record_frame.pack(side=tk.TOP)
        self.export_label = ttk.Label(self.record_frame, text="Save and Export:", style='TLabel')
        self.export_label.pack()

        # Create a record button and timer
        self.record_button = ttk.Button(self.record_frame, text="Record Data", command=self.toggle_record)
        self.record_button.pack()  # Pack the record button
        self.record_time_display = ttk.Label(self.record_frame, text="Time: 0:00", style='TLabel')
        self.record_time_display.pack()  # Pack the record time display

        # Create an export button
        self.export_button = ttk.Button(self.record_frame, text="Export Data", command=self.export_data)
        self.export_button.pack()  # Pack the export button
    
    def build_gui_frame_zoom(self):
        # Create a frame for the zoom slider (inside the sidebar)
        self.zoom_frame = ttk.Frame(self.sidebar, style='TFrame', border=0, relief=tk.FLAT)
        self.zoom_frame.pack(side=tk.TOP)
        self.zoom_label = ttk.Label(self.zoom_frame, text="Zoom:", style='TLabel')
        self.zoom_label.pack()
        self.zoom_slider = ttk.Scale(self.zoom_frame, from_=0, to=20, orient=tk.HORIZONTAL, style='TScale')
        self.zoom_slider.pack()

        # Connect the zoom slider to a function that changes the zoom level
        self.zoom_slider.bind("<ButtonRelease-1>", self.change_zoom)

    """ GUI Update Loop (running in background thread) """

    def gui_update_loop(self):
        """Continuously update the GUI with new data."""
        while True:
            if not self.paused:
                # Get updated data
                if self.debug_mode:
                    data = self.get_simulated_data()
                else:
                    data = self.data_getter.get_data()
                
                # Save the data, ensuring that no other thread (including the main thread) is accessing it during the update
                with self.threading_lock: 
                    self.data = data

                # get stats and record if applicable
                self.get_stats()
                if self.record_mode:
                    self.record_stats()
                    record_time = time.time() - self.record_start_time
                    self.record_time_display.config(text=f"Time: {record_time:.2f}")

                # Update the display
                self.draw_heatmap()
                self.display_stats() 

            time.sleep(UPDATE_INTERVAL)

    def draw_heatmap(self, canvas_resized: bool = False):      
        # The heatmap image starts out as a copy of the data
        heatmap_image: np.ndarray = self.data.copy()

        # Interpolate the data to smooth it out (make the heatmap image have smoother transitions)
        zoom_factor = 4 # determines the degree of interpolation
        heatmap_image = zoom(heatmap_image, zoom_factor, order=3, mode='nearest') # order=3 is cubic interpolation
        # heatmap_image = np.clip(heatmap_image, self.vmin, self.vmax) # clip the values to the min and max (to avoid out-of-range values)

        # Convert the data into RGB colors based on its value
        heatmap_image = heatmap_image / (self.vmax - self.vmin) * 255 # Scale the data to 0-255
        heatmap_image = np.repeat(heatmap_image[:, :, np.newaxis], 3, axis=2) # Create 3 RGB channels
        heatmap_image[:, :, 0] = np.where(heatmap_image[:, :, 0] <= 127, 0, 2*heatmap_image[:, :, 0] - 255) # red channel: 0's until 127, then linear ramp from 0 to 255
        heatmap_image[:, :, 1] = np.zeros_like(heatmap_image[:, :, 1]) # set the green channel to 0
        heatmap_image[:, :, 2] = 255 - 2*np.abs(heatmap_image[:, :, 2] - 127) # blue channel: a triangle function where 0 -> 0 | 127 -> 255 | 255 -> 0

        # heatmap_image[0, 0] = [255, 0, 0] # highlight the top-left corner for debugging
        
        # Calculate the width and height (in pixels) of each cell in the heatmap
        rows, cols = heatmap_image.shape[:2]
        cell_width_pixels = int(self.heatmap_canvas.winfo_width() / cols)
        cell_height_pixels = int(self.heatmap_canvas.winfo_height() / rows)

        if cell_width_pixels == 0 or cell_height_pixels == 0:
            return # On the first iteration the canvas size is sometimes 0, so skip drawing in that case to avoid errors
        
        # Scale the data to the size of the heatmap canvas in pixels by repeating the values
        heatmap_image = np.repeat(heatmap_image, cell_width_pixels, axis=1)
        heatmap_image = np.repeat(heatmap_image, cell_height_pixels, axis=0)
        heatmap_image = np.ascontiguousarray(heatmap_image) # make it a C-contiguous array for faster drawing
        heatmap_image = heatmap_image.astype(np.uint8)

        # Convert the numpy array to a Tkinter PhotoImage
        pil_image = Image.fromarray(heatmap_image)

        if not hasattr(self, 'heatmap_photo') or canvas_resized: # first time or when canvas is resized, create the image
            self.heatmap_photo = ImageTk.PhotoImage(pil_image)
            self.heatmap_image_id = self.heatmap_canvas.create_image(0, 0, image=self.heatmap_photo, anchor=tk.NW)
        else: # update the image (updating this way rather than re-creating it is faster and eliminates flickering)
            self.heatmap_photo.paste(pil_image)
            self.heatmap_canvas.coords(self.heatmap_image_id, (0, 0))

    def get_simulated_data(self):
        """Generate debug (fake) data for the heatmap."""
        data = np.zeros(HEATMAP_SIZE)
        # Generate a heatmap based on a sine wave
        for i in range(HEATMAP_SIZE[0]):
            for j in range(HEATMAP_SIZE[1]):
                data[i][j] = np.abs( np.sin(2 * np.pi * (j + 1/2) / HEATMAP_SIZE[0]) 
                              * np.sin(np.pi * (i + 1/2) / HEATMAP_SIZE[1]) 
                              * np.sin(time.time()) ) * 1023
        return data

    def get_stats(self):
        """Display the mean, standard deviation, min, and max of the heatmap data."""
        self.mean = np.abs(np.mean(self.data))
        self.std = np.std(self.data)
        self.min_val = np.min(self.data)
        self.max_val = np.max(self.data)
    
    def display_stats(self):
        """Display the mean, standard deviation, min, and max of the heatmap data."""
        # Display the stats in the text box
        self.stats_text_box.delete(1.0, tk.END)
        self.stats_text_box.insert(tk.END, f"Ave: {self.mean:.2f}\n")
        self.stats_text_box.insert(tk.END, f"Std: {self.std:.2f}\n")
        self.stats_text_box.insert(tk.END, f"Min: {self.min_val:.2f}\n")
        self.stats_text_box.insert(tk.END, f"Max: {self.max_val:.2f}\n")

    """ Event handlers """

    def toggle_pause(self):
        # Toggle the pause state of the updates
        self.paused = not self.paused
        # Change the text of the button based on the pause state
        if self.paused:
            self.pause_button.config(text="Resume")
        else:
            self.pause_button.config(text="Pause")
    
    def on_close(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.quit()
    
    def on_resize(self, event):
        self.draw_heatmap(canvas_resized=True)

    def toggle_record(self):
        self.record_mode = not self.record_mode
        if self.record_mode:
            self.recorded_data = np.zeros((0, 4)) # Reset the recorded data
            self.record_start_time = time.time();
            self.record_button.config(text="Stop Recording")
        else:
            self.record_button.config(text="Record")

    def record_stats(self):
        # Append the stats to the recorded data numpy array
        new_data = np.array([[self.mean, self.std, self.min_val, self.max_val]])
        self.recorded_data = np.append(self.recorded_data, new_data, axis=0)
    
    def export_data(self):
        folder_path = filedialog.askdirectory()
        # Save the recorded data to a CSV file with the current timestamp as name
        file_name = f"recorded_data_{time.strftime('%Y%m%d_%H%M%S')}.csv"
        file_path = os.path.join(folder_path, file_name)
        np.savetxt(file_path, self.recorded_data, delimiter=",")
        messagebox.showinfo("Export Successful", f"Data exported to {file_path}")
    def change_zoom(self, event):
        # Change the size of text in the sidebar based on the zoom level
        self.zoom_level = int(self.zoom_slider.get())
        self.font_size = 14 + self.zoom_level
        self.data_label.config(font=("Arial", self.font_size, "bold"))
        self.export_label.config(font=("Arial", self.font_size, "bold"))
        self.zoom_label.config(font=("Arial", self.font_size, "bold"))
        self.record_time_display.config(font=("Arial", self.font_size, "bold"))
        self.stats_text_box.config(font=("Arial", self.font_size, "bold"))

if __name__ == "__main__":
    root = tk.Tk() # create main Tkinter window
    app = HeatmapGUI(root) # initialize heatmap in main window (in debug mode because no data getter is provided)
    app.start() # start the Tkinter main loop