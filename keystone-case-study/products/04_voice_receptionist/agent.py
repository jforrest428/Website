"""
Product 4 — 24/7 AI Voice Receptionist
=======================================
Layer A: Real Claude agent with tool-use.

The ReceptionistAgent handles inbound calls for Keystone Plumbing:
- Greets callers as "Dawn"
- Triages emergencies
- Collects caller info
- Offers appointment slots from the live dataset
- Books appointments and logs to call_log.jsonl
- Escalates emergencies to on-call tech

Usage as a library:
    agent = ReceptionistAgent()
    reply = agent.handle_turn([], "Hi, I have a burst pipe!")
"""

import json
import random
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from rich.console import Console

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from shared import brand, claude_client, data_loader

console = Console()
CALL_LOG_PATH = Path(__file__).parent / "call_log.jsonl"

# ── Tool Definitions (Anthropic format) ───────────────────────────────────────

TOOLS = [
    {
        "name": "get_available_slots",
        "description": "Get available appointment slots for scheduling a service call. Returns 3 concrete date/time options based on current technician availability.",
        "input_schema": {
            "type": "object",
            "properties": {
                "job_type": {
                    "type": "string",
                    "description": "Type of job (e.g., 'Drain Cleaning', 'Water Heater Repair')",
                },
                "urgency": {
                    "type": "string",
                    "enum": ["same-day", "next-day", "this-week"],
                    "description": "How urgent is the appointment?",
                },
            },
            "required": ["job_type", "urgency"],
        },
    },
    {
        "name": "book_appointment",
        "description": "Book an appointment for a customer and assign a technician.",
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_name": {"type": "string"},
                "customer_phone": {"type": "string"},
                "service_address": {"type": "string"},
                "job_type": {"type": "string"},
                "slot": {"type": "string", "description": "Slot string returned by get_available_slots"},
                "issue_description": {"type": "string"},
            },
            "required": ["customer_name", "customer_phone", "service_address", "job_type", "slot"],
        },
    },
    {
        "name": "send_sms_confirmation",
        "description": "Send an SMS confirmation to the customer with their appointment details.",
        "input_schema": {
            "type": "object",
            "properties": {
                "phone": {"type": "string"},
                "customer_name": {"type": "string"},
                "appointment_details": {"type": "string", "description": "Full appointment summary for the SMS"},
            },
            "required": ["phone", "customer_name", "appointment_details"],
        },
    },
    {
        "name": "escalate_to_oncall",
        "description": "Escalate an emergency call to the on-call technician. Use this for: burst pipes, flooding, sewage backup, no heat in winter, gas smell, no water.",
        "input_schema": {
            "type": "object",
            "properties": {
                "emergency_type": {"type": "string", "description": "Brief description of the emergency"},
                "caller_name": {"type": "string"},
                "caller_phone": {"type": "string"},
                "service_address": {"type": "string"},
                "additional_details": {"type": "string"},
            },
            "required": ["emergency_type", "caller_phone"],
        },
    },
]


# ── Tool Implementations ───────────────────────────────────────────────────────

def _find_available_slots(job_type: str, urgency: str) -> list[dict]:
    """Look at the jobs sheet to find realistic open slots."""
    j = data_loader.jobs()
    techs = data_loader.technicians()

    as_of = data_loader.latest_job_date().date()

    if urgency == "same-day":
        search_start = as_of
        search_end = as_of + timedelta(days=1)
    elif urgency == "next-day":
        search_start = as_of + timedelta(days=1)
        search_end = as_of + timedelta(days=3)
    else:  # this-week
        search_start = as_of + timedelta(days=1)
        search_end = as_of + timedelta(days=7)

    # Find which techs are booked during this window
    window_jobs = j[
        (j["Scheduled"].dt.date >= search_start)
        & (j["Scheduled"].dt.date <= search_end)
        & (j["Status"].isin(["Scheduled", "Completed"]))
    ]

    busy_techs_by_day: dict[date, set] = {}
    for _, row in window_jobs.iterrows():
        d = row["Scheduled"].date()
        busy_techs_by_day.setdefault(d, set()).add(row["Tech ID"])

    # Generate 3 slots with available techs
    all_tech_ids = techs["Tech ID"].tolist()
    all_tech_names = dict(zip(techs["Tech ID"], techs["Name"]))

    slots = []
    slot_date = search_start
    while len(slots) < 3 and slot_date <= search_end + timedelta(days=7):
        if slot_date.weekday() < 6:  # Mon-Sat
            busy = busy_techs_by_day.get(slot_date, set())
            available = [t for t in all_tech_ids if t not in busy]
            if available:
                tech_id = random.choice(available)
                # Morning or afternoon slot
                hour = random.choice([8, 10, 13, 15])
                time_str = f"{hour}:00 AM" if hour < 12 else f"{hour-12}:00 PM"
                slots.append({
                    "slot_id": f"SLOT-{slot_date.strftime('%Y%m%d')}-{hour:02d}",
                    "date": str(slot_date),
                    "time": time_str,
                    "tech_id": tech_id,
                    "tech_name": all_tech_names.get(tech_id, "Our technician"),
                    "display": f"{slot_date.strftime('%A, %B %d')} at {time_str} with {all_tech_names.get(tech_id, 'our technician')}",
                })
        slot_date += timedelta(days=1)

    return slots[:3]


