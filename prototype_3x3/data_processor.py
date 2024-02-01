"""
This class defines variables and methods to organize, 
"""

class DataProcessor:
    port: str = ""

    def __init__(self, port: str) -> None:
        self.port = port