"""
Product 5 — Missed-Call SMS Responder
======================================
When a call goes unanswered, Claude composes a personalized SMS
within 30 seconds. The caller gets a friendly, on-brand text
before they have time to dial a competitor.

Usage as a library:
    from sms_composer import compose_sms
    result = compose_sms(
        caller_number="+12155551234",
        time_called="11:42 PM",
        business_name="Keystone Plumbing & Drain",
        owner_name="Mike Sullivan",
        business_type="plumbing",
        caller_name=None,       # optional — from CRM lookup
        last_service="Drain cleaning, March 2025",  # optional
    )
    # result = {"sms": "...", "chars": 142, "source": "claude"}
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from shared import claude_client

# ── Fallback templates (used if Claude call fails) ─────────────────────────────

FALLBACK_TEMPLATES = {
    "after_hours": (
        "Hi, this is {business_name} — sorry we missed your call at {time}. "
        "We'll be back in touch first thing in the morning. "
        "To book now: [BOOKING_LINK] — {owner_name}"
    ),
    "business_hours": (
        "Hi, this is {business_name} — sorry we missed your call. "
        "We're on another job but will call you back shortly. "
        "Book online anytime: [BOOKING_LINK]"
    ),
}

BUSINESS_HOURS_START = 8   # 8 AM
BUSINESS_HOURS_END   = 18  # 6 PM

SMS_SYSTEM_PROMPT = """You write missed-call SMS replies for local service businesses
(plumbers, HVAC, electricians, lawn care). Your SMS is the first thing the caller reads
after hanging up — it has to be warm, human, and immediately useful.

Rules:
- HARD LIMIT: 160 characters total (counts spaces and punctuation).
- If you know the caller's name, use it naturally in the opening.
- Reference the time of the call to feel personal, not automated.
- Include a clear CTA: reply to this text, call back, or book online.
- Sign off with the owner's first name or the business name — not both.
- NO marketing language, NO exclamation marks, NO emoji.
- Plain text only. No links unless [BOOKING_LINK] placeholder is appropriate.
- Sound like a person texted this, not a robot.
"""


def _is_after_hours(time_called: str) -> bool:
    """Return True if the call came in outside 8 AM–6 PM."""
    try:
        for fmt in ("%I:%M %p", "%H:%M", "%I %p"):
            try:
                t = datetime.strptime(time_called.strip(), fmt)
                return t.hour < BUSINESS_HOURS_START or t.hour >= BUSINESS_HOURS_END
            except ValueError:
                continue
    except Exception:
        pass
    return False


def compose_sms(
    caller_number: str,
    time_called: str,
    business_name: str,
    owner_name: str,
    business_type: str = "plumbing",
    caller_name: Optional[str] = None,
    last_service: Optional[str] = None,
) -> dict:
    """
    Compose a missed-call SMS via Claude.

    Returns:
        {
            "sms":    str,          # the SMS text
            "chars":  int,          # character count
            "source": "claude" | "fallback",
        }
    """
    after_hours = _is_after_hours(time_called)

    # Build caller context for Claude
    caller_ctx = f"Caller number: {caller_number}\n"
    if caller_name:
        caller_ctx += f"Caller name (from CRM): {caller_name}\n"
    else:
        caller_ctx += "Caller name: unknown\n"
    if last_service:
        caller_ctx += f"Last service (CRM history): {last_service}\n"
    caller_ctx += f"Time of missed call: {time_called}\n"
    caller_ctx += f"After business hours: {'Yes' if after_hours else 'No'}\n"

    user_message = (
        f"Business: {business_name} ({business_type})\n"
        f"Owner: {owner_name}\n"
        f"{caller_ctx}\n"
        "Write a missed-call SMS reply. Under 160 characters. No markdown."
    )

    try:
        sms = claude_client.complete(
            system=SMS_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
            max_tokens=80,
            temperature=0.4,
            label="missed_call_sms",
        ).strip()

        # Enforce hard limit — truncate at word boundary if Claude goes over
        if len(sms) > 160:
            sms = sms[:157].rsplit(" ", 1)[0] + "..."

        return {"sms": sms, "chars": len(sms), "source": "claude"}

    except Exception:
        # Fallback template — never leaves the caller without a reply
        template_key = "after_hours" if after_hours else "business_hours"
        sms = FALLBACK_TEMPLATES[template_key].format(
            business_name=business_name,
            owner_name=owner_name,
            time=time_called,
        )
        return {"sms": sms, "chars": len(sms), "source": "fallback"}
