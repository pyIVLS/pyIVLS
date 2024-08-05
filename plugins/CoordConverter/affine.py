import cv2 as cv
import numpy as np
import os

from PyQt6 import uic
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QFileDialog,
    QVBoxLayout,
)
from PyQt6.QtCore import QObject
from PyQt6.QtGui import QPixmap


class Affine(QObject):
    """Calculates the affine transformation between two images using SIFT keypoints and descriptors. Assumes the images are grayscale.
    Usage:
    - Create an Affine object.
    - Call try_match() with the input image and mask.
    - If the transformation is found, access the transformation matrix using the A attribute.
    - When transformation is found, use coords() to get the transformed coordinates of a point.
    """

    def __init__(self):
        """
        Initializes the Affine class.

        Attributes:
        - MIN_MATCH_COUNT (int): Minimum number of matches required to find affine transformation.
        - imgW (np.ndarray): Image that produced the result.
        - maskW (np.ndarray): Mask that produced the result.
        - A (np.ndarray): Affine transformation matrix.
        """
        self._MIN_MATCH_COUNT = (
            10  # Minimum number of matches required to find affine transformation.
        )
        self.imgW = None  # Image that produced the result
        self.maskW = None  # Mask that produced the result
        self.A = None  # Affine transformation matrix

        # Load the settings widget
        QObject.__init__(self)
        self.path = os.path.dirname(__file__) + os.path.sep
        self.settingsWidget = uic.loadUi(self.path + "affine_settingsWidget.ui")

    @staticmethod
    def _preprocess_img(img):
        """
        Preprocesses the input image by applying Gaussian blur and histogram equalization.

        Args:
        - img (np.ndarray): Input image.

        Returns:
        - img (np.ndarray): Preprocessed image.
        """
        img = cv.GaussianBlur(img, (5, 5), 0)  # Remove noise
        img = cv.equalizeHist(img)  # Bring out contrast
        return img

    @staticmethod
    def _preprocess_mask(mask):
        """
        Preprocesses the input mask by inverting and applying histogram equalization.

        Args:
        - mask (np.ndarray): Input mask.

        Returns:
        - mask (np.ndarray): Preprocessed mask.
        """
        mask = cv.bitwise_not(
            mask
        )  # Invert image. The mask should be white and the background black.
        mask = cv.equalizeHist(mask)  # Bring out contrast
        return mask

    def try_match(
        self,
        img,
        mask,
        octaveLayers=6,
        contrastThresshold=0.08,
        edgeThreshold=14,
        sigma=2.6,
    ) -> bool:
        """
        Attempts to find the affine transformation between the input image and mask using SIFT keypoints and descriptors.

        Args:
        - img (np.ndarray): Input image.
        - mask (np.ndarray): Input mask.
        - octaveLayers (int): Number of octave layers in SIFT. Default is 6.
        - contrastThresshold (float): Contrast threshold in SIFT. Default is 0.08.
        - edgeThreshold (int): Edge threshold in SIFT. Default is 14.
        - sigma (float): Sigma value in SIFT. Default is 2.6.

        Returns:
        - bool: True if the affine transformation is successfully found, False otherwise.
        """
        # Initiate SIFT detector
        sift = cv.SIFT_create(
            nfeatures=0,  # OpenCV default: 0
            nOctaveLayers=octaveLayers,  # OpenCV default: 3
            contrastThreshold=contrastThresshold,  # OpenCV default: 0.04. This value is divided by nOctavelayers. Lowe used 0.03.
            edgeThreshold=edgeThreshold,  # OpenCV default: 10
            sigma=sigma,  # OpenCV default: 1.6
        )

        # Preprocess the images
        img = self._preprocess_img(img)
        mask = self._preprocess_mask(mask)

        # find the keypoints and descriptors with SIFT
        kp1, des1 = sift.detectAndCompute(img, None)
        kp2, des2 = sift.detectAndCompute(mask, None)

        # Use BFMatcher to match descriptors.
        bf = cv.BFMatcher(crossCheck=True)
        matches = bf.match(des1, des2)

        if len(matches) > self._MIN_MATCH_COUNT:
            src_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(
                -1, 1, 2
            )
            dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(
                -1, 1, 2
            )
            A, aMask = cv.estimateAffinePartial2D(
                src_pts, dst_pts, method=cv.RANSAC, ransacReprojThreshold=2
            )
            # Populate the class variables when a transformation is found.
            self.A = A
            self.imgW = img
            self.maskW = mask
            return True
        else:
            return False

    def coords(self, x, y):
        """
        Converts x, y coordinates using the calculated affine matrix.

        Args:
        - x (float): x-coordinate.
        - y (float): y-coordinate.

        Returns:
        - tuple: Transformed coordinates (x', y').
        """
        if self.A is None:
            raise ValueError(
                "Affine transformation matrix not found. Run try_match() first."
            )

        # Create a homogeneous coordinate vector
        point = np.array([[x, y, 1]], dtype=np.float32)

        # Apply the affine transformation matrix
        transformed_point = cv.transform(point, self.A)

        # Extract the transformed coordinates
        x_prime, y_prime, _ = transformed_point[0]

        return x_prime, y_prime

    def mask_button(self):
        """
        Function to be called when the mask button is clicked.
        """
        fileName, _ = QFileDialog.getOpenFileName(
            self.settingsWidget,
            "Open Image",
            self.path + "masks",
            "Image Files (*.png *.jpg *.bmp)",
        )

        if fileName:
            # Display the image in the label
            pixmap = QPixmap(fileName)
            image_label = self.settingsWidget.findChild(QLabel, "imageLabel")
            if image_label:
                image_label.setPixmap(pixmap)
                image_label.setScaledContents(True)  # Make the image fit the label size
