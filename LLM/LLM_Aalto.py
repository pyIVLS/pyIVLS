# File: LLM_Aalto.py
#
# Generic Aalto OpenAI API backend.
# This module is independent of pyIVLS.

import os
import httpx
from openai import OpenAI


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

    def send(self, messages):
        response = self.client.responses.create(
            model=self.model,
            input=messages,
        )

        return response.output_text

    def reset(self):
        # Conversation history is maintained by the caller.
        pass