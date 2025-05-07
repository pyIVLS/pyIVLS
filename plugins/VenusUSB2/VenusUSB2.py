import cv2 as cv
import os

import numpy as np

class VenusUSB2:
    """Handles communication with the VenusUSB2 camera"""

    exposures = [1, 2, 5, 10, 20, 39, 78, 156, 312]
    bufferSize = 1

    def __init__(self):

        # Initialize cap as empty capture
        self.cap = cv.VideoCapture()

    def open(self, source=None, exposure=None) -> "status":
        """Opens the camera using current settings.

        Returns:
            0 - no error
            ~0 - error (add error code later on if needed)
        """
        if (source is None) or (exposure is None):
            return [1, {"Error message":"Source or exposure time not set"}]
        self.cap.open(source)
        if self.cap.isOpened():          
            #set exposure
            
            ## Check if the camera supports setting exposure
            ##		not really needed here, as this code is hardware specifc
            ##		should be used in general purpose code
            ##
            #if not self.cap.get(cv.CAP_PROP_EXPOSURE):
            #  print("Camera does not support setting exposure.")
            #  return
            
            if not self.cap.set(cv.CAP_PROP_EXPOSURE, exposure):
                 return [4, {"Error message":"Can not set exposure time"}]
            
            ##IRtothink#### should the next settings be obtaines as parameters
            
            # Set buffer size to 1.
            self.cap.set(cv.CAP_PROP_BUFFERSIZE, self.bufferSize)
            
            # Set resolution
            self.cap.set(cv.CAP_PROP_FRAME_WIDTH, 1024)
            self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, 768)
            return [0, {"Error message":"OK"}]
        return [4, {"Error message":"Can not open camera"}]

    def close(self):
        """Pretty self explanatory"""
        self.cap.release()

    # FIXME: Maybe this should send more info if an error is encountered.
    # Info could be used in AFFINE to display a message to the user.
    def capture_image(self) -> cv.typing.MatLike:
        """Captures an image from the camera. NOTE: returns color image

        Returns:
            matlike: The image
        """
        # is the cap opened?
        # HACK: Camera is set to buffer 1 frame, so 1 frame is discarded to get current state.
        if self.cap.isOpened():
            self.cap.read()
            _, frame = self.cap.read()
        elif self.open_camera():
            self.cap.read()
            _, frame = self.cap.read()
        else:
            frame = np.zeros((480, 640, 3), np.uint8) # 3 is number of channels
        return frame
