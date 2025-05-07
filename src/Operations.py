from abc import ABC, abstractmethod

import numpy as np

from src.BaseException import ExceptionWithErrorMessage
from src.ConvolutionApplier import ConvolutionApplier
from src.ImageProccessor import AppImage


class Operation(ABC):
    """
    Interface-like class for image processing operations.
    """
    PIXEL_MIN = 0.0
    PIXEL_MAX = 1.0

    convolution_applier = ConvolutionApplier()

    @abstractmethod
    def apply_operation(self, image: AppImage):
        """
        Abstract method to apply the operation to the image.
        """
        pass

    @staticmethod
    @abstractmethod
    def operation_name() -> str:
        """
        Get the name of the operation.
        """
        pass


class BoxBlur(Operation):

    __DEFAULT_BLUR_HEIGHT = 7
    __DEFAULT_BLUR_WIDTH = 7
    __MAX_BLUR_SIZE = 1000

    __PARAMETERS_WITH_WRONG_TYPE_ERROR = "Width and height must be integers."
    __PARAMETERS_WITH_WRONG_VALUE_ERROR = "Width and height must be positive integers."
    __PARAMETERS_WITH_TOO_BIG_SIZE_ERROR = "Width and height must be less than or equal to 1000."

    def __init__(self, params: dict) -> None:
        self.width = params.get("width", self.__DEFAULT_BLUR_WIDTH)
        self.height = params.get("height", self.__DEFAULT_BLUR_HEIGHT)
        self.__validateParam(self.width)
        self.__validateParam(self.height)

    def __validateParam(self, param)-> None:
        if not isinstance(param, int):
            raise OperationError(self.__PARAMETERS_WITH_WRONG_TYPE_ERROR)
        if param <= 0:
            raise OperationError(self.__PARAMETERS_WITH_WRONG_VALUE_ERROR)
        if param > self.__MAX_BLUR_SIZE:
            raise OperationError(self.__PARAMETERS_WITH_TOO_BIG_SIZE_ERROR)

    def apply_operation(self, image: AppImage)-> np.ndarray:
        if self.width % 2 == 0:
            self.width += 1
        if self.height % 2 == 0:
            self.height += 1

        kernel = np.ones((self.width, self.height), np.float32) / (self.width * self.height)
        return self.convolution_applier.convolve(image, kernel)

    @staticmethod
    def operation_name() -> str:
        return "box"


class SobelEdge(Operation):
    __SOBEL_GX = np.array(
        [[-1, 0, 1],
         [-2, 0, 2],
         [-1, 0, 1]], dtype=np.float32)

    __SOBEL_GY = np.array(
        [[-1, -2, -1],
         [0, 0, 0],
         [1, 2, 1]], dtype=np.float32)

    NORMALIZATION_EPSILON = 1e-8

    __RGB2GRAY_WEIGHTS = (0.299, 0.587, 0.114)

    def __init__(self, params: dict):
        # No parameters needed for Sobel
        pass

    def apply_operation(self, image: AppImage) -> np.ndarray:
        grayscale_image = image.image_arr if image.is_grayscale else self.__rgb_to_gray(image.image_arr)

        gradient_x = self.convolution_applier.convolve_grayscale(grayscale_image, self.__SOBEL_GX)
        gradient_y = self.convolution_applier.convolve_grayscale(grayscale_image, self.__SOBEL_GY)

        gradient_magnitude = np.hypot(gradient_x, gradient_y)  # sqrt(Ix**2 + Iy**2) – stable

        gradient_magnitude /= (gradient_magnitude.max() + self.NORMALIZATION_EPSILON)

        image.is_grayscale = True

        return gradient_magnitude

    @staticmethod
    def operation_name() -> str:
        return "sobel"

    def __rgb_to_gray(self, image_array: np.ndarray) -> np.ndarray:
        r, g, b = self.__RGB2GRAY_WEIGHTS
        return r * image_array[..., 0] + g * image_array[..., 1] + b * image_array[..., 2]


