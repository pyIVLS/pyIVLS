import numpy as np
import time


class MockCCSDRV:
    def __init__(self):
        self.integration_time = 0.01
        self.scan_active = False

    def open(self, spectrometerVID, spectrometerPID, integration_time=0.01):
        self.integration_time = integration_time
        print(f"[Mock] Opened mock device with VID: {spectrometerVID}, PID: {spectrometerPID}")
        return True

    def close(self):
        print("[Mock] Closed mock device.")

    def get_integration_time(self):
        return self.integration_time

    def pipe_status(self):
        return "[Mock] Pipe OK"

    def set_integration_time(self, intg_time: float) -> bool:
        if not (1e-6 <= intg_time <= 60):
            raise ValueError("Integration time out of valid range")
        self.integration_time = intg_time
        print(f"[Mock] Integration time set to {intg_time} seconds")
        return True

    def get_device_status(self, debug=False):
        return ["SCAN_IDLE"] if not self.scan_active else ["SCAN_TRANSFER"]

    def start_scan(self):
        self.scan_active = True
        print("[Mock] Starting scan...")
        time.sleep(self.integration_time * 1)
        print("[Mock] Scan completed")
        self.scan_active = False

    def start_scan_continuous(self):
        self.scan_active = True
        print("[Mock] Started continuous scan")

    def start_scan_ext_trigger(self):
        self.scan_active = True
        print("[Mock] Waiting for external trigger...")

    def get_scan_data(self):
        print("[Mock] Getting scan data...")
        data = (np.random.rand(3648) - 1) / 100 + self.integration_time / 10
        return np.array(data)


    def read_eeprom(self, addr, idx, length):
        print(f"[Mock] Reading EEPROM at addr={addr}, idx={idx}, length={length}")
        return bytes([int(255 * np.random.rand()) for _ in range(length)])

    def get_firmware_revision(self):
        return (1, 0, int(self.integration_time * 100) % 255)

    def get_hardware_revision(self):
        return (1, 1, int(self.integration_time * 1000) % 255)
