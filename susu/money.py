##### Exact money handling

# Money is stored as an integer number of pesewas (1 GHS = 100 pesewas).
# Integers never suffer the rounding errors that floats do (0.1 + 0.2 != 0.3), so every total in the program is exact

import re
from .errors import InvalidAmountError

PESEWAS_PER_CEDI = 100

# optional minus, digits, optional dot with 1 or 2 decimal digits
_AMOUNT_PATTERN = re.compile(r"(-?)([0-9]+)(?:\.([0-9]{1,2}))?")


def parse_amount(text: str) -> int:
    # Turn text such as '50', '50.5' or '50.25' into integer pesewas

    # More than two decimal places is rejected, not rounded: silently rounding money would hide a mistake
    # A leading minus is parsed, '-5' gives -500 and the group rejects it with a clear message about amounts needing to be above zero
    
    if not isinstance(text, str):
        raise InvalidAmountError("An amount must be typed as text, e.g. 50.00.")
    match = _AMOUNT_PATTERN.fullmatch(text.strip())
    if match is None:
        raise InvalidAmountError(
            f"Sorry! '{text.strip()}' is not a valid amount. "
            "Please use digits with at most 2 decimal places, e.g. 50 or 50.25."
        )
    sign, whole, fraction = match.groups()
    pesewas = int(whole) * PESEWAS_PER_CEDI + int((fraction or "").ljust(2, "0"))
    return -pesewas if sign else pesewas


def format_amount(pesewas: int) -> str:
    # Turn integer pesewas into text with exactly two decimals: 5000 -> '50.00'
    sign = "-" if pesewas < 0 else ""
    whole, fraction = divmod(abs(pesewas), PESEWAS_PER_CEDI)
    return f"{sign}{whole}.{fraction:02d}"