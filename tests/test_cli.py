import unittest

from susu.cli import main


def run_cli(inputs):
    """Run the menu with scripted answers and return everything it printed."""
    answers = iter(inputs)
    output = []

    def fake_input(prompt=""):
        output.append(prompt)
        try:
            return next(answers)
        except StopIteration:
            raise EOFError from None

    main(input_fn=fake_input, print_fn=output.append)
    return "\n".join(output)


class CliTests(unittest.TestCase):
    def test_full_walkthrough_of_the_brief_example(self):
        text = run_cli([
            "50.00",
            "1", "Ama", "1", "Kofi", "1", "Esi",
            "2", "Ama", "", "50",
            "2", "Kofi", "", "50",
            "2", "Esi", "", "30",
            "3",
            "2", "Esi", "", "20",
            "3",
            "4",
            "5",
        ])
        self.assertIn("Week 1 cannot close yet", text)
        self.assertIn("Esi owes GHS 20.00", text)
        self.assertIn("Week 1 closed. Ama receives GHS 150.00.", text)
        self.assertIn("Next to receive: Kofi", text)
        self.assertIn("Week 1: Ama received GHS 150.00", text)

    def test_bad_weekly_amount_is_asked_again(self):
        text = run_cli(["abc", "0", "50", "5"])
        self.assertEqual(text.count("Error:"), 2)
        self.assertIn("Goodbye.", text)

    def test_errors_are_shown_and_the_menu_keeps_running(self):
        text = run_cli([
            "50",
            "1", "Ama",
            "1", "ama",
            "2", "Yaw", "", "10",
            "2", "Ama", "x", "10",
            "2", "Ama", "", "-5",
            "2", "Ama", "", "60",
            "9",
            "5",
        ])
        self.assertIn("already in the group", text)
        self.assertIn("not a member", text)
        self.assertIn("Week must be a whole number", text)
        self.assertIn("greater than zero", text)
        self.assertIn("owes only GHS 50.00", text)
        self.assertIn("Please choose 1, 2, 3, 4 or 5.", text)
        self.assertIn("Goodbye.", text)

    def test_end_of_input_exits_cleanly(self):
        self.assertIn("Goodbye.", run_cli(["50"]))


if __name__ == "__main__":
    unittest.main()
