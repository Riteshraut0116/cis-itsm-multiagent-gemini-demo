<<<<<<< HEAD
# CIS ITSM Multi-Agent Demo (Gemini 2.5 Flash + MCP + UI/CLI)

This demo shows a CIS-friendly multi-agent workflow:
1) Classify ticket
2) Generate troubleshooting steps
3) Generate user message + ticket work notes

Two runners:
- direct: Python orchestrator calls agents directly
- mcp: agentify via MCP tools (server exposes tools, client calls tools)

## Setup
1) pip install -r requirements.txt
2) copy .env.example .env
3) add GEMINI_API_KEY in .env

## Run CLI (direct)
python run_cli.py --ticket samples/ticket_vpn_809.json --runner direct

## Run MCP server
python -m itsm_agents.mcp_server

## Run CLI (mcp)
python run_cli.py --ticket samples/ticket_vpn_809.json --runner mcp

## Run UI
python run_ui.py
=======
# cis-itsm-multiagent-gemini-demo
>>>>>>> 31dc6f9444bee62c772361451cc9be15b8130af9
