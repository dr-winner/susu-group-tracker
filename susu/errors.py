"""Custom errors.

Every rule the program enforces raises a SusuError subclass, so the command
line (and the tests) can catch them all in one place and show a clear message.
"""


class SusuError(Exception):
    """Base class for every error this program raises on purpose."""


class InvalidAmountError(SusuError):
    """An amount is not a valid, allowed money value."""


