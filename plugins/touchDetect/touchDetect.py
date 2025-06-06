class touchDetect:
    def __init__(self):
        self.R_WHEN_CONTACT = 150 #ohm
        self.stride_to_contact = 10
        self.last_z = {}
        self.recklessness = 150

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
                return (status, {"message": f"TouchDetect: {state}"})
            if status_smu != 0:
                return (status_smu, {"message": f"TouchDetect: {state_smu}"})
            for idx, info in enumerate(manipulator_info):
                manipulator_name = idx + 1
                smu_channel, condet_channel, threshold = info
                # skip iteration for manipulator if nothing is set
                if smu_channel == "" or condet_channel == "":
                    continue
                if condet_channel == "Hi":
                    con.deviceHiCheck(True)
                elif condet_channel == "Lo":
                    con.deviceLoCheck(True)
                else:
                    return (1, {"message": f"TouchDetect: Invalid contact detection channel {condet_channel} for manipulator {manipulator_name}"})
                status, state = mm.mm_open()
                if status != 0:
                    return (status, {"message": f"TouchDetect: {state}"})

                mm.mm_change_active_device(manipulator_name)
                if self.last_z.get(manipulator_name) is not None:
                    print(f"{manipulator_name} has last z at{self.last_z[manipulator_name]}")
                    mm.mm_zmove(z_change = self.last_z[manipulator_name] - self.recklessness, absolute=True)

                while self._contacting(smu, smu_channel, threshold)[1] is False:
                    status, state = mm.mm_zmove(self.stride_to_contact)
                    if status != 0:
                        return (status, {"message": f"TouchDetect: {state}"})
                _, _, z = mm.mm_current_position()
                print(f"Manipulator {manipulator_name} contacted at z={z} with channel {smu_channel}")
                self.last_z[manipulator_name] = z
                print(self.last_z)
            return (0,{"message": "TouchDetect: OK"})
            
        except Exception as e:
            return (2, {"message": f"TouchDetect: Error setting contact detection channels", "exception": str(e)})     
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
            print(f"resistance! {r}")

            if r < threshold:
                return (0, True)
            return (0, False)

        except Exception as e:
            return (3, {"message": "touchDetect error", "exception": str(e)})


    



