"""Core logic for one rotating savings group (susu).

The rules in one place:
* Every member pays the same fixed weekly amount.
* Each week the whole pot goes to ONE member, in the order they joined.
* A week closes only when every member has paid in full.
* Payments are accepted for the current week only (no paying ahead or behind).
* Members can only be added before the first payment is recorded.

All money is integer pesewas (1 GHS = 100 pesewas), so there are no
rounding errors. This module never prints or reads input: the CLI does that.
"""
from __future__ import annotations

from .errors import (
    InvalidAmountError,
    DuplicateMemberError,
    InvalidNameError,
)


def _normalise(name: str) -> str:
    """Key used to compare names: ignores letter case and extra spaces."""
    return " ".join(name.split()).casefold()


class Group:
    """One rotating savings group."""

    def __init__(self, weekly_amount: int) -> None:
        if (
            isinstance(weekly_amount, bool)
            or not isinstance(weekly_amount, int)
            or weekly_amount <= 0
        ):
            raise InvalidAmountError("The weekly contribution must be greater than zero.")
        self._weekly_amount = weekly_amount
        self._members: list[str] = []      # display names, in join order
        self._lookup: dict[str, str] = {}  # normalised name -> display name
        self._current_week = 1

    # ----- read-only views -------------------------------------------------

    @property
    def weekly_amount(self) -> int:
        return self._weekly_amount

    @property
    def members(self) -> tuple[str, ...]:
        """Members in the order they joined (which is also payout order)."""
        return tuple(self._members)

    @property
    def current_week(self) -> int:
        return self._current_week

    # ----- members ---------------------------------------------------------

    def add_member(self, name: str) -> str:
        """Add a member at the end of the payout order; return the stored name."""
        if not isinstance(name, str) or not name.strip():
            raise InvalidNameError("A member needs a name or ID.")
        key = _normalise(name)
        if key in self._lookup:
            raise DuplicateMemberError(f"'{self._lookup[key]}' is already in the group.")
        display = " ".join(name.split())
        self._members.append(display)
        self._lookup[key] = display
        return display

