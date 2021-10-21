"""Module containing universal functions for csv files manipulation that can be used with urpa robots"""

import csv
import logging
import os
import sys

from itertools import islice
from typing import Any, List, Optional, Iterable, Generator, Union

logger = logging.getLogger(__name__)


def csv_append_row(
    file_path: str, row: Iterable, newline: str = "", encoding: str = "utf-8", delimiter: str = ";"
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
        if isinstance(row, dict):
            csv_writer = csv.DictWriter(csv_file, delimiter=delimiter, fieldnames=row.keys())  # type: ignore
        else:
            # mypy is retarded. It thinks `csv_writer` already has type `DictWriter` here
            csv_writer = csv.writer(csv_file, delimiter=delimiter)  # type: ignore
        csv_writer.writerow(row)  # type: ignore


def csv_create_file(
    file_path: str,
    header: Optional[Iterable] = None,
    newline: str = "",
    encoding: str = "utf-8",
    delimiter: str = ";",
    sep: Optional[str] = None,
) -> None:
    """Creates new csv file and writes its header if provided

    :param file_path:     path
    :param header:        optional iterable of columns to write as a header
    :param newline:       newline character
    :param encoding:      encoding of the csv file
    :param delimiter:     csv delimiter
    :param sep:           if provided it writes "sep=<separator>" to first line of the file so it opens correctly in Excel
    :return:              None
    """
    if os.path.isfile(file_path):
        raise FileExistsError(f"File '{file_path}' already exists")
    if header:
        # raises TypeError if 'header' is not iterable
        iter(header)

    with open(file_path, "w", newline=newline, encoding=encoding) as csv_file:
        if header:
            csv_writer = csv.writer(csv_file, delimiter=delimiter)
            if sep:
                csv_writer.writerow(f"sep={sep}")
            csv_writer.writerow(header)


def csv_read_rows(
    file_path: str,
    start_row_index: int = 0,
    end_row_index: int = sys.maxsize,
    newline: str = "",
    encoding: str = "utf-8",
    delimiter: str = ";",
    as_dict: bool = False,
) -> Generator[Union[list, dict], None, None]:
    """Generates rows of a csv file.
    If start_row_index is provided it starts generating from that row index
    If end_row_index is provided it stops generating at that index
    If no start_row_index and end_row_index is provided it yields all rows
    Generator yeields rows as list by default. If 'as_dict' is set to True it generates rows as dicts where
    keys are columns of the first row and values are columns of n-th row

    :param file_path:           path
    :param start_row_index:     start index of the rows to yield
    :param end_row_index:       end index of the rows to yield
    :param newline:             newline character
    :param encoding:            encoding of the csv file
    :param delimiter:           csv delimiter
    :param as_dict:             yields rows as lists if False and as dicts if True. If dicts are used
                                keys are columns of the first row and values are columns of n-th row
    :return:                    list of columns in the row
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File '{file_path}' does not exist")
    with open(file_path, newline=newline, encoding=encoding) as csv_file:
        if as_dict:
            csv_reader = csv.DictReader(csv_file, delimiter=delimiter)
            for row in islice(csv_reader, start_row_index, end_row_index):
                yield dict(row)
        else:
            csv_reader = csv.reader(csv_file, delimiter=delimiter)  # type: ignore
            for row in islice(csv_reader, start_row_index, end_row_index):
                yield row


class Csv_dict_writer:
    """Class used for writing multiple dicts with same keys to one csv file"""

    def __init__(
        self, file_path: str, field_names: List[str], newline: str = "", encoding: str = "utf-8", delimiter: str = ";"
    ):
        """[summary]

        Args:
            file_path (str): file path
            field_names (List): list of keys used in desired dict. One key = one column
            newline (str, optional): newline char for the csv file. Defaults to "".
            encoding (str, optional): encoding of the csv file. Defaults to "utf-8".
            delimiter (str, optional): delimiter used in the csv file. Defaults to ";".
        """
        self.file_path = file_path
        self.fieldnames = field_names
        self.newline = newline
        self.encoding = encoding
        self.delimiter = delimiter

    def write(self, data: dict) -> None:
        """Writes row to csv file
        If file does not exist it creates it and writes header based on `data.keys()`.
        This header is then stored via `self.fieldnames` and used for subsequent writes
        because next dictionary can have same keys but in different order and it would mess up the file.

        If file exists it appends to it

        :param data:    dictionary
        :return:        None
        """
        if not isinstance(data, dict):
            raise TypeError("'data' must be type 'dict'")
        if sorted(self.fieldnames) != sorted(data.keys()):
            raise KeyError(f"Keys '{data.keys()}' are not the same as previously defined keys '{self.fieldnames}'")
        mode = "a" if os.path.isfile(self.file_path) else "w"
        with open(self.file_path, mode, newline=self.newline, encoding=self.encoding) as csv_file:
            csv_writer = csv.DictWriter(csv_file, delimiter=self.delimiter, fieldnames=self.fieldnames)
            if mode == "w":
                csv_writer.writeheader()
            csv_writer.writerow(data)
