"""
Product 3 — Customer Re-Engagement Engine
==========================================
Segments the customer list into five re-engagement buckets,
generates personalized SMS + email outreach for each customer,
and computes projected recovered revenue.

Usage:
    python segment.py              # run all segments
    python segment.py --dry-run    # show segment sizes, no Claude calls
    python segment.py --limit 5    # generate drafts for 5 customers per segment

Output:
    products/03_reengagement/output/{segment_name}.csv
"""

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from shared import brand, claude_client, data_loader

console = Console()
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# ── Reactivation rate assumptions (conservative) ───────────────────────────────
REACTIVATION_RATES = {
    "water_heater_aging":    0.12,
    "sump_pump_seasonal":    0.15,
    "drain_cleaning_lapsed": 0.10,
    "maintenance_lapsed":    0.13,
    "high_ltv_dormant":      0.18,
}

# Average job revenue by segment (from dataset averages)
AVG_JOB_REVENUE = {
    "water_heater_aging":    1850.0,
    "sump_pump_seasonal":    875.0,
    "drain_cleaning_lapsed": 320.0,
    "maintenance_lapsed":    450.0,
    "high_ltv_dormant":      1400.0,
}


# ── Segmentation Logic ─────────────────────────────────────────────────────────

def _latest_job_per_customer() -> pd.DataFrame:
    """Return one row per customer: their most recent completed job + date."""
    j = data_loader.jobs()
    completed = j[j["Status"] == "Completed"].copy()
    latest = (
        completed.sort_values("Completed")
        .groupby("Customer ID")
        .last()
        .reset_index()[["Customer ID", "Customer Name", "Job Type", "Category", "Completed", "Revenue"]]
    )
    latest.rename(columns={"Completed": "Last Service Date", "Revenue": "Last Job Revenue"}, inplace=True)
    return latest


def _all_jobs_by_type(job_types: list[str]) -> pd.DataFrame:
    """Return all completed jobs of given types."""
    j = data_loader.jobs()
    return j[(j["Status"] == "Completed") & (j["Job Type"].isin(job_types))].copy()


def _merge_customer_info(df: pd.DataFrame) -> pd.DataFrame:
    """Merge phone/email from Customers sheet."""
    cust = data_loader.customers()[["Customer ID", "Name", "Phone", "Email"]]
    return df.merge(cust, on="Customer ID", how="left")


def as_of_date() -> date:
    return data_loader.latest_job_date().date()


def segment_water_heater_aging() -> pd.DataFrame:
    """Water heater installs aging (5+ years ideal; uses 12-month threshold against 2-year dataset)."""
    # The synthetic dataset spans only 2 years, so we use 12 months as a proxy for "aging."
    # In production against a full CRM history, this threshold would be 5 years.
    cutoff = as_of_date() - timedelta(days=365)
    wh_jobs = _all_jobs_by_type(["Water Heater Replacement"])
    wh_jobs = wh_jobs[wh_jobs["Completed"].dt.date <= cutoff].copy()
    if wh_jobs.empty:
        return pd.DataFrame(columns=["Customer ID", "Job Type", "Completed", "Months Since", "Segment", "Phone", "Email", "Name"])
    # Latest install per customer
    latest = (
        wh_jobs.sort_values("Completed")
        .groupby("Customer ID")
        .last()
        .reset_index()
    )
    latest["Segment"] = "water_heater_aging"
    latest["Months Since"] = ((as_of_date() - latest["Completed"].dt.date).apply(lambda x: x.days) / 30.44).round(1)
    return _merge_customer_info(latest[["Customer ID", "Job Type", "Completed", "Months Since", "Segment"]])


def segment_sump_pump_seasonal() -> pd.DataFrame:
    """Sump pump installs before last winter season (before Oct 1 of last year)."""
    last_winter_cutoff = date(as_of_date().year - 1, 10, 1)
    sp_jobs = _all_jobs_by_type(["Sump Pump Install"])
    sp_jobs = sp_jobs[sp_jobs["Completed"].dt.date <= last_winter_cutoff].copy()
    if sp_jobs.empty:
        return pd.DataFrame(columns=["Customer ID", "Job Type", "Completed", "Months Since", "Segment", "Phone", "Email", "Name"])
    latest = (
        sp_jobs.sort_values("Completed")
        .groupby("Customer ID")
        .last()
        .reset_index()
    )
    latest["Segment"] = "sump_pump_seasonal"
    latest["Months Since"] = ((as_of_date() - latest["Completed"].dt.date).apply(lambda x: x.days) / 30.44).round(1)
    return _merge_customer_info(latest[["Customer ID", "Job Type", "Completed", "Months Since", "Segment"]])


