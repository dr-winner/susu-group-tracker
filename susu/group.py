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
    GroupStartedError,
    OverpaymentError,
    UnknownMemberError,
    WrongWeekError,
    GroupCompleteError,
    NoMembersError,
)
from .money import format_amount
from .models import CloseResult, Payout, Report


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
        self._paid: dict[str, int] = {}    # member -> pesewas paid THIS week
        self._started = False              # True once any payment is recorded
        self._payouts: list[Payout] = []

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

    @property
    def payouts(self) -> tuple[Payout, ...]:
        return tuple(self._payouts)

    @property
    def is_complete(self) -> bool:
        """True once every member has received the pot."""
        return bool(self._members) and self._current_week > len(self._members)

    # ----- members ---------------------------------------------------------

    def add_member(self, name: str) -> str:
        """Add a member at the end of the payout order; return the stored name."""
        if not isinstance(name, str) or not name.strip():
            raise InvalidNameError("A member needs a name or ID.")
        if self._started:
            raise GroupStartedError(
                "Members cannot be added after payments have started: "
                "a late joiner would receive the pot without having paid earlier weeks."
            )
        key = _normalise(name)
        if key in self._lookup:
            raise DuplicateMemberError(f"'{self._lookup[key]}' is already in the group.")
        display = " ".join(name.split())
        self._members.append(display)
        self._lookup[key] = display
        self._paid[display] = 0
        return display

    def _resolve(self, name: str) -> str:
        """Find a member by name (any letter case); raise if unknown."""
        if isinstance(name, str):
            member = self._lookup.get(_normalise(name))
            if member is not None:
                return member
        raise UnknownMemberError(f"'{name}' is not a member of this group.")

    # ----- contributions ---------------------------------------------------

    def contribute(self, name: str, amount: int, week: int | None = None) -> int:
        """Record a payment (in pesewas) from a member for the current week.

        Partial payments are allowed. Returns what the member still owes
        this week after the payment.
        """
        if self.is_complete:
            raise GroupCompleteError(
                "The cycle is complete: every member has already received the pot."
            )
        member = self._resolve(name)
        if week is not None and week != self._current_week:
            raise WrongWeekError(
                f"Only week {self._current_week} is open for payments "
                f"(week {week} was requested). No paying ahead or behind."
            )
        if isinstance(amount, bool) or not isinstance(amount, int) or amount <= 0:
            raise InvalidAmountError("A payment must be greater than zero.")
        owed = self._weekly_amount - self._paid[member]
        if owed == 0:
            raise OverpaymentError(
                f"{member} has already paid in full for week {self._current_week}."
            )
        if amount > owed:
            raise OverpaymentError(
                f"{member} owes only GHS {format_amount(owed)} for week "
                f"{self._current_week}; cannot accept GHS {format_amount(amount)}."
            )
        self._paid[member] += amount
        self._started = True
        return owed - amount

    def owing(self) -> tuple[tuple[str, int], ...]:
        """(member, pesewas still owed) for everyone not yet paid in full."""
        return tuple(
            (member, self._weekly_amount - self._paid[member])
            for member in self._members
            if self._paid[member] < self._weekly_amount
        )

    # ----- closing a week --------------------------------------------------

    def close_week(self) -> CloseResult:
        """Try to close the current week.

        If everyone has paid in full, the pot goes to the next member in
        order and the next week begins. If not, nothing is paid and the
        result lists who still owes what. Money already paid stays recorded.
        """
        if self.is_complete:
            raise GroupCompleteError(
                "The cycle is complete: every member has already received the pot."
            )
        if not self._members:
            raise NoMembersError("Add at least one member before closing a week.")
        owing = self.owing()
        if owing:
            return CloseResult(closed=False, payout=None, owing=owing)
        recipient = self._members[self._current_week - 1]
        payout = Payout(
            week=self._current_week,
            member=recipient,
            amount=self._weekly_amount * len(self._members),
        )
        self._payouts.append(payout)
        self._current_week += 1
        self._paid = {member: 0 for member in self._members}
        return CloseResult(closed=True, payout=payout, owing=())

    # ----- reporting -------------------------------------------------------

    def report(self) -> Report:
        """A snapshot: current week, who paid in full, who owes, payout history."""
        complete = self.is_complete
        paid_in_full = ()
        owing = ()
        next_recipient = None
        if not complete:
            paid_in_full = tuple(
                m for m in self._members if self._paid[m] >= self._weekly_amount
            )
            owing = self.owing()
            if self._members:
                next_recipient = self._members[self._current_week - 1]
        return Report(
            weekly_amount=self._weekly_amount,
            pot=self._weekly_amount * len(self._members),
            current_week=self._current_week,
            total_weeks=len(self._members),
            complete=complete,
            next_recipient=next_recipient,
            paid_in_full=paid_in_full,
            owing=owing,
            payouts=self.payouts,
        )
