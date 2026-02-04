import os
import json
import shlex
from pathlib import Path
from contextlib import AsyncExitStack
from typing import Any, Dict, Optional, List, Tuple

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPToolClient:
    """
    MCP STDIO client wrapper that spawns an MCP server subprocess and calls tools.

    Key fixes vs old version:
    - Spawns server as a module (python -m itsm_agents.mcp_server) to preserve package context.
    - Passes env (incl. GEMINI_API_KEY) to subprocess.
    - Ensures PYTHONPATH includes app/src for subprocess imports.
    """

    def __init__(
        self,
        command: Optional[str] = None,
        args: Optional[List[str]] = None,
        env: Optional[Dict[str, str]] = None,
    ):
        self.command = command or os.getenv("MCP_SERVER_COMMAND", "python").strip()

        if args is None:
            args_str = os.getenv("MCP_SERVER_ARGS", "-m itsm_agents.mcp_server").strip()
            self.args = shlex.split(args_str)
        else:
            self.args = args

        # Prepare environment for subprocess
        self.env = env or os.environ.copy()

        # Auto-inject app/src into PYTHONPATH for the subprocess
        # this file: app/src/itsm_agents/mcp_client.py -> parents[1] == app/src
        app_src = Path(__file__).resolve().parents[1]
        self.env["PYTHONPATH"] = str(app_src) + os.pathsep + self.env.get("PYTHONPATH", "")

        self.exit_stack = AsyncExitStack()
        self.session: Optional[ClientSession] = None

    async def __aenter__(self):
        params = StdioServerParameters(
            command=self.command,
            args=self.args,
            env=self.env,
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(params))
        read, write = stdio_transport

        self.session = await self.exit_stack.enter_async_context(ClientSession(read, write))
        await self.session.initialize()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.exit_stack.aclose()

    async def call_tool(self, tool_name: str, arguments: dict) -> dict:
        """
        Call an MCP tool and return a decoded dict.

        FastMCP with json_response=True typically returns JSON in a TextContent block.
        We also support alternative shapes robustly.
        """
        if self.session is None:
            raise RuntimeError("MCPToolClient is not initialized. Use 'async with MCPToolClient() as cli:'")

        # NOTE: some SDK versions use `arguments=...`, others may accept `tool_args` etc.
        result = await self.session.call_tool(tool_name, arguments=arguments)

        # 1) If result has `.content` list (typical), try to parse first item
        if hasattr(result, "content") and result.content:
            item = result.content[0]

            # TextContent has `.text`
            if hasattr(item, "text") and isinstance(item.text, str):
                text = item.text.strip()
                # If it's JSON, parse it
                try:
                    return json.loads(text)
                except Exception:
                    return {"raw_text": text}

            # Some variants may return dict-like items
            if isinstance(item, dict):
                # If dict contains "text", attempt JSON parse
                if "text" in item and isinstance(item["text"], str):
                    try:
                        return json.loads(item["text"])
                    except Exception:
                        return {"raw_text": item["text"]}
                return item

        # 2) Fallback: model_dump if available
        if hasattr(result, "model_dump"):
            return result.model_dump()

        # 3) Last resort
        return {"raw": str(result)}