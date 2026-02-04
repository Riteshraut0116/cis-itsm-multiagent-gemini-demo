from .schemas import Ticket
from .agents_direct import classify_ticket, troubleshoot_ticket, compose_response

def run(ticket: Ticket) -> dict:
    cls = classify_ticket(ticket)
    ts = troubleshoot_ticket(ticket, cls)
    comm = compose_response(ticket, cls, ts)

    return {
        "ticket": ticket.model_dump(),
        "classification": cls.model_dump(),
        "troubleshooting": ts.model_dump(),
        "communication": comm.model_dump(),
        "runner": "direct"
    }