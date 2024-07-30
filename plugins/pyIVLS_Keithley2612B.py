#!/usr/bin/python3.8
import pluggy
from plugins.Keithley.Keithley2612B import Keithley2612B


class pyIVLS_Keithley2612B_plugin:
    hookimpl = pluggy.HookimplMarker("pyIVLS")

    @hookimpl
    def get_setup_interface(self, kwargs):
        print(kwargs)
        """returns a widget for a tab in setup, and probably data for the setup structure

          :plugin_type: as all the plugins will be rolled in one loop, but plugins will be of different types, not all of them should return smth. 
          This argument will allow the specific implementation of the hook to identify if any response is needed or not. 
          :return: dict containing widget and setup structure
          """
        self.smu = Keithley2612B()
        print("I am getting info for the Keithley plugin")

        return self.smu.settingsWidget
