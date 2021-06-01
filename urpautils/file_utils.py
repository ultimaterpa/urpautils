import logging
import os
import shutil
import time

from typing import Optional

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
    :return: None
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
        file_path = os.path.join(dir_path,file)
        if os.path.isfile(file_path):
            # file age in seconds
            file_age = time.time() - os.stat(file_path).st_mtime
            # file age in days
            file_age /= 86400
            if file_age > days:
                logger.info(f"Removing '{file_path}' because it is older than '{days}' days")
                remove(file_path)


def write_txt_file(file_name: str, content: str, mode: str = "a") -> None:
    """Writes a text file

    :param file_name:    path
    :param content:      string to write
    :param mode:         mode of writing
    :return:             None
    """
    with open(file_name, mode) as txt_file:
        txt_file.write(content)


def read_txt_file(file_name: str) -> Optional[str]:
    """Reads a text file

    :param file_name:    path
    :return:             str content
    """
    if not os.path.isfile(file_name):
        return None
    with open(file_name, "r") as txt_file:
        return txt_file.read()