import imageio.v2 as imageio
import numpy as np

from src.ProcessedRequest import ProcessedRequest


class AppImage:
    """
    This class is used to represent an image and wrap it
    with the grayscale information for operations optimizations.
    """

    def __init__(self, image_arr: np.ndarray, is_grayscale: bool):
        self.image_arr = image_arr
        self.is_grayscale = is_grayscale


class ImageProcessor:
    """
    This class is responsible for applying the different
    operations to the image.
    It takes the AppImage object and applies the operations
    to the ndarray of the image.
    """


    def process(self, request: ProcessedRequest) -> np.ndarray:
        image = self.__load_image(request.input_image_path)
        for operation in request.operations:
            temp = operation.apply_operation(image)
            image.image_arr = temp

        return image.image_arr

    def __load_image(self, path: str) -> AppImage:
        is_grayscale = False
        image_arr = imageio.imread(path).astype(np.float32) / 255.0
        if image_arr.ndim == 2:
            is_grayscale = True

        return AppImage(image_arr, is_grayscale)
