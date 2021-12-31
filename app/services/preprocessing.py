import cv2
from skimage.feature import hog

from app.core.config import settings


def get_hog_features(
        image,
        orientations=settings.HOG_ORIENTATIONS,
        pixels_per_cell=settings.HOG_PIXELS_PER_CELL,
        cells_per_block=settings.HOG_CELLS_PER_BLOCK,
        transform_sqrt=True,
        block_norm='L2-Hys',
        visualize=True,
        feature_vector=True,
        multichannel=None
):
    hog_desc, hog_image = hog(
        image,
        orientations=orientations,
        pixels_per_cell=pixels_per_cell,
        cells_per_block=cells_per_block,
        transform_sqrt=transform_sqrt,
        block_norm=block_norm,
        visualize=visualize,
        feature_vector=feature_vector,
        multichannel=multichannel
    )
    return hog_desc, hog_image


def enhance_image(image, alpha=settings.IMAGE_ALPHA, beta=settings.IMAGE_BETA):
    enhanced_image = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    return enhanced_image


def convert_to_grayscale(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    return gray_image


def resize_input_hog(image):
    resized_image = cv2.resize(image, (settings.HOG_RESIZE_WIDTH, settings.HOG_RESIZE_HEIGHT))
    return resized_image
