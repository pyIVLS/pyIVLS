import pluggy
from plugins.Keithley2612B.Keithley2612B import Keithley2612B
from plugins.plugin import Plugin
import numpy as np


class pyIVLS_Keithley2612B_plugin(Plugin):
    hookimpl = pluggy.HookimplMarker("pyIVLS")

    def __init__(self):
        self.smu = Keithley2612B()
        super().__init__()

    @hookimpl
    def get_setup_interface(self, pm, plugin_data) -> dict:
        """returns a widget for a tab in setup, and probably data for the setup structure

        :plugin_type: as all the plugins will be rolled in one loop, but plugins will be of different types, not all of them should return smth.
        This argument will allow the specific implementation of the hook to identify if any response is needed or not.
        :return: dict containing widget and setup structure
        """
        self.setup(pm, plugin_data)
        return {self.plugin_name: self.smu.settingsWidget}

    @hookimpl
    def get_functions(self, args):
        """returns a dict of publicly accessible functions.

        :return: dict of functions
        """

        if args.get("function") == self.plugin_info["function"]:
            return self.get_public_methods()

    def open(self) -> tuple:
        """opens the plugin. If already open, returns True.

        :return: Tuple with plugin name and success
        """
        if self.smu.connect():
            return (self.plugin_name, True)
        return (self.plugin_name, False)

    def run_sweep(self) -> list(np.ndarray):
        """runs a sweep

        :return: list of data
        """
        try:
            ret_list = []
            settings = self.smu.parse_settings_widget()
            for setting in settings:
                if setting["single_ch"]:
                    self.smu.keithley_init(setting)
                    data = self.smu.run_singlech_sweep(setting)
                    ret_list.append(data)
                else:
                    raise NotImplementedError("Two channel mode not implemented yet")
        except Exception as e:
            print(f"Error in run_sweep: {e}")
        finally:
            return ret_list



    def measure_resistance(self, channel):
        """measures resistance

        :return: resistance
        """
        # placeholder. Open the connection if it is not open.
        if self.smu.k is None:
            self.smu.connect()
        return self.smu.resistance_measurement(channel)
