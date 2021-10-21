"""Unit tests for all functions in csv_utils.py file"""

import os

import pytest

from urpautils import csv_read_rows, csv_create_file, csv_append_row, Csv_dict_writer


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
    # read row as dict
    for row_ in csv_read_rows(path, as_dict=True):
        assert row_["this"] == "this"
        assert row_["is"] == "is"
        assert row_["header"] == "a row"


def test_csv_dict_writer(tmpdir):
    """Test the Csv_dict_writer class"""
    path = os.path.join(tmpdir, "test.csv")
    dict_writer = Csv_dict_writer(path, ["name", "surname"])
    data = {"name": "ben", "surname": "dover"}
    dict_writer.write(data)
    # first writing creates the file
    assert os.path.isfile(path)
    # change order of keys
    data = {"surname": "litoris", "name": "mike"}
    dict_writer.write(data)
    for i, row_ in enumerate(csv_read_rows(path, as_dict=True)):
        if not i:
            assert row_["name"] == "ben"
            assert row_["surname"] == "dover"
        else:
            assert row_["name"] == "mike"
            assert row_["surname"] == "litoris"
    with pytest.raises(TypeError):
        # data not stored in dictionary
        data = ["hugh", "jass"]
        dict_writer.write(data)
    with pytest.raises(KeyError):
        # data with different keys than what was already written
        data = {"name": "hugh", "middle_name": "G.", "surname": "rection"}
        dict_writer.write(data)
