"""Turns a Report into readable text. Formatting only, no rules."""
from __future__ import annotations

from .models import Report
from .money import format_amount


def format_report(report: Report) -> str:
    lines = [
        "=== Susu Group Report ===",
        f"Weekly contribution: GHS {format_amount(report.weekly_amount)}"
        f"  |  Members: {report.total_weeks}"
        f"  |  Pot: GHS {format_amount(report.pot)}",
    ]
    if report.complete:
        lines.append(f"Cycle complete: all {report.total_weeks} weeks have been paid out.")
    else:
        lines.append(f"Current week: {report.current_week} of {report.total_weeks}")
        if report.next_recipient:
            lines.append(f"Next to receive the pot: {report.next_recipient}")
        lines.append("")
        lines.append("Paid in full:")
        lines.extend([f"  - {name}" for name in report.paid_in_full] or ["  (nobody yet)"])
        lines.append("Still owing:")
        lines.extend(
            [f"  - {name} owes GHS {format_amount(owed)}" for name, owed in report.owing]
            or ["  (nobody)"]
        )
    lines.append("")
    lines.append("Payout history:")
    lines.extend(
        [
            f"  Week {p.week}: {p.member} received GHS {format_amount(p.amount)}"
            for p in report.payouts
        ]
        or ["  (no payouts yet)"]
    )
    return "\n".join(lines)
