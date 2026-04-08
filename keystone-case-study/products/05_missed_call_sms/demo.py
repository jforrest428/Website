"""
Product 5 — Missed-Call SMS Responder: Scripted Demo
=====================================================
Five scenarios showing the full missed-call → SMS flow.
No live Twilio required — demonstrates Claude's output directly.

Usage:
    python products/05_missed_call_sms/demo.py
    python products/05_missed_call_sms/demo.py --scenario 1
"""

import argparse
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

ROOT    = Path(__file__).parent.parent.parent
PRODUCT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(PRODUCT))

from shared import brand
from sms_composer import compose_sms

console = Console()

SCENARIOS = [
    {
        "id": 1,
        "label": "After-hours burst pipe — unknown caller",
        "caller_number": "+12155550011",
        "caller_name": None,
        "time_called": "11:47 PM",
        "last_service": None,
        "context": "Emergency call, 11 PM, new customer — no CRM match.",
    },
    {
        "id": 2,
        "label": "Midday call — known customer, recent job",
        "caller_number": "+12155550022",
        "caller_name": "Patricia Walsh",
        "time_called": "2:14 PM",
        "last_service": "Water heater replacement, January 2026",
        "context": "Business hours, returning customer with recent service history.",
    },
    {
        "id": 3,
        "label": "Saturday morning — unknown caller, drain issue likely",
        "caller_number": "+12155550033",
        "caller_name": None,
        "time_called": "9:05 AM",
        "last_service": None,
        "context": "Weekend morning, tech on another job, caller not in CRM.",
    },
    {
        "id": 4,
        "label": "Evening call — high-value dormant customer",
        "caller_number": "+12155550044",
        "caller_name": "James Whitfield",
        "time_called": "6:48 PM",
        "last_service": "Sump pump installation, June 2025 ($4,200 lifetime spend)",
        "context": "After hours, known high-value customer returning after 10-month gap.",
    },
    {
        "id": 5,
        "label": "Busy signal — commercial account",
        "caller_number": "+12155550055",
        "caller_name": "Riverside Properties (Facility Manager)",
        "time_called": "10:22 AM",
        "last_service": "Commercial PM, November 2025",
        "context": "Business hours, commercial client, all lines busy.",
    },
]


def run_scenario(s: dict) -> None:
    console.rule(f"[bold gold1]Scenario {s['id']}: {s['label']}[/bold gold1]")
    console.print(f"[dim]Context: {s['context']}[/dim]\n")

    # Input table
    t = Table(show_header=False, box=None, padding=(0, 1))
    t.add_column(style="dim")
    t.add_column()
    t.add_row("Caller number",  s["caller_number"])
    t.add_row("Caller name",    s["caller_name"] or "[dim]unknown[/dim]")
    t.add_row("Time of call",   s["time_called"])
    t.add_row("Last service",   s["last_service"] or "[dim]none on file[/dim]")
    console.print(t)
    console.print()

    with console.status("[gold1]Composing SMS via Claude...[/gold1]"):
        result = compose_sms(
            caller_number=s["caller_number"],
            time_called=s["time_called"],
            business_name=brand.COMPANY_NAME,
            owner_name=brand.OWNER_NAME,
            business_type="plumbing",
            caller_name=s["caller_name"],
            last_service=s["last_service"],
        )

    char_color = "green" if result["chars"] <= 160 else "red"
    source_tag = "[green]Claude[/green]" if result["source"] == "claude" else "[yellow]Fallback[/yellow]"

    console.print(Panel(
        result["sms"],
        title=f"[bold]SMS Reply[/bold]  [{char_color}]{result['chars']}/160 chars[/{char_color}]  {source_tag}",
        border_style="gold1",
        padding=(1, 2),
    ))
    console.print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Missed-Call SMS demo")
    parser.add_argument("--scenario", type=int, choices=[s["id"] for s in SCENARIOS],
                        help="Run a single scenario (1–5)")
    args = parser.parse_args()

    console.print(Panel(
        f"[bold]{brand.COMPANY_NAME}[/bold]\nMissed-Call SMS Responder — Demo\n"
        f"[dim]Built by Forrest Analytics Group LLC[/dim]",
        border_style="gold1",
        expand=False,
    ))
    console.print()

    targets = [s for s in SCENARIOS if args.scenario is None or s["id"] == args.scenario]
    for s in targets:
        run_scenario(s)

    console.print("[bold green]Demo complete.[/bold green]")


if __name__ == "__main__":
    main()
