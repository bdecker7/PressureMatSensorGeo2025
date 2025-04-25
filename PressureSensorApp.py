# TODO: implement the stats. Not a high priority 
# because client really only wants the colors, 
# but it is a nice addition
# right now it is all commented out
from appdirs import user_data_dir
import numpy as np
from scipy import ndimage
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
import cv2


# Constants
MIN_VAL = 0
MAX_VAL = 1023
ASPECT_RATIO = 1.0 # Width/Height of the heatmap cells

SERIAL_BAUD_RATE = 115200 # Bits/sec for serial communication
SERIAL_COMM_SIGNAL = b'\x01' # A '1' byte: signal to request data from the Arduino, and the signal that the Arduino is ready

# Save directory for saving the GUI state
SAVE_DIR = user_data_dir("PressureSensorApp", "BYU_GEO_GlobalEngineeringOutreach")
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)
print(SAVE_DIR)
STATE_FILE_PATH = os.path.join(SAVE_DIR, "gui_state.json")

# Location of the GUI Icon
ICON_FILE_NAME = "icon.png"
ICON_PATH = os.path.join(getattr(sys, "_MEIPASS", os.path.dirname(__file__)), ICON_FILE_NAME)

#for recorded video
video = None
file_name = None
file_path = None



# The state of the GUI, in terms of user selections and settings
# This dataclass is regularly saved to a JSON file and loaded 
# when the GUI is started so that the user's previous settings are preserved
@dataclass
class PressureSensorAppState:
    # Automatically determined by the App
    heatmap_canvas_size: tuple[int, int] = (400, 400) # (width, height) in pixels
    # User selections
    data_source: Literal["com_port", "Simulación"] | None = None
    com_port: str | None = None
    frames_per_second: int | Literal["Max"] = "Max"
    recorded_data_save_directory: str | None = None
    recorded_data_filename: str = "Nombre del Archivo"
    # Settings (from the "settings" window at the bottom)
    mirror_heatmap_image: bool = False
    rotate_heatmap_image: Literal[0, 90, 180, 270] = 0 # clockwise
    interp_level: int = 1
    # data_units: Literal["raw", "lbs", "mmHg"] = "raw"
    # display_vals_on_heatmap: bool = False
    font_size: int = 11

DEFAULT_STATE = PressureSensorAppState()


