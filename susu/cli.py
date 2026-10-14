"""Command-line menu for the susu tracker.

No business rules live here. It reads text, calls Group, and prints the
outcome. input_fn / print_fn can be swapped so the menu can be tested.
"""
from __future__ import annotations

from typing import Callable

from .errors import SusuError, WrongWeekError
from .group import Group
from .money import format_amount, parse_amount
from .report import format_report

MENU = """
--- Susu Group Tracker ---
1. Add member
2. Record contribution
3. Close week
4. Show report
5. Quit"""


def _create_group(input_fn: Callable, print_fn: Callable) -> Group:
    while True:
        try:
            weekly = parse_amount(input_fn("Weekly contribution in GHS (e.g. 50.00): "))
            return Group(weekly)
        except SusuError as error:
            print_fn(f"Error: {error}")


def _add_member(group: Group, input_fn: Callable, print_fn: Callable) -> None:
    name = group.add_member(input_fn("Member name or ID: "))
    print_fn(f"Added {name} (position {len(group.members)} in the payout order).")


def _record_contribution(group: Group, input_fn: Callable, print_fn: Callable) -> None:
    name = input_fn("Member name or ID: ")
    raw_week = input_fn(f"Week [{group.current_week}]: ").strip()
    if raw_week == "":
        week = group.current_week
    else:
        try:
            week = int(raw_week)
        except ValueError:
            raise WrongWeekError("Week must be a whole number.") from None
    amount = parse_amount(input_fn("Amount in GHS: "))
    still_owes = group.contribute(name, amount, week)
    shown = name.strip()
    if still_owes:
        print_fn(
            f"Recorded GHS {format_amount(amount)} from {shown}. "
            f"Still owes GHS {format_amount(still_owes)} for week {week}."
        )
    else:
        print_fn(f"Recorded GHS {format_amount(amount)} from {shown}. Paid in full for week {week}.")


def _close_week(group: Group, print_fn: Callable) -> None:
    week = group.current_week
    result = group.close_week()
    if not result.closed:
        print_fn(f"Week {week} cannot close yet. No payout was made.")
        for member, owed in result.owing:
            print_fn(f"  {member} owes GHS {format_amount(owed)}")
        return
    payout = result.payout
    print_fn(
        f"Week {payout.week} closed. {payout.member} receives "
        f"GHS {format_amount(payout.amount)}."
    )
    if group.is_complete:
        print_fn("All weeks are paid out. The cycle is complete.")
    else:
        print_fn(
            f"Week {group.current_week} begins. "
            f"Next to receive: {group.report().next_recipient}."
        )


def main(input_fn: Callable = input, print_fn: Callable = print) -> None:
    try:
        group = _create_group(input_fn, print_fn)
        while True:
            print_fn(MENU)
            choice = input_fn("Choose an option: ").strip()
            if choice == "5":
                print_fn("Goodbye.")
                return
            try:
                if choice == "1":
                    _add_member(group, input_fn, print_fn)
                elif choice == "2":
                    _record_contribution(group, input_fn, print_fn)
                elif choice == "3":
                    _close_week(group, print_fn)
                elif choice == "4":
                    print_fn(format_report(group.report()))
                else:
                    print_fn("Please choose 1, 2, 3, 4 or 5.")
            except SusuError as error:
                print_fn(f"Error: {error}")
    except (EOFError, KeyboardInterrupt):
        print_fn("\nGoodbye.")
