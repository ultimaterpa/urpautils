"""Unit tests for all functions in csv_utils.py file"""

import os

import pytest

from urpautils import csv_read_rows, csv_create_file, csv_append_row


def test_csv_file(tmpdir):
    """Test all functions on one csv file"""
    header = ["this", "is", "header"]
    row = ["this", "is", "a row"]
    path = os.path.join(tmpdir, "test.csv")
    csv_create_file(path, header=header)
    with pytest.raises(FileExistsError):
        assert csv_create_file(path)
    csv_append_row(path, row)
    for index, row_ in enumerate(csv_read_rows(path)):
        if index == 0:
            assert row_ == header
        else:
            assert row_ == row
        assert index < 2
    # read only second row
    for index, row_ in enumerate(csv_read_rows(path, start_row_index=1, end_row_index=1)):
        assert row_ == row
        assert not index
