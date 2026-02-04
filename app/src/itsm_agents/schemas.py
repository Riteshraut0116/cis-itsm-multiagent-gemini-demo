from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal


class Ticket(BaseModel):
    ticket_id: str
    short_description: str
    description: str
    caller: str = "Unknown"
    impact: Optional[str] = None
    urgency: Optional[str] = None


class Classification(BaseModel):
    category: Literal[
        "VPN", "Email/Outlook", "Access/AD", "Network",
        "Laptop/Device", "Storage/Disk", "Application", "Other"
    ]
    priority: Literal["P1", "P2", "P3", "P4"]
    assignment_group: str
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str

    @field_validator("category", mode="before")
    @classmethod
    def normalize_category(cls, v):
        """
        Gemini sometimes returns values like 'Laptop' instead of 'Laptop/Device'.
        This validator normalizes common variants so the demo never crashes.
        """
        if not isinstance(v, str):
            return "Other"

        x = v.strip().lower()

        mapping = {
            "vpn": "VPN",

            "email": "Email/Outlook",
            "outlook": "Email/Outlook",
            "mail": "Email/Outlook",

            "access": "Access/AD",
            "ad": "Access/AD",
            "active directory": "Access/AD",
            "login": "Access/AD",

            "network": "Network",

            "laptop": "Laptop/Device",
            "device": "Laptop/Device",
            "desktop": "Laptop/Device",
            "pc": "Laptop/Device",
            "endpoint": "Laptop/Device",

            "disk": "Storage/Disk",
            "storage": "Storage/Disk",
            "low disk": "Storage/Disk",

            "application": "Application",
            "app": "Application",

            "other": "Other",
        }

        if x in mapping:
            return mapping[x]

        # partial match fallback
        if "outlook" in x or "email" in x:
            return "Email/Outlook"
        if "disk" in x or "storage" in x:
            return "Storage/Disk"
        if "laptop" in x or "device" in x or "desktop" in x:
            return "Laptop/Device"
        if "access" in x or "login" in x or x == "ad":
            return "Access/AD"
        if "vpn" in x:
            return "VPN"
        if "network" in x:
            return "Network"
        if "app" in x:
            return "Application"

        return "Other"


class Troubleshooting(BaseModel):
    probable_cause: str
    steps: List[str]
    data_needed: List[str] = []
    risk_level: Literal["Low", "Medium", "High"] = "Low"


class Communication(BaseModel):
    user_message: str
    ticket_update: str
    close_recommendation: bool