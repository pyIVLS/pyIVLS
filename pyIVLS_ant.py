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

import json

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
        """Populate ANT instruction registry from loaded plugins and their public functions.

        Args:
            plugin_dict (dict): plugin -> plugin metadata dict
            plugin_functions (list): list of dicts returned by plugins via get_functions()
        """
        self.available_instructions = {}

        for plugin_name, pdata in plugin_dict.items():

            # ANT should only see loaded plugins
            if pdata.get("load") != "True":
                continue
            
            # Build ANT-side structure:
            # - raw plugin data
            # - raw callable functions
            # - parsed ai_meta
            # - LLM-facing prepared data
            parsed_ai_meta = self._parse_ai_meta(pdata.get("ai_meta", ""), plugin_name)
            for single_dict in plugin_functions:
                for name, methods in single_dict.items():
                    if name == plugin_name:
                        plugin_methods = methods
                        break

            llm_data = self._build_LLM_data(plugin_name, pdata, plugin_methods, parsed_ai_meta)
            self.available_instructions[plugin_name] = {
                "plugin_data": pdata,
                "functions": plugin_methods,
                "ai_meta": parsed_ai_meta,
                "LLM_data": llm_data,
            }

    def _parse_ai_meta(self, ai_meta_raw, plugin_name):
        """Parse raw ai_meta JSON string into dict.

        Args:
            ai_meta_raw (str | dict): raw ai_meta from plugin_dict
            plugin_name (str): plugin name for logging

        Returns:
            dict: parsed ai_meta, or {} on failure/missing data
        """
        if not ai_meta_raw:
            return {}

        if isinstance(ai_meta_raw, dict):
            return ai_meta_raw

        if not isinstance(ai_meta_raw, str):
            self.logger.warning(
                f"ai_meta for plugin '{plugin_name}' has unsupported type "
                f"{type(ai_meta_raw).__name__}. Ignoring."
            )
            return {}

        try:
            parsed = json.loads(ai_meta_raw)
            if isinstance(parsed, dict):
                return parsed
            self.logger.warning(
                f"ai_meta for plugin '{plugin_name}' is valid JSON but not a dict. Ignoring."
            )
            return {}
        except Exception as exc:
            self.logger.warning(
                f"Failed to parse ai_meta for plugin '{plugin_name}': {exc}"
            )
            return {}

    def _build_LLM_data(self, plugin_name, plugin_data, functions_dict, ai_meta):
        """Build LLM-facing data for one plugin.

        This does not modify ai_meta. It creates a normalized structure ANT can
        later send to the LLM.

        Args:
            plugin_name (str): plugin name
            plugin_data (dict): plugin metadata from plugin_dict
            functions_dict (dict): actual loaded public functions
            ai_meta (dict): parsed ai_meta

        Returns:
            dict: normalized LLM-facing plugin description
        """
        llm_data = {
            "plugin_name": plugin_name,
            "type": plugin_data.get("type", ""),
            "function": plugin_data.get("function", ""),
            "class": plugin_data.get("class", ""),
            "version": plugin_data.get("version", ""),
            "dependencies": plugin_data.get("dependencies", ""),
            "loaded": plugin_data.get("load", "") == "True",
            "llm_available": False,
            "llm_availability_note": "",
            "description": "",
            "keywords": [],
            "capabilities": [],
            "dynamic_state_note": "",
            "settings_note": "",
            "public_functions": {},
            "tool_summary": "",
        }

        # If ai_meta is missing, ANT should communicate this to the LLM-facing layer
        # rather than trying to infer too much on its own.
        if not ai_meta:
            llm_data["llm_available"] = False
            llm_data["llm_availability_note"] = (
                "This plugin is loaded in pyIVLS but is not available for LLM use "
                "because ai_meta is missing or invalid. Ignore it when planning actions."
            )
            llm_data["tool_summary"] = self._build_missing_ai_tool_summary(llm_data)
            return llm_data

        llm_data["llm_available"] = True
        llm_data["description"] = ai_meta.get("description", "")
        llm_data["keywords"] = ai_meta.get("keywords", [])
        llm_data["capabilities"] = ai_meta.get("capabilities", [])
        llm_data["dynamic_state_note"] = ai_meta.get("dynamic_state_note", "")
        llm_data["settings_note"] = ai_meta.get("settings_note", "")

        # Only expose functions that actually exist in loaded public functions.
        # If ai_meta describes extra functions, they are ignored here.
        ai_public = ai_meta.get("public_functions", {})
        public_functions = {}

        if isinstance(ai_public, dict):
            for fn_name, fn_meta in ai_public.items():
                if fn_name not in functions_dict:
                    continue

                if isinstance(fn_meta, str):
                    public_functions[fn_name] = {
                        "description": fn_meta
                    }
                elif isinstance(fn_meta, dict):
                    public_functions[fn_name] = fn_meta
                else:
                    public_functions[fn_name] = {
                        "description": ""
                    }

        # If ai_meta missed some real functions, still include them as callable but undocumented.
        for fn_name in functions_dict:
            if fn_name not in public_functions:
                public_functions[fn_name] = {
                    "description": "No ai_meta description available for this public function."
                }

        llm_data["public_functions"] = public_functions
        llm_data["tool_summary"] = self._build_plugin_tool_summary(llm_data)

        return llm_data


    def _build_missing_ai_tool_summary(self, llm_data):
        """Build short LLM-facing summary for a loaded plugin with missing ai_meta."""
        lines = [
            f"Plugin: {llm_data.get('plugin_name', '')}",
            f"Role: {llm_data.get('function', '')}",
            "LLM availability: unavailable",
            llm_data.get("llm_availability_note", ""),
          ]
        return "\n".join(line for line in lines if line)

    def _build_plugin_tool_summary(self, llm_data):
        """Build compact tool summary text for one plugin."""
        lines = [
            f"Plugin: {llm_data.get('plugin_name', '')}",
            f"Role: {llm_data.get('function', '')}",
        ]

        description = llm_data.get("description", "")
        if description:
            lines.append(f"Description: {description}")

        keywords = llm_data.get("keywords", [])
        if keywords:
            lines.append("Keywords: " + ", ".join(str(k) for k in keywords))

        capabilities = llm_data.get("capabilities", [])
        if capabilities:
            lines.append("Capabilities:")
            for cap in capabilities:
                lines.append(f"- {cap}")

        public_functions = llm_data.get("public_functions", {})
        if public_functions:
            lines.append("Public functions:")
            for fn_name, fn_meta in public_functions.items():
                if isinstance(fn_meta, dict):
                    fn_desc = fn_meta.get("description", "")
                else:
                    fn_desc = str(fn_meta)
                lines.append(f"- {fn_name}: {fn_desc}")

        dynamic_note = llm_data.get("dynamic_state_note", "")
        if dynamic_note:
            lines.append(f"Dynamic state note: {dynamic_note}")

        settings_note = llm_data.get("settings_note", "")
        if settings_note:
            lines.append(f"Settings note: {settings_note}")

        return "\n".join(lines)

    def build_all_LLM_tools_summary(self):
        """Build a combined summary of all loaded plugins for the LLM."""
        if not self.available_instructions:
            return "No loaded plugins are currently available."

        parts = []
        for plugin_name, pdata in self.available_instructions.items():
            llm_data = pdata.get("LLM_data", {})
            summary = llm_data.get("tool_summary", "")
            if summary:
              parts.append(summary)

        if not parts:
            return "No loaded plugins are currently available."

        return "\n\n".join(parts)
