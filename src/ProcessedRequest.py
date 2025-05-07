from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class ProcessedRequest:
    """
    This class is used to represent the processed request
    and wrap it in a convenient way.
    """
    input_image_path: str
    output_image_path: str
    to_save: bool
    display: bool
    operations: List
