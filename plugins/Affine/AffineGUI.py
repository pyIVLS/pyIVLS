import os


from Affine_skimage import Affine, AffineError
from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import Qt, pyqtSlot, QPointF
from PyQt6.QtGui import QAction, QBrush, QImage, QPen, QPixmap
from PyQt6.QtWidgets import QGraphicsPixmapItem, QGraphicsScene, QMenu
import csv
from affineDialog import dialog
from plugin_components import LoggingHelper, CloseLockSignalProvider, public, get_public_methods
from gdsLoadFunctionality import gdsLoadDialog
from PyQt6.QtCore import QObject
from Affine_MDI import DualGraphicsWidget
import numpy as np

# TODO: connect signals and slots for inputting new points.


def image_to_scene(image: np.ndarray) -> QGraphicsScene:
    """Converts a numpy ndarray image to a QGraphicsScene."""
    height, width = image.shape[:2]
    if len(image.shape) == 2:
        # Grayscale image
        qimage = QImage(image.data, width, height, width, QImage.Format.Format_Grayscale8)
    else:
        # Color image
        qimage = QImage(image.data, width, height, 3 * width, QImage.Format.Format_RGB888)

    pixmap = QPixmap.fromImage(qimage)
    scene = QGraphicsScene()
    pixmap_item = QGraphicsPixmapItem(pixmap)
    scene.addItem(pixmap_item)
    return scene


