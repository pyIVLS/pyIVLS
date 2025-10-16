SERIAL_NUMBER = "USB2G3902"
DEFAULT_INTEGRATION_TIME = 0.1  # seconds
OO_MIN_WL = 180
OO_MAX_WL = 875


def s_to_ms(seconds: float) -> int:
    return int(seconds * 1e6)


def ms_to_s(microseconds: int) -> float:
    return microseconds / 1e6
