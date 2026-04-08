"""
Product 4 — Scripted Demo: 4 Realistic Call Scenarios
======================================================
Runs pre-scripted conversations through the real ReceptionistAgent
and prints formatted transcripts.

Usage:
    python scripted_demo.py                    # run all 4 scenarios
    python scripted_demo.py --scenario 1       # run scenario 1 only
    python scripted_demo.py --no-audio         # skip ElevenLabs TTS

Scenarios:
    1. After-hours burst pipe (emergency escalation)
    2. Daytime water heater quote (standard booking)
    3. Clogged drain routine booking (standard booking)
    4. Commercial property manager (multi-unit)
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from agent import ReceptionistAgent

console = Console(width=100)
AUDIO_DIR = Path(__file__).parent / "audio"
AUDIO_DIR.mkdir(exist_ok=True)

# ── Scripted Scenarios ─────────────────────────────────────────────────────────

SCENARIOS = [
    {
        "id": 1,
        "title": "After-Hours Burst Pipe — Emergency Escalation",
        "description": "11:30 PM call. Pipe burst in basement. Agent triages as emergency and dispatches on-call tech.",
        "caller": "James Whitfield",
        "turns": [
            "Hi, I need help! I have water everywhere — my basement pipe just burst and it's flooding fast.",
            "James Whitfield, 215-555-0923.",
            "47 Lakeview Drive, Wayne, Pennsylvania.",
            "The pipe is behind the water heater. Water is coming out fast. I turned off the main but there's already a few inches on the floor.",
        ],
    },
    {
        "id": 2,
        "title": "Daytime Water Heater Quote — Standard Booking",
        "description": "2pm weekday call. Hot water not working. Agent books appointment and sends SMS confirmation.",
        "caller": "Patricia Nguyen",
        "turns": [
            "Hi, I called because I don't have any hot water. My water heater is about 12 years old so I think it might need to be replaced.",
            "Patricia Nguyen.",
            "832 Chestnut Hill Avenue, Glenside, PA 19038.",
            "215-555-4471.",
            "It's making a popping noise too and the water is lukewarm at best. I'm flexible on timing — whenever you can get someone out.",
            "The second one works for me.",
        ],
    },
    {
        "id": 3,
        "title": "Clogged Drain Routine Booking",
        "description": "Morning call. Kitchen drain clogged. Routine same-week booking.",
        "caller": "Robert Castellano",
        "turns": [
            "Hi, my kitchen sink has been draining really slowly for about two weeks. I've tried drain cleaner but it's not helping.",
            "Robert Castellano, at 19 Maple Street, Ardmore, Pennsylvania.",
            "My number is 610-555-0278.",
            "Just the kitchen sink. Dishwasher seems fine. No smell or anything, just really slow.",
            "Thursday morning works perfectly.",
        ],
    },
    {
        "id": 4,
        "title": "Commercial Property Manager — Multi-Unit Building",
        "description": "Property manager calling about recurring drain issues across 3 units.",
        "caller": "Sandra Kim",
        "turns": [
            "Hi, I'm Sandra Kim. I manage a six-unit apartment building in Norristown and I've been having recurring drain issues in three of my units. I'd like to set up a service call.",
            "It's 400 West Marshall Street, Norristown, PA 19401. The affected units are 2B, 3A, and 4C.",
            "My cell is 484-555-0931.",
            "They've all had slow drains for about a month. I suspect there's a main line issue. One of the tenants mentioned sewage smell occasionally.",
            "I'd prefer a morning appointment if possible. The tenants are cooperative — they work from home.",
            "Thursday morning is ideal. Can you give me an estimate of what a camera inspection would run for a 6-unit building?",
        ],
    },
]


# ── TTS (optional ElevenLabs) ──────────────────────────────────────────────────

def _speak(text: str, voice_id: str, filename: Path) -> bool:
    """Generate audio via ElevenLabs. Returns True if successful."""
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        return False
    try:
        import requests
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {"xi-api-key": api_key, "Content-Type": "application/json"}
        payload = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
        }
        r = requests.post(url, json=payload, headers=headers, timeout=30)
        if r.status_code == 200:
            filename.write_bytes(r.content)
            return True
    except Exception as e:
        console.print(f"[dim]TTS error: {e}[/dim]")
    return False


# ── Transcript Rendering ───────────────────────────────────────────────────────

def render_turn(speaker: str, text: str, is_agent: bool = False) -> None:
    if is_agent:
        style = "bold cyan"
        prefix = "🤖 Dawn"
        panel_style = "cyan"
    else:
        style = "bold white"
        prefix = f"👤 {speaker}"
        panel_style = "white"

    console.print(Panel(
        text,
        title=f"[{style}]{prefix}[/{style}]",
        border_style=panel_style,
        padding=(0, 1),
    ))


def run_scenario(scenario: dict, use_audio: bool = False) -> list[dict]:
    """Run a single scripted scenario through the real agent. Returns full transcript."""
    console.print()
    console.rule(f"[bold yellow]Scenario {scenario['id']}: {scenario['title']}[/bold yellow]")
    console.print(f"[dim]{scenario['description']}[/dim]")
    console.print()

    agent = ReceptionistAgent()
    messages: list[dict] = []
    transcript: list[dict] = []

    # ElevenLabs voice IDs
    dawn_voice_id = os.getenv("ELEVENLABS_VOICE_ID_DAWN", "21m00Tcm4TlvDq8ikWAM")  # Rachel voice as default

    for i, user_turn in enumerate(scenario["turns"]):
        # Show caller's line
        render_turn(scenario["caller"], user_turn, is_agent=False)
        transcript.append({"speaker": scenario["caller"], "text": user_turn})

        # Agent processes turn
        console.print("[dim]  thinking…[/dim]")
        reply, messages = agent.handle_turn(messages, user_turn)

        # Show agent reply
        render_turn("Dawn", reply, is_agent=True)
        transcript.append({"speaker": "Dawn", "text": reply})

        if use_audio and reply:
            audio_path = AUDIO_DIR / f"scenario_{scenario['id']}_turn_{i+1}_dawn.mp3"
            ok = _speak(reply, dawn_voice_id, audio_path)
            if ok:
                console.print(f"[dim]  🔊 Audio: {audio_path}[/dim]")

        # Small pause for readability
        if i < len(scenario["turns"]) - 1:
            time.sleep(0.3)

    return transcript


def save_transcript(scenario_id: int, transcript: list[dict]) -> None:
    out_path = Path(__file__).parent / f"transcript_scenario_{scenario_id}.json"
    out_path.write_text(json.dumps(transcript, indent=2), encoding="utf-8")
    console.print(f"[dim]Transcript saved: {out_path}[/dim]")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Run scripted receptionist demo")
    parser.add_argument("--scenario", type=int, default=None, help="Run only this scenario number (1-4)")
    parser.add_argument("--no-audio", action="store_true", help="Skip ElevenLabs TTS generation")
    args = parser.parse_args()

    use_audio = not args.no_audio and bool(os.getenv("ELEVENLABS_API_KEY"))

    console.rule("[bold blue]Keystone Plumbing — AI Voice Receptionist Demo[/bold blue]")
    console.print("[dim]Running scripted conversations through the live Claude agent…[/dim]")
    if use_audio:
        console.print("[dim]ElevenLabs TTS enabled — audio files will be saved to audio/[/dim]")

    scenarios_to_run = (
        [s for s in SCENARIOS if s["id"] == args.scenario]
        if args.scenario
        else SCENARIOS
    )

    for scenario in scenarios_to_run:
        transcript = run_scenario(scenario, use_audio=use_audio)
        save_transcript(scenario["id"], transcript)

    # Log summary
    console.print()
    console.rule("[bold green]Demo Complete[/bold green]")
    from pathlib import Path as P
    log_path = P(__file__).parent / "call_log.jsonl"
    if log_path.exists():
        entries = [json.loads(l) for l in log_path.read_text().splitlines() if l.strip()]
        bookings = [e for e in entries if e.get("event") == "appointment_booked"]
        escalations = [e for e in entries if e.get("event") == "emergency_escalation"]
        sms_sent = [e for e in entries if e.get("event") == "sms_sent"]
        console.print(f"  📅 Appointments booked:  [bold green]{len(bookings)}[/bold green]")
        console.print(f"  🚨 Emergencies escalated: [bold red]{len(escalations)}[/bold red]")
        console.print(f"  📱 SMS confirmations sent: [bold blue]{len(sms_sent)}[/bold blue]")
        console.print(f"  📋 Full call log: {log_path}")


if __name__ == "__main__":
    main()
