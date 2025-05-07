## SETUP
NOTE: the device should first be connected properly to a windows device, with the thorlabs driver software. This makes sure that the correct values are loaded in the EEPROM upon first connection.


# Getting the necessary files
The spectrometer needs a specific file load to initialize. The necessary files are installed with the thorspectra software.
(For me the files were in thorSpectra/CCS/inf/Loader). The file name is CCSxxx.spt (e.g. CCS175.spt).
The files need to be converted to .ihx for fxload to be able to automatically load them on the device. 
this python2 script works for that: https://ftp.dlitz.net/pub/dlitz/cyusb-fw-extract/0.1/
It creates two .ihx files, the second of which is the one we'll be loading on the device.

# udev/rules.d setup
- fill in the path to the corresponding .ihx file
- check that fxload is installed and the path to it is correct (should be usr/(s)bin/fxload)
- Check the vid and pid, the .rules file is set up for a CCS175.

# working?
- The green "ready" light should be lit
- The device should show up with an odd numbered pid (8087 for CCS175)

# requirements (a full list for pyIVLS may be found in README.md)
contourpy==1.2.1
cycler==0.12.1
fonttools==4.53.1
kiwisolver==1.4.5
matplotlib==3.9.1
numpy==2.0.1
packaging==24.1
pillow==10.4.0
pyparsing==3.1.2
python-dateutil==2.9.0.post0
pyusb==1.2.1 #pyusb==1.6.0 is known not to work
six==1.16.0
