import numpy as np
# import Calibration
import time

def get_data_from_com_port(self) -> np.ndarray:
    if self.app_state.com_port is None or self.app_state.com_port == "":
        return np.zeros((10, 10))

    # Check if the selected com port has changed
    if self.app_state.com_port != self.serialcomm.port:
        self.close_serial()

    # Check that the serial port is open and ready
    if not self.serialcomm.is_open:
        opened = self.open_serial(self.app_state.com_port)
        if not opened:
            # Set the serial port to None so that the user can select a new one
            # and to prevent the program from trying to open the same port again
            self.new_state.com_port = None
            self.app_state.com_port = None
            self.after(0, lambda: self.save_app_state())
            self.after(0, lambda: self.strvar_com_port.set(""))
            return np.zeros((10, 10))

    # Serial port is open. Request data from the sensor:
    self.serialcomm.write(b'\x01')

    # Get the raw data from the sensor
    raw_data: np.ndarray = self.serial_read_int_array()
    # TODO: calculations on the raw data, calibrations, etc...
    # data = Calibration.calibrate_data(raw_data)
    return raw_data

def get_data_from_recorded_data(self) -> np.ndarray:
    return np.zeros((10, 10))

def get_data_simulated(self, MIN_VAL, MAX_VAL) -> np.ndarray:
    rows = 16
    cols = 16
    data = np.zeros((rows, cols))
    # Generate heatmap data based on sine waves and the current time
    for i in range(16):
        for j in range(16):
            data[i][j] = MIN_VAL + MAX_VAL * np.clip(
                    np.sin(2 * np.pi * (j + 1 / 2) / rows) * np.sin(np.pi * (i + 1 / 2) / cols) * np.sin(time.time()),
                    0, 1
                )

    return data
