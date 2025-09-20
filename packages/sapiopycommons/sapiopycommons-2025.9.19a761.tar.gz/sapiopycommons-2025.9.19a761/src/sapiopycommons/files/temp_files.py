import os
import shutil
import tempfile
from typing import Callable


# FR-47422: Created class.
class TempFileHandler:
    """
    A utility class to manage temporary files and directories.
    """
    directories: list[str]
    files: list[str]

    def __init__(self) -> None:
        self.directories = []
        self.files = []

    def create_temp_directory(self) -> str:
        """
        Create a temporary directory.

        :return: The path to a newly created temporary directory.
        """
        directory: str = tempfile.mkdtemp()
        self.directories.append(directory)
        return directory

    def create_temp_file(self, data: str | bytes, suffix: str = "") -> str:
        """
        Create a temporary file with the specified data and optional suffix.

        :param data: The data to write to the temporary file.
        :param suffix: An optional suffix for the temporary file.
        :return: The path to a newly created temporary file containing the provided data.
        """
        mode: str = 'w' if isinstance(data, str) else 'wb'
        with tempfile.NamedTemporaryFile(mode=mode, suffix=suffix, delete=False) as tmp_file:
            tmp_file.write(data)
            file_path: str = tmp_file.name
            self.files.append(file_path)
        return file_path

    def create_temp_file_from_func(self, func: Callable, is_binary: bool = True, suffix: str = "", **kwargs) -> str:
        """
        Create a temporary file and populate it using the provided function. The function should accept parameters as
        specified in the `params` dictionary. Any parameter in `params` with the value "<NEW_FILE>" will be replaced
        with the path of the created temporary file.

        :param func: The function to call with the temporary file path that will populate the file.
        :param is_binary: Whether to open the temporary file in binary mode.
        :param suffix: An optional suffix for the temporary file.
        :param kwargs: Keyword arguments to pass to the function. Use "<NEW_FILE>" as a value to indicate where the
            temporary file path should be inserted.
        :return: The path to the newly created temporary file.
        """
        mode: str = 'wb' if is_binary else 'w'
        with tempfile.NamedTemporaryFile(mode, suffix=suffix, delete=False) as tmp_file:
            file_path: str = tmp_file.name
            for key, value in kwargs.items():
                if value == "<NEW_FILE>":
                    kwargs[key] = file_path
            func(**kwargs)
            self.files.append(file_path)
        return file_path

    def cleanup(self) -> None:
        """
        Delete all temporary files and directories created by this handler.
        """
        for directory in self.directories:
            if os.path.exists(directory):
                shutil.rmtree(directory)
        self.directories.clear()

        for file_path in self.files:
            if os.path.exists(file_path):
                os.remove(file_path)
        self.files.clear()
