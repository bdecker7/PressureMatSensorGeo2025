import serial
import numpy as np
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

## FIXME: Add a functionality to display max pressure in a given monment, as well as data storage for finding averages over time

# Set up the serial port (change 'COMX' to the correct port for your Arduino)
ser = serial.Serial('COM3', 9600, timeout=None)

# Create a function to update the heatmap
def update_heatmap():
    heatmap_data = np.zeros((3, 3))
    line = ser.readline().decode('utf-8')
    sensor_value = float(line.strip())
    heatmap_data[5,5] = float(sensor_value)
    heatmap.set_array(heatmap_data)
    canvas.draw()
    root.after(5, update_heatmap)

# Create a function to close the GUI
def close_gui():
    root.quit()

# Create a function to display the value of the clicked square
def on_click(event):
    if event.button == 1:
        x, y = event.xdata, event.ydata
        if x is not None and y is not None:
            value = heatmap.get_array()[int(y), int(x)]
            value_label.config(text=f"Value: {value}")

# Create the Tkinter window
root = tk.Tk()
root.title("Heatmap GUI")

window_width = 1020
window_height = 720
root.geometry(f"{window_width}x{window_height}")

# Specify the percentage of the window that the Matplotlib figure should fill
figure_percentage_width = 90  # Adjust as needed
figure_percentage_height = 90  # Adjust as needed

# Calculate the size of the figure in inches
figure_width = (figure_percentage_width / 100) * window_width / 100
figure_height = (figure_percentage_height / 100) * window_height / 100

title = tk.Label(root, text="Heatmap GUI", font=("Helvetica", 16))
title.pack()

# Create a Matplotlib figure and attach it to Tkinter
fig = Figure(figsize=(figure_width, figure_height), dpi=100)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

# Create a heatmap plot
ax = fig.add_subplot(111)
heatmap = ax.matshow(np.zeros((10, 10)), cmap='jet', vmin=0, vmax=600)

# Add a colorbar
fig.colorbar(heatmap)

# Create a "Quit" button
quit_button = tk.Button(root, text="Quit", command=close_gui)
quit_button.pack()

# Create a label to display the value of the clicked square
value_label = tk.Label(root, text="Value: ")
value_label.pack()

# Bind the click event to the heatmap plot
canvas.mpl_connect('button_press_event', on_click)

# Start the initial heatmap update
update_heatmap()

# Start the Tkinter main loop
root.mainloop()

