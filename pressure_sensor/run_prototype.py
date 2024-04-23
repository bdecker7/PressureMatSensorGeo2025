# Step 1: Upload the sketch in 'prototype_3x3.ino' to the Arduino
# Step 2: Run this Python script to continuously read data from the serial port and display through GUI object

import prototype_3x3.DataProcessor as DataProcessor
import prototype_3x3.HeatmapGUI as HeatmapGUI

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

DataProcessor = DataProcessor.DataProcessor(PORT)
HeatmapGUI = HeatmapGUI.Gui()

while(1):
    if (serialcomm.in_waiting > 0):
        time.sleep(.1)
        string = serialcomm.read_all()
        serialcomm.write(0b1) # Let the Arduino script know that 
        var_decoded = string.decode('ascii')
        
        while(i < 5): # skip the first 5 iterations to ignore bad data
            time.sleep(.1)
            i += 1
            string = serialcomm.read_all()
            serialcomm.write(0b1)

        var_decoded = string.decode('ascii')
        
        data = DataProcessor.stringToIntArray(var_decoded)
        HeatmapGUI.update_heated_map(data)

# Close serial communication
serialcomm.close()