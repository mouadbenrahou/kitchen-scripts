import re
import sys
from fractions import Fraction

cup = {
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

spoon = {
    "cup": 1,
    "cups": 1,
    "c": 1,
    "tbsp": Fraction(1, 16),
    "tbs": Fraction(1, 16),
    "tablespoon": Fraction(1, 16),
    "tablespoons": Fraction(1, 16),
    "tsp": Fraction(1, 48),
    "teaspoon": Fraction(1, 48),
    "teaspoons": Fraction(1, 48),
}

marks = {
    "½": Fraction(1, 2),
    "⅓": Fraction(1, 3),
    "⅔": Fraction(2, 3),
    "¼": Fraction(1, 4),
    "¾": Fraction(3, 4),
    "⅛": Fraction(1, 8),
}


def take_num(s):
    s = s.strip()
    if not s:
        return None, s
    if s[0] in marks:
        return marks[s[0]], s[1:].strip()
    m = re.match(r"(\d+)\s+(\d+)\s*/\s*(\d+)", s)
    if m:
        a, b, c = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if not c:
            return None, s
        return Fraction(a) + Fraction(b, c), s[m.end():].strip()
    m = re.match(r"(\d+)\s*/\s*(\d+)", s)
    if m:
        b, c = int(m.group(1)), int(m.group(2))
        if not c:
            return None, s
        return Fraction(b, c), s[m.end():].strip()
    m = re.match(r"(\d+\.\d+|\d+)", s)
    if m:
        return Fraction(m.group(1)), s[m.end():].strip()
    return None, s


def one(line):
    s = line.strip()
    if not s or s.startswith("#") or re.match(r"\d+\.\s+", s):
        return line.rstrip("\n")

    m = re.match(r"(?i)^(a|an)\s+", s)
    if m:
        qty = Fraction(1)
        rest = s[m.end():]
    else:
        qty, rest = take_num(s)
        if qty is None:
            return line.rstrip("\n")
        if rest[:1] in marks:
            qty = qty + marks[rest[0]]
            rest = rest[1:].strip()

    bits = rest.split(None, 1)
    if not bits:
        return line.rstrip("\n")
    u = bits[0].lower().rstrip(".")
    if u not in spoon:
        return line.rstrip("\n")
    name = bits[1].strip() if len(bits) > 1 else ""
    if name.lower().startswith("of "):
        name = name[3:]
    key = name.lower().split(",")[0].strip()
    if key not in cup:
        return line.rstrip("\n")

    grams = float(qty * spoon[u] * cup[key])
    if abs(grams - round(grams)) < 0.06:
        shown = str(int(round(grams)))
    else:
        shown = ("%.1f" % grams).rstrip("0").rstrip(".")
    return shown + " g " + name


def main():
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        print("usage: cup2g.py [file]")
        print("   or: cup2g.py 1 cup flour")
        return

    text = None
    if len(sys.argv) > 1:
        path = sys.argv[1]
        try:
            f = open(path)
            text = f.read()
            f.close()
        except IOError:
            text = " ".join(sys.argv[1:])
    else:
        text = sys.stdin.read()

    for line in text.splitlines():
        print(one(line))


if __name__ == "__main__":
    main()
