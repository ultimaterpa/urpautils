"""Unit tests for all functions in universal.py file"""


import datetime
from typing import Union

import pytest
from freezegun import freeze_time

from urpautils import universal


@freeze_time("2012-01-14")
class Test_timestamp:
    """Test timestamp function"""

    def test_timestamp_padded(self):
        assert universal.timestamp("%d.%m.%Y") == "14.01.2012"

    def test_timestamp_not_padded(self):
        assert universal.timestamp("%d.%m.%Y", False) == "14.1.2012"


class Test_path_prefix:
    """Test correct prefix of an long path"""

    def test_path_prefix_local(self):
        assert universal.add_long_path_prefix(r"C:\foo\bar") == r"\\?\C:\foo\bar"

    def test_path_prefix_network(self):
        assert universal.add_long_path_prefix(r"\\foo\bar") == r"\\?\UNC\foo\bar"


class Test_kill_app:
    """Not implemented.
    Should it be? Maybe something like: start demo app -> kill it -> assert proccess not existing
    """

    @pytest.mark.skip(reason="might be implemented in the future")
    def test_kill_app(self):
        pass


class Test_email:
    """Not implemented
    There is really no test to run here other than send the email to myself and check it that way
    """

    @pytest.mark.skip(reason="no way of testing this")
    def test_send_email(self):
        pass


class Test_get_birth_date:
    """Test correct reading of a birth date from personal identification number"""

    @pytest.mark.parametrize(
        "number,expected", [("9205200832", datetime.date(1992, 5, 20)), ("901111111", datetime.date(1890, 11, 11))]
    )
    def test_birth_date(self, number, expected):
        assert universal.get_birth_date(number) == expected

    @pytest.mark.parametrize("number", ["123", "123456789123", "abc", "501111111111"])
    def test_value_error(self, number):
        with pytest.raises(ValueError):
            universal.get_birth_date(number)


class Test_verify_rc:
    """Test correct verification of a personal identification number"""

    @pytest.mark.parametrize("number", ["7906047424", "790604/7424", "6354142234", "635414/2234"])
    def test_valid(self, number):
        assert universal.verify_rc(number)

    @pytest.mark.parametrize(
        "number", ["7806047424", "abc", "63541425234", "645414/2234", "63541/42234", "635414/2/234", "abcabcabc"]
    )
    def test_invalid(self, number):
        assert not universal.verify_rc(number)


class Test_verify_ico:
    """Test correct verification of a BIN number"""

    @pytest.mark.parametrize("number", ["26868644", "00885045", "885045", "64824560"])
    def test_valid(self, number):
        assert universal.verify_ico(number)

    @pytest.mark.parametrize("number", ["123456789", "abc", "8850450", "26868643"])
    def test_invalid(self, number):
        assert not universal.verify_ico(number)

    def test_value_error(self):
        with pytest.raises(ValueError):
            universal.verify_ico(123)


class Test_verify_ico_justificatrion:
    """Test correct justification of a BIN number"""

    @pytest.mark.parametrize("number,expected", [("1234", "00001234"), ("12345678", "12345678")])
    def test_valid(self, number, expected):
        assert universal.justify_ico(number) == expected

    @pytest.mark.parametrize("number,expected", [("1234", "11111234"), ("12345678", "12345678")])
    def test_different_fill_char(self, number, expected):
        assert universal.justify_ico(number, "1") == expected

    def test_value_error(self):
        with pytest.raises(ValueError):
            universal.justify_ico(123)
        with pytest.raises(ValueError):
            universal.justify_ico("1234", "00")
        with pytest.raises(ValueError):
            universal.justify_ico("1234", "a")
        with pytest.raises(ValueError):
            universal.justify_ico("1234", 1)
        with pytest.raises(ValueError):
            universal.justify_ico("12")
        with pytest.raises(ValueError):
            universal.justify_ico("123456789")
        with pytest.raises(ValueError):
            universal.justify_ico("1234a")


@pytest.mark.skip(reason="no way of testing this")
def test_clear_ie_cache(self):
    """Not implemented
    There is really no test to run here.
    Besides, we don't want the user to clear their IE cache just by running these tests
    """
    pass


@pytest.mark.skip(reason="might be implemented in the future")
def test_get_app_pid():
    """Not implemented
    Should it be? maybe by starting some demo app and finding its PID
    """
    pass


@pytest.mark.parametrize(
    "today,expected",
    [
        (datetime.date(2021, 9, 2), datetime.date(2021, 9, 1)),
        (datetime.date(2021, 9, 1), datetime.date(2021, 8, 31)),
        (datetime.date(2021, 8, 30), datetime.date(2021, 8, 27)),
        (datetime.date(2021, 9, 29), datetime.date(2021, 9, 27)),
        (datetime.date(2021, 12, 27), datetime.date(2021, 12, 23)),
        (datetime.date(2021, 1, 4), datetime.date(2020, 12, 31)),
    ],
)
def test_get_previous_work_day_date(today, expected):
    """Test correct date of previous work day"""
    # CZ is default country
    assert universal.get_previous_work_day_date(today) == expected
    # try some other country
    assert universal.get_previous_work_day_date(datetime.date(2021, 9, 2), "US") == datetime.date(2021, 9, 1)
    # independence day yeeehaw
    assert universal.get_previous_work_day_date(datetime.date(2018, 7, 5), "US") == datetime.date(2018, 7, 3)


def _create_time(sign: str, value: Union[float, int]) -> str:
    """
    For testing purposes only for function test_robot_has_time
    :param sign             str, + or -
    :param value            int in hours
    :return: str
    """

    now = datetime.datetime.now()

    if sign == "+":
        if value + now.hour >= 24:
            return "23:59:59"
        dt = now + datetime.timedelta(hours=value)
    elif sign == "-":
        if value >= now.hour:
            return "00:00:00"
        dt = now - datetime.timedelta(hours=value)
    else:
        raise ValueError(f"Sign '{sign}' has to be '+' or '-'.")

    return f"{dt.hour}:{dt.minute}:{dt.second}"


@pytest.mark.parametrize(
    "start,end,expected",
    [
        ("0:00:00", _create_time("-", 24), False),
        ("0:00:00", _create_time("-", 12), False),
        ("0:00:00", _create_time("-", 10), False),
        ("0:00:00", _create_time("-", 0.1), False),
        ("0:00:00", _create_time("-", 0), False),
        ("0:00:00", _create_time("+", 0.1), True),
        ("0:00:00", _create_time("+", 10), True),
        ("0:00:00", _create_time("+", 12), True),
        ("0:00:00", _create_time("+", 24), True),
        ("0:00:00", "23:59:59", True),
    ],
)
def test_robot_has_time(start, end, expected):
    assert universal.robot_has_time(start=start, end=end) == expected
