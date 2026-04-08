"""
Pattern Analyzer — surfaces tech-level patterns from negative reviews.
Used by both the CLI and the Streamlit app.
"""

import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from shared import data_loader


def negative_by_tech(window_days: int = 90) -> list[dict]:
    """
    Return a list of techs with negative review mentions in the last window_days,
    sorted by mention count descending.

    Returns:
        List of dicts: {tech_name, count, reviews: [...]}
    """
    rev = data_loader.reviews()
    cutoff = rev["Date"].max() - timedelta(days=window_days)

    neg = rev[
        (rev["Stars"] <= 2)
        & (rev["Date"] >= cutoff)
        & rev["Tech Mentioned"].notna()
        & (rev["Tech Mentioned"].astype(str) != "nan")
    ].copy()

    if neg.empty:
        return []

    grouped = (
        neg.groupby("Tech Mentioned")
        .apply(
            lambda g: {
                "tech_name": g.name,
                "count": len(g),
                "reviews": g[["Review ID", "Date", "Platform", "Stars", "Review Text"]]
                .assign(Date=g["Date"].dt.strftime("%Y-%m-%d"))
                .to_dict("records"),
            },
            include_groups=False,
        )
        .tolist()
    )

    return sorted(grouped, key=lambda x: x["count"], reverse=True)


def flagged_techs(min_mentions: int = 2, window_days: int = 90) -> list[dict]:
    """Return only techs with >= min_mentions negative reviews."""
    return [t for t in negative_by_tech(window_days) if t["count"] >= min_mentions]


def review_velocity(window_days: int = 30) -> dict:
    """Return review counts by star rating for the last window_days."""
    rev = data_loader.reviews()
    cutoff = rev["Date"].max() - timedelta(days=window_days)
    recent = rev[rev["Date"] >= cutoff]
    return recent["Stars"].value_counts().sort_index(ascending=False).to_dict()


def response_rate_by_platform() -> dict:
    """Return response rates grouped by platform."""
    rev = data_loader.reviews()
    result = {}
    for platform, group in rev.groupby("Platform"):
        total = len(group)
        responded = (group["Responded"] == "Yes").sum()
        result[platform] = {
            "total": total,
            "responded": int(responded),
            "rate_pct": round(100 * responded / total, 1) if total > 0 else 0,
        }
    return result


if __name__ == "__main__":
    from rich.console import Console
    from rich.table import Table

    console = Console()
    console.rule("[bold blue]Review Pattern Analysis[/bold blue]")

    flagged = flagged_techs(min_mentions=2)
    if flagged:
        table = Table(title="⚠ Techs with 2+ Negative Reviews (last 90 days)", show_header=True)
        table.add_column("Tech Name", style="bold red")
        table.add_column("Negative Mentions")
        table.add_column("Most Recent Review")
        for t in flagged:
            latest = sorted(t["reviews"], key=lambda r: r["Date"], reverse=True)[0]
            table.add_row(
                t["tech_name"],
                str(t["count"]),
                f"{latest['Stars']}★ — {latest['Review Text'][:60]}…",
            )
        console.print(table)
    else:
        console.print("[green]No techs with 2+ negative mentions in the last 90 days.[/green]")

    console.print()
    console.print("[bold]Response rate by platform:[/bold]")
    for platform, stats in response_rate_by_platform().items():
        bar = "█" * int(stats["rate_pct"] / 5)
        console.print(f"  {platform:<12} {bar} {stats['rate_pct']}%  ({stats['responded']}/{stats['total']})")
