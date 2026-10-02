# File: LLM_Aalto.py
#
# Generic Aalto OpenAI API backend.
# This module is independent of pyIVLS.

import os
import httpx
from openai import OpenAI
import json


class LLM_Aalto:
    """Backend for the Aalto OpenAI Responses API."""

    BASE_URL = "https://aalto-openai-apigw.azure-api.net"
    RESPONSES_PATH = "/v1/openai/responses"
#    DEFAULT_MODEL = "gpt-5-2025-08-07"
    DEFAULT_MODEL = "gpt-5-nano-2025-08-07"

    def __init__(self, model=None, api_key=None):
        api_key = api_key or os.environ.get("AALTO_OPENAI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "AALTO_OPENAI_API_KEY environment variable is not set."
            )

        self.model = model or os.environ.get(
            "AALTO_OPENAI_MODEL",
            self.DEFAULT_MODEL,
        )

        def update_base_url(request: httpx.Request) -> None:
            request.url = request.url.copy_with(
                path=self.RESPONSES_PATH
            )

        self.client = OpenAI(
            base_url=self.BASE_URL,
            api_key='not-used',
            default_headers={
                "Ocp-Apim-Subscription-Key": api_key,
            },
            http_client=httpx.Client(
                event_hooks={
                    "request": [update_base_url]
                }
            ),
        )

    def send(self, request_obj, payload):
        messages = self._convert_to_LLM_specific_messages(request_obj, payload)

        response = self.client.responses.create(
            model=self.model,
            input=messages,
            tools=[
                {
                    "type": "image_generation"
                }
            ],
        )

        result = {}

        result["error"] = ""
        
        if response.output_text:
            result["message"] = response.output_text

        images = [
            item.result
            for item in response.output
            if item.type == "image_generation_call"
        ]

        if images:
            result["image"] = images[0]
            if len(images) > 1:
                result["error"] = f"Number of images returned is {len(images)}. Expected at most 1."

        return result

    def reset(self):
        # Conversation history is maintained by the caller.
        pass

    #### LLM specific part

    def _convert_to_LLM_specific_messages(self, request_obj, payload=None):
        """Convert structured request object into OpenAI-style messages."""
        messages = []

        for block in request_obj.get("system_blocks", []):
            if block:
                messages.append({
                    "role": "system",
                    "content": block,
                })

        for block in request_obj.get("context_blocks", []):
            if block:
                messages.append({
                    "role": "system",
                    "content": block,
                })

        for block in request_obj.get("history_blocks", []):
            if block:
                messages.append({
                    "role": "system",
                    "content": block,
                })

        action_state = request_obj.get("action_state", "")
        if action_state:
            messages.append({
                "role": "system",
                "content": action_state,
            })

        for msg in request_obj.get("recent_messages", []):
            speaker = msg.get("role", "")
            text = msg.get("content", "")
            if not text:
                continue

            if speaker == "user":
                role = "user"
            elif speaker == "assistant":
                role = "assistant"
            else:
                role = "user"

            messages.append({
                "role": role,
                "content": text,
            })
        
        #############Adding system_call_responses
        if payload is not None:
            system_call_instruction = request_obj.get("system_call_response", "")

            if system_call_instruction:
                messages.append({
                    "role": "system",
                    "content": system_call_instruction,
                })

            for response in payload:
                result = response.get("system_call_result", response)

                payload_type = result.get("payload_type")

                if payload_type == "img":
                    image = result.get("payload")

                    # Do not put the image into the JSON representation.
                    result_without_payload = {
                        key: value
                        for key, value in result.items()
                        if key != "payload"
                    }

                    messages.append({
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": json.dumps({
                                    "system_call_result": result_without_payload
                                })
                            },
                            {
                                "type": "input_image",
                                "image_url": f"data:image/jpeg;base64,{image}",
                                "detail": "low",
                            }
                        ]
                    })

                else:
                    ####IRnote: this potentially might fail, as payload may be non-serializable. Not a concern for now, but need to keep in mind
                    messages.append({
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": json.dumps({
                                    "system_call_result": result
                                })
                            }
                        ]
                    })

        return messages