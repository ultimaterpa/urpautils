"""Module containing functions dependent on the urpa library that can be used with urpa robots"""

import ctypes
import locale
import logging

from typing import Tuple, Union, Sequence, Optional

import urpa
import urpatimeout


cf = urpa.condition_factory()
logger = logging.getLogger(__name__)


def parallel_search(
    app: urpa.App, *conditions: Union[urpa.Condition, Sequence[urpa.Condition]], wait: int = 10000
) -> Tuple[int, list]:
    """Searches for multiple elements. Return first one found

    :param app:            urpa app
    :param *conditions:    cf conditions of the elements
    :param wait:           timeout in ms
    :return:               tuple (index of the element found, element)
    """
    t = urpatimeout.Timeout(wait)
    while not t.is_expired():
        for index, condition in enumerate(conditions):
            elements = app.find_all(condition, 0)
            if elements:
                return index, elements
    raise urpa.ElementNotFoundError("Parallel_search: No elemets found for the conditions!")


def check_elements(
    app: urpa.App,
    *conditions: Union[urpa.Condition, Sequence[urpa.Condition]],
    timeout: Optional[int] = None,
) -> None:
    """Searches for control elements

    :param app:            urpa app
    :param *conditions:    cf conditions of the element(s)
    :param timeout:        optional timeout in ms (urpa.default_timeout is used if None)
    :return:               None
    """
    logger.debug("Searching for control elements")
    for condition in conditions:
        if timeout is None:
            app.find_first(condition)
        else:
            app.find_first(condition, timeout=timeout)
    logger.debug("Control elements found")


def robot_setup(
    screen_resolution: Tuple[int, int, int],
    default_timeout: Optional[int] = None,
    default_screenshot_format: str = "png",
    debug_mode: bool = False,
) -> None:
    """Initiates urpa robot

    :param screen_resolution:          tuple (width, heigh, bit depth)
    :param default_timeout:            optional default timeout for element searching. urpa.default_timeout is used if None
    :param default_screenshot_format:  png or bmp
    :param debug_mode:                 bool robot debug mode
    :return:                           None
    """
    possible_screenshot_formats = ("png", "bmp")
    if not default_screenshot_format in possible_screenshot_formats:
        raise ValueError(
            f"Invalid screenhsot format '{default_screenshot_format}'. Please use one of the following: '{possible_screenshot_formats}'"
        )
    urpa.bring_to_foreground()
    if default_timeout is not None:
        urpa.set_default_timeout(default_timeout)
    try:
        urpa.check_screen_resolution(screen_resolution[0], screen_resolution[1], screen_resolution[2])
    except ValueError:
        urpa.set_screen_resolution(screen_resolution[0], screen_resolution[1], screen_resolution[2])
    urpa.default.screenshot_format = default_screenshot_format
    urpa.set_debug_mode(debug_mode)


def save_as(
    file_name: str,
    open_save_as_window: bool = False,
    app_elem: Optional[urpa.AppElement] = None,
    open_save_as_window_shortcut: str = "CTRL+SHIFT+S",
    save_as_window_name: str = "",
    file_name_elem_name: str = "",
    save_button_name: str = "",
    confirm_rewrite_window_name: str = "",
    yes_button_name: str = "",
    timeout: int = 5000,
    force_rewrite: bool = False,
) -> None:
    """Function for operating with 'Save As' dialogue in variety of Windows applications

    :param file_name:                     path to the file to be saved
    :param open_save_as_window:           True if user wishes to open the Save As dialogue via this function.
                                          False if the dialogue is already opened
    :param app_elem:                      Used only if previous arg is set to True - specifies an element on which
                                          to send keyboard shortcut to open the Save As dialogue
    :param open_save_as_window_shortcut:  Specify the keyboard shortcut for opening Save As window
    :param save_as_window_name:           Specify name of the Save As dialogue window.
                                          elem_names[system_language] is used if not provided
    :param file_name_elem_name:           Specify name of the File name edit element.
                                          elem_names[system_language] is used if not provided
    :param save_button_name:              Specify name of the Save button element.
                                          elem_names[system_language] is used if not provided
    :param confirm_rewrite_window_name:   Specify name of the Confirm Save As dialogue window.
                                          elem_names[system_language] is used if not provided
    :param yes_button_name:               Specify name of the Yes button element.
                                          elem_names[system_language] is used if not provided
    :param timeout:                       Timeout for finding the elements
    :param force_rewrite:                 If set to True, file is rewritten if it already exists
    :return:                              None
    """
    # import here for now cuz urpaform is not on PyPI just yet so we can't put it in setup.py
    from urpaform import Form, EditElement

    if open_save_as_window and app_elem is None:
        raise RuntimeError("Please specify an app element on which to open the Save As window")

    elem_names = {
        "en_US": {
            "save_as_window_name": "Save As",
            "file_name_elem_name": "File name:",
            "save_button_name": "Save",
            "confirm_rewrite_window_name": "Confirm Save As",
            "yes_button_name": "Yes",
        },
        "cs_CZ": {
            "save_as_window_name": "Uložit jako",
            "file_name_elem_name": "Název souboru:",
            "save_button_name": "Uložit",
            "confirm_rewrite_window_name": "Potvrdit uložení jako",
            "yes_button_name": "Ano",
        },
    }
    system_language = locale.windows_locale[ctypes.windll.kernel32.GetUserDefaultUILanguage()]
    if not system_language in elem_names.keys() and (
        not save_as_window_name
        or not file_name_elem_name
        or not save_button_name
        or not confirm_rewrite_window_name
        or not yes_button_name
    ):
        raise RuntimeError(
            f"""Unsupported system language: '{system_language}'
                    Please specify names for these elements manually: '{elem_names['en_US'].keys()}'"""
        )

    save_as_window_name = save_as_window_name or elem_names[system_language]["save_as_window_name"]
    file_name_elem_name = file_name_elem_name or elem_names[system_language]["file_name_elem_name"]
    save_button_name = save_button_name or elem_names[system_language]["save_button_name"]
    confirm_rewrite_window_name = (
        confirm_rewrite_window_name or elem_names[system_language]["confirm_rewrite_window_name"]
    )
    yes_button_name = yes_button_name or elem_names[system_language]["yes_button_name"]

    if open_save_as_window:
        app_elem.send_key(open_save_as_window_shortcut)  # type: ignore
    save_as_window = urpa.find_first_app(save_as_window_name, timeout=timeout)
    file_name_field = EditElement(save_as_window.find_first(cf.name(file_name_elem_name).edit(), timeout=timeout))
    with Form("Save As file name") as form:
        form.add(file_name_field, file_name)
    save_as_window.find_first(cf.name(save_button_name).button(), timeout=timeout).send_mouse_click()
    try:
        confirm_save_as_window = urpa.find_first_app(confirm_rewrite_window_name, timeout=timeout)
    except urpa.ElementNotFoundError:
        pass
    else:
        if force_rewrite:
            confirm_save_as_window.find_first(cf.name(yes_button_name).button(), timeout=timeout).send_mouse_click()
        else:
            raise FileExistsError(
                f"File '{file_name}' already exists. If you want to rewrite it set 'force_rewrite' arg to 'True'"
            )


