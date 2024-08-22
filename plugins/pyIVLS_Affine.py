#!/usr/bin/python3.8
import pluggy
from PyQt6 import QtWidgets

from plugins.plugin import Plugin
from plugins.Affine.Affine import Affine


class pyIVLS_Affine_plugin(Plugin):
    """Hooks for affine conversion plugin
    This class acts as a bridge between plugins"""

    hookimpl = pluggy.HookimplMarker("pyIVLS")

    def __init__(self):
        self.affine = Affine()
        super().__init__()

    @hookimpl
    def get_setup_interface(self, pm, plugin_data) -> dict:
        """Sets up the buttons for affine conversion plugin

        Returns:
            dict: name, widget
        """

        self.setup(pm, plugin_data)

        return {self.plugin_name: self._connect_buttons(self.affine.settingsWidget)}

    @hookimpl
    def get_functions(self, args):
        if args.get("function") == self.plugin_info["function"]:
            return self.get_public_methods()

    def _connect_buttons(self, settingsWidget):
        mask_button = settingsWidget.findChild(QtWidgets.QPushButton, "maskButton")

        find_button = settingsWidget.findChild(QtWidgets.QPushButton, "findButton")

        save_button = settingsWidget.findChild(QtWidgets.QPushButton, "saveButton")
        mask_gds_button = settingsWidget.findChild(
            QtWidgets.QPushButton, "maskGdsButton"
        )
        check_mask_button = settingsWidget.findChild(
            QtWidgets.QPushButton, "checkMaskButton"
        )

        # Connect widget buttons to functions
        mask_button.clicked.connect(self.affine.mask_button)
        find_button.clicked.connect(self._find_button)
        save_button.clicked.connect(self.affine.save_button)
        mask_gds_button.clicked.connect(self.affine.mask_gds_button)
        check_mask_button.clicked.connect(self.affine.check_mask_button)
        if self.affine.A is None:
            self.affine.affine_label.setText(
                "Affine matrix not found. Please click 'Find Affine'."
            )
        self.affine.mask_label.setText("Set mask image.")

        return settingsWidget

    def _find_button(self):
        # FIXME: Might be best to save the functions to reduce the number of calls
        camera_funcs = self.pm.hook.get_functions(args={"function": "camera"})[0]
        img = camera_funcs["VenusUSB2"]["camera_get_image"]()
        self.affine.update_img(img)
        self.affine.find_button()