def segment_drain_cleaning_lapsed() -> pd.DataFrame:
    """Drain cleaning customers with no service in 18+ months."""
    cutoff = as_of_date() - timedelta(days=int(18 * 30.44))
    dc_jobs = _all_jobs_by_type(["Drain Cleaning", "Hydro Jetting"])
    dc_jobs = dc_jobs[dc_jobs["Completed"].dt.date <= cutoff].copy()
    if dc_jobs.empty:
        return pd.DataFrame(columns=["Customer ID", "Job Type", "Completed", "Months Since", "Segment", "Phone", "Email", "Name"])
    latest = (
        dc_jobs.sort_values("Completed")
        .groupby("Customer ID")
        .last()
        .reset_index()
    )
    latest["Segment"] = "drain_cleaning_lapsed"
    latest["Months Since"] = ((as_of_date() - latest["Completed"].dt.date).apply(lambda x: x.days) / 30.44).round(1)
    return _merge_customer_info(latest[["Customer ID", "Job Type", "Completed", "Months Since", "Segment"]])


def segment_maintenance_lapsed() -> pd.DataFrame:
    """Annual maintenance customers with no service in 13+ months."""
    cutoff = as_of_date() - timedelta(days=int(13 * 30.44))
    maint_jobs = _all_jobs_by_type(["HVAC Tune-Up", "Backflow Testing"])
    maint_jobs = maint_jobs[maint_jobs["Completed"].dt.date <= cutoff].copy()
    if maint_jobs.empty:
        return pd.DataFrame(columns=["Customer ID", "Job Type", "Completed", "Months Since", "Segment", "Phone", "Email", "Name"])
    latest = (
        maint_jobs.sort_values("Completed")
        .groupby("Customer ID")
        .last()
        .reset_index()
    )
    latest["Segment"] = "maintenance_lapsed"
    latest["Months Since"] = ((as_of_date() - latest["Completed"].dt.date).apply(lambda x: x.days) / 30.44).round(1)
    return _merge_customer_info(latest[["Customer ID", "Job Type", "Completed", "Months Since", "Segment"]])


def segment_high_ltv_dormant() -> pd.DataFrame:
    """High-LTV customers ($3k+ lifetime) with no job in 9+ months."""
    cutoff = as_of_date() - timedelta(days=int(9 * 30.44))
    j = data_loader.jobs()
    completed = j[j["Status"] == "Completed"].copy()

    # Customers with $3k+ lifetime revenue
    ltv = completed.groupby("Customer ID")["Revenue"].sum().reset_index()
    ltv = ltv[ltv["Revenue"] >= 3000]

    # Most recent job per customer
    latest_job = (
        completed.sort_values("Completed")
        .groupby("Customer ID")
        .last()
        .reset_index()[["Customer ID", "Customer Name", "Job Type", "Completed"]]
    )

    merged = ltv.merge(latest_job, on="Customer ID")
    dormant = merged[merged["Completed"].dt.date <= cutoff].copy()
    dormant["Segment"] = "high_ltv_dormant"
    dormant["Months Since"] = ((as_of_date() - dormant["Completed"].dt.date).apply(lambda x: x.days) / 30.44).round(1)
    return _merge_customer_info(dormant[["Customer ID", "Job Type", "Completed", "Months Since", "Segment"]])


# ── Message Generation ─────────────────────────────────────────────────────────

SEGMENT_CONTEXT = {
    "water_heater_aging": "Their water heater was installed {months_since:.0f} months ago ({install_date}). Water heaters typically last 8-12 years; theirs is aging and efficiency drops after year 7. This is a natural check-in — not a scare tactic.",
    "sump_pump_seasonal": "Their sump pump was installed {months_since:.0f} months ago ({install_date}), before last winter. Spring is the highest-risk flooding season in the Philadelphia area. This is a seasonal service reminder.",
    "drain_cleaning_lapsed": "Their last drain cleaning was {months_since:.0f} months ago ({install_date}). Annual drain cleaning prevents major backups. This is a routine annual reminder.",
    "maintenance_lapsed": "Their last maintenance visit was {months_since:.0f} months ago ({install_date}). Annual maintenance keeps their HVAC/plumbing under warranty. This is a friendly annual check-in.",
    "high_ltv_dormant": "This is a high-value customer (significant lifetime spend with Keystone) who hasn't been in for {months_since:.0f} months. Last service: {job_type} on {install_date}. This is a VIP check-in.",
}


