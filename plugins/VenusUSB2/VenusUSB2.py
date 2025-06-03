from datetime import datetime

import cv2 as cv


class venusStatus(Exception):
    # exceptionlist
    # 0 - no error
    # 1 - something is not set that should be
    # 2 - cannot set value for cap
    # 3 - can't open camera

    # NOTE: this is unused for now.

    def __init__(self, message, error_code):
        super().__init__(message)
        self.error_code = error_code
        self.message = message
        self.timestamp = datetime.now().strftime("%H:%M:%S.%f")
        self.message = (
            f"{self.timestamp}: {self.message} (VenusUSB error Code: {self.error_code})"
        )

    def __str__(self):
        return self.message


class VenusUSB2:
    """Handles communication with the VenusUSB2 camera"""

    #exposures = [1, 2, 5, 10, 20, 39, 78, 156, 312]
    exposures = [-12, -11, -10, -9, -8, -7, -6, -5, -4, -3, -2, -1]  # windows interface
    bufferSize = 1
    cap_width = 1024
    cap_height = 768
    full_size_width = 1920
    full_size_height = 1080

    def __init__(self):
        # Initialize cap as empty capture
        self.cap = cv.VideoCapture()

    def open(self, source=None, exposure=None) -> "status":
        """Opens the camera using current settings.

        Returns:
            0 - no error
            ~0 - error (add error code later on if needed)
        """

        if source is None or source == "":
            self.cap.open(1)
        else:
            self.cap.open(source)   
        if self.cap.isOpened():


            # Set buffer size
            self.cap.set(cv.CAP_PROP_BUFFERSIZE, self.bufferSize)
            # Set camera resolution
            self.cap.set(cv.CAP_PROP_FRAME_WIDTH, self.full_size_width)
            self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, self.full_size_height)

            return [0, {"Error message": "OK"}]
        return [4, {"Error message": "Can not open camera"}]
    
    def set_exposure(self, exposure):
        """Sets the exposure time of the camera.

        Args:
            exposure (int): Exposure time in weird arbitrary units
        """

        if not self.cap.set(cv.CAP_PROP_EXPOSURE, exposure):
            return [4, {"Error message": "Can not set exposure time"}]
        camera_exposure = self.cap.get(cv.CAP_PROP_EXPOSURE)

        return [0, {"Error message": "OK"}]

    def close(self):
        """Pretty self explanatory"""
        self.cap.release()

    def capture_image(self, source, exposure, full_size=False):
        """Captures an image from the camera. NOTE: returns color image

        Returns:
            matlike: The captured image as matlike object, in RGB format.
        """

        def get_frame(full_size):
            for _ in range(self.bufferSize):
                # empty out the buffer
                self.cap.read()
            # get the frame
            _, frame = self.cap.read()
            return frame

        # if cap is open, get the frame
        if self.cap.isOpened():
            frame = get_frame(full_size)
        else:
            status, message = self.open(source, exposure)
            if status != 0:
                # if cap is not open, raise an error
                raise venusStatus(message["Error message"], status)
            frame = get_frame(full_size)


        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        return frame

    def capture_buffered(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        return ret, frame