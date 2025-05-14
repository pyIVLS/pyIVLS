import cv2 as cv
import numpy as np


class VenusUSB2:
    """Handles communication with the VenusUSB2 camera"""

    exposures = [1, 2, 5, 10, 20, 39, 78, 156, 312]
    bufferSize = 1
    cap_width = 1024
    cap_height = 768

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
            return [1, {"Error message": "Source or exposure time not set"}]
        self.cap.open(0)  # FIXME: Debug line
        if self.cap.isOpened():
            # set exposure
            if not self.cap.set(cv.CAP_PROP_EXPOSURE, exposure):
                return [4, {"Error message": "Can not set exposure time"}]

            ##IRtothink#### should the next settings be obtaines as parameters

            # Set buffer size to 1.
            self.cap.set(cv.CAP_PROP_BUFFERSIZE, self.bufferSize)
            # FIXME: Make sure that this is the correct aspect ratio,
            # otherwise I think the pixel conversion will be really bad.

            # Set resolution / aspect ratio
            self.cap.set(cv.CAP_PROP_FRAME_WIDTH, self.cap_width)
            self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, self.cap_height)
            return [0, {"Error message": "OK"}]
        return [4, {"Error message": "Can not open camera"}]

    def close(self):
        """Pretty self explanatory"""
        self.cap.release()

    # FIXME: Maybe this should send more info if an error is encountered.
    # Info could be used in AFFINE to display a message to the user.
    def capture_image(self, source, exposure):
        """Captures an image from the camera. NOTE: returns color image

        Returns:
            matlike: The image
        """
        # is the cap opened?
        # HACK: Camera is set to buffer 1 frame, so 1 frame is discarded to get current state.
        if self.cap.isOpened():
            self.cap.read()
            _, frame = self.cap.read()
        elif self.open(source, exposure)[0] == 0:
            self.cap.read()
            _, frame = self.cap.read()
            self.close()
        else:
            frame = np.zeros(
                (self.cap_height, self.cap_width, 3), np.uint8
            )  # 3 is number of channels

        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        return frame
