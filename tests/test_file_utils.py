"""Unit tests for all functions in file_utils.py file"""

import os
import sys
import time

import pytest


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../urpautils")
import file_utils, universal


def test_prepare_and_remove_dir(tmpdir):
    """Test for creating and removing a directory"""
    dir_path = os.path.join(tmpdir, "test_dir")
    file_utils.prepare_dir(dir_path)
    assert os.path.isdir(dir_path)
    file_utils.remove_dir(dir_path)
    assert not os.path.isdir(dir_path)


def test_remove(tmpdir):
    """Test for removing a file"""
    path = tmpdir.join("test.txt").strpath
    file_utils.write_txt_file(path, "")
    assert os.path.isfile(path)
    file_utils.remove(path)
    assert not os.path.isfile(path)


def test_move(tmpdir):
    """Test for moving a file"""
    path = tmpdir.join("test.txt").strpath
    file_utils.write_txt_file(path, "")
    assert os.path.isfile(path)
    file_utils.move(path, path + "moved")
    assert not os.path.isfile(path)
    assert os.path.isfile(path + "moved")


def test_copy(tmpdir):
    """Test for copying a file"""
    path = tmpdir.join("test.txt").strpath
    file_utils.write_txt_file(path, "")
    assert os.path.isfile(path)
    file_utils.copy(path, path + "copy")
    assert os.path.isfile(path)
    assert os.path.isfile(path + "copy")


def test_remove_files_older_than(tmpdir):
    """Test for removing files older than X days from a directory"""
    file_path_do_not_remove = tmpdir.join("dont_remove.txt").strpath
    file_path_remove = tmpdir.join("remove.txt").strpath
    file_utils.write_txt_file(file_path_do_not_remove, "")
    file_utils.write_txt_file(file_path_remove, "")
    assert os.path.isfile(file_path_do_not_remove)
    assert os.path.isfile(file_path_remove)
    # fake file modification time
    os.utime(file_path_remove, (69, 420))
    file_utils.remove_files_older_than(tmpdir, 30)
    assert os.path.isfile(file_path_do_not_remove)
    assert not os.path.isfile(file_path_remove)


class Test_write_and_read_txt_file:
    """Tests for writing and reading a file including utf-8 characters"""

    def test_write_txt_file(self, tmpdir):
        file = tmpdir.join("output.txt")
        file_utils.write_txt_file(file.strpath, "foo")
        assert file.read() == "foo"

    def test_utf_8(self, tmpdir):
        file = tmpdir.join("output.txt")
        file_utils.write_txt_file(file.strpath, "ěščřžýáíéúů")
        assert file_utils.read_txt_file(file.strpath) == "ěščřžýáíéúů"


def test_helper(tmpdir):
    """Test for helper files (typically repetitions.txt and sequence.txt)"""
    path = tmpdir.join("helper.txt").strpath
    helper = file_utils.Helper(path)
    # after init it should have value 0
    assert helper.get() == 0
    helper.write(2)
    assert helper.get() == 2
    # incrementing returns new value
    assert helper.increment() == 3
    # check whether it persisted
    assert helper.get() == 3
    helper.delete()
    assert not os.path.isfile(path)
    # create new helper and test optional kwargs
    helper = file_utils.Helper(path, 5)
    assert helper.get() == 5
    assert helper.increment(2) == 7
    # test ValueError
    with pytest.raises(ValueError):
        assert helper.write("1")
    with pytest.raises(ValueError):
        assert helper.increment("1")


def test_archivate_file(tmpdir):
    """Test for archivating a file - i.e. moving it and adding timestamp to its name"""
    file_name = "some_output_file.txt"
    path = tmpdir.join(file_name).strpath
    timestamp_format = "%Y-%m-%d"
    file_utils.write_txt_file(path, "foo")
    file_utils.archivate_file(path, tmpdir, prefix_timestamp_format=timestamp_format)
    assert not os.path.isfile(path)
    assert os.path.isfile(os.path.join(tmpdir, universal.timestamp(timestamp_format) + file_name))
    # test FileExistsError
    file_utils.write_txt_file(path, "foo")
    with pytest.raises(FileExistsError):
        assert file_utils.archivate_file(path, tmpdir, prefix_timestamp_format=timestamp_format)
    # test force_rewrite flag (raises FileExistsError if not working correctly)
    file_utils.archivate_file(path, tmpdir, prefix_timestamp_format=timestamp_format, force_rewrite=True)


def test_copy_error_img(tmpdir):
    """Test for copying error screenshots"""
    png_name = "test.png"
    path = os.path.join(tmpdir, png_name)
    with open(path, "wb") as png_file:
        png_file.write(b"0")
    output_dir = os.path.join(tmpdir, "dest")
    file_utils.prepare_dir(output_dir)
    file_utils.copy_error_img(output_dir, current_log_dir=tmpdir)
    assert os.path.isfile(os.path.join(output_dir, png_name))
    # test for bmp format
    bmp_name = "test.bmp"
    path = os.path.join(tmpdir, bmp_name)
    with open(path, "wb") as bmp_file:
        bmp_file.write(b"0")
    file_utils.copy_error_img(output_dir, current_log_dir=tmpdir, screenshot_format="bmp")
    assert os.path.isfile(os.path.join(output_dir, bmp_name))
    # test copying different file than the last one
    # slight delay in creating the files because tested function orders them by date and does not work properly
    # if created too quickly in succession
    time.sleep(0.5)
    for i in range(3):
        with open(os.path.join(tmpdir, f"{i}.png"), "wb") as png_file:
            png_file.write(b"0")
            time.sleep(0.5)
    file_utils.copy_error_img(output_dir, current_log_dir=tmpdir, offset=1)
    assert os.path.isfile(os.path.join(output_dir, "1.png"))
