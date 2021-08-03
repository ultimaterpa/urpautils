"""Unit tests for all functions in csv_utils.py file"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
from urpautils import csv_utils


def test_csv_file(tmpdir):
    """Test all functions on one csv file"""
    header = ["this", "is", "header"]
    row = ["this", "is", "a row"]
    path = os.path.join(tmpdir, "test.csv")
    csv_utils.csv_create_file(path, header=header)
    with pytest.raises(FileExistsError):
        assert csv_utils.csv_create_file(path)
    csv_utils.csv_append_row(path, row)
    for index, row_ in enumerate(csv_utils.csv_read_rows(path)):
        if index == 0:
            assert row_ == header
        else:
            assert row_ == row
        assert index < 2
    # read only second row
    for index, row_ in enumerate(csv_utils.csv_read_rows(path, start_row_index=1, end_row_index=1)):
        assert row_ == row
        assert not index
