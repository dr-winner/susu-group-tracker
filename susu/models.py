"""Small immutable data objects returned by the Group.

They are frozen dataclasses so results cannot be changed by accident
after the Group has handed them out.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Payout:
    """The pot paid to one member for one week. Amount is in pesewas."""

    week: int
    member: str
    amount: int


@dataclass(frozen=True)
class CloseResult:
    """Outcome of trying to close a week.

    closed=True  -> payout is set and owing is empty.
    closed=False -> nothing was paid; owing lists (member, pesewas) still due.
    """

    closed: bool
    payout: Payout | None
    owing: tuple[tuple[str, int], ...]


@dataclass(frozen=True)
class Report:
    """A snapshot of the group for display. All money is in pesewas."""

    weekly_amount: int
    pot: int
    current_week: int
    total_weeks: int
    complete: bool
    next_recipient: str | None
    paid_in_full: tuple[str, ...]
    owing: tuple[tuple[str, int], ...]
    payouts: tuple[Payout, ...]
