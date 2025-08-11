#

# detects 20 ohms -> slow down, don't move too far from there
#
import time


class touchDetect:
    def __init__(self, log=None):
        self.last_z = {}
        self.approach_margin = 200  # Margin before last known position to start measurements (microns)
        self.monitoring_duration = 1  # seconds to monitor stability after initial contact
        self.monitoring_stability_attempts = 5  # Number of attempts to achieve stable contact
        self.MAX_CORRECTION_ATTEMPTS = 10  # Maximum attempts to correct non-contacting manipulators

        # Store logging functions from GUI if provided
        self.log = log

    def _move_to_stable_contact(self, mm: object, smu: object, con: object, manipulator_name: int, smu_channel: str, condet_channel: str, threshold: float, stride: int, sample_width: float) -> tuple[int, dict]:
        """
        Moves a single manipulator to stable contact with the sample.

        This function implements the logic:
        1. Move until contact found
        2. Monitor that contact is stable
        3. If stability is broken, resume moving toward contact
        4. Repeat until stable contact is achieved

        Args:
            mm: micromanipulator object
            smu: SMU object
            con: contact detection object
            manipulator_name: manipulator identifier (1-4)
            smu_channel: SMU channel for resistance measurement
            condet_channel: contact detection channel ("Hi" or "Lo")
            threshold: resistance threshold for contact detection
            stride: movement stride size
            sample_width: maximum allowed movement distance

        Returns:
            tuple[int, dict]: (status, result) - 0 for success, error code and details for failure
        """
        try:
            self.log(f"Starting stable contact procedure for manipulator {manipulator_name}")

            # Set up contact detection channel.
            con.deviceLoCheck(False)
            con.deviceHiCheck(False)
            if condet_channel == "Hi":
                con.deviceHiCheck(True)
            elif condet_channel == "Lo":
                con.deviceLoCheck(True)
            else:
                raise ValueError(f"Invalid contact detection channel {condet_channel} for manipulator {manipulator_name}")

            # Set up SMU for resistance measurement
            status, state = smu.smu_setup_resmes(smu_channel)
            assert status == 0, f" Failed to setup resistance measurement: {state}"

            # Set active manipulator
            status, state = mm.mm_change_active_device(manipulator_name)
            assert status == 0, f" Failed to change active device: {state}"

            last_contact_z = self.last_z[manipulator_name]
            self.log(f"Using saved position for manipulator {manipulator_name}: {last_contact_z}")

            # Move to approach position (last position minus margin)
            approach_z = last_contact_z - self.approach_margin
            self.log(f"Moving to approach position: {approach_z} (last contact: {last_contact_z}, margin: {self.approach_margin})")
            status, result = mm.mm_move(z=approach_z)
            assert status == 0, f"Failed to move to approach position: {result}"

            effective_max_distance = sample_width + self.approach_margin
            self.log(f"Using effective max distance: {effective_max_distance} (sample_width: {sample_width} + margin: {self.approach_margin})")

            stability_attempt = 0

            while stability_attempt < self.monitoring_stability_attempts:
                stability_attempt += 1
                self.log(f"Stability attempt {stability_attempt}/{self.monitoring_stability_attempts} for manipulator {manipulator_name}")

                # Move until initial contact is detected
                status, contact_result = self._move_until_contact(mm, smu, manipulator_name, smu_channel, threshold, stride, effective_max_distance)
                assert status == 0, f"Failed to detect initial contact for manipulator {manipulator_name}: {contact_result}"

                # contact detected, now monitor stability
                self.log(f"Initial contact detected for manipulator {manipulator_name} (attempt {stability_attempt}). Monitoring stability...")

                # Monitor stability with the ability to detect when contact is lost
                stable_contact = self._monitor_contact_stability(smu, smu_channel, threshold, duration_seconds=self.monitoring_duration)

                if stable_contact:
                    # Success! Contact remained stable for the full duration
                    _, _, z = mm.mm_current_position()
                    self.last_z[manipulator_name] = z
                    self.log(f"Stable contact achieved for manipulator {manipulator_name} at z={z} after {stability_attempt} attempts")
                    return (0, {"manipulator": manipulator_name, "z_position": z, "attempts": stability_attempt})
                else:
                    # Contact was lost during stability monitoring
                    self.log(f"Contact lost during stability monitoring for manipulator {manipulator_name}. Resuming movement")
                    # Continue the loop to try again - we're already positioned where contact was lost

            # If we get here, we've exceeded the maximum number of stability attempts
            error_msg = f"Failed to achieve stable contact for manipulator {manipulator_name} after {self.monitoring_stability_attempts} attempts"
            return (4, {"Error message": error_msg})

        except Exception as e:
            error_msg = f"Exception in _move_to_stable_contact for manipulator {manipulator_name}: {str(e)}"
            return (2, {"Error message": error_msg, "exception": str(e)})
        finally:
            # Clean up for this manipulator
            con.deviceLoCheck(False)
            con.deviceHiCheck(False)
            smu.smu_outputOFF()

    def move_to_contact(self, mm: object, con: object, smu: object, manipulator_info: list):
        """Moves the specified micromanipulators to contact with the sample.

        Implements iterative contact verification:
        1. Move all manipulators to initial contact
        2. Check which manipulators are still in contact
        3. Move non-contacting manipulators further toward sample
        4. Monitor all contacts for stability before confirming success

        REQUIREMENT: All manipulators must have previously saved z-positions from manual monitoring.

        Args:
            mm (object): micromanipulator object
            con (object): contact detection switcher
            smu (object): smu
            manipulator_info (list): list of tuples with (smu_channel, condet_channel, threshold, stride, sample_width)
        Returns:
            tuple: (status_code, result_dict)
        """
        try:
            self.log("Starting move_to_contact operation")

            # connect devices
            status, state = con.deviceConnect()
            status_smu, state_smu = smu.smu_connect()
            status_mm, state_mm = mm.mm_open()

            assert status == 0, f"Contact detection connection failed: {state}"
            assert status_smu == 0, f"SMU connection failed: {state_smu}"
            assert status_mm == 0, f"Micromanipulator connection failed: {state_mm}"

            self.log("Devices connected successfully")

            contact_results = {}  # Store results for each manipulator
            max_correction_attempts = self.MAX_CORRECTION_ATTEMPTS  # Maximum attempts to correct non-contacting manipulators

            # PHASE 1: Move all manipulators to initial contact
            self.log("PHASE 1: Moving all manipulators to initial contact")

            for idx, info in enumerate(manipulator_info):
                manipulator_name = idx + 1
                smu_channel, condet_channel, threshold, stride, sample_width = info

                # skip iteration for manipulator if nothing is set
                if smu_channel == "" or condet_channel == "":
                    self.log(f"Skipping manipulator {manipulator_name} - no configuration")
                    continue

                self.log(f"Processing manipulator {manipulator_name} with threshold {threshold}, stride {stride}, max distance {sample_width}")

                # move to stable contact by moving until contact is detected, and then monitoring stability
                status, result = self._move_to_stable_contact(mm, smu, con, manipulator_name, smu_channel, condet_channel, threshold, stride, sample_width)
                assert status == 0, f"Failed to achieve initial contact for manipulator {manipulator_name}: {result}"

                contact_results[manipulator_name] = result
                self.log(f"Manipulator {manipulator_name} reached initial contact at z={result['z_position']}")

            # PHASE 2: Iterative contact verification and correction
            self.log("PHASE 2: Starting iterative contact verification")

            correction_attempt = 0
            while correction_attempt < max_correction_attempts:
                correction_attempt += 1
                self.log(f"Contact verification attempt {correction_attempt}/{max_correction_attempts}")

                # Check which manipulators are currently contacting
                contact_status = self._check_all_contacting(smu, con, manipulator_info)

                # Identify non-contacting manipulators that should be contacting
                non_contacting_manipulators = []
                for idx, (is_contacting, info) in enumerate(zip(contact_status, manipulator_info)):
                    manipulator_name = idx + 1
                    smu_channel, condet_channel, threshold, stride, sample_width = info

                    # Only consider configured manipulators that should be contacting
                    if smu_channel != "" and condet_channel != "" and not is_contacting:
                        non_contacting_manipulators.append((manipulator_name, info))

                if not non_contacting_manipulators:
                    self.log("All configured manipulators are contacting - proceeding to stability monitoring")
                    break

                self.log(f"Found {len(non_contacting_manipulators)} non-contacting manipulators: {[m[0] for m in non_contacting_manipulators]}")

                # Move non-contacting manipulators further toward sample
                for manipulator_name, info in non_contacting_manipulators:
                    smu_channel, condet_channel, threshold, stride, sample_width = info
                    self.log(f"Correcting contact for manipulator {manipulator_name}")

                    correction_max_distance = stride * 8  # Limited correction distance

                    status, result = self._move_to_stable_contact(mm, smu, con, manipulator_name, smu_channel, condet_channel, threshold, stride, correction_max_distance)
                    if status == 0:
                        contact_results[manipulator_name] = result
                        self.log(f"Manipulator {manipulator_name} contact corrected at z={result['z_position']}")
                    else:
                        self.log(f"Failed to correct contact for manipulator {manipulator_name}: {result}")

            # Final check - if we still have non-contacting manipulators after max attempts, throw error.
            final_contact_status = self._check_all_contacting(smu, con, manipulator_info)
            non_contacting_final = []
            for idx, (is_contacting, info) in enumerate(zip(final_contact_status, manipulator_info)):
                manipulator_name = idx + 1
                smu_channel, condet_channel, _, _, _ = info
                if smu_channel != "" and condet_channel != "" and not is_contacting:
                    non_contacting_final.append(manipulator_name)

            if non_contacting_final:
                error_msg = f"Failed to achieve contact for manipulators {non_contacting_final} after {max_correction_attempts} correction attempts"
                return (3, {"Error message": error_msg, "non_contacting": non_contacting_final})

            # PHASE 3: Monitor all contacts for stability
            self.log("PHASE 3: Monitoring all contacts for stability")

            for idx, info in enumerate(manipulator_info):
                manipulator_name = idx + 1
                smu_channel, condet_channel, threshold, stride, sample_width = info

                if smu_channel == "" or condet_channel == "":
                    continue

                self.log(f"Monitoring stability for manipulator {manipulator_name}")

                # Set up for stability monitoring
                con.deviceLoCheck(False)
                con.deviceHiCheck(False)
                if condet_channel == "Hi":
                    con.deviceHiCheck(True)
                elif condet_channel == "Lo":
                    con.deviceLoCheck(True)

                mm_status, mm_state = mm.mm_change_active_device(manipulator_name)
                smu_status, smu_state = smu.smu_setup_resmes(smu_channel)
                assert mm_status == 0, f"Failed to change active device for manipulator {manipulator_name}: {mm_state}"
                assert smu_status == 0, f"Failed to setup SMU for manipulator {manipulator_name}: {smu_state}"

                # Monitor stability
                stable_contact = self._monitor_contact_stability(smu, smu_channel, threshold, duration_seconds=self.monitoring_duration)
                if not stable_contact:
                    error_msg = f"Manipulator {manipulator_name} failed stability monitoring"
                    return (4, {"Error message": error_msg, "unstable_manipulator": manipulator_name})

                self.log(f"Manipulator {manipulator_name} passed stability monitoring")

            self.log("Move to contact operation completed successfully - all contacts verified and stable")
            return (0, {"Error message": "OK", "contact_results": contact_results, "correction_attempts": correction_attempt})

        except Exception as e:
            error_msg = f"Exception in move_to_contact: {str(e)}"
            self.log(error_msg)
            return (2, {"Error message": "exception in move_to_contact", "exception": str(e)})
        finally:
            con.deviceLoCheck(False)
            con.deviceHiCheck(False)
            smu.smu_outputOFF()
            con.deviceDisconnect()

    def _monitor_contact_stability(self, smu: object, channel: str, threshold: float, duration_seconds: int = 3) -> bool:
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

        self.log(f"Monitoring contact stability for {duration_seconds} seconds...")
        start_time = time.time()
        measurements = []

        while time.time() - start_time < duration_seconds:
            contacting, r = self._contacting(smu, channel, threshold)

            measurements.append(contacting)

            if not contacting:
                self.log(f"Contact lost during stability monitoring after {time.time() - start_time:.1f} seconds")
                return False

            # Small delay between measurements
            time.sleep(0.1)

        self.log(f"Contact remained stable for {duration_seconds} seconds ({len(measurements)} measurements)")
        return True

    def _calculate_adaptive_stride(self, base_stride: int, latest_resistance: float) -> int:
        """Calculate adaptive stride"""
        adaptive_stride = base_stride  # Default to base stride
        if latest_resistance < 20:
            adaptive_stride = max(1, base_stride // 4)  # must be close to contact, move slowly
        time.sleep(0.05)  # Small delay to slow everything down
        return adaptive_stride

    def _contacting(self, smu: object, channel: str, threshold: float):
        """Check resistance between manipulator probes

        Args:
            smu (object): smu
            channel (str): which channel to measure on
            threshold (float): resistance threshold for contact detection
        Returns:
            tuple of (0, bool) when successful, (code, status) with errors
        """
        status, r = smu.smu_resmes(channel)
        assert status == 0, f"Failed to measure resistance on channel {channel}: {r}"

        self.log(f"Measured resistance: {r} Ω, threshold: {threshold} Ω")
        # assert correct types
        assert isinstance(r, (int, float)), f"Invalid resistance type: {type(r)}"
        assert isinstance(threshold, (int, float)), f"Invalid threshold type: {type(threshold)}"

        if r < threshold:
            self.log(f"Contact detected! Resistance {r} below threshold {threshold}")
            return True, r
        return False, r

    def _check_all_contacting(self, smu: object, con: object, manipulator_info) -> list[bool]:
        """Check contact status for all manipulators and return a list of booleans.

        Args:
            smu: SMU object
            con: contact detection object
            manipulator_info: list of manipulator configurations

        Returns:
            list[bool]: List of contact status for each manipulator (True if contacting, False if not)
        """
        contact_status = []

        for idx, info in enumerate(manipulator_info):
            manipulator_name = idx + 1
            smu_channel, condet_channel, threshold, stride, sample_width = info

            if smu_channel == "" or condet_channel == "":
                # Skip this manipulator - treat as not configured (not contacting)
                contact_status.append(False)
                continue

            try:
                # setup contact detection channel
                con.deviceLoCheck(False)
                con.deviceHiCheck(False)
                if condet_channel == "Hi":
                    con.deviceHiCheck(True)
                elif condet_channel == "Lo":
                    con.deviceLoCheck(True)
                else:
                    raise ValueError(f"Invalid contact detection channel {condet_channel}")

                contacting, r = self._contacting(smu, smu_channel, threshold)
                if not contacting:
                    self.log(f"Manipulator {manipulator_name} not contacting (resistance check failed or above threshold)")
                    contact_status.append(False)
                else:
                    self.log(f"Manipulator {manipulator_name} is contacting")
                    contact_status.append(True)

            except Exception as e:
                self.log(f"Error checking contact for manipulator {manipulator_name}: {str(e)}")
                contact_status.append(False)

        return contact_status

    def _move_until_contact(self, mm: object, smu: object, manipulator_name: int, smu_channel: str, threshold: float, stride: int, effective_max_distance: float) -> tuple[int, dict]:
        total_distance = 0
        # Move until initial contact is detected
        contacting, r = self._contacting(smu, smu_channel, threshold)
        while not contacting:
            if total_distance > effective_max_distance:
                error_msg = f"Maximum distance {effective_max_distance} exceeded for manipulator {manipulator_name} (moved {total_distance})"
                return (3, {"Error message": error_msg})

            # Calculate adaptive stride based on proximity to last known position
            current_stride = self._calculate_adaptive_stride(stride, r)

            status, state = mm.mm_zmove(current_stride)
            assert status == 0, f"Z-move failed: {state}"

            total_distance += current_stride
            contacting, r = self._contacting(smu, smu_channel, threshold)
        # Initial contact detected! Return success
        return (0, True)
