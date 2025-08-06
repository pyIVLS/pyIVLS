import serial
import Final

_BAUDRATE: Final = 128000
_DATABITS: Final = serial.EIGHTBITS
_STOPBITS: Final = serial.STOPBITS_ONE
_PARITY: Final = serial.PARITY_NONE
_TIMEOUT: Final = 5  # seconds.

# open serial port
address = "/dev/serial/by-id/usb-Sutter_Sutter_Instrument_ROE-200_SI9NGJEQ-if00-port0"
ser = serial.Serial(address, baudrate=_BAUDRATE, bytesize=_DATABITS, stopbits=_STOPBITS, parity=_PARITY, timeout=_TIMEOUT)

# read data from the serial port until terminal is closed
while True:
    try:
        data_available = ser.in_waiting
        if data_available:
            print(f"Data available: {data_available} bytes")
            data = ser.read(data_available)  # read available data
        if data:
            print(f"Received data: {data}")
    except KeyboardInterrupt:
        print("Terminating...")
        break
    except Exception as e:
        print(f"Error: {e}")
        break
