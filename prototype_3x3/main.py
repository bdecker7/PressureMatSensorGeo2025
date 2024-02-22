import gui
import get_data

import tkinter as tk

if __name__ == "__main__":
    data_getter = get_data.DataFromSerial('COM7')
    root = tk.Tk() # create main Tkinter window
    app = gui.HeatmapGUI(root, data_getter) # initialize heatmap in main window
    root.mainloop() # Start the Tkinter event loop