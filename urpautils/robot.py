"""Module containing functions dependent on the urpa library that can be used with urpa robots"""

import logging

from typing import Tuple, Union, Sequence, Optional

import urpa
import urpatimeout  # TODO mention this in setup.py


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
    default_timeout: Optional[int]=None,
    default_screenshot_format: str="png",
    debug_mode: bool=False
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
        urpa.set_screen_resolution([0], screen_resolution[1], screen_resolution[2])
    urpa.default.screenshot_format = default_screenshot_format
    urpa.set_debug_mode(debug_mode)
