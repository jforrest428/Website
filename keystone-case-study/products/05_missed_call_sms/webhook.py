"""
Product 5 — Missed-Call SMS Webhook (Twilio)
=============================================
Flask app that Twilio calls when an inbound call goes unanswered.
Composes a personalized SMS via Claude and sends it back to the caller.

Deploy to Railway, Render, or any public server.
Set the following env vars:
    TWILIO_ACCOUNT_SID
    TWILIO_AUTH_TOKEN
    TWILIO_PHONE           (your Twilio number, e.g. +12155550100)
    BUSINESS_NAME          (default: Keystone Plumbing & Drain)
    OWNER_NAME             (default: Mike Sullivan)
    BUSINESS_TYPE          (default: plumbing)
    BOOKING_LINK           (optional URL for online booking)

In Twilio console, set the Voice > "Call Status Changes" webhook URL to:
    https://your-server.com/missed-call

The webhook returns a 204 No Content — Twilio only needs the SMS sent,
not a TwiML response from this endpoint.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

from flask import Flask, Response, abort, request

ROOT    = Path(__file__).parent.parent.parent
PRODUCT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(PRODUCT))

from shared.data_loader import customers  # optional CRM lookup

from sms_composer import compose_sms

try:
    from twilio.rest import Client as TwilioClient
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False

# ── Config from environment ────────────────────────────────────────────────────

TWILIO_SID   = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN",   "")
TWILIO_PHONE = os.getenv("TWILIO_PHONE",         "")
BUSINESS_NAME = os.getenv("BUSINESS_NAME",       "Keystone Plumbing & Drain")
OWNER_NAME    = os.getenv("OWNER_NAME",           "Mike Sullivan")
BUSINESS_TYPE = os.getenv("BUSINESS_TYPE",        "plumbing")
BOOKING_LINK  = os.getenv("BOOKING_LINK",         "")

LOG_PATH = Path(__file__).parent / "missed_calls.jsonl"

# Twilio call statuses that mean the call was NOT answered
MISSED_STATUSES = {"no-answer", "busy", "failed", "canceled"}

app = Flask(__name__)


def _crm_lookup(caller_number: str) -> dict:
    """Look up caller in the Keystone dataset. Returns {} if not found."""
    try:
        df = customers()
        match = df[df["Phone"].str.replace(r"\D", "", regex=True) ==
                   caller_number.replace("+1", "").replace("-", "").replace(" ", "")]
        if len(match):
            row = match.iloc[0]
            return {
                "caller_name": row.get("Name", ""),
                "last_service": "",  # could join with jobs sheet if needed
            }
    except Exception:
        pass
    return {}


def _log_call(payload: dict) -> None:
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(payload) + "\n")


def _send_sms(to: str, body: str) -> str:
    """Send SMS via Twilio. Returns message SID or 'dry-run'."""
    if not TWILIO_AVAILABLE or not TWILIO_SID:
        return "dry-run"
    client = TwilioClient(TWILIO_SID, TWILIO_TOKEN)
    msg = client.messages.create(to=to, from_=TWILIO_PHONE, body=body)
    return msg.sid


@app.route("/health")
def health():
    return {"status": "ok", "product": "missed_call_sms"}, 200


@app.route("/missed-call", methods=["POST"])
def missed_call():
    """
    Twilio StatusCallback endpoint.
    Triggered for every call status change — we only act on missed ones.
    """
    call_status   = request.form.get("CallStatus", "")
    caller_number = request.form.get("From", "")
    call_duration = int(request.form.get("CallDuration", "0") or "0")
    call_sid      = request.form.get("CallSid", "")
    timestamp     = datetime.now().strftime("%I:%M %p")

    # Only act on genuinely missed calls
    if call_status not in MISSED_STATUSES and call_duration > 10:
        return Response(status=204)

    # CRM lookup (optional — graceful if dataset not available)
    crm = _crm_lookup(caller_number)

    result = compose_sms(
        caller_number=caller_number,
        time_called=timestamp,
        business_name=BUSINESS_NAME,
        owner_name=OWNER_NAME,
        business_type=BUSINESS_TYPE,
        caller_name=crm.get("caller_name"),
        last_service=crm.get("last_service"),
    )

    # Sub in real booking link if configured
    sms_body = result["sms"]
    if BOOKING_LINK:
        sms_body = sms_body.replace("[BOOKING_LINK]", BOOKING_LINK)

    sms_sid = _send_sms(caller_number, sms_body)

    _log_call({
        "timestamp":     datetime.utcnow().isoformat(),
        "call_sid":      call_sid,
        "caller":        caller_number,
        "status":        call_status,
        "duration":      call_duration,
        "sms":           sms_body,
        "sms_chars":     result["chars"],
        "sms_source":    result["source"],
        "sms_sid":       sms_sid,
    })

    return Response(status=204)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)), debug=False)
