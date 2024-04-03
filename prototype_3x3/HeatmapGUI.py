import tkinter as tk
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import time
import threading
import os

from DataFromSerial import DataFromSerial

UPDATE_INTERVAL = 0.01 / 2  # Update interval in seconds
HEATMAP_SIZE = (16, 16)  # Size of the heatmap

class HeatmapGUI:
    """GUI for displaying a heatmap based on data from a serial port."""

    def __init__(self, root, data_getter=None, vmin=0, vmax=850):
        if data_getter is None:
            self.debug_mode = True
            vmin=-1
            vmax=1
        else:
            self.debug_mode = False
            self.data_getter = data_getter
        
        # Save the input values
        self.root = root # Tkinter root
        self.vmin = vmin # Minimum value for the heatmap
        self.vmax = vmax # Maximum value for the heatmap

        # Set up the GUI
        self.setup_gui()

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

    def setup_gui(self):
        """Set up the GUI components."""
        self.root.title("GEO Pressure Mat")  # Set the title of the window
        self.root.configure(bg='dimgrey')

        # Create a frame for the heatmap
        self.main_frame = tk.Frame(self.root, bg="dimgrey", border=0, relief=tk.FLAT)
        self.main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.build_gui_heatmap()
        self.build_gui_sidebar()

        # Handle window closing event to properly terminate the program
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Set up the window size
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = int(screen_width * 2 / 3)
        window_height = int(screen_height * 2 / 3)
        self.root.geometry(f"{window_width}x{window_height}")
    
    def build_gui_heatmap(self):
        # Create a Matplotlib figure and axis
        self.fig, self.ax = plt.subplots()  # Create a Matplotlib figure and axis
        self.fig.patch.set_facecolor('dimgrey')  # Set the background color of the figure
        self.ax.tick_params(axis='x', colors='white')  # Set the x-axis tick color to white
        self.ax.tick_params(axis='y', colors='white')  # Set the y-axis tick color to white
        self.plot_frame = tk.Frame(self.main_frame, bg="dimgrey")  # Create a frame for the plot

        # Create a Tkinter canvas using the Matplotlib figure
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_frame)
        self.canvas_widget = self.canvas.get_tk_widget()  # Get the Tkinter widget from the canvas
        self.canvas_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)  # Pack the Tkinter widget

        # Add a colorbar to the heatmap
        self.colorbar = self.ax.imshow(np.zeros(HEATMAP_SIZE), cmap='jet', interpolation='nearest',
                      vmin=self.vmin, vmax=self.vmax)
        self.colorbar.colorbar = self.fig.colorbar(self.colorbar)
        self.colorbar.colorbar.ax.tick_params(axis='y', colors='white')
        self.colorbar.colorbar.ax.yaxis.set_tick_params(color='white')

    def build_gui_sidebar(self):
        # Create a sidebar frame
        self.sidebar = tk.Frame(self.main_frame, bg="dimgrey", border=0, relief=tk.FLAT, width=200)
        self.sidebar.pack(side=tk.RIGHT)

        # Create a pause button
        self.pause_button = tk.Button(self.sidebar, text="Pause", font=("Arial", 14, "bold"), command=self.toggle_pause,
                                      bg="dimgrey", fg="white")
        self.pause_button.pack(side=tk.TOP)  # Pack the pause button

        # Set up the click event
        self.clicked_coords = None
        self.clicked_value_label = tk.Label(self.sidebar, bg="dimgrey", fg="white")
        self.clicked_value_label.pack(side=tk.TOP)
        self.fig.canvas.mpl_connect('button_press_event', self.on_heatmap_click)

        # Add space for displaying statistics
        self.build_gui_frame_stats()

        # Create a frame for data recording, saving, and exporting (inside the sidebar)
        self.build_gui_frame_record_export()

        # Create a frame for holding a "zoom" slider (inside the sidebar)
        self.build_gui_frame_zoom()

    def build_gui_frame_stats(self):
        # Create a frame for related stats (inside the sidebar)
        self.stats_frame = tk.Frame(self.sidebar, bg="dimgrey", border=0, relief=tk.FLAT)
        self.stats_frame.pack(side=tk.TOP)
        self.data_label = tk.Label(self.stats_frame, text="Stats:", font=("Arial", 14, "bold"), bg="dimgrey", fg="white")
        self.data_label.pack()
        self.stats_text_box = tk.Text(self.stats_frame, height=5, width=10, bg="dimgrey", fg="white")
        self.stats_text_box.pack()

    def build_gui_frame_record_export(self):
        self.record_frame = tk.Frame(self.sidebar, bg="dimgrey", border=0, relief=tk.FLAT)
        self.record_frame.pack(side=tk.TOP)
        self.export_label = tk.Label(self.record_frame, text="Save and Export:", font=("Arial", 14, "bold"),
                                     bg="dimgrey", fg="white")
        self.export_label.pack()

        # Create a record button and timer
        self.record_button = tk.Button(self.record_frame, text="Record Data", command=self.toggle_record,
                                       bg="dimgrey", fg="white")
        self.record_button.pack()  # Pack the record button
        self.record_time_display = tk.Label(self.record_frame, text="Time: 0:00", bg="dimgrey", fg="white")
        self.record_time_display.pack()  # Pack the record time display

        # Create an export button
        self.export_button = tk.Button(self.record_frame, text="Export Data", command=self.export_data,
                                       bg="dimgrey", fg="white")
        self.export_button.pack()  # Pack the export button
    
    def build_gui_frame_zoom(self):
        # Create a frame for the zoom slider (inside the sidebar)
        self.zoom_frame = tk.Frame(self.sidebar, bg="dimgrey", border=0, relief=tk.FLAT)
        self.zoom_frame.pack(side=tk.TOP)
        self.zoom_label = tk.Label(self.zoom_frame, text="Zoom:", font=("Arial", 14, "bold"), bg="dimgrey", fg="white")
        self.zoom_label.pack()
        self.zoom_slider = tk.Scale(self.zoom_frame, from_=0, to=10, orient=tk.HORIZONTAL, bg="dimgrey", fg="white")
        self.zoom_slider.pack()

        # Connect the zoom slider to a function that changes the zoom level
        self.zoom_slider.bind("<ButtonRelease-1>", self.change_zoom)
    
    def change_zoom(self, event):
        # Change the size of text in the sidebar based on the zoom level
        self.zoom_level = self.zoom_slider.get()
        self.font_size = 14 + self.zoom_level
        self.data_label.config(font=("Arial", self.font_size, "bold"))
        self.export_label.config(font=("Arial", self.font_size, "bold"))
        self.zoom_label.config(font=("Arial", self.font_size, "bold"))
        self.clicked_value_label.config(font=("Arial", self.font_size, "bold"))
        self.record_button.config(font=("Arial", self.font_size, "bold"))
        self.export_button.config(font=("Arial", self.font_size, "bold"))
        self.pause_button.config(font=("Arial", self.font_size, "bold"))
        self.record_time_display.config(font=("Arial", self.font_size, "bold"))
        self.stats_text_box.config(font=("Arial", self.font_size, "bold"))

        # Change the size of the text axis labels on the heatmap based on the zoom level
        self.ax.tick_params(axis='x', labelsize=self.font_size - 2)
        self.ax.tick_params(axis='y', labelsize=self.font_size - 2)
        self.colorbar.colorbar.ax.yaxis.set_tick_params(labelsize=self.font_size - 2)
        self.canvas.draw()

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
                self.display_heatmap()
                self.display_coords()
                self.display_stats() 

            time.sleep(UPDATE_INTERVAL)

    def display_coords(self):
        if self.clicked_coords:
            clicked_value = self.data[self.clicked_coords]
            self.clicked_value_label.config(text=f"Value at {self.clicked_coords}: {clicked_value:.2f}")

    def display_heatmap(self):
        self.ax.clear()
        self.ax.imshow(self.data, cmap='jet', interpolation='nearest', vmin=self.vmin, vmax=self.vmax)
        self.canvas.draw()

    def toggle_pause(self):
        # Toggle the pause state of the updates
        self.paused = not self.paused
        # Change the text of the button based on the pause state
        if self.paused:
            self.pause_button.config(text="Resume")
        else:
            self.pause_button.config(text="Pause")
    
    def on_heatmap_click(self, event):
        """Handle click events on the heatmap."""
        self.clicked_coords = (int(round(event.ydata)), int(round(event.xdata)))
    
    def get_simulated_data(self):
        """Generate debug (fake) data for the heatmap."""
        data = np.zeros(HEATMAP_SIZE)
        # Generate a heatmap based on a sine wave
        for i in range(HEATMAP_SIZE[0]):
            for j in range(HEATMAP_SIZE[1]):
                data[i][j] = ( np.sin(2 * np.pi * j / HEATMAP_SIZE[0]) 
                              * np.sin(np.pi * i / HEATMAP_SIZE[1]) 
                              * np.sin(time.time()) )
        return data
    
    def on_close(self):
        if tk.messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.quit()
    
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
        self.stats_text_box.insert(tk.END, f"Mean: {self.mean:.2f}\n")
        self.stats_text_box.insert(tk.END, f"Std: {self.std:.2f}\n")
        self.stats_text_box.insert(tk.END, f"Min: {self.min_val:.2f}\n")
        self.stats_text_box.insert(tk.END, f"Max: {self.max_val:.2f}\n")

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
        folder_path = tk.filedialog.askdirectory()
        # Save the recorded data to a CSV file with the current timestamp as name
        file_name = f"recorded_data_{time.strftime('%Y%m%d_%H%M%S')}.csv"
        file_path = os.path.join(folder_path, file_name)
        np.savetxt(file_path, self.recorded_data, delimiter=",")
        tk.messagebox.showinfo("Export Successful", f"Data exported to {file_path}")
    
if __name__ == "__main__":
    root = tk.Tk() # create main Tkinter window
    app = HeatmapGUI(root) # initialize heatmap in main window (in debug mode because no data getter is provided)
    app.start() # start the Tkinter main loop