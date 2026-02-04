# ControlMotors

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPL%203.0-blue.svg)](LICENSE)
[![DOI](https://img.shields.io/badge/DOI-pending%20Zenodo-orange.svg)](https://zenodo.org)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://github.com/Alienor134/UC2_Fluorescence_microscope)
[![Arduino Compatible](https://img.shields.io/badge/Arduino-Compatible-00979D?logo=Arduino&logoColor=white)](https://www.arduino.cc/)

---

## Module Information

**Intended Audience**: Users who want to motorize and automate stages or actuators with stepper motors via Arduino and Python. Suitable for microscopy and robotics workflows requiring homing, limit‑switch safety, backlash compensation, and scripted or GUI control of X/Y/Z axes.

---

__keywords__: Stepper motors, Arduino, Python, Freecad, 3D printing

The goal of this module is to provide simple tools to control a motor to automate manual tasks.

An Arduino is used to control the stepper motors with motor shields. The motors are controllable: 
- via Arduino through the serial interface
- with a Python library that communicates serially with the Arduino
- with a user-friendly Tkinter interface based on the Python library
  
The use of limit-switches is integrated and is preferred for safety and reproducibility. 


## Pre-requisites

- Install [ControlSerial](https://github.com/SonyCSLParis/CSL-Serial) and the [Arduino software](https://www.arduino.cc/en/software)
- The stepper motor(s) and motor shield(s) are readily available. Refer to the example gallery for ideas. 
- The code was tested on Windows and Linux




## Hardware :gear:
Check-out the example gallery and the description of how to implement them: turning a manual stage in a motorized one, building a microscope focus module, increasing the displacement range of a piezo-motor, etc. 

| Component|      Quantity      |  Price per unit | Example|  
|----------|:-------------:|------:|------:|  
| Arduino Uno |    1   |   24€ | [Robotshop](https://www.robotshop.com/eu/fr/microcontroleur-arduino-uno-r3-usb.html)|  
|Stepper motor | tested up to 3 | |
| Stepper driver | | |
| Wires | | |


## Software :desktop_computer:

| Software | Version we used | Download |
|----------|:-------------:|:-------------:|  
| Arduino | 1.8.13 | [download](https://www.arduino.cc/en/software)
| Python  | 3.7 |[install](https://github.com/Alienor134/Teaching/blob/master/Python/Installing_Anaconda_creating_environment.md)
| Controlserial | 1.0 | [install](XXX)




## Codes and files provided :chart_with_upwards_trend:

An [Arduino code](Oquam/Oquam.ino) is provided to control the motors. An extra layer is added in Python to conntrol it easily.
[ControlStage](ControlMotors/ControlStage.py) is a class that can be used the following way:



```python
from serial import Serial
from ControlMotors import ControlStage

arduino_port = "COM6"

stage = ControlStage(arduino_port, [1,1,1]) #gearbox ratio of X, Y and Z axis
stage.handle_enable(1)
stage.move_dx(10)
stage.handle_enable(0)
stage.close() 
```


# Instructions

## Connect the Arduino, the stepper driver and the stepper motor
Refer to the documentation of the motor shield/stepper driver you selected to perform the wiring and understand the meaning of the STEP, DIR, ENABLE and limit‑switch pins. For example: [EasyDrive stepper motor driver](https://www.instructables.com/How-to-Interface-Easy-Driver-With-Stepper-Motor-Us/), [XY-motorized stage wiring](https://github.com/SonyCSLParis/Motorized-stage/tree/main/XY-stage), 

## Arduino and Python codes  

First install Arduino IDE and Python 3.7 (links in the **Software** section)  
Second download this repository. We will call the address where you save it "path/to/repo" (for example "C://User/Me/MyRepos").

Before uploading the firmware, make sure that your wiring (STEP, DIR, ENABLE pins for each axis and limit switches) matches the pin definitions in [Oquam/gshield.h](Oquam/gshield.h). If you change the wiring, you must update gshield.h accordingly so that the firmware drives the correct pins.

Open the [Oquam/Oquam.ino](Oquam/Oquam.ino) file. 
Open it with Arduino IDE software by double clicking on the file **Oquam.ino** and upload the codes on the Arduino by clicking on the arrow. If it fails make sure that you are correctly connected to the Arduino: check the card type and the COM port in the "Tools" ("Outils" on the image). 

<p align="center">
<img src="images/upload_arduino.png" width=700"/>
</p>

### Test basic Oquam commands from the Arduino Serial Monitor

You can talk directly to the Oquam firmware from the Arduino IDE Serial Monitor using the RomiSerial protocol. Set the Serial Monitor to **115200 baud** and **"Both NL & CR"**, then type commands of the form:

```text
#<opcode>[args...]:xxxx
```



Some useful examples:

- Identify the controller (should return a string containing "Oquam"):

	```text
	#?:xxxx
	```

<p align="center">
<img src="images/test_arduino_connection.png" width=700"/>
</p>


- Check whether the stage is idle or running:

	```text
	#I:xxxx
	```

- Enable / disable the motor drivers (1 = enable, 0 = disable):

	```text
	#E[1]:xxxx    ; enable motors
	#E[0]:xxxx    ; disable motors
	```

- Read the current stepper positions (returns `[0,x,y,z]`):

	```text
	#P:xxxx
	```

- Configure homing order (X, Y, Z axis indices: 0,1,2; use -1 to skip an axis) and start homing:

	```text
	#h[0,-1,-1]:xxxx   ; home X only
	#H:xxxx            ; start homing sequence
	```

- Queue a relative move with duration `dt` and displacements `dx,dy,dz` in motor steps:

	```text
	#M[2000,1000,0,0]:xxxx   ; move X by +1000 steps over dt=2000
	```

If a command is accepted you will see a response starting with `#0,` (OK). Errors are returned with non‑zero codes and a short message.





To make the interaction user-friendly, we developed a code that sends instructions to the Arduino through the Serial port. It requires Python. If you already use Python for other projects, you will want to keep this code isolated from your current install. This is possible with a virtual environment. Open Anaconda Prompt and navigate to the repository.

### Option 1 – Run the Python package

```
cd ControlMotors
pip install -e .
```

You can launch the interface 

```
from ControlMotors import ControlStage
from ControlMotors import interface_motors

stage = ControlStage("COM6", [1,1,1])
interface_motors(stage)
```
Press the buttons to move by predefined values, or enter manually a value and press the "move" button. The values correspond to logical stage steps, which are converted to motor steps internally using the gear ratios you provide.


<p align="center">
<img src="images/2023-04-27-17-33-56.png" width=400"/>
</p>

### Option 2 – Use a standalone executable (Windows)

If you do not want to install Python, you can use a pre‑built Windows executable of the Tk interface.

**Pre‑requisites:**
- Arduino flashed with the Oquam firmware from [Oquam/Oquam.ino](Oquam/Oquam.ino).
- The ports described in [Oquam/gshield.h](Oquam/gshield.h) match the wiring of the motor shield and the Arduino.
- The Arduino is connected and appears on a COM port (e.g. COM6).
- The correct gear ratios for X, Y, Z are known.


**Download the executable:**

- Go to the ControlMotors GitHub Releases page.
- Download the latest `interface_motors.exe`.


If the automated port connection fails, check that the correct firmware is flashed on the Arduino, that the COM port is correct, and that no other program (e.g. Arduino IDE serial monitor) is using the same port. You can also test manually from the Serial monitor of Arduino IDE that sending 


Note: You will have to determine the backlash of each of your motors: the number of steps you have to turn before the platform moves when you change directions. You will find 4 backlash values, one per direction per motor. We found backlash values between 7 and 12 steps. 


## Hardware tests

The repository contains a small test suite to validate the stage control. By default only unit tests (no hardware) are run; hardware tests have to be started explicitly.

- To run unit tests only (safe on any machine):

	```bash
	cd ControlMotors
	python run_tests.py
	```

- To also run hardware tests (will move the stage):

	```bash
	cd ControlMotors
	python run_tests.py --with-hardware
	```

	Make sure the Arduino with Oquam is connected, the wiring matches Oquam/gshield.h, and the COM ports in the test files reflect your setup.

One useful interactive hardware script is `Tests/hardware/test_XYZ_motors.py`. When you run it with Python it will:

- Ask for the COM port, which axis/axes (X/Y/Z) to test, gear ratios, step size and homing timeout.
- Guide you through manual checks with motors disabled (you move the axis by hand) and enabled.
- Optionally perform programmed moves and homing at the end, while you visually confirm that the stage behaves as expected.

Always ensure the mechanics are safe to move before running hardware tests.


## Examples
### Photos

<img src="https://user-images.githubusercontent.com/20478886/234916331-f735a618-023f-4e14-959b-d6b5563ef728.jpg" width="40%">
</img> <img src="https://user-images.githubusercontent.com/20478886/234916360-f88d8eee-468c-4019-a319-57cfc0e260fb.jpg" width="40%">
</img> <img src="https://user-images.githubusercontent.com/20478886/234917096-ce442fd7-9bc1-49f0-9840-b0620c93ff43.jpg" width="40%">
</img> <img src="https://user-images.githubusercontent.com/20478886/234917655-ea80404b-b252-4a9d-a70e-d05b6db17a9f.jpg" width="40%"></img> 

### How to reproduce: 

https://github.com/SonyCSLParis/Motorized-stage/tree/main/XY-stage  
https://github.com/SonyCSLParis/Motorized-stage/tree/main/Z-stage  
https://github.com/openUC2/UC2-Motorized-XY-Table  


## License

This project firmware (Oquam) and software is licensed under the [GNU General Public License v3.0](https://tldrlegal.com/license/gnu-general-public-license-v3-(gpl-3))

---

## Version Control and Attribution

This project follows **Open Source Hardware Association (OSHWA)** guidelines for version control and attribution.

### Version Control Practice

- **Repository**: Git-based version control with full commit history
- **Submodule Structure**: Part of the UC2 Fluorescence Microscope parent repository
- **Versioning**: Semantic versioning (MAJOR.MINOR.PATCH)
- **Releases**: Tagged releases with automated testing via GitHub Actions

### Attribution Requirements

When using or modifying this software:

1. **Credit the original authors**: Sony Computer Science Laboratories Paris (CSL Paris) and contributors
2. **Maintain license notices**: Keep GPL-3.0 headers in source files
3. **Document modifications**: Clearly state any changes made
4. **Share derivatives**: Derivatives must be released under GPL-3.0 or compatible license

### Contributing

Contributions are tracked through:
- Git commit history (automatic attribution)
- Pull requests on GitHub
- Contributor acknowledgments in release notes

Guidelines:
- Follow existing code style and add docstrings/comments for public APIs
- Update README/docs when behavior or interfaces change
- Include minimal tests or usage examples for new features

---

## License and Legal Information

### Software License

This software is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.

Full license text: [LICENSE](LICENSE)

### Firmware License

The Arduino firmware (Oquam) used by this module is licensed under GPL-3.0.

### Related Licenses

- **Parent Project** (UC2 Fluorescence Microscope): Hardware under CERN-OHL-S-2.0, Software under GPL-3.0
- **Documentation**: CC BY-SA 4.0

---

## 🔗 Cross-References and Navigation

### Within UC2 Fluorescence Microscope Project

- **Main Repository**: [UC2_Fluorescence_microscope](https://github.com/Alienor134/UC2_Fluorescence_microscope)
- **Documentation Home**: https://alienor134.github.io/UC2_Fluorescence_microscope/docs/
- **Build Instructions**: https://alienor134.github.io/UC2_Fluorescence_microscope/docs/build
- **Bill of Materials**: https://alienor134.github.io/UC2_Fluorescence_microscope/docs/bill_of_materials
- **Automation Guide**: https://alienor134.github.io/UC2_Fluorescence_microscope/docs/automate
- **Examples**: https://alienor134.github.io/UC2_Fluorescence_microscope/docs/example

### Related Control Modules

| Module | Purpose | Documentation |
|--------|---------|---------------|
| [ControlSerial](../ControlSerial/) | Arduino-Python communication | [README](../ControlSerial/README.md) |
| [ControlCamera](../ControlCamera/) | Camera acquisition and control | [README](../ControlCamera/README.md) |
| [ControlLight](../ControlLight/) | Laser and LED control | [README](../ControlLight/README.md) |
| **ControlMotors** | XYZ stage and motor control | [README](README.md) (this file) |


