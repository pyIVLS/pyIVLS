import numpy as np
import time


class MockCCSDRV:
    def __init__(self):
        self.integration_time = 0.01
        self.single_scan_requested = False
        self.continuous_scan_requested = False
        self.ext_scan_requested = False

    def open(self, spectrometerVID, spectrometerPID, integration_time=0.01):
        self.integration_time = integration_time
        print(f"[Mock] Opened connection to device VID: {hex(spectrometerVID)}, PID: {hex(spectrometerPID)} with integration time {integration_time}s")
        return True

    def close(self):
        print("[Mock] Closed connection to device")
        pass

    def get_integration_time(self):
        print(f"[Mock] Current integration time: {self.integration_time}s")
        return self.integration_time

    def pipe_status(self):
        print("[Mock] Pipe OK")
        return "[Mock] Pipe OK"

    def set_integration_time(self, intg_time: float) -> bool:
        if not (1e-6 <= intg_time <= 60):
            raise ValueError("Integration time out of valid range")
        self.integration_time = intg_time
        print(f"[Mock] Set integration time to: {self.integration_time}s")
        return True

    def get_device_status(self):
        statuses = []
        if self.ext_scan_requested:
            statuses.append("SCAN_EXT_TRIGGER")
        elif self.continuous_scan_requested:
            statuses.append("SCAN_TRANSFER")
        elif self.single_scan_requested:
            statuses.append("SCAN_TRANSFER")
        else:
            statuses.append("SCAN_IDLE")
        print(f"[Mock] Device status: {statuses}")
        return statuses

    def start_scan(self):
        self.single_scan_requested = True
        print("[Mock] Starting single scan...")
        time.sleep(self.integration_time * 1)
        self.single_scan_requested = False

    def start_scan_continuous(self):
        print("[Mock] Starting continuous scan...")
        self.continuous_scan_requested = True

    def start_scan_ext_trigger(self):
        print("[Mock] Starting external trigger scan...")
        self.ext_scan_requested = True

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
