import cv2 as cv
import numpy as np
import os

from PyQt6 import uic
from PyQt6 import QtWidgets
from PyQt6.QtCore import QObject
import matplotlib.pyplot as plt

# for gds loading
from klayout import lay


class Affine:
    """Calculates the affine transformation between two images using SIFT keypoints and descriptors.
    Assumes the images are grayscale.
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
        - A (np.ndarray): Affine transformation matrix
        """
        self._MIN_MATCH_COUNT = (
            15  # Minimum number of matches required to find affine transformation.
        )
        self.imgW = None  # Image that produced the result
        self.maskW = None  # Mask that produced the result
        self.A = None  # Affine transformation matrix
        self.internal_img = None  # Internal image
        self.internal_mask = None  # Internal mask
        self.pm = None

        # Load the settings based on the name of this file.
        self.path = os.path.dirname(__file__) + os.path.sep
        filename = (
            os.path.splitext(os.path.basename(__file__))[0] + "_settingsWidget.ui"
        )
        self.settingsWidget = uic.loadUi(self.path + filename)

        # save the labels that might be modified:
        self.affine_label = self.settingsWidget.findChild(
            QtWidgets.QLabel, "affineLabel"
        )
        self.mask_label = self.settingsWidget.findChild(QtWidgets.QLabel, "maskLabel")

    @staticmethod
    def _preprocess_img(img):
        """
        Preprocesses the input image by converting to grayscale, applying Gaussian blur,
        and histogram equalization.

        Args:
        - img (np.ndarray): Input image.

        Returns:
        - img (np.ndarray): Preprocessed image.
        """

        img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)  # Convert to grayscale
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
        # Invert image. The mask should be white and the background black.
        mask = cv.bitwise_not(mask)
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
        Attempts to find the affine transformation between the input image and
        mask using SIFT keypoints and descriptors.

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
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.settingsWidget,
            "Open Image",
            self.path + os.sep + "masks",
            "Image Files (*.png *.jpg *.bmp)",
        )

        if fileName:
            self.internal_mask = cv.imread(fileName, cv.IMREAD_GRAYSCALE)
            self.mask_label.setText("Mask loaded successfully.")

    def mask_gds_button(self):
        """Interface for the gds mask loading button."""
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.settingsWidget,
            "Open .GDS file",
            self.path + os.sep + "masks",
            "Mask Files (*.gds)",
        )
        if fileName:
            self.load_and_save_gds(fileName)

    def find_button(self) -> bool:
        """Interface for the find button

        Returns:
            bool: Affine found or not
        """
        self.update_img()

        if self.internal_mask is None:
            self.affine_label.setText("No mask loaded. Please load a mask.")
            return False

        if self.try_match(self.internal_img, self.internal_mask):
            self.affine_label.setText("Affine matrix found. Click 'Save' to visualize.")
            return True
        else:
            self.affine_label.setText(
                "Affine matrix not found. Check camera feed and click again."
            )
            return False

    def save_button(self):
        """Interface for the save button. Shows the affine transformation."""
        visu = Visualize(self)
        visu.queue_affine()
        visu.show()

    # FIXME: add something to check the state of the camera return, and notify user.
    def update_img(self):
        """Calls the camera through a hook and updates the internal image."""
        return_img = self.pm.hook.camera_get_image()
        if return_img[0] is np.zeros((480, 640, 3), np.uint8):
            self.affine_label.setText("Camera not connected or invalid image format.")
            print("Camera not connected or invalid image format.")

        # HACK: self.pm.hook.camera_get_image() returns a list, take first.
        if isinstance(return_img, list):
            self.internal_img = return_img[0]

    def check_mask_button(self):
        """Interface to check the mask image. Displays the mask image in a window."""
        if self.internal_mask is not None:
            cv.imshow("Mask", self.internal_mask)
            cv.waitKey(0)

    # FIXME: the size is a bit arbitary. Scale to mask size?
    def load_and_save_gds(
        self,
        input_gds_path,
        output_image_path=None,
        width=800,
        height=800,
    ):
        """Loads a GDS file and saves it as a PNG image.

        Args:
            input_gds_path (str): path to .gds file
            output_image_path (str, optional): Where to save results. Defaults to None.
            width (int, optional): image width. Defaults to 800.
            height (int, optional): image height. Defaults to 800.
        """

        if output_image_path is None:
            output_image_path = (
                self.path + os.sep + "masks" + os.sep + "converted_mask.png"
            )
        # Create a layout view
        view = lay.LayoutView()

        view.load_layout(input_gds_path, add_cellview=True)

        # Zoom to fit the entire layout
        view.zoom_fit()
        # mystery function that makes sure all layers are visible: https://www.klayout.de/forum/discussion/1711/screenshot-with-all-the-layer-and-screenshot-only-one-layer#latest
        view.max_hier()

        # Iterate over all layers and make them visible and remove the dither pattern just in case.
        it = view.begin_layers()
        while not it.at_end():
            lp = it.current()
            new_layer = lp.dup()
            new_layer.visible = True
            new_layer.clear_dither_pattern()  # AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA why is this called dither pattern instead of stipple like in the GUI. I'm intensely mad about this
            view.set_layer_properties(it, new_layer)

            it.next()

        # Save the layout view as an image
        view.save_image(output_image_path, width, height)

        self.internal_mask = cv.imread(output_image_path, cv.IMREAD_GRAYSCALE)
        self.mask_label.setText("Mask converted and loaded successfully.")


