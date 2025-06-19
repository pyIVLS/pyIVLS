import os
from datetime import datetime

import cv2 as cv
import numpy as np
import skimage as ski

# for gds loading
from klayout import lay

# Sift detection moved over to skimage since I prefer it.
from skimage.feature import SIFT, match_descriptors
from skimage.color.adapt_rgb import adapt_rgb, each_channel

import skimage as ski

class Preprocessor:
    def __init__(self):
        self.settings = {
            "blurMask": False,
            "invertMask": False,
            "equalizeMask": False,
            "cannyMask": False,
            "blurImage": False,
            "invertImage": False,
            "equalizeImage": False,
            "cannyImage": False,
            "sigmaImage": 1.0,
            "sigmaMask": 1.0,
        }

    def update_settings(self, settings_dict):
        self.settings.update(settings_dict)

    def preprocess_img(self, img):
        print("Preprocessing image")
        s = self.settings
        if len(img.shape) == 3:
            img = ski.color.rgb2gray(img)
        if s['invertImage']:
            print("Inverting image")
            img = 1.0 - img
        if s['equalizeImage']:
            print("Equalizing image")
            img = ski.exposure.equalize_hist(img)
        if s['blurImage']:
            print("Blurring image")
            img = ski.filters.median(img)
        if s['cannyImage']:
            print("Applying Canny edge detection to image")
            img = ski.feature.canny(img, sigma=s['sigmaImage'])
            img = img.astype(float)
        img = (img * 255).astype("uint8")
        return img

    def preprocess_mask(self, mask):
        print("Preprocessing mask")
        s = self.settings
        if len(mask.shape) == 3:
            mask = ski.color.rgb2gray(mask)
        if s['invertMask']:
            print("Inverting mask")
            mask = 1.0 - mask
        if s['equalizeMask']:
            print("Equalizing mask")
            mask = ski.exposure.equalize_hist(mask)
        if s['blurMask']:
            print("Blurring mask")
            mask = ski.filters.median(mask)
        if s['cannyMask']:
            print("Applying Canny edge detection to mask")
            mask = ski.feature.canny(mask, sigma=s['sigmaMask'])
            mask = mask.astype(float)
        mask = (mask * 255).astype("uint8")
        return mask


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


class Affine_IO:
    def __init__(self, path):
        self.path = path

    def load_and_save_gds(
        self,
        input_gds_path,
        output_image_path=None,
        width=1920,
        height=1080,
    ):
        """Loads a GDS file and saves it as a large PNG image.

        Args:
            input_gds_path (str): path to .gds file
            output_image_path (str, optional): Where to save results. Defaults to None.
            width (int, optional): image width.
            height (int, optional): image height.
        """
        filename = os.path.basename(input_gds_path)
        filename = filename.split(".")[0]
        if output_image_path is None:
            output_image_path = (
                self.path + os.sep + "masks" + os.sep + filename + ".png"
            )
        # Create a layout view
        view = lay.LayoutView(options=lay.LayoutView.LV_NoGrid)
        lay.LayoutViewBase.LV_NoEditorOptionsPanel
        view.load_layout(input_gds_path, add_cellview=False)
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

        return internal_mask, filename

    def load_image(self, path):
        """
        Loads an mask image from the specified path.

        Args:
            path (str): Path to the image file.

        Returns:
            cv.matlike: Loaded image.
        """

        img = cv.imread(path)
        filename = os.path.basename(path)
        filename = filename.split(".")[0]
        if img is None:
            raise AffineError(f"Could not load image from {path}", 5)
        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        return img, filename


