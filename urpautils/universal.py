"""Module containing universal functions that can be used with urpa robots"""

import datetime
import functools
import logging
import os
import re
import smtplib
import subprocess
import time
from typing import List, Optional

from email import charset
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import holidays


logger = logging.getLogger(__name__)


def timestamp(format: str = "%d.%m.%Y %H:%M:%S", pad_date_with_zeros: bool = True) -> str:
    """Returns formatted timestamp

    :param format:               timestamp format
    :param pad_date_with_zeros:  pad one-digit numbers of day and month with leading zero
    :return:                     timestamp string
    """
    if not pad_date_with_zeros:
        format = format.replace("%m", "%#m").replace("%d", "%#d")
    return datetime.datetime.now().strftime(format)


def add_long_path_prefix(path: str) -> str:
    r"""Returns original path with prefix to avoid win32api 260 char limit
    C:\Temp -> \\?\C:\Temp
    \\net\folder -> \\?\UNC\net\folder
    https://docs.microsoft.com/en-us/windows/win32/fileio/maximum-file-path-limitation?tabs=cmd

    :param path:          path
    :return:              original path with prefix
    """
    local_prefix = "\\\\?\\"
    network_prefix = "\\\\?\\UNC\\"
    if path[0:2] == "\\\\":
        return f"{network_prefix}{path[2:]}"
    return f"{local_prefix}{path}"


def kill_app(image_name: str, check: bool = False) -> None:
    """Kills app and its tree

    :param image_name:      app image name
    :param check:           check status code of the subprocess.run. Raises Exception if non-zero
    :return:                None
    """
    subprocess.run(("taskkill", "/F", "/IM", f"{image_name}"), check=check)


def send_email_notification(
    email_sender: str,
    recipients: List[str],
    recipients_copy: List[str],
    subject: str,
    body: str,
    smtp_server: str,
    smtp_port: int = 0,
    attachments: List[str] = [],
    debug_level: int = 0,
) -> None:
    """Sends an e-mail

    :param email_sender:    sender of this e-mail
    :param recipients:      list of addresses of recipients
    :param recipients_copy: list of addresses of recipients of a copy
    :param subject:         subject of the e-mail
    :param body:            body of the e-mail
    :param smtp_server:     smtp server
    :param smtp_port:       optional port for the smtp server. smtplib.SMTP_PORT (=25) is used if not provided
    :param attachments:     optional list of attachments' file paths
    :param debug_level:     optional int, default is 0
    :return:                None
    """

    charset.add_charset("utf-8", charset.QP, charset.QP)

    mail = MIMEMultipart("mixed")
    mail["To"] = ", ".join(recipients)
    mail["From"] = email_sender
    mail["Cc"] = ", ".join(recipients_copy)
    mail["Subject"] = Header(subject, "utf-8")

    message_alternative = MIMEMultipart("alternative")
    text = body
    html = "<html><body>" + body + "</body></html>"
    message_alternative.attach(MIMEText(text, "plain", _charset="utf-8"))  # type: ignore
    message_alternative.attach(MIMEText(html, "html", _charset="utf-8"))  # type: ignore
    mail.attach(message_alternative)

    for attachment in attachments:
        with open(attachment, "rb") as att_file:
            part = MIMEApplication(att_file.read(), Name=os.path.basename(attachment))
        part["Content-Disposition"] = f'attachment; filename="{os.path.basename(attachment)}"'
        mail.attach(part)

    logger.info(f"Sending e-mail to '{recipients}', copy: '{recipients_copy}'")
    logger.debug(f"Subject: '{subject}', body: '{body}'")
    sender = smtplib.SMTP(smtp_server, smtp_port)
    sender.set_debuglevel(debug_level)
    sender.sendmail(email_sender, recipients + recipients_copy, mail.as_string())
    sender.quit()
    logger.info("E-mail sent")


