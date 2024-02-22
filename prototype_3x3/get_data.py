# Step 1: Upload the sketch in 'prototype_3x3.ino' to the Arduino
# Step 2: Run this Python script to continuously read data from the serial port and display through GUI object

import data_processor as data_processor

import serial
import time

import data_processor as dp

class DataFromSerial:
    def __init__(self, PORT: str) -> None:
        self.i = 0

        # Open serial communication
        self.serialcomm = serial.Serial(PORT)
        self.serialcomm.timeout = 1

        self.data_processor = dp.DataProcessor()
    
    def get_data(self) -> str:
        while(self.serialcomm.in_waiting == 0):
            time.sleep(0.1)

        data = self.serialcomm.read_all().decode('ascii')
        self.serialcomm.write(0b1) # Let the Arduino script know that everything has been read
        
        while(self.i < 5): # skip the first 5 iterations to ignore bad data
            time.sleep(.1)
            self.i += 1
            data = self.serialcomm.read_all().decode('ascii')
            self.serialcomm.write(0b1)

        return self.data_processor.processData(data)
    
    def close_serial(self):
        self.serialcomm.close()