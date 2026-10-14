import unittest

from susu.errors import DuplicateMemberError, InvalidAmountError, InvalidNameError
from susu.group import Group


class GroupCreationTests(unittest.TestCase):
    def test_creates_group_with_weekly_amount(self):
        group = Group(5000)
        self.assertEqual(group.weekly_amount, 5000)
        self.assertEqual(group.current_week, 1)
        self.assertEqual(group.members, ())

    def test_rejects_zero_negative_or_non_integer_weekly_amount(self):
        for bad in (0, -100, 50.0, "50", None, True):
            with self.subTest(bad=bad):
                with self.assertRaises(InvalidAmountError):
                    Group(bad)


class AddMemberTests(unittest.TestCase):
    def test_members_keep_join_order(self):
        group = Group(5000)
        for name in ("Ama", "Kofi", "Esi"):
            group.add_member(name)
        self.assertEqual(group.members, ("Ama", "Kofi", "Esi"))

    def test_rejects_duplicates_ignoring_case_and_spacing(self):
        group = Group(5000)
        group.add_member("Ama Mensah")
        for duplicate in ("Ama Mensah", "ama mensah", "  AMA   MENSAH ", "Ama Mensah  "):
            with self.subTest(duplicate=duplicate):
                with self.assertRaises(DuplicateMemberError):
                    group.add_member(duplicate)
        self.assertEqual(group.members, ("Ama Mensah",))

    def test_rejects_blank_or_non_text_names(self):
        group = Group(5000)
        for bad in ("", "   ", None, 42):
            with self.subTest(bad=bad):
                with self.assertRaises(InvalidNameError):
                    group.add_member(bad)

    def test_stores_a_clean_display_name(self):
        group = Group(5000)
        self.assertEqual(group.add_member("  Kofi   Mensah "), "Kofi Mensah")
        self.assertEqual(group.members, ("Kofi Mensah",))


if __name__ == "__main__":
    unittest.main()
