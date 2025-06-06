class touchDetect:
    def __init__(self):
        self.last_z = {}
        self.recklessness = 10


    def move_to_contact(self, mm: object, con: object, smu: object, manipulator_info: list):
        """Moves the spesified micromanipulators to contact with the sample.

        Args:
            mm (object): micromanipulator object
            con (object): contact detection switcher
            smu (object): smu
            manipulator_info (dict): manipulator numbers as keys, contains channel info for measurements
        Returns:
            tuple of (code, status)
        """
        try:
            status, state = con.deviceConnect()
            status_smu, state_smu = smu.smu_connect()
            if status != 0:
                return (status, {"message": f"{state}"})
            if status_smu != 0:
                return (status_smu, {"message": f"{state_smu}"})
            # iterate through provided instructions for manipulators
            for idx, info in enumerate(manipulator_info):
                manipulator_name = idx + 1
                smu_channel, condet_channel, threshold, stride = info
                # skip iteration for manipulator if nothing is set
                if smu_channel == "" or condet_channel == "":
                    continue

                # switch mode for contact detection
                if condet_channel == "Hi":
                    con.deviceHiCheck(True)
                elif condet_channel == "Lo":
                    con.deviceLoCheck(True)
                else:
                    return (1, {"message": f"TouchDetect: Invalid contact detection channel {condet_channel} for manipulator {manipulator_name}"})
                status, state = mm.mm_open()
                if status != 0:
                    return (status, {"message": f"{state}"})

                # change device and check if the manipulator has a previous z value
                mm.mm_change_active_device(manipulator_name)
                if self.last_z.get(manipulator_name) is not None:
                    if self._contacting(smu,smu_channel, threshold)[1] is False:
                        # move 10 steps away from the last z value
                        mm.mm_zmove(z_change = self.last_z[manipulator_name] - stride * self.recklessness, absolute=True)

                # move until contact
                while self._contacting(smu, smu_channel, threshold)[1] is False:
                    status, state = mm.mm_zmove(stride)
                    if status != 0:
                        return (status, {"message": f"{state}"})
                
                # back to default
                con.deviceLoCheck(False)
                con.deviceHiCheck(False)

                # update the last z value for the manipulator
                _, _, z = mm.mm_current_position()
                self.last_z[manipulator_name] = z
            return (0,{"message": "OK"})
            
        except Exception as e:
            return (2, {"message": f"exception in move_to_contact", "exception": str(e)})     
        finally:
            con.deviceDisconnect()
  
        
    def _contacting(self, smu: object, channel:str, threshold: float):
        """Check resistance at between manipulator probes

        Args:
            smu (object): smu
            channel (str): which channel to measure on
        Returns:
            tuple of (0, bool) when successful, (code, status) with errors
        """
        try:
            status, r = smu.smu_resmes(channel)
            if status != 0:
                return (status, {"message": f"TouchDetect: {r}"})
            r = float(r)

            if r < threshold:
                return (0, True)
            return (0, False)

        except Exception as e:
            return (3, {"message": "touchDetect error", "exception": str(e)})


    



