"""OpenAI LLM implementation using the official OpenAI Python client.

This module provides the OpenAILLM class, which implements the BaseLLM interface
specifically for OpenAI's language models using the official AsyncOpenAI client. It
supports all OpenAI models and compatible APIs.
"""

import logging

from openai import AsyncOpenAI

from ...config import Config
from ...schemas import OxyRequest, OxyResponse, OxyState
from .remote_llm import RemoteLLM

logger = logging.getLogger(__name__)


class OpenAILLM(RemoteLLM):
    """OpenAI Large Language Model implementation.

    This class provides a concrete implementation of RemoteLLM specifically designed
    for OpenAI's language models. It uses the official AsyncOpenAI client for
    optimal performance and compatibility with OpenAI's API standards.
    """

    async def _execute(self, oxy_request: OxyRequest) -> OxyResponse:
        """Execute a request using the OpenAI API.

        Creates a chat completion request using the official AsyncOpenAI client.
        The method handles payload construction, configuration merging, and
        response processing for OpenAI's chat completion API.

        Args:
            oxy_request: The request object containing messages and parameters.

        Returns:
            OxyResponse: The response containing the model's output with COMPLETED state.
        """
        # Construct payload for OpenAI API request
        llm_config = {
            k: v
            for k, v in Config.get_llm_config().items()
            if k
            not in {
                "cls",
                "base_url",
                "api_key",
                "name",
                "model_name",
            }
        }
        payload = {
            "messages": await self._get_messages(oxy_request),
            "model": self.model_name,
            "stream": False,
        }
        payload.update(llm_config)
        for k, v in self.llm_params.items():
            payload[k] = v
        for k, v in oxy_request.arguments.items():
            if k == "messages":
                continue
            payload[k] = v

        client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )
        completion = await client.chat.completions.create(**payload)
        if payload["stream"]:
            answer = ""
            think_start = True
            think_end = False
            async for chunk in completion:
                if hasattr(chunk.choices[0].delta, "reasoning_content"):
                    if think_start:
                        await oxy_request.send_message(
                            {"type": "stream", "content": {"delta": "<think>"}}
                        )
                        answer += "<think>"
                        think_start = False
                        think_end = True
                    char = chunk.choices[0].delta.reasoning_content
                elif hasattr(chunk.choices[0].delta, "content"):
                    if think_end:
                        await oxy_request.send_message(
                            {"type": "stream", "content": {"delta": "</think>"}}
                        )
                        answer += "</think>"
                        think_end = False
                    char = chunk.choices[0].delta.content
                if char:
                    answer += char
                    await oxy_request.send_message(
                        {"type": "stream", "content": {"delta": char}}
                    )
            return OxyResponse(state=OxyState.COMPLETED, output=answer)
        else:
            return OxyResponse(
                state=OxyState.COMPLETED, output=completion.choices[0].message.content
            )
