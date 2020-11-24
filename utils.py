def isdig(s: str):
    try:
        int(s)
        return True
    except ValueError:
        return False


def check_on_arrow(x1, y1, x2, y2, x3, y3):
    dx1 = x2 - x1
    dy1 = y2 - y1
    dx = x3 - x1
    dy = y3 - y1
    s = dx1 * dy - dx * dy1
    ab = (dx1 * dx1 + dy1 * dy1) ** 0.5
    h = s / ab
    return h


def pass_f(*args, **kwargs):
    _ = args, kwargs


def test(func):
    def func_start_and_stop(*args, **kwargs):
        print(f"start {func}")
        func(*args, **kwargs)
        print(f"end {func}")
    return func_start_and_stop
