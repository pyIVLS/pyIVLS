import cv2 as cv
import os

from PyQt6 import uic
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QObject

"""
User Controls

                    brightness 0x00980900 (int)    : min=0 max=255 step=1 default=128 value=128
                    contrast 0x00980901 (int)    : min=0 max=255 step=1 default=128 value=128
                    saturation 0x00980902 (int)    : min=0 max=255 step=1 default=64 value=64
    white_balance_automatic 0x0098090c (bool)   : default=1 value=1
    white_balance_temperature 0x0098091a (int)    : min=1 max=5 step=1 default=1 value=1 flags=inactive
                    sharpness 0x0098091b (int)    : min=0 max=255 step=1 default=128 value=128

Camera Controls

                auto_exposure 0x009a0901 (menu)   : min=0 max=3 default=3 value=1 (Manual Mode)
            1: Manual Mode
        exposure_time_absolute 0x009a0902 (int)    : min=0 max=320 step=1 default=20 value=10
    focus_automatic_continuous 0x009a090c (bool)   : default=0 value=0
"""

class VenusUSB2(QObject):
    def __init__(self):
        # FIXME check the exposures
        self.handle = "/dev/video2"
        self.exposures = [0,1,2,5,10,20,39,78,156,312]
        print("i have become python, the creator of cameras")

        QObject.__init__(self)    
        self.path = os.path.dirname(__file__) + os.path.sep 
        self.settingsWidget = uic.loadUi(self.path + 'camera_settingsWidget.ui')

    def open_camera(self):
        # Method to open the camera
        self.cap = cv.VideoCapture(self.handle)
        assert self.cap.isOpened(), "Error: Unable to open camera"

    def close_camera(self):
        self.cap.release()

    def capture_image(self):
        # Method to capture an image
        ret, frame = self.cap.read()
        return frame
    

    def preview(self):
        # Method to preview the camera feed
        while True:
            frame = self.capture_image()
            cv.imshow('Camera Feed', frame)
            if cv.waitKey(1) & 0xFF == ord('q'):
                break

    def set_exposure(self, exposure):
        # Method to set the exposure
        assert 0 <= exposure <= 9, "Error: Exposure value out of range"
        self.cap.set(cv.CAP_PROP_EXPOSURE, self.exposures[exposure])

    def get_exposure(self):
        # Method to get the exposure value
        return self.cap.get(cv.CAP_PROP_EXPOSURE)

    