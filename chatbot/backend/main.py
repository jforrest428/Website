import os
import re
import json
import time
import uuid
import smtplib
import logging
from datetime import datetime, date
from collections import defaultdict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

import anthropic
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request

load_dotenv()  # loads .env in local dev; no-op in prod where vars are injected
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from system_prompt import SYSTEM_PROMPT

# ─── Logging ────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ─── App ────────────────────────────────────────────────────────────────────
app = FastAPI(title="Forrest Analytics Chatbot API", version="1.0.0")

ALLOWED_ORIGINS = [
    "https://forrestanalyticsgroup.com",
    "https://www.forrestanalyticsgroup.com",
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1",
    "http://127.0.0.1:5500",
    "null",  # local file:// during testing
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# ─── In-memory state ─────────────────────────────────────────────────────────
# conversation_id -> list of {role, content}
conversations: dict[str, list] = {}

# conversation_id -> metadata dict
conversation_meta: dict[str, dict] = {}

# rate limiting: ip -> list of timestamps
ip_message_counts: dict[str, list] = defaultdict(list)
hourly_conversation_counts: list = []  # list of epoch timestamps

# stats
daily_stats: dict[str, dict] = {}

MAX_MESSAGES_PER_CONVERSATION = 30
MAX_CONVERSATIONS_PER_HOUR = 100
CONVERSATIONS_DIR = "conversations"

os.makedirs(CONVERSATIONS_DIR, exist_ok=True)

# ─── Models ──────────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str
    session_data: Optional[dict] = None  # vertical hint, etc.


class ChatResponse(BaseModel):
    conversation_id: str
    reply: str
    message_count: int
    lead_captured: bool
    booking_requested: bool


# ─── Helpers ─────────────────────────────────────────────────────────────────
def sanitize_input(text: str) -> str:
    """Strip HTML, limit length, remove null bytes."""
    text = text.replace("\x00", "")
    text = re.sub(r"<[^>]+>", "", text)  # strip HTML tags
    text = text.strip()
    return text[:2000]  # hard cap


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def check_rate_limits(ip: str) -> None:
    now = time.time()
    # Per-IP: max 30 messages per conversation (tracked per conv, but also globally)
    # Hourly conversation cap
    global hourly_conversation_counts
    hourly_conversation_counts = [t for t in hourly_conversation_counts if now - t < 3600]
    if len(hourly_conversation_counts) >= MAX_CONVERSATIONS_PER_HOUR:
        raise HTTPException(status_code=429, detail="Service busy — please try again in a few minutes.")


def is_jailbreak_attempt(text: str) -> bool:
    patterns = [
        r"ignore (your|all|previous|the) (instructions|prompt|system)",
        r"pretend (you are|to be|you're)",
        r"act as (a different|an? alternative|unrestricted)",
        r"you are now",
        r"DAN mode",
        r"jailbreak",
        r"override your",
        r"disregard your",
        r"forget your instructions",
        r"new (instructions|system prompt|persona)",
    ]
    text_lower = text.lower()
    return any(re.search(p, text_lower) for p in patterns)


def extract_lead_capture(text: str) -> Optional[dict]:
    """Extract structured lead data from [LEAD_CAPTURE: ...] marker."""
    match = re.search(r"\[LEAD_CAPTURE:\s*([^\]]+)\]", text, re.IGNORECASE)
    if not match:
        return None
    raw = match.group(1)
    data = {}
    for part in raw.split(","):
        if "=" in part:
            k, v = part.split("=", 1)
            data[k.strip()] = v.strip()
    return data if data else None


def extract_booking_intent(text: str) -> bool:
    patterns = [
        r"book(ed|ing)?\s+(a|the)?\s*(call|audit|appointment|session|meeting)",
        r"schedul(e|ing|ed)\s+(a|the)?\s*(call|audit)",
        r"grab\s+(a\s+)?spot",
        r"get\s+(on\s+)?the\s+calendar",
        r"free\s+(15|fifteen)[- ]minute",
    ]
    text_lower = text.lower()
    return any(re.search(p, text_lower) for p in patterns)


def get_today_key() -> str:
    return date.today().isoformat()


def record_daily_stat(key: str, value=None):
    today = get_today_key()
    if today not in daily_stats:
        daily_stats[today] = {
            "conversations": 0,
            "messages": 0,
            "leads_captured": 0,
            "bookings": 0,
            "questions": defaultdict(int),
        }
    if key == "conversation":
        daily_stats[today]["conversations"] += 1
    elif key == "message":
        daily_stats[today]["messages"] += 1
    elif key == "lead":
        daily_stats[today]["leads_captured"] += 1
    elif key == "booking":
        daily_stats[today]["bookings"] += 1
    elif key == "question" and value:
        daily_stats[today]["questions"][value] += 1


def save_conversation_log(conv_id: str, messages: list, meta: dict):
    """Persist conversation to disk as JSON."""
    filepath = os.path.join(CONVERSATIONS_DIR, f"{conv_id}.json")
    payload = {
        "conversation_id": conv_id,
        "timestamp": datetime.utcnow().isoformat(),
        "meta": meta,
        "messages": messages,
    }
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to save conversation log: {e}")


def send_lead_email(lead: dict, conv_id: str, messages: list, meta: dict):
    """Send lead notification + transcript to josh@ via Zoho SMTP."""
    zoho_email = os.getenv("ZOHO_EMAIL")
    zoho_password = os.getenv("ZOHO_APP_PASSWORD")
    if not zoho_email or not zoho_password:
        logger.warning("Zoho SMTP not configured — skipping email")
        return

    to_addr = "josh@forrestanalyticsgroup.com"

    # Build transcript
    transcript_lines = []
    for msg in messages:
        role = "Visitor" if msg["role"] == "user" else "Assistant"
        transcript_lines.append(f"[{role}]\n{msg['content']}\n")
    transcript = "\n".join(transcript_lines)

    name = lead.get("name", "Unknown")
    email = lead.get("email", "Unknown")
    phone = lead.get("phone", "Unknown")
    business = lead.get("business", "Unknown")
    recommended = meta.get("recommended_products", "Not specified")
    qualification_notes = meta.get("qualification_notes", "")

    subject = f"New Lead from Chatbot: {name} — {business}"

    body = f"""New lead captured via the Forrest Analytics chatbot.

LEAD INFORMATION
────────────────
Name:          {name}
Email:         {email}
Phone:         {phone}
Business Type: {business}

AI RECOMMENDATION
─────────────────
{recommended}

QUALIFICATION NOTES
───────────────────
{qualification_notes}

CONVERSATION TRANSCRIPT
───────────────────────
{transcript}

────────────────────────────────────────
Conversation ID: {conv_id}
Captured at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}
"""

    msg = MIMEMultipart()
    msg["From"] = zoho_email
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.zoho.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.login(zoho_email, zoho_password)
            server.sendmail(zoho_email, to_addr, msg.as_string())
        logger.info(f"Lead email sent for conversation {conv_id}")
    except Exception as e:
        logger.error(f"Failed to send lead email: {e}")


# ─── Routes ──────────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@app.get("/stats")
async def stats():
    today = get_today_key()
    today_data = daily_stats.get(today, {
        "conversations": 0,
        "messages": 0,
        "leads_captured": 0,
        "bookings": 0,
        "questions": {},
    })

    total_convs = today_data["conversations"]
    leads = today_data["leads_captured"]
    bookings = today_data["bookings"]

    qual_rate = round(leads / total_convs * 100, 1) if total_convs > 0 else 0
    booking_rate = round(bookings / total_convs * 100, 1) if total_convs > 0 else 0

    questions = dict(today_data.get("questions", {}))
    top_questions = sorted(questions.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        "date": today,
        "conversations_today": total_convs,
        "messages_today": today_data["messages"],
        "leads_captured": leads,
        "bookings_requested": bookings,
        "qualification_rate_pct": qual_rate,
        "booking_rate_pct": booking_rate,
        "top_topics": [{"topic": q, "count": c} for q, c in top_questions],
        "active_conversations": len(conversations),
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: Request, body: ChatRequest):
    ip = get_client_ip(request)

    # Rate limit check
    check_rate_limits(ip)

    # Sanitize input
    user_message = sanitize_input(body.message)
    if not user_message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    # Jailbreak guard
    if is_jailbreak_attempt(user_message):
        return ChatResponse(
            conversation_id=body.conversation_id or str(uuid.uuid4()),
            reply="I'm here to help with Forrest Analytics' AI tools for service businesses — what can I help you with?",
            message_count=0,
            lead_captured=False,
            booking_requested=False,
        )

    # Get or create conversation
    conv_id = body.conversation_id or str(uuid.uuid4())
    is_new = conv_id not in conversations

    if is_new:
        conversations[conv_id] = []
        conversation_meta[conv_id] = {
            "started_at": datetime.utcnow().isoformat(),
            "ip": ip,
            "lead_captured": False,
            "booking_requested": False,
            "recommended_products": "",
            "qualification_notes": "",
            "message_count": 0,
        }
        hourly_conversation_counts.append(time.time())
        record_daily_stat("conversation")

    meta = conversation_meta[conv_id]

    # Per-conversation message cap
    if meta["message_count"] >= MAX_MESSAGES_PER_CONVERSATION:
        return ChatResponse(
            conversation_id=conv_id,
            reply="We've covered a lot of ground! To keep the conversation going, please reach out directly at josh@forrestanalyticsgroup.com or grab a free audit call at forrestanalyticsgroup.com/small-business/",
            message_count=meta["message_count"],
            lead_captured=meta["lead_captured"],
            booking_requested=meta["booking_requested"],
        )

    # Append user message
    conversations[conv_id].append({"role": "user", "content": user_message})
    meta["message_count"] += 1
    record_daily_stat("message")

    # Build messages for Claude
    claude_messages = conversations[conv_id]

    # Add session context to system prompt if vertical hint provided
    system = SYSTEM_PROMPT
    if body.session_data and body.session_data.get("vertical_hint"):
        system += f"\n\n[CONTEXT: Visitor may be from the '{body.session_data['vertical_hint']}' vertical based on their entry point.]"

    # Call Claude
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=600,
            system=system,
            messages=claude_messages,
        )
        assistant_reply = response.content[0].text
    except Exception as e:
        logger.error(f"Claude API error: {e}")
        raise HTTPException(status_code=502, detail="AI service temporarily unavailable.")

    # Append assistant message
    conversations[conv_id].append({"role": "assistant", "content": assistant_reply})

    # Check for lead capture marker
    lead_data = extract_lead_capture(assistant_reply)
    lead_captured = False
    if lead_data and not meta["lead_captured"]:
        meta["lead_captured"] = True
        meta["qualification_notes"] = f"Business: {lead_data.get('business', 'unknown')}"
        lead_captured = True
        record_daily_stat("lead")
        # Send email notification (non-blocking in prod — fire and forget)
        try:
            send_lead_email(lead_data, conv_id, conversations[conv_id], meta)
        except Exception as e:
            logger.error(f"Lead email error: {e}")
        # Save log immediately
        save_conversation_log(conv_id, conversations[conv_id], meta)

    # Check for booking intent
    booking_requested = False
    if extract_booking_intent(assistant_reply) and not meta["booking_requested"]:
        meta["booking_requested"] = True
        booking_requested = True
        record_daily_stat("booking")

    # Strip the lead capture marker from the visible reply
    visible_reply = re.sub(r"\[LEAD_CAPTURE:[^\]]*\]", "", assistant_reply).strip()

    # Periodic log save (every 5 messages)
    if meta["message_count"] % 5 == 0:
        save_conversation_log(conv_id, conversations[conv_id], meta)

    return ChatResponse(
        conversation_id=conv_id,
        reply=visible_reply,
        message_count=meta["message_count"],
        lead_captured=lead_captured,
        booking_requested=booking_requested,
    )