def repeat(func):
    """Wrapper pro funkce, kde provadim vzdy stejnou akci"""

    @functools.wraps(func)
    def wrapper(*args, action: str, repetition: int = 3, **kwargs) -> Callable:
        """Repeat commands in a function until no Exception occurs, or run out of attempts

        :param action:          str, the name of the action for logging purposes
        :param repetition:      int, the number of repetitions, by default, is 3
        :return Callable
        """

        error = None
        logger.info(f"Executing action: '{action}'")
        for pokus in range(1, repetition + 1):
            try:
                logger.info(f"'{pokus}'. attempt to execute: '{action}'")
                return func(*args, **kwargs)
            except Exception as err:
                error = err
                logger.exception(f"An Exception has occured: {err}")
                continue
            finally:
                if not error:
                    logger.info(f"Successfully executed: '{action}'")

        logger.error(f"Unsuccessfully executed: '{action}'")
        raise RuntimeError(f"Robot was unable to execute this action '{action}' due to this error '{error}'")

    return wrapper


def get_birth_date(number: str) -> datetime.date:
    """Returns birth date calculated from personal identification number

    :param number:   string in format xxxxxxxxxx
    :return:         datetime.date object (or raises ValueError)
    """
    if not len(number) in (9, 10):
        raise ValueError("Invalid length")
    year = 1900 + int(number[0:2])
    # females have 50 added to the month value, 20 is added when the serial
    # overflows (since 2004)
    month = int(number[2:4]) % 50 % 20
    day = int(number[4:6])
    # 9 digit numbers were used until January 1st 1954
    if len(number) == 9:
        if year >= 1980:
            year -= 100
        if year > 1953:
            raise ValueError("No 9 digit birth numbers after 1953.")
    elif year < 1954:
        year += 100
    # this can also raise ValueError
    return datetime.date(year, month, day)


def verify_rc(number: str) -> bool:
    """Check whether 'Rodné číslo' is valid
    https://phpfashion.com/jak-overit-platne-ic-a-rodne-cislo

    :param number:   string in format xxxxxxxxxx or xxxxxx/xxxx
    :return:         bool
    """
    # check whether 'number' contains '/' and if its at 5th last place of the input (i.e. xxxxxx/xxxx)
    # if yes, remove it
    if number.count("/"):
        if number.count("/") == 1 and len(number) - number.index("/") == 5:
            number = number.replace("/", "")
        else:
            # the number has '/' but not in the right place or there are more than one
            return False

    if len(number) not in (9, 10):
        return False
    try:
        birth_date = get_birth_date(number)
    except ValueError as err:
        logger.debug(f"RC '{number}' not valid, could not verify birth date: '{str(err)}'")
        return False
    # check the check digit (10 digit numbers only)
    if len(number) == 10:
        check = int(number[:-1]) % 11
        # before 1985 the checksum could be 0 or 10
        if birth_date < datetime.date(1985, 1, 1):
            check = check % 10
        if number[-1] != str(check):
            return False
    return True


def verify_ico(bin: str) -> bool:
    """Check whether IČO number is valid
    https://phpfashion.com/jak-overit-platne-ic-a-rodne-cislo

    :param bin:   string of the BIN number
    :retun:       bool
    """
    if isinstance(bin, str):
        if not bin.isnumeric() or len(bin) > 8:
            return False
        # pad with zeros from left to length 8 (123456 -> 00123456)
        bin = bin.rjust(8, "0")
    else:
        raise ValueError(f"'BIN' must be an instance of 'str', not '{type(bin)}'")

    a = 0
    for i in range(7):
        a += int(bin[i]) * (8 - i)

    a %= 11
    if a == 0:
        c = 1
    elif a == 1:
        c = 0
    else:
        c = 11 - a

    return int(bin[7]) == c


def justify_ico(bin: str, fill_char: str = "0") -> str:
    """Pads BIN number with 'fill_char' to length 8 (123456 -> 00123456)

    Args:
        bin (str): BIN to be padded
        fill_char (str): char to be padded with

    Returns:
        str: padded BIN
    """
    if not isinstance(fill_char, str) or not fill_char.isnumeric() or len(fill_char) != 1:
        raise ValueError(f"Invalid 'fill_char'. Fill char must be numeric string with length exactly 1")
    if isinstance(bin, str):
        if not bin.isnumeric() or len(bin) > 8 or len(bin) < 4:
            raise ValueError("Invalid BIN number. BIN must be numeric value between 4 and 8 digits")
        return bin.rjust(8, fill_char)
    else:
        raise ValueError(f"'BIN' must be an instance of 'str', not '{type(bin)}'")


