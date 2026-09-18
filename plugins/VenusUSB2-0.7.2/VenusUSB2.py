import cv2 as cv


class VenusUSB2:
    """Handles communication with the VenusUSB2 camera"""

    exposures = [1, 2, 5, 10, 20, 39, 78, 156, 312]
    # exposures = [-12, -11, -10, -9, -8, -7, -6, -5, -4, -3, -2, -1]  # windows interface
    bufferSize = 1
    cap_width = 1024
    cap_height = 768
    full_size_width = 640 * 2
    full_size_height = 480 * 2

    def __init__(self):
        # Initialize cap as empty capture
        self.cap = cv.VideoCapture()

    def open(self, source=None, exposure=None) -> tuple[int, dict]:
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
        _ = self.cap.get(cv.CAP_PROP_EXPOSURE)

        return [0, {"Error message": "OK"}]

    def close(self):
        """Pretty self explanatory"""
        self.cap.release()

    def capture_image(self, source, exposure):
        """Captures an image from the camera. NOTE: returns color image

        Returns:
            matlike: The captured image as matlike object, in RGB format.
        """

        def get_frame():
            for _ in range(self.bufferSize):
                # empty out the buffer
                self.cap.read()
            # get the frame
            ret, frame = self.cap.read()
            return ret, frame

        # if cap is open, get the frame
        if self.cap.isOpened():
            ret, frame = get_frame()
        else:
            status, message = self.open(source, exposure)
            if status != 0:
                return [status, message]
            ret, frame = get_frame()

        if not ret:
            return [4, {"Error message": "Can not read frame from camera"}]
        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        return (0, frame)

    def capture_buffered(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            status = 0
        else:
            status = 4
            frame = {"Error message": "Can not read frame from camera"}
        return status, frame
