class touchDetect:
    def __init__(self, log_verbose=None, log_info=None, log_warn=None):
        self.last_z = {}
        self.recklessness = 10
        self.slow_zone_margin = 50  # Distance around last position to use slow movement
        self.slow_stride_factor = 0.2  # Factor to reduce stride when close to last position
        self.approach_margin = 200  # Margin before last known position to start measurements (microns)
        
        # Store logging functions from GUI if provided
        self._log_verbose_func = log_verbose
        self._log_info_func = log_info
        self._log_warn_func = log_warn

    def move_to_contact(self, mm: object, con: object, smu: object, manipulator_info: list):
        """Moves the specified micromanipulators to contact with the sample.

        Args:
            mm (object): micromanipulator object
            con (object): contact detection switcher
            smu (object): smu
            manipulator_info (list): list of tuples with (smu_channel, condet_channel, threshold, stride, sample_width)
        Returns:
            tuple of (code, status)
        """
        try:
            self._log_verbose("Starting move_to_contact operation")
            status, state = con.deviceConnect()
            status_smu, state_smu = smu.smu_connect()
            if status != 0:
                self._log_warn(f"Contact detection connection failed: {state}")
                return (status, {"Error message": f"{state}"})
            if status_smu != 0:
                self._log_warn(f"SMU connection failed: {state_smu}")
                return (status_smu, {"Error message": f"{state_smu}"})
            
            self._log_info("Devices connected successfully")
            
            # iterate through provided instructions for manipulators
            for idx, info in enumerate(manipulator_info):
                manipulator_name = idx + 1
                smu_channel, condet_channel, threshold, stride, sample_width = info
                # skip iteration for manipulator if nothing is set
                if smu_channel == "" or condet_channel == "":
                    self._log_verbose(f"Skipping manipulator {manipulator_name} - no configuration")
                    continue

                self._log_info(f"Processing manipulator {manipulator_name} with threshold {threshold}, stride {stride}, max distance {sample_width}")

                # switch mode for contact detection
                if condet_channel == "Hi":
                    con.deviceHiCheck(True)
                elif condet_channel == "Lo":
                    con.deviceLoCheck(True)
                else:
                    error_msg = f"TouchDetect: Invalid contact detection channel {condet_channel} for manipulator {manipulator_name}"
                    self._log_warn(error_msg)
                    return (1, {"Error message": error_msg})
                
                status, state = mm.mm_open()
                if status != 0:
                    self._log_warn(f"Failed to open micromanipulator: {state}")
                    return (status, {"Error message": f"{state}"})

                # change device
                mm.mm_change_active_device(manipulator_name)
                
                # Get starting position for distance tracking
                start_x, start_y, start_z = mm.mm_current_position()
                self._log_verbose(f"Starting position for manipulator {manipulator_name}: x={start_x}, y={start_y}, z={start_z}")
                
                self._log_verbose(f"Last known positions: {self.last_z}")
                if self.last_z.get(manipulator_name) is not None:
                    last_contact_z = self.last_z[manipulator_name]
                    self._log_info(f"Found previous position for manipulator {manipulator_name}: {last_contact_z}")
                    
                    # Move to approach position (last position minus margin)
                    approach_z = last_contact_z - self.approach_margin
                    self._log_info(f"Moving to approach position: {approach_z} (last contact: {last_contact_z}, margin: {self.approach_margin})")
                    status, result = mm.mm_zmove(approach_z, absolute=True)
                    if status != 0:
                        self._log_warn(f"Failed to move to approach position: {result}")
                        return (status, {"Error message": f"TouchDetect: Failed to move to approach position: {result}"})
                    


                status, state = smu.smu_setup_resmes(smu_channel)
                if status != 0:
                    self._log_warn(f"Failed to setup resistance measurement: {state}")
                    return (status, {"Error message": f"{state}"})

                # move until contact with adaptive stride
                total_distance = 0
                has_last_position = manipulator_name in self.last_z
                
                # Calculate effective maximum distance (sample width + margin for known positions)
                if has_last_position:
                    effective_max_distance = sample_width + self.approach_margin
                    self._log_verbose(f"Using effective max distance: {effective_max_distance} (sample_width: {sample_width} + margin: {self.approach_margin})")
                else:
                    effective_max_distance = float('inf')  # No limit if no previous position, this is used to find the first contact
                    self._log_info(f"No previous position for manipulator {manipulator_name}, performing initial calibration (max distance ignored)")
                
                while self._contacting(smu, smu_channel, threshold)[1] is False:
                    if has_last_position and total_distance > effective_max_distance:
                        error_msg = f"TouchDetect: Maximum distance {effective_max_distance} exceeded for manipulator {manipulator_name} (moved {total_distance})"
                        self._log_warn(error_msg)
                        
                        return (3, {"Error message": error_msg})
                    
                    # Calculate adaptive stride based on proximity to last known position
                    current_stride = self._calculate_adaptive_stride(mm, manipulator_name, stride)
                    
                    status, state = mm.mm_zmove(current_stride)
                    if status != 0:
                        self._log_warn(f"Z-move failed: {state}")
                        return (status, {"Error message": f"{state}"})
                    
                    total_distance += current_stride
                    
                    if has_last_position:
                        self._log_verbose(f"Moved {current_stride} units, total distance: {total_distance}/{effective_max_distance}")
                    else:
                        self._log_verbose(f"Initial calibration: moved {current_stride} units, total distance: {total_distance}")

                # back to default
                con.deviceLoCheck(False)
                con.deviceHiCheck(False)
                smu.smu_outputOFF()

                # update the last z value for the manipulator
                _, _, z = mm.mm_current_position()
                was_first_time = manipulator_name not in self.last_z
                self.last_z[manipulator_name] = z
                
                if was_first_time:
                    self._log_info(f"Initial contact established at z={z} for manipulator {manipulator_name}, baseline saved for future use")
                else:
                    self._log_info(f"Contact found at z={z} for manipulator {manipulator_name}, position updated")
                
            self._log_info("Move to contact operation completed successfully")
            return (0, {"Error message": "OK"})

        except Exception as e:
            error_msg = f"Exception in move_to_contact: {str(e)}"
            self._log_warn(error_msg)
            return (2, {"Error message": "exception in move_to_contact", "exception": str(e)})
        finally:
            con.deviceLoCheck(False)
            con.deviceHiCheck(False)
            smu.smu_outputOFF()
            con.deviceDisconnect()
            self._log_verbose("Disconnected from contact detection device")

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
            self._log_verbose(f"No previous position for manipulator {manipulator_name}, using full stride")
            return base_stride
        
        _, _, current_z = mm.mm_current_position()
        last_contact_z = self.last_z[manipulator_name]
        distance_to_last = abs(current_z - last_contact_z)
        
        # Use slower movement when getting close to the last known contact position
        if distance_to_last <= self.slow_zone_margin:
            # Close to last contact position, use slower movement
            slow_stride = max(1, int(base_stride * self.slow_stride_factor))
            self._log_verbose(f"Close to last contact position (distance: {distance_to_last}), using slow stride: {slow_stride}")
            return slow_stride
        else:
            # Far from last contact position, use full stride
            self._log_verbose(f"Far from last contact position (distance: {distance_to_last}), using full stride: {base_stride}")
            return base_stride

    def _log_verbose(self, message: str) -> None:
        """Log verbose message through GUI logging system if available"""
        if self._log_verbose_func:
            self._log_verbose_func(message)
        else:
            # Fallback to print if no GUI logging available
            print(f"TouchDetect : VERBOSE : {message}")
    
    def _log_info(self, message: str) -> None:
        """Log info message through GUI logging system if available"""
        if self._log_info_func:
            self._log_info_func(message)
        else:
            # Fallback to print if no GUI logging available
            print(f"TouchDetect : INFO : {message}")
    
    def _log_warn(self, message: str) -> None:
        """Log warning message through GUI logging system if available"""
        if self._log_warn_func:
            self._log_warn_func(message)
        else:
            # Fallback to print if no GUI logging available
            print(f"TouchDetect : WARN : {message}")

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
                self._log_warn(f"Resistance measurement failed: {r}")
                return (status, {"Error message": f"TouchDetect: {r}"})
            r = float(r)

            self._log_verbose(f"Measured resistance: {r} Ω, threshold: {threshold} Ω")
            
            if r < threshold:
                self._log_info(f"Contact detected! Resistance {r} below threshold {threshold}")
                return (0, True)
            return (0, False)

        except Exception as e:
            error_msg = f"Exception in resistance measurement: {str(e)}"
            self._log_warn(error_msg)
            return (3, {"Error message": "touchDetect error", "exception": str(e)})
