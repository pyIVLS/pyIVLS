#

# detects 20 ohms -> slow down, don't move too far from there
#


class touchDetect:
    def __init__(self, log=None):
        self.last_z = {}
        self.slow_zone_margin = 50  # Distance around last position to use slow movement
        self.slow_stride_factor = 0.2  # Factor to reduce stride when close to last position
        self.approach_margin = 200  # Margin before last known position to start measurements (microns)
        self.monitoring_duration = 1  # seconds to monitor stability after initial contact
        self.monitoring_stability_attempts = 5  # Number of attempts to achieve stable contact

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

        REQUIREMENT: All manipulators must have previously saved z-positions from manual monitoring.
        This function does not handle initial detection - that must be done via the monitoring function.

        Args:
            mm (object): micromanipulator object
            con (object): contact detection switcher
            smu (object): smu
            manipulator_info (list): list of tuples with (smu_channel, condet_channel, threshold, stride, sample_width)
        Returns:
            success: Bool
        throws:
            AssertionError
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

            for idx, info in enumerate(manipulator_info):
                manipulator_name = idx + 1
                smu_channel, condet_channel, threshold, stride, sample_width = info

                # skip iteration for manipulator if nothing is set
                if smu_channel == "" or condet_channel == "":
                    self.log(f"Skipping manipulator {manipulator_name} - no configuration")
                    continue
                self.log(f"Processing manipulator {manipulator_name} with threshold {threshold}, stride {stride}, max distance {sample_width}")

                status, result = self._move_to_stable_contact(mm, smu, con, manipulator_name, smu_channel, condet_channel, threshold, stride, sample_width)
                assert status == 0, f"Failed to achieve stable contact for manipulator {manipulator_name}: {result}"

                contact_results[manipulator_name] = result
                self.log(f"Manipulator {manipulator_name} successfully contacted at z={result['z_position']} after {result['attempts']} attempts")

            # SECOND PASS: Verify all contacts are still good after all manipulators moved
            self.log("Starting verification pass - checking all contacts are still stable")

            for idx, info in enumerate(manipulator_info):
                manipulator_name = idx + 1
                smu_channel, condet_channel, threshold, stride, sample_width = info

                if smu_channel == "" or condet_channel == "":
                    continue

                if manipulator_name not in contact_results:
                    continue  # Skip if this manipulator wasn't processed in first pass

                self.log(f"Verifying contact for manipulator {manipulator_name}")

                # Set up contact detection for verification
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

                # Check if contact is still good
                status, result = self._move_to_stable_contact(mm, smu, con, manipulator_name, smu_channel, condet_channel, threshold, stride, sample_width)
                assert status == 0, f"Failed to verify contact for manipulator {manipulator_name}: {result}"
                self.log(f"Contact verified for manipulator {manipulator_name}")

            all_good = self._check_all_contacting(smu, con, manipulator_info)
            if not all_good:
                self.log("Move to contact operation failed - not all contacts verified")
                return (1, {"Error message": "Move to contact operation failed", "contact_results": contact_results})

            self.log("Move to contact operation completed successfully - all contacts verified")
            return (0, {"Error message": "OK", "contact_results": contact_results})

        except Exception as e:
            error_msg = f"Exception in move_to_contact: {str(e)}"
            self.log(error_msg)
            return (2, {"Error message": "exception in move_to_contact", "exception": str(e)})
        finally:
            con.deviceLoCheck(False)
            con.deviceHiCheck(False)
            smu.smu_outputOFF()
            con.deviceDisconnect()
            self.log("Disconnected from contact detection device")

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
        import time

        self.log(f"Monitoring contact stability for {duration_seconds} seconds...")
        start_time = time.time()
        measurements = []

        while time.time() - start_time < duration_seconds:
            contact_result = self._contacting(smu, channel, threshold)
            if contact_result[0] != 0:
                self.log(f"Error during stability monitoring: {contact_result[1]}")
                return False

            is_in_contact = contact_result[1]
            measurements.append(is_in_contact)

            if not is_in_contact:
                self.log(f"Contact lost during stability monitoring after {time.time() - start_time:.1f} seconds")
                return False

            # Small delay between measurements
            time.sleep(0.1)

        self.log(f"Contact remained stable for {duration_seconds} seconds ({len(measurements)} measurements)")
        return True

    def _calculate_adaptive_stride(self, mm: object, manipulator_name: int, base_stride: int) -> int:
        """Calculate adaptive stride based on proximity to last known position.

        Args:
            mm: micromanipulator object
            manipulator_name: manipulator identifier
            base_stride: base stride size

        Returns:
            int: calculated stride size
        """
        if manipulator_name not in self.last_z:
            # No previous position known, use full stride
            self.log(f"No previous position for manipulator {manipulator_name}, using full stride")
            return base_stride

        _, _, current_z = mm.mm_current_position()
        last_contact_z = self.last_z[manipulator_name]
        distance_to_last = abs(current_z - last_contact_z)

        # Use slower movement when getting close to the last known contact position
        if distance_to_last <= self.slow_zone_margin:
            # Close to last contact position, use slower movement
            slow_stride = max(1, int(base_stride * self.slow_stride_factor))
            self.log(f"Close to last contact position (distance: {distance_to_last}), using slow stride: {slow_stride}")
            return slow_stride
        else:
            # Far from last contact position, use full stride
            self.log(f"Far from last contact position (distance: {distance_to_last}), using full stride: {base_stride}")
            return base_stride

    def _contacting(self, smu: object, channel: str, threshold: float):
        """Check resistance between manipulator probes

        Args:
            smu (object): smu
            channel (str): which channel to measure on
            threshold (float): resistance threshold for contact detection
        Returns:
            tuple of (0, bool) when successful, (code, status) with errors
        """
        try:
            status, r = smu.smu_resmes(channel)
            if status != 0:
                self.log(f"Resistance measurement failed: {r}")
                return (status, {"Error message": f"{r}"})
            r = float(r)

            self.log(f"Measured resistance: {r} Ω, threshold: {threshold} Ω")

            if r < threshold:
                self.log(f"Contact detected! Resistance {r} below threshold {threshold}")
                return (0, True)
            return (0, False)

        except Exception as e:
            error_msg = f"Exception in resistance measurement: {str(e)}"
            self.log(error_msg)
            return (3, {"Error message": "touchDetect error", "exception": str(e)})

    def _check_all_contacting(self, smu: object, con: object, manipulator_info) -> bool:
        for info in manipulator_info:
            smu_channel, condet_channel, threshold, stride, sample_width = info
            # setup contact detection channel
            con.deviceLoCheck(False)
            con.deviceHiCheck(False)
            if condet_channel == "Hi":
                con.deviceHiCheck(True)
            elif condet_channel == "Lo":
                con.deviceLoCheck(True)
            else:
                raise ValueError(f"Invalid contact detection channel {condet_channel}")

            status, result = self._contacting(smu, smu_channel, threshold)
            if status != 0 or not result:
                error_msg = f"Contact lost on channel {smu_channel} during verification"
                self.log(error_msg)
                return False
        return True

    def _move_until_contact(self, mm: object, smu: object, manipulator_name: int, smu_channel: str, threshold: float, stride: int, effective_max_distance: float) -> tuple[int, dict]:
        total_distance = 0
        # Move until initial contact is detected
        while self._contacting(smu, smu_channel, threshold)[1] is False:
            if total_distance > effective_max_distance:
                error_msg = f"Maximum distance {effective_max_distance} exceeded for manipulator {manipulator_name} (moved {total_distance})"
                return (3, {"Error message": error_msg})

            # Calculate adaptive stride based on proximity to last known position
            current_stride = self._calculate_adaptive_stride(mm, manipulator_name, stride)

            status, state = mm.mm_zmove(current_stride)
            assert status == 0, f"Z-move failed: {state}"

            total_distance += current_stride
            self.log(f"Moved {current_stride} units, total distance: {total_distance}/{effective_max_distance}")
        # Initial contact detected! Return success
        return (0, True)