# Ugly import workaround.
class Visualize:
    def __init__(self, parent):
        self.parent = parent
        self.visuQueue = []

    def queue_affine(self):
        if self.parent.A is not None:
            # Warp the img using the affine transformation matrix
            warped_img = cv.warpAffine(
                self.parent.imgW,
                self.parent.A,
                (self.parent.maskW.shape[1], self.parent.maskW.shape[0]),
            )

            # Convert both images to color to allow blending
            if len(self.parent.maskW.shape) == 2:  # If maskW is grayscale
                mask_color = cv.cvtColor(self.parent.maskW, cv.COLOR_GRAY2BGR)
            else:
                mask_color = self.parent.maskW.copy()

            if len(warped_img.shape) == 2:  # If warped_img is grayscale
                warped_img_color = cv.cvtColor(warped_img, cv.COLOR_GRAY2BGR)
            else:
                warped_img_color = warped_img.copy()

            # Blend the images with transparency
            alpha = 0.5  # Transparency factor
            blended_img = cv.addWeighted(
                mask_color, 1 - alpha, warped_img_color, alpha, 0
            )

            # Get screen resolution
            screen_res = 1920, 1080
            scale_width = screen_res[0] / blended_img.shape[1]
            scale_height = screen_res[1] / blended_img.shape[0]
            scale = min(scale_width, scale_height)

            # Rescale the image
            new_size = (
                int(blended_img.shape[1] * scale),
                int(blended_img.shape[0] * scale),
            )
            resized_img = cv.resize(blended_img, new_size, interpolation=cv.INTER_AREA)

            # add visu to queue
            self.visuQueue.append(resized_img)

        else:
            print("Affine transform not found. Run try_match() first.")

    # Prints out the visualizations in the queue
    def show(self, num_rows=2):
        num_images = len(self.visuQueue)

        # Calculate the number of columns
        num_cols = (num_images + num_rows - 1) // num_rows

        # Adjust the figsize to accommodate the grid layout better
        plt.figure(figsize=(5 * num_cols, 5 * num_rows))

        for i in range(num_images):
            img = self.visuQueue.pop(0)  # Remove the first element from visuQueue
            plt.subplot(num_rows, num_cols, i + 1)
            plt.imshow(img)
            plt.axis("off")  # Optional: Turn off axis

        plt.tight_layout()
        plt.show()
