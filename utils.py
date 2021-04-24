from collections.abc import Callable

import sys


def is_dig(s: str) -> bool:
    """
    checks if s is an integer.
    This needs for checking negative integers
    because isdigit and isnumeric methods don't work with them
    :param s: string to check if an integer
    :return: True if string is integer otherwise False
    """
    try:
        int(s)
        return True
    except ValueError:
        return False


def check_on_arrow(x1: int, y1: int, x2: int, y2: int, point_x: int, point_y: int) -> float:
    """
    counts distance between point with coordinates (point_x, point_y) and
    line with start on (x1, y1) and end on (x2, y2)
    :param x1: x coordinate of line's starting
    :param y1: y coordinate of line's starting
    :param x2: x coordinate of line's ending
    :param y2: y coordinate of line's ending
    :param point_x: x coordinate of dot
    :param point_y: y coordinate of dot
    :return: distance between point and line
    (I don't know how it counts distance, I took formulas from math forum)
    """
    px = x2 - x1
    py = y2 - y1
    norm = px * px + py * py
    u = ((point_x - x1) * px + (point_y - y1) * py) / float(norm)
    if u > 1:
        u = 1
    elif u < 0:
        u = 0
    x = x1 + u * px
    y = y1 + u * py
    dx = x - point_x
    dy = y - point_y
    dist = (dx * dx + dy * dy) ** .5
    return dist


def pass_f(*args, **kwargs) -> None:
    """
    pass-function does absolutely nothing
    :param args: nothing
    :param kwargs: nothing
    :return: None
    """
    _ = args, kwargs


def test(func: Callable) -> Callable:
    """
    decorator for check if function or method ran successful that do:
    1. prints "start <your function>"
    2. runs your function
    3. prints "end <your function>"

    using as decorator

    :param func: your function
    :return: func_start_and_stop
    """
    def func_start_and_stop(*args, **kwargs):
        print(f"start {func}")
        func(*args, **kwargs)
        print(f"end {func}")
    return func_start_and_stop


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)
