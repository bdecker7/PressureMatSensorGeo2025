import serial
import serial.tools.list_ports
import time
import numpy as np

import DataProcessor as dp

class DataFromSerial:
    def __init__(self):
        self.i = 0

        #self.serial_port = self.find_serial_port()
        self.serial_port = "COM10" # Change this to the port of your Arduino
        # Open serial communication
        self.serialcomm = serial.Serial(self.serial_port, baudrate=115200)
        time.sleep(.01)
        if (self.serialcomm.is_open == False):
            print("Serial port not open")
            raise Exception("Serial port not open")

        # Wait for the Arduino to be ready before sending anything
        while self.serialcomm.read(1) != b'\x01': pass
        self.data_processor = dp.DataProcessor()
        
       
    def read_uint16(self) -> int:
        vals: bytes = self.serialcomm.read(2) # read two bytes of binary data
        value = int.from_bytes(vals, 'little') # convert the bytes to an integer
        return value
      

    def read_int_array(self) -> np.ndarray:
        rows: int = self.read_uint16() # read the number of rows
        cols: int = self.read_uint16() # read the number of columns
        vals: bytes = self.serialcomm.read(rows * cols * 2) # read all data
        
        # iterate over the vals and fill the data array
        data: np.ndarray = np.zeros((rows, cols), dtype=int)
        for i in range(0, len(vals), 2):
            row: int = i // (cols * 2)
            col: int = (i // 2) % cols
            data[row, col] = int.from_bytes(vals[i:i+2], 'little')
        return data
    

    def get_data(self) -> np.ndarray:
        # Request data from the Arduino by sending a '1' byte
        self.serialcomm.write(b'\x01')

        # Get the raw data from the Arduino
        raw_data: np.ndarray = self.read_int_array()
        # print(raw_data)
        return raw_data
        
        # FIXME: Process the raw data using the data processor:
        raw_data = raw_data/1024*5
        return self.data_processor.processData(raw_data)
        '''except Exception as e:
            print("Error processing data: ", e, "Data: ", dataString, "End of data")
            data = self.serialcomm.read_all()
            dataString = data.decode('ascii')
            self.serialcomm.write(b'\x01')
            return self.data_processor.processData(dataString.rstrip('\n\r'))'''
    

    def close_serial(self):
        self.serialcomm.close()


    def find_serial_port(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if "Arduino" in port.description:  # Modify this condition based on your device's description
                return port.device
        port = input("No port found. Enter name of COM port (e.g. \"COM3\"):")
        return port


if __name__ == "__main__":
    # Debug mode: 
    # continuously print data from the serial port as a simple array in the terminal
    data_getter = DataFromSerial()
    while True:
        print(data_getter.get_data())
        time.sleep(.1)

    