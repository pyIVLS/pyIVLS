import os
from datetime import datetime
import cv2 as cv
import numpy as np
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
    """Calculates the affine transformation between two images using SIFT keypoints and descriptors (OpenCV only).
    Assumes the images are grayscale.
    Usage:
    - Create an Affine object.
    - Load the mask image using update_interal_mask().
    - Call try_match() with the input image and mask.
    - If the transformation is found, access the transformation matrix using the A attribute.
    - When transformation is found, use coords() to get the transformed coordinates of a point.
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

    @staticmethod
    def _preprocess_img(img):
        """
        Simple preprocessing for img.
            Args:
            - img (np.ndarray): Input image.

            Returns:
            - img (np.ndarray): Preprocessed image.
        """
        if img.shape[2] == 4:
            img = img[:, :, :3]
        if len(img.shape) == 3:  # Check if the image is not grayscale
            img = cv.cvtColor(img, cv.COLOR_RGB2GRAY)
        # blur
        img = cv.GaussianBlur(img, (5, 5), 0)

        return img

    @staticmethod
    def _preprocess_mask(mask):
            """
            Simple preprocessing for mask.
                Args:
                - mask (np.ndarray): Input mask.

            Returns:
            - mask (np.ndarray): Preprocessed mask.
            """
            if mask.shape[2] == 4:
                mask = mask[:, :, :3]

            if len(mask.shape) == 3:  # Check if the mask is not grayscale
                mask = cv.cvtColor(mask, cv.COLOR_RGB2GRAY)
            # blur 
            mask = cv.GaussianBlur(mask, (5, 5), 0)
            
            return mask




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

        kp1 = self.result.get("kp1") # row, col mask points
        kp2 = self.result.get("kp2") # row, col img points

        if img.ndim == 2:
            img = cv.cvtColor(img, cv.COLOR_GRAY2RGB)
        if mask.ndim == 2:
            mask = cv.cvtColor(mask, cv.COLOR_GRAY2RGB)


        # Return the images with keypoints drawn
        img = cv.drawKeypoints(img, kp2, None, color=(255, 0, 0))
        mask = cv.drawKeypoints(mask, kp1, None, color=(0, 255, 0))


        return img, mask


    def try_match(
        self,
        img: np.ndarray,
    ) -> bool:
        """
        Attempts to find the affine transformation between the input image and
        mask using SIFT keypoints and descriptors.
        """
        mask = self.internal_mask
        if img is None:
            raise AffineError("No image provided.", 1)
        if mask is None:
            raise AffineError("No mask loaded.", 2)
        img = self._preprocess_img(img)
        mask = self._preprocess_mask(mask)
        self.result["img"] = img
        self.result["mask"] = mask
        try:
            sift = cv.SIFT_create()
            kp_img, desc_img = sift.detectAndCompute(img, None)
            kp_mask, desc_mask = sift.detectAndCompute(mask, None)
        except Exception as e:
            raise AffineError(f"Error during SIFT detection: {e}", 3) from e
        self.result["kp1"] = kp_mask
        self.result["kp2"] = kp_img

        if desc_mask is not None and desc_img is not None:
            if len(desc_mask) <= 2 and len(desc_img) <= 2:
                raise AffineError(
                    f"Not enough keypoints found: {len(desc_mask)} in mask, {len(desc_img)} in image. Minimum required: {self.MIN_MATCHES}", 3
                )

        

        bf = cv.BFMatcher(cv.NORM_L2)
        matches = bf.knnMatch(desc_mask, desc_img, k=2)
        good_matches = []
        for m, n in matches:
            if m.distance < 0.75 * n.distance:  # stricter ratio for fewer false positives
                good_matches.append(m)
        if len(good_matches) < self.MIN_MATCHES:
            raise AffineError(
                f"Not enough matches found: {len(good_matches)} < {self.MIN_MATCHES}", 3
            )
        # OpenCV keypoints: pt is (x, y) = (col, row)
        src_pts = np.float32([kp_mask[m.queryIdx].pt for m in good_matches]).reshape(-1, 2)
        dst_pts = np.float32([kp_img[m.trainIdx].pt for m in good_matches]).reshape(-1, 2)
        # src_pts: mask (reference), dst_pts: img (target)
        model, inliers = cv.estimateAffinePartial2D(src_pts, dst_pts, method=cv.RANSAC, ransacReprojThreshold=5, maxIters=2000)
        if model is None:
            raise AffineError("RANSAC can't find transform.", 3)
        A = np.eye(3)
        A[:2, :] = model
        self.A = A
        self.result["matches"] = good_matches
        self.result["transform"] = model
        return True

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

            model, inliers = cv.estimateAffinePartial2D(src, dst, method=cv.RANSAC, ransacReprojThreshold=5, maxIters=1000)
            if model is None:
                raise AffineError("RANSAC can't find transform.", 3)
            A = np.eye(3)
            A[:2, :] = model
            self.A = A
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
        # Ensure input is (x, y)
        x, y = point
        point_homogeneous = np.array([x, y, 1.0])
        transformed = self.A @ point_homogeneous
        return float(transformed[0]), float(transformed[1])

    def update_interal_mask(self, path):
        if path.endswith(".gds"):
            mask, filename = self._load_and_save_gds(path)
        else:
            mask, filename = self._load_image(path)
        self.mask_filename = filename
        self.internal_mask = mask
        self.result.clear()
        return mask

    def _load_and_save_gds(self, input_gds_path, output_image_path=None, width=1920, height=1080):
        filename = os.path.basename(input_gds_path)
        filename = filename.split(".")[0]
        if output_image_path is None:
            output_image_path = (
                self.path + os.sep + "masks" + os.sep + filename + ".png"
            )
        view = lay.LayoutView(options=lay.LayoutView.LV_NoGrid)
        lay.LayoutViewBase.LV_NoEditorOptionsPanel
        view.load_layout(input_gds_path, add_cellview=False)
        view.zoom_fit()
        view.max_hier()
        i = 0
        it = view.begin_layers()
        while not it.at_end():
            lp = it.current()
            new_layer = lp.dup()
            new_layer.visible = True
            if i == 0 or i == 1:
                new_layer.clear_dither_pattern()
                new_layer.dither_pattern = 0
            else:
                new_layer.clear_dither_pattern()
                new_layer.dither_pattern = 1

            view.set_layer_properties(it, new_layer)
            i += 1
            it.next()
        view.save_image(output_image_path, width, height)
        internal_mask = cv.imread(output_image_path)
        internal_mask = cv.cvtColor(internal_mask, cv.COLOR_BGR2RGB)
        return internal_mask, filename

    def _load_image(self, path: str):
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
        self.internal_mask = img
        return img, filename

    def test_image(self) -> np.ndarray:
        """
        Loads an test image.
        """
        img = cv.imread(r"plugins\Affine\testImages\testData2.png")
        if img is None:
            raise AffineError("Could not load test image.", 5)
        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
 
        return img

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
            mask = cv.cvtColor(mask, cv.COLOR_GRAY2RGB)

        # get target color
        target_color = mask[y, x]

        # mask the image to find the target color
        color_match = np.all(mask == target_color, axis=-1)

        num_labels, labeled_mask = cv.connectedComponents(color_match.astype(np.uint8))

        props = []
        for label in range(1, num_labels):
            ys, xs = np.where(labeled_mask == label)
            if len(xs) > 0 and len(ys) > 0:
                cx = int(np.mean(xs))
                cy = int(np.mean(ys))
                props.append((label, (cx, cy)))

        label_clicked = labeled_mask[y, x]
        for label, (cx, cy) in props:
            if label == label_clicked:
                return (cx, cy)
        return (x, y)  # return original coords if no region found
