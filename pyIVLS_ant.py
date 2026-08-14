# File: pyIVLS_ant.py
# GUI and functionality for Ai iNTerpreter
#
# ver. 0.1
# ivarad
# 26.08.13
# chat GUI (no LLM connection yet)
import copy
import json
import logging
import os
from os.path import sep
from datetime import datetime

from PyQt6 import uic
from PyQt6.QtGui import QTextCursor
from PyQt6.QtCore import QModelIndex, QObject, Qt, pyqtSignal, pyqtSlot

logger = logging.getLogger(__name__)

class pyIVLS_ant(QObject):

    ### Signals for communication
    info_message = pyqtSignal(str)
    log_message = pyqtSignal(str)
    
    #### Internal functions
    def __init__(self, path):
        super().__init__()
        ui_file_name = path + "components" + sep + "pyIVLS_ant.ui"
        self.widget = uic.loadUi(ui_file_name)
        self.path = path
        self.logger = logger

        self._connect_signals()

    def _connect_signals(self):
        self.widget.pushButton_send.clicked.connect(self._send_action)

    #### GUI functions

    def _send_action(self):
        self._add_message("You",self.widget.textEdit_msg.toPlainText())
        self.widget.textEdit_msg.clear()
        
    
    def _add_message(self, sender, text):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.widget.textEdit_conversation.append(f"<b>[{timestamp}] {sender}:</b> {text}")
        self.widget.textEdit_conversation.moveCursor(QTextCursor.MoveOperation.End)