class Sharpen(Operation):
    __BLURRING_KERNEL_SIZE = 2 * 2 + 1
    __DEFAULT_SHARPEN_FACTOR = 1.0

    __BOX_BLUR_WIDTH_KEY = "width"
    __BOX_BLUR_HEIGHT_KEY = "height"

    __ALPHA_TYPE_ERROR = "Alpha must be a float or int."
    __ALPHA_VALUE_ERROR = "Alpha must be a positive number."
    __ALPHA_VALUE_TOO_BIG_ERROR = "Alpha must be less than or equal to 10."

    def __init__(self, params: dict)-> None:
        self.sharp_factor = params.get("value", self.__DEFAULT_SHARPEN_FACTOR)
        self.validate_param()

    def validate_param(self):
        if not isinstance(self.sharp_factor, float) and not isinstance(self.sharp_factor, int):
            raise OperationError(self.__ALPHA_TYPE_ERROR)
        if self.sharp_factor < 0:
            raise OperationError(self.__ALPHA_VALUE_ERROR)
        if self.sharp_factor > 10:
            raise OperationError(self.__ALPHA_VALUE_TOO_BIG_ERROR)

    def apply_operation(self, image: AppImage) -> np.ndarray:
        blurring_object = BoxBlur({self.__BOX_BLUR_WIDTH_KEY: self.__BLURRING_KERNEL_SIZE,
                                   self.__BOX_BLUR_HEIGHT_KEY: self.__BLURRING_KERNEL_SIZE})

        blurred_image = blurring_object.apply_operation(image)

        detailed_image = image.image_arr - blurred_image

        sharpened_image = image.image_arr + self.sharp_factor * detailed_image

        return np.clip(sharpened_image, self.PIXEL_MIN, self.PIXEL_MAX)

    @staticmethod
    def operation_name() -> str:
        return "sharpen"


class Brightness(Operation):
    __BRIGHTNESS_FACTOR_TYPE_ERROR = "Brightness must be a float or int."
    __BRIGHTNESS_FACTOR_VALUE_ERROR = "Brightness must be between than -1 and 1"

    def __init__(self, params: dict):
        self.brightness_factor = params.get("value")
        self.validate_param()

    def validate_param(self):
        if not isinstance(self.brightness_factor, float) and not isinstance(self.brightness_factor, int):
            raise OperationError(self.__BRIGHTNESS_FACTOR_TYPE_ERROR)
        if self.brightness_factor < -1 or self.brightness_factor > 1:
            raise OperationError(self.__BRIGHTNESS_FACTOR_VALUE_ERROR)

    def apply_operation(self, image: AppImage)-> np.ndarray:
        return np.clip(image.image_arr + self.brightness_factor, self.PIXEL_MIN, self.PIXEL_MAX)

    @staticmethod
    def operation_name() -> str:
        return "brightness"


class Contrast(Operation):
    __MIDPOINT = 0.5

    __CONTRAST_PARAMETER_TYPE_ERROR = "Contrast must be a float or int."

    def __init__(self, params: dict):
        self.gamma_param = params.get("value")
        self.validate_param()

    def validate_param(self):
        if not isinstance(self.gamma_param, float) and not isinstance(self.gamma_param, int):
            raise OperationError(self.__CONTRAST_PARAMETER_TYPE_ERROR)

    def apply_operation(self, image: AppImage) -> np.ndarray:
        return np.clip((image.image_arr - self.__MIDPOINT) *
                       self.gamma_param +
                       self.__MIDPOINT, self.PIXEL_MIN, self.PIXEL_MAX)

    @staticmethod
    def operation_name() -> str:
        return "contrast"


class Saturation(Operation):
    __SATURATION_TYPE_ERR = "Saturation must be a float or int."
    __SATURATION_VALUE_ERR = "Saturation must be non‑negative."

    __RGB2GRAY_WEIGHTS = (0.299, 0.587, 0.114)

    __DEFAULT_SATURATION_FACTOR = 1.0

    def __init__(self, params: dict):

        self.saturation_factor = params.get("value", self.__DEFAULT_SATURATION_FACTOR)
        self.__validate_param()

    def __validate_param(self):
        if not isinstance(self.saturation_factor, float) and not isinstance(self.saturation_factor, int):
            raise OperationError(self.__SATURATION_TYPE_ERR)
        if self.saturation_factor < 0:
            raise OperationError(self.__SATURATION_VALUE_ERR)

    @staticmethod
    def __rgb_to_gray(image: np.ndarray)-> np.ndarray:
        r, g, b = Saturation.__RGB2GRAY_WEIGHTS
        return r * image[..., 0] + g * image[..., 1] + b * image[..., 2]

    def apply_operation(self, image: AppImage) -> np.ndarray:

        grayscale_luminance = self.__rgb_to_gray(image.image_arr)[..., None]

        result = grayscale_luminance + self.saturation_factor * (image.image_arr - grayscale_luminance)

        return np.clip(result, self.PIXEL_MIN, self.PIXEL_MAX)

    @staticmethod
    def operation_name() -> str:
        return "saturation"


class OperationError(ExceptionWithErrorMessage):
    def __init__(self, error_msg: str):
        super().__init__(error_msg)
        self.error_msg = error_msg