def generate_outreach(row: dict, segment: str) -> dict:
    """Generate SMS and email for a single customer."""
    install_date = str(row.get("Completed", ""))[:10]
    months_since = float(row.get("Months Since", 0))
    job_type = str(row.get("Job Type", "plumbing service"))
    name = str(row.get("Name", "there"))
    first_name = name.split()[0] if name and name != "nan" else "there"

    context = SEGMENT_CONTEXT.get(segment, "").format(
        months_since=months_since,
        install_date=install_date,
        job_type=job_type,
    )

    user_message = f"""Generate two pieces of outreach for this Keystone Plumbing customer.

Customer first name: {first_name}
Segment: {segment}
Last service: {job_type} on {install_date} ({months_since:.0f} months ago)
Context: {context}

Return a JSON object with exactly these fields:
{{
  "sms": "SMS text (max 160 characters, sign as '- Keystone Plumbing')",
  "email_subject": "Email subject line (under 60 characters)",
  "email_body": "Email body (3-4 short paragraphs, end with booking link placeholder [BOOKING_LINK])"
}}

Return ONLY the JSON object, no other text."""

    response = claude_client.complete(
        system=brand.REENGAGEMENT_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
        max_tokens=600,
        temperature=0.7,
        label=f"outreach {segment} {first_name}",
    )

    try:
        # Strip any markdown code fences if present
        clean = response.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        return json.loads(clean)
    except json.JSONDecodeError:
        return {
            "sms": f"Hi {first_name}, it's Keystone Plumbing! Time for a check-in on your {job_type}. Book at [BOOKING_LINK] - Keystone Plumbing",
            "email_subject": f"A quick note about your {job_type}",
            "email_body": f"Hi {first_name},\n\nJust checking in about your {job_type} service from {install_date}.\n\nWhen you're ready to schedule, book at [BOOKING_LINK].\n\nMike Sullivan\nOwner, Keystone Plumbing & Drain",
        }


# ── Revenue Projection ─────────────────────────────────────────────────────────

def projected_revenue(segment: str, size: int) -> dict:
    rate = REACTIVATION_RATES.get(segment, 0.10)
    avg_rev = AVG_JOB_REVENUE.get(segment, 500)
    projected = round(size * rate * avg_rev, 0)
    return {
        "segment": segment,
        "size": size,
        "reactivation_rate_pct": round(rate * 100, 0),
        "avg_job_revenue": avg_rev,
        "projected_revenue": projected,
        "expected_customers": round(size * rate, 1),
    }


# ── Full Pipeline ──────────────────────────────────────────────────────────────

SEGMENTS = {
    "water_heater_aging":    segment_water_heater_aging,
    "sump_pump_seasonal":    segment_sump_pump_seasonal,
    "drain_cleaning_lapsed": segment_drain_cleaning_lapsed,
    "maintenance_lapsed":    segment_maintenance_lapsed,
    "high_ltv_dormant":      segment_high_ltv_dormant,
}


def run_all(limit: int | None = None, dry_run: bool = False) -> dict[str, pd.DataFrame]:
    results = {}

    for seg_name, seg_fn in SEGMENTS.items():
        console.rule(f"[bold blue]Segment: {seg_name}[/bold blue]")
        df = seg_fn()
        console.print(f"  {len(df)} customers in segment")

        if dry_run:
            results[seg_name] = df
            continue

        subset = df.head(limit) if limit else df

        sms_drafts = []
        email_subjects = []
        email_bodies = []

        with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console) as progress:
            task = progress.add_task(f"Generating outreach…", total=len(subset))
            for _, row in subset.iterrows():
                outreach = generate_outreach(row.to_dict(), seg_name)
                sms_drafts.append(outreach.get("sms", ""))
                email_subjects.append(outreach.get("email_subject", ""))
                email_bodies.append(outreach.get("email_body", ""))
                progress.advance(task)

        subset = subset.copy()
        subset["SMS Draft"] = sms_drafts
        subset["Email Subject"] = email_subjects
        subset["Email Body"] = email_bodies

        # Rename for output
        out = subset.rename(columns={
            "Completed": "Last Service",
            "Name": "Customer Name",
        })
        cols = ["Customer ID", "Customer Name", "Phone", "Email", "Last Service", "Months Since",
                "Job Type", "SMS Draft", "Email Subject", "Email Body"]
        out = out[[c for c in cols if c in out.columns]]

        csv_path = OUTPUT_DIR / f"{seg_name}.csv"
        out.to_csv(csv_path, index=False)
        console.print(f"  [green]✓ Saved to {csv_path}[/green]")

        results[seg_name] = out

    # Summary
    console.rule("[bold green]Revenue Projection Summary[/bold green]")
    table = Table(show_header=True, header_style="bold")
    table.add_column("Segment")
    table.add_column("Customers", justify="right")
    table.add_column("Reactivation Rate", justify="right")
    table.add_column("Avg Job $", justify="right")
    table.add_column("Projected Revenue", justify="right")

    total_projected = 0
    for seg_name, df in results.items():
        proj = projected_revenue(seg_name, len(df))
        total_projected += proj["projected_revenue"]
        table.add_row(
            seg_name,
            str(proj["size"]),
            f"{proj['reactivation_rate_pct']:.0f}%",
            f"${proj['avg_job_revenue']:,.0f}",
            f"${proj['projected_revenue']:,.0f}",
        )
    table.add_section()
    table.add_row("[bold]TOTAL[/bold]", "", "", "", f"[bold]${total_projected:,.0f}[/bold]")
    console.print(table)

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run customer re-engagement segmentation")
    parser.add_argument("--limit", type=int, default=None, help="Max customers per segment to generate outreach for")
    parser.add_argument("--dry-run", action="store_true", help="Show segment sizes only, no Claude calls")
    args = parser.parse_args()

    run_all(limit=args.limit, dry_run=args.dry_run)
