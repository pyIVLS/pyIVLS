### Hardware abstraction layer for Sutter instrument MPC-325
Simple abstaction layer to use the micromanipulators made in python.
Implements basic functionality, such as:
  - Initialization and calibration
  - moving to a spesified position
  - handling devices / getting their status.

Communicates to the device with VCP-drivers through a virtual serial port.

# Installation:
Add 99-suttermpc325.rules to /etc/udev/rules.d to automatically load basic drivers and open a port.
You might need to fiddle around with the ports a bit to find the correct one, default is set to access the instrument by id. see: mpc-hal.py

# Notes
I have a theory: Sutter dislikes getting manual inputs from the ROE-200 while it is being externally controlled. Pure software controls seem to work fine, but adding manual moves and device changes during external control seems to decrease stability. Is the ROE-200 buffering something into the serial port during manual moves??
