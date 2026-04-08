"""
Tests for Product 5 — Missed-Call SMS Responder.
Run with: python -m pytest products/05_missed_call_sms/ -v
No API key required — all Claude calls are mocked.
"""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ROOT    = Path(__file__).parent.parent.parent
PRODUCT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(PRODUCT))

from sms_composer import (
    FALLBACK_TEMPLATES,
    _is_after_hours,
    compose_sms,
)


# ── Time parsing ───────────────────────────────────────────────────────────────

class TestAfterHours:
    def test_midnight_is_after_hours(self):
        assert _is_after_hours("12:00 AM") is True

    def test_11pm_is_after_hours(self):
        assert _is_after_hours("11:47 PM") is True

    def test_2pm_is_business_hours(self):
        assert _is_after_hours("2:14 PM") is False

    def test_9am_is_business_hours(self):
        assert _is_after_hours("9:05 AM") is False

    def test_6pm_is_after_hours(self):
        # 6 PM = hour 18 = boundary, treated as after-hours
        assert _is_after_hours("6:00 PM") is True

    def test_invalid_time_defaults_to_business_hours(self):
        # Unknown format → returns False (safe default)
        assert _is_after_hours("unknown") is False


# ── SMS composition ────────────────────────────────────────────────────────────

class TestComposeSms:
    def test_claude_path_returns_under_160_chars(self):
        mock_sms = "Hi, this is Keystone Plumbing — sorry we missed your call at 11:47 PM. Reply here to book. — Mike"
        assert len(mock_sms) <= 160

        with patch("sms_composer.claude_client.complete",
                   return_value=mock_sms):
            result = compose_sms(
                caller_number="+12155550011",
                time_called="11:47 PM",
                business_name="Keystone Plumbing & Drain",
                owner_name="Mike Sullivan",
            )
        assert result["chars"] <= 160
        assert result["source"] == "claude"

    def test_long_claude_response_is_truncated(self):
        # Claude goes over 160 chars — should be truncated
        long_sms = "A" * 200
        with patch("sms_composer.claude_client.complete",
                   return_value=long_sms):
            result = compose_sms(
                caller_number="+12155550011",
                time_called="2:00 PM",
                business_name="Keystone Plumbing & Drain",
                owner_name="Mike Sullivan",
            )
        assert result["chars"] <= 160

    def test_fallback_on_claude_failure(self):
        with patch("sms_composer.claude_client.complete",
                   side_effect=Exception("API error")):
            result = compose_sms(
                caller_number="+12155550011",
                time_called="11:47 PM",
                business_name="Keystone Plumbing & Drain",
                owner_name="Mike Sullivan",
            )
        assert result["source"] == "fallback"
        assert "Keystone Plumbing" in result["sms"]

    def test_fallback_after_hours_template(self):
        with patch("sms_composer.claude_client.complete",
                   side_effect=Exception("API error")):
            result = compose_sms(
                caller_number="+12155550011",
                time_called="11:47 PM",
                business_name="Keystone Plumbing & Drain",
                owner_name="Mike Sullivan",
            )
        assert "morning" in result["sms"].lower()

    def test_fallback_business_hours_template(self):
        with patch("sms_composer.claude_client.complete",
                   side_effect=Exception("API error")):
            result = compose_sms(
                caller_number="+12155550011",
                time_called="2:00 PM",
                business_name="Keystone Plumbing & Drain",
                owner_name="Mike Sullivan",
            )
        assert "call back" in result["sms"].lower() or "call you back" in result["sms"].lower()

    def test_known_caller_context_passed_to_claude(self):
        captured = {}
        def fake_complete(system, messages, **kwargs):
            captured["content"] = messages[0]["content"]
            return "Hi Patricia, sorry we missed your call."

        with patch("sms_composer.claude_client.complete",
                   side_effect=fake_complete):
            compose_sms(
                caller_number="+12155550022",
                time_called="2:14 PM",
                business_name="Keystone Plumbing & Drain",
                owner_name="Mike Sullivan",
                caller_name="Patricia Walsh",
                last_service="Water heater replacement, January 2026",
            )
        assert "Patricia Walsh" in captured["content"]
        assert "Water heater" in captured["content"]
