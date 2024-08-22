#!/usr/bin/python3.8
import pluggy
from plugins.Keithley.Keithley2612B import Keithley2612B
import numpy as np


class pyIVLS_Keithley2612B_plugin:
    hookimpl = pluggy.HookimplMarker("pyIVLS")

    @hookimpl
    def get_setup_interface(self):
        """returns a widget for a tab in setup, and probably data for the setup structure

        :plugin_type: as all the plugins will be rolled in one loop, but plugins will be of different types, not all of them should return smth.
        This argument will allow the specific implementation of the hook to identify if any response is needed or not.
        :return: dict containing widget and setup structure
        """
        self.smu = Keithley2612B()

        return {"Keithley2612B": self.smu.settingsWidget}

    @hookimpl
    def get_functions(self, args) -> dict[str, callable]:
        """returns a dict of publicly accessible functions.

        :return: dict of functions
        """

        if args.get("device") == "smu":
            return {
                "open": self.smu.connect,
                "run_sweep": self.run_sweep,
                "measure_resistance": self.measure_resistance,
            }

    # DEPRECATED - REMOVE
    def open(self, **kwargs) -> tuple[str, bool]:
        """opens the plugin

        :return: None
        """
        self.smu.connect()

    def run_sweep(self) -> np.ndarray:
        """runs a sweep

        :return: list of data
        """
        try:
            settings = self.smu.parse_settings_widget()
            if settings["single_ch"]:
                self.smu.keithley_init(settings)
                data = self.smu.keithley_run_single_ch_sweep(settings)
                return data
            else:
                raise NotImplementedError("Two channel mode not implemented yet")
        except:
            print("Error in run_sweep")
            return np.array([])

    """
    This should measure the current resistance at some probe. Prolly needs an arg for the probe.
    This should also handle changing the mode to resistance measurement and 
    when the current position is reached, return to normal measurement mode.
    """

    def measure_resistance(self):
        """measures resistance

        :return: resistance
        """
        raise NotImplementedError("Not implemented yet")
