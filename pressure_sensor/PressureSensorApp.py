import serial.tools.list_ports as list_ports

from appdirs import user_data_dir
import numpy as np

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


HEATMAP_SIZE = (10, 10) # Size of the heatmap (rows, columns)


@dataclass
class PressureSensorGUIState:
    data_source: Literal["com_port", "recorded", "simulated"] | None = None
    com_port: str | None = None
    frames_per_second: int | Literal["Max"] = "Max"
    recorded_data_save_directory: str | None = None
    recorded_data_filename: str = "data"
    recorded_data_append_datetime: bool = True
    interp_level: int = 1
    font_size: int = 11
    data_units: Literal["raw", "lbs", "mmHg"] = "raw"
    display_vals_on_heatmap: bool = False

DEFAULT_STATE = PressureSensorGUIState()


# Save directory for saving the GUI state
SAVE_DIR = user_data_dir("PressureSensorApp", "BYU_GEO_GlobalEngineeringOutreach")
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)
STATE_FILE = os.path.join(SAVE_DIR, "gui_state.json")


# Location of the GUI Icon
ICON_FILE_NAME = "icon.png"
ICON_PATH = os.path.join(getattr(sys, "_MEIPASS", os.path.dirname(__file__)), ICON_FILE_NAME)


class PressureSensorGUI(tk.Tk):

    """ Initialization """

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
        self.destroy()
        sys.exit(0)

    def save_state(self):
        with open(STATE_FILE, "w") as file:
            json.dump(asdict(self.state), file, indent=4)

    def initialize_variables(self):
        # Create the GUI state JSON file if it doesn't exist
        if not os.path.exists(STATE_FILE):
            with open(STATE_FILE, "w") as file:
                json.dump(asdict(DEFAULT_STATE), file, indent=4)
        
        # Load in the GUI state from the JSON file
        with open(STATE_FILE, "r") as file:
            state = json.load(file)
            self.state = PressureSensorGUIState(**state)
            self.new_state = PressureSensorGUIState(**state)

        # Variables that are reset each time the GUI is started
        self.paused: bool = True
        self.recording: bool = False
        self.time_recording_started: float = time.time()
        self.available_com_ports: list[str] = [port.name for port in list_ports.comports()]
        
        # Variable to hold the data that will be displayed on the heatmap
        self.data: np.ndarray = np.zeros((10, 10))

    
    """ Build the GUI widgets """

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

        frm_heatmap = ttk.Frame(self)
        frm_heatmap.grid(row=0, column=0, sticky="nsew")
        self.build_frm_heatmap(parent=frm_heatmap)

        frm_heatmap_colorbar = ttk.Frame(self)
        frm_heatmap_colorbar.grid(row=0, column=1, sticky="nsew")
        self.build_frm_heatmap_colorbar(parent=frm_heatmap_colorbar)

        ttk.Separator(self, orient="vertical").grid(row=0, column=2, sticky="ns", padx=self.padding)

        frm_controls_stats_settings = ttk.Frame(self)
        frm_controls_stats_settings.grid(row=0, column=3, sticky="nsew")
        self.build_frm_controls_stats_settings(parent=frm_controls_stats_settings)

        self.columnconfigure(0, weight=1, minsize=500)
        self.rowconfigure(0, weight=1, minsize=500)
    
    def build_frm_heatmap(self, parent: ttk.Frame):
        # Heatmap should always have square aspect ratio. 
        # The canvas may become rectangular, but the actual data display area should be square and centered.
        # Possibly have grid lines. But even better, have little x's at the cetner of each grid cell.
        pass

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

        ttk.Separator(parent, orient="horizontal").grid(row=5, column=0, sticky="ew", pady=self.padding)

        frm_stats = ttk.Frame(parent)
        frm_stats.grid(row=6, column=0, sticky="ew")
        self.build_frm_stats(parent=frm_stats)

        ttk.Separator(parent, orient="horizontal").grid(row=7, column=0, sticky="ew", pady=self.padding)

        frm_settings = ttk.Frame(parent)
        frm_settings.grid(row=8, column=0, sticky="ew")
        self.build_frm_settings(parent=frm_settings)

    def build_frm_data_source(self, parent: ttk.Frame):
        lbl_data_source = ttk.Label(parent, text="Data Source", style="Header.TLabel")
        lbl_data_source.grid(row=0, column=0, sticky="w")
        parent.columnconfigure(0, weight=1)

        self.strvar_radiobtns_data_source = tk.StringVar(parent, value="none")

        radiobtn_com_port = ttk.Radiobutton(parent, 
                                            text="COM Port", 
                                            variable=self.strvar_radiobtns_data_source, 
                                            value="com_port", 
                                            command=self.on_radiobtn_data_source)
        radiobtn_com_port.grid(row=1, column=0, sticky="w")

        self.dropdown_com_port = ttk.Combobox(parent, width=6)
        self.dropdown_com_port.bind("<<ComboboxSelected>>", lambda e: self.on_dropdown_select_com_port())
        self.dropdown_com_port["values"] = self.available_com_ports
        self.dropdown_com_port.grid(row=1, column=1, sticky="w")

        btn_refresh_com_ports = ttk.Button(parent, text="⟳", style="IconButton.TButton", command=self.on_btn_refresh_com_ports_list)
        btn_refresh_com_ports.grid(row=1, column=2, sticky="w", padx=(self.padding, 0))

        radiobtn_recorded_data = ttk.Radiobutton(parent, 
                                                 text="Recorded Data", 
                                                 variable=self.strvar_radiobtns_data_source, 
                                                 value="recorded_data", 
                                                 command=self.on_radiobtn_data_source)
        radiobtn_recorded_data.grid(row=2, column=0, sticky="w")

        radiobtn_simulated_data = ttk.Radiobutton(parent, 
                                                  text="Simulated Data", 
                                                  variable=self.strvar_radiobtns_data_source, 
                                                  value="simulated_data",
                                                  command=self.on_radiobtn_data_source)
        radiobtn_simulated_data.grid(row=3, column=0, sticky="w")

    def build_frm_playpause_etc(self, parent: ttk.Frame):
        self.strvar_playpause_btn = tk.StringVar(parent, value="▶")
        btn_playpause = ttk.Button(parent, textvariable=self.strvar_playpause_btn, style="PlayPause.TButton", command=self.on_btn_playpause)
        btn_playpause.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, self.padding))
        parent.rowconfigure(0, weight=1)

        lbl_framespersecond = ttk.Label(parent, text="Frames/Second:")
        lbl_framespersecond.grid(row=0, column=1, sticky="e")
        parent.columnconfigure(1, weight=1)

        self.strvar_framespersecond = tk.StringVar(parent, value="Max")
        cmbbox_framespersecond = ttk.Combobox(parent, textvariable=self.strvar_framespersecond, width=4)
        cmbbox_framespersecond["values"] = ["Max", "20", "10", "5", "2", "1"]
        cmbbox_framespersecond.grid(row=0, column=2, sticky="w")

        frm_prev_next_frame = ttk.Frame(parent)
        frm_prev_next_frame.grid(row=1, column=1, columnspan=2, sticky="ew", pady=(self.padding, 0))
        frm_prev_next_frame.columnconfigure(0, weight=1)
        frm_prev_next_frame.columnconfigure(1, weight=1)

        btn_prev_frame = ttk.Button(frm_prev_next_frame, text="< Prev", width=len("< Prev"), style="TButton", command=self.on_btn_prev_frame)
        btn_prev_frame.grid(row=0, column=0, sticky="nsew")

        btn_next_frame = ttk.Button(frm_prev_next_frame, text="Next >", width=len("Next >"), style="TButton", command=self.on_btn_next_frame)
        btn_next_frame.grid(row=0, column=1, sticky="nsew")

        lbl_frame_number = ttk.Label(parent, text="Frame:")
        lbl_frame_number.grid(row=2, column=0, sticky="w")

        self.strvar_frame_number = tk.StringVar(parent, value="0")
        lbl_frame_number_value = ttk.Label(parent, textvariable=self.strvar_frame_number)
        lbl_frame_number_value.grid(row=2, column=1, sticky="w")

    def build_frm_stats(self, parent: ttk.Frame):
        lbl_frm_stats = ttk.Label(parent, text="Statistics", style="Header.TLabel")
        lbl_frm_stats.grid(row=0, column=0, columnspan=4, sticky="w")
        parent.columnconfigure(0, weight=0)
        
        lbl_max = ttk.Label(parent, text="Max:")
        lbl_max.grid(row=1, column=0, sticky="w")
        self.strvar_stats_max = tk.StringVar(parent, value="0.0")
        lbl_max_value = ttk.Label(parent, textvariable=self.strvar_stats_max)
        lbl_max_value.grid(row=1, column=1, sticky="w")

        lbl_min = ttk.Label(parent, text="Min:")
        lbl_min.grid(row=2, column=0, sticky="w")
        self.strvar_stats_min = tk.StringVar(parent, value="0.0")
        lbl_min_value = ttk.Label(parent, textvariable=self.strvar_stats_min)
        lbl_min_value.grid(row=2, column=1, sticky="w")

        lbl_avg = ttk.Label(parent, text="Avg:")
        lbl_avg.grid(row=3, column=0, sticky="w")
        self.strvar_stats_avg = tk.StringVar(parent, value="0.0")
        lbl_avg_value = ttk.Label(parent, textvariable=self.strvar_stats_avg)
        lbl_avg_value.grid(row=3, column=1, sticky="w")

        lbl_std_dev = ttk.Label(parent, text="Std Dev:")
        lbl_std_dev.grid(row=4, column=0, sticky="w")
        self.strvar_stats_std_dev = tk.StringVar(parent, value="0.0")
        lbl_std_dev_value = ttk.Label(parent, textvariable=self.strvar_stats_std_dev)
        lbl_std_dev_value.grid(row=4, column=1, sticky="w")

        parent.columnconfigure(1, weight=1)

    def build_frm_record_data(self, parent: ttk.Frame):
        lbl_recorded_data = ttk.Label(parent, text="Record Data", style="Header.TLabel")
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
        self.strval_recording_directory = tk.StringVar(frm_recording_directory, value="← Select Directory")
        self.lbl_recording_directory = ttk.Label(frm_recording_directory, textvariable=self.strval_recording_directory, style="SmallText.TLabel")
        self.lbl_recording_directory.grid(row=0, column=1, sticky="ew")
        frm_recording_directory.columnconfigure(1, weight=1)

        # Name of file to save the recorded data
        frm_recording_filename = ttk.Frame(parent)
        frm_recording_filename.grid(row=2, column=1, sticky="ew")
        self.strval_recording_filename = tk.StringVar(frm_recording_filename, value="data")
        self.entry_recording_filename = ttk.Entry(frm_recording_filename, textvariable=self.strval_recording_filename, width=8)
        self.entry_recording_filename.grid(row=0, column=1, sticky="ew")
        self.entry_recording_filename.bind("<FocusOut>", lambda e: self.on_btn_new_recording_filename())
        frm_recording_filename.columnconfigure(1, weight=1)
        lbl_csv = ttk.Label(frm_recording_filename, text=".csv")
        lbl_csv.grid(row=0, column=2, sticky="w")
        self.boolvar_append_datetime = tk.BooleanVar(frm_recording_filename, value=True)
        self.chkbtn_append_datetime = ttk.Checkbutton(frm_recording_filename, text="Append Date/Time", style="TCheckbutton", variable=self.boolvar_append_datetime)
        self.chkbtn_append_datetime.grid(row=0, column=3, sticky="w", padx=(self.padding, 0))
        self.chkbtn_append_datetime.bind("<Button-1>", lambda e: self.on_btn_chkbtn_append_datetime())

        # Frame counter and time elapsed
        frm_frm_counter = ttk.Frame(parent)
        frm_frm_counter.grid(row=3, column=0, columnspan=2, sticky="ew")
        lbl_frame_counter = ttk.Label(frm_frm_counter, text="Frames Recorded:")
        lbl_frame_counter.grid(row=0, column=0, sticky="w")
        self.strvar_frame_counter = tk.StringVar(frm_frm_counter, value="0")
        lbl_frame_counter_value = ttk.Label(frm_frm_counter, textvariable=self.strvar_frame_counter)
        lbl_frame_counter_value.grid(row=0, column=1, sticky="w", padx=(self.padding, 0))

    def build_frm_settings(self, parent: ttk.Frame):
        lbl_settings = ttk.Label(parent, text="Settings", style="Header.TLabel")
        lbl_settings.grid(row=0, column=0, columnspan=3, sticky="w")
        parent.columnconfigure(0, weight=1)

        lbl_font_size = ttk.Label(parent, text="Font Size")
        lbl_font_size.grid(row=1, column=0, sticky="w")

        btn_decrease_font_size = ttk.Button(parent, text="-", command=self.on_btn_decrease_font_size)
        btn_decrease_font_size.grid(row=1, column=1, sticky="w")

        btn_increase_font_size = ttk.Button(parent, text="+", command=self.on_btn_increase_font_size)
        btn_increase_font_size.grid(row=1, column=2, sticky="w")


    """ Event Handlers """

    def on_radiobtn_data_source(self):
        new_source = self.strvar_radiobtns_data_source.get()
        pass

    def on_dropdown_select_com_port(self):
        pass

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
        if not self.recording:
            if not self.state.recorded_data_save_directory or not self.state.recorded_data_filename:
                return

            save_name: str = self.state.recorded_data_filename
            if self.state.recorded_data_append_datetime:
                save_name += "_" + time.strftime("%Y-%m-%d_%H-%M-%S")
            save_path = os.path.join(self.state.recorded_data_save_directory, save_name + ".csv")
            
            # Ask user if they want to overwrite the existing file
            if os.path.exists(save_path):
                prompt = f"File '{save_name}' already exists. Recording will overwrite the file. Continue?"
                if messagebox.askyesno("Overwrite File", prompt):
                    self.recording = True
                    self.time_recording_started = time.time()
                    self.refresh_gui()
        
        else:
            self.recording = False
            self.refresh_gui()

    def on_btn_select_recording_directory(self):
        # Select a new directory to save the recorded data
        self.new_state.recorded_data_save_directory = filedialog.askdirectory(mustexist=True)
        self.refresh_gui()
    
    def on_btn_new_recording_filename(self):
        self.new_state.recorded_data_filename = self.strval_recording_filename.get()
        self.refresh_gui()

    def on_btn_chkbtn_append_datetime(self):
        self.new_state.recorded_data_append_datetime = self.boolvar_append_datetime.get()
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


    """ Refresh the GUI """
    # These methods do NOT update the heatmap or anything else that updates continuously. 
    # That is done in a background thread.
    # These functions update the visual state of the GUI widgets (such as disabling or enabling widgets).
    # Most of the event handlers (above) will call 'refresh_gui()' to visually reflect a new GUI state after 
    # a button is clicked or a selection is made.

    def refresh_gui(self):
        self.refresh_frm_data_source()
        self.refresh_frm_playpause_etc()
        self.refresh_frm_record_data()
        self.refresh_frm_stats()
        self.refresh_frm_settings()

        # Save the new state
        self.state = deepcopy(self.new_state)
        self.save_state()

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
            self.chkbtn_append_datetime.configure(state="disabled")
        else:
            self.strvar_record.set("⬤")
            self.btn_recording_directory.configure(state="normal")
            self.entry_recording_filename.configure(state="normal")
            self.chkbtn_append_datetime.configure(state="normal")
        
        # Disable/Enable the record button based on whether a directory has been selected
        if not self.new_state.recorded_data_save_directory:
            self.btn_record.configure(state="disabled")
        else:
            self.btn_record.configure(state="normal")

        # Update the displayed directory name
        if self.new_state.recorded_data_save_directory != self.state.recorded_data_save_directory:
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
            self.new_state.recorded_data_filename = "data"
            self.strval_recording_filename.set(self.new_state.recorded_data_filename)

    def refresh_frm_stats(self):
        pass

    def refresh_frm_settings(self):
        pass


    """ Background Thread: Continuously retrieve data and update the heatmap """
    # NOTE: all changes to GUI widgets should be done in the main thread, not in this thread.
    # When a widget needs to be updated, use 'self.after(0, method_name)' to call a method to run in the main thread

    def threadloop_data_update(self):
        while True:
            update_started: float = time.time()

            # If GUI is paused, don't update the data
            if self.paused:
                time.sleep(0.1)
                continue
                
            # Get new data
            if self.state.data_source == "com_port":
                pass
            elif self.state.data_source == "recorded":
                pass
            elif self.state.data_source == "simulated":
                pass
                
            # Update the heatmap
            self.draw_heatmap()

            # Wait until the next frame should happen
            if self.state.frames_per_second == "Max":
                continue
            time_per_frame = 1 / self.state.frames_per_second
            time_to_wait = time_per_frame - (time.time() - update_started)
            if time_to_wait > 0:
                time.sleep(time_to_wait)

    def draw_heatmap(self, canvas_resized: bool = False):
        pass


    """ Helper methods """


if __name__ == "__main__":
    app = PressureSensorGUI()
    app.mainloop()