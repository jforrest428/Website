"""
Product 1 — Owner's Daily Briefing
===================================
Generates a 6am SMS-style business briefing for the Keystone Plumbing owner.

Usage:
    python generate_briefing.py                     # uses most recent date in dataset
    python generate_briefing.py --date 2026-04-07   # specific date

Output:
    products/01_daily_briefing/output/{date}.json   (raw context)
    products/01_daily_briefing/output/{date}.txt    (final SMS text)
"""

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

# Allow imports from project root
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared import brand, claude_client, data_loader

console = Console()
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


# ── Data Extraction ────────────────────────────────────────────────────────────

def _jobs_for_date(target_date: date, status: str | None = None) -> list[dict]:
    """Return jobs scheduled on target_date, optionally filtered by status."""
    j = data_loader.jobs()
    mask = j["Scheduled"].dt.date == target_date
    if status:
        mask &= j["Status"] == status
    subset = j[mask].copy()
    return subset.to_dict("records")


def _revenue_for_date(target_date: date) -> float:
    """Total revenue from completed jobs on target_date."""
    j = data_loader.jobs()
    mask = (j["Completed"].dt.date == target_date) & (j["Status"] == "Completed")
    return float(j[mask]["Revenue"].sum())


def _revenue_same_day_last_year(target_date: date) -> float:
    last_year = target_date.replace(year=target_date.year - 1)
    return _revenue_for_date(last_year)


def _overdue_invoices(as_of: date, days_threshold: int = 14) -> list[dict]:
    """Invoices unpaid for more than days_threshold days as of as_of."""
    inv = data_loader.invoices()
    unpaid = inv[inv["Paid"] != "Yes"].copy()
    unpaid["age_days"] = (
        (as_of - unpaid["Invoice Date"].dt.date).apply(lambda x: x.days if hasattr(x, "days") else 0)
    )
    overdue = unpaid[unpaid["age_days"] > days_threshold]
    return overdue[["Invoice ID", "Customer Name", "Total", "age_days"]].to_dict("records")


def _negative_unresponded_reviews(as_of: date, window_days: int = 7) -> list[dict]:
    """1-2 star reviews in the last window_days that haven't been responded to."""
    rev = data_loader.reviews()
    cutoff = as_of - timedelta(days=window_days)
    mask = (
        (rev["Stars"] <= 2)
        & (rev["Date"].dt.date >= cutoff)
        & (rev["Responded"] == "No")
    )
    subset = rev[mask][["Review ID", "Platform", "Stars", "Review Text", "Tech Mentioned"]].copy()
    return subset.to_dict("records")


def _big_pipeline_jobs(as_of: date, min_revenue: float = 5000) -> list[dict]:
    """Scheduled-but-not-completed jobs with Revenue > min_revenue."""
    j = data_loader.jobs()
    mask = (
        (j["Status"] == "Scheduled")
        & (j["Revenue"] >= min_revenue)
        & (j["Scheduled"].dt.date >= as_of)
    )
    subset = j[mask][["Job ID", "Customer Name", "Job Type", "Revenue", "Scheduled", "Tech Name"]].head(5)
    return subset.to_dict("records")


# ── Context Builder ────────────────────────────────────────────────────────────

def build_context(for_date: date) -> dict:
    """Assemble the structured JSON context for a given date."""
    yesterday = for_date - timedelta(days=1)

    yesterday_jobs = _jobs_for_date(yesterday, status="Completed")
    yesterday_revenue = _revenue_for_date(yesterday)
    last_year_revenue = _revenue_same_day_last_year(yesterday)
    yoy_pct = (
        ((yesterday_revenue - last_year_revenue) / last_year_revenue * 100)
        if last_year_revenue > 0
        else None
    )

    todays_schedule = _jobs_for_date(for_date)
    overdue = _overdue_invoices(for_date)
    negative_reviews = _negative_unresponded_reviews(for_date)
    big_jobs = _big_pipeline_jobs(for_date)

    # Summarize today's schedule by tech
    tech_schedule: dict[str, list] = {}
    for job in todays_schedule:
        tech = str(job.get("Tech Name", "Unassigned"))
        tech_schedule.setdefault(tech, []).append(
            {"job_type": job.get("Job Type"), "city": job.get("City"), "priority": job.get("Priority")}
        )

    return {
        "briefing_date": str(for_date),
        "yesterday": {
            "date": str(yesterday),
            "completed_jobs": len(yesterday_jobs),
            "revenue": round(yesterday_revenue, 2),
            "vs_last_year_revenue": round(last_year_revenue, 2),
            "yoy_change_pct": round(yoy_pct, 1) if yoy_pct is not None else None,
            "top_jobs": [
                {"job_type": j.get("Job Type"), "revenue": j.get("Revenue"), "tech": j.get("Tech Name")}
                for j in sorted(yesterday_jobs, key=lambda x: x.get("Revenue", 0), reverse=True)[:3]
            ],
        },
        "today_schedule": {
            "total_jobs": len(todays_schedule),
            "by_tech": tech_schedule,
            "emergency_count": sum(1 for j in todays_schedule if j.get("Priority") == "Emergency"),
        },
        "accounts_receivable": {
            "overdue_count": len(overdue),
            "overdue_total": round(sum(r["Total"] for r in overdue), 2),
            "oldest_days": max((r["age_days"] for r in overdue), default=0),
            "top_overdue": overdue[:3],
        },
        "reputation": {
            "negative_unresponded": len(negative_reviews),
            "reviews": [
                {
                    "platform": r["Platform"],
                    "stars": r["Stars"],
                    "snippet": str(r["Review Text"])[:100],
                    "tech": r.get("Tech Mentioned"),
                }
                for r in negative_reviews
            ],
        },
        "pipeline": {
            "big_opportunities": len(big_jobs),
            "jobs": [
                {
                    "customer": j["Customer Name"],
                    "type": j["Job Type"],
                    "revenue": j["Revenue"],
                    "date": str(j["Scheduled"]),
                    "tech": j["Tech Name"],
                }
                for j in big_jobs
            ],
        },
    }


