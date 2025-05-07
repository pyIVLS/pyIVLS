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
Best command to run after plugging in is to calibrate, since other commands seem to crash on the first run. 
This doesn't matter on subsequent runs. Commands and more info available in the Manual for the manipulators.
