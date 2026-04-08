"""
Tests for Product 4 — Voice Receptionist.
Tests the tool implementations (no Claude API calls needed).
Run: python -m pytest products/04_voice_receptionist/test_receptionist.py -v
"""
import sys
import json
from pathlib import Path
import pytest

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "products" / "04_voice_receptionist"))

from agent import _find_available_slots, ReceptionistToolHandler


def test_find_slots_returns_three():
    slots = _find_available_slots("Drain Cleaning", "this-week")
    assert len(slots) == 3


def test_slots_have_required_fields():
    slots = _find_available_slots("Water Heater Repair", "next-day")
    for s in slots:
        assert "slot_id" in s
        assert "date" in s
        assert "time" in s
        assert "tech_name" in s
        assert "display" in s


def test_slots_different_dates_or_times():
    """Returned slots shouldn't all be identical."""
    slots = _find_available_slots("Drain Cleaning", "this-week")
    slot_ids = [s["slot_id"] for s in slots]
    assert len(set(slot_ids)) > 1, "All slots returned the same slot ID"


def test_tool_handler_get_slots(tmp_path, monkeypatch):
    import agent
    monkeypatch.setattr(agent, "CALL_LOG_PATH", tmp_path / "call_log.jsonl")

    handler = ReceptionistToolHandler()
    result = handler.handle("get_available_slots", {"job_type": "Drain Cleaning", "urgency": "this-week"})
    assert "slots" in result
    assert len(result["slots"]) > 0


def test_tool_handler_book_appointment(tmp_path, monkeypatch):
    import agent
    monkeypatch.setattr(agent, "CALL_LOG_PATH", tmp_path / "call_log.jsonl")

    handler = ReceptionistToolHandler()
    result = handler.handle("book_appointment", {
        "customer_name": "Test Customer",
        "customer_phone": "215-555-0001",
        "service_address": "123 Test St, Wayne PA",
        "job_type": "Drain Cleaning",
        "slot": "any",
        "issue_description": "Slow drain",
    })
    assert "confirmation_number" in result
    assert result["confirmation_number"].startswith("KP-")
    assert result["status"] == "confirmed"


def test_tool_handler_escalate(tmp_path, monkeypatch):
    import agent
    monkeypatch.setattr(agent, "CALL_LOG_PATH", tmp_path / "call_log.jsonl")

    handler = ReceptionistToolHandler()
    result = handler.handle("escalate_to_oncall", {
        "emergency_type": "Burst pipe",
        "caller_phone": "215-555-9999",
        "caller_name": "Test Caller",
        "service_address": "456 Emergency Ave",
    })
    assert result["escalated"] is True
    assert "on_call_tech" in result
    assert result["eta_minutes"] > 0


def test_call_log_written(tmp_path, monkeypatch):
    import agent
    log_path = tmp_path / "call_log.jsonl"
    monkeypatch.setattr(agent, "CALL_LOG_PATH", log_path)

    handler = ReceptionistToolHandler()
    handler.handle("get_available_slots", {"job_type": "Test", "urgency": "this-week"})
    handler.handle("escalate_to_oncall", {"emergency_type": "Test emergency", "caller_phone": "000"})

    assert log_path.exists()
    lines = [l for l in log_path.read_text().splitlines() if l.strip()]
    assert len(lines) >= 2
    events = [json.loads(l)["event"] for l in lines]
    assert "slots_queried" in events
    assert "emergency_escalation" in events
