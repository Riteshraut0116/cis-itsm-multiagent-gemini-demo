import json
import time
import os
import sys
import asyncio
import shlex
from contextlib import AsyncExitStack
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

# -------------------------
# Automatic PYTHONPATH fix
# -------------------------
# Ensures imports like `import itsm_agents` work regardless of where Streamlit is executed from.
THIS_FILE = Path(__file__).resolve()

# ui_streamlit.py is inside: app/src/itsm_agents/
# repo root is 3 levels up from app/src/itsm_agents -> app/src -> app -> repo
REPO_ROOT = THIS_FILE.parents[3]
APP_SRC = REPO_ROOT / "app" / "src"

# Add app/src to sys.path if missing
if str(APP_SRC) not in sys.path:
    sys.path.insert(0, str(APP_SRC))

# Also set PYTHONPATH for any subprocesses and libraries that read it
os.environ["PYTHONPATH"] = str(APP_SRC) + os.pathsep + os.environ.get("PYTHONPATH", "")

import streamlit as st

from itsm_agents.schemas import Ticket
from itsm_agents.orchestrator_direct import run as run_direct
from itsm_agents.orchestrator_mcp import run as run_mcp


# -------------------------
# Paths (robust)
# -------------------------
# ui_streamlit.py is inside: app/src/itsm_agents/
# repo root is 3 levels up from app/src/itsm_agents -> app/src -> app -> repo
REPO_ROOT = Path(__file__).resolve().parents[3]
SAMPLES_DIR = REPO_ROOT / "samples"


def load_sample_ticket(filename: str):
    """Load a sample JSON from repo-root /samples folder."""
    p = SAMPLES_DIR / filename
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return None


# -------------------------
# MCP STDIO Status Helpers (Option B)
# -------------------------
def _run_async(coro):
    """
    Run async coroutine safely from Streamlit.
    Streamlit generally runs sync code; asyncio.run() is fine.
    Fallback is included for environments where an event loop is already running.
    """
    try:
        return asyncio.run(coro)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()


def check_mcp_status_stdio():
    """
    STDIO MCP status check:
    - Spawns MCP server as a subprocess using stdio transport
    - Initializes MCP session
    - Lists tools
    This matches MCP stdio transport expectations (client launches server subprocess). [1](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports)
    The Python SDK flow is stdio_client -> ClientSession -> initialize() -> list_tools(). [2](https://deepwiki.com/modelcontextprotocol/docs/5.1-python-sdk)

    Configurable via .env:
      MCP_SERVER_COMMAND=python
      MCP_SERVER_ARGS=-m itsm_agents.mcp_server
    """
    cmd = os.getenv("MCP_SERVER_COMMAND", "python").strip()
    args_str = os.getenv("MCP_SERVER_ARGS", "-m itsm_agents.mcp_server").strip()
    args = shlex.split(args_str)

    async def _probe():
        try:
            # Lazy imports so UI still runs in direct mode even if MCP deps missing
            from mcp import ClientSession, StdioServerParameters
            from mcp.client.stdio import stdio_client
        except Exception as e:
            return {
                "ok": False,
                "mode": "stdio",
                "message": f"Missing MCP client dependencies in UI runtime: {e}",
                "details": {"hint": "Install MCP SDK in this environment: pip install mcp"},
            }

        exit_stack = AsyncExitStack()
        try:
            env = os.environ.copy()
            # Ensure spawned MCP server can import from app/src
            env["PYTHONPATH"] = str(APP_SRC) + os.pathsep + env.get("PYTHONPATH", "")

            server_params = StdioServerParameters(command=cmd, args=args, env=env)


            # Connect via stdio (client spawns server subprocess) [1](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports)
            stdio_transport = await exit_stack.enter_async_context(stdio_client(server_params))
            stdio, write = stdio_transport

            session = await exit_stack.enter_async_context(ClientSession(stdio, write))

            # MCP handshake [2](https://deepwiki.com/modelcontextprotocol/docs/5.1-python-sdk)
            await session.initialize()

            # Probe tools list [2](https://deepwiki.com/modelcontextprotocol/docs/5.1-python-sdk)
            tools_resp = await session.list_tools()
            tool_names = [t.name for t in tools_resp.tools]

            return {
                "ok": True,
                "mode": "stdio",
                "message": (
                    "MCP STDIO server initialized successfully.\n"
                    f"Tools: {', '.join(tool_names) if tool_names else '(none)'}"
                ),
                "details": {
                    "command": cmd,
                    "args": args,
                    "tool_count": len(tool_names),
                    "tools": tool_names,
                },
            }
        except Exception as e:
            return {
                "ok": False,
                "mode": "stdio",
                "message": f"Failed to initialize MCP STDIO server: {e}",
                "details": {"command": cmd, "args": args},
            }
        finally:
            await exit_stack.aclose()

    return _run_async(_probe())


