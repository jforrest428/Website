"""
Product 2 — Review Reply & Reputation Manager
==============================================
Drafts personalized Google/Yelp/Angi review replies for Keystone Plumbing.

Usage:
    python draft_replies.py                 # draft all unanswered reviews
    python draft_replies.py --limit 20      # draft at most N reviews
    python draft_replies.py --force         # re-draft even if cached

Output:
    products/02_review_reply/drafts.jsonl   (one JSON line per review)
"""

import argparse
import json
import sys
from pathlib import Path

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from shared import brand, claude_client, data_loader

console = Console()
DRAFTS_PATH = Path(__file__).parent / "drafts.jsonl"


def _load_existing_drafts() -> dict[str, dict]:
    """Load previously drafted replies keyed by Review ID."""
    if not DRAFTS_PATH.exists():
        return {}
    result = {}
    for line in DRAFTS_PATH.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rec = json.loads(line)
            result[rec["review_id"]] = rec
    return result


def _append_draft(draft: dict) -> None:
    with DRAFTS_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(draft) + "\n")


def draft_reply(review: dict) -> str:
    """Call Claude to draft a reply for a single review."""
    stars = review.get("Stars", 5)
    platform = review.get("Platform", "Google")
    text = review.get("Review Text", "")
    tech = review.get("Tech Mentioned")
    review_date = str(review.get("Date", ""))[:10]

    tech_line = f"\nTechnician mentioned: {tech}" if tech and str(tech) != "nan" else ""
    user_message = f"""Please draft a reply to this review posted on {platform}.

Stars: {stars}/5
Date: {review_date}{tech_line}
Review text:
\"{text}\"

Write the reply now."""

    return claude_client.complete(
        system=brand.REVIEW_REPLY_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
        max_tokens=300,
        temperature=0.3,
        label=f"review {review.get('Review ID')} ({stars}★ {platform})",
    )


def run(limit: int | None = None, force: bool = False) -> list[dict]:
    """
    Draft replies for all unanswered (or negative) reviews.

    Args:
        limit: Max number of reviews to process. None = all.
        force: If True, re-draft even if a draft already exists.

    Returns:
        List of draft dicts.
    """
    rev = data_loader.reviews()

    # Filter: unanswered OR 1-2 stars
    mask = (rev["Responded"] == "No") | (rev["Stars"] <= 2)
    targets = rev[mask].copy().sort_values("Date", ascending=False)

    if limit:
        targets = targets.head(limit)

    existing = _load_existing_drafts() if not force else {}
    results = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(f"Drafting replies for {len(targets)} reviews…", total=len(targets))

        for _, row in targets.iterrows():
            rid = str(row["Review ID"])
            progress.update(task, description=f"[cyan]Review {rid}[/cyan]")

            if rid in existing and not force:
                draft = existing[rid]
            else:
                reply_text = draft_reply(row.to_dict())
                draft = {
                    "review_id": rid,
                    "platform": row.get("Platform"),
                    "stars": int(row.get("Stars", 5)),
                    "review_date": str(row.get("Date"))[:10],
                    "review_text": str(row.get("Review Text")),
                    "tech_mentioned": str(row.get("Tech Mentioned")) if str(row.get("Tech Mentioned")) != "nan" else None,
                    "responded": str(row.get("Responded")),
                    "drafted_reply": reply_text,
                    "status": "pending",  # pending / approved / skipped
                }
                _append_draft(draft)
                existing[rid] = draft

            results.append(existing[rid])
            progress.advance(task)

    console.rule("[bold green]Draft Summary[/bold green]")
    table = Table(show_header=True, header_style="bold")
    table.add_column("Review ID", style="dim")
    table.add_column("Platform")
    table.add_column("Stars")
    table.add_column("Status")
    table.add_column("Reply Preview", max_width=50, no_wrap=True)
    for d in results[:20]:
        table.add_row(
            d["review_id"],
            d["platform"] or "",
            "★" * d["stars"],
            d["status"],
            (d["drafted_reply"] or "")[:50] + "…",
        )
    console.print(table)

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Draft review replies for Keystone Plumbing")
    parser.add_argument("--limit", type=int, default=None, help="Max reviews to process")
    parser.add_argument("--force", action="store_true", help="Re-draft even if cached")
    args = parser.parse_args()

    console.rule("[bold blue]Review Reply Manager[/bold blue]")
    drafts = run(limit=args.limit, force=args.force)
    console.print(f"\n[green]✓ {len(drafts)} drafts ready.[/green] Open the Streamlit UI to review them:")
    console.print("[dim]  streamlit run products/02_review_reply/app.py[/dim]")
