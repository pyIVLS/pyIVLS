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
from PyQt6.QtWidgets import QMenu
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QPoint, Qt
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
    _llm_summary_finished = pyqtSignal(str)
    _llm_error = pyqtSignal(str)
    _llm_stopped = pyqtSignal()

    def __init__(self, path):
        super().__init__()

        ui_file_name = path + "components" + sep + "pyIVLS_ant.ui"
        self.widget = uic.loadUi(ui_file_name)
        self.path = path
        self.logger = logger

        self.llm = pyIVLS_LLM()
        self.messages = []              # full raw chat history
        self.chat_summary = ""          # compact running summary
        self.llm_context_blocks = []    # user-added context blocks
        self.llm_history_blocks = []    # user-added history blocks
        self.last_n_messages = self._get_historyMsgCnt()        # default for now, user may change it
        
        self.pending_actions = []
        self.executed_actions = []
        self.execution_results = []
        self._next_action_id = 1

        
        #initialize interactivness of execList_list widget
        # Enable drag & drop reordering
        self.widget.execList_list.setDragDropMode(
            self.widget.execList_list.DragDropMode.InternalMove
        )

        self.widget.execList_list.setDefaultDropAction(
            Qt.DropAction.MoveAction
        )

        # Enable right-click context menu
        self.widget.execList_list.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )

        self.widget.execList_list.customContextMenuRequested.connect(
            self.show_exec_list_menu
        )
        
        self._llm_thread = None
        self._llm_summary_thread = None

        self._llm_finished.connect(self._llm_request_finished)
        self._llm_summary_finished.connect(self._update_summary)
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

        messages = self.build_messages_for_LLM()

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

    def _get_chat_summary(self):
        return self.widget.msgMetaChat_textedit.toPlainText()

    def _get_context(self):
        return self.widget.msgMetaContext_textedit.toPlainText()

    def _get_pinned_history(self):
        return self.widget.msgMetaPinned_textedit.toPlainText()

    @pyqtSlot(str)
    def _update_summary(self, answer):
        return self.widget.msgMetaChat_textedit.setPlainText(answer)

    def _get_historyMsgCnt(self):
        return self.widget.msgMetaMsgHistory_spin.value()
    
    def _refresh_pending_actions_widget(self):
        """Rebuild the pending-actions QListWidget from self.pending_actions."""

        self.widget.execList_list.clear()
        for action in self.pending_actions:
            self.widget.execList_list.addItem(f"{action.get('plugin', '')}:{action.get('function', '')}")

    @pyqtSlot(QPoint)
    def show_exec_list_menu(self, position):
        list_widget = self.widget.execList_list

        # Find the item that was right-clicked
        item = list_widget.itemAt(position)

        # No item under cursor
        if item is None:
            return

        # Select the item
        list_widget.setCurrentItem(item)

        # Create menu
        menu = QMenu(list_widget)

        option1 = menu.addAction("Delete")
        option2 = menu.addAction("Execute")
        option3 = menu.addAction("Execute all")

        # Show menu
        action = menu.exec(
            list_widget.mapToGlobal(position)
        )

        # Call functions
        if action == option1:
            self.delete_pending_action(list_widget.currentRow())

        elif action == option2:
            self.execute_pending_action(list_widget.currentRow())

        elif action == option3:
            self.execute_all_pending_actions()
            
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

    def _llm_summary_request(self, messages):
        try:
            answer = self.llm.send(messages)
            self._llm_summary_finished.emit(answer)
        except ThreadStopped:
            self.logger.info("LLM summary request stopped")
            self._llm_stopped.emit()
        except Exception as exc:
            self.logger.exception("LLM summary request failed")
            self._llm_error.emit(str(exc))
        finally:
            self._llm_summary_thread = None

    @pyqtSlot(str)
    def _llm_request_finished(self, answer):
        self.messages.append({
            "role": "assistant",
            "content": answer,
        })
        self._add_message("ANT", answer)
        self._buildSummary()

    @pyqtSlot(str)
    def _llm_request_error(self, error):
        self._add_message("ANT", f"LLM error: {error}")

    @pyqtSlot()
    def _llm_request_stopped(self):
        self._add_message("ANT", "LLM request stopped.")

    #### functions for creating LLM message

    def build_messages_for_LLM(self):
        """Build the message list sent to the LLM.

        Order:
        1. system prompt
        2. tool summary
        3. chat summary
        4. optional context blocks
        5. optional history blocks
        6. action state
        7. last N chat messages
        """
        
        request = {
            "system_blocks": [],
            "context_blocks": [],
            "history_blocks": [],
            "action_state": "",
            "recent_messages": [],
        }


        system_prompt = self._build_system_prompt()
        if system_prompt:
            request["system_blocks"].append(system_prompt)

        tool_summary = self.build_all_LLM_tools_summary()
        if tool_summary:
            request["system_blocks"].append(
                self._format_tool_summary(tool_summary)
            )

        self.chat_summary = self._get_chat_summary()
        if self.chat_summary:
            request["system_blocks"].append(
                self._format_chat_summary(self.chat_summary)
            )

        context_text = self._get_context()
        if context_text:
            request["context_blocks"].append(
                self._format_context_blocks(context_text)
            )

        history_text = self._get_pinned_history()
        if history_text:
            request["history_blocks"].append(
                self._format_history_blocks(history_text)
            )
            
        action_state_text = self._format_action_state_for_LLM()
        if action_state_text:
            request["action_state"] = action_state_text

        request["recent_messages"] = self._get_last_n_messages()

        return request
    

    def _build_system_prompt(self):
        """Return the stable ANT system prompt.

        This should be included in every LLM request.
        """
        return (
            "You are ANT (Ai iNTerpreter) inside pyIVLS measurement software.\n\n"
            "pyIVLS is a plugin-based measurement software environment. "
            "It works through loaded plugins that expose standardized public functions. "
            "Some plugins represent hardware devices such as cameras or source-measure units, "
            "and some plugins represent higher-level scripts or procedures.\n\n"
            "Your main job is to help the operator to perform the needed measurement. "
            "To implement this job you propose structured actions using only the "
            "currently loaded plugins and their public functions.\n\n"
            "Rules:\n"
            "- Use only plugins and functions explicitly provided in the tool summary.\n"
            "- If a plugin is marked unavailable for LLM use, ignore it for planning.\n"
            "- Do not invent plugin names, function names, settings, or device states.\n"
            "- Dynamic state may change outside ANT and must not be assumed unless checked.\n"
            "- If information is missing, ask for clarification or state the limitation.\n"
            "- Prefer short, truthful, technically precise answers.\n"
            "- If the user asks to perform an operation, prefer proposing structured actions "
            "rather than claiming execution has already happened.\n"
            "- Sequence creation may be proposed, but execution must not be assumed.\n"
        )

    def _format_tool_summary(self, tool_summary):
        return (
            "AVAILABLE TOOLS AND PLUGINS\n"
            "The following plugins are currently loaded and visible to ANT.\n"
            "Use only the functions explicitly listed below.\n\n"
            f"{tool_summary}"
        )

    def _format_chat_summary(self, summary):
        return (
            "CHAT SUMMARY\n"
            "This is a compact summary of earlier conversation. "
            "Use it as background context, but prefer the most recent user messages "
           "if there is a conflict.\n\n"
           f"{summary}"
        )

    def _format_context_blocks(self,context):
        """Format context blocks explicitly added by the user.

        Context is meant to be active supporting information relevant now.
        """

        return (
            "ADDITIONAL CONTEXT\n"
            "The following context was explicitly added for the current discussion. "
            "Use it when relevant.\n"
            f"{context}"
        )

    def _format_history_blocks(self, pinned_history):
        """Format history blocks explicitly restored by the user.

        History is older conversation/data that may be useful but is lower priority
        than current context and recent messages.
        """
        
        return (
            "SELECTED HISTORY\n"
            "The following older history was explicitly restored into the current LLM request. "
            "Use it as background information if relevant.\n"
            f"{pinned_history}"
        )

    def _format_action_state_for_LLM(self):
        """Return action-state block for inclusion in LLM messages."""
        parts = [
            "ACTION STATE",
            "In this context, an action means a proposed or executed call to one of the available public functions of a loaded plugin.",
            "ANT may add such actions to a pending list, and the operator may execute, delete, or reorder them.",
            "Use this information to avoid repeating already pending or already executed plugin-function calls.",
            ""
        ]

        if self.pending_actions:
            parts.append("Pending actions:")
            for action in self.pending_actions:
                parts.append(
                    f"- [{action.get('id')}] "
                    f"{action.get('plugin')}:{action.get('function')} "
                    f"args={action.get('args', {})}"
                )
        else:
            parts.append("Pending actions: none")

        parts.append("")

        if self.executed_actions:
            parts.append("Executed actions:")
            for action in self.executed_actions[-20:]:
                parts.append(
                    f"- [{action.get('id')}] "
                    f"{action.get('plugin')}:{action.get('function')} "
                    f"status={action.get('status')}"
                )
        else:
            parts.append("Executed actions: none")

        parts.append("")

        if self.execution_results:
            parts.append("Recent execution results:")
            for result in self.execution_results[-20:]:
                parts.append(
                    f"- action_id={result.get('action_id')} "
                    f"status={result.get('status')} "
                    f"summary={result.get('result_summary')}"
                )
        else:
            parts.append("Recent execution results: none")

        return "\n".join(parts)

    def _get_last_n_messages(self):
        """Return the last N chat messages from full conversation history."""
        last_n_messages = self._get_historyMsgCnt()

        # Take a somewhat larger window than the normal prompt window
        summary_window = min(last_n_messages*2, len(self.messages))
        return list(self.messages[-summary_window:])

    #### helpers for creating LLM message

    def _buildSummary(self):
        """Update chat summary if autosummary is enabled and enough
        new messages accumulated.

        Summary is built from:
        - previous chat summary
        - current tool summary
        - recent raw conversation messages
        """
        if self.last_n_messages>0:
            self.last_n_messages = self.last_n_messages - 1
        
        if (not self._autoSummary()) or self.last_n_messages>0:
            return

        # Take a somewhat larger window than the normal prompt window
        recent_messages = self._get_last_n_messages()

        tool_summary = self.build_all_LLM_tools_summary()

        summary_prompt = (
            "You are maintaining a compact running summary for ANT, where ANT means "
            "'Ai iNTerpreter', an AI assistant integrated into pyIVLS.\n\n"
            "pyIVLS is a plugin-based measurement software environment. "
            "Loaded plugins provide standardized public functions for hardware devices "
            "and higher-level procedures.\n\n"
            "Update the summary using the previous summary and the recent conversation.\n\n"
            "Keep only information that may matter later, such as:\n"
            "- current user goal\n"
            "- relevant plugins, tools, or device roles\n"
            "- constraints or safety requirements\n"
            "- assumptions already established\n"
            "- unresolved questions\n"
            "- proposed or approved actions\n\n"
            "Rules:\n"
            "- Be concise.\n"
            "- Do not invent facts.\n"
            "- Preserve important technical decisions.\n"
            "- Prefer facts over conversational phrasing.\n"
            "- Return only the updated summary text.\n"
              )

        summary_request = {
            "system_blocks": [summary_prompt],
            "context_blocks": [],
            "history_blocks": [],
            "action_state": "",
            "recent_messages": list(recent_messages),
        }

        if tool_summary:
            summary_request["system_blocks"].append(
                "AVAILABLE TOOLS AND PLUGINS\n"
                "The following plugins are currently loaded and visible to ANT.\n"
                "Use this only as reference for interpreting the conversation.\n\n"
                f"{tool_summary}"
            )

        self.chat_summary = self._get_chat_summary()
        if self.chat_summary:
            summary_request["system_blocks"].append(
                "PREVIOUS SUMMARY\n"
                "Update and compress the following summary using the recent messages.\n\n"
                f"{self.chat_summary}"
            )

        self._llm_summary_thread = thread_with_exception(
            self._llm_summary_request,
            summary_request,
        )
        self._llm_summary_thread.start()


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
            plugin_methods = {}
            found = False
            for single_dict in plugin_functions:
                for name, methods in single_dict.items():
                    if name == plugin_name:
                        plugin_methods = methods
                        found = True
                        break
                if found:
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
    
    #### Action lists/objects helpers

    def _make_action_object(self, plugin, function, args=None, reason="", source="llm"):
        """Create one internal action object."""
        if args is None:
            args = {}

        action = {
            "id": self._next_action_id,
            "plugin": plugin,
            "function": function,
            "args": args,
            "reason": reason,
            "source": source,
            "status": "pending",   # pending / executed / failed / deleted
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
        self._next_action_id += 1
        return action
    
    def _validate_action_dict(self, action_dict):
        """Validate one proposed action against loaded plugin callables.

           Note: mainly overkill, all that is included here should already be checked
           by plugin contaner or excluded in ant if ai_meta is missing.
           This is mainly a double shield for autonomous use.


        Expected input:
        {
            "plugin": "...",
            "function": "...",
            "args": {...},
            "reason": "..."
        }
        """
        if not isinstance(action_dict, dict):
            return False, "Action is not a dict."

        plugin = action_dict.get("plugin")
        function = action_dict.get("function")
        args = action_dict.get("args", {})

        if not plugin:
            return False, "Missing plugin."
        if not function:
            return False, "Missing function."
        if plugin not in self.available_instructions:
            return False, f"Unknown or unavailable plugin: {plugin}"

        llm_data = self.available_instructions[plugin].get("LLM_data", {})
        if not llm_data.get("llm_available", False):
            return False, f"Plugin '{plugin}' is loaded but not available for LLM use."
        
        functions = self.available_instructions[plugin].get("functions", {})
        if function not in functions:
            return False, f"Unknown function '{function}' for plugin '{plugin}'."

        if not isinstance(args, dict):
            return False, "Action args must be a dict."

        return True, "OK"

    def add_pending_actions_from_LLM(self, actions):
        """Validate and add LLM-proposed actions to the pending queue.

        Args:
            actions (list): list of dicts with keys plugin/function/args/reason

        Returns:
            tuple[list,  list]: (added_actions, rejected_actions)
        """
        added = []
        rejected = []

        if not isinstance(actions, list):
            return added, [{"error": "Actions payload is not a list."}]

        for action_dict in actions:
            ok, msg = self._validate_action_dict(action_dict)
            if not ok:
                rejected.append({
                    "action": action_dict,
                    "error": msg,
                })
                continue

            action = self._make_action_object(
                plugin=action_dict.get("plugin", ""),
                function=action_dict.get("function", ""),
                args=action_dict.get("args", {}),
                reason=action_dict.get("reason", ""),
                source="llm",
            )
            self.pending_actions.append(action)
            added.append(action)

        self._refresh_pending_actions_widget()
        return added, rejected

    def delete_pending_action(self, index):
        """Delete one pending action by index."""
        if index < 0 or index >= len(self.pending_actions):
            return False

        action = self.pending_actions.pop(index)
        action["status"] = "deleted"
        self._refresh_pending_actions_widget()
        return True
    
    def execute_pending_action(self, index):
        """Execute one pending action by index.

        Returns:
            dict: execution result object
        """
        if index < 0 or index >= len(self.pending_actions):
            return {
                "status": "error",
                "result_summary": "Invalid pending action index."
            }

        action = self.pending_actions.pop(index)
        plugin = action.get("plugin", "")
        function = action.get("function", "")
        args = action.get("args", {})

        result_obj = {
            "action_id": action.get("id"),
            "plugin": plugin,
            "function": function,
            "status": "error",
            "result_summary": "",
            "raw_result": None,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }

        try:
            func = self.available_instructions[plugin]["functions"][function]

            if args:
                raw_result = func(**args)
            else:
                raw_result = func()

            result_obj["raw_result"] = raw_result
            interpreted_status, interpreted_summary = self._interpret_plugin_result(raw_result)

            result_obj["status"] = interpreted_status
            result_obj["result_summary"] = interpreted_summary

            if interpreted_status == "success":
                action["status"] = "executed"
            else:
                action["status"] = "failed"

            self.executed_actions.append(action)

        except Exception as exc:
            action["status"] = "failed"
            result_obj["status"] = "failed"
            result_obj["result_summary"] = f"{type(exc).__name__}: {exc}"
            self.executed_actions.append(action)

        self.execution_results.append(result_obj)
        self._refresh_pending_actions_widget()
        return result_obj
    
    def execute_all_pending_actions(self):
        """Execute all currently pending actions in order.

        Returns:
            list: list of execution result objects
        """
        results = []
        while self.pending_actions:
            result = self.execute_pending_action(0)
            results.append(result)
        return results
    
    def _summarize_execution_result(self, raw_result):
        """Convert raw execution result into short text for LLM/context."""
        if raw_result is None:
            return "Function executed successfully."

        if isinstance(raw_result, (str, int, float, bool)):
            return f"Returned: {raw_result}"

        if isinstance(raw_result, (list, tuple)):
            if len(raw_result) == 2:
                return f"Returned pair: {raw_result[0]}, {raw_result[1]}"
            return f"Returned list/tuple of length {len(raw_result)}.

        if isinstance(raw_result, dict):
            return f"Returned dict with keys: {', '.join(raw_result.keys())}"

        return f"Returned object of type {type(raw_result).__name__}"
    
    def _interpret_plugin_result(self, raw_result):
        """Interpret plugin return value.

        Returns:
            tuple[str,  str]:
                ("success" | "failed", summary_text)
        """
        if raw_result is None:
            return "success", "Function executed successfully."

        if isinstance(raw_result, (list, tuple)):
            # Common pyIVLS style: [status,  payload] or (status, payload)
            if len(raw_result) >= 2 and isinstance(raw_result[0], int):
                status_code = raw_result[0]
                payload = raw_result[1]

                if status_code == 0:
                    return "success", self._summarize_execution_result(raw_result)

                # non-zero status means failure
                if isinstance(payload, dict) and "Error message" in payload:
                    return "failed", f"Error {status_code}: {payload['Error message']}"
                return "failed", f"Error {status_code}: {payload}"

        # Fallback: if no explicit status code is found, treat as success
        return "success", self._summarize_execution_result(raw_result)