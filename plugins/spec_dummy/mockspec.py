import numpy as np
import time


class MockCCSDRV:
    def __init__(self):
        self.integration_time = 0.01
        self.scan_active = False

    def open(self, spectrometerVID, spectrometerPID, integration_time=0.01):
        self.integration_time = integration_time
        return True

    def close(self):
        pass
    def get_integration_time(self):
        return self.integration_time

    def pipe_status(self):
        return "[Mock] Pipe OK"

    def set_integration_time(self, intg_time: float) -> bool:
        if not (1e-6 <= intg_time <= 60):
            raise ValueError("Integration time out of valid range")
        self.integration_time = intg_time
        return True

    def get_device_status(self, debug=False):
        return ["SCAN_IDLE"] if not self.scan_active else ["SCAN_TRANSFER"]

    def start_scan(self):
        self.scan_active = True
        time.sleep(self.integration_time * 1)
        self.scan_active = False

    def start_scan_continuous(self):
        self.scan_active = True

    def start_scan_ext_trigger(self):
        self.scan_active = True

    def get_scan_data(self):
        data = (np.random.rand(3648)) / 2 # from 0 to 0.5
        data -= 0.4 # from -0.4 to 0.1
        data = data + (self.integration_time)
        return np.array(data)


    def read_eeprom(self, addr, idx, length):
        return bytes([int(255 * np.random.rand()) for _ in range(length)])

    def get_firmware_revision(self):
        return (1, 0, int(self.integration_time * 100) % 255)

    def get_hardware_revision(self):
        return (1, 1, int(self.integration_time * 1000) % 255)
