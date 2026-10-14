import unittest

from susu.group import Group
from susu.report import format_report


def make_group(*names, weekly=5000):
    group = Group(weekly)
    for name in names:
        group.add_member(name)
    return group


class ReportTests(unittest.TestCase):
    def test_report_before_any_payment(self):
        report = make_group("Ama", "Kofi").report()
        self.assertEqual(report.current_week, 1)
        self.assertEqual(report.pot, 10000)
        self.assertEqual(report.paid_in_full, ())
        self.assertEqual(report.owing, (("Ama", 5000), ("Kofi", 5000)))
        self.assertEqual(report.payouts, ())
        self.assertEqual(report.next_recipient, "Ama")

    def test_report_shows_paid_owing_and_history(self):
        group = make_group("Ama", "Kofi", "Esi")
        group.contribute("Ama", 5000)
        group.contribute("Kofi", 5000)
        group.contribute("Esi", 3000)
        group.contribute("Esi", 2000)
        group.close_week()
        group.contribute("Ama", 5000)
        group.contribute("Kofi", 1000)

        report = group.report()
        self.assertEqual(report.current_week, 2)
        self.assertEqual(report.paid_in_full, ("Ama",))
        self.assertEqual(report.owing, (("Kofi", 4000), ("Esi", 5000)))
        self.assertEqual(report.next_recipient, "Kofi")

        text = format_report(report)
        self.assertIn("Current week: 2 of 3", text)
        self.assertIn("Kofi owes GHS 40.00", text)
        self.assertIn("Esi owes GHS 50.00", text)
        self.assertIn("Week 1: Ama received GHS 150.00", text)

    def test_report_when_the_cycle_is_complete(self):
        group = make_group("Ama")
        group.contribute("Ama", 5000)
        group.close_week()
        report = group.report()
        self.assertTrue(report.complete)
        self.assertIsNone(report.next_recipient)
        self.assertIn("Cycle complete", format_report(report))

    def test_report_for_an_empty_group_does_not_crash(self):
        text = format_report(Group(5000).report())
        self.assertIn("Members: 0", text)


if __name__ == "__main__":
    unittest.main()