class PressureSensorApp(tk.Tk):
    
    ################################################################################################
    # Initialization
    ################################################################################################

    def __init__(self):
        super().__init__()
        self.title("GEO Pressure Sensor")

        self.protocol("WM_DELETE_WINDOW", self.on_close) # Handle the window close event

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
        global video
        if video is not None:
            video.release()
            video = None
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

    
    ################################################################################################
    # Build the GUI widgets
    ################################################################################################

    def setup_gui_styles(self):
        self.padding = 10

        bg_color = "white"
        fg_color = "black"

        self.style = ttk.Style()
        self.style.theme_use("vista")
        self.configure(bg=bg_color)
        self.style.configure("TFrame", relief="flat", background=bg_color)
        self.style.configure("TSeparator")
        
        self.style.configure("TLabel", font=("Arial", 11), background=bg_color, foreground=fg_color)
        self.style.configure("SmallText.TLabel", font=("Arial", 9), background=bg_color, foreground=fg_color)
        self.style.configure("Header.TLabel", font=("Arial", 13, "bold"), background=bg_color, foreground=fg_color)
        
        self.style.configure("TButton", font=("Arial", 11), width=2, background=bg_color, foreground=fg_color)
        self.style.configure("PlayPause.TButton", font=("Times", 20), width=3, background=bg_color, foreground="green")
        self.style.configure("Record.TButton", font=("Arial", 20), width=3, background=bg_color, foreground="red")
        self.style.configure("IconButton.TButton", font=("Times", 12), width=2, background=bg_color, foreground=fg_color)

        self.style.configure("TRadiobutton", font=("Arial", 11), background=bg_color, foreground=fg_color)
        self.style.configure("TCheckbutton", font=("Arial", 11), background=bg_color, foreground=fg_color)
        self.style.configure("TCombobox", font=("Arial", 11), background=bg_color, foreground=fg_color)

    def build_gui(self):
        self.configure(padx=self.padding, pady=self.padding)

        self.frm_heatmap = ttk.Frame(master=self)
        self.frm_heatmap.grid(row=0, column=0, sticky="nsew")
        self.build_frm_heatmap(parent=self.frm_heatmap)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        frm_heatmap_colorbar = ttk.Frame(self)
        frm_heatmap_colorbar.grid(row=0, column=1, sticky="nsew")
        self.build_frm_heatmap_colorbar(parent=frm_heatmap_colorbar)

        ttk.Separator(self, orient="vertical").grid(row=0, column=2, sticky="ns", padx=self.padding)

        frm_controls_stats_settings = ttk.Frame(self)
        frm_controls_stats_settings.grid(row=0, column=3, sticky="nsew")
        self.build_frm_controls_stats_settings(parent=frm_controls_stats_settings)

    def build_frm_heatmap(self, parent: ttk.Frame):
        # Ensure the program will not be too large for the screen
        heatmap_width = min(self.app_state.heatmap_canvas_size[0], self.winfo_screenwidth()*0.7)
        heatmap_height = min(self.app_state.heatmap_canvas_size[1], self.winfo_screenheight()*0.75)

        # Create the canvas for the heatmap
        self.canvas_heatmap = tk.Canvas(
            parent, bg="white", highlightthickness=0, border=0, relief="flat", 
            width=heatmap_width, height=heatmap_height
        )
        self.canvas_heatmap.grid(row=0, column=0, sticky="nsew")
        self.canvas_heatmap.bind("<Configure>", self.on_heatmap_resize)
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)

    def build_frm_heatmap_colorbar(self, parent: ttk.Frame):
        pass

    def build_frm_controls_stats_settings(self, parent: ttk.Frame):
        frm_data_source = ttk.Frame(parent)
        frm_data_source.grid(row=0, column=0, sticky="ew")
        self.build_frm_data_source(parent=frm_data_source)

        ttk.Separator(parent, orient="horizontal").grid(row=1, column=0, sticky="ew", pady=self.padding)

        frm_playpause_etc = ttk.Frame(parent)
        frm_playpause_etc.grid(row=2, column=0, sticky="ew")
        self.build_frm_playpause_etc(parent=frm_playpause_etc)
        
        ttk.Separator(parent, orient="horizontal").grid(row=3, column=0, sticky="ew", pady=self.padding)

        frm_record_data = ttk.Frame(parent)
        frm_record_data.grid(row=4, column=0, sticky="ew")
        self.build_frm_record_data(parent=frm_record_data)

        # ttk.Separator(parent, orient="horizontal").grid(row=5, column=0, sticky="ew", pady=self.padding)

        # frm_stats = ttk.Frame(parent)
        # frm_stats.grid(row=6, column=0, sticky="ew")
        # self.build_frm_stats(parent=frm_stats)

        parent.rowconfigure(7, weight=1) # Empty row that is allowed to expand (empty space)
        ttk.Separator(parent, orient="horizontal").grid(row=8, column=0, sticky="ew", pady=self.padding)

        frm_settings = ttk.Frame(parent)
        frm_settings.grid(row=9, column=0, sticky="ew")
        self.build_frm_settings(parent=frm_settings)

    def build_frm_data_source(self, parent: ttk.Frame):
        lbl_data_source = ttk.Label(parent, text="Fuente de Datos", style="Header.TLabel")
        lbl_data_source.grid(row=0, column=0, sticky="w")
        parent.columnconfigure(0, weight=1)

        self.strvar_radiobtns_data_source = tk.StringVar(parent, value=self.app_state.data_source)

        radiobtn_com_port = ttk.Radiobutton(parent, 
                                            text="USB", 
                                            variable=self.strvar_radiobtns_data_source, 
                                            value="com_port", 
                                            command=self.on_radiobtn_data_source)
        radiobtn_com_port.grid(row=1, column=0, sticky="w")

        self.strvar_com_port = tk.StringVar(parent, value=self.app_state.com_port)
        self.dropdown_com_port = ttk.Combobox(parent, width=10, textvariable=self.strvar_com_port)
        self.dropdown_com_port.bind("<<ComboboxSelected>>", lambda e: self.on_dropdown_select_com_port())
        self.dropdown_com_port["values"] = self.available_com_ports
        self.dropdown_com_port.grid(row=1, column=1, sticky="w")

        btn_refresh_com_ports = ttk.Button(parent, text="⟳", style="IconButton.TButton", command=self.on_btn_refresh_com_ports_list)
        btn_refresh_com_ports.grid(row=1, column=2, sticky="w", padx=(self.padding, 0))


        radiobtn_simulated_data = ttk.Radiobutton(parent, 
                                                  text="Simulación", 
                                                  variable=self.strvar_radiobtns_data_source, 
                                                  value="Simulación",
                                                  command=self.on_radiobtn_data_source)
        radiobtn_simulated_data.grid(row=3, column=0, sticky="w")

    def build_frm_playpause_etc(self, parent: ttk.Frame):
        self.strvar_playpause_btn = tk.StringVar(parent, value="◼")
        btn_playpause = ttk.Button(parent, textvariable=self.strvar_playpause_btn, style="PlayPause.TButton", command=self.on_btn_playpause)
        btn_playpause.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, self.padding))
        parent.rowconfigure(0, weight=1)

        lbl_framespersecond = ttk.Label(parent, text="FPS:")
        lbl_framespersecond.grid(row=0, column=1, sticky="e")
        parent.columnconfigure(1, weight=1)

        self.strvar_framespersecond = tk.StringVar(parent, value="Máximo")
        cmbbox_framespersecond = ttk.Combobox(parent, textvariable=self.strvar_framespersecond, width=4)
        cmbbox_framespersecond["values"] = ["Máx", "20", "10", "5", "2", "1"]
        cmbbox_framespersecond.grid(row=0, column=2, sticky="w")

        frm_prev_next_frame = ttk.Frame(parent)
        frm_prev_next_frame.grid(row=1, column=1, columnspan=2, sticky="ew", pady=(self.padding, 0))
        frm_prev_next_frame.columnconfigure(0, weight=1)
        frm_prev_next_frame.columnconfigure(1, weight=1)

        btn_prev_frame = ttk.Button(frm_prev_next_frame, text="< Vuelva", width=len("< Vuelva"), style="TButton", command=self.on_btn_prev_frame)
        btn_prev_frame.grid(row=0, column=0, sticky="nsew")

        btn_next_frame = ttk.Button(frm_prev_next_frame, text="Sigue >", width=len("Sigue >"), style="TButton", command=self.on_btn_next_frame)
        btn_next_frame.grid(row=0, column=1, sticky="nsew")

        lbl_frame_number = ttk.Label(parent, text="Fotograma:")
        lbl_frame_number.grid(row=2, column=0, sticky="w")

        self.strvar_frame_number = tk.StringVar(parent, value="0")
        lbl_frame_number_value = ttk.Label(parent, textvariable=self.strvar_frame_number)
        lbl_frame_number_value.grid(row=2, column=1, sticky="w")

    # def build_frm_stats(self, parent: ttk.Frame):
    #     lbl_frm_stats = ttk.Label(parent, text="Estadística", style="Header.TLabel")
    #     lbl_frm_stats.grid(row=0, column=0, columnspan=4, sticky="w")
    #     parent.columnconfigure(0, weight=0)
        
    #     lbl_max = ttk.Label(parent, text="Máximo:")
    #     lbl_max.grid(row=1, column=0, sticky="w")
    #     self.strvar_stats_max = tk.StringVar(parent, value="0.0")
    #     lbl_max_value = ttk.Label(parent, textvariable=self.strvar_stats_max)
    #     lbl_max_value.grid(row=1, column=1, sticky="w")

    #     lbl_min = ttk.Label(parent, text="Mínimo:")
    #     lbl_min.grid(row=2, column=0, sticky="w")
    #     self.strvar_stats_min = tk.StringVar(parent, value="0.0")
    #     lbl_min_value = ttk.Label(parent, textvariable=self.strvar_stats_min)
    #     lbl_min_value.grid(row=2, column=1, sticky="w")

    #     lbl_avg = ttk.Label(parent, text="Promedio:")
    #     lbl_avg.grid(row=3, column=0, sticky="w")
    #     self.strvar_stats_avg = tk.StringVar(parent, value="0.0")
    #     lbl_avg_value = ttk.Label(parent, textvariable=self.strvar_stats_avg)
    #     lbl_avg_value.grid(row=3, column=1, sticky="w")

    #     lbl_std_dev = ttk.Label(parent, text="Desviación Estándar:")
    #     lbl_std_dev.grid(row=4, column=0, sticky="w")
    #     self.strvar_stats_std_dev = tk.StringVar(parent, value="0.0")
    #     lbl_std_dev_value = ttk.Label(parent, textvariable=self.strvar_stats_std_dev)
    #     lbl_std_dev_value.grid(row=4, column=1, sticky="w")

    #     parent.columnconfigure(1, weight=1)

    def build_frm_record_data(self, parent: ttk.Frame):
        lbl_recorded_data = ttk.Label(parent, text="Grabe", style="Header.TLabel")
        lbl_recorded_data.grid(row=0, column=0, columnspan=2, sticky="w")

        self.strvar_record = tk.StringVar(parent, value="⬤")
        self.btn_record = ttk.Button(parent, textvariable=self.strvar_record, style="Record.TButton", command=self.on_btn_record)
        self.btn_record.grid(row=1, column=0, rowspan=2, sticky="nsew", padx=(0, self.padding))

        # Selection of the directory to save the recorded data
        frm_recording_directory = ttk.Frame(parent)
        frm_recording_directory.grid(row=1, column=1, sticky="nsew")
        parent.columnconfigure(1, weight=1)
        self.btn_recording_directory = ttk.Button(frm_recording_directory, text=u"\U0001F4C1", style="TButton", width=4, command=self.on_btn_select_recording_directory)
        self.btn_recording_directory.grid(row=0, column=0, sticky="w")
        self.strval_recording_directory = tk.StringVar(frm_recording_directory, value="← Seleccionar directorio")
        self.lbl_recording_directory = ttk.Label(frm_recording_directory, textvariable=self.strval_recording_directory, style="SmallText.TLabel")
        self.lbl_recording_directory.grid(row=0, column=1, sticky="ew")
        frm_recording_directory.columnconfigure(1, weight=1)

        # Name of file to save the recorded data
        frm_recording_filename = ttk.Frame(parent)
        frm_recording_filename.grid(row=2, column=1, sticky="ew")
        self.strval_recording_filename = tk.StringVar(frm_recording_filename, value=self.app_state.recorded_data_filename)
        self.entry_recording_filename = ttk.Entry(frm_recording_filename, textvariable=self.strval_recording_filename, width=8)
        self.entry_recording_filename.grid(row=0, column=1, sticky="ew")
        self.entry_recording_filename.bind("<FocusOut>", lambda e: self.on_btn_new_recording_filename())
        frm_recording_filename.columnconfigure(1, weight=1)
        lbl_vid = ttk.Label(frm_recording_filename, text=".mp4")
        lbl_vid.grid(row=0, column=2, sticky="w")
       
        # Frame counter and time elapsed
        frm_frm_counter = ttk.Frame(parent)
        frm_frm_counter.grid(row=3, column=0, columnspan=2, sticky="ew")
        lbl_frame_counter = ttk.Label(frm_frm_counter, text="Fotogramas grabados:")
        lbl_frame_counter.grid(row=0, column=0, sticky="w")
        self.strvar_frame_counter = tk.StringVar(frm_frm_counter, value="0")
        lbl_frame_counter_value = ttk.Label(frm_frm_counter, textvariable=self.strvar_frame_counter)
        lbl_frame_counter_value.grid(row=0, column=1, sticky="w", padx=(self.padding, 0))

    def build_frm_settings(self, parent: ttk.Frame):
        lbl_settings = ttk.Label(parent, text="Ajustes", style="Header.TLabel")
        lbl_settings.grid(row=0, column=0, sticky="w")
        parent.columnconfigure(0, weight=1)

        # Image rotation and mirroring
        frm_settings_image_rotation_mirror = ttk.Frame(parent)
        frm_settings_image_rotation_mirror.grid(row=1, column=0, sticky="nsew")

        lbl_image_orientaion = ttk.Label(frm_settings_image_rotation_mirror, text="Orientación de la Imagen")
        lbl_image_orientaion.grid(row=0, column=0, sticky="ew")
        frm_settings_image_rotation_mirror.columnconfigure(0, weight=1)

        self.bvar_chkbtn_mirror_image = tk.BooleanVar(frm_settings_image_rotation_mirror, value=self.app_state.mirror_heatmap_image)
        chkbtn_mirror_image = ttk.Checkbutton(
            frm_settings_image_rotation_mirror, variable=self.bvar_chkbtn_mirror_image, text="Espejo", command=self.on_chkbtn_mirror_heatmap_image
        )
        chkbtn_mirror_image.grid(row=0, column=1, sticky="ew")

        icon: str = "\u27F3" if self.app_state.mirror_heatmap_image else "\u27F2"
        self.strvar_btn_rotate_image = tk.StringVar(frm_settings_image_rotation_mirror, value=f"Gire {icon}")
        btn_rotate_image = ttk.Button(frm_settings_image_rotation_mirror, textvariable=self.strvar_btn_rotate_image, width=8, command=self.on_btn_rotate_heatmap_image)
        btn_rotate_image.grid(row=0, column=2, sticky="ew")


        # Font Size
        frm_settings_font_size = ttk.Frame(parent)
        frm_settings_font_size.grid(row=2, column=0, sticky="nsew")

        lbl_font_size = ttk.Label(frm_settings_font_size, text="Tamaño de Fuente")
        lbl_font_size.grid(row=1, column=0, sticky="w")
        frm_settings_font_size.columnconfigure(0, weight=1)

        btn_decrease_font_size = ttk.Button(frm_settings_font_size, text="-", width=3, command=self.on_btn_decrease_font_size)
        btn_decrease_font_size.grid(row=1, column=1, sticky="w")

        btn_increase_font_size = ttk.Button(frm_settings_font_size, text="+", width=3, command=self.on_btn_increase_font_size)
        btn_increase_font_size.grid(row=1, column=2, sticky="w")


    ################################################################################################
    # Event Handlers
    ################################################################################################

    def on_heatmap_resize(self, event):
        self.draw_heatmap(canvas_resized=True)
        self.new_state.heatmap_canvas_size = self.canvas_heatmap.winfo_width(), self.canvas_heatmap.winfo_height()
        self.refresh_gui()

    def on_radiobtn_data_source(self):
        new_source = self.strvar_radiobtns_data_source.get()
        
        if new_source == "com_port":
            self.new_state.data_source = "com_port"
        elif new_source == "Simulación":
            self.new_state.data_source = "Simulación"
        
        self.refresh_gui()

    def on_dropdown_select_com_port(self):
        self.new_state.com_port = self.dropdown_com_port.get()
        self.refresh_gui()

    def on_btn_refresh_com_ports_list(self):
        self.available_com_ports = [port.name for port in list_ports.comports()]
        self.dropdown_com_port["values"] = self.available_com_ports

    def on_btn_playpause(self):
        self.paused = not self.paused
        self.refresh_gui()

    def on_btn_prev_frame(self):
        pass

    def on_btn_next_frame(self):
        pass

    def on_btn_record(self):
        global video
        global file_name
        global file_path
        if not self.recording:
            if not self.app_state.recorded_data_save_directory or not self.app_state.recorded_data_filename:
                return

            save_name: str = self.app_state.recorded_data_filename
            save_path= os.path.join(self.app_state.recorded_data_save_directory, save_name)            
            # Ask user if they want to overwrite the existing file
            if os.path.exists(save_path+".mp4"):
                prompt = f"El archivo '{save_name}' ya existe. La grabación lo sobrescribirá. ¿Continuar?"
                if messagebox.askyesno("Advertencia", prompt):
                    self.recording = True
                    self.time_recording_started = time.time()
                    self.refresh_gui()
            else:
                self.recording = True
                self.time_recording_started = time.time()
                self.refresh_gui()
            file_name = save_name
            file_path = save_path
        else:
            self.recording = False
            # close video
            if video is not None:
                video.release()
                video = None
            self.refresh_gui()
        

    def on_btn_select_recording_directory(self):
        # Select a new directory to save the recorded data
        self.new_state.recorded_data_save_directory = filedialog.askdirectory(mustexist=True)
        self.refresh_gui()
    
    def on_btn_new_recording_filename(self):
        self.new_state.recorded_data_filename = self.strval_recording_filename.get()
        self.refresh_gui()

    def on_btn_decrease_font_size(self):
        # Decrease the font size by 1pt for all widgets
        styles_to_modify = ["TLabel", "Header.TLabel", "TButton", "PlayPause.TButton", "TRadiobutton", "TCheckbutton", "TCombobox"]
        for style in styles_to_modify:
            current_font = self.style.lookup(style, "font")
            font_parts = current_font.split()
            font_name = font_parts[0]
            font_size = int(font_parts[1])
            
            if style == "Header.TLabel":
                self.style.configure(style, font=(font_name, font_size - 1, "bold"))
            else:
                self.style.configure(style, font=(font_name, font_size - 1))

    def on_btn_increase_font_size(self):
        # Increase the font size by 1pt for all widgets
        styles_to_modify = ["TLabel", "Header.TLabel", "TButton", "PlayPause.TButton", "TRadiobutton", "TCheckbutton", "TCombobox"]
        for style in styles_to_modify:
            current_font = self.style.lookup(style, "font")
            font_parts = current_font.split()
            font_name = font_parts[0]
            font_size = int(font_parts[1])
            
            if style in ["Header.TLabel"]:
                self.style.configure(style, font=(font_name, font_size + 1, "bold"))
            else:
                self.style.configure(style, font=(font_name, font_size + 1))     

    def on_chkbtn_mirror_heatmap_image(self):
        self.new_state.mirror_heatmap_image = self.bvar_chkbtn_mirror_image.get()
        icon: str = "\u27F3" if self.new_state.mirror_heatmap_image else "\u27F2"
        self.strvar_btn_rotate_image.set(f"Rotate {icon}")
        self.refresh_gui()

    def on_btn_rotate_heatmap_image(self):
        if self.app_state.rotate_heatmap_image == 270:
            self.new_state.rotate_heatmap_image = 0
        elif self.app_state.rotate_heatmap_image == 180:
            self.new_state.rotate_heatmap_image = 270
        elif self.app_state.rotate_heatmap_image == 90:
            self.new_state.rotate_heatmap_image = 180
        else:
            self.new_state.rotate_heatmap_image = 90

        self.refresh_gui()


    ################################################################################################
    # Refresh the GUI 
    ################################################################################################
    # These methods do NOT update the heatmap or anything else that updates continuously. 
    # That is done in a background thread.
    # These functions update the visual state of the GUI widgets (such as disabling or enabling widgets).
    # Most of the event handlers (above) will call 'refresh_gui()' to visually reflect a new GUI state after 
    # a button is clicked or a selection is made.
    ################################################################################################

    def refresh_gui(self):
        self.refresh_frm_data_source()
        self.refresh_frm_playpause_etc()
        self.refresh_frm_record_data()
        self.refresh_frm_stats()
        self.refresh_frm_settings()

        # Save the new state
        self.app_state = deepcopy(self.new_state)
        self.save_app_state()

        # Force the GUI to update the display
        self.update_idletasks()
    
    def refresh_frm_data_source(self):
        pass

    def refresh_frm_playpause_etc(self):
        if self.paused:
            self.strvar_playpause_btn.set("▶")
        else:
            self.strvar_playpause_btn.set("◼")

    def refresh_frm_record_data(self):
        # Set appearance of record button, enable/disable recording widgets
        if self.recording:
            self.strvar_record.set("◼")
            self.btn_recording_directory.configure(state="disabled")
            self.entry_recording_filename.configure(state="disabled")
        else:
            self.strvar_record.set("⬤")
            self.btn_recording_directory.configure(state="normal")
            self.entry_recording_filename.configure(state="normal")
        
        # Disable/Enable the record button based on whether a directory has been selected
        if not self.new_state.recorded_data_save_directory:
            self.btn_record.configure(state="disabled")
        else:
            self.btn_record.configure(state="normal")

        # Update the displayed directory name
        if self.new_state.recorded_data_save_directory != self.app_state.recorded_data_save_directory:
            lbl_width = self.lbl_recording_directory.winfo_width() # width of label in pixels
            font_name, font_size = self.style.lookup(self.lbl_recording_directory.cget("style"), "font").split()[:2]
            char_width = tkfont.Font(family=font_name, size=int(font_size)).measure("d") # width of a character in pixels
            num_chars = lbl_width // char_width
            
            dirname = self.new_state.recorded_data_save_directory if self.new_state.recorded_data_save_directory else "← Select Directory"
            if len(dirname) > num_chars:
                self.strval_recording_directory.set("..." + dirname[-num_chars:] + "/")
            else:
                self.strval_recording_directory.set(dirname)
        
        # Update the filename entry box if it is empty
        if not self.new_state.recorded_data_filename:
            self.new_state.recorded_data_filename = "Nombre del Archivo"
            self.strval_recording_filename.set(self.new_state.recorded_data_filename)

    def refresh_frm_stats(self):
        pass

    def refresh_frm_settings(self):
        pass


    ################################################################################################
    # Background Thread: Continuously retrieve data and update the heatmap 
    ################################################################################################
    # NOTE: all changes to GUI widgets should be done in the main thread, not in this thread.
    # If a widget needs to be updated in this thread, use 'self.after(0, lambda: method_name)' 
    # to call a method to run in the main thread that updates the widget
    ################################################################################################

    def threadloop_data_update(self):
        while True:
            update_started: float = time.time()

            # If GUI is paused, don't update the data
            if self.paused:
                time.sleep(0.1)
                continue
                
            # Get new data
            if self.app_state.data_source == "com_port":
                self.data = self.get_data_from_com_port()
            elif self.app_state.data_source == "Simulación":
                self.data = self.get_data_simulated()
                
            # Update the heatmap
            self.draw_heatmap()

            # Wait until the next frame should happen
            if self.app_state.frames_per_second == "Max":
                continue
            time_per_frame = 1 / self.app_state.frames_per_second
            time_to_wait = time_per_frame - (time.time() - update_started)
            if time_to_wait > 0:
                time.sleep(time_to_wait)

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
        return raw_data
 
    def serial_read_uint16(self) -> int:
        vals: bytes = self.serialcomm.read(2) # read two bytes of binary data
        value = int.from_bytes(vals, 'little') # convert the bytes to an integer
        return value
    
    def serial_read_int_array(self) -> np.ndarray:
        rows: int = self.serial_read_uint16() # read the number of rows
        cols: int = self.serial_read_uint16() # read the number of columns
        vals: bytes = self.serialcomm.read(rows * cols * 2) # read all data
        
        # iterate over the vals and fill the data array
        data: np.ndarray = np.zeros((rows, cols), dtype=int)
        for i in range(0, len(vals), 2):
            row: int = i // (cols * 2)
            col: int = (i // 2) % cols
            data[row, col] = int.from_bytes(vals[i:i+2], 'little')
        return data

    def get_data_from_recorded_data(self) -> np.ndarray:
        return np.zeros((10, 10))
    
    def get_data_simulated(self) -> np.ndarray:
        rows = 16
        cols = 16
        data = np.zeros((rows, cols))

        # Generate heatmap data based on sine waves and the current time
        for i in range(16):
            for j in range(16):
                data[i][j] = np.clip(
                    np.sin(2*np.pi*(j+1/2)/rows) * 
                    np.sin(np.pi*(i+1/2)/cols) * 
                    np.sin(time.time()), 0, 1
                    )         
        return data

    def draw_heatmap(self, canvas_resized: bool = False):
        # Heatmap image starts as a copy of the data
        heatmap_image: np.ndarray = self.data.copy()

        # Rotate and/or mirror the image as needed
        if self.app_state.rotate_heatmap_image == 90:
            heatmap_image = np.rot90(heatmap_image)
        elif self.app_state.rotate_heatmap_image == 180:
            heatmap_image = np.rot90(heatmap_image, 2)
        elif self.app_state.rotate_heatmap_image == 270:
            heatmap_image = np.rot90(heatmap_image, 3)
        if self.app_state.mirror_heatmap_image:
            heatmap_image = np.fliplr(heatmap_image)



        MAX_VAL = np.max(heatmap_image)
        p25 = np.percentile(heatmap_image, 25) # calculate the 25th percentile
        
        MIN_VAL = np.min(heatmap_image)
        if(MAX_VAL <= 0):
            MAX_VAL = 1023
        # Interpolate the data (smooth it out)
        ndimage.zoom(heatmap_image, zoom=4, order=3, mode='nearest')
        heatmap_image = np.clip(heatmap_image, MIN_VAL, MAX_VAL)

        # Build and apply a colormap to the data (making the data an RGB image)
        normalized_data = (heatmap_image - p25) / (MAX_VAL - p25)
        heatmap_image = apply_colormap(normalized_data, "inferno") # causing possible error
        heatmap_image *= 255 # Convert to 0-255 range (for RGB) rather than 0-1

        # Calculate the size of each heatmap cell based on the size of the canvas
        rows, cols = heatmap_image.shape[:2]
        canvas_width: int = self.canvas_heatmap.winfo_width() # pixels
        canvas_height: int = self.canvas_heatmap.winfo_height() # pixels
        canvas_aspect_ratio: float = canvas_width / canvas_height
        if canvas_aspect_ratio > ASPECT_RATIO: 
            # canvas will be wider than the heatmap
            cell_height: int = int(canvas_height / rows)
            cell_width: int = int(cell_height / ASPECT_RATIO)
        else: 
            # canvas will be taller than the heatmap
            cell_width: int = int(canvas_width / cols)
            cell_height: int = int(cell_width * ASPECT_RATIO)

        # While GUI is being built, canvas size may be 0. This prevents an error:
        if cell_width == 0 or cell_height == 0:
            return
        
        # Scale the data based on the calculated cell sizes
        heatmap_image = np.repeat(heatmap_image, cell_width, axis=1)
        heatmap_image = np.repeat(heatmap_image, cell_height, axis=0)
        heatmap_image = np.ascontiguousarray(heatmap_image) # Make it a C-contiguous array for faster drawing
        heatmap_image = heatmap_image.astype(np.uint8)

        # There may be some extra space on the canvas. 
        # Fill it in by expanding a few of the cell widths/heights by 1 pixel.
        leftover_height: int = canvas_height - (cell_height * rows)
        leftover_width: int = canvas_width - (cell_width * cols)
        if canvas_aspect_ratio > ASPECT_RATIO:
            pixels_to_add = leftover_height
        else:
            pixels_to_add = leftover_width
        for pixel in range(pixels_to_add):
            i = pixel * cell_height + int(cell_height/2)
            j = pixel * cell_width + int(cell_width/2)
            heatmap_image = np.insert(heatmap_image, i, heatmap_image[i, :], axis=0)
            heatmap_image = np.insert(heatmap_image, j, heatmap_image[:, j], axis=1)

        # Draw the heatmap on the canvas
        topmost_pixel = 0 if canvas_aspect_ratio > ASPECT_RATIO else int((leftover_height - leftover_width) / 2)
        leftmost_pixel = 0 if canvas_aspect_ratio < ASPECT_RATIO else int((leftover_width - leftover_height) / 2)
        pil_image = Image.fromarray(heatmap_image)       #this is what makes the actual heatmap from the data array
        if not hasattr(self, 'heatmap_photo') or canvas_resized:
            self.heatmap_photo = ImageTk.PhotoImage(pil_image)     
            self.heatmap_image_id = self.canvas_heatmap.create_image(
                leftmost_pixel, topmost_pixel, anchor="nw", image=self.heatmap_photo
            )
        else:
            self.heatmap_photo.paste(pil_image)
            self.canvas_heatmap.coords(self.heatmap_image_id, (leftmost_pixel, topmost_pixel)) #error with input arguments

        self.array_for_recorded_data = heatmap_image
        
        # Save the heatmap frame in video record
        if self.recording:
            self.create_video_from_frames(file_path, 30, heatmap_image)
       
    def create_video_from_frames(self, folder: str, fps: int, frame_to_add: np.array):
        global video
        # create folder to store the video
        # if not os.path.exists(folder):
        #     try:
        #         #os.makedirs(folder)
        #         print(folder)
        #     except Exception as e:
        #             print("error from folder")
        #names the video
        video_path = folder + ".mp4"
        
        height, width, layers = frame_to_add.shape

        # create video
        if video is None:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video = cv2.VideoWriter(video_path, fourcc, fps, (width, height), True)

        # convert RGB to BGR for video record
        frame = cv2.cvtColor(frame_to_add, cv2.COLOR_RGB2BGR)

        # Write frame to the video
        video.write(frame)


    def save_heatmap_data(self, heatmap_image: np.ndarray, data_filename: str, image_filename: str):
    # Save the heatmap data as a NumPy binary file
        np.save(data_filename, heatmap_image)
    
    # Save the heatmap as an image
        pil_image = Image.fromarray(heatmap_image.astype(np.uint8))
        pil_image.save(image_filename)





    ################################################################################################
    # Helper methods 
    ################################################################################################

    def open_serial(self, port: str) -> bool:
        try:
            # Attempt to open serial port. May raise a SerialException.
            self.serialcomm = serial.Serial(port, SERIAL_BAUD_RATE, timeout=4)
            time.sleep(0.01) # Wait for the serial port to open
            
            # Check that the serial port opened successfully
            if not self.serialcomm.is_open:
                raise Exception("Serial port did not open.")
            
            # Wait up to 3 seconds for a signal from the Arduino that it is ready
            ready_signal_received = False
            start_time = time.time()
            while time.time() - start_time < 3:
                if self.serialcomm.in_waiting > 0:
                    if self.serialcomm.read(size=1) == SERIAL_COMM_SIGNAL:
                        ready_signal_received = True
                        break
            if not ready_signal_received:
                raise Exception(f"Ready signal '{SERIAL_COMM_SIGNAL}' not received within 3 seconds.")

            # Serial port is open and ready
            return True
        
        except (serial.SerialException, Exception) as e:
            messagebox.showerror(
                "Serial Port Error",
                "Error opening serial port: \n\n" \
                f"{str(e)}"
            )
            self.close_serial()            
            return False
        
    def close_serial(self):
        global video
        if video is not None:
            video.release()
            video = None
        self.serialcomm.close()
        

    def save_app_state(self):
        with open(STATE_FILE_PATH, "w") as file:
            json.dump(asdict(self.app_state), file, indent=4)


if __name__ == "__main__":
    app = PressureSensorApp()
    app.mainloop()

