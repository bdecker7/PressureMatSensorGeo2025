"""
This class defines variables and methods to organize, 
"""

import numpy as np

class DataProcessor:

    def __init__(self) -> None:
        pass

    def processData(self, data_string: str) -> np.ndarray:
        return self.stringToIntArray(data_string)

    def stringToIntArray(self, data_string: str) -> np.ndarray:
        # rows = str.split('\n')
        rows = data_string.split('\n')

        #put the following data into a 2D array
        data = []
        for row in rows:
            data.append([float(num) for num in row.split(',') if num not in ['[',']','\r','']])
        
        return np.array(data)