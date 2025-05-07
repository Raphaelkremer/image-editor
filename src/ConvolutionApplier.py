import numpy as np

from src.ImageProccessor import AppImage


class ConvolutionApplier:
    """
    a class to apply convolution to an image using a kernel.
    """

    def convolve(self, image: AppImage, kernel: np.ndarray) -> np.ndarray:
        if image.is_grayscale:
            return self.convolve_grayscale(image.image_arr, kernel)
        else:
            return self.__convolve_rgb(image.image_arr, kernel)

    def __convolve_rgb(self, image_array: np.ndarray, kernel: np.ndarray)-> np.ndarray:
        kernel_height, kernel_width = kernel.shape
        padding_size_height, padding_size_width = kernel_height // 2, kernel_width // 2
        padded_image = np.pad(image_array, ((padding_size_height, padding_size_height),
                                            (padding_size_width, padding_size_width), (0, 0)), "reflect")
        output_ndarray = np.empty_like(image_array)

        for y in range(image_array.shape[0]):
            for x in range(image_array.shape[1]):
                window = padded_image[y:y + kernel_height, x:x + kernel_width]
                output_ndarray[y, x] = (window * kernel[..., None]).sum(axis=(0, 1))
        return output_ndarray

    def convolve_grayscale(self, image_array: np.ndarray, kernel: np.ndarray)-> np.ndarray:
        kernel_height, kernel_width = kernel.shape
        padding_height, padding_width = kernel_height // 2, kernel_width // 2
        padded_image = np.pad(
            array=image_array,
            pad_width=((padding_height, padding_height), (padding_width, padding_width)),
            mode="reflect"
        )
        output_image = np.empty_like(image_array)
        for y in range(image_array.shape[0]):
            for x in range(image_array.shape[1]):
                window = padded_image[y:y + kernel_height, x:x + kernel_width]
                output_image[y, x] = (window * kernel).sum()
        return output_image
