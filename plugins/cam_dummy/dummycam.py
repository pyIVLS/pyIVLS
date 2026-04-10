import os
import cv2 as cv


class DummyCamera:
    """Mock camera implementing VenusUSB2-like API, reading frames from a file."""

    exposures = [1, 2, 5, 10, 20, 39, 78, 156, 312]
    bufferSize = 1

    def __init__(self):
        self.image_path = None
        self.opened = False

    def open(self, source=None, exposure=None):
        """Opens the mock camera by validating the source file path."""
        if source is None or source == "":
            return [4, {"Error message": "Image file path not provided"}]
        if not os.path.isfile(source):
            return [4, {"Error message": "Image file does not exist"}]
        self.image_path = source
        self.opened = True
        return [0, {"Error message": "OK"}]

    def set_exposure(self, exposure):
        """No-op for mock; kept for API compatibility."""
        return [0, {"Error message": "OK"}]

    def close(self):
        self.opened = False
        self.image_path = None

    def _read_image(self, path):
        img = cv.imread(path)
        if img is None:
            return None
        return cv.cvtColor(img, cv.COLOR_BGR2RGB)

    def capture_image(self, source=None, exposure=None):
        """Returns the selected image as a frame (RGB)."""
        path = source if source else self.image_path
        if not path or not os.path.isfile(path):
            return [4, {"Error message": "No image selected or file does not exist"}]
        img = self._read_image(path)
        if img is None:
            return [4, {"Error message": f"Failed to load image: {path}"}]
        return (0, img)

    def capture_buffered(self):
        """Buffered capture to mimic camera streaming; returns the same image repeatedly."""
        return self.capture_image()
