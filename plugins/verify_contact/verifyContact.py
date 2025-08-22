#

# detects 20 ohms -> slow down, don't move too far from there
#
import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class ManipulatorInfo:
    mm_number: int
    smu_channel: str
    condet_channel: str
    threshold: int
    stride: int
    sample_width: float
    function: str
    last_z: Optional[int] = None
    spectrometer_height: Optional[int] = None

    def __post_init__(self):
        """Generates new field (self.function) after __init__ is called"""
        if self.smu_channel == "spectrometer" or self.condet_channel == "spectrometer":
            self.function: str = "spectrometer"
        elif self.smu_channel == "none" or self.condet_channel == "none":
            self.function: str = "unconfigured"
        elif self.smu_channel == "" or self.condet_channel == "":
            self.function: str = "unconfigured"
        else:
            self.function: str = "normal"

    def with_new_settings(self, **kwargs) -> "ManipulatorInfo":
        """
        Creates a new ManipulatorInfo instance with updated settings.
        This ensures __post_init__ is called to recalculate derived fields.

        Args:
            **kwargs: Fields to update (e.g., threshold=100, stride=5)

        Returns:
            ManipulatorInfo: New instance with updated settings
        """
        # Get current values as a dict
        current_values = self.to_dict()

        # Update with provided kwargs
        current_values.update(kwargs)
        return ManipulatorInfo(**current_values)

    def to_dict(self) -> dict:
        """Converts the ManipulatorInfo instance to a dictionary."""
        return {"mm_number": self.mm_number, "smu_channel": self.smu_channel, "condet_channel": self.condet_channel, "threshold": self.threshold, "stride": self.stride, "sample_width": self.sample_width, "function": self.function, "last_z": self.last_z, "spectrometer_height": self.spectrometer_height}

    def to_named_dict(self) -> dict:
        """Returns a dictionary with named keys for each field. Useful for saving to ini for instance."""
        return {
            f"{self.mm_number}_smu": self.smu_channel,
            f"{self.mm_number}_con": self.condet_channel,
            f"{self.mm_number}_res": self.threshold,
            f"{self.mm_number}_last_z": self.last_z,
            "stride": self.stride,
            "sample_width": self.sample_width,
            "spectrometer_height": self.spectrometer_height,
        }

    def validate(self) -> list[str]:
        """Returns a list of validation errors, if any."""
        errors = []
        if self.threshold <= 0:
            errors.append("Invalid threshold")
        if self.stride <= 0:
            errors.append("Invalid stride")
        if self.sample_width <= 0:
            errors.append("Invalid sample width")
        if self.function == "spectrometer" and self.spectrometer_height is None:
            errors.append("Spectrometer height is not set")
        if self.function == "normal" and self.last_z is None:
            errors.append("Last known position is not set for normal function")
        return errors

    def is_configured(self) -> bool:
        """Returns True if the manipulator is configured, False otherwise."""
        return self.function != "unconfigured"

    def needs_z_pos(self) -> bool:
        """Returns True if the manipulator needs a Z position to be set, False otherwise."""
        return self.function == "normal" and self.last_z is None


