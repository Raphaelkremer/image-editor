import argparse

from src.BaseException import ExceptionWithErrorMessage


class ArgsParser:

    __CONFIG_ARG_NAME = "config"
    __CONFIG_ARG = "--" + __CONFIG_ARG_NAME

    def __init__(self):
        self.__parser = argparse.ArgumentParser()
        self.__parser.add_argument(self.__CONFIG_ARG, required=True, )

    def parse_args(self, argv) -> str:
        try:
            arguments_namespace = self.__parser.parse_args(argv)
            path = arguments_namespace.config
            return path

        except (argparse.ArgumentError, SystemExit) as e:
            raise ArgsError("Invalid command‑line arguments.")
        except AttributeError as e:
            raise ArgsError("Config argument not found.")


class ArgsError(ExceptionWithErrorMessage):
    def __init__(self, error_msg: str):
        super().__init__(error_msg)
        self.error_msg = error_msg
