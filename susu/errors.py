"""Custom errors.

Every rule the program enforces raises a SusuError subclass, so the command
line (and the tests) can catch them all in one place and show a clear message.
"""


class SusuError(Exception):
    """Base class for every error this program raises on purpose."""


class InvalidAmountError(SusuError):
    """An amount is not a valid, allowed money value."""


class InvalidNameError(SusuError):
    """A member name or ID is empty or not text."""


class DuplicateMemberError(SusuError):
    """A member with this name or ID already exists."""


class UnknownMemberError(SusuError):
    """The named member is not in the group."""


class GroupStartedError(SusuError):
    """Members can no longer be added because payments have started."""


class WrongWeekError(SusuError):
    """A payment was aimed at a week that is not the current week."""


class OverpaymentError(SusuError):
    """A payment is larger than what the member still owes this week."""


class NoMembersError(SusuError):
    """The action needs at least one member."""


class GroupCompleteError(SusuError):
    """Every member has already received the pot; the cycle is over."""


