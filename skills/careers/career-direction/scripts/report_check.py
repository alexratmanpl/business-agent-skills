#!/usr/bin/env python3
"""Check a filled direction report before it is handed over.

Reads the report-data block out of the page and fails on what makes a direction report
worthless or unsafe to forward. Most of it is invisible in the page: a missing field draws an
empty chip, an empty cell or a default colour, so the report looks finished, and a wrong type
costs the section it is in. Every problem exits 1, and one about a field names its path.

  data      the block is not JSON, or holds <script or </script, which can cut the page off
  shape     a wrong type, or a key the page does not read, such as "gaps[0].weigth"
  required  a claim with no source; a forecast with nothing dated behind it or nothing
            that could prove it wrong; demand asserted and not counted; a family with no
            pay range, no entry bar, or no mark saying whether one source backs it or two;
            a gap with no weight; no record of what could not be confirmed; a row with
            nothing in it. A reading of a person also needs a verdict on each family and a
            "when" on each position
  reading   a verdict, odds, a "when", a worth, clocks, a shape, habits or a thread in a report
            with nothing about a person in it, which has nobody for them to judge
  values    a tone, weight, ageing, status or other word the page does not recognise; a count
            that is not a whole number of 0 or more; odds that are not percentages; a position
            in a family that is not on the list, or that closes on no date
  track     a step outside the twelve-column track, or on columns another step in its lane holds
  page      a script that no longer matches the policy that lets it run, which a browser then
            refuses, so the page is blank; a second copy of the data (in any element that has
            its id), the script or the policy, which a browser may read where this checker
            read the first
  privacy   an email address, a phone number, a personal profile link, a street address,
            a surname beside the first name. These are the common shapes and no more: a
            surname written first goes unseen, and a posting number of nine digits or more
            reads as a phone number. Sums are not phone numbers: a currency beside digits,
            or a range of grouped thousands, reads as pay

It cannot tell evidence that is all self-assessment from evidence that is sourced,
because marking a source as their own is a legitimate answer. Count those by hand.
Length is reported and does not fail: a long field is a judgement, a missing one is not. A
label that still says the example is invented is reported the same way, because only whoever
reads the report can say whether it is true.
"""

import argparse
import base64
import hashlib
import json
import math
import re
import sys
import unicodedata

# Values the page colours. Anything else still renders, as a plain grey chip with no
# meaning, which is worse than an error because it looks deliberate. Reported rather
# than corrected: the fix depends on what was meant.
TONES = {"good", "amb", "bad", "acc", "plain"}
ENUMS = {
    "habits[].tone": {"good", "amb", "bad"},
    "thread.events[].kind": {"turn", "build", "test"},
    "thread.events[].verdict": {"confirms", "fails", "start"},
    "gaps[].weight": {"decides", "slows", "closes doors"},
    "market.families[].ages": {"well", "mixed", "badly"},
    "market.families[].verdictTone": TONES,
    "market.families[].sourcing": {"confirmed", "unconfirmed"},
    "market.positions[].status": {"open", "closes", "recurs", "closed"},
    "market.positions[].evidence": {"strong", "some", "thin"},
    "market.positions[].when": {"now", "build", "later"},
    "horizon.clocks.lanes[].steps[].tone": TONES,
}

