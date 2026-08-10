"""
This is a class for peltier controller

"""

import logging
from threading import Lock

logger = logging.getLogger(__name__)


class itc503:
    def __init__(self):
        self.lock = Lock()

    def open(self, source=None):
        """Opens the itc503 device for use

        Returns status
            0 - no error
        """
        logger.warning("WARNING; USING MOCK")
        return 0

    def close(self):
        """Closes connection to itc 503 and restores the device into LOCAL MODE

        Returns status
            0 - no error
        """
        logger.warning("WARNING; USING MOCK")

        return 0

    def setT(self, temperature):
        """set the setpoint

        Returns status
            0 - no error
        """
        logger.warning("WARNING; USING MOCK")

        return 0

    def getData(self):
        """get the data out of controller and return it as a float

        Returns:
            temperature as a float
        """
        with self.lock:
            logger.warning("WARNING; USING MOCK")

            return 0.0
