# TODO ###### indented items are already done """"""""
# ## urpatools / urpautils
#  - parellel search
#  - nastaveni robota + nastaveni rozliseni (jedna funkce)
#       - zabijeni aplikaci
#  - archivace
#  - kopirovani error screenshotu
#       - obsluha helper souboru (trida s metodama `write`, `get`, `increment`, `delete`)
#       - obecne zapisovani/cteni/appendovani/mazani .txt souboru
#  - kontrola prvku
#       - notifikacni email
#       - get timestamp (s moznosti leading zeroes nebo bez nich)
#       - funkce pro pridani prefixu pred cestu k souboru pro obejiti win32api limitu 260 znaku. Prida prefix `\\?\` nebo `\\?\UNC\` podle toho, zda se jedna o sitove uloziste nebo ne
#       - priprava adresare (vytvori ho, pokud neexistuje)
#  - zjisteni typu souboru podle jeho signature: https://en.wikipedia.org/wiki/List_of_file_signatures . Nevim, v kolika robotech to je pouzitelne, ale v cmzrb se mi to ted hodilo. Kdyz DA vracelo excel soubor v base64 a ja jsem musel zjistit, zda to je xls nebo xlsx
#       - mazani cache IE
#       - mazani souboru z konkretniho adresare, ktere jsou starsi nez XXXX
#  - nejaka trida pro operovani s CSV - write row, read row, read all rows, ....
# ​
# ## utility pro bussiness logiku
#       - kontrola spravnosti ICa / Rodneho cisla   --------------------- ZATIM MAM POUZE ICO
import datetime
import logging
import os
import smtplib
import subprocess
import time

from email import charset
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Union

logger = logging.getLogger(__name__)


def timestamp(format: str="%d.%m.%Y %H:%M:%S", pad_date_with_zeros: bool=True) -> str:
    """Returns formatted timestamp

    :param format:               timestamp format
    :param pad_date_with_zeros:  pad one-digit numbers of day and month with leading zero
    :return:                     timestamp string
    """
    if not pad_date_with_zeros:
        format = format.replace("%m","%#m").replace("%d","%#d")
    return datetime.datetime.now().strftime(format)


def add_path_prefix(path: str) -> str:
    r"""Returns original path with prefix to avoid win32api 260 char limit
    C:\Temp -> \\?\C:\Temp
    \\net\folder -> \\?\UNC\net\folder

    :param path:          path
    :return:              original path with prefix
    """
    local_prefix = "\\\\?\\"
    network_prefix = "\\\\?\\UNC\\"
    if path[0:2] == "\\\\":
        return f"{network_prefix}{path[2:]}" 
    return f"{local_prefix}{path}"


def prepare_dir(dir_name: str) -> None:
    """Creates directory dir_name if it does not exist
    
    :param dir_name:      path
    :return:              None
    """
    if not os.path.exists(dir_name):
        logger.info(f"Creating new directory '{dir_name}'.")
        os.mkdir(dir_name)


def kill_app(image_name: str) -> None:
    """Kills app and its tree
    
    :param image_name:      app image name
    :return:                None
    """
    subprocess.run(("taskkill", "/F", "/IM", f"{image_name}"))


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

    def increment(self, increment: int=1) -> int:
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


def send_email_notification(email_sender: str, recipients : list, recipient_copy : list, subject: str, body: str, smtp_server: str) -> None:
    """Sends an e-mail
    
    :param email_sender:    sender of this e-mail
    :param recipients:      list of addresses of recipients
    :param recipients_copy: list of addresses of recipients of a copy
    :param subject:         subject of the e-mail
    :param body:            body of the e-mail
    :param smtp_server:     smtp server
    :return:                None
    """
    charset.add_charset("utf-8", charset.QP, charset.QP, "utf-8")
    mail = MIMEMultipart("alternative")
    mail["Subject"] = Header(subject, "utf-8")
    mail["From"] = email_sender
    mail["To"] = ", ".join(recipients)
    mail["Cc"] = ", ".join(recipient_copy)
    text = body
    html = "<html><body>" + body + "</body></html>"
    txt_message = MIMEText(text.encode("utf-8"), "plain", "utf-8")
    html_message = MIMEText(html.encode("utf-8"), "html", "utf-8")
    mail.attach(txt_message)
    mail.attach(html_message)
    logger.info(f"Sending e-mail to '{recipients}', copy: '{recipient_copy}'")
    logger.debug(f"Subject: '{subject}', body: '{body}'")
    sender = smtplib.SMTP(smtp_server)
    sender.set_debuglevel(1)
    sender.sendmail(email_sender, recipients + recipient_copy, mail.as_string())
    sender.quit()
    logger.info("E-mail sent")


def check_bin(bin: Union[str, int]) -> bool:
    """Check whether a BIN (IČO) number is valid
    https://phpfashion.com/jak-overit-platne-ic-a-rodne-cislo

    :param bin:   string or integer of the BIN number
    :retun:       bool
    """
    if isinstance(bin, str):
        if len(bin) != 8 or not bin.isnumeric():
            return False
    elif isinstance(bin, int):
        if 10000000 > bin > 99999999:
            # must have 8 digits
            return False
        bin = str(bin)
    else:
        raise ValueError(f"'BIN' must be an instance of 'str' or 'int', not '{type(bin)}'")

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


def clear_ie_cache() -> None:
    r"""Clears Internet Explorer cache and makes registry change so it does not open customize window on first run
    RunDll32.exe InetCpl.cpl,ClearMyTracksByProcess 255
    reg ADD "HKEY_CURRENT_USER\Software\Policies\Microsoft\Internet Explorer\Main" /v DisableFirstRunCustomize /d 1 /t REG_DWORD /f
    reg ADD "HKEY_CURRENT_USER\Software\Policies\Microsoft\Internet Explorer\Main" /v RunOnceComplete /d 1 /t REG_DWORD /f
    reg ADD "HKEY_CURRENT_USER\Software\Policies\Microsoft\Internet Explorer\Main" /v RunOnceHasShown /d 1 /t REG_DWORD /f
    """
    subprocess.run(("RunDll32.exe", "InetCpl.cpl,ClearMyTracksByProcess", "255"))
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
        )
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
        )
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
        )
    )