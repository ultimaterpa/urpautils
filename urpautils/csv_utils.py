"""Module containing universal functions for csv files manipulation that can be used with urpa robots"""

import csv
import logging
import os
import sys

from itertools import islice
from typing import Optional, Iterable, Generator

logger = logging.getLogger(__name__)


def csv_append_row(
    file_path: str, row: Iterable, newline: str = "", encoding: str = "utf-8-sig", delimiter: str = ";"
) -> None:
    """Appends a row to an existing csv file.

    :param file_path:    path
    :param row:          iterable of columns in one row
    :param newline:      newline character
    :param encoding:     encoding of the csv file
    :param delimiter:    csv delimiter
    :return:             None
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File '{file_path}' does not exist")
    with open(file_path, "a", newline=newline, encoding=encoding) as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=delimiter)
        csv_writer.writerow(row)


def csv_create_file(
    file_path: str,
    header: Optional[Iterable] = None,
    newline: str = "",
    encoding: str = "utf-8-sig",
    delimiter: str = ";",
) -> None:
    """Creates new csv file and writes its header if provided

    :param file_path:     path
    :param header:        optional iterable of columns to write as a header
    :param newline:       newline character
    :param encoding:      encoding of the csv file
    :param delimiter:     csv delimiter
    return None
    """
    if os.path.isfile(file_path):
        raise FileExistsError(f"File '{file_path}' already exists")
    if header:
        try:
            iter(header)
        except TypeError as err:
            logger.error(f"'header' must be an iterable, not '{type(header)}'")
            raise err
    with open(file_path, "w", newline=newline, encoding=encoding) as csv_file:
        if header:
            csv_writer = csv.writer(csv_file, delimiter=delimiter)
            csv_writer.writerow(header)


def csv_read_rows(
    file_path: str,
    start_row_index: int = 0,
    end_row_index: int = sys.maxsize,
    newline: str = "",
    encoding: str = "utf-8-sig",
    delimiter: str = ";",
) -> Generator[list, None, None]:
    """Generates rows of a csv file.
    If start_row_index is provided it starts generating from that row index
    If end_row_index is provided it stops generating at that index
    If no start_row_index and end_row_index is provided it yields all rows

    :param file_path:     path
    :param row_index:     index of the row to return
    :return:              list of columns in the row
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File '{file_path}' does not exist")
    with open(file_path, newline=newline, encoding=encoding) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=delimiter)
        for row in islice(csv_reader, start_row_index, end_row_index):
            yield row