# -------------------------
# Page Setup
# -------------------------
st.set_page_config(
    page_title="CIS ITSM Multi-Agent (Gemini 2.5 Flash)",
    page_icon="🤖",
    layout="wide"
)

# -------------------------
# Styling (attractive UI)
# -------------------------
st.markdown("""
<style>
.block-container {padding-top: 1rem; padding-bottom: 2rem;}
h1, h2, h3 {font-family: 'Segoe UI', sans-serif;}
.big-card {
  background: linear-gradient(135deg, #0f172a, #1e293b);
  border: 1px solid rgba(255,255,255,0.12);
  padding: 18px;
  border-radius: 16px;
  color: #f8fafc;
  box-shadow: 0 10px 30px rgba(0,0,0,0.25);
}
.badge {
  display:inline-block; padding: 6px 10px; border-radius: 999px;
  background: rgba(99,102,241,0.18);
  border: 1px solid rgba(99,102,241,0.35);
  color:#c7d2fe; font-size: 12px; margin-right:8px;
}
.badge-ok {
  background: rgba(16,185,129,0.18);
  border: 1px solid rgba(16,185,129,0.35);
  color:#a7f3d0;
}
.badge-warn {
  background: rgba(245,158,11,0.18);
  border: 1px solid rgba(245,158,11,0.35);
  color:#fde68a;
}
.kpi {
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.10);
  padding: 12px; border-radius: 14px;
}
.small-note {color: rgba(255,255,255,0.7); font-size: 12px;}
hr {border: none; height: 1px; background: rgba(255,255,255,0.08); margin: 14px 0;}
</style>
""", unsafe_allow_html=True)

# Optional: show last MCP status badge in header (if checked)
header_mcp_badge = ""
if "mcp_status" in st.session_state:
    if st.session_state.mcp_status.get("ok"):
        header_mcp_badge = '<span class="badge badge-ok">MCP: Online</span>'
    else:
        header_mcp_badge = '<span class="badge badge-warn">MCP: Offline</span>'

st.markdown(f"""
<div class="big-card">
  <h1>🤖 CIS ITSM Multi-Agent Demo</h1>
  <span class="badge badge-ok">Gemini 2.5 Flash</span>
  <span class="badge">Multi-Agent</span>
  <span class="badge badge-warn">MCP Optional</span>
  {header_mcp_badge}
  <p style="margin-top:8px;">
    Classifier → Troubleshooter → Communication. Demo CIS value in minutes.
  </p>
</div>
""", unsafe_allow_html=True)


# -------------------------
# Sidebar Controls
# -------------------------
st.sidebar.header("⚙️ Demo Controls")

runner = st.sidebar.radio(
    "Runner Mode",
    ["direct", "mcp"],
    index=0,
    help="direct = fastest. mcp = agentified tools via MCP (stdio)."
)

# --- MCP Status Button UI (STDIO) ---
st.sidebar.markdown("### 🧩 MCP Server (STDIO)")
st.sidebar.caption(
    "This MCP server uses STDIO transport (no host/port). The status check spawns the server and runs initialize + list_tools."  # [1](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports)[2](https://deepwiki.com/modelcontextprotocol/docs/5.1-python-sdk)
)

colA, colB = st.sidebar.columns([1, 1])
with colA:
    status_btn = st.button("🩺 Check MCP Status", use_container_width=True)
with colB:
    clear_status_btn = st.button("🧹 Clear", use_container_width=True)

if clear_status_btn:
    st.session_state.pop("mcp_status", None)

if status_btn:
    with st.sidebar.spinner("Checking MCP (stdio)..."):
        st.session_state.mcp_status = check_mcp_status_stdio()

if "mcp_status" in st.session_state:
    s = st.session_state.mcp_status
    if s.get("ok"):
        st.sidebar.success(f"✅ {s.get('message')}")
        with st.sidebar.expander("Details"):
            st.sidebar.json(s.get("details", {}))
    else:
        st.sidebar.error(f"❌ {s.get('message')}")
        with st.sidebar.expander("Details"):
            st.sidebar.json(s.get("details", {}))

st.sidebar.markdown("---")

sample = st.sidebar.selectbox(
    "Load sample ticket",
    ["Custom", "VPN Error 809", "Outlook not opening", "Low disk space"]
)

st.sidebar.markdown("---")
st.sidebar.caption(
    "Tip: For STDIO MCP, you typically do NOT start the MCP server manually. The client/orchestrator spawns it as a subprocess."  # [1](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports)
)


# -------------------------
# Default Ticket + Load Sample
# -------------------------
default_ticket = {
    "ticket_id": "INC-DEMO-001",
    "short_description": "VPN not connecting",
    "description": "User cannot connect to VPN. Error 809.",
    "caller": "Demo User",
    "impact": "Single User",
    "urgency": "Medium"
}

