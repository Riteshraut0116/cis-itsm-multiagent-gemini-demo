import logging
import json
from mcp.server.fastmcp import FastMCP

from .schemas import Ticket
from .agents_direct import classify_ticket, troubleshoot_ticket, compose_response

logging.basicConfig(level=logging.INFO)  # writes to stderr via logging

mcp = FastMCP("CIS-ITSM-MultiAgent", json_response=True)

@mcp.tool()
def classify_ticket_tool(ticket: dict) -> dict:
    t = Ticket(**ticket)
    cls = classify_ticket(t)
    return cls.model_dump()

@mcp.tool()
def troubleshoot_ticket_tool(ticket: dict, classification: dict) -> dict:
    t = Ticket(**ticket)
    # reconstruct Classification using schema validation (reuse by dict)
    from .schemas import Classification
    cls = Classification(**classification)
    ts = troubleshoot_ticket(t, cls)
    return ts.model_dump()

@mcp.tool()
def compose_response_tool(ticket: dict, classification: dict, troubleshooting: dict) -> dict:
    from .schemas import Classification, Troubleshooting
    t = Ticket(**ticket)
    cls = Classification(**classification)
    ts = Troubleshooting(**troubleshooting)
    comm = compose_response(t, cls, ts)
    return comm.model_dump()

def main():
    # runs stdio server
    mcp.run()

if __name__ == "__main__":
    main()