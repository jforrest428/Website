"""
Tests for Product 3 — Re-Engagement Engine.
Run: python -m pytest products/03_reengagement/test_reengagement.py -v
"""
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "products" / "03_reengagement"))

from segment import (
    segment_water_heater_aging,
    segment_sump_pump_seasonal,
    segment_drain_cleaning_lapsed,
    segment_maintenance_lapsed,
    segment_high_ltv_dormant,
    projected_revenue,
)


def test_water_heater_segment_nonempty():
    df = segment_water_heater_aging()
    assert len(df) > 0


def test_sump_pump_segment_nonempty():
    df = segment_sump_pump_seasonal()
    assert len(df) > 0


def test_drain_cleaning_segment_nonempty():
    df = segment_drain_cleaning_lapsed()
    assert len(df) > 0


def test_all_segments_have_required_columns():
    required = {"Customer ID", "Months Since", "Segment"}
    for seg_fn in [
        segment_water_heater_aging,
        segment_sump_pump_seasonal,
        segment_drain_cleaning_lapsed,
        segment_maintenance_lapsed,
        segment_high_ltv_dormant,
    ]:
        df = seg_fn()
        if len(df) > 0:
            for col in required:
                assert col in df.columns, f"Missing column {col} in {seg_fn.__name__}"


def test_months_since_positive():
    """All 'Months Since' values should be positive."""
    df = segment_water_heater_aging()
    assert (df["Months Since"] > 0).all()


def test_projected_revenue_calculation():
    proj = projected_revenue("water_heater_aging", 50)
    assert proj["projected_revenue"] > 0
    assert proj["size"] == 50
    assert 0 < proj["reactivation_rate_pct"] <= 100
    # 50 customers × 12% × $1850 = $11,100
    assert proj["projected_revenue"] == pytest.approx(11100, rel=0.01)


def test_projected_revenue_all_segments():
    """Total projected revenue across all segments should be meaningful."""
    from segment import SEGMENTS
    total = sum(
        projected_revenue(name, len(SEGMENTS[name]()))["projected_revenue"]
        for name in SEGMENTS
    )
    assert total > 10000, f"Total projected revenue too low: ${total:,.0f}"
