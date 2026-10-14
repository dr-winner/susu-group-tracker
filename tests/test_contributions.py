import unittest

from susu.errors import (
    GroupStartedError,
    InvalidAmountError,
    OverpaymentError,
    UnknownMemberError,
    WrongWeekError,
)
from susu.group import Group


def make_group(*names, weekly=5000):
    group = Group(weekly)
    for name in names:
        group.add_member(name)
    return group


class ContributionTests(unittest.TestCase):
    def test_full_payment_clears_what_is_owed(self):
        group = make_group("Ama", "Kofi")
        self.assertEqual(group.contribute("Ama", 5000), 0)
        self.assertEqual(group.owing(), (("Kofi", 5000),))

    def test_partial_payment_is_allowed_and_remainder_is_tracked(self):
        group = make_group("Ama", "Esi")
        self.assertEqual(group.contribute("Esi", 3000), 2000)
        self.assertIn(("Esi", 2000), group.owing())

    def test_partial_payments_add_up(self):
        group = make_group("Esi")
        group.contribute("Esi", 3000)
        self.assertEqual(group.contribute("Esi", 2000), 0)
        self.assertEqual(group.owing(), ())

    def test_rejects_unknown_member(self):
        group = make_group("Ama")
        with self.assertRaises(UnknownMemberError):
            group.contribute("Yaw", 5000)

    def test_rejects_zero_and_negative_amounts(self):
        group = make_group("Ama")
        for bad in (0, -1, -5000):
            with self.subTest(bad=bad):
                with self.assertRaises(InvalidAmountError):
                    group.contribute("Ama", bad)

    def test_rejects_non_integer_amounts(self):
        group = make_group("Ama")
        for bad in (50.0, "50", None, True):
            with self.subTest(bad=bad):
                with self.assertRaises(InvalidAmountError):
                    group.contribute("Ama", bad)

    def test_rejects_payment_above_what_is_owed_and_changes_nothing(self):
        group = make_group("Ama")
        with self.assertRaises(OverpaymentError):
            group.contribute("Ama", 5001)
        self.assertEqual(group.owing(), (("Ama", 5000),))

    def test_overpayment_after_a_partial_payment(self):
        group = make_group("Ama")
        group.contribute("Ama", 3000)
        with self.assertRaises(OverpaymentError):
            group.contribute("Ama", 2001)
        self.assertEqual(group.contribute("Ama", 2000), 0)

    def test_rejects_payment_when_already_paid_in_full(self):
        group = make_group("Ama")
        group.contribute("Ama", 5000)
        with self.assertRaises(OverpaymentError):
            group.contribute("Ama", 1)

    def test_member_lookup_ignores_case(self):
        group = make_group("Ama Mensah")
        group.contribute("  ama   mensah ", 5000)
        self.assertEqual(group.owing(), ())

    def test_only_the_current_week_accepts_payments(self):
        group = make_group("Ama")
        for wrong_week in (0, 2, -1):
            with self.subTest(week=wrong_week):
                with self.assertRaises(WrongWeekError):
                    group.contribute("Ama", 1000, week=wrong_week)
        self.assertEqual(group.contribute("Ama", 1000, week=1), 4000)
        self.assertEqual(group.contribute("Ama", 1000, week=None), 3000)

    def test_cannot_add_members_after_the_first_payment(self):
        group = make_group("Ama", "Kofi")
        group.contribute("Ama", 100)
        with self.assertRaises(GroupStartedError):
            group.add_member("Esi")
        self.assertEqual(group.members, ("Ama", "Kofi"))

    def test_members_can_still_be_added_before_any_payment(self):
        group = make_group("Ama")
        group.add_member("Kofi")
        self.assertEqual(group.members, ("Ama", "Kofi"))

    def test_owing_lists_everyone_before_any_payment(self):
        group = make_group("Ama", "Kofi")
        self.assertEqual(group.owing(), (("Ama", 5000), ("Kofi", 5000)))


if __name__ == "__main__":
    unittest.main()
