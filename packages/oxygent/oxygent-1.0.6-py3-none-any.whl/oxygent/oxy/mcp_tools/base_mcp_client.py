"""Base MCP (Model Context Protocol) client implementation.

This module provides the BaseMCPClient class, which implements the BaseTool interface
for communicating with MCP servers. It handles server initialization, tool discovery,
and tool execution through the Model Context Protocol standard.
"""

import asyncio
import logging
from contextlib import AsyncExitStack
from typing import Any, Dict

import anyio
from mcp import ClientSession
from pydantic import Field

from ...config import Config
from ...schemas import OxyRequest, OxyResponse, OxyState
from ..base_tool import BaseTool
from .mcp_tool import MCPTool

logger = logging.getLogger(__name__)


class BaseMCPClient(BaseTool):
    """Base client for Model Context Protocol (MCP) servers.

    This class provides a foundation for connecting to and interacting with MCP servers.
    It handles server lifecycle management, tool discovery, dynamic tool registration,
    and tool execution through the MCP protocol.

    Attributes:
        included_tool_name_list: List of tool names discovered from the MCP server.
    """

    included_tool_name_list: list = Field(default_factory=list)
    headers: Dict[str, str] = Field(
        default_factory=dict, description="Extra HTTP headers"
    )
    is_dynamic_headers: bool = Field(False, description="is dynamic headers")
    is_inherit_headers: bool = Field(False, description="is inherit headers")
    is_keep_alive: bool = Field(default_factory=Config.get_tool_mcp_is_keep_alive)

    def __init__(self, **kwargs):
        """Initialize the MCP client with necessary resources.

        Sets up the client session, cleanup mechanisms, and context managers for proper
        resource management throughout the client lifecycle.
        """
        super().__init__(**kwargs)
        self._session: ClientSession = None
        self._cleanup_lock: asyncio.Lock = asyncio.Lock()
        self._exit_stack: AsyncExitStack = AsyncExitStack()
        self._stdio_context: Any = Field(None)

    async def list_tools(self) -> None:
        """Discover and register tools from the MCP server.

        Connects to the MCP server, retrieves the list of available tools
        """
        if not self._session:
            raise RuntimeError(f"Server {self.name} not initialized")

        tools_response = await self._session.list_tools()
        self.add_tools(tools_response)

    def add_tools(self, tools_response) -> None:
        """
        dynamically creates MCPTool instances for each discovered tool. These tools are
        then registered with the MAS for use by agents.
        """
        params = self.model_dump(
            exclude={
                "sse_url",
                "server_url",
                "headers",
                "middlewares",
                "included_tool_name_list",
                "name",
                "desc",
                "mcp_client",
                "server_name",
                "input_schema",
            }
        )
        for item in tools_response:
            if isinstance(item, tuple) and item[0] == "tools":
                for tool in item[1]:
                    self.included_tool_name_list.append(tool.name)

                    mcp_tool = MCPTool(
                        name=tool.name,
                        desc=tool.description,
                        mcp_client=self,
                        server_name=self.name,
                        input_schema=tool.inputSchema,
                        **params,
                    )
                    mcp_tool.set_mas(self.mas)
                    self.mas.add_oxy(mcp_tool)

    async def _execute(self, oxy_request: OxyRequest) -> OxyResponse:
        """Execute a tool call through the MCP server.

        Forwards the tool execution request to the appropriate MCP server tool and
        processes the response. Handles both single and multiple content responses from
        the MCP protocol.
        """
        tool_name = oxy_request.callee

        if not self.is_dynamic_headers and self.is_keep_alive:
            if not self._session:
                raise RuntimeError(f"Server {self.name} not initialized")

            try:
                mcp_response = await self._session.call_tool(
                    tool_name, oxy_request.arguments
                )
            except anyio.ClosedResourceError:
                await self.init(is_fetch_tools=False)  # TODO: refetch tools
                mcp_response = await self._session.call_tool(
                    tool_name, oxy_request.arguments
                )
        else:
            if self.is_dynamic_headers:
                _headers = (
                    oxy_request.shared_data.get("_headers", {})
                    if self.is_inherit_headers
                    else {}
                )
                if "host" in _headers:
                    del _headers["host"]
                merged_headers = (
                    self.headers | _headers | oxy_request.shared_data.get("headers", {})
                )
            else:
                merged_headers = self.headers
            mcp_response = await self.call_tool(
                tool_name,
                oxy_request.arguments,
                headers=merged_headers,
            )
        # TODO: Handle result objects and progress tracking
        results = [content.text.strip() for content in mcp_response.content]
        return OxyResponse(
            state=OxyState.COMPLETED,
            output=results[0] if len(results) == 1 else results,
        )

    async def cleanup(self) -> None:
        """Clean up MCP server resources and connections.

        Safely closes the MCP server session and all associated resources. Uses a
        cleanup lock to prevent concurrent cleanup operations and handles cancellation
        and other exceptions gracefully.
        """
        async with self._cleanup_lock:
            try:
                await self._exit_stack.aclose()
            except asyncio.CancelledError:
                # TODO cleanup(): Operation was cancelled
                logger.error("main(): cancel_me is cancelled now")
            except Exception:
                pass
                # Suppress cleanup exceptions to prevent cascading failures
            finally:
                self._session = None
                self._stdio_context = None
