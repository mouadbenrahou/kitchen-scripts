#!/usr/bin/env python3
"""Scale the ingredient amounts in a plain-text recipe.

    scale_recipe.py --factor 2 pancakes.txt
    scale_recipe.py --to 6 pancakes.txt          # reads "Serves 4" from the recipe
    scale_recipe.py --from 4 --to 6 < pancakes.txt
"""
import argparse
import re
import sys
from fractions import Fraction

from quantities import format_quantity, parse_amount, read_text

UNITS = {
    "cup": "cup", "cups": "cup", "c": "cup",
    "tbsp": "tbsp", "tbs": "tbsp", "tablespoon": "tbsp", "tablespoons": "tbsp",
    "tsp": "tsp", "teaspoon": "tsp", "teaspoons": "tsp",
    "oz": "oz", "ounce": "oz", "ounces": "oz",
    "lb": "lb", "lbs": "lb", "pound": "lb", "pounds": "lb",
    "g": "g", "gram": "g", "grams": "g",
    "kg": "kg",
    "ml": "ml",
    "l": "l", "liter": "l", "litre": "l",
    "clove": "clove", "cloves": "clove",
    "pinch": "pinch", "pinches": "pinch",
    "can": "can", "cans": "can",
    "slice": "slice", "slices": "slice",
    "bunch": "bunch", "bunches": "bunch",
    "sprig": "sprig", "sprigs": "sprig",
}

PLURAL = {
    "cup": "cups",
    "clove": "cloves",
    "pinch": "pinches",
    "can": "cans",
    "slice": "slices",
    "bunch": "bunches",
    "sprig": "sprigs",
}

SERVINGS = re.compile(r"(?i)^(\s*(?:servings?|serves|yield)\s*[:=]?\s*)(\d+)(.*)$")
STEP = re.compile(r"\d+\.\s+")


def scale_line(line, factor):
    """Scale one ingredient line. Lines that are not ingredients come back unchanged."""
    s = line.strip()
    if not s or s.startswith("#") or STEP.match(s):
        return line.rstrip("\n")

    amount, rest = parse_amount(s)
    if amount is None:
        return line.rstrip("\n")

    unit, name = "", rest
    bits = rest.split(None, 1)
    if bits:
        word = bits[0].lower().rstrip(".")
        if word in UNITS:
            unit = UNITS[word]
            name = bits[1] if len(bits) > 1 else ""
    if name.lower().startswith("of "):
        name = name[3:]

    if isinstance(amount, tuple):
        low, high = amount[0] * factor, amount[1] * factor
        text = format_quantity(low) + " to " + format_quantity(high)
        biggest = high
    else:
        biggest = amount * factor
        text = format_quantity(biggest)

    if unit:
        text += " " + (PLURAL[unit] if biggest > 1 and unit in PLURAL else unit)
    if name:
        text += " " + name
    return text


def scale_recipe(text, factor, servings=None):
    """Scale every line of a recipe; rewrite the servings line if `servings` is given."""
    out = []
    for line in text.splitlines():
        m = SERVINGS.match(line)
        if m and servings:
            out.append("%s%d%s" % (m.group(1), servings, m.group(3)))
        else:
            out.append(scale_line(line, factor))
    return "\n".join(out)


def find_servings(text):
    for line in text.splitlines():
        m = SERVINGS.match(line)
        if m:
            return int(m.group(2))
    return None


def positive_fraction(value):
    try:
        f = Fraction(value)
    except (ValueError, ZeroDivisionError):
        raise argparse.ArgumentTypeError("not a number: %r" % value)
    if f <= 0:
        raise argparse.ArgumentTypeError("has to be > 0")
    return f


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Scale the ingredient amounts in a plain-text recipe.",
        epilog="Give either --factor, or --to (with --from or a 'Serves N' line in the recipe).",
    )
    p.add_argument("file", nargs="?", help="recipe file (default: read from stdin)")
    p.add_argument("--factor", type=positive_fraction, help="multiply every amount, e.g. 2, 0.5 or 3/2")
    p.add_argument("--from", dest="src", type=int, metavar="N", help="servings the recipe makes now")
    p.add_argument("--to", dest="dst", type=int, metavar="N", help="servings you want")
    args = p.parse_args(argv)

    text = read_text(args.file) if args.file else sys.stdin.read()

    if args.factor is not None:
        if args.src or args.dst:
            p.error("use either --factor or --from/--to, not both")
        print(scale_recipe(text, args.factor))
        return

    src = args.src or find_servings(text)
    if not src or not args.dst:
        p.error("need --factor, or --to plus --from (or a 'Serves N' line in the recipe)")
    print(scale_recipe(text, Fraction(args.dst, src), servings=args.dst))


if __name__ == "__main__":
    main()
