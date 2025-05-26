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

    exposures = [1, 2, 5, 10, 20, 39, 78, 156, 312]
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
            self.cap.open(0)
        else:
            self.cap.open(source)   
        if self.cap.isOpened():


            # Set buffer size
            self.cap.set(cv.CAP_PROP_BUFFERSIZE, self.bufferSize)


            return [0, {"Error message": "OK"}]
        return [4, {"Error message": "Can not open camera"}]
    
    def set_exposure(self, exposure):
        """Sets the exposure time of the camera.

        Args:
            exposure (int): The exposure time in milliseconds.
        """
        if not self.cap.set(cv.CAP_PROP_EXPOSURE, exposure):
            return [4, {"Error message": "Can not set exposure time"}]

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

        # if cap isn't open, open -> get frame -> close again.
        elif self.open(source, exposure)[0] == 0:
            frame = get_frame(full_size)
            self.close()

        else:
            err = self.open(source, exposure)
            # NOTE: instead of the black frame, this now raises an error to be handled elsewhere.
            raise venusStatus(err[1]["Error message"], err[0])

        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        return frame
