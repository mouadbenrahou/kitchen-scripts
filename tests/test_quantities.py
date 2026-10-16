import unittest
from fractions import Fraction

from quantities import format_quantity, parse_amount, parse_number


class ParseNumberTest(unittest.TestCase):
    def test_forms(self):
        cases = {
            "2 cups": Fraction(2),
            "1.5 cups": Fraction(3, 2),
            "1/2 cup": Fraction(1, 2),
            "1 1/2 cups": Fraction(3, 2),
            "½ cup": Fraction(1, 2),
            "1½ cups": Fraction(3, 2),
            "⅞ cup": Fraction(7, 8),
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(parse_number(text), (expected, "cups" if "cups" in text else "cup"))

    def test_not_a_number(self):
        self.assertEqual(parse_number("salt to taste"), (None, "salt to taste"))
        self.assertEqual(parse_number(""), (None, ""))

    def test_zero_denominator(self):
        self.assertEqual(parse_number("1/0 cup"), (None, "1/0 cup"))


class ParseAmountTest(unittest.TestCase):
    def test_article(self):
        self.assertEqual(parse_amount("a pinch of salt"), (Fraction(1), "pinch of salt"))

    def test_ranges(self):
        for text in ("2-3 cloves", "2 to 3 cloves", "2–3 cloves"):
            with self.subTest(text=text):
                self.assertEqual(parse_amount(text), ((Fraction(2), Fraction(3)), "cloves"))

    def test_single(self):
        self.assertEqual(parse_amount("3 eggs"), (Fraction(3), "eggs"))


class FormatQuantityTest(unittest.TestCase):
    def test_format(self):
        self.assertEqual(format_quantity(Fraction(3)), "3")
        self.assertEqual(format_quantity(Fraction(1, 2)), "1/2")
        self.assertEqual(format_quantity(Fraction(9, 4)), "2 1/4")
        self.assertEqual(format_quantity(0), "0")
        self.assertEqual(format_quantity(Fraction(1, 3) * 2), "2/3")


if __name__ == "__main__":
    unittest.main()
