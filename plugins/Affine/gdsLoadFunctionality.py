from gdsLoadDialog import Ui_Dialog
from PyQt6.QtCore import Qt, QObject, pyqtSignal, pyqtSlot, QEvent, QRect, QRectF
from PyQt6.QtWidgets import QDialog, QPushButton
from PyQt6.QtGui import QPixmap, QImage, QMouseEvent
from PyQt6.QtWidgets import QGraphicsScene, QRubberBand
from klayout import lay
import os
import cv2 as cv
import numpy as np
from matplotlib import cm as mpl_cm


class wrapperSettings:
    def __init__(self):
        pass


class gdsWrapper(QObject):
    # signal to update the graphics view
    layout_updated = pyqtSignal(np.ndarray)

    def __init__(self, path):
        super().__init__()
        self.path = path
        filename = os.path.basename(path)
        filename, extension = filename.split(".")
        assert extension.lower() == "gds", "Input file must be a GDS file."
        self.view = lay.LayoutView(options=lay.LayoutView.LV_NoGrid)
        self.view.load_layout(path, add_cellview=False)
        self.view.selection_size()
        self.view.zoom_fit()
        self.view.max_hier()
        self.h = self.view.viewport_height()
        self.w = self.view.viewport_width()
        aspect_ratio = self.w / self.h
        # scale the image to have the same aspect ratio and height 1080
        if aspect_ratio > 1:
            self.w = 1920
            self.h = int(1920 / aspect_ratio)
        else:
            self.h = 1080
            self.w = int(1080 * aspect_ratio)

        # Track default colors for restoring when color-scheme disabled
        self._default_colors: list[tuple[int, int]] = []  # (frame_color, fill_color)

        num_layers = 0
        it = self.view.begin_layers()
        # set layers visible and record defaults
        while not it.at_end():
            lp = it.current()
            try:
                # Capture defaults before modification
                frame_c = int(lp.frame_color)
                fill_c = int(lp.fill_color)
            except Exception:
                frame_c = 0xFFFFFF
                fill_c = 0xFFFFFF
            self._default_colors.append((frame_c, fill_c))

            new_layer = lp.dup()
            new_layer.visible = True
            new_layer.clear_dither_pattern()
            self.view.set_layer_properties(it, new_layer)
            it.next()
            num_layers += 1

        self.num_layers = num_layers
        self.view.set_config("grid-show-ruler", "false")
        self.view.commit_config()
        self.view.set_config("background-color", "#00000000")
        self.view.set_config("grid-visible", "false")

        # initialize array to keep track of visible layers
        self.visible_layers = [True] * self.num_layers
        # color scheme state
        self._color_scheme_enabled: bool = False
        self._layer_colors: list[int] | None = None

    def new_image(self):
        # render the image based on visible layers
        it = self.view.begin_layers()
        layer_index = 0
        while not it.at_end():
            lp = it.current()
            new_layer = lp.dup()
            new_layer.visible = self.visible_layers[layer_index]
            new_layer.clear_dither_pattern()
            # apply distinct colors if enabled, else restore defaults
            if self._color_scheme_enabled and self._layer_colors is not None:
                try:
                    color_int = int(self._layer_colors[layer_index])
                    new_layer.frame_color = color_int
                    new_layer.fill_color = color_int
                except Exception:
                    pass
            else:
                # restore default colors
                try:
                    frame_c, fill_c = self._default_colors[layer_index]
                    new_layer.frame_color = frame_c
                    new_layer.fill_color = fill_c
                except Exception:
                    pass
            self.view.set_layer_properties(it, new_layer)
            it.next()
            layer_index += 1

        # generate image
        output_image_path = os.path.join(os.path.dirname(self.path), "temp_render.png")
        self.view.save_image(output_image_path, width=self.w, height=self.h)
        image = cv.imread(output_image_path)
        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        os.remove(output_image_path)
        return image

    def set_layer_visible(self, layer_index, visible):
        if 0 <= layer_index < self.num_layers:
            self.visible_layers[layer_index] = visible

    def is_layer_visible(self, layer_index):
        if 0 <= layer_index < self.num_layers:
            return self.visible_layers[layer_index]
        return False

    def _generate_distinct_colors(self) -> list[int]:
        """Generate visually distinct RGB colors (0xRRGGBB integers) for layers."""
        cmap = mpl_cm.get_cmap("tab20", max(self.num_layers, 1))
        colors: list[int] = []
        for i in range(self.num_layers):
            r, g, b, _ = cmap(i)
            ri, gi, bi = int(r * 255), int(g * 255), int(b * 255)
            colors.append((ri << 16) | (gi << 8) | bi)
        return colors

    def set_color_scheme(self, enable: bool):
        """Enable or disable distinct per-layer coloring and trigger re-render."""
        if enable and not self._color_scheme_enabled:
            self._layer_colors = self._generate_distinct_colors()
            self._color_scheme_enabled = True
        elif not enable and self._color_scheme_enabled:
            self._color_scheme_enabled = False
            self._layer_colors = None
        # Re-render with current settings
        self.emit_new_image()

    @pyqtSlot()
    def emit_new_image(self):
        image = self.new_image()
        self.layout_updated.emit(image)


