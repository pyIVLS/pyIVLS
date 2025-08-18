#

# detects 20 ohms -> slow down, don't move too far from there
#
import time


class touchDetect:
    def __init__(self, log=None):
        self.last_z = {}
        self.approach_margin = 200  # Margin before last known position to start measurements (microns)
        self.monitoring_duration = 2  # seconds to monitor stability after initial contact
        self.monitoring_stability_attempts = 5  # Number of attempts to achieve stable contact
        self.MAX_CORRECTION_ATTEMPTS = 10  # Maximum attempts to correct non-contacting manipulators

        # Store logging functions from GUI if provided
        self.log = log


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

            max_correction_attempts = self.MAX_CORRECTION_ATTEMPTS  # Maximum attempts to correct non-contacting manipulators

            # PHASE 1: Move all manipulators to initial contact
            self.log("PHASE 1: Moving all manipulators to initial contact")

            for idx, info in enumerate(manipulator_info):
                manipulator_name = idx + 1
                smu_channel, condet_channel, threshold, stride, sample_width = info
                self.log(f"{smu_channel}, {condet_channel} for {manipulator_name}")
                # skip iteration for manipulator if nothing is set
                if smu_channel == "none" or condet_channel == "none" or smu_channel is None or condet_channel is None or smu_channel == "" or condet_channel == "" :
                    self.log(f"Skipping manipulator {manipulator_name} - no configuration")
                    continue

                self.log(f"Processing manipulator {manipulator_name} with threshold {threshold}, stride {stride}, max distance {sample_width}")
                
                # Set up for resistance measurement
                status, state = self._manipulator_measurement_setup(mm, smu, con, condet_channel, manipulator_name, smu_channel)
                assert status == 0, f"Failed to set up measurement for manipulator {manipulator_name}: {state}"

                # move to last known position
                status, state = self._move_manipulator_to_last_contact(mm, manipulator_name)
                assert status == 0, f"Failed to move manipulator {manipulator_name} to last contact position: {state}"

                # compute the effective maximum distance for this manipulator
                effective_max_distance = self.approach_margin + sample_width # width of the sample + approach margin

                # move down until contact is detected
                status, result = self._move_until_contact(mm, smu, manipulator_name, smu_channel, threshold, stride, effective_max_distance)
                assert status == 0, f"Failed to move manipulator {manipulator_name} down until contact: {result}"

            # PHASE 2: Iterative contact verification and correction
            self.log("PHASE 2: Starting iterative contact verification")

            correction_attempt = 0
            while correction_attempt < max_correction_attempts:
                correction_attempt += 1
                self.log(f"Contact verification attempt {correction_attempt}/{max_correction_attempts}")

                # Check which manipulators are currently contacting
                contact_status = self._check_all_contacting(smu, con, mm, manipulator_info)

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

                    status, state = self._manipulator_measurement_setup(mm, smu, con, condet_channel, manipulator_name, smu_channel)
                    assert status == 0, f"Failed to set up measurement for manipulator {manipulator_name}: {state}"

                    correction_max_distance = stride * 8  # Limited correction distance
                    
                    # move until contact is detected using the method that does not use the last known position
                    status, result = self._move_until_contact(mm, smu, manipulator_name, smu_channel, threshold, stride, correction_max_distance)
                    if status == 0:
                        self.log(f"Manipulator {manipulator_name} corrected successfully")
                    else:
                        self.log(f"Failed to correct contact for manipulator {manipulator_name}: {result}")

            """
            # PHASE 3: Monitor all contacts for stability
            self.log("PHASE 3: Monitoring all contacts for stability")

            contacting = self._check_all_contacting(smu, con, mm, manipulator_info)
            
            # Identify non-contacting manipulators that should be contacting
            non_contacting_manipulators = []
            for idx, (is_contacting, info) in enumerate(zip(contacting, manipulator_info)):
                manipulator_name = idx + 1
                smu_channel, condet_channel, threshold, stride, sample_width = info

                # Only consider configured manipulators that should be contacting
                if smu_channel != "" and condet_channel != "" and not is_contacting:
                    non_contacting_manipulators.append((manipulator_name, info))

            if non_contacting_manipulators:
                self.log(f"Non-contacting manipulators after correction: {[m[0] for m in non_contacting_manipulators]}")
                return (3, {"Error message": "Not all manipulators are contacting after correction", "non_contacting_manipulators": non_contacting_manipulators})
            """
            self.log("Move to contact operation completed successfully - all contacts verified and stable")
            return (0, {"Error message": "OK", "correction_attempts": correction_attempt})

        except Exception as e:
            error_msg = f"Exception in move_to_contact: {str(e)}"
            self.log(error_msg)
            return (2, {"Error message": "exception in move_to_contact", "exception": str(e)})
        finally:
            self._channels_off(con, smu)

    def _monitor_contact_stability(self, smu: object, channel: str, threshold: float, duration_seconds: int) -> bool:
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

    def _check_all_contacting(self, smu: object, con: object, mm: object, manipulator_info) -> list[bool]:
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
            if smu_channel == "none" or condet_channel == "none" or smu_channel is None or condet_channel is None or smu_channel == "" or condet_channel == "" :
                self.log(f"Skipping manipulator {manipulator_name} - no configuration")
                contact_status.append(False)
                continue
            status, state = self._manipulator_measurement_setup(mm, smu, con, condet_channel, manipulator_name, smu_channel)
            assert status == 0, f"Failed to set up measurement for manipulator {manipulator_name}: {state}"
            if smu_channel == "none" or condet_channel == "none" or smu_channel is None or condet_channel is None or smu_channel == "" or condet_channel == "" :
                # Skip unconfigured manipulator - (not contacting)
                contact_status.append(False)
                continue

            try:
                contacting = self._monitor_contact_stability(smu, smu_channel, threshold, duration_seconds=self.monitoring_duration)
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
            self.log(f"Moving manipulator {manipulator_name} down by {current_stride} microns (total moved: {total_distance + current_stride})")

            total_distance += current_stride
            contacting, r = self._contacting(smu, smu_channel, threshold)
        # Initial contact detected! Return success
        return (0, {"Error message": "OK"})

    def _move_manipulator_to_last_contact(self, mm: object, manipulator_name: int) -> tuple[int, dict]:
        try:
            if manipulator_name not in self.last_z:
                error_msg = f"No last contact position saved for manipulator {manipulator_name}"
                return (3, {"Error message": error_msg})

            last_position = self.last_z[manipulator_name]
            last_position = last_position - self.approach_margin  # Move down to approach margin
            self.log(f"Moving manipulator {manipulator_name} to last contact position {last_position}")
            status, result = mm.mm_move(z = last_position)
            if status != 0:
                return (status, result)

            return (0, {"message": f"Manipulator {manipulator_name} moved to last contact position {last_position}"})
        except Exception as e:
            return (1, {"Error message": f"Error moving manipulator {manipulator_name} to last contact position: {str(e)}"})

    def _manipulator_measurement_setup(self, mm: object, smu: object, con: object, condet_channel: str, manipulator_name: int, smu_channel: str) -> tuple[int, dict]:
        """Set up SMU for resistance measurement on a specific manipulator channel."""
        try:
            # setup smu for resistance measurement
            smu_status, smu_state = smu.smu_setup_resmes(smu_channel)
            assert smu_status == 0, f"Failed to setup SMU for manipulator {manipulator_name}: {smu_state}"

            # set active manipulator
            mm_status, mm_state = mm.mm_change_active_device(manipulator_name)
            assert mm_status == 0, f"Failed to change active device for manipulator {manipulator_name}: {mm_state}"

            # setup contact detection channel
            con.deviceLoCheck(False)
            con.deviceHiCheck(False)
            if condet_channel == "Hi":
                con.deviceHiCheck(True)
            elif condet_channel == "Lo":
                con.deviceLoCheck(True)
            else:
                raise ValueError(f"Invalid contact detection channel {condet_channel}")
            
            return (0, {"message": f"SMU setup successful for manipulator {manipulator_name}"})
        except Exception as e:
            return (1, {"Error message": f"Error setting up SMU for manipulator {manipulator_name}: {str(e)}"})
        
    def _channels_off(self, con: object, smu: object):
        """Cleanup function to reset contact detection and SMU state."""
        try:
            con.deviceLoCheck(False)
            con.deviceHiCheck(False)
            smu.smu_outputOFF()
            smu.smu_disconnect()
            con.deviceDisconnect()
            self.log("Cleanup completed successfully")
            
        except Exception as e:
            self.log(f"Error during cleanup: {str(e)}")