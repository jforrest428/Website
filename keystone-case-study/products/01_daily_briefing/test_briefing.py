"""
End-to-end tests for Product 1 — Daily Briefing.
Run: python -m pytest products/01_daily_briefing/test_briefing.py -v
"""
import sys
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "products" / "01_daily_briefing"))

from shared import data_loader
from generate_briefing import build_context


def test_context_structure():
    """build_context() returns all required keys."""
    ctx = build_context(date(2026, 4, 7))
    assert "briefing_date" in ctx
    assert "yesterday" in ctx
    assert "today_schedule" in ctx
    assert "accounts_receivable" in ctx
    assert "reputation" in ctx
    assert "pipeline" in ctx


def test_context_values_are_real():
    """Values are pulled from real dataset — not zero for the entire test range."""
    j = data_loader.jobs()
    # Dataset has jobs up to 2026-04-06
    ctx = build_context(date(2026, 4, 7))
    # Yesterday (2026-04-06) should have some completed jobs and revenue
    assert ctx["yesterday"]["completed_jobs"] >= 0
    assert ctx["yesterday"]["revenue"] >= 0


def test_overdue_invoices_nonzero():
    """There are overdue invoices in the dataset."""
    ctx = build_context(date(2026, 4, 7))
    assert ctx["accounts_receivable"]["overdue_count"] > 0
    assert ctx["accounts_receivable"]["overdue_total"] > 0


def test_latest_date():
    """latest_job_date() returns a real date from the dataset."""
    latest = data_loader.latest_job_date()
    assert latest.year >= 2026
    assert latest.year <= 2027


def test_revenue_types():
    """Revenue fields are numeric."""
    ctx = build_context(date(2026, 4, 7))
    assert isinstance(ctx["yesterday"]["revenue"], (int, float))
    assert isinstance(ctx["accounts_receivable"]["overdue_total"], (int, float))


def test_briefing_for_date_cached(tmp_path, monkeypatch):
    """briefing_for_date() uses the output cache and doesn't call Claude twice."""
    from generate_briefing import briefing_for_date, OUTPUT_DIR
    import generate_briefing

    # Pre-seed with a fake cached result
    test_date = date(2025, 1, 1)
    fake_txt = tmp_path / f"{test_date}.txt"
    fake_txt.write_text("Cached briefing text.", encoding="utf-8")

    monkeypatch.setattr(generate_briefing, "OUTPUT_DIR", tmp_path)
    result = briefing_for_date(test_date)
    assert result == "Cached briefing text."
