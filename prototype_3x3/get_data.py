import serial
import serial.tools.list_ports
import time

import data_processor as dp

class DataFromSerial:
    def __init__(self, PORT: str) -> None:
        self.i = 0

        self.serial_port = self.find_serial_port()
        # Open serial communication
        self.serialcomm = serial.Serial(PORT)
        time.sleep(.01)
        if (self.serialcomm.isOpen() == False):
            print("Serial port not open")
            raise Exception("Serial port not open")
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

    def find_serial_port():
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if "Arduino" in port.description:  # Modify this condition based on your device's description
                return port.device
        return None  # Device not found
    
if __name__ == "__main__":
    print(DataFromSerial.find_serial_port()) # Test the find_serial_port method

    