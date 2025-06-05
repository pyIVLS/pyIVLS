class touchDetect:
    def __init__(self):
        self.R_WHEN_CONTACT = 1 #ohm
        self.stride_to_contact = 10

    def move_to_contact(self, mm: object, con: object, smu: object, manipulator_info: dict):
        """Moves the spesified micromanipulators to contact with the sample.

        Args:
            mm (object): micromanipulator object
            con (object): contact detection switcher
            smu (object): smu
            manipulator_info (dict): manipulator numbers as keys, contains channel info for measurements
        Returns:
            tuple of (code, status)
        """
        status, state = con.deviceConnect()
        if status != 0:
            return (status, {"message": f"TouchDetect: {state}"})

        try:
            for manipulator_name, info in manipulator_info.items():
                smu_channel = info["channel_smu"]
                condet_channel = info["channel_con"]
                if condet_channel is "Hi":
                    con.deviceHiCheck(True)
                elif condet_channel is "Lo":
                    con.deviceLoCheck(True)
                else:
                    return (1, {"message": f"TouchDetect: Invalid contact detection channel {condet_channel} for manipulator {manipulator_name}"})
                status, state = mm.mm_open()
                if status != 0:
                    return (status, {"message": f"TouchDetect: {state}"})

                mm.mm_change_active_device(manipulator_name)

                while self._contacting(smu, smu_channel)[1] is False:
                    status, state = mm.mm_zmove(self.stride_to_contact)
                    if status != 0:
                        return (status, {"message": f"TouchDetect: {state}"})
            
        except Exception as e:
            return (2, {"message": f"TouchDetect: Error setting contact detection channels", "exception": str(e)})     
        finally:
            con.deviceDisconnect()       
        
    def _contacting(self, smu: object, channel:str):
        """Check resistance at between manipulator probes

        Args:
            smu (object): smu
            channel (str): which channel to measure on
        Returns:
            tuple of (0, bool) when successful, (code, status) with errors
        """
        try:
            r = smu.resistance_measurement(channel)
            if r < self.R_WHEN_CONTACT:
                return (0, True)
            return (0, False)

        except Exception as e:
            return (3, {"message": "touchDetect error", "exception": str(e)})


    



