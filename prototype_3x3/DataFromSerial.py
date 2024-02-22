import serial
import serial.tools.list_ports
import time

import DataProcessor as dp

class DataFromSerial:
    def __init__(self) -> None:
        self.i = 0

        #self.serial_port = self.find_serial_port()
        self.serial_port = "COM7" # Change this to the port of your Arduino
        # Open serial communication
        self.serialcomm = serial.Serial(self.serial_port)
        time.sleep(.01)
        if (self.serialcomm.isOpen() == False):
            print("Serial port not open")
            raise Exception("Serial port not open")
        self.serialcomm.timeout = 1

        self.data_processor = dp.DataProcessor()
    
    def get_data(self) -> str:
        while(self.serialcomm.in_waiting == 0):
            time.sleep(0.1)

        data = self.serialcomm.read_all()
        dataString = data.decode('ascii')
        self.serialcomm.write(b'\x01') # Let the Arduino script know that everything has been read
        
        while(self.i < 5): # skip the first 5 iterations to ignore bad data
            time.sleep(.1)
            self.i += 1
            data = self.serialcomm.read_all()
            dataString = data.decode('ascii')
            self.serialcomm.write(b'\x01')

        try:
            return self.data_processor.processData(dataString.rstrip('\n\r'))
        except Exception as e:
            print("Error processing data: ", e)
            data = self.serialcomm.read_all()
            dataString = data.decode('ascii')
            self.serialcomm.write(b'\x01')
            return self.data_processor.processData(dataString.rstrip('\n\r'))
    
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
    print(DataFromSerial.find_serial_port()) # Test the find_serial_port method

    