def clear_ie_cache(check: bool = False) -> None:
    r"""Clears Internet Explorer cache and makes registry change so it does not open 'customize' window on first run
    RunDll32.exe InetCpl.cpl,ClearMyTracksByProcess 255
    reg ADD "HKEY_CURRENT_USER\Software\Policies\Microsoft\Internet Explorer\Main" /v DisableFirstRunCustomize /d 1 /t REG_DWORD /f
    reg ADD "HKEY_CURRENT_USER\Software\Policies\Microsoft\Internet Explorer\Main" /v RunOnceComplete /d 1 /t REG_DWORD /f
    reg ADD "HKEY_CURRENT_USER\Software\Policies\Microsoft\Internet Explorer\Main" /v RunOnceHasShown /d 1 /t REG_DWORD /f

    :param check:    check status code of the subprocess.run. Raises Exception if non-zero
    """
    subprocess.run(("RunDll32.exe", "InetCpl.cpl,ClearMyTracksByProcess", "255"), check=check)
    time.sleep(5)
    subprocess.run(
        (
            "reg",
            "ADD",
            r"HKEY_CURRENT_USER\Software\Policies\Microsoft\Internet Explorer\Main",
            "/v",
            "DisableFirstRunCustomize",
            "/d",
            "1",
            "/t",
            "REG_DWORD",
            "/f",
        ),
        check=check,
    )
    subprocess.run(
        (
            "reg",
            "ADD",
            r"HKEY_CURRENT_USER\Software\Policies\Microsoft\Internet Explorer\Main",
            "/v",
            "RunOnceComplete",
            "/d",
            "1",
            "/t",
            "REG_DWORD",
            "/f",
        ),
        check=check,
    )
    subprocess.run(
        (
            "reg",
            "ADD",
            r"HKEY_CURRENT_USER\Software\Policies\Microsoft\Internet Explorer\Main",
            "/v",
            "RunOnceHasShown",
            "/d",
            "1",
            "/t",
            "REG_DWORD",
            "/f",
        ),
        check=check,
    )


def get_app_pid(
    app_name: str,
    pids_to_exclude: List[Optional[int]] = [],
    number_of_retries: int = 3,
    wait_before_next_try: int = 10000,
) -> int:
    """Finds all PIDs of an 'app_name' application and returns first one

    :param app_name:              image name of the app
    :param pids_to_exclude:       list of PIDs that are filtered out
    :param number_of_retries:     number of retries
    :param wait_before_next_try:  amount of miliseconds to wait before next try
    :return:                      int of the first PID found
    """
    if not isinstance(pids_to_exclude, list):
        raise ValueError(f"'pids_to_exclude' must be 'list', not '{type(pids_to_exclude)}'")
    for retry in range(1, number_of_retries + 1):
        logger.info(f"Try '{retry}' of finding PID for application '{app_name}'")
        tasklist_command = f'tasklist /FI "IMAGENAME eq {app_name}*"'
        for pid_to_exclude in pids_to_exclude:
            tasklist_command += f' /FI "PID ne {pid_to_exclude}"'
        tasklist_output = subprocess.check_output(tasklist_command)
        # find first number surrounded by whitespaces
        try:
            pid = int(re.search(rb"\s+(\d+)\s+", tasklist_output).group(1))  # type: ignore
        except AttributeError:
            logger.warning("PID not found")
            time.sleep(wait_before_next_try / 1000)
            continue
        logger.info(f"PID found: {pid}")
        return pid
    raise RuntimeError(f"Unable to find PID for image name '{app_name}'")


def get_previous_work_day_date(today: datetime.date = datetime.date.today(), country: str = "CZ") -> datetime.date:
    """Returns previous work day based on value 'today'

    :param today:      date to use as reference
    :param country:    code of country to fetch list of holidays for
    :return:           datetime.date
    """
    holiday_days = getattr(holidays, country)()
    for offset in range(1, 366):
        # loop till a working day is found
        previous_day = today - datetime.timedelta(offset)
        # weekdays 5 and 6 are saturday and sunday
        if not previous_day in holiday_days and not previous_day.weekday() in (5, 6):
            return previous_day
    raise RuntimeError("No previous working day found")
