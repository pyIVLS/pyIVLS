import os
from datetime import datetime

from Affine import Affine, AffineError
from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import QObject, Qt, pyqtSignal
from PyQt6.QtGui import QBrush, QImage, QPen, QPixmap
from PyQt6.QtWidgets import QGraphicsPixmapItem, QGraphicsScene


class AffineGUI(QObject):
    """Gui for Affine plugin"""

    log_message = pyqtSignal(str)
    info_message = pyqtSignal(str)
    closeLock = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        # load ui files
        self.settingsWidget, self.MDIWidget = self._load_widgets()
        # init settings if needed
        self.settings = {}

        # init core functionality
        self.affine = Affine()

        # init dependency functions
        self.functions = {}
        self.mdi_img = None
        self.mdi_mask = None

    def _initGUI(self, settings):
        # placeholder
        self.settings = settings
        settingsWidget = self.settingsWidget
        MDIWidget = self.MDIWidget
        last_mask_path = settings.get("default_mask_path", None)
        if last_mask_path is not None:
            try:
                mask = self.affine.update_interal_mask(last_mask_path)
                self._update_MDI(mask, None)
            except AffineError as e:
                self.log_message.emit(e.message)
        # do some stuff tm
        return settingsWidget, MDIWidget

    def _load_widgets(self):
        """Load the widgets from the UI files."""
        # Load the settings based on the name of this file.
        self.path = os.path.dirname(__file__) + os.path.sep
        for _, _, files in os.walk(self.path):
            for file in files:
                if file.endswith(".ui"):
                    if file.split("_")[1].lower() == "settingswidget.ui":
                        settingsWidget = uic.loadUi(self.path + file)
                    elif file.split("_")[1].lower() == "mdiwidget.ui":
                        MDIWidget = uic.loadUi(self.path + file)

        self._find_labels(settingsWidget, MDIWidget)
        settingsWidget, MDIWidget = self._connect_buttons(settingsWidget, MDIWidget)
        return settingsWidget, MDIWidget

    def _find_labels(self, settingsWidget, MDIWidget):
        """Finds the labels in the settings widget."""
        self.camera_label = MDIWidget.findChild(QtWidgets.QGraphicsView, "Camera")
        self.gds_label = MDIWidget.findChild(QtWidgets.QGraphicsView, "Gds")
        self.dispKP = settingsWidget.findChild(QtWidgets.QCheckBox, "dispKP")
        assert self.gds_label is not None, "gds_label not found in MDIWidget"
        self.gds_scene = QGraphicsScene(self.gds_label)
        self.camera_scene = QGraphicsScene(self.camera_label)

        # set the scene to the label
        self.gds_label.setScene(self.gds_scene)
        self.camera_label.setScene(self.camera_scene)

        # set equal size for the graphics views

    def _connect_buttons(self, settingsWidget, MDIWidget):
        """Connects the buttons, checkboxes and label clicks to their actions.

        Args:
            settingsWidget (_type_): _description_
            MDIWidget (_type_): _description_

        Returns:
            _type_: _description_
        """
        mask_button = settingsWidget.findChild(QtWidgets.QPushButton, "maskButton")
        assert mask_button is not None, "maskButton not found in settingsWidget"
        find_button = settingsWidget.findChild(QtWidgets.QPushButton, "findButton")
        assert find_button is not None, "findButton not found in settingsWidget"
        manual_button = settingsWidget.findChild(QtWidgets.QPushButton, "manualButton")
        assert manual_button is not None, "manualButton not found in settingsWidget"
        dispKP = settingsWidget.findChild(QtWidgets.QCheckBox, "dispKP")
        assert dispKP is not None, "dispKP not found in MDIWidget"

        mask_button.clicked.connect(self._mask_button_action)
        find_button.clicked.connect(self._find_button_action)
        manual_button.clicked.connect(self._manual_button_action)
        dispKP.stateChanged.connect(self._disp_kp_state_changed)

        # connect the label click on gds to a function
        self.gds_label.mousePressEvent = lambda event: self._gds_label_clicked(event)

        return settingsWidget, MDIWidget

    def _find_button_action(self):
        """Action for the find button."""
        # Fixme: deebug.
        # img = self.functions["camera"]["camera_capture_image"]()
        img = self.affine.test_image()
        self._update_MDI(None, img)
        try:
            if self.affine.try_match(img):
                timestamp = datetime.now().strftime("%H:%M:%S.%f")
                num_matches = len(self.affine.result["matches"])
                mask = self.affine.result["mask"]
                img = self.affine.result["img"]
                self._update_MDI(mask, img)

                self.log_message.emit(
                    f"{timestamp}: Found {num_matches} matches between the image and the mask."
                )
        except AffineError as e:
            self.log_message.emit(e.message)

    def _manual_button_action(self):
        """Action for the save button."""
        print("manual button pressed")

    def _mask_button_action(self):
        """Interface for the gds mask loading button."""
        try:
            fileName, _ = QtWidgets.QFileDialog.getOpenFileName(
                self.settingsWidget,
                "Open .GDS, .png or .jpg file",
                self.path + os.sep + "masks",
                "Mask Files (*.gds);;Images (*.png *.jpg)",
            )
            if fileName:
                mask = self.affine.update_interal_mask(fileName)
                self._update_MDI(mask, None)
        except AffineError as e:
            self.log_message.emit(e.message)

    def _disp_kp_state_changed(self):
        """Action for the dispKP checkbox."""
        try:
            if self.dispKP.isChecked():
                img, mask = self.affine.draw_keypoints()
                self._update_MDI(mask, img, save_internal=False)
            else:
                img, mask = self.mdi_img, self.mdi_mask
                self._update_MDI(mask, img)
        except AffineError:
            pass

    def _gds_label_clicked(self, event):
        print("what the sigma")
        # Map from view coords → scene coords
        pos = self.gds_label.mapToScene(event.pos())
        x, y = pos.x(), pos.y()

        self.gds_scene.addEllipse(
            x - 3,
            y - 3,
            6,
            6,
            brush=QBrush(Qt.GlobalColor.red),
            pen=QPen(Qt.GlobalColor.transparent),
        )
        # convert the clicked coords to the image coords
        try:
            img_x, img_y = self.affine.coords((x, y))

            # Draw red dot on the image scene
            self.camera_scene.addEllipse(
                img_x - 3,
                img_y - 3,
                6,
                6,
                brush=QBrush(Qt.GlobalColor.red),
                pen=QPen(Qt.GlobalColor.transparent),
            )
        except AffineError as e:
            print(f"Affine transform failed: {e}")

    def _update_MDI(self, mask, img, save_internal=True):
        """Updates the MDI widget with the mask and image.
        This wants 3 ch images"""
        if img is not None:
            h, w, ch = img.shape
            bytes_per_line = ch * w
            qimg = QImage(img.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg)
            pixmap_item = QGraphicsPixmapItem(pixmap)

            # Create or update the scene
            self.camera_scene.addItem(pixmap_item)
            self.camera_label.setScene(self.camera_scene)
            if save_internal:
                self.mdi_img = img

        if mask is not None:
            h, w, ch = mask.shape
            bytes_per_line = ch * w
            qmask = QImage(mask.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qmask)
            pixmap_item = QGraphicsPixmapItem(pixmap)

            # Create or update the scene
            self.gds_scene.addItem(pixmap_item)
            self.gds_label.setScene(self.gds_scene)

            if save_internal:
                self.mdi_mask = mask

    def _getLogSignal(self):
        return self.log_message

    def _getInfoSignal(self):
        return self.info_message

    def _getCloseLockSignal(self):
        return self.closeLock

    def _fetch_dependency_functions(self, function_dict, dependencies):
        # FIXME: doesn't give proper returns since I think that it is not necessary
        # to parse out spesific functions from the dependencies
        for function in function_dict:
            if function in dependencies:
                try:
                    self.functions[function] = function_dict[function]
                except KeyError:
                    self.log_message.emit(
                        f"AffineFunction {function} not found for Affine plugin."
                    )
        return []

    def _get_public_methods(self, function: str) -> dict:
        """
        Returns a nested dictionary of public methods for the plugin
        """
        methods = {
            method: getattr(self, method)
            for method in dir(self)
            if callable(getattr(self, method))
            and not method.startswith("__")
            and not method.startswith("_")
            and method.startswith(f"{function.lower()}_")
        }
        return methods

    def positioning_coords(self, coords: tuple[float, float]) -> tuple[float, float]:
        """Returns the coordinates of the positioner."""
        return self.affine.coords(coords)
