import numpy as np
import seabreeze.spectrometers as sb
import oo_utils as utils
from oo_utils import s_to_micros
from typing import Optional
from enum import Enum

"""
Ocean Optics USB2000 spectrometer driver.
Modified from TLCCS Drivers. 
HOX: Integration times are in microseconds (µs) internally, but the user interface uses milliseconds
and the value is stored in seconds in the .ini and internal settings dict.
Conversion functions are in oo_utils.py, and should be used to since they are clearer to the reader.
"""


class trigger_mode(Enum):
    CONTINUOUS = 0
    SOFTWARE = 1
    EXTERNAL = 2


class OODRV:
    integration_time: int = s_to_micros(utils.DEFAULT_INTEGRATION_TIME)  # microseconds
    _integ_limits: Optional[tuple[int, int]] = None  # (min, max) integration time in µs, set in open()
    _spectro: Optional[sb.Spectrometer] = None

    @property
    def spectro(self) -> sb.Spectrometer:
        assert self._spectro is not None, "Device not open"
        return self._spectro

    @property
    def integ_limits(self) -> tuple[int, int]:
        assert self._integ_limits is not None, "Device not open"
        return self._integ_limits

    def open(self) -> None:
        """Open the spectrometer and set the integration time limits. Also sets the integration time to the default value."""
        if self._spectro is not None:
            return  # already open
        self._spectro = sb.Spectrometer.from_serial_number(utils.SERIAL_NUMBER)
        self._integ_limits = self._spectro.integration_time_micros_limits
        self.set_integration_time(self.integration_time)

    def get_integration_time(self) -> int:
        """Returns current integration time in micros

        Returns:
            int: integration time in micros
        """
        return self.integration_time

    def set_integration_time(self, intg_time: int) -> None:
        """Set the integration time in microseconds

        Args:
            intg_time (int): Integration time in microseconds

        Returns:
            bool: True if successful, False otherwise
        """
        assert intg_time >= self.integ_limits[0], f"Integration time below minimum of {self.integ_limits[0]} µs"
        assert intg_time <= self.integ_limits[1], f"Integration time above maximum of {self.integ_limits[1]} µs"
        self.spectro.integration_time_micros(intg_time)
        self.get_spectrum()  # take a spectrum to make sure the new time is applied.
        self.integration_time = intg_time

    def get_device_status(self):
        raise NotImplementedError("get_device_status not implemented")

    def get_spectrum(self, correct_dark_counts=False) -> np.ndarray:
        """Get a spectrum from the spectrometer.

        Args:
            correct_dark_counts (bool, optional): Whether to correct for dark counts. Defaults to False.
        Returns:
            np.ndarray: The spectrum as a numpy array.
        """
        intensities = self.spectro.intensities(correct_dark_counts=correct_dark_counts)
        max_intensity = self.spectro.max_intensity  # 4095.0

        # normalize to range 0-1 based on max intensity
        intensities = intensities / max_intensity
        return intensities

    def get_wavelengths(self) -> np.ndarray:
        """Get the wavelengths from the spectrometer.

        Returns:
            np.ndarray: The wavelengths as a numpy array.
        """
        wavelengths = self.spectro.wavelengths()
        return wavelengths

    def trigger_mode(self, mode: trigger_mode) -> None:
        """Set the trigger mode of the spectrometer. This can be implemented in the future if external triggering is needed.
        See: https://www.optosirius.co.jp/OceanOptics/technical/external-triggering-options.pdf
        TL;DR: USB2000 can be triggered externally, but it requires additional hardware.

        Args:
            mode (trigger_mode): The trigger mode to set.
        """
        raise NotImplementedError("trigger_mode not implemented")
