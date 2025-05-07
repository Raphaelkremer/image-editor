from Operations import (
    Brightness, Contrast, Saturation,  # <- your concrete classes
    Sharpen, SobelEdge, BoxBlur,
)
from Operations import Operation  # the ABC
from src.BaseException import ExceptionWithErrorMessage


class OperationFactory:

    @staticmethod
    def build(operation_dict) -> Operation:
        """
        Build an operation object from a dictionary.
        Responsible for making the Operations polymorphic and open
        for extension.
        """
        operation_type = operation_dict.get("type")
        if operation_type == BoxBlur.operation_name():
            return BoxBlur(operation_dict)
        elif operation_type == SobelEdge.operation_name():
            return SobelEdge(operation_dict)
        elif operation_type == Brightness.operation_name():
            return Brightness(operation_dict)
        elif operation_type == Contrast.operation_name():
            return Contrast(operation_dict)
        elif operation_type == Saturation.operation_name():
            return Saturation(operation_dict)
        elif operation_type == Sharpen.operation_name():
            return Sharpen(operation_dict)
        raise OperationFactoryException("Undefined operation type: " + operation_type)


class OperationFactoryException(ExceptionWithErrorMessage):
    def __init__(self, error_msg: str):
        super().__init__(error_msg)
        self.error_msg = error_msg
