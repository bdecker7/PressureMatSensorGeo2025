"""
This class defines variables and methods to organize, 
"""

import numpy as np

class DataProcessor:

    def __init__(self) -> None:
        self.R_C = 220 #resistance of the pull-down resistor
        self.VOLTS = 5 #voltage of the power supply
        pass

    def processData(self, data_string: str) -> np.ndarray:
        rawVoltages: np.ndarray = self.stringToIntArray(data_string)/1024*5
        size = rawVoltages.shape[0]
        resistances = np.zeros((size,size))

        #calculate the resistance of the sensor for each row
        for k in range(size):
            voltages = np.zeros((size,size))
            for i in range(size):
                for j in range(size):
                    if i == j:
                        voltages[i,j] = self.VOLTS - rawVoltages[k,i]
                    else:
                        voltages[i,j] = -rawVoltages[k,i]
            
            I = rawVoltages[k]/self.R_C
            I = I.reshape(size,1)
            R_flat = np.linalg.solve(voltages, I)
            R_flat = 1/R_flat
            resistances[k] = R_flat.reshape(1, size)

        return resistances
    
    def stringToIntArray(self, data_string: str) -> np.ndarray:
        rows = data_string.split('\n')

        #put the following data into a 2D array
        data = []
        for row in rows:
            data.append([float(num) for num in row.split(',') if num not in ['[',']','\r','']])
        
        return np.array(data)
    
if __name__ == "__main__":
    dataProcessor = DataProcessor() # create main Tkinter window
    data = dataProcessor.processData("600,400,200\n200,200,200\n200,200,200")
    print(data) # Test the processData method