def open_file(
    file_name: str,
    open_open_file_window: bool = False,
    app_elem: Optional[urpa.AppElement] = None,
    open_open_file_window_shortcut: str = "CTRL+O",
    open_file_window_name: str = "",
    file_name_elem_name: str = "",
    open_button_name: str = "",
    timeout: int = 5000,
) -> None:
    """Function for operating with 'Open' dialogue in variety of Windows applications

    :param file_name:                       path to the file to be opened
    :param open_open_file_window:           True if user wishes to open the Open dialogue via this function.
                                            False if the dialogue is already opened
    :param app_elem:                        Used only if previous arg is set to True - specifies an element on which
                                            to send keyboard shortcut to open the Open dialogue
    :param open_open_file_window_shortcut:  Specify the keyboard shortcut for opening Open window
    :param open_file_window_name:           Specify name of the Open dialogue window.
                                            elem_names[system_language] is used if not provided
    :param file_name_elem_name:             Specify name of the File name edit element.
                                            elem_names[system_language] is used if not provided
    :param open_button_name:                Specify name of the Open button element.
                                            elem_names[system_language] is used if not provided
    :param timeout:                         Timeout for finding the elements
    :return:                                None
    """
    from urpaform import Form, EditElement

    if open_open_file_window and app_elem is None:
        raise RuntimeError("Please specify an app element on which to open the Open File window")

    elem_names = {
        "en_US": {
            "open_file_window_name": "Open",
            "file_name_elem_name": "File name:",
            "open_button_name": "Open",
        },
        "cs_CZ": {
            "open_file_window_name": "Otevřít",
            "file_name_elem_name": "Název souboru:",
            "open_button_name": "Otevřít",
        },
    }

    system_language = locale.windows_locale[ctypes.windll.kernel32.GetUserDefaultUILanguage()]
    if not system_language in elem_names.keys() and (
        not open_file_window_name or not file_name_elem_name or not open_button_name
    ):
        raise RuntimeError(
            f"""Unsupported system language: '{system_language}'
                    Please specify names for these elements manually: '{elem_names['en_US'].keys()}'"""
        )
    open_file_window_name = open_file_window_name or elem_names[system_language]["open_file_window_name"]
    file_name_elem_name = file_name_elem_name or elem_names[system_language]["file_name_elem_name"]
    open_button_name = open_button_name or elem_names[system_language]["open_button_name"]

    if open_open_file_window:
        app_elem.send_key(open_open_file_window_shortcut)  # type: ignore

    open_file_window = urpa.find_first_app(open_file_window_name, timeout=timeout)
    file_name_field = EditElement(open_file_window.find_first(cf.name(file_name_elem_name).edit(), timeout=timeout))
    with Form("Open File name") as form:
        form.add(file_name_field, file_name)
    open_file_window.find_first(
        cf.name(open_button_name).class_name("Button").button(), timeout=timeout
    ).send_mouse_click()
