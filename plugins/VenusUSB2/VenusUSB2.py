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
            self.cap.read()  # read so that the camera doesn't feel sad
            # also makes sure that the exposure is properly set, some cameras seem to need this.
            if exposure is None:
                exposure = 1
            if not self.cap.set(cv.CAP_PROP_EXPOSURE, exposure):
                self.close()
                return [4, {"Error message": "Can not set exposure time"}]

            ##IRtothink#### should the next settings be obtaines as parameters

            # Set buffer size to 1.
            self.cap.set(cv.CAP_PROP_BUFFERSIZE, self.bufferSize)

            # Set resolution / aspect ratio
            self.cap.set(cv.CAP_PROP_FRAME_WIDTH, self.cap_width)
            self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, self.cap_height)
            return [0, {"Error message": "OK"}]
        return [4, {"Error message": "Can not open camera"}]

    def close(self):
        """Pretty self explanatory"""
        self.cap.release()

    def capture_image(self, source, exposure, full_size=False):
        """Captures an image from the camera. NOTE: returns color image

        Returns:
            matlike: The captured image as matlike object, in RGB format.
        """

        def get_frame(full_size):
            # FIXME: check if this creates too much overhead, I imagine changing the resolution should be constant time and not affect the performance.
            # besides, full_size will probably be used just for single captures for Affine.
            if full_size:
                self.cap.set(cv.CAP_PROP_FRAME_WIDTH, self.full_size_width)
                self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, self.full_size_height)

            for _ in range(self.bufferSize):
                # empty out the buffer
                self.cap.read()
            # get the frame
            _, frame = self.cap.read()

            if full_size:
                self.cap.set(cv.CAP_PROP_FRAME_WIDTH, self.cap_width)
                self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, self.cap_height)
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
