import sys
import os
import time

from PyQt6 import uic
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QObject

class Keithley2612B(QObject):

####################################  threads


################################### internal functions


########Slots

########Signals


########Functions
    def __init__(self):
        QObject.__init__(self)    
        self.path = os.path.dirname(__file__) + os.path.sep 
        self.settingsWidget = uic.loadUi(self.path + 'Keithley2612B_settingsWidget.ui')