class Affine:
    """Calculates the affine transformation between two images using SIFT keypoints and descriptors.
    Assumes the images are grayscale.
    Usage:
    - Create an Affine object.
    - Load the mask image using update_interal_mask().
    - Call try_match() with the input image and mask.
    - If the transformation is found, access the transformation matrix using the A attribute.
    - When transformation is found, use coords() to get the transformed coordinates of a point.

    revision 1.2.0
    - Separated keypoint detection and transformation estimation.
    """

    # TODO: Add the canny method to the preprocessing as an option. Might be useful to be able to call on it if the first method fails.
    # maybe first try without canny, then automatically with canny if the previous one fails and only then return an error to the user.
    def __init__(self):
        """Initializes an instance of Affine."""
        self.path = os.path.dirname(__file__) + os.path.sep
        self.result = dict()
        self.A = None  # Affine transformation matrix
        self.internal_img = None  # Internal image
        self.internal_mask = None  # Internal mask
        self.MIN_MATCHES = 4
        self.preprocessor = Preprocessor()
        self.io = Affine_IO(self.path)

    def draw_keypoints(self):
        """
        Uses skimage's standard plot_matches to visualize matched keypoints.
        
        Returns:
            Matplotlib figure showing matches.
        """
        if self.result.get("img") is None or self.result.get("mask") is None:
            raise AffineError("No affine transformation found.", 4)


        img = self.result["img"]
        mask = self.result["mask"]
        print(f"Not implemented.")

        return img, mask


    # tunable parameters: max_ratio, cross_check, min_matches
    def try_match(
        self,
        img: np.ndarray,
    ) -> bool:
        """
        Attempts to find the affine transformation between the input image and
        mask using SIFT keypoints and descriptors.

        Args:
            img (np.ndarray): Input image to match with the mask.
        Raises:
            - AffineError: something bad has taken place
        """
        max_ratio = 0.75
        cross_check = True
        mask = self.internal_mask
        if img is None:
            # ok so this should be caught in the GUI already.
            raise AffineError("No image provided.", 1)
        if mask is None:
            raise AffineError("No mask loaded.", 2)
        img = self.preprocessor.preprocess_img(img)
        mask = self.preprocessor.preprocess_mask(mask)
        self.result["img"] = img
        self.result["mask"] = mask

        # Detect keypoints and compute descriptors
        try:
            sift = SIFT()
            sift.detect_and_extract(img)
            kp_img, desc_img = sift.keypoints, sift.descriptors

            sift.detect_and_extract(mask)
            kp_mask, desc_mask = sift.keypoints, sift.descriptors
        except RuntimeError as e:
            raise AffineError(f"Runtime error during SIFT detection: {e}", 3) from e
        
        self.result["kp1"] = kp_mask
        self.result["kp2"] = kp_img

        # Match descriptors, lowes ratio test. 0.75?
        matches = match_descriptors(desc_mask, desc_img, max_ratio=max_ratio, cross_check=cross_check)

        if len(matches) < self.MIN_MATCHES:
            raise AffineError(
                f"Not enough matches found: {len(matches)} < {self.MIN_MATCHES}", 3
            )

        # estimate affine transformation with ransac
        # OH MAN I LOVE COORDINATE SYSTEMS :)))
        if kp_mask is None or kp_img is None:
            raise AffineError("No keypoints found in either image or mask.", 3)
        src = kp_mask[matches[:, 0]][:, ::-1].astype(np.float32)  # mask keypoints
        dst = kp_img[matches[:, 1]][:, ::-1].astype(np.float32)  # image keypoints

        model, inliers = self.get_transformation(src, dst)


        # Populate the class variables when a transformation is found.
        self.A = model.params


        self.result["img"] = img
        self.result["mask"] = mask
        self.result["kp1"] = kp_mask
        self.result["kp2"] = kp_img
        self.result["matches"] = matches
        self.result["transform"] = model
        return True

    def get_transformation(self, src, dst) -> np.ndarray:
        # NOTE: This is using SimilarityTransform, which accounts for rotation, translation, and scaling but not perspective changes.
        # easy to change, but I think its reasonable to assume that the camera is situated directly above the img.
        model, inliers = ski.measure.ransac(
            (src, dst),
            ski.transform.SimilarityTransform,
            residual_threshold=5,  # this can be increased to maybe get more inliers on difficult images, at the cost of accuracy.
            min_samples=self.MIN_MATCHES,  # 4 seems to be a good value for this.
            max_trials=1000,
        )
        if inliers is None:
            raise AffineError("Ransac can't find transform.", 3)
        return model, inliers
    
    def manual_transform(self, src, dst, img, mask):
        """
        Apply an affine transform manually, given points from the mask and image respectively.

        Args:
            src_points (list of (x, y)): Points from the mask.
            dst_points (list of (x, y)): Corresponding points from the image.
        """
        try:
            src = np.array(src, dtype=np.float32)
            dst = np.array(dst, dtype=np.float32)

            model, inliers = self.get_transformation(
                src,
                dst,
            )

            # Populate the class variables when a transformation is found.
            self.A = model.params
            self.result["img"] = img
            self.result["mask"] = mask
            self.result["kp1"] = src
            self.result["kp2"] = dst
            self.result["matches"] = np.array(
                [[i, i] for i in range(len(src))]  # dummy matches to retain the structure
            )

        except Exception as e:
            raise AffineError(
                f"Error during manual transformation: {e}", 3
            ) from e



    def coords(self, point: tuple[float, float]) -> tuple[float, float]:
        """
        Transforms a point from the mask to the corresponding point on the image using the affine transformation.

        Args:
            point (tuple): (x, y) coordinates of the point on the mask.

        Returns:
            tuple: (x, y) coordinates of the transformed point on the image.

        Raises:
            AffineError: If no affine transformation has been found.
        """
        if self.A is None:
            raise AffineError("No affine transformation found.", 4)

        # Turn (x, y) into homogeneous 3x1 column vector because the matrix is 3x3
        point_homogeneous = np.array([point[0], point[1], 1.0])
        transformed = self.A @ point_homogeneous

        return float(transformed[0]), float(transformed[1])

    def update_internal_mask(self, path):
        if path.endswith(".gds"):
            mask, filename = self.io.load_and_save_gds(path)
        else:
            mask, filename = self.io.load_image(path)
        self.mask_filename = filename
        # saves the mask in color 
        self.internal_mask = mask
        self.result.clear()
        return mask


    def center_on_component(self, x: int, y: int):
        """Finds the centroid of a connected component in the mask image based on the color.

        Args:
            x (int):
            y (int):

        Raises:
            AffineError: something bad has taken place

        Returns:
            tuple(int,int): centered coordinates of the selected component.
        """
        if self.internal_mask is None:
            raise AffineError("No internal mask available loaded.", 2)

        mask = self.internal_mask
        if mask.ndim != 3 or mask.shape[2] != 3:
            ski.color.gray2rgb(mask)

        # get target color
        target_color = mask[y, x]

        # mask the image to find the target color
        color_match = np.all(mask == target_color, axis=-1)

        # label connected components of this color
        labeled_mask = ski.measure.label(color_match, connectivity=2)

        # find the label of the clicked pixel
        label_clicked = labeled_mask[y, x]

        # get the properties of the labeled regions and find the centroid for the clicked label
        props = ski.measure.regionprops(labeled_mask)
        for region in props:
            if region.label == label_clicked:
                cy, cx = region.centroid

                return (int(cx), int(cy))
        return (x, y)  # return original coords if no region found
