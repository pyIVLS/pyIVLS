# File: pyIVLS_ant.py
# GUI and functionality for Ai iNTerpreter
#
# ver. 0.1
# ivarad
# 26.08.13
# chat GUI (no LLM connection yet)
# ver. 0.2
# ivarad + chatgpt
# 26.08.14
# Basic chat with asynchronous LLM backend via threadStopped (+ GUI modification)

import logging
from os.path import sep
from datetime import datetime

from PyQt6 import uic
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QTextCursor

from threadStopped import thread_with_exception, ThreadStopped
from LLM.pyIVLS_LLM import pyIVLS_LLM

logger = logging.getLogger(__name__)


class pyIVLS_ant(QObject):

    ### Signals for communication
    info_message = pyqtSignal(str)
    log_message = pyqtSignal(str)

    _llm_finished = pyqtSignal(str)
    _llm_error = pyqtSignal(str)
    _llm_stopped = pyqtSignal()

    def __init__(self, path):
        super().__init__()

        ui_file_name = path + "components" + sep + "pyIVLS_ant.ui"
        self.widget = uic.loadUi(ui_file_name)
        self.path = path
        self.logger = logger

        self.llm = pyIVLS_LLM()
        self.messages = []

        self._llm_thread = None

        self._llm_finished.connect(self._llm_request_finished)
        self._llm_error.connect(self._llm_request_error)
        self._llm_stopped.connect(self._llm_request_stopped)

        self.available_instructions = {}

        self._connect_signals()

    def _connect_signals(self):
        self.widget.pushButton_send.clicked.connect(self._send_action)
        self.widget.pushButton_cancelRequest.clicked.connect(self._cancelRequest_action)

    ### GUI functions

    def _send_action(self):
        text = self.widget.textEdit_msg.toPlainText().strip()
        if not text or self._llm_thread is not None:
            return

        self._add_message("You", text)
        self.widget.textEdit_msg.clear()

        self.messages.append({
            "role": "user",
            "content": text,
        })

        self._setLLMStatus(True)

        messages = list(self.messages)

        self._llm_thread = thread_with_exception(
            self._llm_request,
            messages,
        )
        self._llm_thread.start()

    def _cancelRequest_action(self):
        """Stops the running sequence thread."""
        if hasattr(self, "_llm_thread") and self._llm_thread.is_alive():
            result = self._llm_thread.thread_stop()
            self.logger.info("Stop LLM analysis requested: " + result[1])
        else:
            self.logger.info("No running LLM requests to stop.")
        self._setLLMStatus(False)

    def _setLLMStatus(self, status):
        self.widget.pushButton_send.setEnabled(not status)
        self.widget.pushButton_cancelRequest.setEnabled(status)
        
    ### LLM functions

    def _llm_request(self, messages):
        try:
            answer = self.llm.send(messages)
            self._llm_finished.emit(answer)
        except ThreadStopped:
            self.logger.info("LLM request stopped")
            self._llm_stopped.emit()
        except Exception as exc:
            self.logger.exception("LLM request failed")
            self._llm_error.emit(str(exc))
        finally:
            self._setLLMStatus(False)
            self._llm_thread = None

    @pyqtSlot(str)
    def _llm_request_finished(self, answer):
        self.messages.append({
            "role": "assistant",
            "content": answer,
        })
        self._add_message("ANT", answer)

    @pyqtSlot(str)
    def _llm_request_error(self, error):
        self._add_message("ANT", f"LLM error: {error}")

    @pyqtSlot()
    def _llm_request_stopped(self):
        self._add_message("ANT", "LLM request stopped.")

    def _add_message(self, sender, text):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.widget.textEdit_conversation.append(
            f"<b>[{timestamp}] {sender}:</b> {text}"
        )
        self.widget.textEdit_conversation.moveCursor(
            QTextCursor.MoveOperation.End
        )

    #### Slots for communication with plugins
    @pyqtSlot(dict, list)
    def getPluginFunctions(self, plugin_dict, plugin_functions):
        """Populates the list of available functions for building sequencies. This is called from the container signal "seqComponents_signal".

        Args:
            plugin_dict: dict of available plugins needed to extract class (step or loop)
            plugin_functions: list of available functions returned by plugins
        """
        self.available_instructions = {}
        for plugin in plugin_dict:
            if plugin_dict[plugin]["load"] != "True":
                continue
        for functions in plugin_functions:
            if plugin in functions:
                self.available_instructions[plugin] = {
                "meta": plugin_dict[plugin]["ai_meta"],
                "functions": functions[plugin],
                 }
                break
