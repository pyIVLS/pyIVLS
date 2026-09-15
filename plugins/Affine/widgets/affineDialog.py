"""Registration dialog for affine plugin"""

import time

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qtagg import (
    FigureCanvasQTAgg as FigureCanvas,
)
from plugin_components import LoggingHelper, ini_to_bool
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QBrush, QColor, QImage, QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QLineEdit,
    QSpinBox,
)
from worker_thread import WorkerThread

from plugins.Affine.Affine_skimage import AffineError
from plugins.Affine.widgets.affineMatchDialog import Ui_Dialog


class dialog(QDialog, Ui_Dialog):
    """
    Affine registration dialog for manual and automatic matching.
    Handles preprocessing settings, manual point selection, and result visualization.
    """

    info_msg = Signal(str)

    def __init__(self, affine, img, mask, settings, pointslist=None, logger: LoggingHelper | None = None):
        """
        Initialize the dialog.
        Args:
            affine: Affine object for registration.
            img: Input image (numpy array).
            mask: Mask image (numpy array).
            settings: Settings dictionary for preprocessing and matching.
            pointslist: Optional list of points on the mask that represent the targets.
        """
        super().__init__(None, Qt.WindowType.WindowMaximizeButtonHint | Qt.WindowType.WindowCloseButtonHint)
        self.setupUi(self)
        self.info_msg.connect(self.show_message)  # TODO: this is in fact completely BORKED, no messages are getting through.

        # good sigmas:
        self.sigma_list = [1.0, 2.0, 3.0, 4.0, 5.0]
        # morphological operation types
        self.morphology_types = ["erosion", "dilation", "opening", "closing"]
        self.affine = affine
        self.pointslist = pointslist
        self.img = img
        self.mask = mask
        self.manual_mode = False
        self.expecting_img_click = False
        self.mask_points = []
        self.img_points = []
        self.num_needed = 2
        self.img_scene = QGraphicsScene()
        self.mask_scene = QGraphicsScene()

        self.logger = logger
        self.worker_thread = None  # Initialize worker thread reference

        # Connect mouse events for manual mode
        self.imgView.mousePressEvent = self._img_view_clicked
        self.maskView.mousePressEvent = self._mask_view_clicked
        self.matchButton.clicked.connect(self._on_match_button_clicked)
        self.manualButton.clicked.connect(self._on_manual_button_clicked)
        # Fill comboboxes
        for sigma in self.sigma_list:
            self.sigmaImage.addItem(str(sigma))
            self.sigmaMask.addItem(str(sigma))

        # Fill morphology type comboboxes
        for morph_type in self.morphology_types:
            self.morphologyTypeMask.addItem(morph_type)
            self.morphologyTypeImage.addItem(morph_type)

        # Fill backend combobox
        backends = ["SIFT", "ORB"]
        for backend in backends:
            self.backendCombo.addItem(backend)

        # Set initial values from settings
        self.blurMask.setChecked(ini_to_bool(settings["blurmask"]))
        self.invertMask.setChecked(ini_to_bool(settings["invertmask"]))
        self.equalizeMask.setChecked(ini_to_bool(settings["equalizemask"]))
        self.cannyMask.setChecked(ini_to_bool(settings["cannymask"]))
        self.blurImage.setChecked(ini_to_bool(settings["blurimage"]))
        self.invertImage.setChecked(ini_to_bool(settings["invertimage"]))
        self.equalizeImage.setChecked(ini_to_bool(settings["equalizeimage"]))
        self.cannyImage.setChecked(ini_to_bool(settings["cannyimage"]))
        self.otsuMask.setChecked(ini_to_bool(settings["otsumask"]))
        self.otsuImage.setChecked(ini_to_bool(settings["otsuimage"]))
        self.manualThresholdMask.setChecked(ini_to_bool(settings["manualthresholdmask"]))
        self.manualThresholdImage.setChecked(ini_to_bool(settings["manualthresholdimage"]))
        self.morphologyMask.setChecked(ini_to_bool(settings["morphologymask"]))
        self.morphologyImage.setChecked(ini_to_bool(settings["morphologyimage"]))
        self.sigmaImage.setCurrentText(str(settings["sigmaimage"]))
        self.sigmaMask.setCurrentText(str(settings["sigmamask"]))
        self.thresholdImage.setValue(int(settings["thresholdimage"]))
        self.thresholdMask.setValue(int(settings["thresholdmask"]))
        self.morphologyTypeMask.setCurrentText(settings["morphologytypemask"])
        self.morphologyTypeImage.setCurrentText(settings["morphologytypeimage"])
        self.morphologyStrengthMask.setValue(int(settings["morphologystrengthmask"]))
        self.morphologyStrengthImage.setValue(int(settings["morphologystrengthimage"]))
        self.crossCheck.setChecked(ini_to_bool(settings["crosscheck"]))
        self.ratioTestSpinBox.setValue(float(settings["ratiotest"]))
        self.residualTestSpinBox.setValue(int(settings["residualthreshold"]))
        self.backendCombo.setCurrentText(settings["backend"])
        self.scalingSpinBox.setValue(float(settings["scalingfactor"]))

        # Set up conditional enabling connections
        self.manualThresholdMask.stateChanged.connect(self._update_threshold_mask_state)
        self.manualThresholdImage.stateChanged.connect(self._update_threshold_image_state)
        self.morphologyMask.stateChanged.connect(self._update_morphology_mask_state)
        self.morphologyImage.stateChanged.connect(self._update_morphology_image_state)
        self.blurMask.stateChanged.connect(self._update_sigma_mask_state)
        self.cannyMask.stateChanged.connect(self._update_sigma_mask_state)
        self.blurImage.stateChanged.connect(self._update_sigma_image_state)
        self.cannyImage.stateChanged.connect(self._update_sigma_image_state)

        # Update initial states
        self._update_threshold_mask_state()
        self._update_threshold_image_state()
        self._update_morphology_mask_state()
        self._update_morphology_image_state()
        self._update_sigma_mask_state()
        self._update_sigma_image_state()

        if self.affine.A is not None:
            result = self.affine.result
            self.draw_result(result, self.pointslist)
            self.info_message("Showing saved result")

        # Connect UI elements to settings change handler at the end to prevent unncessary signaling during setup
        for child in self.groupBox.children():
            if isinstance(child, QCheckBox):
                child.stateChanged.connect(self._preprocessing_settings_changed)
            elif isinstance(child, QComboBox):
                child.currentTextChanged.connect(self._preprocessing_settings_changed)
            elif isinstance(child, QSpinBox):
                child.valueChanged.connect(self._preprocessing_settings_changed)
            elif isinstance(child, QLineEdit):
                child.textChanged.connect(self._preprocessing_settings_changed)

        # Connect backend combobox to settings change handler
        for child in self.groupBox_2.children():
            if isinstance(child, QComboBox):
                child.currentTextChanged.connect(self._preprocessing_settings_changed)

        # draw initial images
        self._preprocessing_settings_changed()

    def _preprocessing_settings_changed(self):
        """
        Called when preprocessing settings are changed. Updates local settings and refreshes the displayed images.
        """
        settings = {}
        blurMask = self.blurMask.isChecked()
        invertMask = self.invertMask.isChecked()
        equalizeMask = self.equalizeMask.isChecked()
        cannyMask = self.cannyMask.isChecked()
        blurImage = self.blurImage.isChecked()
        invertImage = self.invertImage.isChecked()
        equalizeImage = self.equalizeImage.isChecked()
        cannyImage = self.cannyImage.isChecked()
        otsuMask = self.otsuMask.isChecked()
        otsuImage = self.otsuImage.isChecked()
        manualThresholdMask = self.manualThresholdMask.isChecked()
        manualThresholdImage = self.manualThresholdImage.isChecked()
        morphologyMask = self.morphologyMask.isChecked()
        morphologyImage = self.morphologyImage.isChecked()
        crossCheck = self.crossCheck.isChecked()
        try:
            sigmaImage = float(self.sigmaImage.currentText())
        except ValueError:
            sigmaImage = 1.0
        try:
            sigmaMask = float(self.sigmaMask.currentText())
        except ValueError:
            sigmaMask = 1.0
        thresholdImage = self.thresholdImage.value()
        thresholdMask = self.thresholdMask.value()
        # Get morphology settings
        morphologyTypeMask = self.morphologyTypeMask.currentText()
        morphologyTypeImage = self.morphologyTypeImage.currentText()
        morphologyStrengthMask = self.morphologyStrengthMask.value()
        morphologyStrengthImage = self.morphologyStrengthImage.value()
        settings["ratiotest"] = self.ratioTestSpinBox.value()
        settings["residualthreshold"] = self.residualTestSpinBox.value()
        settings["scalingfactor"] = self.scalingSpinBox.value()

        # Get backend setting
        settings["backend"] = self.backendCombo.currentText()

        settings["blurmask"] = blurMask
        settings["invertmask"] = invertMask
        settings["equalizemask"] = equalizeMask
        settings["cannymask"] = cannyMask
        settings["otsumask"] = otsuMask
        settings["manualthresholdmask"] = manualThresholdMask
        settings["thresholdmask"] = thresholdMask
        settings["morphologymask"] = morphologyMask
        settings["morphologytypemask"] = morphologyTypeMask
        settings["morphologystrengthmask"] = morphologyStrengthMask
        settings["blurimage"] = blurImage
        settings["invertimage"] = invertImage
        settings["equalizeimage"] = equalizeImage
        settings["cannyimage"] = cannyImage
        settings["otsuimage"] = otsuImage
        settings["manualthresholdimage"] = manualThresholdImage
        settings["thresholdimage"] = thresholdImage
        settings["morphologyimage"] = morphologyImage
        settings["morphologytypeimage"] = morphologyTypeImage
        settings["morphologystrengthimage"] = morphologyStrengthImage
        settings["sigmaimage"] = sigmaImage
        settings["sigmamask"] = sigmaMask
        settings["crosscheck"] = crossCheck
        self.affine.update_settings(settings)
        img = self.affine.preprocessor.preprocess_img(self.img)
        mask = self.affine.preprocessor.preprocess_mask(self.mask)
        self.update_images(img, mask)

    def _update_threshold_mask_state(self):
        """Enable/disable threshold mask spinbox based on checkbox state."""
        self.thresholdMask.setEnabled(self.manualThresholdMask.isChecked())

    def _update_threshold_image_state(self):
        """Enable/disable threshold image spinbox based on checkbox state."""
        self.thresholdImage.setEnabled(self.manualThresholdImage.isChecked())

    def _update_morphology_mask_state(self):
        """Enable/disable morphology mask controls based on checkbox state."""
        enabled = self.morphologyMask.isChecked()
        self.morphologyTypeMask.setEnabled(enabled)
        self.morphologyStrengthMask.setEnabled(enabled)

    def _update_morphology_image_state(self):
        """Enable/disable morphology image controls based on checkbox state."""
        enabled = self.morphologyImage.isChecked()
        self.morphologyTypeImage.setEnabled(enabled)
        self.morphologyStrengthImage.setEnabled(enabled)

    def _update_sigma_mask_state(self):
        """Enable/disable sigma mask combobox based on blur or edge detect checkbox state."""
        self.sigmaMask.setEnabled(self.blurMask.isChecked() or self.cannyMask.isChecked())

    def _update_sigma_image_state(self):
        """Enable/disable sigma image combobox based on blur or edge detect checkbox state."""
        self.sigmaImage.setEnabled(self.blurImage.isChecked() or self.cannyImage.isChecked())

    @staticmethod
    def to_pixmap(image):
        """
        Convert a numpy image array to a QPixmap for display.
        Args:
            image (np.ndarray): Image array (2D grayscale or 3D RGB/RGBA).
        Returns:
            QPixmap or None: Pixmap for display, or None if input is None.
        Raises:
            ValueError: If the image format is unsupported.
        """
        if image is None:
            return None
        if len(image.shape) == 2:
            height, width = image.shape
            bytes_per_line = width
            qimage = QImage(
                image.data,
                width,
                height,
                bytes_per_line,
                QImage.Format.Format_Grayscale8,
            )
        elif len(image.shape) == 3 and image.shape[2] == 3:
            height, width, _ = image.shape
            bytes_per_line = width * 3
            qimage = QImage(image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        elif len(image.shape) == 3 and image.shape[2] == 4:
            height, width, _ = image.shape
            bytes_per_line = width * 4
            qimage = QImage(image.data, width, height, bytes_per_line, QImage.Format.Format_RGBA8888)
        else:
            raise ValueError("Unsupported image format")
        return QPixmap.fromImage(qimage)

    def update_images(self, img, mask):
        """
        Update the QGraphicsView widgets with the given images.
        Args:
            img (np.ndarray): The image to display.
            mask (np.ndarray): The mask to display.
        """
        imgview = self.imgView
        maskview = self.maskView
        # Ensure imgview has a valid scene
        if imgview.scene() is None:
            imgview.setScene(QGraphicsScene())
        img_scene = imgview.scene()
        if maskview.scene() is None:
            maskview.setScene(QGraphicsScene())
        mask_scene = maskview.scene()
        # catch None cases, should not happen but the linter complains
        assert img_scene is not None, "Image scene is None"
        assert mask_scene is not None, "Mask scene is None"
        img_scene.clear()
        mask_scene.clear()
        if img is not None:
            img_pixmap = self.to_pixmap(img)
            if img_pixmap is not None and img_scene is not None:
                img_scene.addItem(QGraphicsPixmapItem(img_pixmap))
        if mask is not None:
            mask_pixmap = self.to_pixmap(mask)
            if mask_pixmap is not None and mask_scene is not None:
                mask_scene.addItem(QGraphicsPixmapItem(mask_pixmap))

    def info_message(self, msg: str) -> None:
        self.info_msg.emit(msg)

    @Slot(str)
    def show_message(self, str):
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        self.statusText.setText(f"{timestamp}: {str}")

    def draw_result(
        self,
        result,
        pointslist=None,
        show_points=True,
        draw_matches=True,
    ):
        """
        Draws the result of matching or manual transformation in the resultView.
        Args:
            result (dict): Result dictionary from Affine.
            pointslist (list, optional): List of points on the mask that represent the targets.
            show_points (bool): Whether to show points.
            draw_matches (bool): Whether to draw matches.
        """
        try:
            kp1 = result["kp1"]
            kp2 = result["kp2"]
            matches = result["matches"]
            mask_img = result["mask"]
            img_img = result["img"]
            h1, w1 = mask_img.shape[:2]
            h2, w2 = img_img.shape[:2]
            out_img = np.zeros((max(h1, h2), w1 + w2, 3), dtype=np.uint8)
            out_img[:h1, :w1] = mask_img if mask_img.ndim == 3 else np.stack([mask_img] * 3, axis=-1)
            out_img[:h2, w1 : w1 + w2] = img_img if img_img.ndim == 3 else np.stack([img_img] * 3, axis=-1)
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(out_img)
            # Draw matches
            if draw_matches:
                # Get indices of matched keypoints
                matched_indices_1 = set()
                matched_indices_2 = set()

                # draw the matches with points and lines connecting them
                for m in matches:
                    idx1, idx2 = m
                    matched_indices_1.add(idx1)
                    matched_indices_2.add(idx2)
                    y1, x1 = kp1[idx1]
                    y2, x2 = kp2[idx2]
                    ax.plot([x1, x2 + w1], [y1, y2], "r-", linewidth=0.5)
                    ax.plot(x1, y1, "bo", markersize=2)
                    ax.plot(x2 + w1, y2, "go", markersize=2)

                # Draw unmatched keypoints in mask (left side)
                for idx, (y, x) in enumerate(kp1):
                    if idx not in matched_indices_1:
                        ax.plot(x, y, "co", markersize=1.5, alpha=0.6)  # cyan circles for unmatched mask keypoints

                # Draw unmatched keypoints in image (right side)
                for idx, (y, x) in enumerate(kp2):
                    if idx not in matched_indices_2:
                        ax.plot(x + w1, y, "mo", markersize=1.5, alpha=0.6)  # magenta circles for unmatched image keypoints
            # Draw defined points
            if show_points and pointslist is not None:
                for pt in pointslist:
                    # draw on mask
                    x_mask, y_mask = pt
                    ax.plot(
                        x_mask,
                        y_mask,
                        "mo",
                        markersize=6,
                        markeredgewidth=2,
                        markeredgecolor="k",
                    )
                    # convert the mask points to image coords and draw
                    x_img, y_img = self.affine.coords((x_mask, y_mask))
                    ax.plot(
                        x_img + w1,
                        y_img,
                        "co",
                        markersize=6,
                        markeredgewidth=2,
                        markeredgecolor="k",
                    )
            ax.axis("off")
            plt.tight_layout()
            # Overlay transformed mask outline on the image if affine matrix exists
            if hasattr(self.affine, "A") and self.affine.A is not None:
                h_mask, w_mask = mask_img.shape[:2]
                corners = np.array(
                    [[0, 0], [w_mask, 0], [w_mask, h_mask], [0, h_mask]],
                    dtype=np.float32,
                )
                transformed = np.array([self.affine.coords((x, y)) for x, y in corners])
                for i in range(4):
                    x0, y0 = transformed[i % 4]
                    x1_, y1_ = transformed[(i + 1) % 4]
                    ax.plot([x0 + w1, x1_ + w1], [y0, y1_], "y-", linewidth=1)
            canvas = FigureCanvas(fig)
            scene = self.resultView.scene()
            if scene is not None:
                scene.clear()
            else:
                scene = QGraphicsScene()
                self.resultView.setScene(scene)
            canvas.draw()
            width, height = canvas.get_width_height()
            img_buf = canvas.buffer_rgba()
            qimg = QImage(img_buf, width, height, QImage.Format.Format_RGBA8888)
            pixmap = QPixmap.fromImage(qimg)
            scene.addItem(QGraphicsPixmapItem(pixmap))
            plt.close(fig)
        except KeyError as e:
            self.info_message(f"KeyError during result drawing: {e}")

    def _on_match_button_clicked(self):
        """
        Handle match button click event. Runs automatic matching and displays the result.
        """

        def _run_matching(worker_thread):
            """
            Perform the actual matching work. This runs in a separate thread.
            """

            img = self.img
            self.affine.try_match(img)
            result = self.affine.result

            # Emit progress with result data
            worker_thread.progress.emit({"result": result, "pointslist": self.pointslist})

            return result

        def _on_matching_progress(data):
            """Handle progress updates from the worker thread."""
            result = data["result"]
            pointslist = data["pointslist"]

            # Print keypoint statistics
            kp1_count = len(result["kp1"])
            kp2_count = len(result["kp2"])
            matches_count = len(result["matches"])
            message = f"Keypoints found - Mask: {kp1_count}, Image: {kp2_count}\n"
            message += f"Matching successful, found {matches_count} matches out of {min(kp1_count, kp2_count)} possible"
            self.info_message(message)
            self.draw_result(result, pointslist)

        def _on_matching_finished():
            """Handle completion of the matching process."""
            self.matchButton.setEnabled(True)
            self.manualButton.setEnabled(True)

        def _on_matching_error(error_message):
            """Handle errors from the matching process."""
            self.info_message(f"Exception during matching: {error_message}")
            # Re-enable the match button if it was disabled
            self.matchButton.setEnabled(True)
            self.manualButton.setEnabled(True)

        self.info_message("Starting automatic matching...")
        self._preprocessing_settings_changed()

        # Disable the match button to prevent multiple simultaneous operations
        self.matchButton.setEnabled(False)
        self.manualButton.setEnabled(False)

        # Create and configure the worker thread
        self.worker_thread = WorkerThread(task=_run_matching)
        self.worker_thread.progress.connect(_on_matching_progress)
        self.worker_thread.finished.connect(_on_matching_finished)
        self.worker_thread.error.connect(_on_matching_error)

        # Start the worker thread
        self.worker_thread.start()

    def _on_manual_button_clicked(self):
        """
        Enable manual mode for point selection and transformation.
        """
        self.manual_mode = True
        self.expecting_img_click = False
        self.mask_points = []
        self.img_points = []
        self._draw_manual_points()
        self.info_message(f"Manual mode enabled. Click {self.num_needed} points on the mask (left), then {self.num_needed} on the image (right). Colors indicate matching order.")
        self.groupBox.setEnabled(False)  # disable preprocessing settings during manual mode
        self.groupBox_2.setEnabled(False)  # disable backend selection during manual mode

    def _draw_manual_points(self):
        """
        Draw points on mask and image views for visual feedback during manual mode.
        """
        maskview = self.maskView
        imgview = self.imgView
        # Ensure scenes exist
        if maskview.scene() is None:
            maskview.setScene(QGraphicsScene())
        mask_scene = maskview.scene()
        if imgview.scene() is None:
            imgview.setScene(QGraphicsScene())
        img_scene = imgview.scene()
        colors = ["red", "green", "blue", "orange", "purple", "cyan"]
        if mask_scene is not None:
            mask_scene.clear()
            mask_pixmap = self.to_pixmap(self.mask)
            if mask_pixmap is not None:
                mask_scene.addItem(QGraphicsPixmapItem(mask_pixmap))
            for i, (x, y) in enumerate(self.mask_points):
                color = colors[i % len(colors)]
                ellipse = mask_scene.addEllipse(x - 4, y - 4, 8, 8)
                if ellipse is not None:
                    ellipse.setBrush(QBrush(QColor(color)))
        if img_scene is not None:
            img_scene.clear()
            img_pixmap = self.to_pixmap(self.img)
            if img_pixmap is not None:
                img_scene.addItem(QGraphicsPixmapItem(img_pixmap))
            for i, (x, y) in enumerate(self.img_points):
                color = colors[i % len(colors)]
                ellipse = img_scene.addEllipse(x - 4, y - 4, 8, 8)
                if ellipse is not None:
                    ellipse.setBrush(QBrush(QColor(color)))

    def _mask_view_clicked(self, event):
        """
        Handle mouse click on the mask view for manual point selection.
        """
        if not self.manual_mode or self.expecting_img_click:
            return
        pos = event.position().toPoint() if hasattr(event, "position") else event.pos()
        scene_pos = self.maskView.mapToScene(pos)
        x, y = scene_pos.x(), scene_pos.y()
        if len(self.mask_points) < self.num_needed:
            self.mask_points.append((x, y))
            maskview = self.maskView
            if maskview.scene() is None:
                maskview.setScene(QGraphicsScene())
            mask_scene = maskview.scene()
            colors = ["red", "green", "blue", "orange", "purple", "cyan"]
            color = colors[(len(self.mask_points) - 1) % 6]
            if mask_scene is not None:
                ellipse = mask_scene.addEllipse(x - 4, y - 4, 8, 8)
                if ellipse is not None:
                    ellipse.setBrush(QBrush(QColor(color)))
            if len(self.mask_points) == self.num_needed:
                self.expecting_img_click = True
        else:
            self.info_message("All mask points selected. Now select points on the image.")

    def _img_view_clicked(self, event):
        """
        Handle mouse click on the image view for manual point selection.
        """
        if not self.manual_mode or not self.expecting_img_click:
            return
        pos = event.position().toPoint() if hasattr(event, "position") else event.pos()
        scene_pos = self.imgView.mapToScene(pos)
        x, y = scene_pos.x(), scene_pos.y()
        if len(self.img_points) < self.num_needed:
            self.img_points.append((x, y))
            imgview = self.imgView
            if imgview.scene() is None:
                imgview.setScene(QGraphicsScene())
            img_scene = imgview.scene()
            colors = ["red", "green", "blue", "orange", "purple", "cyan"]
            color = colors[(len(self.img_points) - 1) % 6]
            if img_scene is not None:
                ellipse = img_scene.addEllipse(x - 4, y - 4, 8, 8)
                if ellipse is not None:
                    ellipse.setBrush(QBrush(QColor(color)))
            if len(self.img_points) == self.num_needed:
                try:
                    self.affine.manual_transform(self.mask_points, self.img_points, self.img, self.mask)
                    self.draw_result(
                        self.affine.result,
                        self.pointslist,
                        draw_matches=True,
                    )
                except AffineError as e:
                    self.info_message(f"Manual transformation failed: {e}")
                    self.groupBox.setEnabled(True)  # manual mode over, re-enable preprocessing settings
                    self.groupBox_2.setEnabled(True)  # manual mode over, re-enable backend selection
                self.manual_mode = False
                self.mask_points = []
                self.img_points = []
                self._draw_manual_points()
        else:
            self.info_message("All image points selected. If you want to retry, re-enter manual mode.")
            self.groupBox.setEnabled(True)  # manual mode over, re-enable preprocessing settings
            self.groupBox_2.setEnabled(True)  # manual mode over, re-enable backend selection