class AffineGUI(QObject):
    """
    GUI implementation of the Affine plugin for pyIVLS.

    public API:

    -positioning_coords(coords: tuple[float, float]) -> tuple[float, float]

    revision 2.0.0
    -Added dialog for matching and manual mode. Added settings for preprocessing.
    -Formatted into proper pyIVLS plugin format.

    Revision 0.1.1
    -Manual mode implementeted.

    version 0.1
    2025.05.21
    otsoha
    """

    COORD_DATA = Qt.ItemDataRole.UserRole + 1

    def __init__(self, settings=None):
        super().__init__()
        # load ui files
        self.MDIWidget = DualGraphicsWidget()
        self.settingsWidget = self._load_widgets()
        # init settings if needed
        self.settings = settings if settings is not None else {}
        # init core functionality
        self.affine = Affine(self.settings)
        self.dependency = ["camera"]
        self.logger = LoggingHelper(self)
        self.closelock = CloseLockSignalProvider()
        # init dependency functions
        self.functions = {}
        self.dialog = None
        self.temp_points = list[QPointF]()
        self.mask = None  # internal reference to the mask ndarray

    # TODO: Read settings from file, for instance latest points and mask + default names for text inputs.
    def _initGUI(self, settings):
        self._gui_change_mask_uploaded(False)
        self.settings = settings
        settingsWidget: QtWidgets.QWidget = self.settingsWidget
        MDIWidget = self.MDIWidget
        pointcount = settings.get("pointcount", 2)
        addpointscheck = settings.get("addpointscheck", "False")
        centerclicks = settings.get("centerclicks", "False")
        centerclicks = True if centerclicks == "True" else False
        addpointscheck = True if addpointscheck == "True" else False
        ratiotest = float(settings["ratiotest"])
        residualthreshold = int(settings["residualthreshold"])
        crosscheck = True if settings["crosscheck"] == "True" else False
        backend = settings.get("backend", "SIFT")
        default_camera = settings["cameracombobox"]
        # set the camera combobox to the default camera
        if default_camera:
            cambox = settingsWidget.findChild(QtWidgets.QComboBox, "cameraComboBox")
            cambox.setCurrentText(default_camera)
        # set the settings widget values
        self.settingsWidget.pointCount.setValue(int(pointcount))
        self.settingsWidget.centerClicks.setChecked(centerclicks)

        # read preprocessing settings
        s = {}
        s["sigmaimage"] = settings.get("sigmaimage")
        s["sigmamask"] = settings.get("sigmamask")
        s["sigmaimage"] = float(s["sigmaimage"])
        s["sigmamask"] = float(s["sigmamask"])
        s["blurmask"] = settings["blurmask"]
        s["invertmask"] = settings["invertmask"]
        s["equalizemask"] = settings["equalizemask"]
        s["cannymask"] = settings["cannymask"]
        s["otsumask"] = settings["otsumask"]
        s["manualthresholdmask"] = settings.get("manualthresholdmask", "False")
        s["thresholdmask"] = settings.get("thresholdmask", "128")
        s["morphologymask"] = settings.get("morphologymask", "False")
        s["morphologytypemask"] = settings.get("morphologytypemask", "erosion")
        s["morphologystrengthmask"] = settings.get("morphologystrengthmask", "3")
        s["blurimage"] = settings["blurimage"]
        s["invertimage"] = settings["invertimage"]
        s["equalizeimage"] = settings["equalizeimage"]
        s["cannyimage"] = settings["cannyimage"]
        s["otsuimage"] = settings["otsuimage"]
        s["manualthresholdimage"] = settings.get("manualthresholdimage", "False")
        s["thresholdimage"] = settings.get("thresholdimage", "128")
        s["morphologyimage"] = settings.get("morphologyimage", "False")
        s["morphologytypeimage"] = settings.get("morphologytypeimage", "erosion")
        s["morphologystrengthimage"] = settings.get("morphologystrengthimage", "3")
        # convert to boolean from string literals "True" and "False"
        s["blurmask"] = True if s["blurmask"] == "True" else False
        s["invertmask"] = True if s["invertmask"] == "True" else False
        s["equalizemask"] = True if s["equalizemask"] == "True" else False
        s["cannymask"] = True if s["cannymask"] == "True" else False
        s["otsumask"] = True if s["otsumask"] == "True" else False
        s["manualthresholdmask"] = True if s["manualthresholdmask"] == "True" else False
        s["thresholdmask"] = int(s["thresholdmask"])
        s["morphologymask"] = True if s["morphologymask"] == "True" else False
        s["morphologystrengthmask"] = int(s["morphologystrengthmask"])
        s["blurimage"] = True if s["blurimage"] == "True" else False
        s["invertimage"] = True if s["invertimage"] == "True" else False
        s["equalizeimage"] = True if s["equalizeimage"] == "True" else False
        s["cannyimage"] = True if s["cannyimage"] == "True" else False
        s["otsuimage"] = True if s["otsuimage"] == "True" else False
        s["manualthresholdimage"] = True if s["manualthresholdimage"] == "True" else False
        s["thresholdimage"] = int(s["thresholdimage"])
        s["morphologyimage"] = True if s["morphologyimage"] == "True" else False
        s["morphologystrengthimage"] = int(s["morphologystrengthimage"])
        s["ratiotest"] = ratiotest
        s["residualthreshold"] = residualthreshold
        s["crosscheck"] = crosscheck
        s["backend"] = backend

        # set the preprocessing settings to the affine object
        self.affine.update_settings(s)

        return settingsWidget, MDIWidget

    def _load_widgets(self):
        """Load the widgets from the UI files."""
        # Load the settings based on the name of this file.
        settingsWidget = None
        self.path = os.path.dirname(__file__) + os.path.sep
        for _, _, files in os.walk(self.path):
            for file in files:
                if file.endswith(".ui"):
                    try:
                        if file.split("_")[1].lower() == "settingswidget.ui":
                            settingsWidget = uic.loadUi(self.path + file)  # type: ignore
                    except IndexError:
                        continue

        assert settingsWidget is not None, "Settings widget not found in the plugin directory."
        self._find_labels(settingsWidget)
        settingsWidget = self._connect_buttons(settingsWidget)
        return settingsWidget

    def _find_labels(self, settingsWidget):
        """Finds the labels in the settings widget."""

        # inputs
        self.dispKP = settingsWidget.findChild(QtWidgets.QCheckBox, "dispKP")
        self.pointCount = settingsWidget.findChild(QtWidgets.QSpinBox, "pointCount")
        self.pointName = settingsWidget.findChild(QtWidgets.QLineEdit, "pointName")
        self.definedPoints = settingsWidget.findChild(QtWidgets.QListWidget, "definedPoints")
        self.definedPoints.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.cameraComboBox: QtWidgets.QComboBox = settingsWidget.cameraComboBox

    def _connect_buttons(self, settingsWidget):
        """Connects the buttons, checkboxes and label clicks to their actions.

        Args:
            settingsWidget (_type_): _description_
            MDIWidget (_type_): _description_

        Returns:
            _type_: _description_
        """
        # Save inputs that are used in multiple functions
        self.centerCheckbox = settingsWidget.findChild(QtWidgets.QCheckBox, "centerClicks")

        # add a custom context menu in the list widget to allow point deletion
        self.definedPoints.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.definedPoints.customContextMenuRequested.connect(self._list_widget_context_menu)
        # connect item click to draw the points on the mask and image.
        self.definedPoints.itemClicked.connect(self._list_item_clicked_action)

        # connect the buttons to their actions
        settingsWidget.maskButton.clicked.connect(self._mask_button_action)
        settingsWidget.savePoints.clicked.connect(self.save_points_action)
        settingsWidget.importPoints.clicked.connect(self._import_points_action)
        settingsWidget.showButton.clicked.connect(self._open_dialog)

        # connect clicks on views to functionality
        self.MDIWidget._view_left.point_clicked.connect(self._on_mask_point_clicked)
        self.MDIWidget._view_right.point_clicked.connect(self._on_image_point_clicked)

        return settingsWidget

    # GUI Functionality

    @pyqtSlot(QPointF)
    def _on_mask_point_clicked(self, point: QPointF):
        print(f"Mask point clicked: {point}")
        self.temp_points.append(point)
        if len(self.temp_points) == self.pointCount.value():
            # add points to list widget
            name = self.pointName.text() if self.pointName.text() != "" else f"Point set {self.definedPoints.count() + 1}"
            self.update_list_widget(self.temp_points, name)
            self.temp_points = []

    @pyqtSlot(QPointF)
    def _on_image_point_clicked(self, point: QPointF):
        print(f"Image point clicked: {point}")

    def _gui_change_mask_uploaded(self, mask_loaded):
        self.settingsWidget.affineBox.setEnabled(mask_loaded)
        self.settingsWidget.groupBox.setEnabled(mask_loaded)

    def _list_widget_context_menu(self, pos):
        def remove_item(item):
            self.definedPoints.takeItem(self.definedPoints.row(item))

        item = self.definedPoints.itemAt(pos)
        if item is None:
            return

        menu = QMenu()
        delete_action = QAction("Delete", self.definedPoints)
        rename_action = QAction("Rename", self.definedPoints)
        rename_action.triggered.connect(lambda: item.setText("New name"))
        delete_action.triggered.connect(lambda: remove_item(item))
        menu.addAction(delete_action)
        menu.exec(self.definedPoints.mapToGlobal(pos))

    def save_points_action(self):
        """Action for the save button."""
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(
            self.settingsWidget,
            "Save points",
            self.path + os.sep + "measurement_points",
            ".csv (*.csv);;All Files (*)",
        )
        if fileName:
            with open(fileName, "w", newline="") as csvfile:
                cswriter = csv.writer(csvfile, delimiter=",")
                fields = ["Name", "x_mask", "y_mask", "x_img", "y_img"]
                cswriter.writerow(fields)
                for i in range(self.definedPoints.count()):
                    item = self.definedPoints.item(i)
                    name = item.text()
                    points = item.data(self.COORD_DATA)
                    for x_mask, y_mask in points:
                        if self.affine.A is not None:
                            img_x, img_y = self.affine.coords((x_mask, y_mask))
                        else:
                            img_x, img_y = -1, -1
                        cswriter.writerow([name, x_mask, y_mask, img_x, img_y])

    def _import_points_action(self):
        """Action for the import points button."""
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.settingsWidget,
            "Open points file",
            self.path + os.sep + "measurement_points",
            "comma-separated values (*.csv);;All Files (*)",
        )
        if fileName:
            point_dict = {}
            with open(fileName, "r") as csvfile:
                csreader = csv.reader(csvfile, delimiter=",")
                next(csreader)
                for row in csreader:
                    # extract the name and coordinates
                    name = row[0]
                    x_mask = float(row[1])
                    y_mask = float(row[2])
                    point_dict.setdefault(name, []).append((x_mask, y_mask))
            for name, points in point_dict.items():
                self.update_list_widget(points, name)

    def _list_item_clicked_action(self, item):
        # Draw all points from all selected items
        selected_items = self.definedPoints.selectedItems()
        all_points = []
        for sel_item in selected_items:
            points = sel_item.data(self.COORD_DATA)
            if points:
                all_points.extend(points)
        if not all_points:
            return
        self.draw_points_mdi(all_points, Qt.GlobalColor.red, clear_scene=True)

    def _mask_button_action(self):
        """Interface for the gds mask loading button."""
        try:
            fileName, _ = QtWidgets.QFileDialog.getOpenFileName(
                self.settingsWidget,
                "Open .GDS, .png or .jpg file",
                self.path + os.sep + "masks",
                "Mask Files (*.gds);;Images (*.png *.jpg)",
            )
            # we now have a filename, try to load the mask
            if fileName:
                if fileName.endswith(".gds"):
                    self.dialog = gdsLoadDialog(fileName)
                    result = self.dialog.exec()
                    if result == QtWidgets.QDialog.DialogCode.Rejected:
                        return
                    mask = self.dialog.get_mask()
                    if mask is None:
                        return
                    mask = self.affine.update_internal_mask_preprocessing(fileName, mask)
                # image file, use old pathway
                else:
                    mask = self.affine.update_internal_mask(fileName)

                # mask is now a ndarray, convert to scene and set to mdi
                mask_scene = image_to_scene(mask)
                self.MDIWidget.set_scene("left", mask_scene)
                self.settingsWidget.label.setText(f"Mask loaded: {os.path.basename(fileName)}")
                self._gui_change_mask_uploaded(mask_loaded=True)
                self.mask = mask  # keep internal reference to the mask ndarray for passing to dialog
        except AffineError as e:
            self.logger.log_error(e.message)

    def _open_dialog(self):
        """Opens the matching dialog for aff transformation."""

        def _on_close():
            assert self.dialog is not None, "Dialog is not initialized."
            res = self.affine.result.get("matches", None)
            if res is not None and len(res) > 0:
                self.logger.log_info(f"Affine: Transformation confirmed. {len(res)} matches found.")
            else:
                self.logger.log_info("Affine: No transformation confirmed")
            self.dialog = None

        img = self.functions["camera"][self.cameraComboBox.currentText()]["camera_capture_image"]()
        if img[0] != 0:
            self.logger.log_error(f"Affine: Error capturing image: {img[1]}")
            return
        # update img to mdi
        img_scene = image_to_scene(img[1])
        self.MDIWidget.set_scene("right", img_scene)

        # Get defined points as a flat list of (x_mask, y_mask)
        pointslist = []
        for i in range(self.definedPoints.count()):
            pts = self.definedPoints.item(i).data(self.COORD_DATA)
            if pts:
                pointslist.extend(pts)
        if not pointslist:
            pointslist = None
        status, settings = self.parse_settings_widget()
        if status == 0:
            # Pass the settings dict to the dialog
            self.dialog = dialog(self.affine, img[1], self.mask, settings, pointslist=pointslist, logger=self.logger)
            self.dialog.finished.connect(_on_close)
            self.dialog.show()
        else:
            self.logger.log_warn(f"Affine: Error parsing settings widget: {settings['error message']} {settings['exception']}")

    def update_list_widget(self, points: list[QPointF], name: str):
        """
        Updates the list widget with the given points and name.
        If clear_list is True, clears the list before adding the new points.
        """
        item = QtWidgets.QListWidgetItem(name)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        item.setData(self.COORD_DATA, points)
        self.definedPoints.addItem(item)

    # hook implementations

    def _getLogSignal(self):
        return self.logger.logger_signal

    def _getInfoSignal(self):
        return self.logger.info_popup_signal

    def _getCloseLockSignal(self):
        return self.closelock.closeLock

    def _fetch_dependency_functions(self, function_dict):
        self.missing_functions = []
        self.functions = {}

        for dep_category in self.dependency:
            if dep_category not in function_dict:
                self.missing_functions.append(dep_category)

            else:
                self.functions[dep_category] = function_dict[dep_category]

        # self.functions["camera"] is a list of nested dictionaries, iterate through every camera

        self.cameraComboBox.clear()
        cameras = self.functions.get("camera", {})
        if not cameras:
            return self.missing_functions
        else:
            for camera in self.functions["camera"]:
                # get the camera name (key of the dictionary)
                self.cameraComboBox.addItem(camera)

        return self.missing_functions

    def _get_public_methods(self, function: str) -> dict:
        """
        Returns a nested dictionary of public methods for the plugin
        """
        return get_public_methods(self)

    # public API

    # FIXME: non standard return type for plugin
    @public
    def positioning_coords(self, coords: tuple[float, float]) -> tuple[float, float]:
        """Returns the transformed coordinates."""
        try:
            transformed = self.affine.coords(coords)
            return transformed
        except AffineError:
            return (-1, -1)

    @public
    def positioning_measurement_points(self):
        """Returns the measurement points defined in the list widget."""
        points = []
        names = []
        for i in range(self.definedPoints.count()):
            item = self.definedPoints.item(i)
            if item is not None:
                points.append(item.data(self.COORD_DATA))
                names.append(item.text())
        return points, names

    @public
    def parse_settings_widget(self):
        """Parse settings widget, return dict"""
        try:
            settings = {
                "pointcount": self.settingsWidget.pointCount.value(),
                "cameraComboBox": self.settingsWidget.cameraComboBox.currentText(),
                "centerClicks": self.centerCheckbox.isChecked(),
            }
            # extend the settings with the preprprocessing settings
            s = self.affine.preprocessor.settings
            # convert prepro settings to correct types
            settings["ratiotest"] = float(self.affine.ratio_test)
            settings["residualthreshold"] = int(self.affine.residual_threshold)
            settings["crosscheck"] = True if self.affine.cross_check else False
            settings["backend"] = self.affine.backend
            settings["scalingfactor"] = self.affine.scalingfactor
            settings.update(s)

            assert settings["sigmaimage"] >= 0, "sigmaImage must be non-negative"
            assert settings["sigmamask"] >= 0, "sigmaMask must be non-negative"
            assert 0 <= settings["thresholdimage"] <= 255, "thresholdImage must be between 0 and 255"
            assert 0 <= settings["thresholdmask"] <= 255, "thresholdMask must be between 0 and 255"
            assert 1 <= settings["morphologystrengthimage"] <= 15, "morphologyStrengthImage must be between 1 and 15"
            assert 1 <= settings["morphologystrengthmask"] <= 15, "morphologyStrengthMask must be between 1 and 15"
        except AttributeError as e:
            return 2, {
                "error message": f"settings widget not initialized : {str(e)}",
                "exception": str(e),
            }
        except (ValueError, AssertionError) as e:
            return 1, {"error message": f"Affine value error: {str(e)}", "exception": str(e)}
        return 0, settings
