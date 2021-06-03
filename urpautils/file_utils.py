"""Module containing universal functions for file operations that can be used with urpa robots"""

import logging
import os
import shutil
import time

from typing import Optional
from urpautils.universal import timestamp

logger = logging.getLogger(__name__)


def remove_dir(path: str) -> None:
    """Tries to remove a directory

    :param path:    path
    :return:        None
    """
    try:
        if os.path.isdir(path):
            logger.info(f"Removing directory '{path}'")
            shutil.rmtree(path)
    except PermissionError:
        logger.warning(f"Unable to remove direcotry '{path}'")


def remove(path: str) -> None:
    """Removes a file

    :param path:    path
    :return:        None
    """
    if os.path.isfile(path):
        os.remove(path)


def move(file_path: str, destination: str) -> None:
    """Moves a file

    :param file_path:    path
    :param destination:  destination path
    :return:             None
    """
    if os.path.isfile(file_path):
        shutil.move(file_path, destination)


def copy(src: str, dest: str) -> None:
    """Copies a file

    :param src:   source path
    :param dest:  destination path
    :return: None
    """
    try:
        shutil.copyfile(src, dest)
    except PermissionError:
        logger.warning(f"Unable to copy '{src}' into '{dest}'")


def remove_files_older_than(dir_path: str, days: int) -> None:
    """Removes all files in a directory that are older than 'days' days

    :param dir_path:     path
    :param days:         number of days
    :return:             None
    """
    files = os.listdir(dir_path)
    for file in files:
        file_path = os.path.join(dir_path, file)
        if os.path.isfile(file_path):
            # file age in seconds
            file_age = time.time() - os.stat(file_path).st_mtime
            # file age in days
            file_age /= 86400
            if file_age > days:
                logger.info(f"Removing '{file_path}' because it is older than '{days}' days")
                remove(file_path)


def write_txt_file(file_name: str, content: str, mode: str = "w") -> None:
    """Writes a text file

    :param file_name:    path
    :param content:      string to write
    :param mode:         mode of writing (writing, appending, ...)
    :return:             None
    """
    # maybe TODO: expand this function so it works with all kinds of files, not just text? e.g. binary etc.
    possible_modes = ("w", "a", "w+", "a+")
    if not mode in possible_modes:
        raise ValueError(f"Invalid write mode '{mode}'. Please use on of the following: '{possible_modes}'")
    with open(file_name, mode) as txt_file:
        txt_file.write(content)


def read_txt_file(file_name: str) -> Optional[str]:
    """Reads a text file

    :param file_name:    path
    :return:             str content
    """
    # maybe TODO: expand this function so it works with all kinds of files, not just text? e.g. binary etc.
    if not os.path.isfile(file_name):
        return None
    with open(file_name, "r") as txt_file:
        return txt_file.read()


class Helper:
    """Class for reading and writing helper text files"""

    def __init__(self, file_name: str) -> None:
        """Init. Creates file if it does not exist

        :param file_name:      file name
        """
        self.file_name = file_name
        if not os.path.isfile(file_name):
            logger.info(f"Creating '{file_name}' file")
            self.write(0)

    def get(self) -> int:
        """Reads the file and returns its content as integer

        :return:    int
        """
        with open(self.file_name) as helper_file:
            return int(helper_file.read())

    def write(self, value: int) -> None:
        """Writes integer 'value' to the file

        :param value:    integer
        :return:         None
        """
        if not isinstance(value, int):
            logger.error(f"Value '{value}' is not an integer")
            raise ValueError(f"Value '{value}' is not an integer")
        with open(self.file_name, "w") as helper_file:
            helper_file.write(str(value))

    def increment(self, increment: int = 1) -> int:
        """Increments number in file by 'increment'

        :param increment:    how much to increment by
        :return:             number after incrementing
        """
        new_value = self.get() + increment
        self.write(new_value)
        return new_value

    def delete(self) -> None:
        """Removes the file

        :return:       None
        """
        os.remove(self.file_name)


def archive_file(
    source_file: str,
    destination_path: str,
    use_timestamp_prefix: bool = True,
    timestamp_format: str = "%Y-%m-%d_",
    force_rewrite: bool = False,
) -> str:
    """Moves 'source_file' to 'destination_path' and if selected adds timestamp prefix to its name

    :param source_file:            path to file
    :param destination_path:       path to directory
    :param use_timestamp_prefix:   bool - add timestamp to the file name
    :param timestamp_format:       format of the timestamp prefix
    :param force_rewrite:          bool - if destination file already exists it is rewriten if True
    :return:                       string - path to the new file
    """
    if not os.path.isfile(source_file):
        raise FileNotFoundError(f"File '{source_file}' does not exist")

    file_name = os.path.basename(source_file)
    if use_timestamp_prefix:
        file_name = f"{timestamp(timestamp_format)}{file_name}"
    output_file_path = os.path.join(destination_path, file_name)

    if os.path.isfile(output_file_path):
        if force_rewrite:
            logger.info(f"Rewriting file '{output_file_path}'")
        else:
            raise FileExistsError(
                f"Cannot write file '{output_file_path}' because it already exists. If you want to rewrite it use 'force_rewrite = True'"
            )

    move(source_file, output_file_path)
