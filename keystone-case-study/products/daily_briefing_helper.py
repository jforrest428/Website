"""Helper used by the Daily Briefing Streamlit viewer to load/generate briefings."""
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

OUTPUT_DIR = ROOT / "products" / "01_daily_briefing" / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def get_briefings_for_range(start: date, end: date) -> dict[str, str]:
    """
    Return a dict of {date_str: sms_text} for each date in [start, end].
    Generates any missing briefings on demand.
    """
    result = {}
    current = start
    while current <= end:
        txt = _load_or_generate(current)
        if txt:
            result[str(current)] = txt
        current += timedelta(days=1)
    return result


def _load_or_generate(for_date: date) -> str | None:
    txt_path = OUTPUT_DIR / f"{for_date}.txt"
    if txt_path.exists():
        return txt_path.read_text(encoding="utf-8").strip()
    try:
        # Import lazily so Streamlit app can start before Claude is called
        import importlib.util, os
        spec = importlib.util.spec_from_file_location(
            "generate_briefing",
            ROOT / "products" / "01_daily_briefing" / "generate_briefing.py",
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.briefing_for_date(for_date)
    except Exception as e:
        return f"[Error generating briefing: {e}]"
