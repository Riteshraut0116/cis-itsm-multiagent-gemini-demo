# 🤖 CIS ITSM Multi‑Agent Demo (Gemini 2.5 Flash)

A polished **ITSM (ServiceNow-style) multi-agent demo** that classifies incidents, generates troubleshooting steps, and produces **user-ready communications** in minutes.  
Powered by **Google Gemini 2.5 Flash**, with two execution modes:

- ⚡ **Direct Runner**: fastest, runs agents in-process
- 🧩 **MCP Runner (STDIO)**: tool-based execution via **MCP server**, closer to real agent/tool orchestration

---

## ✨ Highlights

- **Streamlit UI Demo**: Clean UI for demos and rapid iteration
- **Multi‑Agent Pipeline**:  
  **Classifier → Troubleshooter → Communication**
- **Gemini-powered reasoning**: Uses Gemini for intelligent categorization & next steps
- **MCP (STDIO) Tooling**: Exposes agent functions as MCP tools (JSON-RPC over stdio)
- **Sample Tickets Included**: One-click load of realistic incident scenarios
- **Downloadable Output**: Export full pipeline output as JSON (great for demos)
- **MCP Status Button (STDIO)**: Verifies MCP server can spawn + initialize + list tools

---

## 📂 File Structure

cis-itsm-multiagent-gemini-demo/
├── app/                                   # Application source root
│   └── src/                               # Python package root (PYTHONPATH target)
│       └── itsm_agents/                   # Core multi-agent package
│           ├── __init__.py                # Package initializer
│           ├── agents_direct.py           # Direct (in-process) agent implementations
│           ├── agents.py                  # Shared agent logic/helpers (if any)
│           ├── cli.py                     # CLI entry helpers (if used)
│           ├── config.py                  # Configuration loading (env/model params)
│           ├── gemini_client.py           # Gemini API client wrapper
│           ├── json_utils.py              # JSON utilities/helpers
│           ├── mcp_client.py              # MCP STDIO client wrapper (tool calls)
│           ├── mcp_server.py              # MCP server exposing tools (stdio)
│           ├── orchestrator_direct.py     # Orchestrates pipeline using direct runner
│           ├── orchestrator_mcp.py        # Orchestrates pipeline using MCP runner
│           ├── schemas.py                 # Pydantic schemas (Ticket, outputs, etc.)
│           └── ui_streamlit.py            # Streamlit UI (direct + MCP modes)
│
├── tests/                                 # Unit tests
│   ├── __init__.py                        # Test package initializer
│   └── test_json_utils.py                 # Tests for JSON utility functions
│
├── samples/                               # Sample incident/ticket JSONs for demo
│   ├── ticket_disk_space.json             # Low disk space scenario sample
│   ├── ticket_outlook.json                # Outlook not opening scenario sample
│   └── ticket_vpn_809.json                # VPN error 809 scenario sample
│
├── .env                                   # Local secrets/config (DO NOT COMMIT)
├── .gitignore                             # Git ignore rules
├── README.md                              # Project documentation
├── requirements.txt                       # Python dependencies
├── run_cli.py                             # Convenience script to run CLI mode
└── run_ui.py                              # Convenience script to run Streamlit UI

---

## 🎯 What You Get (Output)

Running a ticket produces:

✅ **Classification** (category, summary, reasoning)  
🛠 **Troubleshooting** (steps, checks, likely root cause)  
💬 **Communication**  
- A **message you can send to the user**
- **Ticket work notes** for ServiceNow updates
- A **close recommendation**

![Final Output](cis-itsm-multiagent-gemini-demo\samples\screenshot.png)

---

## 🧠 Architecture (Simple View)

### Direct Runner
Streamlit UI → `orchestrator_direct.py` → runs:
- `classify_ticket()`
- `troubleshoot_ticket()`
- `compose_response()`

### MCP Runner (STDIO)
Streamlit UI → `orchestrator_mcp.py` → MCP Client spawns subprocess:
- `python -m itsm_agents.mcp_server`
→ calls tools:
- `classify_ticket_tool`
- `troubleshoot_ticket_tool`
- `compose_response_tool`

> ✅ MCP Runner uses **STDIO**, so it does **not** run on host/port. The client spawns it as a subprocess.

---

## 🛠️ Tech Stack

