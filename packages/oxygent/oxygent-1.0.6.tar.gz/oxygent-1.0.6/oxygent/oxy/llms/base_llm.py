"""Base LLM module for Large Language Model implementations.

This module provides the abstract base class for all LLM implementations in the OxyGent
system. It handles multimodal input processing, think message extraction, and provides a
consistent interface for different LLM providers.
"""

import copy
import json
import logging
from typing import Optional

from pydantic import Field

from ...config import Config
from ...schemas import OxyRequest, OxyResponse
from ...utils.common_utils import (
    extract_first_json,
    file_to_base64,
    image_to_base64,
    video_to_base64,
)
from ..base_oxy import Oxy

logger = logging.getLogger(__name__)


class BaseLLM(Oxy):
    """Base class for Large Language Model implementations.

    This class provides common functionality for all LLM implementations including:
    - Multimodal input processing (images, videos)
    - Think message extraction and forwarding
    - Base64 conversion for media URLs
    - Error handling with user-friendly messages

    Attributes:
        category: The category type, always "llm" for LLM implementations.
        timeout: Maximum execution time in seconds.
        llm_params: Additional parameters specific to the LLM implementation.
        is_send_think: Whether to send think messages to the frontend.
        friendly_error_text: User-friendly error message for exceptions.
        is_convert_url_to_base64: Whether to convert media URLs to base64.
        max_image_pixels: Maximum pixel count for image processing.
        max_video_size: Maximum size in bytes for video processing.
    """

    category: str = Field("llm", description="")
    timeout: float = Field(300, description="Timeout in seconds.")

    llm_params: dict = Field(default_factory=dict)
    is_send_think: bool = Field(
        default_factory=Config.get_message_is_send_think,
        description="Whether to send think messages to the frontend.",
    )
    friendly_error_text: Optional[str] = Field(
        default="Sorry, I seem to have encountered a problem. Please try again.",
        description="User-friendly error message displayed when exceptions occur.",
    )

    is_multimodal_supported: bool = Field(
        False, description="whether to support multimodal input"
    )

    is_convert_url_to_base64: bool = Field(
        default=False,
        description="Whether to convert image or video URLs to base64 format.",
    )
    max_image_pixels: int = Field(
        default=10000000, description="Maximum pixel count allowed per image."
    )
    max_video_size: int = Field(
        default=12 * 1024 * 1024,
        description="Maximum video file size in bytes (default: 12MB).",
    )
    max_file_size_bytes: int = Field(
        default=2 * 1024 * 1024,
        description="Maximum non-media file size (bytes) for base64 embedding.",
    )

    async def _get_messages(self, oxy_request: OxyRequest):
        """Preprocess messages for multimoding input."""
        # ---------- if "messages" ----------
        if "messages" not in oxy_request.arguments:
            query_val = oxy_request.arguments.get("query", "")
            # A2A-style parts -> content, otherwise -> str
            if isinstance(query_val, list):
                content_field = query_val
            elif isinstance(query_val, dict):
                content_field = [query_val]
            else:
                content_field = str(query_val)
            oxy_request.arguments["messages"] = [
                {"role": "user", "content": content_field}
            ]

        # hold url
        if not self.is_convert_url_to_base64:
            return oxy_request.arguments["messages"]

        # convert url into base_64 data
        messages_processed = copy.deepcopy(oxy_request.arguments["messages"])

        for message in messages_processed:
            if not isinstance(message.get("content"), list):
                continue

            for item in message["content"]:
                item_type = item.get("type")
                if item_type == "text":
                    continue

                if item_type == "image_url":
                    item[item_type]["url"] = await image_to_base64(
                        item[item_type]["url"], self.max_image_pixels
                    )
                elif item_type == "video_url":
                    item[item_type]["url"] = await video_to_base64(
                        item[item_type]["url"], self.max_video_size
                    )
                elif item_type in {
                    "table_file",
                    "doc_file",
                    "pdf_file",
                    "code_file",
                    "file",
                }:
                    try:
                        item[item_type]["url"] = await file_to_base64(
                            item[item_type]["url"], self.max_file_size_bytes
                        )
                    except Exception as e:
                        logger.warning(
                            f"Failed to base64-embed {item_type}: {e}",
                            extra={
                                "trace_id": oxy_request.current_trace_id,
                                "node_id": oxy_request.node_id,
                            },
                        )
                else:
                    logger.warning(
                        f"Unexpected content type: {item_type}",
                        extra={
                            "trace_id": oxy_request.current_trace_id,
                            "node_id": oxy_request.node_id,
                        },
                    )

        return messages_processed

    async def _execute(self, oxy_request: OxyRequest) -> OxyResponse:
        """Execute the LLM request."""
        raise NotImplementedError("This method is not yet implemented")

    async def _post_send_message(self, oxy_response: OxyResponse):
        """Send think messages to the frontend after response generation.

        Extracts and forwards thinking process messages to the frontend if
        is_send_think is enabled. Supports both XML-style <think> tags and
        JSON-based think messages.

        Args:
            oxy_response: The response object containing the LLM output.
        """
        await super()._post_send_message(oxy_response)
        # Send thinking process to frontend
        oxy_request = oxy_response.oxy_request
        if self.is_send_think:
            try:
                msg = ""
                if "</think>" in oxy_response.output:
                    msg = (
                        oxy_response.output.split("</think>")[0]
                        .replace("<think>", "")
                        .strip()
                    )
                else:
                    tool_call_dict = json.loads(extract_first_json(oxy_response.output))
                    if "think" in tool_call_dict:
                        msg = tool_call_dict["think"].strip()
                await oxy_request.send_message({"type": "think", "content": msg})
            except json.JSONDecodeError:
                pass
            except Exception as e:
                logger.error(
                    e,
                    extra={
                        "trace_id": oxy_request.current_trace_id,
                        "node_id": oxy_request.node_id,
                    },
                )
