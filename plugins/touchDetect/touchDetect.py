class touchDetect:
    def __init__(self):
        self.R_WHEN_CONTACT = 1 #ohm

    
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
        try:
            for manipulator_name, info in manipulator_info.items():
                smu_channel = info["channel_smu"]
                condet_channel = info["channel_con"]
                condet
        



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


    



