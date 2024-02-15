"""
This class defines variables and methods to organize, 
"""

import numpy as np

class DataProcessor:
    port: str = ""

    def __init__(self, port: str) -> None:
        self.port = port

    def parseStringToInt(self, string: str) -> np.array:
        rows = str.split('\n')

        #put the following data into a 2D array
        data = []
        for row in rows:
            data.append([int(num) for num in row.split(',') if num not in ['[',']']])
        
        return np.array(data)