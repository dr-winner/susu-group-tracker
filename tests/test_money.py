import unittest

from susu.errors import InvalidAmountError
from susu.money import format_amount, parse_amount


class ParseAmountTests(unittest.TestCase):
    def test_whole_and_decimal_amounts(self):
        cases = {"50": 5000, "50.00": 5000, "50.5": 5050, "0.10": 10, "0.05": 5, "  12.34 ": 1234}
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(parse_amount(text), expected)

    def test_rejects_malformed_text(self):
        bad = ["", "   ", "abc", "50.005", "1e2", "5,0", ".5", "50.", "GHS 50", "5 0", "--5", "+5"]
        for text in bad:
            with self.subTest(text=text):
                with self.assertRaises(InvalidAmountError):
                    parse_amount(text)

    def test_rejects_non_text(self):
        for value in (50, 50.0, None):
            with self.subTest(value=value):
                with self.assertRaises(InvalidAmountError):
                    parse_amount(value)

    def test_negative_is_parsed_so_the_group_can_reject_it_clearly(self):
        self.assertEqual(parse_amount("-5"), -500)

    def test_no_floating_point_error(self):
        # With floats, 0.1 + 0.2 == 0.30000000000000004
        self.assertEqual(parse_amount("0.10") + parse_amount("0.20"), parse_amount("0.30"))
        self.assertEqual(parse_amount("1.10") + parse_amount("2.20"), parse_amount("3.30"))


class FormatAmountTests(unittest.TestCase):
    def test_always_two_decimals(self):
        self.assertEqual(format_amount(5000), "50.00")
        self.assertEqual(format_amount(5), "0.05")
        self.assertEqual(format_amount(0), "0.00")
        self.assertEqual(format_amount(15050), "150.50")

    def test_round_trip(self):
        for text in ("0.01", "19.99", "1234.56"):
            with self.subTest(text=text):
                self.assertEqual(format_amount(parse_amount(text)), text)

    def test_negative(self):
        self.assertEqual(format_amount(-5), "-0.05")


if __name__ == "__main__":
    unittest.main()
