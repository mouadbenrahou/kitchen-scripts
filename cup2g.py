#!/usr/bin/env python3
"""Convert cup and spoon measures to grams.

    cup2g.py 1 cup flour
    cup2g.py recipe.txt
    cat recipe.txt | cup2g.py
"""
import argparse
import os
import re
import sys
from fractions import Fraction

from quantities import parse_amount, read_text

# Grams in one US cup.
GRAMS_PER_CUP = {
    "flour": 125,
    "all purpose flour": 125,
    "plain flour": 125,
    "bread flour": 130,
    "cake flour": 114,
    "sugar": 200,
    "caster sugar": 200,
    "white sugar": 200,
    "brown sugar": 220,
    "butter": 227,
    "milk": 245,
    "water": 240,
    "oil": 218,
    "olive oil": 216,
    "honey": 340,
    "cocoa": 85,
    "cocoa powder": 85,
    "oats": 90,
    "rolled oats": 90,
    "rice": 185,
    "salt": 292,
    "baking powder": 230,
    "baking soda": 220,
    "yogurt": 245,
    "cream": 240,
    "heavy cream": 238,
    "maple syrup": 322,
    "chocolate chips": 170,
    "almond flour": 96,
}

# How much of a cup each measure is.
CUPS = {
    "cup": 1, "cups": 1, "c": 1,
    "tbsp": Fraction(1, 16), "tbs": Fraction(1, 16),
    "tablespoon": Fraction(1, 16), "tablespoons": Fraction(1, 16),
    "tsp": Fraction(1, 48), "teaspoon": Fraction(1, 48), "teaspoons": Fraction(1, 48),
}

STEP = re.compile(r"\d+\.\s+")


def ingredient_key(name):
    """'All-purpose flour, sifted' -> 'all purpose flour'."""
    return re.sub(r"[-\s]+", " ", name.split(",")[0]).strip().lower()


def show_grams(grams):
    if abs(grams - round(grams)) < 0.06:
        return str(int(round(grams)))
    return ("%.1f" % grams).rstrip("0").rstrip(".")


def convert_line(line):
    """Convert one ingredient line to grams. Anything it can't convert comes back unchanged."""
    s = line.strip()
    if not s or s.startswith("#") or STEP.match(s):
        return line.rstrip("\n")

    amount, rest = parse_amount(s)
    if amount is None:
        return line.rstrip("\n")

    bits = rest.split(None, 1)
    if not bits:
        return line.rstrip("\n")
    unit = bits[0].lower().rstrip(".")
    if unit not in CUPS:
        return line.rstrip("\n")
    name = bits[1].strip() if len(bits) > 1 else ""
    if name.lower().startswith("of "):
        name = name[3:]
    key = ingredient_key(name)
    if key not in GRAMS_PER_CUP:
        return line.rstrip("\n")

    def grams(q):
        return float(q * CUPS[unit] * GRAMS_PER_CUP[key])

    if isinstance(amount, tuple):
        shown = show_grams(grams(amount[0])) + " to " + show_grams(grams(amount[1]))
    else:
        shown = show_grams(grams(amount))
    return shown + " g " + name


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Convert cup and spoon measures to grams.",
        epilog="Known ingredients: " + ", ".join(sorted(GRAMS_PER_CUP)),
    )
    p.add_argument("input", nargs="*",
                   help="a recipe file, or an ingredient like: 1 cup flour (default: read from stdin)")
    args = p.parse_args(argv)

    if not args.input:
        text = sys.stdin.read()
    elif len(args.input) == 1 and os.path.isfile(args.input[0]):
        text = read_text(args.input[0])
    else:
        text = " ".join(args.input)

    for line in text.splitlines():
        print(convert_line(line))


if __name__ == "__main__":
    main()
