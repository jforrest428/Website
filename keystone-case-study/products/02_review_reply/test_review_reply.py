"""
Tests for Product 2 — Review Reply Manager.
Run: python -m pytest products/02_review_reply/test_review_reply.py -v
"""
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "products" / "02_review_reply"))

from shared import data_loader
from patterns import negative_by_tech, flagged_techs, response_rate_by_platform


def test_reviews_loaded():
    rev = data_loader.reviews()
    assert len(rev) == 420


def test_negative_reviews_exist():
    rev = data_loader.reviews()
    neg = rev[rev["Stars"] <= 2]
    assert len(neg) > 0


def test_negative_by_tech_returns_list():
    result = negative_by_tech(window_days=365)
    assert isinstance(result, list)
    if result:
        assert "tech_name" in result[0]
        assert "count" in result[0]
        assert "reviews" in result[0]


def test_david_chen_flagged():
    """David Chen should have 3+ negative mentions in the full dataset window."""
    result = negative_by_tech(window_days=730)  # full 2-year window
    names = {r["tech_name"]: r["count"] for r in result}
    assert "David Chen" in names, "David Chen not found in negative mentions"
    assert names["David Chen"] >= 3, f"Expected 3+ mentions, got {names['David Chen']}"


def test_flagged_techs_minimum():
    flagged = flagged_techs(min_mentions=2, window_days=730)
    assert any(t["tech_name"] == "David Chen" for t in flagged)


def test_response_rate_by_platform():
    rates = response_rate_by_platform()
    assert len(rates) > 0
    for platform, stats in rates.items():
        assert "total" in stats
        assert "rate_pct" in stats
        assert 0 <= stats["rate_pct"] <= 100


def test_unresponded_reviews_exist():
    rev = data_loader.reviews()
    unresponded = rev[rev["Responded"] == "No"]
    assert len(unresponded) > 0