# What the page reads, and what it expects to find there. A dict is an object read by
# key, a list holds many of its one entry, a tuple is a list of fixed length, and T, W
# and C are text, a whole number and a count. A wrong type costs the section it is in,
# which the page names in a banner. A mistyped key is quieter: gaps[0].weigth reads as an
# empty weight, the chip renders grey, and nothing says why. The page reads null as
# absent, and so does the checker.
T, W, C = "text", "whole number", "count"
SCHEMA = {
    "meta": {"name": T, "date": T, "eyebrow": T, "lede": T, "footer": T},
    "shape": [T],
    "evidence": [{"title": T, "text": T, "src": T}],
    "selling": [{"title": T, "text": T}],
    "habits": [{"label": T, "tone": T, "text": T}],
    "thread": {
        "intro": T, "outro": T,
        "events": [{"year": T, "kind": T, "title": T, "detail": T,
                    "verdict": T, "verdictText": T}],
    },
    "gaps": [{"gap": T, "weight": T, "evidence": T, "fix": T, "cost": T}],
    "constraints": {"hard": [T], "soft": [T]},
    "decisions": [{"label": T, "text": T}],
    "corrections": [T],
    "market": {
        "asOf": T, "skipped": T,
        "lines": [{"text": T, "src": T}],
        "skills": [{"name": T, "countN": C, "note": T}],
        "families": [{"name": T, "buys": T, "why": T, "demandN": C, "demandNote": T,
                      "pay": T, "entryBar": T, "sourcing": T, "trend": T, "ages": T,
                      "verdict": T, "verdictTone": T, "note": T}],
        "positions": [{"employer": T, "title": T, "loc": T, "family": T, "status": T,
                       "statusDate": T, "evidence": T, "oddsNow": T, "oddsAfter": T,
                       "when": T, "note": T}],
    },
    "horizon": {
        "note": T, "agesWell": [T], "agesBadly": [T],
        "shifts": [{"title": T, "mechanism": T, "alreadyVisible": T, "src": T,
                    "falsifier": T, "worthTo": T}],
        "clocks": {"title": T, "axis": [T],
                   "lanes": [{"name": T, "sub": T,
                              "steps": [{"at": W, "span": W, "label": T,
                                         "detail": T, "tone": T}]}]},
        "calendar": [{"date": T, "what": T}],
    },
    "glossary": [(T, T)],
    "sources": {"produced": [T], "checked": [T], "notConfirmed": [T]},
}

# What a row has to carry, by the path of the row. Each of these is drawn as an empty
# chip, an empty cell or a default colour when it is missing, and none of that is an error
# to the page, so the report would look finished. A key may be a path from the row, which
# is how the report as a whole is held to sources.notConfirmed: an empty list renders as
# nothing, the same silence as leaving it out.
REQUIRED = {
    "": ("sources.notConfirmed",),
    "evidence[]": ("title", "text", "src"),
    "selling[]": ("title", "text"),
    "habits[]": ("label", "tone", "text"),
    "thread.events[]": ("year", "kind", "title"),
    "gaps[]": ("gap", "weight", "evidence", "fix"),
    "decisions[]": ("label", "text"),
    "market.lines[]": ("text", "src"),
    "market.skills[]": ("name", "countN"),
    "market.families[]": ("name", "buys", "why", "demandN", "demandNote", "pay", "entryBar",
                          "sourcing", "trend", "ages"),
    "market.positions[]": ("employer", "title", "family", "status", "evidence"),
    "horizon.shifts[]": ("title", "alreadyVisible", "src", "falsifier"),
    "horizon.clocks.lanes[]": ("name",),
    "horizon.clocks.lanes[].steps[]": ("at", "span", "label"),
    "horizon.calendar[]": ("date", "what"),
}
# What only a reading of a person can fill. A report that is the market only has nobody to
# judge, so it carries no verdict and no "when", and asking for them sends the run to invent
# a person. A report holding any of PERSON is a reading, and these are required in it.
ABOUT_THEM = {"market.families[]": ("verdict", "verdictTone"), "market.positions[]": ("when",)}
PERSON = ("evidence", "selling", "gaps")
# The other way round: a report with none of PERSON in it has nobody for these to judge, and a run
# that wrote them has invented somebody.
READING_ONLY = {"shape[]", "habits[]", "thread", "horizon.clocks", "horizon.shifts[].worthTo",
                "market.families[].verdict", "market.families[].verdictTone",
                "market.positions[].when", "market.positions[].oddsNow",
                "market.positions[].oddsAfter"}
# Why a field matters, for the ones where the reason is not obvious from the name.
HINTS = {
    "src": "Write where it came from, or mark it as their own account",
    "falsifier": "Without something that would prove it wrong it is a prediction, not a reading",
    "alreadyVisible": "Name the dated thing it can be seen in today",
    "demandN": "It is how many open positions were counted, as a number",
    "demandNote": "Put the source and the date of the count in it",
    "pay": "A family with no ceiling cannot be priced against anybody's floor",
    "entryBar": "A family priced only at its ceiling reads as reachable when it is not",
    "sourcing": "One source is a lead, not a finding, and the report has to say which this is",
    "trend": "The page draws the column, so where nothing is known write not established",
    "family": "Write the name of one of the families, so the position can be tied to it",
    "weight": "A gap with no weight cannot be acted on",
    "ages": "The chart cannot place a family without it",
    "tone": "Without it the chip is grey and says nothing",
    "notConfirmed": "Say what could not be established, so a silence reads differently "
                    "from an absence",
}

