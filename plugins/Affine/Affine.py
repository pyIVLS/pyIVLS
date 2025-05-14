import os
from datetime import datetime

import cv2 as cv
import numpy as np

# for gds loading
from klayout import lay


class AffineError(Exception):
    """Trying out a custom error class.
    Might be easier to handle errors in the form of exceptions
    instead of returning error codes.?"""

    def __init__(self, message, error_code):
        super().__init__(message)
        self.error_code = error_code
        self.message = message
        self.timestamp = datetime.now().strftime("%H:%M:%S.%f")
        self.message = (
            f"{self.timestamp}: {self.message} (Affine error Code: {self.error_code})"
        )

    def __str__(self):
        return self.message


class Affine:
    """Calculates the affine transformation between two images using SIFT keypoints and descriptors.
    Assumes the images are grayscale.
    Usage:
    - Create an Affine object.
    - Call try_match() with the input image and mask.
    - If the transformation is found, access the transformation matrix using the A attribute.
    - When transformation is found, use coords() to get the transformed coordinates of a point.
    """

    _MIN_MATCH_COUNT = (
        4  # Minimum number of matches required to find affine transformation.
    )

    def __init__(self):
        """Initializes an instance of Affine."""
        self.path = os.path.dirname(__file__) + os.path.sep
        self.result = dict()
        self.A = None  # Affine transformation matrix
        self.internal_img = None  # Internal image
        self.internal_mask = None  # Internal mask

    @staticmethod
    def _preprocess_img(img):
        """
        Preprocesses the input image by resizing, applying Gaussian blur, and histogram equalization.

            Args:
            - img (np.ndarray): Input image.

            Returns:
            - img (np.ndarray): Preprocessed image.
        """

        if len(img.shape) == 3:  # Check if the image is not grayscale
            img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        # img = cv.GaussianBlur(img, (5, 5), 0)  # Remove noise
        # img = cv.medianBlur(img, 5)  # Remove noise
        img = cv.equalizeHist(img)  # Bring out contrast
        return img

    @staticmethod
    def _preprocess_mask(mask):
        """
        Preprocesses the input mask by resizing, inverting, and applying histogram equalization.

            Args:
            - mask (np.ndarray): Input mask.

        Returns:
        - mask (np.ndarray): Preprocessed mask.
        """

        if len(mask.shape) == 3:  # Check if the image is not grayscale
            mask = cv.cvtColor(mask, cv.COLOR_BGR2GRAY)
        # Invert image. The mask should be white and the background black
        mask = cv.bitwise_not(mask)
        mask = cv.equalizeHist(mask)  # Bring out contrast
        return mask

    def draw_keypoints(self):
        """
        Draws the keypoints on the images, and for visual validation:
        - Projects mask keypoints (kp2) into image coordinates using the affine matrix
        - Draws lines between the matched keypoints to show correspondences
        - Saves results to internal result dictionary
        """
        if self.result.get("img") is None or self.result.get("mask") is None:
            raise AffineError("No affine transformation found.", 4)

        img = self.result["img"].copy()
        mask = self.result["mask"].copy()
        kp1 = self.result["kp1"]
        kp2 = self.result["kp2"]
        matches = self.result["matches"]

        # Draw SIFT keypoints
        # img = cv.drawKeypoints(img, kp1, None, (0, 255, 0))
        # mask = cv.drawKeypoints(mask, kp2, None, (0, 255, 0))

        # Overlay projected kp2 points on the img using affine matrix
        if self.A is not None:
            for m in matches:
                pt_mask = kp2[m.trainIdx].pt  # (x, y) in mask

                # Transform mask keypoint to image space using coords()
                projected = self.coords(pt_mask)

                # Draw the projected point on the image in red
                cv.circle(
                    img, (int(projected[0]), int(projected[1])), 4, (0, 0, 255), -1
                )

                # Draw the original image keypoint in green
                cv.circle(mask, (int(pt_mask[0]), int(pt_mask[1])), 4, (0, 255, 0), 1)

        return img, mask

    def try_match(
        self,
        img: np.ndarray,
        octaveLayers=6,
        contrastThresshold=0.08,
        edgeThreshold=14,
        sigma=2.6,
    ) -> bool:
        """
        Attempts to find the affine transformation between the input image and
        mask using SIFT keypoints and descriptors.

        Args:
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
        mask = self.internal_mask
        if img is None:
            # ok so this should be caught in the GUI already.
            raise AffineError("No image provided.", 1)
        if mask is None:
            raise AffineError("No mask loaded.", 2)
        # Preprocess the images
        img = self._preprocess_img(img)
        mask = self._preprocess_mask(mask)

        # find the keypoints and descriptors with SIFT
        kp1, des1 = sift.detectAndCompute(img, None)
        kp2, des2 = sift.detectAndCompute(mask, None)

        # Use BFMatcher to match descriptors.
        bf = cv.BFMatcher(crossCheck=True)
        matches = bf.match(des1, des2)

        # Sort them in ascending order of distance
        matches = sorted(matches, key=lambda x: x.distance)

        # take top percentage of matches
        num_matches = int(len(matches) * 0.10)
        matches = matches[:num_matches]

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
            img = cv.cvtColor(img, cv.COLOR_GRAY2RGB)
            mask = cv.cvtColor(mask, cv.COLOR_GRAY2RGB)

            self.result["img"] = img
            self.result["mask"] = mask
            self.result["kp1"] = kp1
            self.result["kp2"] = kp2
            self.result["aMask"] = aMask
            self.result["matches"] = matches

            return True
        else:
            raise AffineError(
                f"Not enough matches are found - {len(matches)}/{self._MIN_MATCH_COUNT}",
                3,
            )

    def coords(self, point: tuple[float, float]) -> tuple[float, float]:
        """
        Transforms a point from the mask to the corresponding point on the image using the affine transformation.

        Args:
        - point (tuple): (x, y) coordinates of the point on the mask.

        Returns:
        - transformed_point (tuple): (x, y) coordinates of the corresponding point on the image.
        """
        if self.A is None:
            raise AffineError("No affine transformation found.", 4)

        # Convert the point to a homogeneous coordinate for affine transformation
        point_homogeneous = np.array([[point[0]], [point[1]], [1]])

        # Apply the affine transformation matrix A
        transformed_point = np.dot(self.A, point_homogeneous)

        # Return the transformed (x, y) coordinates
        return (transformed_point[0][0], transformed_point[1][0])

    # TODO: tune this one. The size is currently scaled to be the same as the camera images.
    def load_and_save_gds(
        self,
        input_gds_path,
        output_image_path=None,
        width=1024,
        height=768,
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

        internal_mask = cv.imread(output_image_path)
        internal_mask = cv.cvtColor(internal_mask, cv.COLOR_BGR2RGB)
        self.internal_mask = internal_mask
        return internal_mask

    def load_image(self, path: str) -> np.ndarray:
        """
        Loads an mask image from the specified path.

        Args:
            path (str): Path to the image file.

        Returns:
            np.ndarray: Loaded image.
        """

        img = cv.imread(path)
        if img is None:
            raise AffineError(f"Could not load image from {path}", 5)
        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        img = cv.resize(img, (1024, 768))  # Resize to match the camera image size
        self.internal_mask = img
        return img

    def update_interal_mask(self, path):
        if path.endswith(".gds"):
            mask = self.load_and_save_gds(path)
        else:
            mask = self.load_image(path)
        return mask

    def test_image(self) -> np.ndarray:
        """
        Loads a test image from the specified path.

        Returns:
            np.ndarray: Loaded test image.
        """
        img = cv.imread("plugins/Affine/testImages/NC3.png")
        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        img = cv.resize(img, (1024, 768))
        return img
