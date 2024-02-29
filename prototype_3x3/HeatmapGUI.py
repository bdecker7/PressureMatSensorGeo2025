import tkinter as tk
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import time
import threading

from DataFromSerial import DataFromSerial

UPDATE_INTERVAL = 0.01 / 2  # Update interval in seconds
HEATMAP_SIZE = (3, 3)  # Size of the heatmap

class HeatmapGUI:
    """GUI for displaying a heatmap based on data from a serial port."""

    def __init__(self, root, data_getter=None, vmin=0, vmax=1024):
        if data_getter is None:
            self.debug_mode = True
        else:
            self.debug_mode = False
            self.data_getter = data_getter
        
        # Set up the heatmap
        self.root = root # Tkinter root
        self.vmin = vmin # Minimum value for the heatmap
        self.vmax = vmax # Maximum value for the heatmap

        # Set up the GUI
        self.fig, self.ax = plt.subplots()
        self.setup_gui()

        # Start the data update thread
        self.paused = False
        self.data_thread = threading.Thread(target=self.update_data)
        self.data_thread.daemon = True
        self.data_thread.start()

        # Set up the click event
        self.clicked_coords = None
        self.clicked_value_label = tk.Label(self.root)
        self.clicked_value_label.pack()
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)

    def setup_gui(self):
        """Set up the GUI components."""
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.fig.colorbar(self.ax.imshow(np.zeros(HEATMAP_SIZE), cmap='jet', interpolation='nearest', vmin=self.vmin, vmax=self.vmax))
        self.generate_initial_heatmap()
        self.pause_button = tk.Button(self.root, text="Pause", command=self.toggle_pause)
        self.pause_button.pack()

    def generate_initial_heatmap(self):
        """Generate the initial heatmap."""
        data = np.zeros(HEATMAP_SIZE)
        self.ax.clear()
        self.ax.imshow(data, cmap='jet', interpolation='nearest')
        self.canvas.draw()

    def update_data(self):
        """Continuously update the heatmap with new data."""
        while True:
            if not self.paused:
                if self.debug_mode:
                    new_data = np.random.randint(self.vmin, self.vmax, size=HEATMAP_SIZE)
                else:
                    new_data = self.data_getter.get_data()
                self.ax.clear()
                self.ax.imshow(new_data, cmap='jet', interpolation='nearest', vmin=self.vmin, vmax=self.vmax)
                self.canvas.draw()
                if self.clicked_coords:
                    clicked_value = new_data[self.clicked_coords]
                    self.clicked_value_label.config(text=f"Value at {self.clicked_coords}: {clicked_value}")
            time.sleep(UPDATE_INTERVAL)

    def toggle_pause(self):
        # Toggle the pause state of the updates
        self.paused = not self.paused
        # Change the text of the button based on the pause state
        if self.paused:
            self.pause_button.config(text="Resume")
        else:
            self.pause_button.config(text="Pause")
    
    def on_click(self, event):
        """Handle click events on the heatmap."""
        self.clicked_coords = (int(round(event.ydata)), int(round(event.xdata)))

if __name__ == "__main__":
    root = tk.Tk() # create main Tkinter window
    app = HeatmapGUI(root) # initialize heatmap in main window
    root.mainloop() # Start the Tkinter event loop