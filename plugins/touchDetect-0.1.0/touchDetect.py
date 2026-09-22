import time
from dataclasses import dataclass
from typing import Any

from threadStopped import ThreadStopped


# Idea
class PluginError(Exception):
    """Raised when an external plugin returns a non-zero status code."""

    def __init__(self, status_code: int, message: str = "Plugin call failed", details: dict | None = None):
        super().__init__(f"{message} (Status Code: {status_code})")
        self.status_code = status_code
        self.details = details or {}


def unpack_resp(ret_tuple: tuple[int, Any]) -> Any:
    """
    Unpacks (status_code, payload/details) from external plugins.
    When status != 0, we expect state to be a dictionary with an "Error message" key.
    PluginError is raised based on that. Else, we just return.

    """
    status, state = ret_tuple

    # Assuming status code 0 indicates success
    if status != 0:
        error_msg = state.get("Error message", "Unknown error")
        raise PluginError(status, message=error_msg, details=state)

    return state


@dataclass
class ManipulatorInfo:
    mm_number: int
    smu_channel: str
    condet_channel: str
    threshold: int
    stride: int
    sample_width: float
    function: str
    last_z: int | None = None
    spectrometer_height: int | None = None

    def __post_init__(self):
        """Generates new field (self.function) after __init__ is called"""
        if self.smu_channel == "spectrometer" or self.condet_channel == "spectrometer":
            self.function: str = "spectrometer"
        elif self.smu_channel == "none" or self.condet_channel == "none" or self.smu_channel == "" or self.condet_channel == "":
            self.function: str = "unconfigured"
        else:
            self.function: str = "normal"

        # convert all to proper types
        self.mm_number = int(self.mm_number)
        self.smu_channel = str(self.smu_channel)
        self.condet_channel = str(self.condet_channel)
        self.threshold = int(self.threshold)
        self.stride = int(self.stride)
        self.sample_width = float(self.sample_width)
        self.last_z = int(self.last_z) if self.last_z is not None else None
        self.spectrometer_height = int(self.spectrometer_height) if self.spectrometer_height is not None else None

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
        return {
            "mm_number": self.mm_number,
            "smu_channel": self.smu_channel,
            "condet_channel": self.condet_channel,
            "threshold": self.threshold,
            "stride": self.stride,
            "sample_width": self.sample_width,
            "function": self.function,
            "last_z": self.last_z,
            "spectrometer_height": self.spectrometer_height,
        }

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
        return self.function == "normal"  # and self.last_z is None
        # Commented second part of statement out because if it is set, then resetting the z-position is not possible
        # since the manipulators are filtered out


