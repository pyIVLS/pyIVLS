"""
This is a template for a plugin core implementation in pyIVLS

This file should be independent on GUI, i.e. it should be made in a way that allows to reuse it in other scripts
"""

import cv2 as cv


class pluginTemplate:
    """below is an minimum example from VenusUSB camera plugin"""

    def __init__(self):
        # Initialize cap as empty capture
        self.cap = cv.VideoCapture()

    def open(self, source=None, exposure=None) -> int:
        """Opens the camera using current settings.

        Returns:
            0 - no error
            ~0 - error (add error code later on if needed)
        """
        if (source is None) or (exposure is None):
            return 1
        self.cap.open(source)
        if self.cap.isOpened():
            return 0
        return 2

    def close(self):
        """Pretty self explanatory"""
        self.cap.release()
