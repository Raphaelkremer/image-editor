import sys
from pathlib import Path

import imageio as iio
import matplotlib.pyplot as plt
import numpy as np

from ArgsParser import ArgsParser
from FileProcessor import FileProcessor
from src.BaseException import ExceptionWithErrorMessage
from src.ImageProccessor import ImageProcessor


def save(path: str, image_array: np.ndarray) -> None:
    out_path = Path(path)
    parent_dir = out_path.parent
    if not path:
        raise ExceptionWithErrorMessage("Output path is empty.")
    parent_dir.mkdir(parents=True, exist_ok=True)
    img_uint8 = np.clip(image_array, 0.0, 1.0)
    try:
        iio.imwrite(out_path, (img_uint8 * 255).astype(np.uint8))
    except (OSError, ValueError, RuntimeError) as e:
        raise ExceptionWithErrorMessage(f"Failed to save image: {e}") from e


def show_image(processed_image):
    plt.imshow(processed_image, cmap="gray" if processed_image.ndim == 2 else None)
    plt.axis("off")
    plt.show()


def main(argv):
    args_parser = ArgsParser()
    file_processor = FileProcessor()
    image_processor = ImageProcessor()
    try:
        json_configuration_filepath = args_parser.parse_args(argv)
        processed_request = file_processor.process_json_file(json_configuration_filepath)
        processed_image = image_processor.process(processed_request)
        if processed_request.to_save:
            save(processed_request.output_image_path, processed_image)
        if processed_request.display:
            show_image(processed_image)



    except ExceptionWithErrorMessage as e:
        print(e.error_msg)
        return


if __name__ == "__main__":
    main(sys.argv[1:])