class touchDetect:
    MAX_CORRECTION_ATTEMPTS = 10  # maximum attempts to correct non-contacting manipulators
    MONITORING_DURATION = 2  # seconds, to monitor stability after initial contact
    APPROACH_MARGIN = 200  # microns, margin before last known position

    def __init__(self, log=None):
        # Store logging functions from GUI if provided
        self.log = log
        # Store last known Z positions for each manipulator
        self.last_z_positions = {}

    def _log(self, message):
        if self.log:
            self.log(message)

    def monitor_manual_contact_detection(
        self,
        mm: dict,
        smu: dict,
        con: dict,
        manipulator_infos: list[ManipulatorInfo],
        progress_callback=None,
        error_callback=None,
        stop_requested_callback=None,
    ) -> tuple[int, dict]:
        """
        Monitors for manual contact detection and saves Z positions to an internal dictionary.
        This whole things is quite a lot.

        Args:
            mm: Micromanipulator methods dict
            smu: SMU methods dict
            con: Contact detection methods dict
            manipulator_infos: List of ManipulatorInfo objects to monitor
            progress_callback: Function to call with progress messages
            error_callback: Function to call with error messages
            stop_requested_callback: Function that returns True if stop is requested


        Returns:
            tuple[int, dict]: (status, result_dict)
        """
        try:
            self._log("Starting manual contact detection monitoring")

            # Connect to devices
            status, state = con["deviceConnect"]()
            if status != 0:
                if error_callback:
                    error_callback(f"Contact detection connection failed: {state}")
                return (status, {"Error message": f"Contact detection failed: {state}"})

            status_smu, state_smu = smu["smu_connect"]()
            if status_smu != 0:
                if error_callback:
                    error_callback(f"SMU connection failed: {state_smu}")
                return (status_smu, {"Error message": f"SMU failed: {state_smu}"})

            status_mm, state_mm = mm["mm_open"]()
            if status_mm != 0:
                if error_callback:
                    error_callback(f"Micromanipulator connection failed: {state_mm}")
                return (status_mm, {"Error message": f"MM failed: {state_mm}"})

            if progress_callback:
                progress_callback("All devices connected successfully")

            # Filter to only configured manipulators
            configured_manipulators = [info for info in manipulator_infos if info.is_configured()]

            # remove manipulators which do not need z-positions:
            configured_manipulators = [info for info in configured_manipulators if info.needs_z_pos()]

            if not configured_manipulators:
                error_msg = "No configured manipulators found"
                if error_callback:
                    error_callback(error_msg)
                return (1, {"Error message": error_msg})

            # Process each configured manipulator
            for info in configured_manipulators:
                if stop_requested_callback and stop_requested_callback():
                    break

                self._log(f"Starting monitoring for manipulator {info.mm_number}")
                if progress_callback:
                    progress_callback(f"Starting monitoring for manipulator {info.mm_number} (SMU: {info.smu_channel}, Con: {info.condet_channel}, Threshold: {info.threshold})")

                # Set up measurement for this manipulator
                self._manipulator_measurement_setup(mm, smu, con, info)

                if progress_callback:
                    progress_callback(f"MANUAL CONTROL: Move manipulator {info.mm_number} manually until contact is detected")
                    progress_callback(f"Monitoring resistance on {info.smu_channel} with threshold {info.threshold}...")

                # Monitor loop for this manipulator
                contact_detected = False
                last_resistance_log = None

                while not contact_detected and not (stop_requested_callback and stop_requested_callback()):
                    try:
                        contacting, r = self._contacting(smu, info)

                        # Log resistance updates less frequently to avoid spam
                        if last_resistance_log is None or abs(r - last_resistance_log) > info.threshold * 0.1:
                            if progress_callback:
                                progress_callback(f"Manipulator {info.mm_number} resistance: {r:.1f} Ω (threshold: {info.threshold} Ω)")
                            last_resistance_log = r

                        if contacting:
                            # Contact detected! Save the z-position to both ManipulatorInfo and low-level storage
                            position_data = mm["mm_current_position"]()
                            _x, _y, z_position = position_data
                            info.last_z = int(z_position)
                            # Store in low-level dictionary for move_to_contact to use
                            self.last_z_positions[info.mm_number] = int(z_position)
                            self._log(f"Contact detected for manipulator {info.mm_number} at Z={z_position}")
                            if progress_callback:
                                progress_callback(f"Contact detected for manipulator {info.mm_number} at Z={z_position}")
                            contact_detected = True

                        time.sleep(0.1)

                    except PluginError as e:
                        if error_callback:
                            error_callback(f"Exception during monitoring for manipulator {info.mm_number}: {e!s}")
                        break

                # Clean up for this manipulator
                self._channels_off_single_manipulator(con, smu)

            if not (stop_requested_callback and stop_requested_callback()):
                saved_positions = {info.mm_number: info.last_z for info in configured_manipulators if info.last_z is not None}
                if progress_callback:
                    progress_callback("Monitoring completed for all configured manipulators")
                    progress_callback(f"Saved positions: {saved_positions}")
                return (0, {"Error message": "Monitoring completed successfully", "saved_positions": saved_positions})
            else:
                if progress_callback:
                    progress_callback("Monitoring stopped by user")
                return (0, {"Error message": "Monitoring stopped by user"})

        except PluginError as e:
            error_msg = f"Exception during monitoring: {e!s}"
            self._log(error_msg)
            if error_callback:
                error_callback(error_msg)
            return (2, {"Error message": error_msg, "Exception": str(e)})

        finally:
            # Clean up
            self._channels_off(con, smu)
            if progress_callback:
                progress_callback("Disconnected from all devices")

    def _setup_and_move_to_contact(self, mm: dict, smu: dict, con: dict, info: ManipulatorInfo) -> tuple[int, dict]:
        """Helper method to setup measurement and move to contact for a single manipulator."""
        # Set up for resistance measurement
        self._manipulator_measurement_setup(mm, smu, con, info)

        # move to last known position
        status, state = self._move_manipulator_to_last_contact(mm, info)
        if status != 0:
            return status, {"Error message": f"Failed to move to last contact position: {state}"}

        # compute the maximum move distance for the initial move
        effective_max_distance = self.APPROACH_MARGIN + info.sample_width

        # move down until contact is detected
        status, result = self._move_until_contact(mm, smu, info, effective_max_distance)
        return status, result

    def move_to_contact(self, mm: dict, con: dict, smu: dict, manipulator_info: list[ManipulatorInfo]):
        """Moves the specified micromanipulators to contact with the sample.

        Implements iterative contact verification:
        1. Move all manipulators to initial contact
        2. Check which manipulators are still in contact
        3. Move non-contacting manipulators further toward sample
        4. Monitor all contacts for stability before confirming success

        Args:
            mm (dict): micromanipulator methods dict
            con (dict): contact detection switcher methods dict
            smu (dict): smu methods dict
            manipulator_info (list[ManipulatorInfo]): list of ManipulatorInfo objects
        Returns:
            tuple: (status_code, result_dict)
        """
        try:
            self._log("Starting move_to_contact operation")

            # connect devices
            status, state = con["deviceConnect"]()
            if status != 0:
                error_msg = f"Contact detection connection failed: {state}"
                return (status, {"Error message": error_msg})

            status_smu, state_smu = smu["smu_connect"]()
            if status_smu != 0:
                error_msg = f"SMU connection failed: {state_smu}"
                return (status_smu, {"Error message": error_msg})

            status_mm, state_mm = mm["mm_open"]()
            if status_mm != 0:
                error_msg = f"Micromanipulator connection failed: {state_mm}"
                return (status_mm, {"Error message": error_msg})

            # remove manipulators from the list with no configuration
            manipulator_info = [info for info in manipulator_info if info.is_configured()]

            # Populate last_z positions from stored data and validate
            for info in manipulator_info:
                if info.mm_number in self.last_z_positions:
                    info.last_z = self.last_z_positions[info.mm_number]
                    self._log(f"Loaded stored z position for manipulator {info.mm_number}: {info.last_z}")
                elif info.function == "normal":
                    # Normal manipulators require a stored z position
                    error_msg = f"Manipulator {info.mm_number} requires a stored z position from previous monitoring. Run manual monitoring first."
                    self._log(error_msg)
                    return (1, {"Error message": error_msg})

            # remove manipulators with invalid configurations:
            validated = []
            for info in manipulator_info:
                errors = info.validate()
                if errors:
                    self._log(f"Manipulator {info.mm_number} has validation errors: {errors}")
                else:
                    validated.append(info)
            self._log(f"Filtered manipulators to {len(validated)} valid configurations")

            manipulator_info = [info for info in validated if info.function == "normal"]
            spectrometer_info = [info for info in validated if info.function == "spectrometer"]

            self._log(f"Manipulators to move to contact: {[info.mm_number for info in manipulator_info]}")
            self._log(f"Spectrometers to position: {[info.mm_number for info in spectrometer_info]}")

            # PHASE 1: Move all manipulators of type normal to contact:
            self._log("PHASE 1: Moving all manipulators to initial contact")

            for info in manipulator_info:
                self._log(f"Processing manipulator {info.mm_number} with threshold {info.threshold}, stride {info.stride}, max distance {info.sample_width}")
                status, result = self._setup_and_move_to_contact(mm, smu, con, info)
                if status != 0:
                    error_msg = f"Contact detection connection failed: {result}"
                    return (status, {"Error message": error_msg})

            # PHASE 2: Iterative contact verification and correction
            self._log("PHASE 2: Starting iterative contact verification")

            correction_attempt = 0
            while correction_attempt < self.MAX_CORRECTION_ATTEMPTS:
                correction_attempt += 1
                self._log(f"Contact verification attempt {correction_attempt}/{self.MAX_CORRECTION_ATTEMPTS}")

                # Check which manipulators are currently contacting
                uncontacting = self._get_uncontacting(smu, con, mm, manipulator_info)

                if not uncontacting:
                    self._log("All configured manipulators are contacting")
                    break

                self._log(f"Found {len(uncontacting)} non-contacting manipulators: {[m.mm_number for m in uncontacting]}")

                # Move non-contacting manipulators further toward sample
                for info in uncontacting:
                    self._log(f"Correcting contact for manipulator {info.mm_number}")

                    self._manipulator_measurement_setup(mm, smu, con, info)

                    correction_max_distance = info.stride * 8  # Limited correction distance

                    # move until contact is detected using the method that does not use the last known position
                    status, result = self._move_until_contact(mm, smu, info, correction_max_distance)
                    if status == 0:
                        self._log(f"Manipulator {info.mm_number} corrected successfully, starting monitoring")
                        # After moving, monitor stability for a few seconds
                        stable = self._monitor_contact_stability(smu, info, duration_seconds=self.MONITORING_DURATION)
                        if stable:
                            self._log(f"Manipulator {info.mm_number} contact is stable after correction")
                    else:
                        self._log(f"Failed to correct contact for manipulator {info.mm_number}: {result}")

            self._log("Move to contact operation completed successfully - all contacts verified and stable")

            # move spectrometer to position:
            # get the positions of the contacting manipulators
            if spectrometer_info:
                zs = []
                for info in manipulator_info:
                    idx = info.mm_number
                    position_data = mm["mm_current_position"](manipulator_name=idx)
                    _x, _y, z_position = position_data
                    zs.append(z_position)
                avg_z = sum(zs) / len(zs)
                self._log(f"Moving spectrometer to average Z position of contacting manipulators: {avg_z} with offset {spectrometer_info[0].spectrometer_height}")
                for info in spectrometer_info:  # loop just in case multiple spectros are configured.
                    status, state = mm["mm_change_active_device"](info.mm_number)
                    if status != 0:
                        error_msg = f"Failed to change active device for spectrometer {info.mm_number}: {state}"
                        return (status, {"Error message": error_msg})
                    target_z = avg_z - info.spectrometer_height
                    self._log(f"Moving spectrometer {info.mm_number} to Z={target_z}")
                    status, state = mm["mm_zmove"](target_z, absolute=True)
                    if status != 0:
                        error_msg = f"Failed to move spectrometer {info.mm_number} to Z={target_z}: {state}"
                        return (status, {"Error message": error_msg})
                    self._log(f"Spectrometer {info.mm_number} moved to Z={target_z}")
            return (0, {"Error message": "OK"})

        except ThreadStopped:
            raise  # re-raise to be caught by outer layers that handle thread stopping
        except Exception as e:
            error_msg = f"Exception in move_to_contact: {e!s}"
            self._log(error_msg)
            # this is a lower level function, which i believe should rely on exceptions.
            raise
            return (2, {"Error message": "exception in move_to_contact", "exception": str(e)})
        finally:
            self._channels_off(con, smu)

    def _monitor_contact_stability(self, smu: dict, info: ManipulatorInfo, duration_seconds: int) -> bool:
        """
        Monitors contact stability for a specified duration after initial contact detection.

        Args:
            smu: SMU method dictionary
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
            contacting, _r = self._contacting(smu, info)

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

    def _contacting(self, smu: dict, info: ManipulatorInfo) -> tuple[bool, float]:
        """Check resistance between manipulator probes

        Args:
            smu (object): smu
            info (ManipulatorInfo): manipulator information
        Returns:
            tuple of (0, bool) when successful, (code, status) with errors
        """
        r = unpack_resp(smu["smu_resmes"](info.smu_channel))

        # Check types for weird cases
        if not isinstance(r, (int, float)):
            raise TypeError(f"Expected resistance to be int or float, got {type(r)} with value {r}")
        if not isinstance(info.threshold, (int, float)):
            raise TypeError(f"Expected threshold to be int or float, got {type(info.threshold)} with value {info.threshold}")

        self._log(f"Measured resistance: {r} Ω, threshold: {info.threshold} Ω")
        if r < info.threshold:
            self._log(f"Contact detected! Resistance {r} below threshold {info.threshold}")
            return True, r
        return False, r

    def _get_uncontacting(self, smu: dict, con: dict, mm: dict, mi: list[ManipulatorInfo]) -> list[ManipulatorInfo]:
        """Check contact status for all manipulators and return a list of booleans.

        Args:
            smu: SMU method dict
            con: contact detection method dict
            manipulator_info: list of ManipulatorInfo objects

        Returns:
            list[ManipulatorInfo]:
        """
        contact_status = []

        for info in mi:
            self._manipulator_measurement_setup(mm, smu, con, info)
            contacting = self._monitor_contact_stability(smu, info, duration_seconds=self.MONITORING_DURATION)
            if not contacting:
                self._log(f"Manipulator {info.mm_number} not contacting (above threshold)")
                contact_status.append(info)
            else:
                self._log(f"Manipulator {info.mm_number} is contacting")

        return contact_status

    def _move_until_contact(self, mm: dict, smu: dict, manipulator_info: ManipulatorInfo, max_distance_to_move: float) -> tuple[int, dict]:
        """Move the manipulator until contact is detected or the maximum distance is exceeded.

        Args:
            mm (dict): Micromanipulator methods dict
            smu (dict): SMU methods dict
            manipulator_info (ManipulatorInfo): Manipulator information
            max_distance_to_move (float): Maximum distance to move the manipulator

        Returns:
            tuple[int, dict]: Status code and additional information
        """
        total_distance = 0
        # Move until initial contact is detected
        contacting, r = self._contacting(smu, manipulator_info)
        while not contacting:
            if total_distance > max_distance_to_move:
                raise RuntimeError(f"Exceeded maximum move distance of {max_distance_to_move} microns for manipulator {manipulator_info.mm_number} without detecting contact.")

            # Calculate adaptive stride based on proximity to last known position
            current_stride = self._calculate_adaptive_stride(manipulator_info.stride, r)

            unpack_resp(mm["mm_zmove"](current_stride))

            self._log(f"Moving manipulator {manipulator_info.mm_number} down by {current_stride} microns (total moved: {total_distance + current_stride})")

            total_distance += current_stride
            contacting, r = self._contacting(smu, manipulator_info)
        # Initial contact detected! Return success
        return (0, {"Error message": "OK"})

    def _move_manipulator_to_last_contact(self, mm: dict, manipulator_info: ManipulatorInfo) -> tuple[int, dict]:
        """Does no error checking, just assumes that the ManipulatorInfo is already validated in public functions. Moves the manipulator to the last known contact position + APPROACH_MARGIN.

        Args:
            mm (dict): Micromanipulator methods dict
            manipulator_info (ManipulatorInfo): Manipulator information

        Returns:
            tuple[int, dict]: Status code and additional information
        """

        last_position = manipulator_info.last_z
        if last_position is None:
            raise ValueError(f"Last known position for manipulator {manipulator_info.mm_number} is not set. Cannot move to last contact position.")
        last_position = last_position - self.APPROACH_MARGIN  # Move down to approach margin
        self._log(f"Moving manipulator {manipulator_info.mm_number} to last contact position {last_position}")
        unpack_resp(mm["mm_move"](z=last_position))
        return (
            0,
            {"Error message": "OK"},
        )

    def _manipulator_measurement_setup(self, mm: dict, smu: dict, con: dict, mi: ManipulatorInfo) -> None:
        """Set up SMU for resistance measurement on a specific manipulator channel."""
        # setup smu for resistance measurement
        unpack_resp(smu["smu_setup_resmes"](mi.smu_channel))

        # set active manipulator
        unpack_resp(mm["mm_change_active_device"](mi.mm_number))

        # setup contact detection channel
        con["deviceLoCheck"](False)
        con["deviceHiCheck"](False)
        if mi.condet_channel == "Hi":
            con["deviceHiCheck"](True)
        elif mi.condet_channel == "Lo":
            con["deviceLoCheck"](True)
        else:
            raise ValueError(f"Invalid contact detection channel {mi.condet_channel}")

    def _channels_off(self, con: dict, smu: dict):
        """Cleanup function to reset contact detection and SMU state."""
        con["deviceLoCheck"](False)
        con["deviceHiCheck"](False)
        smu["smu_outputOFF"]()
        smu["smu_disconnect"]()
        con["deviceDisconnect"]()
        self._log("Cleanup completed successfully")

    def _channels_off_single_manipulator(self, con: dict, smu: dict):
        """Cleanup function for a single manipulator without disconnecting devices."""
        con["deviceLoCheck"](False)
        con["deviceHiCheck"](False)
        smu["smu_outputOFF"]()

    def verify_contact(self, mm: dict, smu: dict, con: dict, infos: list[ManipulatorInfo]) -> tuple[int, dict]:
        """Verifies contact for all manipulators."""
        self._log("Starting verify_contact operation")
        unpack_resp(smu["smu_connect"]())
        unpack_resp(con["deviceConnect"]())
        unpack_resp(mm["mm_open"]())

        stables = []
        for info in infos:
            stable = self._verify_contact_single(smu, con, mm, info)
            stables.append(stable)

        self._channels_off(con, smu)
        self._log("Verify contact operation completed successfully")
        for i, stable in enumerate(stables):
            if not stable:
                return (0, {"Error message": f"Manipulator {infos[i].mm_number} not in contact"})
        return (0, {"Error message": "Verify contact operation completed successfully"})

    def _verify_contact_single(self, smu: dict, con: dict, mm: dict, info: ManipulatorInfo) -> bool:
        """Verifies contact for a single manipulator."""
        self._log(f"Starting verify_contact for manipulator {info.mm_number}")

        self._manipulator_measurement_setup(mm, smu, con, info)
        stable = self._monitor_contact_stability(smu, info, self.MONITORING_DURATION)

        return stable
