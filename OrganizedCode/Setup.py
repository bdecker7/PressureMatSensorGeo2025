from appdirs import user_data_dir
import numpy as np
# from scipy import ndimage
from colormaps import apply_colormap
from PIL import Image, ImageTk
import serial.tools.list_ports as list_ports
import serial

import sys
import os

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import tkinter.font as tkfont
import json
from dataclasses import dataclass, asdict
from typing import Literal
from copy import copy, deepcopy
import threading
import time

# Constants
MIN_VAL = 0
MAX_VAL = 1023
ASPECT_RATIO = 1.0  # Width/Height of the heatmap cells

SERIAL_BAUD_RATE = 115200  # Bits/sec for serial communication
SERIAL_COMM_SIGNAL = b'\x01'  # A '1' byte: signal to request data from the Arduino, and the signal that the Arduino is ready

# Save directory for saving the GUI state
SAVE_DIR = user_data_dir("PressureSensorApp", "BYU_GEO_GlobalEngineeringOutreach")
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)
print(SAVE_DIR)
STATE_FILE_PATH = os.path.join(SAVE_DIR, "gui_state.json")

# Location of the GUI Icon
ICON_FILE_NAME = "icon.png"
ICON_PATH = os.path.join(getattr(sys, "_MEIPASS", os.path.dirname(__file__)), ICON_FILE_NAME)


# The state of the GUI, in terms of user selections and settings
# This dataclass is regularly saved to a JSON file and loaded
# when the GUI is started so that the user's previous settings are preserved
@dataclass
class PressureSensorAppState:
    # Automatically determined by the App
    heatmap_canvas_size: tuple[int, int] = (400, 400)  # (width, height) in pixels
    # User selections
    data_source: Literal["com_port", "recorded", "simulated"] | None = None
    com_port: str | None = None
    frames_per_second: int | Literal["Max"] = "Max"
    recorded_data_save_directory: str | None = None
    recorded_data_filename: str = "data"
    recorded_data_append_datetime: bool = True
    # Settings (from the "settings" window at the bottom)
    mirror_heatmap_image: bool = False
    rotate_heatmap_image: Literal[0, 90, 180, 270] = 0  # clockwise
    interp_level: int = 1
    data_units: Literal["raw", "lbs", "mmHg"] = "raw"
    display_vals_on_heatmap: bool = False
    font_size: int = 11


DEFAULT_STATE = PressureSensorAppState()


class PressureSensorApp(tk.Tk):

    ################################################################################################
    # Initialization
    ################################################################################################

    def __init__(self):
        super().__init__()
        self.title("GEO Pressure Sensor")

        self.protocol("WM_DELETE_WINDOW", self.on_close)  # Handle the window close event

        self.initialize_variables()

        if os.path.exists(ICON_PATH):
            self.iconphoto(True, tk.PhotoImage(file=ICON_PATH))

        self.setup_gui_styles()
        self.build_gui()

        self.refresh_gui()

        self.thread_data_update = threading.Thread(target=self.threadloop_data_update, daemon=True)
        self.threadlock_data_update = threading.Lock()
        self.thread_data_update.start()

    def on_close(self):
        self.destroy()
        sys.exit(0)

    def initialize_variables(self):
        # Variables that are reset each time the GUI is started
        self.paused: bool = False
        self.recording: bool = False
        self.time_recording_started: float = time.time()
        self.available_com_ports: list[str] = [port.name for port in list_ports.comports()]

        # Variable to hold the data that will be displayed on the heatmap
        self.data: np.ndarray = np.zeros((10, 10))

        # Variables for managing serial communication
        self.serialcomm: serial.Serial = serial.Serial()

        # Create the GUI state JSON file if it doesn't exist
        if not os.path.exists(STATE_FILE_PATH):
            with open(STATE_FILE_PATH, "w") as file:
                json.dump(asdict(DEFAULT_STATE), file, indent=4)

        # Load in the GUI state from the JSON file
        with open(STATE_FILE_PATH, "r") as file:
            try:
                state = json.load(file)
                self.app_state = PressureSensorAppState(**state)
                self.new_state = PressureSensorAppState(**state)
            except TypeError:
                self.app_state = deepcopy(DEFAULT_STATE)
                self.new_state = deepcopy(DEFAULT_STATE)

        if self.app_state.com_port not in self.available_com_ports:
            self.app_state.com_port = None
            self.new_state.com_port = None
