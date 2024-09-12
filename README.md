Updated 9/12/2024 by Michael Murdock.

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

You will need to install all the python packages listed in `requirements.txt` using `pip install [package name]` commands in the terminal.

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
> I **highly** recommend that you spend some time (one class period or so at least) learning about `Tkinter` and creating your own apps with simple buttons and things before you **ever** go too deeply into editing this app. Here is a really great resource: https://tkdocs.com/tutorial/intro.html

# Code structure & philosophy: `PressureSensorApp.py`

This is the code that runs the App. It displays a "heatmap" visualization of the pressure array, gathers that data from the Arduino (as applicable), and allows the user to change some settings, etc.

The first times you are looking at the code in `PressureSensorApp.py` (and honestly just whenever you work on it), I would recommend collapsing all of the function definitions so that you aren't scrolling through all of the hundreds of lines of code. This helps the code structure be a lot more visible.

## Structure of `PressureSensorApp.py`

1. Imports
2. Constants:
    - `MIN_VAL` and `MAX_VAL`
    
        The minimum and maximum possible values for data drawn on the heatmap. When raw voltages are read from the Arduino, they are returned as values ranging from 0 (0 V) to 1023 (5 V), so currently those are the minimum and maximum values. This is used in the `draw_heatmap()` method to correctly normalize the data and apply a colormap.

    - `ASPECT_RATIO`
    
        If you ever make a pressure sensor mat with *individual taxels* that are not square (meaning the spacing between taxels is different in one dimension than the other), change this value so that the heatmap in the App will accurately portray the shape of those taxels. If the mat is not square because there are simply more taxels in one dimension than in another (but the individual taxels are still square), do not change this number.
    
    - `SERIAL_BAUD_RATE`
        
        This is the rate of communication (in bits/second) between the computer and the Arduino. If this is changed here, it needs to also be changed in the Arduino script `pressure_sensor.ino`.

    - `SERIAL_COMM_SIGNAL`
    
        This is the 'ready' signal sent from the Arduino to the computer when it has finished being set up. It is also the 'send data' signal the computer sends to the Arduino to request that it collect and return new data.

    - `SAVE_DIR`
    
        This is the directory where the App's 'state' is stored on the user's hard drive. On a Windows computer, it ends up being something like `C:\Users\username\AppData\Local\BYU_GEO_GlobalEngineeringOutreach\PressureSensorApp`

    - `STATE_FILE_PATH`

        This is the actual file path where the app's 'state' is stored. On Windows, something like: `C:\Users\username\AppData\Local\BYU_GEO_GlobalEngineeringOutreach\PressureSensorApp\`

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
5. Wait until the next frame should happen, as long as `self.app_state.frames_per_second` is not set to `"Max"` (partially implemented).