class touchDetect:
    MAX_CORRECTION_ATTEMPTS = 10  # maximum attempts to correct non-contacting manipulators
    MONITORING_DURATION = 2  # seconds, to monitor stability after initial contact
    APPROACH_MARGIN = 200  # microns, margin before last known position

    def __init__(self, log=None):
        # Store logging functions from GUI if provided
        self.log = log

    def _log(self, message):
        if self.log:
            self.log(message)

    def check_all_contacting(self, smu: object, con: object, manipulators: list[ManipulatorInfo]) -> bool:
        """
        Checks if all specified manipulators are in contact.

        Args:
            smu (object): SMU object for resistance measurement
            manipulators (list[ManipulatorInfo]): List of manipulator information objects

        Returns:
            bool: True if all manipulators are in contact, False otherwise
        """
        for info in manipulators:
            # filter out unconfigured manipulators
            if not info.is_configured():
                continue
            
            # setup resmes
            resmes_status, resmes_state = self._manipulator_measurement_setup(smu, con, info)
            assert resmes_status == 0, f"Failed to setup resmes for manipulator {info.mm_number}: {resmes_state}"

            # monitor
            if not self._monitor_contact_stability(smu, info, self.MONITORING_DURATION):
                self._log(f"Manipulator {info.mm_number} lost contact during stability monitoring")
                return False
        return True

    def _monitor_contact_stability(self, smu: object, info: ManipulatorInfo, duration_seconds: int) -> bool:
        """
        Monitors contact stability for a specified duration after initial contact detection.

        Args:
            smu: SMU object for resistance measurement
            channel: SMU channel to measure
            threshold: resistance threshold for contact detection
            duration_seconds: how long to monitor for stability

        Returns:
            bool: True if contact remained stable for the entire duration, False otherwise
        """

        self._log(f"Monitoring contact stability for {duration_seconds} seconds...")
        start_time = time.time()
        measurements = []

        while time.time() - start_time < duration_seconds:
            contacting, r = self._contacting(smu, info)

            measurements.append(contacting)

            if not contacting:
                self._log(f"Contact lost during stability monitoring after {time.time() - start_time:.1f} seconds")
                return False

            # Small delay between measurements
            time.sleep(0.1)

        self._log(f"Contact remained stable for {duration_seconds} seconds ({len(measurements)} measurements)")
        return True


    def _contacting(self, smu: object, info: ManipulatorInfo):
        """Check resistance between manipulator probes

        Args:
            smu (object): smu
            info (ManipulatorInfo): manipulator information
        Returns:
            tuple of (0, bool) when successful, (code, status) with errors
        """
        status, r = smu.smu_resmes(info.smu_channel)
        assert status == 0, f"Failed to measure resistance on channel {info.smu_channel}: {r}"

        self._log(f"Measured resistance: {r} Ω, threshold: {info.threshold} Ω")
        # assert correct types
        assert isinstance(r, (int, float)), f"Invalid resistance type: {type(r)}"
        assert isinstance(info.threshold, (int, float)), f"Invalid threshold type: {type(info.threshold)}"

        if r < info.threshold:
            self._log(f"Contact detected! Resistance {r} below threshold {info.threshold}")
            return True, r
        return False, r

    def _manipulator_measurement_setup(self, smu: object, con: object, mi: ManipulatorInfo) -> tuple[int, dict]:
        """Set up SMU for resistance measurement on a specific manipulator channel."""
        try:
            # setup smu for resistance measurement
            smu_status, smu_state = smu.smu_setup_resmes(mi.smu_channel)
            assert smu_status == 0, f"Failed to setup SMU for manipulator {mi.mm_number}: {smu_state}"

            # setup contact detection channel
            con.deviceLoCheck(False)
            con.deviceHiCheck(False)
            if mi.condet_channel == "Hi":
                con.deviceHiCheck(True)
            elif mi.condet_channel == "Lo":
                con.deviceLoCheck(True)
            else:
                raise ValueError(f"Invalid contact detection channel {mi.condet_channel}")

            return (0, {"message": f"SMU setup successful for manipulator {mi.mm_number}"})
        except Exception as e:
            return (1, {"Error message": f"Error setting up SMU for manipulator {mi.mm_number}: {str(e)}"})

    def _channels_off(self, con: object, smu: object):
        """Cleanup function to reset contact detection and SMU state."""
        try:
            con.deviceLoCheck(False)
            con.deviceHiCheck(False)
            smu.smu_outputOFF()
            smu.smu_disconnect()
            con.deviceDisconnect()
            self._log("Cleanup completed successfully")

        except Exception as e:
            self._log(f"Error during cleanup: {str(e)}")

    def _channels_off_single_manipulator(self, con: object, smu: object):
        """Cleanup function for a single manipulator without disconnecting devices."""
        try:
            con.deviceLoCheck(False)
            con.deviceHiCheck(False)
            smu.smu_outputOFF()
        except Exception as e:
            self._log(f"Error during single manipulator cleanup: {str(e)}")
