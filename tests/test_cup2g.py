import contextlib
import io
import unittest

from cup2g import convert_line, main


class ConvertLineTest(unittest.TestCase):
    def test_conversions(self):
        self.assertEqual(convert_line("1 cup flour"), "125 g flour")
        self.assertEqual(convert_line("½ cup butter"), "113.5 g butter")
        self.assertEqual(convert_line("2 tbsp sugar"), "25 g sugar")
        self.assertEqual(convert_line("a cup of milk"), "245 g milk")

    def test_ranges(self):
        self.assertEqual(convert_line("1 to 2 cups flour"), "125 to 250 g flour")

    def test_all_unicode_fractions(self):
        self.assertEqual(convert_line("⅝ cup sugar"), "125 g sugar")

    def test_ingredient_names(self):
        self.assertEqual(convert_line("1 cup all-purpose flour, sifted"), "125 g all-purpose flour, sifted")

    def test_left_alone(self):
        for line in ("3 eggs", "1 cup chopped walnuts", "1. Preheat the oven", "# Cookies"):
            with self.subTest(line=line):
                self.assertEqual(convert_line(line), line)

    def test_cli_words(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            main(["1", "cup", "flour"])
        self.assertEqual(out.getvalue(), "125 g flour\n")


if __name__ == "__main__":
    unittest.main()
