SERIAL_NUMBER = "USB2G3902"
DEFAULT_INTEGRATION_TIME = 0.1  # seconds
OO_MIN_WL = 180
OO_MAX_WL = 875


def s_to_micros(seconds: float) -> int:
    return int(seconds * 1e6)


def micros_to_s(microseconds: int) -> float:
    return microseconds / 1e6


def millis_to_s(milliseconds: int) -> float:
    return milliseconds / 1e3


def s_to_millis(seconds: float) -> int:
    return int(seconds * 1e3)


OO_MIN_INT_TIME = micros_to_s(3000)  # 3 milliseconds (0.003 seconds)
OO_MAX_INT_TIME = micros_to_s(655350000)  # 655350 milliseconds (655.35 seconds)
