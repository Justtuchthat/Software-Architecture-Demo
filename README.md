# Software Architecture Demo

Using PyGame to visually show how sensors in the field will communicate with each other.

## Installation

Using venv and pip:

```bash
# Initialize a new Python virtual environment
python -m venv venv

# Activate the venv (Linux/MacOS)
source activate venv/bin/activate

# Activate the venv (Windows cmd.exe)
venv/Scripts/activate.bat

# Activate the venv (Windows PowerShell)
venv/Scripts/Activate.ps1

# Install the requirements to run the project
pip install -r requirements.txt

# Run the project
python main.py

# Once done, deactivate the venv
deactivate
```

## Key binds

After running the project, you will start in 'mode 0'. Pressing keyboard numbers 0, 1, and 2 will change the project into their respective modes. Pressing keyboard number 3 will generate a regular triangular grid of sensors, each with 180 units of distance and a 200-unit radius of range. 


### Mode 0

This mode allows for adding sensors in the field. First, mouse over the center of where the sensor should be and left-click. Then move the mouse the desired distance for the range the sensor can communicate, and left click again. This places the sensor and allows all sensors to regenerate the communication network. The blue mesh network and the blinking sensors that are out of range are only visual. These cues are not used in communication, as this uses a different mesh network.

### Mode 1

This mode allows for 'disabling' or removing sensors. Hover over the center of the sensor that needs to be removed and left-click. It is now removed. Although the visual mesh is regenerated, the communication network is not regenerated to simulate in-field failure of sensors. Only when placing new sensors does the communication mesh network regenerate.

### Mode 2

To allow for communication from any sensor to the hub, only the hub can print to the command line. When in mode 2, click any sensor like you would in mode 1, but now it will send a message meant for the hub, which will be printed once received by the hub, using the MQTT-like communication mesh network. 

## Communication

As stated in the Mode 2 subsection of the Keybinds section, an MQTT-like mesh network is used for communication. While it was possible to install libraries to mimic how MQTT would work out in the field, it is also possible to do this using only a Python implementation. For ease of execution on new PCs, the second approach was chosen. Although it is not an exact implementation of MQTT that is used for this, the manner of communication does resemble MQTT.