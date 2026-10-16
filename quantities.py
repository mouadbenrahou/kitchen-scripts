"""Shared helpers for reading and writing recipe quantities.

Understands whole numbers, decimals, fractions ("1/2"), mixed numbers
("1 1/2"), unicode fractions ("½", "1½"), "a"/"an", and ranges
("2-3", "2 to 3", "1–2").
"""
import re
from fractions import Fraction

FRACTIONS = {
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

_MIXED = re.compile(r"(\d+)\s+(\d+)\s*/\s*(\d+)")
_FRACTION = re.compile(r"(\d+)\s*/\s*(\d+)")
_NUMBER = re.compile(r"(\d+\.\d+|\d+)")
_ARTICLE = re.compile(r"(?i)^(a|an)\s+")
_RANGE = re.compile(r"(?:-|–|—|\bto\b)\s*")


def parse_number(s):
    """Read one number from the start of `s`.

    Returns (Fraction, rest) or (None, s) if `s` does not start with a number.
    """
    s = s.strip()
    if not s:
        return None, s
    if s[0] in FRACTIONS:
        return FRACTIONS[s[0]], s[1:].strip()
    m = _MIXED.match(s)
    if m:
        whole, num, den = (int(g) for g in m.groups())
        if den == 0:
            return None, s
        return Fraction(whole) + Fraction(num, den), s[m.end():].strip()
    m = _FRACTION.match(s)
    if m:
        num, den = int(m.group(1)), int(m.group(2))
        if den == 0:
            return None, s
        return Fraction(num, den), s[m.end():].strip()
    m = _NUMBER.match(s)
    if m:
        qty, rest = Fraction(m.group(1)), s[m.end():].strip()
        if rest[:1] in FRACTIONS:  # "1½"
            qty += FRACTIONS[rest[0]]
            rest = rest[1:].strip()
        return qty, rest
    return None, s


def parse_amount(s):
    """Read the amount at the start of an ingredient line.

    Returns (amount, rest) where amount is a Fraction, a (low, high) tuple
    for ranges, or None if the line does not start with an amount.
    """
    s = s.strip()
    m = _ARTICLE.match(s)
    if m:
        return Fraction(1), s[m.end():]
    qty, rest = parse_number(s)
    if qty is None:
        return None, s
    m = _RANGE.match(rest)
    if m:
        high, rest2 = parse_number(rest[m.end():])
        if high is not None:
            return (qty, high), rest2
    return qty, rest


def format_quantity(q, max_denominator=8):
    """Show a quantity the way a cook writes it: 2, 1/2, 2 1/4."""
    q = Fraction(q).limit_denominator(max_denominator)
    if q <= 0:
        return "0"
    if q.denominator == 1:
        return str(q.numerator)
    whole, num = divmod(q.numerator, q.denominator)
    if whole:
        return "%d %d/%d" % (whole, num, q.denominator)
    return "%d/%d" % (num, q.denominator)


def read_text(path):
    """Read a recipe file as UTF-8 (so ½ and ¼ work on every OS)."""
    with open(path, encoding="utf-8") as f:
        return f.read()
