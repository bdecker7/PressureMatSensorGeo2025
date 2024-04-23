import HeatmapGUI as HeatmapGUI
import DataFromSerial as DataFromSerial

import tkinter as tk

if __name__ == "__main__":
    data_getter = DataFromSerial.DataFromSerial()
    root = tk.Tk() # create main Tkinter window
    app = HeatmapGUI.HeatmapGUI(root, data_getter) # initialize heatmap in main window
    root.mainloop() # Start the Tkinter event loop