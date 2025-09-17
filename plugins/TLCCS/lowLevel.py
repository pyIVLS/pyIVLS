from array import array
import usb.core
import usb.util
import TLCCS_const as const


class LLIO:
    """This class handles low level usb communication with a
    Thorlabs ccs-device. Communication is done with pyusb.
    Includes control IN/OUT transfers and raw (bulk) read.
    """

    def __init__(self, THORSPEC_VID, THORSPEC_PID):
        self.vid = THORSPEC_VID
        self.pid = THORSPEC_PID
        self.bulk_in_pipe = None
        self.timeout = None
        self.dev = None
        self.connected = False

    def _connect(self) -> bool:
        """private function to connect to the device.

        Raises:
            ValueError: device not found with the given vid and pid
            ConnectionError: usb error when connecting to the device
        """
        try:
            if not self.connected:
                self.dev = usb.core.find(idVendor=self.vid, idProduct=self.pid)
                if self.dev is None:
                    raise ValueError("Device not found")
                self.dev.set_configuration()
                self.connected = True
                return True
            return False
        except usb.core.USBError as e:
            raise ConnectionError(f"Failed to connect to device: {e}") from e

    def __del__(self):
        if self.dev is not None:
            self.close()

    def open(self) -> bool:
        """interface to open the connection and set default values for
        bulk_in_pipe and timeout."""
        if self._connect():
            self.bulk_in_pipe = const.LL_DEFAULT_BULK_IN_PIPE
            self.timeout = 0 # for no timeout
            self.flush()
            return True
        return False

    def close(self) -> None:
        """Closes the connection to the device. Disposes resources and
        sets dev to None."""
        usb.util.dispose_resources(self.dev)
        self.dev = None
        self.connected = False

    def get_bulk_in_status(self) -> str:
        """Send a standard control transfer to the device to get the status of the bulk_in_pipe. NOTE: Unused and only briefly tested.

        Returns:
            str: Usb status of the bulk_in_pipe. Either "USB_PIPE_READY", "USB_PIPE_STALLED" or "USB_PIPE_STATE_UNKNOWN"
        """
        # Prepare the request
        bmRequestType = usb.util.build_request_type(
            usb.util.ENDPOINT_IN,
            usb.util.CTRL_TYPE_STANDARD,
            usb.util.CTRL_RECIPIENT_ENDPOINT,
        )
        bRequest = 0
        wValue = 0
        wIndex = self.bulk_in_pipe
        length = 2
        attr_value = "DEFAULT"
        # Perform the control transfer
        statusdata = self.dev.ctrl_transfer(bmRequestType, bRequest, wValue, wIndex, length, timeout=self.timeout)

        # Check the returned status
        if len(statusdata) < 2:
            attr_value = "USB_PIPE_STATE_UNKNOWN"
        if statusdata[0] & 1:  # Halt bit
            attr_value = "USB_PIPE_STALLED"
        else:
            attr_value = "USB_PIPE_READY"

        return attr_value

    def flush(self):
        """Reads the bulk_in_pipe until timeout and throws out the result."""
        try:
            full_flush_size = const.CCS_SERIES_NUM_RAW_PIXELS * 2
            self.dev.read(self.bulk_in_pipe, full_flush_size, timeout=2000)
            return True
        except Exception:
            return True

    def read_raw(self, readTo: array):
        """Bulk read from default bulk_in_pipe. Note: Reading is done in bytes. Catches errors with try-except

        Args:
            readTo (array): data is read into this. The size of the array specifies the size of the read.
        """
        try:
            self.dev.read(self.bulk_in_pipe, readTo, timeout=self.timeout)
        except usb.core.USBError as e:
            print(f"USB error in TLCCS read_raw: {e}")

    def control_out(self, bRequest, payload, bmRequestType=0x40, wValue=0, wIndex=0):
        """Sends a control OUT transfer to the device. (usually) For setting data.

        Args:
            bRequest (hexadecimal): type of request, provided in const.py
            payload (array): data payload to be transfered with the command, if needed.
            bmRequestType (hexadecimal, optional): specifies type of transfer. Defaults to 0x40.
            wValue (int, optional): Defaults to 0.
            wIndex (int, optional): Defaults to 0.
        """
        try:
            self.dev.ctrl_transfer(bmRequestType, bRequest, wValue, wIndex, payload, timeout=self.timeout)
        except usb.core.USBError as e:
            print(f"USB error in TLCCS control_out: {e}")

    def control_in(self, bRequest, readTo: array, bmRequestType=0xC0, wValue=0, wIndex=0):
        """Sends a control IN transfer and reads data. (usually) For reading data.

        Args:
            bRequest (hexadecimal): type of request, provided in const.py
            readTo (array): data is read into this. The size of the array specifies the size of the read.
            bmRequestType (hexadecimal, optional): specifies type of transfer.. Defaults to 0xC0.
            wValue (int, optional): Defaults to 0.
            wIndex (int, optional): Defaults to 0.

        """
        try:
            self.dev.ctrl_transfer(bmRequestType, bRequest, wValue, wIndex, readTo, timeout=self.timeout)
        except usb.core.USBError as e:
            print(f"USB error in TLCCS control_in: {e}")
