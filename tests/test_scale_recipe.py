import contextlib
import io
import os
import unittest
from fractions import Fraction

from scale_recipe import find_servings, main, scale_line, scale_recipe

EXAMPLE = os.path.join(os.path.dirname(__file__), "..", "examples", "pancakes.txt")


class ScaleLineTest(unittest.TestCase):
    def test_units_and_plurals(self):
        self.assertEqual(scale_line("1 cup flour", 2), "2 cups flour")
        self.assertEqual(scale_line("2 cups flour", Fraction(1, 2)), "1 cup flour")
        self.assertEqual(scale_line("1½ tsp salt", Fraction(3, 2)), "2 1/4 tsp salt")
        self.assertEqual(scale_line("a pinch of nutmeg", 2), "2 pinches nutmeg")

    def test_ranges(self):
        self.assertEqual(scale_line("2-3 cloves garlic", 2), "4 to 6 cloves garlic")

    def test_no_unit(self):
        self.assertEqual(scale_line("3 eggs", 2), "6 eggs")

    def test_left_alone(self):
        for line in ("", "# Pancakes", "1. Mix everything", "Salt to taste"):
            with self.subTest(line=line):
                self.assertEqual(scale_line(line, 2), line)


class ScaleRecipeTest(unittest.TestCase):
    def test_servings_line(self):
        text = "Serves 4\n2 cups flour"
        self.assertEqual(find_servings(text), 4)
        self.assertEqual(scale_recipe(text, Fraction(6, 4), servings=6), "Serves 6\n3 cups flour")

    def test_cli_to(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            main(["--to", "8", EXAMPLE])
        self.assertIn("Serves 8", out.getvalue())
        self.assertIn("4 cups all-purpose flour", out.getvalue())
        self.assertIn("2 pinches nutmeg", out.getvalue())

    def test_cli_rejects_both(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            main(["--factor", "2", "--to", "6", EXAMPLE])


if __name__ == "__main__":
    unittest.main()
