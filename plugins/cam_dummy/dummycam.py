import os
import cv2 as cv


class DummyCamera:
    """Mock camera: returns the image selected in the GUI."""

    def __init__(self):
        self.image_path = None
        self.opened = False

    def open(self, source=None, exposure=None):
        if source is None or not os.path.isfile(source):
            return [4, {"Error message": "Image file not provided or does not exist"}]
        self.image_path = source
        self.opened = True
        return [0, {"Error message": "OK"}]

    def set_exposure(self, exposure):
        return [0, {"Error message": "OK"}]

    def close(self):
        self.opened = False
        self.image_path = None

    def capture_image(self, source=None, exposure=None):
        path = source if source else self.image_path
        if not path or not os.path.isfile(path):
            return [4, {"Error message": "No image selected or file does not exist"}]
        img = cv.imread(path)
        if img is None:
            return [4, {"Error message": f"Failed to load image: {path}"}]
        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        return (0, img)

    def capture_buffered(self):
        return self.capture_image()