def _log_call(entry: dict) -> None:
    CALL_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CALL_LOG_PATH.open("a", encoding="utf-8") as f:
        entry["logged_at"] = datetime.now().isoformat()
        f.write(json.dumps(entry) + "\n")


class ReceptionistToolHandler(claude_client.ToolHandler):
    """Handles all tool calls for the receptionist agent."""

    def handle(self, tool_name: str, tool_input: dict) -> Any:
        if tool_name == "get_available_slots":
            return self._get_available_slots(**tool_input)
        elif tool_name == "book_appointment":
            return self._book_appointment(**tool_input)
        elif tool_name == "send_sms_confirmation":
            return self._send_sms_confirmation(**tool_input)
        elif tool_name == "escalate_to_oncall":
            return self._escalate_to_oncall(**tool_input)
        else:
            return {"error": f"Unknown tool: {tool_name}"}

    def _get_available_slots(self, job_type: str, urgency: str, **_) -> dict:
        slots = _find_available_slots(job_type, urgency)
        result = {
            "slots": slots,
            "message": f"Found {len(slots)} available slots for {job_type}.",
        }
        _log_call({"event": "slots_queried", "job_type": job_type, "urgency": urgency, "slots": slots})
        return result

    def _book_appointment(
        self,
        customer_name: str,
        customer_phone: str,
        service_address: str,
        job_type: str,
        slot: str,
        issue_description: str = "",
        **_,
    ) -> dict:
        # Find the slot details from the slot_id or slot string
        slots = _find_available_slots(job_type, "this-week")
        matched_slot = next((s for s in slots if s["slot_id"] == slot or s["display"] == slot), slots[0] if slots else None)

        booking = {
            "confirmation_number": f"KP-{random.randint(10000, 99999)}",
            "customer_name": customer_name,
            "customer_phone": customer_phone,
            "service_address": service_address,
            "job_type": job_type,
            "issue_description": issue_description,
            "tech_name": matched_slot["tech_name"] if matched_slot else "Our senior technician",
            "appointment_date": matched_slot["date"] if matched_slot else str(data_loader.latest_job_date().date() + timedelta(days=2)),
            "appointment_time": matched_slot["time"] if matched_slot else "10:00 AM",
            "status": "confirmed",
        }

        _log_call({"event": "appointment_booked", **booking})
        console.print(f"    [green]📅 BOOKED:[/green] {booking['confirmation_number']} — {booking['customer_name']} on {booking['appointment_date']}")
        return booking

    def _send_sms_confirmation(self, phone: str, customer_name: str, appointment_details: str, **_) -> dict:
        sms_record = {
            "event": "sms_sent",
            "to": phone,
            "customer_name": customer_name,
            "message": appointment_details,
        }
        _log_call(sms_record)
        console.print(f"    [blue]📱 SMS sent to {phone}:[/blue] {appointment_details[:80]}…")
        return {"success": True, "message": f"Confirmation SMS sent to {phone}"}

    def _escalate_to_oncall(
        self,
        emergency_type: str,
        caller_phone: str,
        caller_name: str = "Unknown",
        service_address: str = "Unknown",
        additional_details: str = "",
        **_,
    ) -> dict:
        on_call_tech = brand.TECHS.get(brand.ON_CALL_TECH_ID, {})
        escalation = {
            "event": "emergency_escalation",
            "emergency_type": emergency_type,
            "caller_name": caller_name,
            "caller_phone": caller_phone,
            "service_address": service_address,
            "additional_details": additional_details,
            "on_call_tech": on_call_tech.get("name", "Mike Sullivan"),
            "on_call_tech_id": brand.ON_CALL_TECH_ID,
            "eta_minutes": random.randint(20, 45),
        }
        _log_call(escalation)
        console.print(f"    [bold red]🚨 EMERGENCY ESCALATED:[/bold red] {emergency_type} → {on_call_tech.get('name')} dispatched")
        return {
            "escalated": True,
            "on_call_tech": on_call_tech.get("name", "Mike Sullivan"),
            "eta_minutes": escalation["eta_minutes"],
            "message": f"Emergency escalated. {on_call_tech.get('name', 'Mike')} is the on-call tech and will call within 5 minutes. ETA {escalation['eta_minutes']} min.",
        }


# ── ReceptionistAgent ──────────────────────────────────────────────────────────

class ReceptionistAgent:
    """
    Stateless per-turn receptionist agent.

    Usage:
        agent = ReceptionistAgent()
        # First turn
        reply, messages = agent.handle_turn([], "I have a burst pipe!")
        # Subsequent turns
        reply, messages = agent.handle_turn(messages, "It's at 123 Oak St, Philadelphia")
    """

    def __init__(self):
        self.tool_handler = ReceptionistToolHandler()

    def handle_turn(
        self,
        transcript_so_far: list[dict],
        latest_user_message: str,
    ) -> tuple[str, list[dict]]:
        """
        Process one turn of the conversation.

        Args:
            transcript_so_far: List of prior messages (role/content dicts).
            latest_user_message: The caller's latest utterance.

        Returns:
            (agent_reply: str, updated_messages: list[dict])
        """
        messages = list(transcript_so_far)
        messages.append({"role": "user", "content": latest_user_message})

        reply, updated = claude_client.complete_with_tools(
            system=brand.RECEPTIONIST_SYSTEM_PROMPT,
            messages=messages,
            tools=TOOLS,
            tool_handler=self.tool_handler,
            max_tokens=512,
            temperature=0.3,
            label="receptionist turn",
        )

        return reply, updated
