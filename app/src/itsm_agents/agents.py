from .gemini_client import GeminiClient
from .schemas import Ticket, Classification, Troubleshooting, Communication

client = None

def get_client():
    global client
    if client is None:
        client = GeminiClient()
    return client

def classifier_agent(ticket: Ticket) -> Classification:
    system = "You are an ITSM Ticket Classification Agent for CIS operations."
    user = f"""
Classify this ITSM ticket into:
- category (VPN, Email/Outlook, Access/AD, Network, Laptop/Device, Storage/Disk, Application, Other)
- priority (P1-P4)
- assignment_group (string)
- confidence (0 to 1)
- reason (short)

Ticket:
ticket_id: {ticket.ticket_id}
short_description: {ticket.short_description}
description: {ticket.description}
impact: {ticket.impact}
urgency: {ticket.urgency}
"""
    data = get_client().generate_json(system, user)
    return Classification(**data)

def troubleshooter_agent(ticket: Ticket, cls: Classification) -> Troubleshooting:
    system = "You are a CIS L1/L2 Troubleshooting Agent."
    user = f"""
Create troubleshooting plan for this ticket.
Return JSON with:
- probable_cause
- steps (list of 4-7 steps)
- data_needed (list of any info needed from user)
- risk_level (Low/Medium/High)

Ticket:
{ticket.model_dump()}

Classification:
{cls.model_dump()}
"""
    data = get_client().generate_json(system, user)
    return Troubleshooting(**data)

def communication_agent(ticket: Ticket, cls: Classification, ts: Troubleshooting) -> Communication:
    system = "You are a Service Desk Communication Agent. Keep message professional and short."
    user = f"""
Write:
1) user_message: message to the end user with steps/questions
2) ticket_update: message that can be pasted into ServiceNow work notes
3) close_recommendation: true if issue likely resolved by steps, else false

Return JSON with fields:
user_message, ticket_update, close_recommendation

Ticket:
{ticket.model_dump()}

Classification:
{cls.model_dump()}

Troubleshooting:
{ts.model_dump()}
"""
    data = get_client().generate_json(system, user)
    return Communication(**data)