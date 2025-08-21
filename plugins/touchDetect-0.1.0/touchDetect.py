#

# detects 20 ohms -> slow down, don't move too far from there
#
import time
import enum
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
        """Generates new field (self.function) after __init__ is called
        """
        if self.smu_channel == "spectrometer" or self.condet_channel == "spectrometer":
            self.function: str = "spectrometer"
        elif self.smu_channel == "none" or self.condet_channel == "none":
            self.function: str = "unconfigured"
        elif self.smu_channel == "" or self.condet_channel == "":
            self.function: str = "unconfigured"
        else: 
            self.function: str = "normal"

    def validate(self) -> list[str]:
        """Returns a list of validation errors, if any.
        """
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
        """Returns True if the manipulator is configured, False otherwise.
        """
        return self.function != "unconfigured"


class touchDetect:
    def __init__(self, log=None):
        self.approach_margin = 200  # Margin before last known position to start measurements (microns)
        self.monitoring_duration = 2  # seconds to monitor stability after initial contact
        self.monitoring_stability_attempts = 5  # Number of attempts to achieve stable contact
        self.MAX_CORRECTION_ATTEMPTS = 10  # Maximum attempts to correct non-contacting manipulators

        # Store logging functions from GUI if provided
        self.log = log

    def _log(self, message):
        if self.log:
            self.log(message)

    def _setup_and_move_to_contact(self, mm: object, smu: object, con: object, info: ManipulatorInfo) -> tuple[int, dict]:
        """Helper method to setup measurement and move to contact for a single manipulator."""
        try:
            # Set up for resistance measurement
            status, state = self._manipulator_measurement_setup(mm, smu, con, info)
            if status != 0:
                return status, {"Error message": f"Failed to set up measurement: {state}"}

            # move to last known position
            status, state = self._move_manipulator_to_last_contact(mm, info)
            if status != 0:
                return status, {"Error message": f"Failed to move to last contact position: {state}"}

            # compute the maximum move distance for the initial move
            effective_max_distance = self.approach_margin + info.sample_width

            # move down until contact is detected
            status, result = self._move_until_contact(mm, smu, info, effective_max_distance)
            return status, result
            
        except Exception as e:
            return 1, {"Error message": f"Exception in setup and move: {str(e)}"}


    def move_to_contact(self, mm: object, con: object, smu: object, manipulator_info: list[ManipulatorInfo]):
        """Moves the specified micromanipulators to contact with the sample.

        Implements iterative contact verification:
        1. Move all manipulators to initial contact
        2. Check which manipulators are still in contact
        3. Move non-contacting manipulators further toward sample
        4. Monitor all contacts for stability before confirming success

        Args:
            mm (object): micromanipulator object
            con (object): contact detection switcher
            smu (object): smu
            manipulator_info (list[ManipulatorInfo]): list of ManipulatorInfo objects
        Returns:
            tuple: (status_code, result_dict)
        """
        try:
            self._log("Starting move_to_contact operation")

            # connect devices
            status, state = con.deviceConnect()
            status_smu, state_smu = smu.smu_connect()
            status_mm, state_mm = mm.mm_open()

            assert status == 0, f"Contact detection connection failed: {state}"
            assert status_smu == 0, f"SMU connection failed: {state_smu}"
            assert status_mm == 0, f"Micromanipulator connection failed: {state_mm}"

            # remove manipulators from the list with no configuration
            manipulator_info = [info for info in manipulator_info if info.is_configured()]

            # remove manipulators with invalid configurations:
            validated = []
            for info in manipulator_info:
                errors = info.validate()
                if errors:
                    self._log(f"Manipulator {info.mm_number} has validation errors: {errors}")
                else:
                    validated.append(info)
            manipulator_info = validated
            self._log(f"Filtered manipulators to {len(manipulator_info)} valid configurations")

            # PHASE 1: Move all manipulators to initial contact
            self._log("PHASE 1: Moving all manipulators to initial contact")

            for info in manipulator_info:
                self._log(f"Processing manipulator {info.mm_number} with threshold {info.threshold}, stride {info.stride}, max distance {info.sample_width}")

                status, result = self._setup_and_move_to_contact(mm, smu, con, info)
                assert status == 0, f"Failed to move manipulator {info.mm_number} to contact: {result}"

            # PHASE 2: Iterative contact verification and correction
            self._log("PHASE 2: Starting iterative contact verification")

            correction_attempt = 0
            while correction_attempt < self.MAX_CORRECTION_ATTEMPTS:
                correction_attempt += 1
                self._log(f"Contact verification attempt {correction_attempt}/{self.MAX_CORRECTION_ATTEMPTS}")

                # Check which manipulators are currently contacting
                uncontacting = self._get_uncontacting(smu, con, mm, manipulator_info)

                if not uncontacting:
                    self._log("All configured manipulators are contacting - proceeding to stability monitoring")
                    break

                self._log(f"Found {len(uncontacting)} non-contacting manipulators: {[m.mm_number for m in uncontacting]}")

                # Move non-contacting manipulators further toward sample
                for info in uncontacting:
                    self._log(f"Correcting contact for manipulator {info.mm_number}")

                    status, state = self._manipulator_measurement_setup(mm, smu, con, info)
                    assert status == 0, f"Failed to set up measurement for manipulator {info.mm_number}: {state}"

                    correction_max_distance = info.stride * 8  # Limited correction distance
                    
                    # move until contact is detected using the method that does not use the last known position
                    status, result = self._move_until_contact(mm, smu, info, correction_max_distance)
                    if status == 0:
                        self._log(f"Manipulator {info.mm_number} corrected successfully")
                    else:
                        self._log(f"Failed to correct contact for manipulator {info.mm_number}: {result}")

            self._log("Move to contact operation completed successfully - all contacts verified and stable")
            return (0, {"Error message": "OK"})

        except Exception as e:
            error_msg = f"Exception in move_to_contact: {str(e)}"
            self._log(error_msg)
            return (2, {"Error message": "exception in move_to_contact", "exception": str(e)})
        finally:
            self._channels_off(con, smu)

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

    def _calculate_adaptive_stride(self, base_stride: int, latest_resistance: float) -> int:
        """Calculate adaptive stride"""
        adaptive_stride = base_stride  # Default to base stride
        if latest_resistance < 20:
            adaptive_stride = max(1, base_stride // 4)  # must be close to contact, move slowly
        time.sleep(0.05)  # Small delay to slow everything down
        return adaptive_stride

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

    def _get_uncontacting(self, smu: object, con: object, mm: object, mi: list[ManipulatorInfo]) -> list[ManipulatorInfo]:
        """Check contact status for all manipulators and return a list of booleans.

        Args:
            smu: SMU object
            con: contact detection object
            manipulator_info: list of ManipulatorInfo objects

        Returns:
            list[ManipulatorInfo]: 
        """
        contact_status = []

        for info in mi:
            status, state = self._manipulator_measurement_setup(mm, smu, con, info)
            assert status == 0, f"Failed to set up measurement for manipulator {info.mm_number}: {state}"

            try:
                contacting = self._monitor_contact_stability(smu, info, duration_seconds=self.monitoring_duration)
                if not contacting:
                    self._log(f"Manipulator {info.mm_number} not contacting (above threshold)")
                    contact_status.append(info)
                else:
                    self._log(f"Manipulator {info.mm_number} is contacting")

            except Exception as e:
                self._log(f"Error checking contact for manipulator {info.mm_number}: {str(e)}")
                contact_status.append(info)

        return contact_status

    def _move_until_contact(self, mm: object, smu: object, manipulator_info: ManipulatorInfo, max_distance_to_move: float) -> tuple[int, dict]:
        total_distance = 0
        # Move until initial contact is detected
        contacting, r = self._contacting(smu, manipulator_info.smu_channel, manipulator_info.threshold)
        while not contacting:
            if total_distance > max_distance_to_move:
                error_msg = f"Maximum distance {max_distance_to_move} exceeded for manipulator {manipulator_info.mm_number} (moved {total_distance})"
                return (3, {"Error message": error_msg})

            # Calculate adaptive stride based on proximity to last known position
            current_stride = self._calculate_adaptive_stride(manipulator_info.stride, r)

            status, state = mm.mm_zmove(current_stride)
            assert status == 0, f"Z-move failed: {state}"
            self._log(f"Moving manipulator {manipulator_info.mm_number} down by {current_stride} microns (total moved: {total_distance + current_stride})")

            total_distance += current_stride
            contacting, r = self._contacting(smu, manipulator_info.smu_channel, manipulator_info.threshold)
        # Initial contact detected! Return success
        return (0, {"Error message": "OK"})

    def _move_manipulator_to_last_contact(self, mm: object, manipulator_info: ManipulatorInfo) -> tuple[int, dict]:
        """Does no error checking, just assumes that the ManipulatorInfo is already validated in public functions.

        Args:
            mm (object): _description_
            manipulator_info (ManipulatorInfo): _description_

        Returns:
            tuple[int, dict]: _description_
        """

        last_position = manipulator_info.last_z
        last_position = last_position - self.approach_margin  # Move down to approach margin
        self._log(f"Moving manipulator {manipulator_info.mm_number} to last contact position {last_position}")
        status, result = mm.mm_move(z = last_position)
        if status != 0:
            return (status, result)
        return (0, {"message": f"Manipulator {manipulator_info.mm_number} moved to last contact position {last_position}"})

    def _manipulator_measurement_setup(self, mm: object, smu: object, con: object, mi: ManipulatorInfo) -> tuple[int, dict]:
        """Set up SMU for resistance measurement on a specific manipulator channel."""
        try:
            # setup smu for resistance measurement
            smu_status, smu_state = smu.smu_setup_resmes(mi.smu_channel)
            assert smu_status == 0, f"Failed to setup SMU for manipulator {mi.mm_number}: {smu_state}"

            # set active manipulator
            mm_status, mm_state = mm.mm_change_active_device(mi.mm_number)
            assert mm_status == 0, f"Failed to change active device for manipulator {mi.mm_number}: {mm_state}"

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