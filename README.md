# Susu Group Tracker

A small command-line program that manages one rotating savings group (susu).

Every member pays the same fixed weekly amount in GHS. Each week the whole pot
is paid to one member, in the order the members joined. A week only closes when
everyone has paid in full.

## Requirements

- Python 3.10 or newer (developed on Python 3.14)
- No third-party packages: standard library only

## Run the program

From the project folder:

```
python3 -m susu
```

You will be asked for the weekly contribution, then shown a menu:

```
1. Add member
2. Record contribution
3. Close week
4. Show report
5. Quit
```

### Example session

```
Weekly contribution in GHS (e.g. 50.00): 50.00
> 1  Ama      -> Added Ama (position 1 in the payout order).
> 1  Kofi
> 1  Esi
> 2  Ama   (week: press Enter)  50
> 2  Kofi                       50
> 2  Esi                        30
> 3  -> Week 1 cannot close yet. No payout was made.
        Esi owes GHS 20.00
> 2  Esi                        20
> 3  -> Week 1 closed. Ama receives GHS 150.00.
        Week 2 begins. Next to receive: Kofi.
```

## Run the tests

```
python3 -m unittest -v
```

The tests cover money handling, members, contributions (including partial
payments), closing weeks (including the "week cannot close" case), the report,
and the command-line menu.

## Project layout

```
susu/
  money.py     exact money: text <-> integer pesewas
  errors.py    one error type per broken rule
  models.py    small immutable result objects (Payout, CloseResult, Report)
  group.py     all the rules (no printing, no input)
  report.py    turns a Report into text
  cli.py       the menu; calls Group and prints results
  __main__.py  lets you run: python3 -m susu
tests/         automated tests, one file per feature
NOTES.md       assumptions, decisions, and what I would improve
```

## Rules the program enforces

- Unknown members, duplicate members, zero or negative amounts, and payments
  above what a member owes for the week are rejected.
- Partial payments are allowed.
- Payments are accepted for the current week only (no paying ahead or behind).
- Members can only be added before the first payment is recorded.
- Money is stored as whole pesewas, so there are no rounding errors.

See `NOTES.md` for the reasoning behind these choices.
