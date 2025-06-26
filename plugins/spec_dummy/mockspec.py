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
        if not (1e-6 <= intg_time <= 10):
            raise ValueError("Integration time out of valid range")
        self.integration_time = intg_time
        print(f"[Mock] Integration time set to {intg_time} seconds")
        return True

    def get_device_status(self, debug=False):
        return ["SCAN_IDLE"] if not self.scan_active else ["SCAN_TRANSFER"]

    def start_scan(self):
        self.scan_active = True
        print("[Mock] Starting scan...")
        time.sleep(self.integration_time * 0.5)
        self.scan_active = False

    def start_scan_continuous(self):
        self.scan_active = True
        print("[Mock] Started continuous scan")

    def start_scan_ext_trigger(self):
        self.scan_active = True
        print("[Mock] Waiting for external trigger...")

    def get_scan_data(self):
        print("[Mock] Getting scan data...")
        return self._acquire_raw_scan_data(self._get_raw_data())

    def _get_raw_data(self):
        pixel_count = 3648  # mimicking CCS_SERIES_NUM_RAW_PIXELS
        base = self.integration_time
        # Simulate raw uint16 values (just pretend they come from the hardware)
        return np.random.randint(100, 65535, size=pixel_count, dtype=np.uint16)

    def _acquire_raw_scan_data(self, raw: np.ndarray):
        num_pixels = 3648 - 64  # mimicking scan pixels minus dark pixel offset
        dark_com = np.mean(raw[:64])
        norm_com = 1.0 / (65535 - dark_com)
        # Simulate processed data between 0 and 1
        data = (raw[64:64+num_pixels] - dark_com) * norm_com
        # Offset by integration time to simulate change in intensity
        data += self.integration_time * 0.01
        data = np.clip(data, 0, 1)
        return data

    def read_eeprom(self, addr, idx, length):
        print(f"[Mock] Reading EEPROM at addr={addr}, idx={idx}, length={length}")
        return bytes([int(255 * np.random.rand()) for _ in range(length)])

    def get_firmware_revision(self):
        return (1, 0, int(self.integration_time * 100) % 255)

    def get_hardware_revision(self):
        return (1, 1, int(self.integration_time * 1000) % 255)
