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
# ivarad + ai aalto (chatgpt 5.4)
# 26.09.30
# ANT prompts added
# plugin public functions exposed to ANT
# ANT vision added
# ivarad + ai aalto (chatgpt 5.4)
# ver. 0.3

import logging
from os.path import sep
from datetime import datetime

from PyQt6 import uic
from PyQt6.QtWidgets import QMenu
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QPoint, Qt
from PyQt6.QtGui import QTextCursor, QPixmap

from threadStopped import thread_with_exception, ThreadStopped
from LLM.pyIVLS_LLM import LLM_Aalto

import json
import base64
import cv2 as cv
import numpy as np

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

        self.widget = uic.loadUi(path + "components" + sep + "pyIVLS_ant.ui")
        self.visionWidget = uic.loadUi(path + "components" + sep + "ANT_visionWidget.ui")
        self.vision_label = self.visionWidget.ANTVisionLabel
        self.vision_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.vision_label.setScaledContents(False)

        self.path = path
        self.logger = logger

        self.llm = LLM_Aalto()
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

    @pyqtSlot(dict)
    def _update_summary(self, llm_return):
        answer = llm_return.get("message")
        error = llm_return.get("error")
        image = llm_return.get("image")
        if error is not None:
            self.logger.error(error)
        if image is not None:
            self.logger.error("LLM request for summary generation should not generate images")
        if answer is None:
            return
        return self.widget.msgMetaChat_textedit.setPlainText(answer)

    def _get_historyMsgCnt(self):
        return self.widget.msgMetaMsgHistory_spin.value()
    
    def _refresh_pending_actions_widget(self):
        """Rebuild the pending-actions QListWidget from self.pending_actions."""

        self.widget.execList_list.clear()
        for action in self.pending_actions:
            self.widget.execList_list.addItem(f"{action.get('plugin', '')}:{action.get('function', '')}")

    def _autoSummary(self):
        return self.widget.msgMetaChat_auto.isChecked()

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

    def setImage(self, image_base64):
        try:
            # Decode Base64 into the original image bytes.
            image_data = base64.b64decode(image_base64)

            # Let Qt determine whether it is PNG, JPEG, etc.
            pixmap = QPixmap()
            if not pixmap.loadFromData(image_data):
                self.logger.error("Failed to decode generated image.")
                return

            scaled_pixmap = pixmap.scaled(
                self.vision_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )

            self.vision_label.setPixmap(scaled_pixmap)

        except Exception as e:
            self.logger.error(f"Failed to process image generated by ANT: {e}")

    def get_MDI_interface(self):
        return {"ANT": self.visionWidget}
    ### LLM functions

    def _llm_request(self, messages, payload = None):
        try:
            answer = self.llm.send(messages, payload)
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
            answer = self.llm.send(messages, payload = None)
            self._llm_summary_finished.emit(answer)
        except ThreadStopped:
            self.logger.info("LLM summary request stopped")
            self._llm_stopped.emit()
        except Exception as exc:
            self.logger.exception("LLM summary request failed")
            self._llm_error.emit(str(exc))
        finally:
            self._llm_summary_thread = None

    @pyqtSlot(dict)
    def _llm_request_finished(self, llm_return):
        answer = llm_return.get("message")
        error = llm_return.get("error")
        image = llm_return.get("image")
        if error is not None:
            self.logger.log_error(error)
        
        if image is not None:
            self.setImage(image)
            
        if answer is None:
            return
        is_json, payload = self._parse_LLM_json_payload(answer)

        if is_json:
            parsed_message, actions, system_calls = self._extract_LLM_payload_fields(payload)

            if system_calls:
                call_response = self._execute_system_calls_from_LLM(system_calls)

                followup_request = self.build_messages_for_LLM()
                followup_request["system_call_response"] = self._format_system_call_result()

                self._setLLMStatus(True)
                self._llm_thread = thread_with_exception(
                    self._llm_request,
                    followup_request,
                    call_response
                )
                self._llm_thread.start()

            added = []
            rejected = []
            if actions:
                added, rejected = self.add_pending_actions_from_LLM(actions)

            lines = []
            if parsed_message:
                lines.append(parsed_message)

            if added:
                lines.append("Added to pending actions:")
                for action in added:
                    lines.append(
                        f"- {action.get('plugin', '')}:{action.get('function', '')}"
                    )

            if rejected:
                lines.append("Rejected actions:")
                for item in rejected:
                    lines.append(f"- {item.get('error', 'Unknown error')}")

            chat_text = "\n".join(lines).strip()
            if not chat_text:
                chat_text = "JSON payload processed."
        else:
            chat_text = answer

        self.messages.append({
            "role": "assistant",
            "content": chat_text,
        })
        self._add_message("ANT", chat_text)
        self._buildSummary()

    @pyqtSlot(str)
    def _llm_request_error(self, error):
        self._add_message("ANT", f"LLM error: {error}")

    @pyqtSlot()
    def _llm_request_stopped(self):
        self._add_message("ANT", "LLM request stopped.")

    #### functions for parsing LLM returned messages
    def _parse_LLM_json_payload(self, answer):
        """Try to parse LLM answer as JSON payload.

        Supported structure:
        {
            "message": "...",      # optional
            "actions": [ ... ]     # optional
        }

        Returns:
            tuple[bool,  dict]:
                (is_json, payload_dict)
        """
        if not isinstance(answer, str):
            return False, {}

        text = answer.strip()
        if not text:
            return False, {}

        try:
            payload = json.loads(text)
        except Exception:
            return False, {}

        if not isinstance(payload, dict):
            return False, {}

        return True, payload

    def _extract_LLM_payload_fields(self, payload):
        """Extract supported fields from parsed JSON payload."""
        message = payload.get("message", "")
        actions = payload.get("actions", [])
        system_calls = payload.get("system_calls", [])

        if not isinstance(message, str):
            message = str(message)

        if not isinstance(actions, list):
            actions = []

        if not isinstance(system_calls, list):
            system_calls = []

        return message, actions, system_calls

    def _parse_system_call(self, call_obj):
        """Parse one ANT-internal system_call.

        Expected:
        {
            "call": int,
            "type": "action_result",
            "args": int,
            "reason": str
        }
        """
        if not isinstance(call_obj, dict):
            return None, "system_call is not a dict"

        call_id = call_obj.get("call")
        call_type = call_obj.get("type")
        args = call_obj.get("args")
        reason = call_obj.get("reason", "")

        if not isinstance(call_id, int):
            return None, "system_call.call must be int"

        if call_type != "action_result":
            return None, f"Unsupported system_call type: {call_type}"

        if not isinstance(args, int):
            return None, "system_call.args must be action_id integer for type='action_result'"

        if not isinstance(reason, str):
            reason = str(reason)

        return {
            "call": call_id,
            "type": call_type,
            "args": args,
            "reason": reason,
        }, ""

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
        8. optional: system call response
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
            "Your main job is to help the operator perform the needed measurement. "
            "To implement this job you propose structured actions using only the "
            "currently loaded plugins and their public functions.\n\n"
            
            "OUTPUT RULES:\n"
            "- If your reply is only chat to the operator and does not require ANT to do anything, return plain text.\n"
            "- Image or other visual information must be used only when the operator explicitly requests visual information to be returned by ANT.\n"
            "- Do not generate or return an image or other visual information merely because an image could be useful, illustrative, or convenient.\n"
            "- A response may contain at most one image.\n"
            "- When visual information is requested by the operator the image should be returned as base64-encoded text.\n"
            "- If your reply requires ANT to do anything beyond chat, return a valid JSON object and nothing else.\n"
            "- If your reply is JSON object, do not wrap JSON in markdown code fences.\n"
            "- JSON fields are optional. Use only the fields you need.\n"
            "- Supported JSON fields currently are:\n"
            '  "message": optional human-readable text for chat\n'
            '  "actions": optional list of proposed public-function calls\n'
            '  "system_calls": optional list of internal ANT information processing calls\n'
            "- 'actions' are proposed calls to public functions available through the plugin mechanism. Their later execution may require operator validation depending on settings.\n"
            "- 'system_calls' are internal requests for providing ANT with already available but not yet analyzed data, statuses, or logs.\n"
            "- A system_call must return to ANT the requested information, or a note that the information is absent, without requiring a new message from the operator.\n"
            "- If enough relevant information is already available in recent execution results, statuses, or logs, prefer using it instead of proposing actions to obtain new data.\n"
            "- If relevant information is not available to ANT, or if it might be outdated, propose actions to acquire new data for analysis or ask the operator for additional instructions.\n"
            "- ANT may receive an update about the availability of action execution results, new logs or statuses without a new operator message.\n"
            "- If ANT receives an update that new action execution results, logs, or statuses are available, and you were waiting for them, you may use system_calls to request the relevant information without waiting for the next operator input.\n"
            "- Each action object must use this schema:\n"
            "  {\n"
            '    "plugin": "PluginName",\n'
            '    "function": "public_function_name",\n'
            '    "args": {},\n'
            '    "reason": "optional explanation"\n'
            "  }\n"

            "- Each system_call object must use this schema:\n"
            "  {\n"
            '    "call": 1,\n'
            '    "type": "action_result",\n'
            '    "args": 12,\n'
            '    "reason": "this field will be returned back together with the call result. Explanation provided here should be sufficient for ANT to understand\n
                             why this result is needed and what to do with it further."\n'
            "  }\n"
            "- For system_calls, \"call\" is a unique integer identifier chosen by you for relating returned information to the request.\n"
            "- For system_calls with \"type\": \"action_result\", \"args\" must be the integer corresponding to the action_id in the execution results list. This identifies the raw result that should be provided to ANT.\n"
            "- For system_calls with \"type\": \"action_result\", request them only for action_ids that already exist in the recent execution results list.\n"
            "- Currently the only supported system_call type is \"action_result\".\n"
            "- Do not request system_calls repeatedly in a chain.\n"
            "- Do not request another system_call from a system_call result. After receiving a system_call result, either answer the operator or propose actions.\n"

            
            "Rules:\n"
            "- Use only plugins and functions explicitly provided in the tool summary.\n"
            "- If a plugin is marked unavailable for LLM use, ignore it for planning.\n"
            "- Do not invent plugin names, function names, settings, or device states.\n"
            "- Dynamic state may change outside ANT and must not be assumed unless checked.\n"
            "- If information is missing, ask for clarification or state the limitation.\n"
            "- Prefer short, truthful, technically precise answers.\n"
            "- If the user asks to perform an operation, prefer proposing structured actions "
            "rather than claiming execution has already happened.\n"
            "- Actions may be proposed, but execution must not be assumed.\n"
            "- The user may provide additional rules, but new rules should not contradict existing ones.\n"
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

    def _format_system_call_result(self):
        """Format context blocks explicitly added by the user.

        Context is meant to be active supporting information relevant now.
        """

        system_call_prompt = (
            "SYSTEM CALL RESULT\n"
            "The following content contains the results of one or more system_calls submitted in the previous message.\n"
            "The results are generated automatically from data already available to ANT.\n"
            "No additional input from the operator is involved.\n"
            "Each system call result is represented by a JSON object with the following general structure: \n"
            "{\n"
            "\"system_call_result\": {\n"
            "    \"call\": call_id, \n"
            "    \"action_id\": action_id,\n"
            "    \"plugin\": plugin,\n"
            "    \"function\": function,\n"
            "    \"action_execution_status\": status,\n"
            "    \"action_execution_summary\": summary,\n"
            "    \"payload_type\": payload_type,\n"
            "    \"payload\": payload,\n"
            "    \"reason\": reason,\n"
            "    \"system_call_status\": \"success\",\n"
            "    \"system_call_error\": \"\"\n"
            "    }\n"
            "}\n"
            "Fields are optional unless explicitly stated otherwise.\n"
            "Field meanings:\n"
            " call: Optional. If the system_call was successfully unpacked, contains the unique call identifier from the original system_call.\n"
            " action_id: Optional. If the system_call was successfully unpacked, contains the action identifier (args) from the original system_call.\n"
            " plugin: Optional. If the system_call was successfully unpacked and is of action_result type, contains the name of the plugin from which the function was executed.\n"
            " function: Optional. If the system_call was successfully unpacked and is of action_result type, contains the name of the function that was executed.\n"
            " action_execution_status: Optional. Describes the execution status of the function named in the function field. Possible values are \"success\" or \"failed\".\n"
            " action_execution_summary: Optional. A textual description of the action execution result, including relevant execution errors when applicable.\n"
            " payload_type: Optional. Describes the type of data returned by the executed function. If this value is \"img\", an image input immediately follows this system_call_result and belongs to this result.\n"
            " payload: Optional. Contains data returned by the executed function when action_execution_status is \"success\" and payload_type is not \"img\". This field is absent when payload_type is \"img\".\n"
            " reason: Optional. If the system_call was successfully unpacked, contains the reason from the original system_call. This field is intended to provide ANT with sufficient information to understand why the result was requested and how the returned information should be interpreted, processed, or used further. Use this information together with the other fields of the system_call_result when determining how to process the result.\n"
            " system_call_status: Mandatory. Describes whether the system_call itself was successfully processed. Possible values are \"success\" or \"failed\". Successful processing of the system_call does not automatically mean that the requested information was successfully obtained. Availability of the requested information should be determined from the other fields of this structure.\n"
            " system_call_error: Mandatory. If system_call_status is \"failed\", contains a textual description of the system_call processing error. Otherwise it is empty.\n"
            "\n\n"
            "Multiple system_call_result objects may be provided, one for each system_call submitted in the previous message.\n"
            "IMPORTANT IMAGE ASSOCIATION RULE:\n"
            "If a system_call_result has \"payload_type\": \"img\", the next image input belongs to that system_call_result. The image and the immediately preceding system_call_result therefore form one result pair. Do not associate an image with any other system_call_result.\n"
            "IMPORTANT INTERPRETATION RULES:\n"
            "1. system_call_status and action_execution_status describe different stages of processing and should be interpreted separately.\n"
            "2. system_call_status=\"success\" means that the system_call was successfully processed; it does not by itself mean that the requested function was successfully executed or that the requested information is available.\n"
            "3. action_execution_status=\"success\" indicates successful execution of the function, but the returned payload should still be inspected to determine what information was actually returned.\n"
            "4. Missing optional fields should not by themselves be interpreted as errors or failures.\n"
            "5. Do not invent or assume specific data values that are not present in the system_call_result or its associated image.\n"
            "6. The reason field is provided by the ANT and sent in original system_call, it is intended to explain the purpose of the request and the intended further use of the result. Consider the reason together with the returned data, execution status, and other available information when processing the result.\n"
            )

            return system_call_prompt

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
            "- Do not return images or any visual data.\n"
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
            return f"Returned list/tuple of length {len(raw_result)}."

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
    
    # system call helpers
    def _find_execution_result_by_action_id(self, action_id):
        """Find execution result object by action_id."""
        for result in reversed(self.execution_results):
            if result.get("action_id") == action_id:
                return result
        return None
    
    def _execute_system_calls_from_LLM(self, system_calls):
        """Execute ANT-internal system calls.

        System calls do not call plugin functions.
        They only retrieve already available ANT-side data.

        Returns:
            [dict]
                
            each dict has optional fields,
            see _process_raw_result_for_LLM for details
            system_call_status of the dict - should be present always. Always check it is success|failed
        """
        context_blocks = []

        if not isinstance(system_calls, list):
            context = {
                "system_call_result": {
                    "system_call_status": "failed",
                    "system_call_error":"system_calls payload is not a list.",
                }
            }
            return [context]

        for call_obj in system_calls:
            call, error = self._parse_system_call(call_obj)

            if error:
                context = {
                    "system_call_result": {
                        "system_call_status": "failed",
                        "system_call_error":error,
                    }
                }
                context_blocks.append(context)
                continue

            call_id = call["call"]
            call_type = call["type"]
            action_id = call["args"]
            reason = call["reason"]

            if call_type == "action_result":
                result = self._find_execution_result_by_action_id(action_id)

                if result is None:
                    context = {
                        "system_call_result": {
                            "call": call_id,
                            "action_id": action_id,
                            "reason": reason,
                            "system_call_status": "failed",
                            "system_call_error":"No execution result found for action_id",
                        }
                    }
                    context_blocks.append(context)
                    continue

            context = self._process_raw_result_for_LLM(result)
            context["system_call_result"]["reason"] = reason
            context["system_call_result"]["call"] = call_id
            context_blocks.append(context)

        return context_blocks

    def _process_raw_result_for_LLM(self, result_obj):
        """Convert raw execution result into machine-readable LLM context and payloads.

        Returns: 
            dict of a form:
                {"call": call_id,
                "action_id": action_id,
                "plugin": plugin,
                "function": function,
                "action_execution_status": status,
                "action_execution_summary": summary,
                "payload_type": raw_type,
                "payload":raw_result,
                "reason":reason,
                "system_call_status": "success",
                "system_call_error": "",}
            !!!fields are optional, presence of the field must be checked before use

        """
        action_id = result_obj.get("action_id")
        plugin = result_obj.get("plugin", "")
        function = result_obj.get("function", "")
        status = result_obj.get("status", "")
        summary = result_obj.get("result_summary", "")
        raw_result = result_obj.get("raw_result", None)

        # Case 1: camera image
        if self._is_camera_capture_result(result_obj):
            image = self._extract_image_from_camera_result(raw_result)

            if image is not None:
                image_payload = self._encode_image_for_LLM(image)

                if image_payload is not None:
                    context = {
                        "system_call_result": {
                            "action_id": action_id,
                            "plugin": plugin,
                            "function": function,
                            "action_execution_status": status,
                            "action_execution_summary": summary,
                            "payload_type": "img",
                            "payload":image_payload,
                            "system_call_status": "success",
                            "system_call_error":"",
                        }
                    }

                    return context

            context = {
                "system_call_result": {
                    "action_id": action_id,
                    "plugin": plugin,
                    "function": function,
                    "action_execution_status": status,
                    "action_execution_summary": summary,
                    "payload_type": "None",
                    "system_call_status": "failed",
                    "system_call_error": "Camera capture action found, but no encodable image was available.",
                }
            }

            return context

        # Case 2: generic / unsupported raw result
        raw_type = type(raw_result).__name__

        context = {
            "system_call_result": {
                "action_id": action_id,
                "plugin": plugin,
                "function": function,
                "action_execution_status": status,
                "action_execution_summary": summary,
                "payload_type": raw_type,
                "payload":raw_result,
                "system_call_status": "success",
                "system_call_error": "",
            }
        }

        return context
    
    # functions for image messages
    def _extract_image_from_camera_result(self, raw_result):
        """Extract RGB image from camera_capture_image raw result.

        Expected:
            (status, image_or_error)
            [status, image_or_error]
        """
        if raw_result is None:
            return None

        if isinstance(raw_result, np.ndarray):
            return raw_result

        if isinstance(raw_result, (list, tuple)) and len(raw_result) >= 2:
            status = raw_result[0]
            payload = raw_result[1]

            if (
                isinstance(status, int)
                and status == 0
                and isinstance(payload, np.ndarray)
            ):
                return payload

        return None
    
    def _encode_image_for_LLM(self, image):
        """Encode RGB numpy image as base64 JPEG for LLM input."""
        if image is None:
            return None

        if not isinstance(image, np.ndarray):
            return None

        # Camera image is RGB, OpenCV imencode expects BGR.
        if image.ndim == 3 and image.shape[2] == 3:
            image_to_encode = cv.cvtColor(image, cv.COLOR_RGB2BGR)
        else:
            image_to_encode = image

        ok, buffer = cv.imencode(".jpg", image_to_encode)
        if not ok:
            return None

        base64_image = base64.b64encode(buffer).decode("utf-8")

        return base64_image

    def _is_camera_capture_result(self, result_obj):
        """Return True if execution result is from a camera image capture action."""
        plugin = result_obj.get("plugin", "")
        function = result_obj.get("function", "")

        if function != "camera_capture_image":
            return False

        plugin_info = self.available_instructions.get(plugin, {})
        plugin_data = plugin_info.get("plugin_data", {})
        llm_data = plugin_info.get("LLM_data", {})

        plugin_function = plugin_data.get("function", "")
        llm_function = llm_data.get("function", "")

        return plugin_function == "camera" or llm_function == "camera"