# ── Claude Generation ──────────────────────────────────────────────────────────

def generate_sms(context: dict) -> str:
    """Call Claude to turn the context into an SMS briefing."""
    user_message = f"""Here is today's business context for {brand.OWNER_NAME} at {brand.COMPANY_NAME}:

{json.dumps(context, indent=2, default=str)}

Write the daily briefing text message now. Remember: max 180 words, SMS format, plain text only."""

    return claude_client.complete(
        system=brand.BRIEFING_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
        max_tokens=400,
        temperature=0.3,
        label=f"daily briefing {context['briefing_date']}",
    )


# ── Public API ─────────────────────────────────────────────────────────────────

def briefing_for_date(for_date: date | str) -> str:
    """
    Generate (or load from cache) the SMS briefing for a given date.

    Args:
        for_date: date object or ISO string like "2026-04-07"

    Returns:
        SMS text string.
    """
    if isinstance(for_date, str):
        from datetime import date as date_cls
        for_date = date_cls.fromisoformat(for_date)

    # Check output cache first
    txt_path = OUTPUT_DIR / f"{for_date}.txt"
    if txt_path.exists():
        return txt_path.read_text(encoding="utf-8").strip()

    context = build_context(for_date)
    sms = generate_sms(context)

    # Persist
    json_path = OUTPUT_DIR / f"{for_date}.json"
    json_path.write_text(json.dumps(context, indent=2, default=str), encoding="utf-8")
    txt_path.write_text(sms, encoding="utf-8")

    return sms


# ── CLI ────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate Owner's Daily Briefing")
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="Date to generate briefing for (YYYY-MM-DD). Defaults to most recent date in dataset.",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Bypass output cache and regenerate even if output already exists.",
    )
    args = parser.parse_args()

    if args.date:
        from datetime import date as date_cls
        target = date_cls.fromisoformat(args.date)
    else:
        target = data_loader.latest_job_date().date()

    console.rule(f"[bold blue]Keystone Daily Briefing — {target}[/bold blue]")

    if args.no_cache:
        # Remove cached outputs so briefing_for_date regenerates
        for ext in (".json", ".txt"):
            p = OUTPUT_DIR / f"{target}{ext}"
            if p.exists():
                p.unlink()

    console.print(f"[dim]Building context for {target}...[/dim]")
    context = build_context(target)

    console.print(Panel(
        json.dumps(context, indent=2, default=str),
        title="[bold]Raw Context (JSON)[/bold]",
        border_style="dim",
        expand=False,
    ))

    console.print("[dim]Calling Claude...[/dim]")
    sms = generate_sms(context)

    # Save outputs
    json_path = OUTPUT_DIR / f"{target}.json"
    txt_path = OUTPUT_DIR / f"{target}.txt"
    json_path.write_text(json.dumps(context, indent=2, default=str), encoding="utf-8")
    txt_path.write_text(sms, encoding="utf-8")

    console.print()
    console.print(Panel(
        sms,
        title=f"[bold green]SMS Briefing — {target}[/bold green]",
        border_style="green",
        subtitle=f"{len(sms.split())} words",
    ))
    console.print(f"\n[dim]Saved to:[/dim] {txt_path}")
    console.print(f"[dim]Context: [/dim] {json_path}")


if __name__ == "__main__":
    main()