# Things that identify a person rather than describe them. The report is a file that gets
# forwarded, and a phone number in it travels with the file. These are the common shapes
# and nothing more: a backstop for the rule that the report carries no contact details,
# not a replacement for it. A job board, a company page on LinkedIn or an organisation's
# repository is a source and is not flagged; a personal profile is, and so is a company's
# own page on X or GitHub, which looks like one (github.com/orgs/<name> is how GitHub
# writes an organisation).
CAPITAL = "A-ZÀ-ÖØ-ÞĂĆČĎĐĚŁŃŇŐŘŚŠŤŮŰŹŻŽȘȚ"  # Latin capitals, with the Polish and Czech ones
NAME = rf"[{CAPITAL}][\w'’-]*"
# A surname comes after one of these, in lower case, as often as not: Jane van Dijk, Jane de la Cruz,
# and some are written close up: Jane deLeon.
PARTICLES = "van|von|de|der|den|da|di|del|la|le|du|dos|ter|ten|los|las"
STREET_WORD = ("Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Drive|Dr|Boulevard|Blvd|Close"
               "|Crescent|Terrace")
ADDRESSES = [
    # 221B Baker Street
    rf"(?<![\w-])\d{{1,4}}[A-Za-z]?\s+(?:{NAME}\s+){{1,3}}(?:{STREET_WORD})\b",
    # 5 rue de Rivoli
    r"(?<![\w-])\d{1,4}[A-Za-z]?,?\s+(?i:rue)\s+\w",
    # ul. Piękna 5, Via Roma 12
    rf"(?<![\w-])(?:(?i:ul\.|ulica|ulice|aleja|plac|nám\.|náměstí)"
    rf"|Via|Calle|Carrer|Piazza|Rua|Avenida)\s+(?:{NAME}\s+){{1,3}}\d{{1,4}}[A-Za-z]?\b",
    # Hauptstr. 5, Kerkstraat 3, Vinohradská 12
    rf"(?<![\w-])[{CAPITAL}]\w*(?:straße|strasse|str\.?|straat|gasse|laan|allee|platz|ská"
    r"|\w{3}ova)\s+\d{1,4}[A-Za-z]?\b",
]
PROFILES = (r"(?<![\w-])(?:linkedin\.com/(?:in|pub)/|(?:x|twitter)\.com/\w|xing\.com/profile/"
            r"|t\.me/\w|wa\.me/\d|github\.com/[\w-]+/?(?![\w/-]))")
# Every part of these two can be read one way only: a run of digits is one group and a start
# has to sit at the edge of its word. Otherwise one long field takes the checker an afternoon.
# The edge is not a letter, a digit, a slash or an equals sign (an id in an address), a hyphen or a
# comma (job boards put an id after one). A dot is not on the list: a label is often written
# Tel.603 123 456, with the number starting where the label ends.
EDGE = r"(?<![\w/=,-])"
PHONE = re.compile(rf"{EDGE}(?:\(\d{{1,5}}\)|\d+)"
                   r"(?:[ .-]?\(\d{1,5}\)|[ .-]\d{2,}|(?<=\))\d+)*(?!\w)")
EMAIL = re.compile(r"(?<![\w.+-])[\w.+-]+@[\w-]+\.[\w.]{2,}")
# A sum is not a number to ring. Digits with a currency beside them, before or after, are a sum
# however they are grouped, and so is a range of two numbers in grouped thousands with no currency
# at all: 55 000-75 000 is as long as a phone number and reads as a sum to anyone. A number is
# bounded, so one long field of digits and spaces cannot take the checker an afternoon.
MONEY = "€$£¥₹₺₽₩₴"
CODES = ("CZK|PLN|EUR|USD|GBP|CHF|SEK|NOK|DKK|HUF|RON|CAD|AUD|JPY|INR|CNY|AED|SGD|HKD|NZD|ZAR|BRL"
         "|MXN|TRY|ILS|UAH|BGN|RSD|ISK|KRW|RUB|Kč|zł|Ft|lei|kr")
SIGN = rf"(?:[{MONEY}]|(?<![^\W\d_])(?:{CODES}))"
AMOUNT = r"\d(?:[ .,]?\d){0,20}"
THOUSANDS = r"\d{1,3}(?:[ .]\d{3}){1,6}"
SUMS = re.compile(
    rf"{SIGN}\s?{AMOUNT}(?:\s?-\s?{AMOUNT})?"
    rf"|{EDGE}{AMOUNT}(?:\s?-\s?{AMOUNT})?\s?(?:[{MONEY}]|(?:{CODES})(?!\w))"
    rf"|{EDGE}{THOUSANDS}-{THOUSANDS}(?!\w)")