mapping = {
    "VPN Error 809": "ticket_vpn_809.json",
    "Outlook not opening": "ticket_outlook.json",
    "Low disk space": "ticket_disk_space.json"
}

# use session state so switching sample updates JSON area smoothly
if "ticket_json" not in st.session_state:
    st.session_state.ticket_json = json.dumps(default_ticket, indent=2)

if sample != "Custom":
    filename = mapping.get(sample)
    loaded = load_sample_ticket(filename) if filename else None
    if loaded:
        st.session_state.ticket_json = json.dumps(loaded, indent=2)
    else:
        st.sidebar.warning(
            f"Sample file not found: samples/{filename}\n"
            f"Expected at: {SAMPLES_DIR}"
        )


# -------------------------
# Layout
# -------------------------
left, right = st.columns([1, 1])

with left:
    st.subheader("🎫 Ticket Input")

    st.markdown(
        f"<div class='small-note'>Samples folder detected: <b>{SAMPLES_DIR}</b></div>",
        unsafe_allow_html=True
    )

    ticket_json = st.text_area(
        "Ticket JSON",
        value=st.session_state.ticket_json,
        height=320
    )
    st.session_state.ticket_json = ticket_json

    run_btn = st.button("🚀 Run Multi-Agent", use_container_width=True)

    with st.expander("📝 Quick Steps for demo (quick script)", expanded=False):
        st.write(
            "- Select a sample ticket (VPN/Outlook/Disk)\n"
            "- Run in **direct** mode (fast)\n"
            "- Switch to **mcp** mode (agentified tools over **stdio**)\n"
            "- Click **Check MCP Status** to validate tools list\n"
            "- Show classification, steps, and user-ready communication\n"
            "- Download output JSON"
        )

with right:
    st.subheader("📊 Results")

    if run_btn:
        try:
            t0 = time.time()

            # Validate ticket JSON
            ticket = Ticket(**json.loads(ticket_json))

            if runner == "mcp":
                # Encourage using the stdio probe
                if "mcp_status" not in st.session_state:
                    st.info("MCP mode selected. Click 'Check MCP Status' to validate MCP stdio initialization.")
                else:
                    if not st.session_state.mcp_status.get("ok"):
                        st.warning("MCP status is OFFLINE (per last check). Run may fail.")

            with st.spinner("Running agents..."):
                if runner == "direct":
                    out = run_direct(ticket)
                else:
                    out = run_mcp(ticket)

            dt = round(time.time() - t0, 2)

            # KPIs
            c1, c2, c3 = st.columns(3)
            c1.metric("Runner", out.get("runner", runner))
            c2.metric("Time (sec)", dt)

            category = "N/A"
            try:
                category = out["classification"]["category"]
            except Exception:
                pass

            c3.metric("Category", category)

            st.markdown("<hr/>", unsafe_allow_html=True)

            tab1, tab2, tab3, tab4 = st.tabs(
                ["✅ Classification", "🛠 Troubleshooting", "💬 Communication", "🧾 Full JSON"]
            )

            with tab1:
                st.json(out.get("classification", {}))

            with tab2:
                st.json(out.get("troubleshooting", {}))

            with tab3:
                comm = out.get("communication", {})
                st.success("User message (send to user)")
                st.write(comm.get("user_message", ""))

                st.info("Ticket work notes (paste into ServiceNow)")
                st.write(comm.get("ticket_update", ""))

                st.write("Close recommendation:", comm.get("close_recommendation", False))

            with tab4:
                st.json(out)

            st.download_button(
                "⬇ Download full output JSON",
                data=json.dumps(out, indent=2),
                file_name="itsm_multiagent_output.json",
                mime="application/json",
                use_container_width=True
            )

        except Exception as e:
            if runner == "mcp":
                st.error("MCP runner failed to connect or execute tools.")
                st.info(
                    "✅ STDIO MCP Fix:\n"
                    "1) Do NOT run `python -m itsm_agents.mcp_server` manually (stdio expects a client to spawn it)\n"
                    "2) Click **Check MCP Status** in the sidebar (it spawns + initializes the server)\n"
                    "3) Ensure MCP SDK is installed in this venv: `pip install mcp`\n"
                    "4) Ensure your .env has:\n\n"
                    "   MCP_SERVER_COMMAND=python\n"
                    "   MCP_SERVER_ARGS=-m itsm_agents.mcp_server\n"
                )
            st.error(f"Error details: {e}")
            st.stop()


st.markdown("---")
st.caption(
    "If sample tickets do not load: ensure the folder 'samples/' exists at repo root. "
    "For STDIO MCP: you usually do not start the MCP server manually; the runner spawns it."  # [1](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports)
)