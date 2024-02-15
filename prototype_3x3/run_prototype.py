# Step 1: Upload the sketch in 'prototype_3x3.ino' to the Arduino
# Step 2: Run this Python script to continuously read data from the serial port and display through GUI object

import data_processor as data_processor
import gui

import serial
import time
import numpy as np


PORT = 'COM7' # The port from which Arduino data should be read

rows = 3
cols = 3
i = 0

# Open serial communication
serialcomm = serial.Serial(PORT)
serialcomm.timeout = 1

data_processor = data_processor.DataProcessor(PORT)
gui = gui.Gui()

while(1):
    if (serialcomm.in_waiting > 0):
        time.sleep(.1)
        string = serialcomm.read_all()
        serialcomm.write(0b1)
        var_decoded = string.decode('ascii')
        
        while(i < 5): # skip the first 5 iterations to ignore bad data
            time.sleep(.1)
            i += 1
            string = serialcomm.read_all()
            serialcomm.write(0b1)

        var_decoded = string.decode('ascii')
        print(var_decoded)
        
        data = data_processor.parseStringToInt(var_decoded)
    

# Close serial communication
serialcomm.close()