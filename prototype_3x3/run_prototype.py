# Step 1: Upload the sketch in 'prototype_3x3.ino' to the Arduino
# Step 2: Run this Python script to continuously read data from the serial port and display through GUI object

import prototype_3x3.data_processor as data_processor
import gui

import serial


PORT = "COM4" # The port from which Arduino data should be read

data_processor = data_processor.DataProcessor()
gui = gui.gui()

# Open serial communication
serialcomm = serial.Serial(PORT, 9600, timeout=None)
serialcomm = serial.Serial(PORT)
serialcomm.timeout = 1



# Close serial communication
serialcomm.close()