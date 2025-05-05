# core/io.py

import numpy as np
import imageio.v3 as iio



# CONSTANTS

# Padding mode used by every convolution
PAD_MODE = "reflect"

# RGB → Grayscale luminance weights (ITU‑R BT.601)
RGB2GRAY_WEIGHTS = (0.299, 0.587, 0.114)

# Sobel derivative kernels
SOBEL_GX = np.array(
    [[-1, 0, 1],
     [-2, 0, 2],
     [-1, 0, 1]], dtype=np.float32)

SOBEL_GY = np.array(
    [[-1, -2, -1],
     [ 0,  0,  0],
     [ 1,  2,  1]], dtype=np.float32)

# Default box‑blur kernel sizes
DEFAULT_BLUR_W = 7   # horizontal
DEFAULT_BLUR_H = 7   # vertical

# Unsharp‑mask radius
SHARPEN_RADIUS = 2

# Numerical safety value to avoid divide‑by‑zero
EPS = 1e-8

# Valid pixel range after processing
PIXEL_MIN = 0.0
PIXEL_MAX = 1.0






"""
the following part is used to save and load the images in the format of numPy's ndarray
"""


def load(path: str):
    arr = iio.imread(path).astype(np.float32) / 255.0
    if arr.ndim == 2:
        arr = np.repeat(arr[..., None], 3, axis=2)
    return arr


def save(path: str, img: np.ndarray):
    img_uint8 = np.clip(img * 255, 0, 255).astype(np.uint8)
    iio.imwrite(path, img_uint8)



"""
the convolution function
"""


def convolve(img: np.ndarray, kernel: np.ndarray):
    kh, kw = kernel.shape
    ph, pw = kh // 2, kw // 2
    padded = np.pad(img, ((ph, ph), (pw, pw), (0, 0)), PAD_MODE)
    out = np.empty_like(img)

    for y in range(img.shape[0]):
        for x in range(img.shape[1]):
            window = padded[y:y+kh, x:x+kw]
            out[y, x] = (window * kernel[..., None]).sum(axis=(0, 1))  # TODO: understand that line
    return out




"""
the blurring function
"""


def box_blur(img: np.ndarray, x: int = DEFAULT_BLUR_W, y: int = DEFAULT_BLUR_H):
    if x % 2 == 0:
        x += 1
    if y % 2 == 0:
        y += 1
    kernel = np.ones((x, y), np.float32) / (x * y)
    return convolve(img, kernel)


def convolve_grayscale(img: np.ndarray, kernel: np.ndarray):
    kh, kw = kernel.shape
    ph, pw = kh // 2, kw // 2
    padded = np.pad(img, ((ph, ph), (pw, pw)), mode=PAD_MODE)
    out = np.empty_like(img)
    for y in range(img.shape[0]):
        for x in range(img.shape[1]):
            patch = padded[y:y + kh, x:x + kw]
            out[y, x] = (patch * kernel).sum()
    return out


"""
helper to convert the image to grayscale for the sobel filter
"""
def rgb_to_gray(img: np.ndarray):
    r, g, b = RGB2GRAY_WEIGHTS
    return r*img[...,0] + g*img[...,1] + b*img[...,2]



def sobel_edge(img):

    gx = SOBEL_GX
    gy = SOBEL_GY

    gray = rgb_to_gray(img)

    ix = convolve_grayscale(gray, gx)
    iy = convolve_grayscale(gray, gy)

    mag = np.hypot(ix, iy)              # sqrt(Ix**2 + Iy**2) – stable

    mag /= (mag.max() + EPS)            # 1e‑8 prevents divide‑by‑0

    return np.repeat(mag[..., None], 3, axis=2)


def sharpen(img: np.ndarray, alpha: float = 1.0):

    box_size = SHARPEN_RADIUS * 2 + 1
    blurred = box_blur(img, box_size, box_size)

    mask = img - blurred

    sharpened = img + alpha * mask

    return np.clip(sharpened, PIXEL_MIN, PIXEL_MAX)


















