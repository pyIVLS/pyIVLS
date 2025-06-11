import skimage as ski
import matplotlib.pyplot as plt
from skimage.color.adapt_rgb import adapt_rgb, each_channel, hsv_value
from skimage import filters


@adapt_rgb(each_channel)
def sobel_each(image):
    return filters.sobel(image)



def _preprocess_mask(mask):
        """
        Simple preprocessing for mask.
            Args:
            - mask (np.ndarray): Input mask.

        Returns:
        - mask (np.ndarray): Preprocessed mask.
        """
        @adapt_rgb(each_channel)
        def canny_each(image, sigma):
            return ski.feature.canny(image, sigma=sigma)
        
        if mask.shape[2] == 4:
            mask = mask[:, :, :3]

        sobel = canny_each(mask, sigma=2.0)
        sobel = (sobel * 255).astype('uint8')

        sobel = ski.color.rgb2gray(sobel)
 
        print("Sobel shape:", sobel.shape)

        return sobel

mask = ski.io.imread(r"plugins\Affine\masks\refLED_v3_flat.png")
mask = _preprocess_mask(mask)
plt.imshow(mask, cmap='gray')
plt.axis('off')
plt.show()

