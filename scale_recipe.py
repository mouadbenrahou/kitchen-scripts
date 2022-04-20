#!/usr/bin/env python3
import re
import sys
from fractions import Fraction

fracs = {
    "½": Fraction(1, 2),
    "⅓": Fraction(1, 3),
    "⅔": Fraction(2, 3),
    "¼": Fraction(1, 4),
    "¾": Fraction(3, 4),
    "⅛": Fraction(1, 8),
    "⅜": Fraction(3, 8),
    "⅝": Fraction(5, 8),
    "⅞": Fraction(7, 8),
}

units = {
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

plural = {
    "cup": "cups",
    "clove": "cloves",
    "pinch": "pinches",
    "can": "cans",
    "slice": "slices",
    "bunch": "bunches",
    "sprig": "sprigs",
}


def take_num(s):
    s = s.strip()
    if not s:
        return None, s
    if s[0] in fracs:
        return fracs[s[0]], s[1:].strip()
    m = re.match(r"(\d+)\s+(\d+)\s*/\s*(\d+)", s)
    if m:
        a, b, c = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if c == 0:
            return None, s
        return Fraction(a) + Fraction(b, c), s[m.end():].strip()
    m = re.match(r"(\d+)\s*/\s*(\d+)", s)
    if m:
        b, c = int(m.group(1)), int(m.group(2))
        if c == 0:
            return None, s
        return Fraction(b, c), s[m.end():].strip()
    m = re.match(r"(\d+\.\d+|\d+)", s)
    if m:
        return Fraction(m.group(1)), s[m.end():].strip()
    return None, s


def show(q):
    q = Fraction(q).limit_denominator(8)
    if q <= 0:
        return "0"
    if q.denominator == 1:
        return str(q.numerator)
    w = q.numerator // q.denominator
    n = q.numerator % q.denominator
    if w:
        return "%d %d/%d" % (w, n, q.denominator)
    return "%d/%d" % (n, q.denominator)


def scale_line(line, factor):
    s = line.strip()
    if not s or s.startswith("#"):
        return line.rstrip("\n")
    if re.match(r"\d+\.\s+", s):
        return line.rstrip("\n")

    m = re.match(r"(?i)^(a|an)\s+", s)
    if m:
        qty = Fraction(1)
        rest = s[m.end():]
    else:
        qty, rest = take_num(s)
        if qty is None:
            return line.rstrip("\n")
        if rest[:1] in fracs:
            qty = qty + fracs[rest[0]]
            rest = rest[1:].strip()

    m = re.match(r"(?:-|–|—|\bto\b)\s*", rest)
    if m:
        qty2, rest2 = take_num(rest[m.end():])
        if qty2 is not None:
            qty = (qty, qty2)
            rest = rest2

    word = ""
    name = rest
    bits = rest.split(None, 1)
    if bits:
        word = bits[0].lower().rstrip(".")
        if word in units:
            name = bits[1] if len(bits) > 1 else ""
        else:
            word = ""
    if name.lower().startswith("of "):
        name = name[3:]

    if isinstance(qty, tuple):
        lo = qty[0] * factor
        hi = qty[1] * factor
        text = show(lo) + " to " + show(hi)
        n = hi
    else:
        n = qty * factor
        text = show(n)

    unit = units[word] if word else ""
    if unit:
        if n > 1 and unit in plural:
            text += " " + plural[unit]
        else:
            text += " " + unit
    if name:
        text += " " + name
    return text


def main():
    factor = None
    src = None
    dst = None
    path = None

    argv = sys.argv[1:]
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--factor" and i + 1 < len(argv):
            i += 1
            factor = float(argv[i])
        elif a == "--from" and i + 1 < len(argv):
            i += 1
            src = int(argv[i])
        elif a == "--to" and i + 1 < len(argv):
            i += 1
            dst = int(argv[i])
        elif a in ("-h", "--help"):
            print("usage: scale_recipe.py [--factor N | --from A --to B] [file]")
            return
        else:
            path = a
        i += 1

    if path:
        f = open(path)
        text = f.read()
        f.close()
    else:
        text = sys.stdin.read()
    lines = text.splitlines()

    if factor is not None:
        if factor <= 0:
            print("factor has to be > 0", file=sys.stderr)
            sys.exit(1)
        factor = Fraction(str(factor))
        dst = None
    else:
        if src is None:
            for line in lines:
                m = re.match(r"(?i)\s*(?:servings?|serves|yield)\s*[:=]?\s*(\d+)", line)
                if m:
                    src = int(m.group(1))
                    break
        if not src or not dst:
            print("need --factor, or --from and --to", file=sys.stderr)
            sys.exit(1)
        factor = Fraction(dst, src)

    out = []
    for line in lines:
        m = re.match(r"(?i)^(\s*(?:servings?|serves|yield)\s*[:=]?\s*)(\d+)(.*)$", line)
        if m and dst:
            out.append("%s%d%s" % (m.group(1), dst, m.group(3)))
            continue
        out.append(scale_line(line, factor))
    print("\n".join(out))


if __name__ == "__main__":
    main()
