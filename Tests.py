from pyftdi.ftdi import Ftdi
import pyftdi.serialext

if __name__ == "__main__":
    print("Hello, World!")
    Ftdi.show_devices()
    port = pyftdi.serialext.serial_for_url("ftdi://ftdi:232:UUT1/1", baudrate=400)
    print(port)
    port.rts = False
    port.dtr = False
