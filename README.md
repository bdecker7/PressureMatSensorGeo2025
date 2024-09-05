Updated 9/4/2024 by Michael Murdock.

Feel free to reach out to me at mm13000@byu.edu

# Welcome: Getting set up

## Install these:
- [VS Code](https://code.visualstudio.com/download)
- These VS Code extensions:
    - Pylance
    - Python
    - Python Debugger
- [Python (latest version)](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads) (can also be installed from within VSCode; VSCode might prompt you to do this when you first open it)
- [Arduino IDE](https://www.arduino.cc/en/software)

## Download this repository

If you are the first one to do this in the 2024-25 class, just download this repository as a zip file and unzip into a place that makes sense for you on your computer. *Then* create a new repository with this folder as its root directory. This way you will have ownership of the new repository.

If someone on the 2024-25 team has already done this, then you will want to clone this repository onto your computer by:
1. Opening a terminal in the directory where you want the repository to be stored
2. Copying the clone link from GitHub online
3. Running the command `git clone [link]`

## Python packages

You will need to install all the python packages listed in `requirements.txt` using `pip install [package name]` commands.

You can do this in bulk by using `pip install -r requirements.txt`

## GitHub Copilot

GitHub copilot is *very* useful for debugging, understanding the code, and writing new code. You can get a free student license at https://education.github.com/pack

Once your student developer pack is active, you can install the GitHub Copilot extension in VSCode and sign in with your GitHub account to begin using it.

You can also just use Chat GPT, but Copilot allows you do the same things without so much copying and pasting.

# Helpful reference links

[Pressure Mat Design](https://www.instructables.com/O-mat/)

Several good reference files are contained in the `Reference Files` directory.

# Running the code

The main python file is `PressureSensorApp.py`. This can be run from within VSCode, and you do not need to be connected to the physical pressure sensor for it to work. Try running it and selecting "simulated data" as the data source once it opens.

Once it runs, try connecting it to the physical pressure sensor and selecting the appropriate COM port as the data source.

To turn it into an executable, see the "Creating an executable file to distribute the PressureSensorApp" section below.

# TkInter: the engine behind the PressureSensorApp

The graphical user interface (GUI) that you see as the app itself is all built on `Tkinter`, a python interface for `Tk`, which is a popular and versatile GUI platform.

In this code, many of the widgets (buttons, dropdowns, frames, etc.) are created using `ttk`, which is a more modern version of `Tk` that helps the app have a consistent, modern style and look more presentable.

> **Important note:**
>
> I **highly** recommend that you spend some time (one class period or so) learning about `Tkinter` and creating your own mini apps with simple buttons and things before you ever go too deeply into editing this app. This is a **fantastic** resource: https://tkdocs.com/tutorial/intro.html

# Code structure & philosophy: `PressureSensorApp.py`

The first times you are looking at the code (and honestly just whenever you work on it), I would recommend collapsing all of the function definitions so that you aren't scrolling through all of the hundreds of lines of code. This helps the code structure be a lot more visible.

## Structure of `PressureSensorApp.py`

1. Imports
2. Constants:
    - `MIN_VAL` and `MAX_VAL`
    
        The minimum and maximum possible values for data drawn on the heatmap. When raw voltages are read from the Arduino, they are returned as values ranging from 0 (0 V) to 1023 (5 V), so currently those are the minimum and maximum values. This is used in the `draw_heatmap()` method to correctly normalize the data and apply a colormap.

    - `ASPECT_RATIO`
    
        If you ever make a pressure sensor mat with *individual taxels* that are not square, change this value so that the heatmap in the App will accurately portray the shape of those taxels. If the mat is not square because there are simply more taxels in one dimension than in another (but the individual taxels are still square), do not change this number.
    
    - `SERIAL_BAUD_RATE`
        
        This is the rate of communication (in bits/second) between the computer and the Arduino. If this is changed here, it needs to also be changed in the Arduino script `pressure_sensor.ino`.

    - `SERIAL_COMM_SIGNAL`
    
        This is the 'ready' signal sent from the Arduino to the computer when it has finished being set up. It is also the 'send data' signal the computer sends to the Arduino to request that it collect and return new data.

    - `SAVE_DIR`
    
        This is the directory where the App's 'state' is stored on the user's hard drive. On a Windows computer, it ends up being something like `C:\Users\username\AppData\Local\BYU_GEO_GlobalEngineeringOutreach\PressureSensorApp`

    - `STATE_FILE_PATH`

        This is the actual file path where the app's 'state' is stored.

    - `ICON_FILE_NAME`

        This is the name of the icon image file (can be png, jpeg, etc.)

    - `ICON_PATH`

        This is the path to the icon image file. The icon needs to be located in the same directory as `PressureSensorApp.py`

3. `PressureSensorAppState` dataclass and `DEFAULT_STATE` constant.
    
    The App saves its 'state' (including the window size, preferences selected by the user, settings, etc.) to the user's hard drive so that the next time they open the app it will be in the same state. This dataclass contains the variables that are stored in that state (and accessed by the App while it runs). See details below.

4. `PressureSensorApp` class

    This is the main class that sets up and runs the application. See details below.

5. `__main__` method that creates an instance of `PressureSensorApp` and starts it running.

## The `PressureSensorAppState` dataclass

The variables in this class are repeatedly saved as a `json` file to the user's hard drive so that the most recent app configuration can be loaded when the user runs the app again.

## The `PressureSensorApp` class

The `PressureSensorApp` class has the following structure. Note the block comments

### Initialization

This code defines what happens when the `__main__` method of `PressureSensorApp.py` calls 
```python
app = PressureSensorApp()
```
to create an instance of the app class.

It basically has the following purposes:
1. Create an instance of `tk.Tk` using `super().__init__()`
2. Define the title of the main app window with `self.title()`
3. Define what happens when the main window is closed with `self.protocol("WM_DELETE_WINDOW", ...)`
4. Initialize variables such as the whether or not data display is paused, recording is paused, the serial communication object, and the app's state (loaded in from the JSON file on the hard drive if possible)
5. Cause the setup of the app's visual styles by calling `self.setup_gui_styles()`
6. Cause the Tkinter GUI (the app with all its widgets) to be built by calling `self.build_gui()`
7. Create a background thread that will handle continuously reading the data and updating the heatmap by calling `threading.Thread()`. Handling this in a background thread allows the app to not freeze up while new data is being loaded and the heatmap updated.

### Build the GUI widgets

These methods are run **once** when the app is launched. They create the `Tkinter` widgets (buttons, dropdown menus, separators, frames, etc.) that define the appearance and functionality of the app.

In the `build_gui()` method, you will be able to see that the app is organized into three main `Tkinter` frames: one for the heatmap, one for the heatmap colorbar (not yet implemented), and one for the sidebar with buttons and settings and things.

Notice that the heatmap frame is allowed to be resized. This is accomplished through:
- `sticky="nsew"` in the `self.frm_heatmap.grid()` command. This says that the frame should always expand to fill available space in its grid location.
- `self.columnconfigure(0, weight=1)` says that column `0` of `self` (the main app window) expands when the app is resized. The default `weight=0`, which means that no expansion/contraction happens for `self`'s first grid column. Try setting this to `weight=0` and see what happens when you resize the main window to be wider or thinner.
- `self.rowconfigure(0, weight=1)` says that row `0` of `self` also expands.

Within each frame, additional frames and other `Tkinter` widgets are created and then placed into the frames using the `grid()` command.

The methods in this section of the code also bind buttons to events, connecting the buttons, dropdown menus, or other user actions to the "event handler" methods which actually perform an action when called (such as playing or pausing the data display, or changing the data source).

### Event Handlers

These methods are called whenever a user clicks a button, selects an item, or otherwise interacts with the app. 

In most cases, these event handlers will:

1. Change some variable in `self.new_state` 
2. Call `self.refresh_gui()` which will look at `new_state` (and compare it to the previous state `self.app_state`), update the appearance of the app widgets as necessary, and save the `new_state` to the hard drive as a JSON file (by calling `self.save_app_state()`) and redefine `self.app_state` as a copy of `self.new_state`.

### Refresh the GUI

These methods are all called by the first method, `refresh_gui(self)`.

They have the role of updating the visual state of the app's widgets, such as whether or not certain buttons are enabled or disabled, or changing the play/pause button's icon. Things like that.

Most of these haven't really been implemented. When you work on implementing them, they should use `self.new_state` to determine whether certain buttons should be enabled or disabled. 

For example (this is currently implemented), when the directory for recorded files has not been selected yet, it doesn't really make sense for the user to be able to start recording. So the "record" button is disabled until a directory for saving recorded files is selected. This is accomplished with the following code:
```python
if not self.new_state.recorded_data_save_directory:
    self.btn_record.configure(state="disabled")
else:
    self.btn_record.configure(state="normal")
```

### Background Thread: Continuously retrieve data and update the heatmap

These methods are all called by the first method: `threadloop_data_update(self)`.

This first method contains an infinite `while` loop that is running in a separate thread from the main loop.

This handles the following:
1. If the app is "paused" don't do anything. Just skip to the next loop iteration until the app is no longer "paused".
2. Get data from the appropriate source based on the value of `self.app_state.data_source` (either `"com_port"`, `"recorded"`, or `"simulated"`)
3. Use the new data to draw a new heatmap
4. If recording, save the new data to the hard drive or memory (not yet implemented).
5. Wait until the next frame should happen, as long as `self.app_state.frames_per_second` is not `"Max"` (partially implemented).

> **Here is something you can do to get your feet wet with Tkinter and this App**
>
> The code for waiting for the next frame to happen (#5 in the list above) has not yet been fully implemented. I think it is complete within this `threadloop_data_update` method. But the event handling is not in place so that the user can actually *change* the frames per second. When you run the app, you'll notice that you can change the value in the "frames per second" dropdown, but it doesn't affect the data display at all.
> 
> What's wrong?
> 
> Notice that there is currently no event handler method to tell the GUI what to do when the user selects something from the "frames per second" dropdown menu. That method should be named something like `def on_dropdown_framespersecond(self)`, but it doesn't exist.
>
> Try defining an event handler method to handle this. It could look something like this:
> ```python
> def on_dropdown_framespersecond(self):
>   new_val: str = self.strvar_framespersecond.get()
>   if new_val != "Max":
>       # self.new_state.frames_per_second has type `int | Literal["Max"]`
>       new_val = int(new_val)
>   self.new_state.frames_per_second = new_val
>   self.refresh_gui()
> ```
>
> Does it work now? Probably not. You still need to **bind** the event (the user making a selection in the dropdown box) to the the event handler method.
>
> Go find the place where the dropdown menu is created. This is located in the "Build the GUI widgets" section in the `build_frm_playpause_etc()` method. Do you see these lines of code?
> ```python
> self.strvar_framespersecond = tk.StringVar(parent, value="Max")
> cmbbox_framespersecond = ttk.Combobox(parent, textvariable=self.strvar_framespersecond, width=4)
> cmbbox_framespersecond["values"] = ["Max", "20", "10", "5", "2", "1"]
> cmbbox_framespersecond.grid(row=0, column=2, sticky="w")
> ```
> 
> Notice that nowhere in this code is the combobox bound to an event handler. Try asking ChatGPT or GitHub Copilot `"How can I bind an event to a user selecting an item from a ttk Combobox?"`. You could include the code above.
> 
> You should get something that tells you to add the line `cmbbox_framespersecond.bind("<<ComboboxSelected>>", self.on_dropdown_framespersecond)` (or something similar) to the code. Add this line below the above code.
> 
> Run the GUI again and try changing the frames per second. Does it work now?
>
> Hopefully this helps you get a feel for the code structure and the process of implementing new features.

### Helper methods

These method handle opening and closing the serial port (including waiting for a ready signal from the Arduino when attempting to open), as well as saving the app state (an instance of the `PressureSensorAppState` dataclass) to a JSON file on the user's hard drive.

Feel free to add more methods here as needed! (As well as anywhere else in the code of course.)

# Code structure & philosophy: `pressure_sensor.ino`

# Some next steps and needed improvements

## Unimplemented features

There are a number of features for which I created placeholders in the code

## Important improvements

### Smoothing the data display

### Calibrating to display actual forces/pressures

### Mathematical correction for the cross-talk between neighboring taxels ('tactical pixels', aka grid points on the pressure sensor)

## Ideas - do whatever you like with these :)
- displaying the cell numbers alongside the canvas so you can see which way it is oriented (make sure to change this based on orientation selected)
- displaying 1-pixel grid lines through the centers of the grids on the canvas
- An option (checkbox in the 'Settings' area) to display text values on top of the heatmap so you can see what the actual values are at a given taxel.


# Creating an executable file to distribute the PressureSensorApp

Install `pyinstaller` with pip (in a terminal):

```powershell
pip install pyinstaller
```

Open a terminal and be sure the current directory in the terminal is the directory where `PressureSensorApp.py`, `icon.png`, and any other supporting scripts such as `colormaps.py` are located.

Then run the following command:

```powershell
pyinstaller --noconsole --icon=icon.png --add-data 'icon.png;.' PressureSensorApp.py
```
- `--noconsole` allows the app to run without a separate console window. Remove this option if you would like to debug the executable file using print statements, or to be able to see any errors that might be produced while it runs. Many times, however, debugging is easier from within the VSCode debugger, before you create an executable.
- `--icon=icon.png` determines the icon for the executable `.exe` file itself.
- `--add-data 'icon.png;.'` ensures that the icon will be accessible to the App at runtime (it will be packaged with the executable). This will allow the icon to be set as the window icon (which appears in the top left corner of the app window).

# Colormaps for the GUI heatmap

The `colormaps.py` script contains the colormaps that can be used for the heatmap. The ones listed there wiere chosen because they have been scientifically researched and shown to perceptually/visually represent actual changes in numerical values accurately. In other words, they are "perceptually uniform." See https://matplotlib.org/stable/users/explain/colors/colormaps.html for more information about what that means.

## To add a new colormap to the available ones 

1. Get the colormap as an array. Run the following code in a separate python script or a jupyter notebook:
    ```python
    import numpy as np
    from matplotlib iport colormaps as cmaps

    cmap = cmaps.get_cmap('cividis')
    cmap_array = cmap(np.linspace(0, 1, 256))

    print('= np.array([')
    for color in cmap_array:
        print(f'    [{color[0]:.5f}, {color[1]:.5f}, {color[2]:.5f}],')
    print('])')
    ```
2. Copy the **entire** printed array into the `colormaps.py` script at the top, saving it as 
    ```python
    NEW_COLORMAP = np.array([
        [0.267004, 0.004874, 0.329415, 1.0],
        [0.268510, 0.009605, 0.335427, 1.0],
        [0.269944, 0.014625, 0.341379, 1.0],
        # ... (more color entries)
        [0.993248, 0.906157, 0.143936, 1.0],
        [0.996775, 0.901065, 0.142015, 1.0]
    ])
    ```
3. Add the colormap to the `apply_colormap()` method in the `colormaps.py` script:
    ```python
    def apply_colormap(
        normalized_array: np.ndarray, 
        colormap: Literal['viridis', 'plasma', 'inferno', 'magma', 'cividis', 'new_colormap']
    ) -> np.ndarray:
        .
        .
        elif colormap == 'new_colormap':
            cmap_array = NEW_COLORMAP
        .
        .
    ```

## To apply a different colormap to the App
To use the colormap in the App, you will need to  modify which colormap is used within the `draw_heatmap()` method in the `PressureSensorApp.py` script.