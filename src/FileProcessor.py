import json
import os

from Operations import Operation
from ProcessedRequest import ProcessedRequest
from src.BaseException import ExceptionWithErrorMessage
from src.OperationFactory import OperationFactory


class FileProcessorException(ExceptionWithErrorMessage):

    def __init__(self, error_msg: str):
        super().__init__(error_msg)
        self.error_msg = error_msg


class FileProcessor:
    """
    Reads & validates the JSON configuration file and returns ProcessRequest object,
    which is simpler to use in the main program.
    """

    __OPERATIONS_LIST_ERROR = "`operations` must be a list."
    __DISPLAY_OR_SAVE_ERROR = "Config must specify at least one of `output` or `display = true`."
    __INPUT_FILE_ERROR = "`input` must be an existing image file path of the correct type."
    __FILE_NOT_FOUND_ERROR = "Config file not found"
    __FILE_READ_ERROR = "Error reading file: {}"
    __INVALID_JSON_ERROR = "Invalid JSON"
    __INVALID_JSON_ERROR_MSG = "Invalid JSON"
    __INVALID_INPUT_FILE_ERROR = "`input` must be an existing image file path of the correct type."

    __FILE_ENDING = ('.png', '.jpg', '.jpeg')


    def process_json_file(self, path: str)-> ProcessedRequest:
        """
        Reads the JSON configuration file, validates it and its structure,
        and returns a ProcessedRequest object.
        :param path:
        :return:
        """
        self.__check_if_file_path_is_valid(path)
        data = self.__get_json_data_from_file(path)

        input_path = data.get("input")
        self.__validate_input_file_name_and_existence(input_path)
        output_path = data.get("output", "")
        if output_path == "":
            to_save = False
        else:
            to_save = True
        display = bool(data.get("display", False))

        self.check_if_display_or_save(display, to_save)

        raw_operations = self.check_if_operations_are_list_and_return_list(data)

        operations = self.parse_operations(raw_operations)

        return ProcessedRequest(
            input_image_path=os.path.abspath(input_path),
            output_image_path=os.path.abspath(output_path) if to_save else "",
            to_save=to_save,
            display=display,
            operations=operations,
        )

    @staticmethod
    def parse_operations(raw_operations: list[dict]) -> list[Operation]:
        operations = []
        for idx, operation_dict in enumerate(raw_operations):
            operation = OperationFactory.build(operation_dict)
            operations.append(operation)
        return operations

    def check_if_operations_are_list_and_return_list(self, data)-> list:
        raw_operations = data.get("operations", [])
        if not isinstance(raw_operations, list):
            raise FileProcessorException(self.__OPERATIONS_LIST_ERROR)
        return raw_operations

    def check_if_display_or_save(self, display, to_save: bool):
        if not to_save and not display:
            raise FileProcessorException(self.__DISPLAY_OR_SAVE_ERROR)

    def __check_if_file_path_is_valid(self, path):
        if not os.path.isfile(path):
            raise FileProcessorException(self.__INPUT_FILE_ERROR)

    def __get_json_data_from_file(self, path) -> dict:
        try:
            with open(path, "r", encoding="utf-8") as fp:
                return json.load(fp)
        except OSError:
            raise FileProcessorException(self.__FILE_READ_ERROR)
        except json.JSONDecodeError as e:
            raise FileProcessorException(self.__INVALID_JSON_ERROR)

    def __validate_input_file_name_and_existence(self, input_path):
        if (
                not input_path or
                not os.path.isfile(input_path) or
                not input_path.lower().endswith(self.__FILE_ENDING)
        ):
            raise FileProcessorException(self.__INVALID_INPUT_FILE_ERROR)