# A date, or a run of years such as the reports that were read, is taken out before the digits are
# counted: the hour of a time beside a date would otherwise join its digits into a run as long as a
# phone number. Only what is one is taken out. A month is 01 to 12 and a day 01 to 31, and a number
# that is not a year or a run of them stays as it is.
DATES = re.compile(r"(?<!\d)(?:(?:19|20)\d\d-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01])"
                   r"|(?:0?[1-9]|[12]\d|3[01])\.(?:0?[1-9]|1[0-2])\.(?:19|20)\d\d)(?!\d)")
YEARS = re.compile(r"(?<![\d-])(?:19|20)\d{2}(?:[ .-](?:19|20)\d{2})+(?![\d-])")


def blanked(pattern, text):
    """The text with what the pattern finds turned to spaces, so every other place stays put."""
    return pattern.sub(lambda found: " " * len(found.group()), text)


def find_phone(text):
    """Where digits in groups, nine to fifteen of them, are, once the sums, the dates and the
    years are taken out, or None. A date has eight, a spaced dash breaks a price range, and a
    year or a count is a single group."""
    left = blanked(YEARS, blanked(DATES, blanked(SUMS, text)))
    for found in PHONE.finditer(left):
        if 9 <= len(re.sub(r"\D", "", found.group())) <= 15:
            return found.span()
    return None


# What draws nothing and is not a format character: the Hangul fillers, which Unicode leaves in
# the middle of a word (the fullwidth and halfwidth ones fold to U+1160 first), and a Braille
# pattern with no dots.
BLANK_GLYPHS = {"\u115f", "\u1160", "\u2800"}


def capped(text, keep=32):
    """The text with a run of combining marks cut to `keep`. CPython puts a run of them in order
    one mark at a time, so a long one takes the square of its length, and nobody's text holds more
    than a few in a row."""
    kept, run = [], 0
    for char in text:
        run = run + 1 if unicodedata.combining(char) else 0
        if run <= keep:
            kept.append(char)
    return "".join(kept)


def fold(text):
    """The text as a reader sees it, which is what the patterns have to read. A fullwidth @ folds
    to the plain one. Whatever a browser shows as a space is a space, a line break and a tab
    included, a run of them is one space, as a browser draws it, and every dash is a hyphen. What
    draws nothing goes: format characters, controls, the marks that sit on the letter before
    them, and the fillers. A copied phone number is often set in no-break or thin spaces, and a
    pasted address can hold a zero-width character anywhere in it."""
    shown = []
    for char in unicodedata.normalize("NFKC", capped(text)):
        kind = unicodedata.category(char)
        if char.isspace():   # every space separator, and the tab and the line break
            shown.append(" ")
        elif kind in ("Cf", "Cc", "Mn", "Me") or char in BLANK_GLYPHS:
            continue
        else:
            shown.append("-" if kind == "Pd" or char == "\u2212" else char)
    return re.sub(" {2,}", " ", "".join(shown))


def span_of(pattern):
    def find(text):
        found = pattern.search(text)
        return found.span() if found else None
    return find


IDENTIFIERS = [
    (span_of(EMAIL), "an email address"),
    (find_phone, "a phone number"),
    (span_of(re.compile(PROFILES, re.I)), "a personal profile link"),
    (span_of(re.compile("|".join(ADDRESSES))), "a street address"),
]


def walk(node, path=""):
    """Yield (path, value) for every string, and (path, dict) for every mapping."""
    if isinstance(node, dict):
        yield path, node
        for key, value in node.items():
            yield from walk(value, f"{path}.{key}" if path else key)
    elif isinstance(node, list):
        for i, value in enumerate(node):
            yield from walk(value, f"{path}[{i}]")
    elif isinstance(node, str):
        yield path, node


def generic(path):
    """market.families[2].ages -> market.families[].ages"""
    return re.sub(r"\[\d+\]", "[]", path)


def describe(value):
    if isinstance(value, bool):
        return "true or false"
    named = {dict: "an object", list: "a list", str: "text", type(None): "null"}.get(type(value))
    return named or str(value)[:24]