class gdsLoadDialog(QDialog):
    request_new_image = pyqtSignal()

    def __init__(self, path):
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
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.scene = QGraphicsScene()
        self.ui.graphicsView.setScene(self.scene)
        # Rubber-band selection for manual cropping
        self._rubber_band = QRubberBand(QRubberBand.Shape.Rectangle, self.ui.graphicsView.viewport())
        self._rb_origin = None
        self._img = None  # keep latest rendered/cropped image
        self._crop_px = None  # persistent crop rectangle in pixel coords: (x1, y1, x2, y2)
        # Install event filter to capture mouse events on the viewport for cropping
        if self.ui.graphicsView and hasattr(self.ui.graphicsView, "viewport"):
            vp = self.ui.graphicsView.viewport()
            if vp is not None:
                vp.installEventFilter(self)

        self.path = path
        self.wrapper = gdsWrapper(path)
        self.wrapper.layout_updated.connect(self.update_graphics_view)
        self.request_new_image.connect(self.wrapper.emit_new_image)
        self.request_new_image.emit()

        # fill combobox
        for layer_index in range(self.wrapper.num_layers):
            self.ui.layerComboBox.addItem(f"Layer {layer_index}", layer_index)

        # connect combobox change signal
        self.ui.layerComboBox.currentIndexChanged.connect(self.layer_combo_changed)

        # connect checkbox signal
        self.ui.drawLayerCheckBox.stateChanged.connect(self.layer_check_changed)
        self.ui.drawLayerCheckBox.setChecked(True)  # initial state

        # fill w and h spinboxes
        self.ui.widthSpinBox.setValue(self.wrapper.w)
        self.ui.heightSpinBox.setValue(self.wrapper.h)
        # connect apply button
        self.ui.applyResize.clicked.connect(self.apply_resize)
        # connect resizing signals
        self.ui.widthSpinBox.valueChanged.connect(self.width_changed)

        # block height changes if aspect ratio is to be kept
        self.ui.aspectRatioCheckBox.stateChanged.connect(self.aspect_ratio_changed)
        self.ui.aspectRatioCheckBox.setChecked(True)  # initial state

        # connect recolor checkbox
        self.ui.recolorCheckBox.stateChanged.connect(self.recolor_changed)

        # connect draw all and hide all buttons
        self.ui.drawAllButton.clicked.connect(self.draw_all_layers)
        self.ui.hideAllButton.clicked.connect(self.hide_all_layers)

        # Add Cancel Crop and Zoom buttons programmatically
        self.cancelCropButton = QPushButton(self.ui.groupBox)
        self.cancelCropButton.setObjectName("cancelCropButton")
        self.cancelCropButton.setText("Cancel crop")
        self.ui.verticalLayout_3.addWidget(self.cancelCropButton)
        self.cancelCropButton.clicked.connect(self.cancel_crop)

        self.zoomInButton = QPushButton(self.ui.groupBox)
        self.zoomInButton.setObjectName("zoomInButton")
        self.zoomInButton.setText("Zoom in")
        self.ui.verticalLayout_3.addWidget(self.zoomInButton)
        self.zoomInButton.clicked.connect(lambda: self.zoom(1.2))

        self.zoomOutButton = QPushButton(self.ui.groupBox)
        self.zoomOutButton.setObjectName("zoomOutButton")
        self.zoomOutButton.setText("Zoom out")
        self.ui.verticalLayout_3.addWidget(self.zoomOutButton)
        self.zoomOutButton.clicked.connect(lambda: self.zoom(0.8))

    def aspect_ratio_changed(self):
        self.ui.heightSpinBox.setEnabled(not self.ui.aspectRatioCheckBox.isChecked())

    def width_changed(self):
        if self.ui.aspectRatioCheckBox.isChecked():
            # adjust height based on width
            aspect_ratio = self.wrapper.w / self.wrapper.h
            new_width = self.ui.widthSpinBox.value()
            new_height = int(new_width / aspect_ratio)
            self.ui.heightSpinBox.blockSignals(True)
            self.ui.heightSpinBox.setValue(new_height)
            self.ui.heightSpinBox.blockSignals(False)

    def apply_resize(self):
        self.wrapper.w = self.ui.widthSpinBox.value()
        self.wrapper.h = self.ui.heightSpinBox.value()
        self.request_new_image.emit()

    def layer_combo_changed(self):
        layer_index = self.ui.layerComboBox.currentData()
        # set the checkbox state
        is_visible = self.wrapper.is_layer_visible(layer_index)
        self.ui.drawLayerCheckBox.setChecked(is_visible)

    def layer_check_changed(self):
        layer_index = self.ui.layerComboBox.currentData()
        is_checked = self.ui.drawLayerCheckBox.isChecked()
        self.wrapper.set_layer_visible(layer_index, is_checked)
        self.request_new_image.emit()

    def recolor_changed(self):
        checked = self.ui.recolorCheckBox.isChecked()
        self.wrapper.set_color_scheme(checked)

    def draw_all_layers(self):
        for layer_index in range(self.wrapper.num_layers):
            self.wrapper.set_layer_visible(layer_index, True)
        self.request_new_image.emit()
        self.ui.drawLayerCheckBox.setChecked(True)

    def hide_all_layers(self):
        for layer_index in range(self.wrapper.num_layers):
            self.wrapper.set_layer_visible(layer_index, False)
        self.request_new_image.emit()
        self.ui.drawLayerCheckBox.setChecked(False)

    @pyqtSlot(np.ndarray)
    def update_graphics_view(self, image: np.ndarray):
        # Any rendering change resets crop selection and hides rubber band
        self._crop_px = None
        try:
            if self._rubber_band is not None:
                self._rubber_band.hide()
        except Exception:
            pass
        self.scene.clear()

        w, h = image.shape[1], image.shape[0]
        # ensure the numpy array is contiguous and keep a reference so the buffer isn't freed
        img = np.ascontiguousarray(image)
        self._img = img  # keep reference to the numpy buffer
        # create QImage from numpy buffer (RGB888 expected for 3-channel uint8 images)
        self.imgQ = QImage(img.data, w, h, img.strides[0], QImage.Format.Format_RGB888)
        pixMap = QPixmap.fromImage(self.imgQ)
        self.scene.addPixmap(pixMap)
        # view.fitInView(QRectF(0, 0, w, h), Qt.AspectRatioMode.KeepAspectRatio)
        self.scene.update()

    def cancel_crop(self):
        # Clear persistent crop and re-render full image
        self._crop_px = None
        # Restore spinboxes to current render size
        self.ui.widthSpinBox.blockSignals(True)
        self.ui.heightSpinBox.blockSignals(True)
        self.ui.widthSpinBox.setValue(self.wrapper.w)
        self.ui.heightSpinBox.setValue(self.wrapper.h)
        self.ui.widthSpinBox.blockSignals(False)
        self.ui.heightSpinBox.blockSignals(False)
        self.request_new_image.emit()

    def zoom(self, factor: float):
        try:
            self.ui.graphicsView.scale(factor, factor)
        except Exception:
            pass

    def get_mask(self):
        # render new image
        base = self.wrapper.new_image()

        # Apply crop at export time if available
        if isinstance(self._crop_px, tuple) and len(self._crop_px) == 4:
            h, w = base.shape[0], base.shape[1]
            x1, y1, x2, y2 = self._crop_px
            x1 = max(0, min(w, int(x1)))
            x2 = max(0, min(w, int(x2)))
            y1 = max(0, min(h, int(y1)))
            y2 = max(0, min(h, int(y2)))
            if x2 > x1 and y2 > y1:
                return np.ascontiguousarray(base[y1:y2, x1:x2])

        return base

    # Event filter to enable rubber-band rectangle selection for cropping
    def eventFilter(self, a0, a1):
        """Intercept mouse events on the graphicsView viewport to implement rubber-band cropping."""
        if self.ui.graphicsView is not None and a0 is self.ui.graphicsView.viewport():
            # catch mouse events
            if isinstance(a1, QMouseEvent):
                # Press
                if a1.type() == QEvent.Type.MouseButtonPress and (a1.buttons() & Qt.MouseButton.LeftButton):
                    self._rb_origin = a1.position().toPoint()
                    self._rubber_band.setGeometry(QRect(self._rb_origin, self._rb_origin))
                    self._rubber_band.show()
                    return True
                # Move
                elif a1.type() == QEvent.Type.MouseMove and self._rubber_band.isVisible() and self._rb_origin is not None:
                    current = a1.position().toPoint()
                    rect = QRect(self._rb_origin, current).normalized()
                    self._rubber_band.setGeometry(rect)
                    return True
                # Release
                elif a1.type() == QEvent.Type.MouseButtonRelease and self._rubber_band.isVisible() and self._rb_origin is not None:
                    end_pt = a1.position().toPoint()
                    rect = QRect(self._rb_origin, end_pt).normalized()
                    self._rb_origin = None
                    # Map viewport rect to scene coordinates
                    tl_scene = self.ui.graphicsView.mapToScene(rect.topLeft())
                    br_scene = self.ui.graphicsView.mapToScene(rect.bottomRight())
                    roi_scene = QRectF(tl_scene, br_scene).normalized()
                    # Convert to image pixel coordinates (scene coords align with image since added at (0,0))
                    if self._img is not None and self._img.size > 0:
                        h, w = self._img.shape[0], self._img.shape[1]
                        x1 = max(0, min(w, int(roi_scene.left())))
                        y1 = max(0, min(h, int(roi_scene.top())))
                        x2 = max(0, min(w, int(roi_scene.right())))
                        y2 = max(0, min(h, int(roi_scene.bottom())))
                        if x2 > x1 and y2 > y1:
                            # Store crop rectangle for export; keep the selection visible
                            self._crop_px = (x1, y1, x2, y2)
                            self._rubber_band.setGeometry(rect)
                            self._rubber_band.show()
                    return True
        return QDialog.eventFilter(self, a0, a1)
