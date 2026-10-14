import unittest

from susu.errors import GroupCompleteError, NoMembersError
from susu.group import Group
from susu.money import parse_amount


def make_group(*names, weekly=5000):
    group = Group(weekly)
    for name in names:
        group.add_member(name)
    return group


def everyone_pays_in_full(group):
    for name in group.members:
        group.contribute(name, group.weekly_amount)


class CloseWeekTests(unittest.TestCase):
    def test_week_cannot_close_when_someone_has_not_paid_in_full(self):
        group = make_group("Ama", "Kofi", "Esi")
        group.contribute("Ama", 5000)
        group.contribute("Kofi", 5000)
        group.contribute("Esi", 3000)
        result = group.close_week()
        self.assertFalse(result.closed)
        self.assertIsNone(result.payout)
        self.assertEqual(result.owing, (("Esi", 2000),))
        self.assertEqual(group.payouts, ())
        self.assertEqual(group.current_week, 1)

    def test_week_cannot_close_when_nobody_has_paid(self):
        group = make_group("Ama", "Kofi")
        result = group.close_week()
        self.assertFalse(result.closed)
        self.assertEqual(result.owing, (("Ama", 5000), ("Kofi", 5000)))

    def test_a_failed_close_keeps_money_already_paid(self):
        group = make_group("Ama", "Kofi")
        group.contribute("Ama", 5000)
        group.contribute("Kofi", 1000)
        group.close_week()
        self.assertEqual(group.owing(), (("Kofi", 4000),))
        group.contribute("Kofi", 4000)
        self.assertTrue(group.close_week().closed)

    def test_closing_pays_the_whole_pot_to_the_first_member(self):
        group = make_group("Ama", "Kofi", "Esi")
        everyone_pays_in_full(group)
        result = group.close_week()
        self.assertTrue(result.closed)
        self.assertEqual(result.payout.member, "Ama")
        self.assertEqual(result.payout.week, 1)
        self.assertEqual(result.payout.amount, 15000)
        self.assertEqual(group.current_week, 2)

    def test_payouts_follow_join_order_one_member_per_week(self):
        group = make_group("Ama", "Kofi", "Esi")
        for _ in range(3):
            everyone_pays_in_full(group)
            group.close_week()
        self.assertEqual([p.member for p in group.payouts], ["Ama", "Kofi", "Esi"])
        self.assertEqual([p.week for p in group.payouts], [1, 2, 3])

    def test_next_week_starts_with_everyone_owing_the_full_amount(self):
        group = make_group("Ama", "Kofi")
        everyone_pays_in_full(group)
        group.close_week()
        self.assertEqual(group.owing(), (("Ama", 5000), ("Kofi", 5000)))

    def test_cycle_completes_after_every_member_has_been_paid(self):
        group = make_group("Ama", "Kofi")
        for _ in range(2):
            self.assertFalse(group.is_complete)
            everyone_pays_in_full(group)
            group.close_week()
        self.assertTrue(group.is_complete)

    def test_nothing_is_allowed_after_the_cycle_is_complete(self):
        group = make_group("Ama")
        everyone_pays_in_full(group)
        group.close_week()
        with self.assertRaises(GroupCompleteError):
            group.contribute("Ama", 100)
        with self.assertRaises(GroupCompleteError):
            group.close_week()

    def test_cannot_close_a_group_with_no_members(self):
        with self.assertRaises(NoMembersError):
            Group(5000).close_week()

    def test_pot_is_exact_with_awkward_amounts(self):
        group = make_group("Ama", "Kofi", "Esi", weekly=parse_amount("33.33"))
        everyone_pays_in_full(group)
        self.assertEqual(group.close_week().payout.amount, parse_amount("99.99"))

    def test_the_example_from_the_brief(self):
        group = make_group("Ama", "Kofi", "Esi", weekly=parse_amount("50.00"))
        group.contribute("Ama", parse_amount("50"))
        group.contribute("Kofi", parse_amount("50"))
        group.contribute("Esi", parse_amount("30"))

        blocked = group.close_week()
        self.assertFalse(blocked.closed)
        self.assertEqual(blocked.owing, (("Esi", parse_amount("20.00")),))

        group.contribute("Esi", parse_amount("20"))
        paid = group.close_week()
        self.assertTrue(paid.closed)
        self.assertEqual((paid.payout.member, paid.payout.amount), ("Ama", parse_amount("150.00")))

        self.assertEqual(group.current_week, 2)
        self.assertEqual(group.members[group.current_week - 1], "Kofi")  # Kofi is next


if __name__ == "__main__":
    unittest.main()
