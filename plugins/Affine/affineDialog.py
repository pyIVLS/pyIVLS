import sys
from PyQt6.QtWidgets import QApplication, QDialog
from PyQt6.QtCore import QFile, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QCheckBox, QComboBox
from PyQt6.QtGui import QImage, QPixmap
from affineMatchDialog import Ui_Dialog
import numpy as np

class dialog(QDialog):


    # Slots

    
    def __init__(self, affine, img, mask, pointslist=None):
        super(QDialog, self).__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # find all objects inside "groupBox" and connect them to the _preprocessing_settings_changed function
        for child in self.ui.groupBox.children():
            if isinstance(child, (QCheckBox)):
                child.stateChanged.connect(self._preprocessing_settings_changed)
            elif isinstance(child, (QComboBox)):
                child.currentTextChanged.connect(self._preprocessing_settings_changed)
        self.affine = affine

        self.pointslist = pointslist  # List of (x_mask, y_mask) tuples
        # preprocess:
        self.img = img 
        self.mask = mask
        self._preprocessing_settings_changed()
        self.ui.matchButton.clicked.connect(self._on_match_button_clicked)

    def _preprocessing_settings_changed(self):
        """Called when preprocessing settings are changed."""
        print("preprocessing settings changed")
        blurMask = self.ui.blurMask.isChecked()
        invertMask = self.ui.invertMask.isChecked()
        equalizeMask = self.ui.equalizeMask.isChecked()
        cannyMask = self.ui.cannyMask.isChecked()
        blurImage = self.ui.blurImage.isChecked()
        invertImage = self.ui.invertImage.isChecked()
        equalizeImage = self.ui.equalizeImage.isChecked()
        cannyImage = self.ui.cannyImage.isChecked()

        """
        # check validity of sigma values
        try:
            sigmaImage = float(self.ui.sigmaImage.currentText())
            sigmaMask = float(self.ui.sigmaMask.currentText())
        except ValueError:
            return 
        if sigmaImage < 0 or sigmaMask < 0:
            return
        """
        sigmaImage = 1.0
        sigmaMask = 1.0
        settings = {
            "blurMask": blurMask,
            "invertMask": invertMask,
            "equalizeMask": equalizeMask,
            "cannyMask": cannyMask,
            "blurImage": blurImage,
            "invertImage": invertImage,
            "equalizeImage": equalizeImage,
            "cannyImage": cannyImage,
            "sigmaImage": sigmaImage,
            "sigmaMask": sigmaMask
        }
        # preprocess the images
        self.affine.preprocessor.update_settings(settings)
        img = self.affine.preprocessor.preprocess_img(self.img)
        mask = self.affine.preprocessor.preprocess_mask(self.mask)
        self.update_images(img, mask)

    @staticmethod
    def to_pixmap(image):
        """Convert an image to a QPixmap."""
        if image is None:
            return None
        if len(image.shape) == 2:
            # Grayscale image
            height, width = image.shape
            bytes_per_line = width
            qimage = QImage(image.data, width, height, bytes_per_line, QImage.Format.Format_Grayscale8)
        elif len(image.shape) == 3 and image.shape[2] == 3:
            # RGB image
            height, width, _ = image.shape
            bytes_per_line = width * 3
            qimage = QImage(image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        elif len(image.shape) == 3 and image.shape[2] == 4:
            # RGBA image
            height, width, _ = image.shape
            bytes_per_line = width * 4
            qimage = QImage(image.data, width, height, bytes_per_line, QImage.Format.Format_RGBA8888)
        else:
            raise ValueError("Unsupported image format")
        return QPixmap.fromImage(qimage)
    
    def update_images(self, img, mask):
        imgview = self.ui.imgView
        maskview = self.ui.maskView

        # Clear previous scenes if any
        if hasattr(imgview, 'scene') and imgview.scene() is not None:
            imgview.scene().clear()
        if hasattr(maskview, 'scene') and maskview.scene() is not None:
            maskview.scene().clear()

        from PyQt6.QtWidgets import QGraphicsScene, QGraphicsPixmapItem
        if img is not None:
            img_pixmap = self.to_pixmap(img)
            if img_pixmap is not None:
                scene = QGraphicsScene()
                scene.addItem(QGraphicsPixmapItem(img_pixmap))
                imgview.setScene(scene)
        if mask is not None:
            mask_pixmap = self.to_pixmap(mask)
            if mask_pixmap is not None:
                scene = QGraphicsScene()
                scene.addItem(QGraphicsPixmapItem(mask_pixmap))
                maskview.setScene(scene)

    def _on_match_button_clicked(self):
        try:
            print("Match button clicked")
            self._preprocessing_settings_changed()  # Ensure preprocessing is applied

            # Run matching
            img = self.img
            # no preprocessing here, affine does it internally.
            self.affine.try_match(img)
            result = self.affine.result
            kp1 = result["kp1"]
            kp2 = result["kp2"]
            matches = result["matches"]
            mask_img = result["mask"]
            img_img = result["img"]
            print(f"Found {len(matches)} matches")
            # Create a side-by-side image
            import matplotlib.pyplot as plt
            import numpy as np
            h1, w1 = mask_img.shape[:2]
            h2, w2 = img_img.shape[:2]
            out_img = np.zeros((max(h1, h2), w1 + w2, 3), dtype=np.uint8)
            out_img[:h1, :w1] = mask_img if mask_img.ndim == 3 else np.stack([mask_img]*3, axis=-1)
            out_img[:h2, w1:w1+w2] = img_img if img_img.ndim == 3 else np.stack([img_img]*3, axis=-1)
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(out_img)
            # Draw matches (fix: use (col, row) = (x, y) for plotting)
            for m in matches:
                idx1, idx2 = m  # mask index, image index
                y1, x1 = kp1[idx1]  # (row, col)
                y2, x2 = kp2[idx2]
                ax.plot([x1, x2 + w1], [y1, y2], 'r-', linewidth=0.5)
                ax.plot(x1, y1, 'bo', markersize=2)
                ax.plot(x2 + w1, y2, 'go', markersize=2)
            # Draw defined points on mask and their transformed locations on image
            if self.pointslist is not None:
                for pt in self.pointslist:
                    # pt is (x_mask, y_mask) in GUI, but mask keypoints are (y, x)
                    x_mask, y_mask = pt
                    # Draw on mask (left)
                    ax.plot(x_mask, y_mask, 'mo', markersize=6, markeredgewidth=2, markeredgecolor='k')
                    # Draw on image (right) if affine is available
                    if hasattr(self.affine, 'A') and self.affine.A is not None:
                        x_img, y_img = self.affine.coords((x_mask, y_mask))
                        ax.plot(x_img + w1, y_img, 'co', markersize=6, markeredgewidth=2, markeredgecolor='k')
            ax.axis('off')
            plt.tight_layout()
            # Overlay transformed mask outline on the image if affine matrix exists
            if hasattr(self.affine, 'A') and self.affine.A is not None:
                import cv2
                h_mask, w_mask = mask_img.shape[:2]
                corners = np.float32([[0,0], [w_mask,0], [w_mask,h_mask], [0,h_mask]]).reshape(-1,1,2)
                transformed = cv2.perspectiveTransform(corners, self.affine.A)
                transformed = transformed.reshape(-1,2)
                # Draw on the right image
                for i in range(4):
                    x0, y0 = transformed[i % 4]
                    x1_, y1_ = transformed[(i+1) % 4]
                    ax.plot([x0 + w1, x1_ + w1], [y0, y1_], 'y-', linewidth=1)
            # Show in resultView
            from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
            canvas = FigureCanvas(fig)
            scene = self.ui.resultView.scene()
            if scene is not None:
                scene.clear()
            else:
                from PyQt6.QtWidgets import QGraphicsScene
                scene = QGraphicsScene()
                self.ui.resultView.setScene(scene)
            canvas.draw()
            width, height = canvas.get_width_height()
            img_buf = canvas.buffer_rgba()
            from PyQt6.QtGui import QImage, QPixmap
            qimg = QImage(img_buf, width, height, QImage.Format.Format_RGBA8888)
            pixmap = QPixmap.fromImage(qimg)
            from PyQt6.QtWidgets import QGraphicsPixmapItem
            scene.addItem(QGraphicsPixmapItem(pixmap))
            plt.close(fig)
        except Exception as e:
            print(f"Matching failed: {e}")
