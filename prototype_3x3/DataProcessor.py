"""
This class defines variables and methods to organize, 
"""

import numpy as np

class DataProcessor:

    def __init__(self) -> None:
        self.R_C = 300 #resistance of the pull-down resistor
        self.VOLTS = 5 #voltage of the power supply
        pass

    def processData(self, data_string: str) -> np.ndarray:
        rawVoltages: np.ndarray = self.stringToIntArray(data_string)/1024*5
        size = rawVoltages.shape[0]
        overallVoltages = np.empty((size, size), dtype=object)

        #calculate the resistance of the sensor for each row
        for k in range(size):
            voltages = np.zeros((size,size))
            for i in range(size):
                for j in range(size):
                    if i == j:
                        voltages[i,j] = self.VOLTS - rawVoltages[k,i]
                    else:
                        voltages[i,j] = -rawVoltages[k,i]
            overallVoltages[k,k] = voltages

        # Calculate currents using vectorized operations
        I = rawVoltages / self.R_C

        # Flatten the array to a column vector
        I_flat = I.flatten().reshape(-1, 1)

        # Solve the system of linear equations
        R_flat = np.linalg.solve(overallVoltages, I_flat)

        # Reshape the result back to a matrix
        R_matrix = R_flat.reshape(size, size)

        # Invert the elements of the resulting matrix to get resistance values
        R_matrix = 1 / R_matrix

        return R

    def stringToIntArray(self, data_string: str) -> np.ndarray:
        rows = data_string.split('\n')

        #put the following data into a 2D array
        data = []
        for row in rows:
            data.append([float(num) for num in row.split(',') if num not in ['[',']','\r','']])
        
        return np.array(data)
    
if __name__ == "__main__":
    dataProcessor = DataProcessor() # create main Tkinter window
    data = dataProcessor.processData("500,500,500\n500,500,500\n500,500,500")
    print(data) # Test the processData method