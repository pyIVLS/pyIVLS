import os
from touchDetect import touchDetect
from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6 import uic  
from PyQt6.QtWidgets import QWidget, QComboBox , QGroupBox
from PyQt6.QtCore import QObject

from datetime import datetime


class touchDetectGUI(QObject):


    non_public_methods = []  
    public_methods = []  
    green_style = "border-radius: 10px; background-color: rgb(38, 162, 105); min-height: 20px; min-width: 20px;"
    red_style = "border-radius: 10px; background-color: rgb(165, 29, 45); min-height: 20px; min-width: 20px;"

    ########Signals
    # signals retained since this plugins needs to send errors to main window.
    log_message = pyqtSignal(str)
    info_message = pyqtSignal(str)
    def emit_log(self, message: str):
        """creates a log message with timestamp and plugin name."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        plugin_name = "touchDetect"
        self.log_message.emit(f"{timestamp}: {plugin_name} caught: {message}")

    @property
    def dependency(self):
        return self._dependencies
    
    @dependency.setter
    def dependency(self, value):
        if isinstance(value, list):
            self._dependencies = value
            self.dependencies_changed()
        else:
            raise TypeError("AffineMove: Dependencies must be a list")
    
    ########Functions
    def __init__(self):
        super().__init__()
        self.path = os.path.dirname(__file__) + os.path.sep
        # depenenies are in format plugin: object, metadata: dict.
        self._dependencies = [None, None]
        self.functionality = touchDetect()

        self.settingsWidget = uic.loadUi(self.path + "touchDetect_Settings.ui")

        # Initialize the combo boxes for dependencies
        self.smu_box: QComboBox = self.settingsWidget.smuBox
        self.micromanipulator_box: QComboBox = self.settingsWidget.micromanipulatorBox
        self.condet_box: QComboBox = self.settingsWidget.condetBox

        # find status labels and indicators
        self.smu_indicator = self.settingsWidget.smuIndicator
        self.mm_indicator = self.settingsWidget.mmIndicator
        self.con_indicator = self.settingsWidget.conIndicator

        # find manipulator boxes
        man1: QGroupBox = self.settingsWidget.manipulator1
        man2: QGroupBox = self.settingsWidget.manipulator2
        man3: QGroupBox = self.settingsWidget.manipulator3
        man4: QGroupBox = self.settingsWidget.manipulator4

        # find comboboxes in manipulator boxes
        man1_smu_box: QComboBox = man1.findChild(QComboBox, "mansmu_1")
        man1_con_box: QComboBox = man1.findChild(QComboBox, "mancon_1")
        man2_smu_box: QComboBox = man2.findChild(QComboBox, "mansmu_2")
        man2_con_box: QComboBox = man2.findChild(QComboBox, "mancon_2")
        man3_smu_box: QComboBox = man3.findChild(QComboBox, "mansmu_3")
        man3_con_box: QComboBox = man3.findChild(QComboBox, "mancon_3")
        man4_smu_box: QComboBox = man4.findChild(QComboBox, "mansmu_4")
        man4_con_box: QComboBox = man4.findChild(QComboBox, "mancon_4")

        self.manipulator_boxes = [[man1, man1_smu_box, man1_con_box],
                                  [man2, man2_smu_box, man2_con_box],
                                  [man3, man3_smu_box, man3_con_box],
                                  [man4, man4_smu_box, man4_con_box]]
        
        self.settings = [{}, {}, {}, {}]  

        # find threshold line edit
        self.threshold = self.settingsWidget.reshold
        self.stride = self.settingsWidget.stride
        

    ########Functions
    ########GUI Slots


    ########Functions
    ################################### internal

    def _fetch_dep_plugins(self):
        """returns the micromanipulator, smu and contacting plugins based on the current selection in the combo boxes.

        Returns:
            tuple[mm, smu, con]: micromanipulator, smu and con plugins.
        Raises:
            AssertionError: if any of the plugins is not found.
        """

        micromanipulator = None
        smu = None
        condet = None
        for plugin, metadata in self.dependency:
            if metadata.get("function") == "micromanipulator":
                current_text = self.micromanipulator_box.currentText()
                if current_text == metadata.get("name"):
                    micromanipulator = plugin
            elif metadata.get("function") == "smu":
                if self.smu_box.currentText() == metadata.get("name"):
                    smu = plugin
            elif metadata.get("function") == "contacting":
                if self.condet_box.currentText() == metadata.get("name"):
                    condet = plugin
        
        assert micromanipulator is not None, "touchDetect: micromanipulator plugin is None"
        assert smu is not None, "touchDetect: smu plugin is None"
        assert condet is not None, "touchDetect: contacting plugin is None"
        
        return micromanipulator, smu, condet


    ########Functions
    ########GUI changes

    def update_status(self):
        """
        Updates the status of the mm, smu and contacting plugins. 
        This function is called when the status changes.
        """
        mm, smu, con = self._fetch_dep_plugins()
        self.channel_names = smu.smu_channelNames()
        if self.channel_names is not None:
            self.smu_indicator.setStyleSheet(self.green_style)
        status, state = mm.mm_devices()

        if status == 0: 
            self.mm_indicator.setStyleSheet(self.green_style)
            for i,status in enumerate(state):
                if status:
                    box, smu_box, con_box = self.manipulator_boxes[i]
                    box.setVisible(True)
                    smu_box.clear()
                    con_box.clear()
                    smu_box.addItems(self.channel_names)
                    con_box.addItems(["Hi", "Lo"])

                    settings = self.settings[i]
                    if "channel_smu" in settings:
                        smu_box.setCurrentText(settings["channel_smu"])
                    if "channel_con" in settings:
                        con_box.setCurrentText(settings["channel_con"])
        else:
            self.emit_log(state)
        con_status, con_state = con.deviceConnect()
        if con_status == 0:
            self.con_indicator.setStyleSheet(self.green_style)
            con_status, con_state = con.deviceDisconnect()
        else:
            self.emit_log(con_state)


    def dependencies_changed(self):
        self.smu_box.clear()
        self.micromanipulator_box.clear()
        self.condet_box.clear()
        
        for plugin, metadata in self.dependency:
            if metadata.get("function") == "micromanipulator":
                self.micromanipulator_box.addItem(metadata.get("name"))
            elif metadata.get("function") == "smu":
                self.smu_box.addItem(metadata.get("name"))
            elif metadata.get("function") == "contacting":
                self.condet_box.addItem(metadata.get("name"))
        self.micromanipulator_box.setCurrentIndex(0)
        self.smu_box.setCurrentIndex(0)
        self.condet_box.setCurrentIndex(0)

    ########Functions
    ########plugins interraction

    def _getLogSignal(self):
        return self.log_message

    def _getInfoSignal(self):
        return self.info_message

    def setup(self, settings) -> QWidget:
        """
        Sets up the GUI for the plugin. This function is called by hook to initialize the GUI.
        """
        def parse_ini(settings: dict):
            temp = [{}, {}, {}, {}]
            for key, value in settings.items():
                try:
                    # split at "_"
                    number, func = key.split("_")
                    number = int(number)
                    if func == "smu":
                        temp[number-1]["channel_smu"] = value
                    elif func == "con":
                        temp[number-1]["channel_con"] = value
                except ValueError:
                    # this is here to make sure that only _1, _2, etc. are parsed for manipulator settings
                    continue
            stride = settings.get("stride", "")
            threshold = settings.get("res_threshold", "")
            return temp, threshold, stride


        for box, _, _ in self.manipulator_boxes:
            box.setVisible(False)
        # save the settings dict to be used later
        self.settings, threshold, stride = parse_ini(settings)
        self.threshold.setText(threshold)
        self.stride.setText(stride)
        self.settingsWidget.initButton.clicked.connect(self.update_status)
        self.settingsWidget.pushButton.clicked.connect(self._test)
        return self.settingsWidget

    def _test(self):
        status, state = self.move_to_contact()
        print(f"{status}, {state}")        



    def parse_settings_widget(self) -> dict:
        """
        parses settings widget, returns error code and settings.
        TODO: Return a dict?
        """
        settings = []
        for i, (box, smu_box, con_box) in enumerate(self.manipulator_boxes):
            smu_channel = smu_box.currentText()
            con_channel = con_box.currentText()
            settings.append((smu_channel, con_channel))

        # check that the same con channel does not appear twice
        con_channels = [s[1] for s in settings] 
        # remove "" from channels
        con_channels = [chn for chn in con_channels if chn != ""]        
        if len(con_channels) != len(set(con_channels)):
            return (1, {"message": "Contact detection channels must be unique across manipulators."})

        # check that the threshold is a float
        try:
            threshold = float(self.threshold.text())
        except ValueError:
            return (1, {"message": "TouchDetect: Threshold must be a number."})
        
        # check that the stride is an integer
        try:
            stride = int(self.stride.text())
        except ValueError:
            return (1, {"message": "TouchDetect: Stride must be an integer."})


        return (0, settings)

    ########Functions to be used externally
    def move_to_contact(self):
        def create_dict():
            # check settings
            status, settings = self.parse_settings_widget()
            if status == 0:
                temp = []
                threshold = float(self.threshold.text())
                stride = int(self.stride.text())
                for i in range(len(self.manipulator_boxes)):
                    devnum = i + 1
                    _, smu_box, con_box = self.manipulator_boxes[i]
                    temp.append((smu_box.currentText(), con_box.currentText(), threshold, stride))
                return temp
            else:
                self.emit_log(settings.get("message", "Unknown error"))
                return None
        mm, smu, con = self._fetch_dep_plugins()
        manipulator_info = create_dict()

        status, state = self.functionality.move_to_contact(mm, con, smu, manipulator_info)

        if status != 0:
            self.emit_log(f"{state.get('message', 'Unknown error')}, Exception: {state.get('exception', 'Not provided')}")
            return (status, state)
        return (status, state)




        