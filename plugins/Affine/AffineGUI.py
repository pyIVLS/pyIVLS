import os


from Affine_skimage import Affine, AffineError
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, pyqtSlot, QPointF, pyqtSignal, QObject
from PyQt6.QtGui import QAction, QImage, QPixmap
from PyQt6.QtWidgets import QGraphicsPixmapItem, QGraphicsScene, QMenu, QGroupBox, QLabel
import csv
from affineDialog import dialog
from plugin_components import LoggingHelper, CloseLockSignalProvider, public, get_public_methods, ini_to_bool, DependencyManager, load_widget
from gdsLoadFunctionality import gdsLoadDialog
from Affine_MDI import DualGraphicsWidget
import numpy as np


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

    rev 2.1.0
    - Major refactoring and bugfixes

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
    gui_update_signal = pyqtSignal()

    def __init__(
        self,
    ):
        super().__init__()
        # load ui files
        self.MDIWidget = DualGraphicsWidget()
        path = os.path.dirname(os.path.abspath(__file__))
        self.path = path + os.path.sep
        self.settingsWidget = load_widget(settings=True, mdi=False, path=path)
        self._find_labels(self.settingsWidget)
        self._connect_buttons(self.settingsWidget)

        self.settings = {}
        # init core functionality
        self.affine = Affine(None)

        self.logger = LoggingHelper(self)
        self.closelock = CloseLockSignalProvider()

        # initialize dependencyManager
        dependencies = {"camera": ["camera_capture_image"]}
        self.dm = DependencyManager("affine", dependencies, self.settingsWidget, {"camera": "cameraComboBox"})

        # init dependency functions
        self.dialog = None
        self.temp_points = list[QPointF]()
        self.mask = None  # internal reference to the mask ndarray

        # connect gui update signal
        self.gui_update_signal.connect(self._gui_update)

    @property
    def function_dict(self):
        return self.dm.function_dict

    def _initGUI(self, settings):
        # Keep mask-related UI state aligned with whether a mask is currently loaded.
        self._gui_change_mask_uploaded(self.mask is not None)
        # init camerabox through dm
        self.dm.initialize_dependency_selection(settings)

        self.settings = settings

        # set the preprocessing settings to the affine object
        self.affine.update_settings(settings)

        # write to GUI elements from settings dict
        self.set_gui_from_settings()

        return self.settingsWidget, self.MDIWidget

    def _find_labels(self, settingsWidget):
        """Finds the labels in the settings widget."""

        # inputs
        self.dispKP = settingsWidget.findChild(QtWidgets.QCheckBox, "dispKP")
        self.pointCount = settingsWidget.findChild(QtWidgets.QSpinBox, "pointCount")
        self.pointName = settingsWidget.findChild(QtWidgets.QLineEdit, "pointName")
        self.definedPoints = settingsWidget.findChild(QtWidgets.QListWidget, "definedPoints")
        self.definedPoints.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.definedPoints.setDragEnabled(True)
        self.definedPoints.setAcceptDrops(True)
        self.definedPoints.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.InternalMove)
        self.definedPoints.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.cameraComboBox: QtWidgets.QComboBox = settingsWidget.cameraComboBox
        self.affineBox = settingsWidget.findChild(QGroupBox, "affineBox")
        self.pointGroupBox = settingsWidget.findChild(QGroupBox, "groupBox")
        self.maskLabel = settingsWidget.findChild(QLabel, "label")

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
        # connect item click and selection change to draw points on the mask image
        self.definedPoints.itemClicked.connect(self._list_item_clicked_action)
        self.definedPoints.itemSelectionChanged.connect(self._refresh_left_points_display)

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
        point_to_store = point

        if self.centerCheckbox.isChecked() and self.affine.internal_mask is not None:
            try:
                mask_shape = self.affine.internal_mask.shape
                max_y = mask_shape[0] - 1
                max_x = mask_shape[1] - 1
                x = int(round(point.x()))
                y = int(round(point.y()))

                if 0 <= x <= max_x and 0 <= y <= max_y:
                    centered_x, centered_y = self.affine.center_on_component(x, y)
                    point_to_store = QPointF(float(centered_x), float(centered_y))
            except Exception as e:
                self.logger.log_warn(f"Affine: could not center click on component: {str(e)}")

        self.temp_points.append(point_to_store)
        # live-render points while inputting
        self._refresh_left_points_display()
        # required num points reached
        if len(self.temp_points) == self.pointCount.value():
            # add points to list widget
            name = self.pointName.text() if self.pointName.text() != "" else f"Point set {self.definedPoints.count() + 1}"
            self.update_list_widget(self.temp_points, name)
            self.temp_points = []
            # refresh display to show only selected sets (no temp points)
            # self._refresh_left_points_display()

    @pyqtSlot(QPointF)
    def _on_image_point_clicked(self, point: QPointF):
        print(f"Image point clicked: {point}")

    def _gui_change_mask_uploaded(self, mask_loaded):
        if self.affineBox is not None:
            self.affineBox.setEnabled(mask_loaded)
        if self.pointGroupBox is not None:
            self.pointGroupBox.setEnabled(mask_loaded)

    def _list_widget_context_menu(self, pos):
        def delete_selected():
            rows = sorted([self.definedPoints.row(it) for it in self.definedPoints.selectedItems()], reverse=True)
            for r in rows:
                self.definedPoints.takeItem(r)

        def rename_first_selected():
            items = self.definedPoints.selectedItems()
            if not items:
                return
            items[0].setText("New name")

        if self.definedPoints.itemAt(pos) is None and not self.definedPoints.selectedItems():
            return

        menu = QMenu()
        delete_action = QAction("Delete Selected", self.definedPoints)
        rename_action = QAction("Rename First Selected", self.definedPoints)

        delete_action.triggered.connect(delete_selected)
        rename_action.triggered.connect(rename_first_selected)

        menu.addAction(delete_action)
        menu.addAction(rename_action)
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
            points, names = self.positioning_measurement_points()
            with open(fileName, "w", newline="") as csvfile:
                cswriter = csv.writer(csvfile, delimiter=",")
                fields = ["Name", "x_mask", "y_mask", "x_img", "y_img"]
                cswriter.writerow(fields)
                for name, point_set in zip(names, points):
                    for x_mask, y_mask in point_set:
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
                next(csreader, None)  # skip header if present
                for row in csreader:
                    if not row or len(row) < 3:
                        continue
                    # extract the name and coordinates
                    name = row[0]
                    try:
                        x_mask = float(row[1])
                        y_mask = float(row[2])
                    except ValueError:
                        continue
                    # store as QPointF for consistent rendering
                    point_dict.setdefault(name, []).append(QPointF(x_mask, y_mask))
            for name, points in point_dict.items():
                self.update_list_widget(points, name)

    def _list_item_clicked_action(self, item):
        # Redraw based on current selection whenever an item is clicked
        self._refresh_left_points_display()

    def _normalize_points(self, points_list):
        """Ensure a list of points is List[QPointF]."""
        norm = []
        if not points_list:
            return norm
        for pt in points_list:
            if isinstance(pt, QPointF):
                norm.append(pt)
            else:
                try:
                    x, y = float(pt[0]), float(pt[1])
                    norm.append(QPointF(x, y))
                except Exception:
                    continue
        return norm

    def _refresh_left_points_display(self):
        """Draw selected measurement sets on the left view; include temp points if any."""
        selected_items = self.definedPoints.selectedItems()
        point_sets: list[list[QPointF]] = []
        for sel_item in selected_items:
            pts = self._normalize_points(sel_item.data(self.COORD_DATA))
            if pts:
                point_sets.append(pts)
        # show live input points as an extra set if present
        if len(self.temp_points) > 0:
            point_sets.append(self._normalize_points(self.temp_points))
        # draw or clear if nothing selected and no temp points
        if point_sets:
            self.MDIWidget.draw_points_on_left(point_sets)
        else:
            # clear any previously drawn points by drawing empty sets
            self.MDIWidget.draw_points_on_left([])

    def _mask_button_action(self):
        """Interface for the gds mask loading button."""
        try:
            fileName, _ = QtWidgets.QFileDialog.getOpenFileName(
                self.settingsWidget,
                "Open .GDS, .png or .jpg file",
                self.path + os.sep + "masks",
                "Mask Files or Images(*.gds *.png *.jpg);;All Files (*)",
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
                if self.maskLabel is not None:
                    self.maskLabel.setText(f"Mask loaded: {os.path.basename(fileName)}")
                self._gui_change_mask_uploaded(mask_loaded=True)
                self.mask = mask  # keep internal reference to the mask ndarray for passing to dialog
        except AffineError as e:
            self.logger.log_error(e.message)

    def _open_dialog(self):
        """Opens the matching dialog for aff transformation."""

        def _on_close():
            if self.dialog is None:
                raise RuntimeError("Dialog is not initialized.")
            res = self.affine.result.get("matches", None)
            if res is not None and len(res) > 0:
                self.logger.log_info(f"Affine: Transformation confirmed. {len(res)} matches found.")
            else:
                self.logger.log_info("Affine: No transformation confirmed")
            self.dialog = None

        selected_camera = self.cameraComboBox.currentText()
        cameras = self.function_dict.get("camera", {})
        if selected_camera not in cameras:
            self.logger.log_error("Affine: No camera plugin selected or available.", include_trace=False)
            return

        img = cameras[selected_camera]["camera_capture_image"]()
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
        else:
            # convert any QPointF to plain (x, y) tuples for dialog compatibility
            tmp = []
            for pt in pointslist:
                if isinstance(pt, QPointF):
                    tmp.append((pt.x(), pt.y()))
                else:
                    try:
                        tmp.append((float(pt[0]), float(pt[1])))
                    except Exception:
                        continue
            pointslist = tmp
        status, settings = self.parse_settings_widget()
        if status == 0:
            # Pass the settings dict to the dialog
            self.dialog = dialog(self.affine, img[1], self.mask, settings, pointslist=pointslist, logger=self.logger)
            self.dialog.finished.connect(_on_close)
            self.dialog.show()
        else:
            self.logger.log_warn(f"Affine: Error parsing settings widget: {settings['Error message']} {settings['exception']}")

    def update_list_widget(self, points: list[QPointF], name: str):
        """
        Updates the list widget with the given points and name.
        If clear_list is True, clears the list before adding the new points.
        """
        item = QtWidgets.QListWidgetItem(name)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        # normalize to QPointF for consistent rendering/storage
        item.setData(self.COORD_DATA, self._normalize_points(points))
        self.definedPoints.addItem(item)

    # hook implementations

    def _getLogSignal(self):
        return self.logger.logger_signal

    def _getInfoSignal(self):
        return self.logger.info_popup_signal

    def _getCloseLockSignal(self):
        return self.closelock.closeLock

    def _fetch_dependency_functions(self, function_dict):
        """Set dependency methods from plugin manager and return missing dependency methods."""
        _is_valid, missing = self.dm.set_available_dependency_functions(function_dict)
        return missing

    def _get_public_methods(self, function: str) -> dict:
        """
        Returns a nested dictionary of public methods for the plugin
        """
        return get_public_methods(self)

    @pyqtSlot()
    def _gui_update(self):
        """Emits a signal to update the GUI."""
        self.pointCount.setValue(int(self.settings["pointcount"]))
        self.centerCheckbox.setChecked(ini_to_bool(self.settings["centerclicks"]))

    @pyqtSlot()
    def set_gui_from_settings(self):
        """Sets gui elemenets from internal dict"""
        self.gui_update_signal.emit()

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
                raw_points = item.data(self.COORD_DATA) or []  # of type qpointF
                tuple_points = [(point.x(), point.y()) for point in raw_points]
                points.append(tuple_points)
                names.append(item.text())
        return points, names

    @public
    def parse_settings_widget(self):
        """Parse settings widget, return dict"""
        ts = {}  # temp settings
        ts["pointcount"] = self.pointCount.value()
        ts["centerclicks"] = self.centerCheckbox.isChecked()

        status, ts = self.dm.parse_dependencies(ts)
        if status != 0:
            return status, ts

        internal_settings = self.affine.get_settings()

        # update to ts
        ts.update(internal_settings)

        # all tests pass, write to internal settings
        self.settings.update(ts)

        return 0, ts

    @public
    def setSettings(self, settings: dict):
        """Sets the plugin settings from a dictionary.

        Args:
            settings (dict): A dictionary containing plugin settings.
        """
        self.settings = settings
        self.affine.update_settings(settings)  # send settings to affine core
        self.dm.set_dependency_settings(settings)  # set settings to selected deps through dm
        self.set_gui_from_settings()