# A browser ends the data block at the first end tag, in any case and followed by a space, a
# slash or a bracket, and it reads on from there as markup. A start tag after a comment opener
# hides that end tag, so the block runs on into the page. So the block is parsed as JSON first,
# which does not care what a string holds, and what the strings hold is looked at after. A start
# tag is refused on its own: nothing a report says needs one. JSON skips four characters of
# whitespace and an end tag may be followed by one of five, which is fewer than Python's \s: a
# no-break space at the edge of the block is not skipped, and one in the end tag does not end it.
START = re.compile(r'<script[^>]{0,300}\bid="report-data"[^>]{0,300}>', re.I)
BLANKS = re.compile(r"[ \t\n\r]*")
END = re.compile(r"[ \t\n\r]*</script[\t\n\f\r />]", re.I)
MARKUP = re.compile(r"<(?:/?script)", re.I)


TOO_DEEP = "the report data nests far deeper than a report does"


def refuse_constant(name):
    raise ValueError(f"{name} is not valid JSON")


def read_report(filename):
    """The data, the page it came from, and what stopped it being read."""
    try:
        text = open(filename, encoding="utf-8").read()
    except (OSError, ValueError) as error:
        return None, "", [f"cannot read {filename}: {error}"]
    start = START.search(text)
    if not start:
        return None, text, ["no <script id=\"report-data\"> block in this file"]
    first = BLANKS.match(text, start.end()).end()
    try:
        data, last = json.JSONDecoder(parse_constant=refuse_constant).raw_decode(text, first)
        if not END.match(text, last):
            raise json.JSONDecodeError("Extra data", text, last)
        if isinstance(data, dict):
            data = without_nulls(data)
    except ValueError as error:   # bad JSON, a constant like NaN, or an integer too long to read
        return None, text, [f"the report data is not valid JSON: {error}. "
                            "JSON needs double quotes on every key and string, no "
                            "trailing commas and no comments"]
    except RecursionError:
        return None, text, [TOO_DEEP]
    if MARKUP.search(text, first, last):
        return None, text, ["the report data holds <script or </script, which a browser reads as "
                            "markup and which can cut the page off. Write that < as \\u003c"]
    if not isinstance(data, dict):
        return None, text, [f"the report data is {describe(data)}, and has to be an object"]
    return data, text, []


# The policy names the one script that may run, by its digest, so text that gets out of the data
# runs nothing. A browser refuses a script that no longer matches, and the page is then blank with
# nothing on it to say why. A page is read as a browser reads it: a carriage return and a line feed
# are one line feed.
RENDERER = re.compile(r"<script>(.*?)</script>", re.S)
SCRIPT_START = re.compile(r"<script\b", re.I)
HOLDER = re.compile(r"""(?<![\w-])id\s*=\s*["']?report-data(?![\w-])""", re.I)
# A browser decodes the character references in an attribute's value, so id="report&#45;data" is the
# data's id. Only a numeric one can spell it. A code point has six hex digits or seven decimal ones at
# most, and a number past the last one is no character.
REFERENCE = re.compile(r"&#(?:[xX]0*([0-9a-fA-F]{1,6})|0*([0-9]{1,7}));?")
# A meta tag is found by how it opens and looked at after. A pattern that asked for the policy in
# the same breath ran on from every <meta in the data to the next >, and back again.
META = re.compile(r"<meta\b[^>]*>", re.I)
IS_POLICY = re.compile(r'\bhttp-equiv="Content-Security-Policy"', re.I)
CONTENT = re.compile(r'\bcontent="([^"]*)"', re.I)
SCRIPT_SRC = re.compile(r"(?:^|;)\s*script-src\s+([^;]*)")


def decoded(text):
    """The text with its numeric character references turned into the characters they name."""
    def character(found):
        number = int(found.group(1), 16) if found.group(1) else int(found.group(2))
        return chr(number) if number <= 0x10FFFF else found.group()
    return REFERENCE.sub(character, text)


