# Pressure Sensor Project

Force_Sensor_GUI.py - The main in-progress file for talking with the Arduino and displaying the information

[Pressure Mat Design](https://www.instructables.com/O-mat/)

[Demultiplexer Data Sheet](https://github.com/James-Wade1/pressure_sensor/blob/main/Demultiplexer%20Data%20Sheet.pdf) - ours is a CD74HCT238E. Note: A demultiplexer takes one input and directs it to multiple outputs

[Multiplexer Data Sheet](https://github.com/James-Wade1/pressure_sensor/blob/main/Multiplexer%20Datasheet%20TI%20CD74HCT251E.pdf) - ours is a CD74HCT251E. Note: A multiplexer takes multiple inputs and directs one output


## Creating an executable file to distribute the PressureSensorApp

Install `pyinstaller` with pip (in a terminal):

```powershell
pip install pyinstaller
```

Open a terminal and be sure the current directory in the terminal is the directory where `PressureSensorApp.py`, `icon.png`, and any other supporting scripts such as `colormaps.py` are located.

Then run the following command:

```powershell
pyinstaller --noconsole --icon=icon.png --add-data 'icon.png;.' PressureSensorApp.py
```
- `--noconsole` allows the app to run without a separate console window. Remove this option if you would like to debug the executable file using print statements, or see any errors that are produced while it runs. Many times, however, debugging will be easier from within VSCode.
- `--icon=icon.png` determines the icon for the executable `.exe` file itself.
- `--add-data 'icon.png;.'` ensures that the icon will be accessible to the App at runtime (it will be packaged with the executable). This will allow the icon to be set as the window icon (which appears in the top left corner of the app window).

## Colormaps for the GUI heatmap

The `colormaps.py` script contains the colormaps that can be used for the heatmap. The ones listed there wiere chosen because they have been scientifically researched and shown to perceptually represent actual change in values correctly. They are "perceptually uniform." See https://matplotlib.org/stable/users/explain/colors/colormaps.html

To add a new colormap to the available ones, do the following: 

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
2. Copy the printed array into the `colormaps.py` script at the top, saving it as 
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

To use the colormap in the App, you will need to  modify which colormap is used within the `draw_heatmap()` method in the `PressureSensorApp.py` script.