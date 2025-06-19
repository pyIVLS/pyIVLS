import sys
from PyQt6.QtWidgets import QApplication, QDialog
from PyQt6.QtCore import QFile, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QCheckBox, QComboBox
from affineMatchDialog import Ui_Dialog
import numpy as np

class dialog(QDialog):
    signalDialogClosed = pyqtSignal()
    signalPreprocessingSettingsChanged = pyqtSignal(dict)
    signalMatchRequested = pyqtSignal(dict)

    # Slots
    @pyqtSlot(list[np.ndarray])
    def update_images(self, images):
        """Update the images in the dialog."""
        print("Images updated:", len(images))
        # Here you would update the UI with the new images
        # For example, you could set them to a QLabel or QGraphicsView

    @pyqtSlot(dict)
    def match_recieved(self, match):
    
    def __init__(self):
        super(QDialog, self).__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        # find all objects inside "groupBox" and connect them to the _preprocessing_settings_changed function
        for child in self.ui.groupBox.children():
            if isinstance(child, (QCheckBox)):
                child.stateChanged.connect(self._preprocessing_settings_changed)
            elif isinstance(child, (QComboBox)):
                child.currentTextChanged.connect(self._preprocessing_settings_changed)


    def _preprocessing_settings_changed(self):
        """Called when preprocessing settings are changed."""
        print("preprocessing settings changed")
        equalizeImage = self.ui.equalizeImage.isChecked()
        cannyMask = self.ui.cannyMask.isChecked()
        blurImage = self.ui.blurImage.isChecked()
        invertImage = self.ui.invertImage.isChecked()
        equalizeImage = self.ui.equalizeImage.isChecked()
        cannyMask = self.ui.cannyMask.isChecked()
        blurMask = self.ui.blurMask.isChecked()
        invertMask = self.ui.invertMask.isChecked()


        # check validity of sigma values
        try:
            sigmaImage = float(self.ui.sigmaImage.currentText())
            sigmaMask = float(self.ui.sigmaMask.currentText())
        except ValueError:
            return 
        if sigmaImage < 0 or sigmaMask < 0:
            return
        
        settings = {
            "equalizeImage": equalizeImage,
            "cannyMask": cannyMask,
            "blurImage": blurImage,
            "invertImage": invertImage,
            "blurMask": blurMask,
            "invertMask": invertMask,
            "sigmaImage": sigmaImage,
            "sigmaMask": sigmaMask
        }
        self.signalPreprocessingSettingsChanged.emit(settings)