def check_page(text):
    script = RENDERER.search(text)
    if not script:
        return ["the page has no script of its own, so nothing draws the report"]
    # This checker reads the first copy of each of the three things a browser runs, and a browser
    # reads what is live, which a comment or a template can put somewhere else. The data is found
    # by its id, which any element can carry, and a browser takes the first element that does, with
    # its character references decoded.
    starts = len(SCRIPT_START.findall(text))
    if starts > 2:
        return [f"the page has {starts} <script tags, and a browser runs two: the data and the "
                "script that draws it. A copy of either, in a comment too, can stand in for the "
                "live one while this checker reads it instead"]
    holders = len(HOLDER.findall(decoded(text)))
    if holders != 1:
        return [f"the page has {holders} places that write id=report-data, and has to have one. "
                "A browser reads the data from the first element with that id, which need not be "
                "the block this checker read"]
    policies = [tag for tag in META.findall(text) if IS_POLICY.search(tag)]
    if len(policies) > 1:
        return [f"the page has {len(policies)} Content-Security-Policy tags, and has to have one. "
                "A browser applies them all, and this checker read the first"]
    digest = base64.b64encode(hashlib.sha256(script.group(1).encode("utf-8")).digest()).decode()
    content = CONTENT.search(policies[0]) if policies else None
    rule = SCRIPT_SRC.search(content.group(1)) if content else None
    if not rule:
        return [f"the page has no Content-Security-Policy with a script-src. Without one, text "
                f"that gets out of the data runs as script. Put script-src 'sha256-{digest}' in it"]
    if rule.group(1).split() != [f"'sha256-{digest}'"]:
        return [f"the page's script-src is '{rule.group(1).strip()}', and has to be "
                f"'sha256-{digest}' and nothing else. A browser runs the script its policy names "
                "and no other, so a page whose script was edited is blank, and a policy that "
                "names more lets more run"]
    return []


def without_nulls(node):
    if isinstance(node, dict):
        return {key: without_nulls(value) for key, value in node.items() if value is not None}
    if isinstance(node, list):
        return [without_nulls(value) for value in node]
    return node


