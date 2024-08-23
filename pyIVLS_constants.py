# File: pyIVLS_constants.py definitions for the constants used in pyIVLS

### main config name
configFileName = "pyIVLS.ini"


### Keithley constants
KEITHLEY_VISA = "TCPIP::192.168.1.5::INSTR"
LINE_FREQ = 50  # Hz

### Sutter constants
SUTTER_DEFAULT_PORT = (
    "/dev/serial/by-id/usb-Sutter_Sutter_Instrument_ROE-200_SI9NGJEQ-if00-port0"
)

### Thorspec constants
THORSPEC_PID = 0x1313
THORSPEC_VID = 0x8087

### Plugin constants
HOOKS = ["get_setup_interface", "get_functions"]

### conDetect
CONDETECT_PORT = "ftdi://ftdi:232:UUT1/1"