- **UI**: Streamlit
- **LLM**: Google Gemini API (Gemini 2.5 Flash)
- **Config**: python-dotenv (`.env`)
- **MCP**: MCP Python SDK (STDIO transport)
- **Schemas**: Pydantic models
- **Tests**: Basic tests for utilities (expandable)

---

## 📦 Prerequisites

- Python 3.10+ recommended
- A Google Gemini API key
- pip / venv

---

## 🚀 Getting Started

### 1) Clone the repo

git clone <repo-url>
cd cis-itsm-multiagent-gemini-demo

### 2) Create & activate virtual environment

python -m venv venv
venv\Scripts\activate

### 3) Install dependencies

pip install -r requirements.txt

### 4) 🖥️ Run the Streamlit UI

Option A: Run via Streamlit directly
streamlit run app/src/itsm_agents/ui_streamlit.py

Option B: Run using helper script
python run_ui.py

---

## 🏃 Running Modes: Direct vs MCP

nside the UI sidebar you can select:

Runner Mode: direct
Runner Mode: mcp


✅ Method 1: Run with Direct Runner (Fastest)

Open UI
Select Runner Mode → direct
Load a sample ticket (VPN/Outlook/Disk)
Click 🚀 Run Multi‑Agent

How it behaves

Executes all agent functions inside the same Streamlit process
No MCP subprocess
Very fast and best for demos where speed matters


✅ Method 2: Run with MCP Runner (STDIO)

Open UI
Select Runner Mode → mcp
(Recommended) Click 🩺 Check MCP Status
Click 🚀 Run Multi‑Agent

How it behaves

Spawns MCP server as a subprocess using your .env command/args
Calls each tool via MCP:

classify → troubleshoot → compose response


Slightly more overhead, but closer to real “agent tool calling”

---

## 🧾 Direct vs MCP (Quick Comparison)

+---------------------------+-----------------------------+----------------------------------+
| Feature                   | Direct Runner               | MCP Runner (STDIO)               |
+---------------------------+-----------------------------+----------------------------------+
| Where code runs           | Same Streamlit process      | Separate MCP server subprocess   |
| Speed                     | Fastest                     | Slight overhead                  |
| Tool-calling realism      | Lower (function calls)      | Higher (MCP tool calls)          |
| Isolation                 | None                        | Better isolation (separate proc) |
| Env / .env dependency     | UI process only             | UI + MCP subprocess env          |
| Setup complexity          | Low                         | Medium (MCP client/server flow)  |
| Best for                  | Quick demos, dev, debugging | Agent/tool demos, extensibility  |
| Failure surface area      | Smaller                     | Larger (spawn, IPC, tools)       |
| Debugging                 | Simple stack traces         | Needs stderr/log visibility      |
| Requires MCP installed    | No                          | Yes (MCP SDK in venv)            |
+---------------------------+-----------------------------+----------------------------------+

---

## 👤 Author

**Ritesh Raut**  
*Programmer Analyst, Cognizant*

⚡ From ticket to resolution-ready notes in minutes — powered by Gemini + MCP tools 🤖🧰

---

### 🌐 Connect with me:
<p align="left">
<a href="https://github.com/Riteshraut0116" target="blank"><img align="center" src="https://raw.githubusercontent.com/rahuldkjain/github-profile-readme-generator/master/src/images/icons/Social/github.svg" alt="Riteshraut0116" height="30" width="40" /></a>
<a href="https://linkedin.com/in/ritesh-raut-9aa4b71ba" target="blank"><img align="center" src="https://raw.githubusercontent.com/rahuldkjain/github-profile-readme-generator/master/src/images/icons/Social/linked-in-alt.svg" alt="ritesh-raut-9aa4b71ba" height="30" width="40" /></a>
<a href="https://www.instagram.com/riteshraut1601/" target="blank"><img align="center" src="https://raw.githubusercontent.com/rahuldkjain/github-profile-readme-generator/master/src/images/icons/Social/instagram.svg" alt="riteshraut1601" height="30" width="40" /></a>
<a href="https://www.facebook.com/ritesh.raut.649321/" target="blank"><img align="center" src="https://raw.githubusercontent.com/rahuldkjain/github-profile-readme-generator/master/src/images/icons/Social/facebook.svg" alt="ritesh.raut.649321" height="30" width="40" /></a>
</p>

---