def is_number(value):
    """A number the page can place: not true or false, and not past what a browser reads as
    Infinity, which 1e999 is."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    try:
        return math.isfinite(float(value))
    except OverflowError:
        return False


def is_whole(value):
    """3 and 3.0 are the same number to a browser, so they are to the checker."""
    return is_number(value) and float(value).is_integer()


FITS = {T: lambda value: isinstance(value, str), W: is_whole,
        C: lambda value: is_whole(value) and value >= 0}
WANTS = {T: "text", W: "a whole number", C: "a whole number, 0 or more,"}


def join(path, key):
    return f"{path}.{key}" if path else key


def check_shape(node, spec, path=""):
    """Everywhere the data is not what the page reads: a wrong type, or a key it ignores."""
    here = path or "the report"
    if isinstance(spec, dict):
        if not isinstance(node, dict):
            return [f"{here} is {describe(node)}; the page reads an object there"]
        problems = []
        for key, value in node.items():
            if key in spec:
                problems += check_shape(value, spec[key], join(path, key))
            else:
                problems.append(f"{join(path, key)} is not a key the page reads, so it "
                                f"renders nothing. Expected one of: {', '.join(sorted(spec))}")
        return problems
    if isinstance(spec, list):
        if not isinstance(node, list):
            return [f"{here} is {describe(node)}; the page reads a list there"]
        return [problem for i, item in enumerate(node)
                for problem in check_shape(item, spec[0], f"{path}[{i}]")]
    if isinstance(spec, tuple):
        if not (isinstance(node, list) and len(node) == len(spec)):
            return [f"{here} has to be a list of {len(spec)}, such as [term, meaning]"]
        return [problem for i, (item, kind) in enumerate(zip(node, spec))
                for problem in check_shape(item, kind, f"{path}[{i}]")]
    return [] if FITS[spec](node) else [
        f"{here} is {describe(node)}; the page needs {WANTS[spec]} there"]


def dig(node, *path):
    """The value at a path, or None where any step of it is missing or not an object."""
    for key in path:
        node = node.get(key) if isinstance(node, dict) else None
    return node


def rows(node, *path):
    """(index, object) for each object in the list at a path. Anything else yields
    none: check_shape has already said what is wrong with it."""
    items = dig(node, *path)
    if not isinstance(items, list):
        return []
    return [(i, item) for i, item in enumerate(items) if isinstance(item, dict)]


NAMES = ("title", "name", "gap", "label", "employer", "date")


def blank(value):
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, list):
        return all(blank(item) for item in value)
    if isinstance(value, dict):
        return all(blank(item) for item in value.values())
    return value is None


def is_reading(data):
    """A reading holds something about a person. A row with nothing in it is not that: it is an
    empty card, and check_required says so."""
    return any(not blank(data.get(key)) for key in PERSON)


def check_required(data):
    problems = []
    reading = is_reading(data)
    for path, row in walk(data):
        if not isinstance(row, dict):
            continue
        if path and generic(path) in REQUIRED and blank(row):
            problems.append(f"{path} is an empty row, which the page draws as an empty card. "
                            "Delete it")
            continue
        for key in REQUIRED.get(generic(path), ()) + (ABOUT_THEM.get(generic(path), ())
                                                       if reading else ()):
            if not blank(dig(row, *key.split("."))):
                continue
            name = next((f" ('{row[k]}')" for k in NAMES
                         if isinstance(row.get(k), str) and row[k].strip()), "")
            hint = HINTS.get(key.split(".")[-1])
            problems.append(f"{join(path, key)} is missing or empty{name}."
                            + (f" {hint}" if hint else ""))
    return problems


def check_reading(data):
    """Nothing in the report is about a person, so nothing in it may judge one."""
    if is_reading(data):
        return []
    return [f"{path} judges somebody, and nothing in the report is about a person: it has no "
            "evidence, selling or gaps. Cut it, or add the reading it comes from"
            for path, value in walk(data) if generic(path) in READING_ONLY and not blank(value)]


def around(text, span):
    """The words a match sits in, out to the spaces on each side, so whoever fixes it finds it."""
    start, end = span
    while start and not text[start - 1].isspace():
        start -= 1
    while end < len(text) and not text[end].isspace():
        end += 1
    return text[start:end][:80]


def folded(data):
    """(path, what a reader sees) for every string in the report. Folding is the costly step, so
    it is done once and each check reads the result."""
    return [(path, fold(value)) for path, value in walk(data) if isinstance(value, str)]


def check_identifiers(seen):
    problems = []
    for path, text in seen:
        found = []
        for find, what in IDENTIFIERS:
            span = find(text)
            if span:
                found.append(f"{what} ('{around(text, span)}')")
        if found:
            problems.append(f"{path} contains what looks like {', '.join(found)}. The report "
                            "should carry nothing that identifies them. If it is something else, "
                            "reword it so that it cannot be read as one")
    return problems


def check_clocks(data):
    """at and span are columns on a twelve-column track. Out of range, a step is clamped and
    silently lands somewhere it was not meant to. Steps in a lane follow one another: the page
    draws one that starts inside another on a second row, and links it with an arrow that says
    "then" over a picture that says "at once"."""
    problems = []
    for i, lane in rows(data, "horizon", "clocks", "lanes"):
        placed = []
        for j, step in rows(lane, "steps"):
            at, span, label = step.get("at"), step.get("span"), step.get("label", "?")
            if not (is_whole(at) and is_whole(span)):
                continue
            if at < 0 or span < 1 or at + span > 12:
                problems.append(
                    f"horizon.clocks.lanes[{i}].steps[{j}] '{label}' runs from column {at} for "
                    f"{span}, outside the twelve-column track. It will be clamped and land wrong")
                continue
            for k, other_at, other_span, other_label in placed:
                if at < other_at + other_span and other_at < at + span:
                    problems.append(
                        f"horizon.clocks.lanes[{i}].steps[{j}] '{label}' shares columns with "
                        f"steps[{k}] '{other_label}'. Steps in a lane follow one another: move "
                        "one, or give it a lane of its own")
                    break
            placed.append((j, at, span, label))
    return problems


# What the page ties together by hand. A position names its family by writing the name out, and a
# name that differs by a letter is a family that is not there. The date a position closes on is
# the one thing a reader needs of it. Odds are what the page sorts on, so they are percentages.
ODDS = re.compile(r"[<>~\u2248]?\s*\d+(?:\s*[-\u2013]\s*\d+)?\s*%")


def check_positions(data):
    problems = []
    names = {row["name"] for _, row in rows(data, "market", "families")
             if isinstance(row.get("name"), str)}
    for i, row in rows(data, "market", "positions"):
        here = f"market.positions[{i}]"
        family = row.get("family")
        if isinstance(family, str) and family.strip() and family not in names:
            listed = (", ".join(f"'{name}'" for name in sorted(names))
                      or "none, there are no families")
            problems.append(f"{here}.family is '{family}', which is not the name of a family on "
                            f"the list. Write one of: {listed}. A posting that fits none goes in "
                            "market.lines")
        if row.get("status") == "closes" and blank(row.get("statusDate")):
            problems.append(f"{here}.statusDate is missing or empty. A position that closes needs "
                            "the date it closes on")
        for key in ("oddsNow", "oddsAfter"):
            odds = row.get(key)
            if isinstance(odds, str) and odds.strip() and not ODDS.fullmatch(odds.strip()):
                problems.append(f"{here}.{key} is '{odds}'. Odds are percentages, such as 15% "
                                "or 10-20%")
    return problems


def check_labels(data):
    """The example says it is invented in two places, and a real person's report replaces both."""
    return [f"{path} still says the example is invented. If that line is the example's own, "
            "replace it with one that is true of this report"
            for path in ("meta.eyebrow", "meta.footer")
            if re.search(r"\binvented\b", str(dig(data, *path.split(".")) or ""), re.I)]


