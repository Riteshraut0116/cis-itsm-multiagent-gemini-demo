import json
import argparse
from .schemas import Ticket
from .orchestrator_direct import run as run_direct
from .orchestrator_mcp import run as run_mcp

def main():
    parser = argparse.ArgumentParser(description="CIS ITSM Multi-Agent Demo (Gemini 2.5 Flash + MCP)")
    parser.add_argument("--ticket", required=True, help="Path to ticket JSON")
    parser.add_argument("--runner", choices=["direct", "mcp"], default="direct", help="Choose execution mode")
    args = parser.parse_args()

    with open(args.ticket, "r", encoding="utf-8") as f:
        ticket_data = json.load(f)

    ticket = Ticket(**ticket_data)

    output = run_direct(ticket) if args.runner == "direct" else run_mcp(ticket)
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()