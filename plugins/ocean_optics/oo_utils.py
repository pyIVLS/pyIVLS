SERIAL_NUMBER = "USB2G3902"
DEFAULT_INTEGRATION_TIME = 0.1  # seconds
OO_MIN_WL = 180
OO_MAX_WL = 875


def s_to_ms(seconds: float) -> int:
    """Convert seconds to microseconds

    Args:
        seconds (float)

    Returns:
        int: microseconds
    """
    return int(seconds * 1e6)


def ms_to_s(microseconds: int) -> float:
    """Convert microseconds to seconds

    Args:
        microseconds (int)

    Returns:
        float: seconds
    """
    return microseconds / 1e6


OO_MIN_INT_TIME = ms_to_s(3000)
OO_MAX_INT_TIME = ms_to_s(655350000)