def check_enums(data):
    problems = []
    for path, value in walk(data):
        allowed = ENUMS.get(generic(path))
        if allowed and isinstance(value, str) and value.strip() and value not in allowed:
            problems.append(f"{path} is '{value}', which the page does not colour. "
                            f"Use one of: {', '.join(sorted(allowed))}")
    return problems


def check_length(data, limit, ceiling):
    """A direction report is read by someone deciding, not studying. Long fields
    are the failure mode: the report turns into prose and stops being scannable.
    The whole-report figure is the backstop, and says which sections hold the words."""
    notes = []
    total = 0
    by_section = {}
    for path, value in walk(data):
        if not isinstance(value, str):
            continue
        words = len(value.split())
        total += words
        section = re.split(r"[.\[]", path, maxsplit=1)[0]
        by_section[section] = by_section.get(section, 0) + words
        if words > limit:
            notes.append(f"{path} runs to {words} words. Over {limit} it reads as prose; "
                         "split it or cut it")
    if total > ceiling:
        where = ", ".join(f"{name} {words}" for name, words in
                          sorted(by_section.items(), key=lambda item: (-item[1], item[0])) if words)
        notes.append(f"the whole report runs to {total} words, over {ceiling}. By section: {where}")
    return notes, total


def check_name(data, seen):
    """Initials are two tokens and name nobody; a full name is two tokens and names
    somebody. Counting tokens alone rejected the more private of the two. A first name
    followed by a capitalised word anywhere else is a surname, which the check can see
    only because it knows the first name: it cannot tell initials from a surname. A
    surname written first, before the name, goes unseen."""
    name = fold(str(dig(data, "meta", "name") or "")).strip()
    parts = name.split()
    initials = bool(parts) and all(len(p.rstrip(".")) <= 1 for p in parts)
    if initials or not parts:
        return []
    if len(parts) > 1:
        return [f"meta.name is '{name}'. A first name or initials is enough, and the "
                "report travels better without a full one"]
    surname = re.compile(rf"\b{re.escape(name)}\s+(?:(?:{PARTICLES})\s*){{0,2}}{NAME}")
    return [f"{path} gives {name} a surname: '{found.group()}'. A first name is enough"
            for path, text in seen
            for found in [surname.search(text)] if found]


def plain(text):
    """What the data put into a message, with control characters shown rather than sent to the
    terminal, where an escape sequence is an instruction, and a line break, which is more than a
    line feed, would start a line of the checker's own."""
    return "".join(f"\\u{ord(c):04x}"
                   if unicodedata.category(c) in ("Cc", "Cf", "Cs", "Zl", "Zp") else c
                   for c in text)


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("report", help="the filled direction-report.html")
    parser.add_argument("--max-field-words", type=int, default=45)
    parser.add_argument("--max-words", type=int, default=1500)
    args = parser.parse_args()

    data, text, problems = read_report(args.report)
    if data is None:
        for problem in problems:
            print(f"  {plain(problem)}", file=sys.stderr)
        return 1

    try:
        seen = folded(data)
        problems = (check_shape(data, SCHEMA) + check_required(data) + check_enums(data)
                    + check_reading(data) + check_identifiers(seen) + check_clocks(data)
                    + check_positions(data) + check_name(data, seen) + check_page(text))
        notes, total = check_length(data, args.max_field_words, args.max_words)
        notes += check_labels(data)
    except RecursionError:   # nesting the parser read, in a place no field of a report nests
        print(f"  {TOO_DEEP}", file=sys.stderr)
        return 1

    if problems:
        print(f"{len(problems)} problem(s) to fix:\n", file=sys.stderr)
        for problem in problems:
            print(f"  {plain(problem)}", file=sys.stderr)
        print("", file=sys.stderr)

    if notes:
        print(f"{len(notes)} thing(s) to look at:\n")
        for note in notes:
            print(f"  {plain(note)}")
        print("")

    sections = [k for k in SCHEMA if data.get(k)]
    print(f"{len(sections)} section(s) filled: {', '.join(sorted(sections))}")
    print(f"{total} words in total, against a ceiling of {args.max_words}.")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
