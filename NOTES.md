# Notes

## Assumptions (things the brief did not say)

1. **Money is whole pesewas.** 1 GHS = 100 pesewas and every amount is stored as an integer, so 0.10 + 0.20 is exactly 0.30. Input with more than 2 decimal places (e.g. `50.005`) is rejected, not rounded, because silently rounding someone's money would hide a mistake.
2. **Members can only join before the first payment is recorded.** After that, adding a member is rejected. Reason: a late joiner would receive the pot without having paid earlier weeks, and the pot size would change halfway through the cycle. Fixing the member list also fixes the cycle length (one week per member) and the pot (weekly amount x members).
3. **Payments are accepted for the current week only.** Paying ahead or for an earlier week is rejected. The `week` can be given when recording a payment; if it is not the current week the payment is refused. Because a week cannot close until everyone has paid in full, no earlier week can ever be left unpaid.
4. **A member who is behind blocks the week.** If someone has not paid in full, the week stays open: nothing is paid out, nothing is refunded, and money already paid stays recorded against that member. When the last person pays, the week closes and the whole pot goes to the next member in order. There are no penalties, no carried-over debt and no skipping of defaulters.
5. **A member who has paid in full cannot pay more** that week (treated as an overpayment).
6. **Names:** leading/trailing spaces are removed, repeated spaces are collapsed, and names are compared ignoring letter case. `ama` and ` AMA ` are duplicates of `Ama`. The first spelling is kept for display. Lookups when paying also ignore case.
7. **One cycle per group.** After every member has received the pot once, the group is complete. Further payments or closing are rejected. A new cycle would be a new group.
8. **Closing an empty group** is rejected.
9. **No saved data.** The group lives in memory while the program runs.

## Decisions

- **Logic is separate from the menu.** `group.py` never prints or reads input. That is why it can be tested directly, and the menu (`cli.py`) is only a thin layer that could be swapped for an API.
- **A week that cannot close is a normal result, not an error.** `close_week()` returns a `CloseResult` saying `closed=False` and who owes what. Real problems (unknown member, overpayment, etc.) raise errors.
- **One error type per rule**, all inheriting from `SusuError`, so the menu can catch them in one place and tests can check the exact rule that failed.
- **Immutable results** (frozen dataclasses, tuples) so callers cannot change the group's state by accident.
- **Standard library only** (`unittest`), so nothing needs installing.
- **Menu input is injectable** (`input_fn` / `print_fn`), so the menu itself has automated tests.
- Small, feature-by-feature commits, with tests added alongside each feature.

## What I would improve with more time

- Save and load the group (JSON file or small database) so it survives restarts.
- A real policy for members who do not pay: grace periods, penalties, skipping or replacing a member, with the group agreeing to the rule up front.
- Allow late joiners under explicit rules (for example, they join at the end and pay a catch-up amount).
- Keep a timestamped ledger of every payment for an audit trail and receipts.
- Support several groups at once, and a small HTTP API on top of `Group`.
- Allow a negotiated payout order (for example, a lottery or a member in urgent need going first).
- Property-based tests for the money and payout invariants (total paid out always equals total paid in).