> **Here is something you can do to get your feet wet with Tkinter and this App**
>
> The code for waiting for the next frame to happen (#5 in the list above) has not yet been fully implemented. I think it is complete within this `threadloop_data_update` method. But the event handling is not in place so that the user can actually *change* the frames per second. When you run the app, you'll notice that you can change the value in the "frames per second" dropdown, but it doesn't affect the data display at all.
> 
> What's wrong?
> 
> Look at the code and notice that there is currently no event handler method to tell the GUI what to ***do*** when the user selects something from the "frames per second" dropdown menu. That method should be named something like `def on_dropdown_framespersecond(self)`, but it doesn't exist.
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
> Go find the place where the dropdown menu widget is ***created***. This is located in the "Build the GUI widgets" section in the `build_frm_playpause_etc()` method. Do you see the lines of code listed below?
> ```python
> self.strvar_framespersecond = tk.StringVar(parent, value="Max")
> cmbbox_framespersecond = ttk.Combobox(parent, textvariable=self.strvar_framespersecond, width=4)
> cmbbox_framespersecond["values"] = ["Max", "20", "10", "5", "2", "1"]
> cmbbox_framespersecond.grid(row=0, column=2, sticky="w")
> ```
> 
> Notice that nowhere in this code is the combobox widget bound to an event handler. The GUI doesn't know there should be any connection between the dropdown menu being selected, and the function `on_dropdown_framespersecond` being called.
>
> Try asking ChatGPT or GitHub Copilot `"How can I bind an event to a user selecting an item from a ttk Combobox?"`. You could include the code above.
> 
> You should get something that tells you to add the line `cmbbox_framespersecond.bind("<<ComboboxSelected>>", self.on_dropdown_framespersecond)` (or something similar) to the code. Add this line below the above code.
> 
> Run the GUI again and try changing the frames per second. Does it work now?
>
> Hopefully this helps you get a feel for the code structure and the process of implementing new features into the App.

### Helper methods

These method handle opening and closing the serial port (including waiting for a ready signal from the Arduino when attempting to open), as well as saving the app state (an instance of the `PressureSensorAppState` dataclass) to a JSON file on the user's hard drive.

Feel free to add more methods here as needed! (As well as anywhere else in the code of course.)

# Code structure & philosophy: `pressure_sensor.ino`

This is the code that runs on the Arduino.

Its purpose is to gather voltage values (analog readings running from `0` to `1023`, or 10-bit integers) from each of the "taxels" on the pressure mat and send those voltage readings to the computer over the serial port.

## Structure of `pressure_sensor.ino`

1. `// #define DEBUG`

    Uncomment this line (and re-upload the sketch to the Arduino) to run the Arduino in "debugging" mode. It will then automatically gather data and send it once per second. It will send the data as strings rather than in binary format. This is slower but it allows bug isolation. In other words, it allows you to view the state/output of the Arduino in a more raw way, without the App, in order to diagnose whether a bug is caused by the Arduino and/or hardware side of things, or if it's the App.

2. Pin definitions

    Read these pin definitions as `[pin name in the code] [pin # on the Arduino board]`

    - `DS0`, `DS1`, `DS2`

        These pins control the output pin of the demultiplexers

    - `D1E`, `D2E`

        These pins control whether the first and second demultiplexers are enabled.

    - `MS0`, `MS1`, `MS2`, `MS3`

        These pins control the input pin of the multiplexer
    
    - `VOLTAGE_READ`

        This pin is the pin that reads the output of the multiplexer as an analog value from `0` to `1023` (a 10-bit integer)

    - `COL`

        This defines the number of columns in the pressure sensor matrix of "taxels". This cannot be greater than the number of possible output pins of input pins of the multiplexer.
    
    - `ROW`

        This defines the number of rows in the pressure sensor matrix. It cannot be greater than the number of output pins on the demultiplexer(s).
    
    - `GET_DATA`

        This defines the "ready" byte (currently `0000 0001` or `1` in decimal) that the App will send to the Arduino to tell it to collect data. It is also what the Arduino sends to the App to inform it of a correct setup (serial port connection ready to be used).
    
3. Multiplexer (Mux) and Demultiplexer (Demux) selector arrays

    These `bool` arrays define which pins on the demultiplexer and multiplexer should be enabled in order to select the correct input/output pin.

    To understand these arrays, look at the first column (the first entry in each of the arrays). The first column has the structure `LOW` `LOW` `LOW` `LOW`. If you translate this to binary, this is `0000`, or the number `0` (in decimal). This corresponds to selecting the first input pin on the multiplexer. For the demultiplexers, we only use the first 3 arrays (because there are only 8 ($ 2^3 $) output pins per demultiplexer), for which the first column would be `LOW` `LOW` `LOW`, or `000` in binary, or `0` (decimal). Again, selecting the first pin (this time an *output* pin rather than *input* since it is a demultiplexer).

    Now lets look at the 6th column. For the multiplexer (all 4 arrays), this has the structure: `HIGH` `LOW` `HIGH` `LOW`. In binary this is `1010`. This corresponds to the number `5` in decimal ("little-endian" byte order, meaning the bytes are read from right to left), or the 6th input pin. For the demultiplexer, this is `HIGH` `LOW` `HIGH`, or `101` in binary, or `5` in decimal, or the 6th output pin.

    The second from the last column is `LOW` `HIGH` `HIGH` `HIGH`, or `0111` in binary, or `14`, or the 15th input pin on the multiplexer. For the demultiplexers, the last column (first three arrays only) is `LOW` `HIGH` `HIGH`, or `011` in binary, or `6` in decimal, which is the 7th output pin. In this case, the code needs to have enabled the second demux and disabled the first one, so that this will correspond to the *15th* output pin between the two demultiplexers.

4. Function declarations and definitions

    - `setup()`

        Open the serial port with baud rate `115200` (bits per second)

        Set the pin configurations for the mux and demux.

        When not in debug mode, send a "ready" message to th computer

    - `loop()`

        The main loop.

        In regular mode:

            Wait for a prompt from the App

            Send the size of the data array (rows and columns)

            Collect data and send it
        
        In debug mode:

            Collect and send data in debugging mode (sends strings rather than binary format data)

            Wait for 500 ms to collect and send data again

    - `demuxSetup()` and `muxSetup()`

        Set the pin modes and starting states of the pins

    - `muxSelect(int i)`

        Select an input pin on the multiplexer corresponding to the value of `i` (which can range from `0` to `15`)

    - `demuxSelect(int i)`

        Select an output pin from the demultiplexers corresponding to the value of `i` which can range from `0` to `15`.

        Currently, since we have two 8-channel digital demultiplexers, we have to have some logic to decide which one should be enabled and which disabled in order to simulate having 16 output pins.
    
    - `sendTwoByteInt(uint16_t value)`

        Send a 16-bit integer over serial (literally just sends the two bytes; does not send them as a string)

    - `collectAndSendData(bool debug = False)`

        Collects data at each of the row/column combinations on the pressure mat.

        When each new row or new column is selected, there is a small delay in the code to ensure that the voltage at that pin has a chance to stabilize. Currently this is set with `delayMicroseconds(100)` to a value of $100~\mu s$ ($0.1~ms$). However it might be worth looking into if this is enough or if it could be diminished further to increase the speed of the Arduino code.

        If in debug mode, sends the data as a string with a space after it.

        If not in debug mode, send the code as a binary two-byte int (which is faster both for sending and for the App to receive and parse).

# Some next steps and needed improvements

## Unimplemented features

There are a number of features for which I created visual placeholders in the app (such as buttons) but besides the buttons being created, the features aren't actually implemented. If you click on the buttons, it does nothing.

The work to implement these features involves defining event handlers for when those buttons are clicked, binding the buttons to those event handlers, and then (as needed) adding helper methods (or adding details to existing methods) to actually carry out the work involved in whatever the feature is.

Here are some of my thoughts about these features.

## Important improvements

### Smoothing the data display

Take a look imports at the top of the `PressureSensorApp.py` file. Find the commented out line (and uncomment it): 
```python
from scipy import ndimage
```

Now look in the `draw_heatmap(self, canvas_resized: bool = False)` method in the "Background Thread" section of the `PressureSensorApp.py` file. Find the commented out line that reads (and uncomment it):
```python
ndimage.zoom(heatmap_image, zoom=4, order=3, mode='nearest')
```

Now run `PressureSensorApp.py`. Pretty cool right?

You should especially try and do this with the actual pressure mat (and put your hand on it and move it around), not just with simulated data, if you can.

This is a feature that I added, but then it caused problems when creating an executable with the `pyinstaller` package (see the section below on how to do that). It seemed to create the executable just fine, but then the file wouldn't run. The problem disappeared as soon as I was no longer trying to import `scipy`. Maybe it'll work for you! It's worth a try. Try it out on your computer and on others' computers to be sure if it seems like its working.

If it doesn't work, I suggest implementing the functionality of the `scipy.ndimage.zoom()` using `numpy`. I'm not sure exactly how to do this, but just spend some time learning about `scipy.ndimage.zoom()` and what it does, and then have GitHub Copilot or ChatGPT help you actually implement it. 

Ideally, package that functionality into a single helper method that you can call, so you can simply replace the line:
```python
ndimage.zoom(heatmap_image, zoom=4, order=3, mode='nearest')
```
with
```python
myzoom(heatmap_image, zoom=4, order=3)
```
or something along those lines.

### Calibrating to display actual forces/pressures

This is an important need! We want to be able to display actual forces or pressures for each taxel on the pressure mat.

Currently, it displays the raw voltage values (from `0` to `1023`).

You'll need to characterize how those voltage values correspond to pressures/forces, and create a method that calibrates between the two.

The place where you'll call that method is probably here:
```python
def get_data_from_com_port(self) -> np.ndarray:
    ...
    # Get the raw data from the sensor
    raw_data: np.ndarray = self.serial_read_int_array()
    # data = YOUR_METHOD(raw_data)
    return data
```

### Mathematical correction for the cross-talk between neighboring taxels

Open the App and connect it to the pressure sensor. Pick a specific taxel and press really hard on it, but try to keep your pressure steady. Note the color.

Now pick a taxel in the same row or same column. Keeping the pressure on the first taxel, add pressure to the new taxel. You should notice that in one of the cases at least (same row or same column), when you apply pressure on the second taxel, the voltage measured by the Arduino goes *down* for the first taxel, even though you have been keeping the pressure constant.

This is called cross-talk. See the `Resistive Fabric-Based Sensor.pdf` file in the `Reference Files` directory for info about this. 

This needs to be mathematically calibrated for. 

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