from .schemas import Ticket, Classification, Troubleshooting, Communication
from .gemini_client import GeminiClient

_client = None

def client() -> GeminiClient:
    global _client
    if _client is None:
        _client = GeminiClient()
    return _client


def classify_ticket(ticket: Ticket) -> Classification:
    system = (
        "You are an ITSM Ticket Classification Agent for Cognizant CIS. "
        "You must return ONLY valid JSON and follow the schema strictly."
    )

    user = f"""
TASK:
Classify the ticket and return ONLY valid JSON (no markdown, no ``` fences, no extra text).

OUTPUT JSON SCHEMA (MUST follow exactly):
{{
  "category": "VPN | Email/Outlook | Access/AD | Network | Laptop/Device | Storage/Disk | Application | Other",
  "priority": "P1 | P2 | P3 | P4",
  "assignment_group": "string",
  "confidence": 0.0,
  "reason": "short text"
}}

STRICT RULES:
1) category MUST be exactly ONE of these values (case-sensitive):
   "VPN","Email/Outlook","Access/AD","Network","Laptop/Device","Storage/Disk","Application","Other"
   Do NOT shorten (example: do NOT output "Laptop"). Do NOT invent new values.
2) priority MUST be exactly one of: "P1","P2","P3","P4"
3) confidence MUST be a NUMBER between 0 and 1 (example: 0.72).
4) assignment_group should be a CIS-style group name. Use one of these patterns:
   - "CIS-VPN-Support"
   - "CIS-EUC-Support"
   - "CIS-Network-Ops"
   - "CIS-Access-Management"
   - "CIS-App-Support"
   If unsure, choose the closest one.
5) If not sure: set category="Other", priority="P3", confidence <= 0.6 and explain in reason.
6) Return ONLY JSON. No trailing commas.

TICKET:
{ticket.model_dump()}
""".strip()

    data = client().generate_json(system, user)
    return Classification(**data)


def troubleshoot_ticket(ticket: Ticket, cls: Classification) -> Troubleshooting:
    system = (
        "You are a CIS Troubleshooting Agent (L1/L2). "
        "You must return ONLY valid JSON and follow the schema strictly."
    )

    user = f"""
TASK:
Create a troubleshooting plan that a service desk engineer can follow.

OUTPUT JSON SCHEMA (MUST follow exactly):
{{
  "probable_cause": "short text",
  "steps": ["step 1", "step 2", "step 3", "step 4"],
  "data_needed": ["optional question 1", "optional question 2"],
  "risk_level": "Low | Medium | High"
}}

STRICT RULES:
1) steps MUST be a list of 4 to 5 short, clear steps (no more than 1-2 lines each).
2) data_needed MUST be a list (can be empty []).
3) risk_level MUST be exactly one of: "Low", "Medium", "High".
4) Return ONLY JSON. No markdown. No ``` fences. No trailing commas.

TICKET:
{ticket.model_dump()}

CLASSIFICATION:
{cls.model_dump()}
""".strip()

    data = client().generate_json(system, user)
    return Troubleshooting(**data)


def compose_response(ticket: Ticket, cls: Classification, ts: Troubleshooting) -> Communication:
    system = (
        "You are a Service Desk Communication Agent. "
        "Your response should be professional, short, and action-oriented. "
        "You must return ONLY valid JSON and follow the schema strictly."
    )

    user = f"""
TASK:
Write (1) a message to the user and (2) a work-notes update for the ticket.

OUTPUT JSON SCHEMA (MUST follow exactly):
{{
  "user_message": "short professional message",
  "ticket_update": "work notes text",
  "close_recommendation": false
}}

STRICT RULES:
1) user_message: short and polite; include next steps and questions from data_needed (if any).
2) ticket_update: include classification + probable cause + steps summary in service desk tone.
3) close_recommendation MUST be true/false (boolean, not string).
4) Return ONLY JSON. No markdown. No ``` fences. No trailing commas.

TICKET:
{ticket.model_dump()}

CLASSIFICATION:
{cls.model_dump()}

TROUBLESHOOTING:
{ts.model_dump()}
""".strip()

    data = client().generate_json(system, user)
    return Communication(**data)