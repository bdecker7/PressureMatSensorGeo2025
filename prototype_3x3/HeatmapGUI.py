import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import time
import threading

from DataFromSerial import DataFromSerial

class HeatmapGUI:
    def __init__(self, root: tk.Tk, data_getter: DataFromSerial):
        self.data_getter = data_getter
        self.vmin = 0
        self.vmax = 800

        # Initialize the main window
        self.root = root
        self.root.title("Heatmap GUI")
        
        # Create a Matplotlib figure and a subplot
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        # Create a Tkinter canvas widget to embed Matplotlib plot
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.fig.colorbar(self.ax.imshow(np.zeros((3, 3)), cmap='jet', interpolation='nearest',vmin=self.vmin, vmax=self.vmax))

        # Generate initial heatmap
        self.generate_heatmap()

        #self.update_interval = 0.01/2  # Update interval in seconds
        self.update_interval = 0.01  # Update interval in seconds
        self.paused = False

        # Create a separate thread for updating data
        self.data_thread = threading.Thread(target=self.update_data)
        self.data_thread.daemon = True  # Mark the thread as a daemon
        # (a daemon thread runs in the background and does not prevent the program from exiting)
        self.data_thread.start()

        # Create a button to pause/resume updates
        self.pause_button = tk.Button(root, text="Pause", command=self.toggle_pause)
        self.pause_button.pack()

    def generate_heatmap(self):
        # Generate sample data for the heatmap
        data = np.zeros((3, 3))
        # Clear the previous plot and display the new heatmap
        self.ax.clear()
        self.ax.imshow(data, cmap='jet', interpolation='nearest')
        self.canvas.draw()

    def update_data(self):
        # Continuously update data while the program is running
        while True:
            # Check if the update is not paused
            if not self.paused:
                # Generate new random data for the heatmap
                #new_data = np.random.rand(10, 10)

                new_data = self.data_getter.get_data()

                # Clear the previous plot and display the new heatmap
                self.ax.clear()
                self.ax.imshow(new_data, cmap='jet', interpolation='nearest',vmin=self.vmin, vmax=self.vmax)
                self.canvas.draw()
            # Wait for the specified update interval
            time.sleep(self.update_interval)

    def toggle_pause(self):
        # Toggle the pause state of the updates
        self.paused = not self.paused
        # Change the text of the button based on the pause state
        if self.paused:
            self.pause_button.config(text="Resume")
        else:
            self.pause_button.config(text="Pause")