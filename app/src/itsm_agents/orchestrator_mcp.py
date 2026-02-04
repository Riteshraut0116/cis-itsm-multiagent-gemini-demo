import os
import asyncio
import shlex
from pathlib import Path

from .schemas import Ticket
from .mcp_client import MCPToolClient


def run(ticket: Ticket) -> dict:
    """
    Runs the pipeline using MCP over STDIO.

    Key points:
    - Spawns server using module invocation (-m itsm_agents.mcp_server), not by file path,
      so relative imports inside the package work correctly.
    - Passes full environment to the MCP subprocess (GEMINI_API_KEY, etc.).
    - Ensures app/src is present on PYTHONPATH for subprocess imports.

    MCP STDIO transport expects the client to launch the server as a subprocess and
    communicate over stdin/stdout. [1](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports)
    """

    async def _run():
        # Read command/args from .env (or defaults)
        cmd = os.getenv("MCP_SERVER_COMMAND", "python").strip()
        args_str = os.getenv("MCP_SERVER_ARGS", "-m itsm_agents.mcp_server").strip()
        args = shlex.split(args_str)

        # Inherit current environment (ensures GEMINI_API_KEY etc. are available)
        env = os.environ.copy()

        # Ensure app/src is on PYTHONPATH for the MCP server subprocess.
        # orchestrator_mcp.py lives in: app/src/itsm_agents/orchestrator_mcp.py
        # parents[1] => app/src
        app_src = Path(__file__).resolve().parents[1]
        env["PYTHONPATH"] = str(app_src) + os.pathsep + env.get("PYTHONPATH", "")

        async with MCPToolClient(command=cmd, args=args, env=env) as cli:
            # 1) Classification tool
            cls = await cli.call_tool(
                "classify_ticket_tool",
                {"ticket": ticket.model_dump()}
            )

            # 2) Troubleshooting tool
            ts = await cli.call_tool(
                "troubleshoot_ticket_tool",
                {
                    "ticket": ticket.model_dump(),
                    "classification": cls
                }
            )

            # 3) Communication tool
            comm = await cli.call_tool(
                "compose_response_tool",
                {
                    "ticket": ticket.model_dump(),
                    "classification": cls,
                    "troubleshooting": ts
                }
            )

            return {
                "ticket": ticket.model_dump(),
                "classification": cls,
                "troubleshooting": ts,
                "communication": comm,
                "runner": "mcp",
            }

    # Run async pipeline in sync context
    return asyncio.run(_run())