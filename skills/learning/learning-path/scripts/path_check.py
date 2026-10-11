#!/usr/bin/env python3
"""Check a learning plan before it is handed over.

Reads a plan written in the format references/plan.md sets out, and enforces
the rules stated there. Each one guards against a defect that makes a learning
path worse than none, and each is invisible in a plan that looks finished:

  - a fact with no source or no date, or a source read too long ago to trust
  - a standard nobody verified, or a goal nobody could check
  - a milestone that cites nothing, or rests only on an unconfirmed lead
  - an outcome that is an activity rather than something anyone can observe
  - a budget verdict the evidence or the milestones do not add up to
  - a NO PATH plan that hands out a to-do list anyway
  - a fact review whose counts do not match the table it reviewed
  - template text left where the plan's own words go ('<why>', 'https://...', '...' after a
    label); the first four different ones are named

What it cannot check: whether a quote is really on the page, whether two
sources are really independent, and whether a claim says no more than its
quote. That is the fact review in references/review.md. It also reads wording
by its shape, not its meaning, and reads only some sections for it. A vague
outcome, condition or to-do list can pass.

A gate, not a checklist. Problems exit 1. Wording that is usually vague but has
real exceptions, and things worth a second look, are printed and exit 0. An
unreadable file or a bad argument exits 2. A date one day ahead is accepted,
since the plan and the machine checking it may sit in different time zones.

Hours may be written 1.5 or 1,5. In a total, a comma before three digits is
thousands, so 2,200 is two thousand two hundred. Hours a week takes no thousands.

In Hours a week the first figure counts and what follows it is commentary. A figure is one
number, or two joined by a hyphen, an en or em dash, '--' or 'to' ('5-6'). The budget uses the
low end of a range. Commentary may name a day after a bare number, or after hours and a week
(the hour unit comes straight after the figure). A number is bare when a clause ends straight
after it: a comma, semicolon, round bracket, en or em dash, a hyphen or '--' with a space on
each side, or a full stop or colon and a space. A time unit that opens the next clause belongs
to the number, which is then not bare. A day anywhere else is hours per day, and the field is
refused. The figure is read as hours whatever unit follows it, so write 1.5 hours, not 90
minutes. For example, these pass:
    5 (about an hour a day)
    5 hours a week -- about an hour a day
and these are refused:
    1 hour a day
    5 - 1 hour a day
    30 (minutes a day)
    90 minutes a week (15 minutes a day)
    5 hours (about an hour a day)
    5 solid hours a week (about an hour a day)
    5 days a week, 30 minutes a day
    5 [about an hour a day]
    5-about an hour a day

Usage: path_check.py learning-path-TOPIC.md [--today YYYY-MM-DD] [--max-age-days 30]
"""

import argparse
import datetime
import re
import sys

VERDICTS = {"PATH", "NO PATH"}
BUDGETS = {"fits", "tight", "unknown"}
TIERS = {"1", "2", "3", "4", "learner"}
STATUSES = {"confirmed", "unconfirmed"}
GOAL_FIELDS = ["Performance", "Standard", "Conditions", "Deadline",
               "Hours a week", "Starting point", "Use"]
# The three lines that make a goal checkable by someone else. With any of them
# missing there is nothing to aim at, and the only honest verdict is NO PATH.
DEFINING = ["Performance", "Standard", "Conditions"]
EMPTY_VALUES = {"", "missing", "none", "n/a", "na", "tbd", "unknown", "-", "?"}
MILESTONE_FIELDS = ["Outcome", "Practice", "Check", "Evidence", "Time", "Resources"]
REQUIRED_MILESTONE_FIELDS = ["Outcome", "Practice", "Check", "Evidence", "Time"]
CHECKS_LINES = ["Rubric", "Reviews", "Exit check", "Re-plan when", "Spaced review"]
EVIDENCE_COLUMNS = ["id", "claim", "quote", "source", "tier", "published",
                    "checked", "status"]
PATH_SECTIONS = ["goal", "verdict", "evidence", "path", "checks", "not verified",
                 "verification"]
# A NO PATH plan holds these and nothing else. An extra section is where a
# to-do list gets smuggled back in under another name. "Versions of the goal"
# is optional: the concrete goals offered when theirs was undefined.
NO_PATH_SECTIONS = ["goal", "verdict", "what would change the verdict", "evidence",
                    "not verified", "verification"]
NO_PATH_OPTIONAL = ["versions of the goal"]
# A NO PATH verdict says why before anything else, so nobody reads three
# paragraphs before finding out there is no plan.
NO_PATH_OPENINGS = [
    "This goal is not defined enough to build a learning path",
    "The standard could not be verified",
    "Learning is not what stands between you and this goal",
    "These hours cannot reach this standard",
]

# Openings that name an activity or an exposure rather than a performance.
# Nobody can watch someone "get familiar" with anything, so a milestone worded
# this way cannot be checked and cannot be failed, which is exactly what makes
# it comfortable to write. With a measurable condition attached, some become
# real ("learn a tune by ear in 30 minutes"), so those are only flagged.
VAGUE = re.compile(
    r"^(?:learn(?:\s+about)?|study|explore|master|attend|look\s+into|"
    r"read\s+(?:about|up)|familiari[sz]e|(?:get|become|be)\s+familiar|"
    r"(?:gain|get)\s+(?:some\s+)?exposure|get\s+a\s+feel|get\s+to\s+know|"
    r"(?:get|become|feel|be)\s+(?:more\s+)?comfortable|(?:be|become)\s+aware|"
    r"(?:be\s+)?introduced\s+to|watch|read|(?:develop|gain|build|get)\s+(?:an?\s+)?"
    r"(?:basic\s+|good\s+|solid\s+|deeper\s+)?(?:understanding|knowledge|overview|grasp)|"
    r"work\s+on|try|go\s+through|practi[cs]e|revise|"
    r"take\s+(?:an?\s+|the\s+)?(?:[a-z-]+\s+)?(?:course|class|module|lesson|tutorial|workshop)|"
    r"(?:complete|finish)\s+(?:the\s+|a\s+|an\s+|all\s+|\d+\s+)?(?:[a-z-]+\s+)?"
    r"(?:course|module|chapter|lesson|tutorial|book|unit|video|reading)s?)\b",
    re.IGNORECASE)
# Often vague, sometimes a real standard: "Can understand the main points of
# clear standard speech" is a CEFR descriptor, and a musician can "cover" a song
# live. Flagged for a second look, never failed.
VAGUE_NOTE = re.compile(r"^(?:understand|know|improve|research|review|cover)\b",
                        re.IGNORECASE)
MEASURABLE = re.compile(
    r"\d+(?:\.\d+)?\s*(?:%|(?:percent|s|secs?|seconds?|mins?|minutes?|h|hrs?|hours?|bpm|wpm|"
    r"km|m|metres?|meters?|kg|reps?|laps?|lengths?|words?|points?|marks?|/\s*\d+)\b)|"
    r"\b(?:in\s+under|within|without|unaided|unprepared|from\s+memory|scoring|"
    r"at\s+least|no\s+more\s+than|by\s+ear|at\s+sight|timed|live)\b|"
    r"\band\s+(?:name|identify|explain|write|answer|summari[sz]e|list|play|sing|perform|"
    r"build|produce|draw|teach|present|solve|reproduce)\b", re.IGNORECASE)
# A check, or a self-set standard, that nobody but the learner's mood could fail.
NO_CHECK = re.compile(r"^(?:(?:you|they|i)\s+)?(?:will\s+)?(?:feel|feels|feeling|"
                      r"be\s+confident|confidence|none|n/?a|tbd)\b", re.IGNORECASE)
FEELING = re.compile(r"\b(?:feel|feels|feeling|confident|comfortable|happy|satisfied|"
                     r"good\s+enough)\b", re.IGNORECASE)
CAN_PREFIX = re.compile(r"^(?:they\s+|you\s+)?(?:can|could|will|be\s+able\s+to|"
                        r"able\s+to)\s+", re.IGNORECASE)

# Places that are not sources. A search page shows what exists, not what it
# says. A chatbot answer, ours included, is recall with a link on it.
NOT_SOURCES = [
    (re.compile(r"://(?:www\.)?google\.[a-z.]+/search", re.I), "a search results page"),
    (re.compile(r"://scholar\.google\.[a-z.]+/scholar\?", re.I), "a search results page"),
    (re.compile(r"://(?:www\.)?bing\.com/search", re.I), "a search results page"),
    (re.compile(r"://(?:html\.)?duckduckgo\.com/(?:html/)?\?", re.I), "a search results page"),
    (re.compile(r"://search\.yahoo\.com", re.I), "a search results page"),
    (re.compile(r"://(?:www\.)?(?:chatgpt\.com|chat\.openai\.com)", re.I), "a chatbot answer"),
    (re.compile(r"://claude\.ai/(?:chat|share)", re.I), "a chatbot answer"),
    (re.compile(r"://(?:www\.)?perplexity\.ai", re.I), "a chatbot answer"),
    (re.compile(r"://(?:gemini|bard)\.google\.com", re.I), "a chatbot answer"),
    (re.compile(r"://g\.co/gemini", re.I), "a chatbot answer"),
    (re.compile(r"://copilot\.microsoft\.com", re.I), "a chatbot answer"),
    (re.compile(r"://search\.brave\.com/search", re.I), "a search results page"),
    (re.compile(r"://(?:www\.)?(?:ecosia\.org|kagi\.com|you\.com)/search", re.I),
     "a search results page"),
    (re.compile(r"://(?:www\.)?startpage\.com/", re.I), "a search results page"),
    (re.compile(r"://yandex\.[a-z.]+/search", re.I), "a search results page"),
    (re.compile(r"://(?:www\.)?baidu\.com/s\?", re.I), "a search results page"),
    (re.compile(r"://chat\.mistral\.ai", re.I), "a chatbot answer"),
    (re.compile(r"://chat\.deepseek\.com", re.I), "a chatbot answer"),
    (re.compile(r"://(?:www\.)?grok\.com", re.I), "a chatbot answer"),
    (re.compile(r"://(?:www\.)?meta\.ai", re.I), "a chatbot answer"),
    (re.compile(r"://poe\.com", re.I), "a chatbot answer"),
]
MONTH_WORDS = re.compile(r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?"
                         r"\s+\d{4}\b", re.IGNORECASE)

LINK = re.compile(r"https?://[^\s)>\]|]+|\bdoi:\s*10\.[^\s)>\]|]+", re.IGNORECASE)
EVIDENCE_ID = re.compile(r"\bE\d+\b")
DAY = re.compile(r"^\d{4}-\d{2}-\d{2}$")
CHECKED = re.compile(r"checked\s+(\d+)\s+claims?\s+on\s+(\d{4}-\d{2}-\d{2})", re.I)
# A figure with a comma or a point in it that is neither thousands nor a decimal, such as 1,5000 or
# 0,750, matches nothing and is a problem, not a guess. NUMBER_START keeps a match from starting
# inside a number: the 5000 in 1,5000, the 5 in 1.5.
THOUSANDS = r"[1-9]\d{0,2}(?:,\d{3})+"
DECIMAL = r"\d+(?:\.\d+|,\d{1,2})?"
NUMBER = THOUSANDS + "|" + DECIMAL
NUMBER_START = r"(?<!\d)(?<!\d[.,])"
HOUR_UNIT = r"h|hrs?|hours?"
TIME_UNIT = HOUR_UNIT + r"|min|mins|minutes?"
AMOUNT = re.compile(NUMBER_START + "(" + NUMBER + r")\s*(" + TIME_UNIT + r")\b", re.I)
# A figure that AMOUNT would take by its tail: '.5 h' as 5 h, and '1 200 h' or "1'200 h" as 200 h.
# A count beside the hours, such as the 2 000 in '61 h over 2 000 flashcards', has no unit and is
# not read.
CLIPPED_AMOUNT = re.compile(r"(?:(?<!\w)[.,]|\d[\s'’](?=\d{3}))(?:" + NUMBER + r")\s*(?:"
                            + TIME_UNIT + r")\b", re.I)
H_AND_MIN = re.compile(r"(\d+)\s*h\s*(\d{1,2})\b(?!\s*(?:h|hrs?|hours?)\b)", re.I)
# A week has 168 hours, so a comma in Hours a week is always decimal.
FIGURE = re.compile(r"^\s*(" + DECIMAL + r")(?:\s*(?:--|-|–|—|to)\s*(" + DECIMAL + r"))?"
                    r"(?![.,]?\d)")
# Where the first clause after the figure ends; the docstring lists the ends. Without the space
# after a full stop or a colon, 1:30 would end at its colon.
CLAUSE_END = re.compile(r"[,;(—–]|\s--?\s|[.:]\s")
STARTS_WITH_TIME_UNIT = re.compile(r"(?:" + TIME_UNIT + r")\b", re.I)
STARTS_WITH_HOUR_UNIT = re.compile(r"(?:" + HOUR_UNIT + r")\b", re.I)
# A phrase that names a day: 'a day', 'per day', 'each day', 'every day', 'daily', '/day'.
DAY_PHRASE = re.compile(r"\b(?:a|per|each|every)\s+day\b|\bdaily\b|/\s*day", re.I)
WEEK = re.compile(r"\b(?:week|weekly|wk)\b", re.I)
RATE = re.compile(r"(?<![a-z])[x×]\s*\d|\d\s*[x×](?![a-z])|"
                  r"\b(?:a|per|each|every)\s+(?:week|day|session)\b|/\s*(?:week|day)",
                  re.IGNORECASE)


def to_float(text):
    """A number that NUMBER matched, as a float."""
    if re.fullmatch(THOUSANDS, text):
        return float(text.replace(",", ""))
    return float(text.replace(",", "."))


def parse_day(text):
    text = text.strip()
    if not DAY.match(text):
        return None
    try:
        return datetime.date.fromisoformat(text)
    except ValueError:
        return None


def loose_shape(text):
    """Whether text is written 2026, 2026-03 or 2026-03-14, a real date or not."""
    return bool(re.fullmatch(r"\d{4}(?:-\d{2}(?:-\d{2})?)?", text))


def loose_date(text):
    """2026, 2026-03 or 2026-03-14 as the earliest day it could mean, else None. A missing
    month or day is 01."""
    return parse_day((text + "-01-01")[:10]) if loose_shape(text) else None


def plain(text):
    return text.replace("*", "").replace("_", " ").strip()


def template_text(lines):
    """Text from the templates in plan.md, left in: '<why>', 'https://…', or '…' after a label.
    A code span, and a web link or an email address in angle brackets, are not template text."""
    found = []
    for line in lines:
        line = plain(re.sub(r"`[^`\n]*`", "", line))
        for match in re.finditer(r"(?<!\w)<([A-Za-z][^<>\n]*)>", line):
            inner = match.group(1)
            if "@" not in inner and not re.match(r"https?:", inner, re.I):
                found.append(match.group(0))
        found += re.findall(r"https://(?:…|\.\.\.)", line)
        if re.search(r":[ \t]*(?:…|\.\.\.)$", line):
            found.append(line[-40:])
    return found


def empty(value):
    """MISSING, none, TBD and friends, with or without what follows them."""
    first = re.split(r"[.:;,(—–-]", plain(value).lower(), maxsplit=1)[0]
    return first.strip() in EMPTY_VALUES


def split_sections(text):
    """Header lines before the first '## ', then [(section name, lines)]."""
    header, sections = [], []
    for line in text.split("\n"):
        match = re.match(r"^##\s+(.+?)\s*#*\s*$", line)
        if match:
            sections.append((plain(match.group(1)).strip(" :").lower(), []))
        elif sections:
            sections[-1][1].append(line)
        else:
            header.append(line)
    return header, sections


def section(sections, name):
    for key, lines in sections:
        if key == name:
            return lines
    return None


def header_fields(lines):
    fields = {}
    for line in lines:
        match = re.match(r"^\s*[*_]{0,2}(As of|Verdict|Effort|Budget)[*_]{0,2}\s*:"
                         r"\s*[*_]{0,2}\s*(.*?)\s*$", line, re.I)
        if match:
            fields[match.group(1).lower()] = match.group(2).strip().strip("*_ ")
    return fields


def bullet_fields(lines, names):
    """'- Name: value' bullets, with indented or numbered continuation lines appended. A
    numbered item is a continuation at any indent, since it can never start a field, and its
    marker is not part of the text."""
    wanted = {name.lower(): name for name in names}
    parts, current = {}, None
    for line in lines:
        match = re.match(r"^\s*[-*+]\s+[*_]{0,2}([A-Za-z][A-Za-z -]*?)[*_]{0,2}\s*:"
                         r"\s*[*_]{0,2}\s*(.*)$", line)
        if match and match.group(1).strip().lower() in wanted:
            current = wanted[match.group(1).strip().lower()]
            parts[current] = [match.group(2).strip()]
        elif current and line.strip() and (line.startswith(("  ", "\t"))
                                           or re.match(r"\s*\d+[.)](?:\s|$)", line)):
            parts[current].append(re.sub(r"^\d+[.)](?:\s+|$)", "", line.strip()))
        else:
            current = None
    return {name: " ".join(chunk for chunk in chunks if chunk) for name, chunks in parts.items()}


def cells(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|") and not line.endswith("\\|"):
        line = line[:-1]
    return [cell.strip().replace("\\|", "|") for cell in re.split(r"(?<!\\)\|", line)]


def tables(lines):
    found, current = [], []
    for line in lines + [""]:
        if line.strip().startswith("|"):
            current.append(line)
        elif current:
            found.append(current)
            current = []
    return found


def evidence_rows(lines):
    """The ledger: the table in Evidence whose header has every column. Other
    tables there, such as a count across postings, are left alone."""
    for table in tables(lines):
        columns = [plain(c).lower() for c in cells(table[0])]
        if any(c not in columns for c in EVIDENCE_COLUMNS):
            continue
        rows = []
        for line in table[1:]:
            values = cells(line)
            if all(set(v) <= set("-: ") for v in values):
                continue  # the separator row
            if len(values) != len(columns):
                return rows, [f"an Evidence row has {len(values)} cells where the header "
                              f"has {len(columns)}. Write a '|' inside a cell as '\\|': "
                              f"{line.strip()[:80]}"]
            rows.append(dict(zip(columns, values)))
        return rows, []
    return [], ["the Evidence section has no table with the columns "
                + ", ".join(c.capitalize() for c in EVIDENCE_COLUMNS)]


def milestones(lines):
    """[(id, title, fields)] from '### M1. Title' blocks. Other '###' headings in
    Path, such as notes, are not milestones and end the one before them."""
    found, current, body = [], None, []
    for line in lines + ["### end"]:
        heading = re.match(r"^###\s+(.*)$", line)
        if not heading:
            if current:
                body.append(line)
            continue
        if current:
            found.append((current[0], current[1], bullet_fields(body, MILESTONE_FIELDS)))
        match = re.match(r"^[*_]{0,2}(?:M|Milestone\s+)(\d+)\b[*_]*[\s.:)—–-]*(.*)$",
                         heading.group(1).strip(), re.I)
        current = (f"M{match.group(1)}", match.group(2).strip()) if match else None
        body = []
    return found


def total_hours(text, where, problems):
    """One total in hours, before any bracketed basis: '6 h (E4)', '90 min
    (estimate: ...)', '1 h 30'. A rate such as '3 x 50 min a week' is not a total,
    and summing it as one is how a short plan passes as fitting."""
    main = text.split("(")[0]
    if RATE.search(main):
        problems.append(f"{where}: '{text[:60]}' is a rate, not a total. Give the total "
                        "hours, e.g. '25 h (estimate: 3 x 50 min a week for 10 weeks)'")
        return None
    pair = H_AND_MIN.search(main)
    if pair:
        return int(pair.group(1)) + int(pair.group(2)) / 60
    amounts = AMOUNT.findall(main)
    if len(amounts) > 1:
        problems.append(f"{where}: '{text[:60]}' holds {len(amounts)} amounts. Give one "
                        "total, e.g. '1.5 h'")
        return None
    # A number with a unit that no amount took is one the checker cannot read: 0,750 h beside 6 min.
    with_unit = re.findall(r"\d\s*(?:" + TIME_UNIT + r")\b", main, re.I)
    if not amounts or len(with_unit) > len(amounts) or CLIPPED_AMOUNT.search(main):
        if with_unit:
            problems.append(f"{where}: '{text[:60]}' has a number the checker cannot read. "
                            "Write hours as '6 h', '1.5 h', '1,5 h' or '2,200 h'")
        else:
            problems.append(f"{where}: '{text[:60]}' has no hours in it, e.g. '6 h'")
        return None
    value, unit = to_float(amounts[0][0]), amounts[0][1].lower()
    return value / 60 if unit.startswith("min") else value


def check_basis(text, where, by_id, problems):
    """Hours come from a cited row or from a labelled estimate with its basis."""
    basis = text[text.find("("):] if "(" in text else ""
    if any(i in by_id for i in EVIDENCE_ID.findall(basis)):
        return
    if re.search(r"estimate\s*:\s*\w+", basis, re.I):
        return
    problems.append(f"{where}: '{text[:60]}' cites no evidence and gives no estimate "
                    "basis. Write '(E4)' or '(estimate: <how you got it>)'")


def vague(text):
    """'fail', 'note' or None for an outcome or a performance line."""
    opening = CAN_PREFIX.sub("", plain(text))
    if VAGUE.match(opening):
        return "note" if MEASURABLE.search(opening) else "fail"
    if VAGUE_NOTE.match(opening):
        return "note"
    return None


def solid(ids, by_id):
    """IDs that can carry weight: confirmed, and about the field, not the learner."""
    return [i for i in ids if i in by_id and by_id[i]["status"] == "confirmed"
            and by_id[i]["tier"] != "learner"]


def check_header(fields, today, max_age):
    problems, notes = [], []
    as_of = parse_day(fields.get("as of", ""))
    if as_of is None:
        problems.append("no 'As of: YYYY-MM-DD' line at the top. The plan has to say "
                        "which day its facts were true on")
    elif as_of > today + datetime.timedelta(days=1):
        problems.append(f"As of is {as_of}, after today ({today}). Take the date from the "
                        "environment, not from memory")
    elif (today - as_of).days > max_age:
        problems.append(f"As of is {as_of}, {(today - as_of).days} days ago. Standards and "
                        "versions move; re-check the sources and re-date the plan")
    elif as_of != today:
        notes.append(f"As of is {as_of}, not today ({today})")
    verdict = fields.get("verdict", "").upper()
    if verdict not in VERDICTS:
        problems.append(f"Verdict is '{fields.get('verdict', '')}'. It has to be PATH or "
                        "NO PATH")
    return as_of, verdict, problems, notes


def check_evidence(rows, as_of, today, max_age):
    problems, notes, by_id, undated = [], [], {}, 0
    for row in rows:
        rid = plain(row["id"])
        where = f"evidence {rid or '(no ID)'}"
        if not re.fullmatch(r"E\d+", rid):
            problems.append(f"{where}: IDs are E1, E2, ... so milestones can cite them")
            continue
        if rid in by_id:
            problems.append(f"{where}: the ID is used twice")
        by_id[rid] = row
        for column in ("claim", "quote", "source"):
            if not row[column].strip():
                problems.append(f"{where}: the {column} is empty")
        row["tier"], row["status"] = plain(row["tier"]).lower(), plain(row["status"]).lower()
        tier, status = row["tier"], row["status"]
        if tier not in TIERS:
            problems.append(f"{where}: tier is '{tier}'. Use 1, 2, 3, 4 or learner")
        links = sorted(set(m.lower() for m in LINK.findall(row["source"])))
        if tier in {"1", "2", "3", "4"} and not links:
            problems.append(f"{where}: the source has no link. A fact nobody can open is "
                            "not a fact the plan can use")
        for link in links:
            for pattern, what in NOT_SOURCES:
                if pattern.search(link):
                    problems.append(f"{where}: {link} is {what}, not a source. Link the "
                                    "page that says it")
        if status not in STATUSES:
            problems.append(f"{where}: status is '{status}'. Use confirmed or unconfirmed")
        elif status == "confirmed" and tier in {"3", "4"}:
            if len(links) < 2:
                problems.append(f"{where}: confirmed on one tier-{tier} source. That takes "
                                "a second, independent source; otherwise it is unconfirmed")
            else:
                notes.append(f"{where}: confirmed by two tier-{tier} sources. Check by hand "
                             "that neither is repeating the other")
        published = plain(row["published"])
        if not published:
            problems.append(f"{where}: Published is empty. Give a date, a version, or "
                            "'undated'")
        elif published.lower() == "undated":
            undated += 1
        elif MONTH_WORDS.search(published):
            problems.append(f"{where}: Published is '{published}'. Write a date as YYYY-MM or "
                            "YYYY-MM-DD, so it can be compared with today")
        elif loose_shape(published) and not loose_date(published):
            problems.append(f"{where}: Published is '{published}', which is not a real date. "
                            f"If it is a version, write it as 'v{published}'")
        elif (loose_date(published) or today) > today + datetime.timedelta(days=1):
            problems.append(f"{where}: published {published}, after today")
        checked = parse_day(plain(row["checked"]))
        if checked is None:
            problems.append(f"{where}: Checked is '{row['checked']}'. Give the day the "
                            "source was read, as YYYY-MM-DD")
        elif checked > today + datetime.timedelta(days=1):
            problems.append(f"{where}: checked {checked}, after today")
        elif (today - checked).days > max_age:
            problems.append(f"{where}: read on {checked}, {(today - checked).days} days ago. "
                            "Read it again; pages change")
    if undated:
        notes.append(f"{undated} source(s) carry no date or version. Their Checked date "
                     "is the only evidence they are current")
    return by_id, problems, notes


def check_goal(goal, verdict, by_id):
    problems, notes = [], []
    for name in GOAL_FIELDS:
        if name not in goal:
            problems.append(f"the Goal section has no '- {name}:' line")
    if verdict != "PATH":
        return problems, notes
    for name in DEFINING:
        if name in goal and empty(goal[name]):
            problems.append(f"Goal '{name}' is '{goal[name] or 'empty'}', and the verdict is "
                            "PATH. Without performance, standard and conditions the goal "
                            "is not defined, and the verdict is NO PATH")
    performance = goal.get("Performance", "")
    if not empty(performance):
        kind = vague(performance)
        if kind == "fail":
            problems.append(f"Goal 'Performance' is '{performance[:60]}', an activity. Say "
                            "what they will be able to do that someone could check")
        elif kind == "note":
            notes.append(f"Goal 'Performance' opens with '{plain(performance).split()[0]}'. "
                         "Fine if the Standard says how it is judged")
    standard = plain(goal.get("Standard", ""))
    if standard.lower().startswith("self-set"):
        if len(standard.split()) < 4:
            problems.append("Goal 'Standard' is self-set but does not say how it will be "
                            "checked. Write 'self-set: <what someone could check>'")
        elif FEELING.search(standard):
            problems.append(f"Goal 'Standard' is '{standard[:60]}'. A feeling cannot be "
                            "checked by anyone else: name the recording, time, result or "
                            "person that will show it")
    elif not empty(standard) and not solid(EVIDENCE_ID.findall(standard), by_id):
        problems.append("Goal 'Standard' cites no confirmed evidence about the field. The "
                        "path aims at the standard, so it is the first thing to verify")
    if empty(goal.get("Starting point", "")):
        notes.append("the starting point is missing. The first milestone should find it")
    return problems, notes


def check_milestones(found, by_id):
    problems, notes, total, cited = [], [], 0.0, set()
    if not found:
        problems.append("the verdict is PATH and the Path section has no milestones "
                        "('### M1. ...')")
    for mid, title, fields in found:
        where = f"{mid} '{title}'" if title else mid
        for name in REQUIRED_MILESTONE_FIELDS:
            if not fields.get(name, "").strip():
                problems.append(f"{where}: '- {name}:' is missing or empty")
        if NO_CHECK.match(plain(fields.get("Check", ""))) or re.search(
                r"\bfeels?\s+(?:natural|right|good|easy|confident)\b", fields.get("Check", ""),
                re.I):
            problems.append(f"{where}: the check '{fields['Check'][:60]}' is not a check. "
                            "Say how the work is judged, by whom, against what")
        outcome = fields.get("Outcome", "")
        kind = vague(outcome) if outcome else None
        if kind == "fail":
            problems.append(f"{where}: the outcome '{outcome[:60]}' is an activity, not a "
                            "performance. Say what they will do that someone could watch "
                            "or mark")
        elif kind == "note":
            notes.append(f"{where}: the outcome opens with '{plain(outcome).split()[0]}'. "
                         "Fine if the condition and the Check make it observable")
        ids = EVIDENCE_ID.findall(fields.get("Evidence", ""))
        cited.update(ids)
        unknown = [i for i in ids if i not in by_id]
        if unknown:
            problems.append(f"{where}: cites {', '.join(unknown)}, which the Evidence table "
                            "does not have")
        if fields.get("Evidence", "").strip() and not ids:
            problems.append(f"{where}: Evidence names no row. Cite the E-numbers it rests on")
        elif ids and not unknown and not solid(ids, by_id):
            problems.append(f"{where}: rests on nothing confirmed about the field. An "
                            "unconfirmed lead, or the learner's own record, can shape a "
                            "milestone but not carry one")
        resources = fields.get("Resources", "")
        if resources.strip():
            resource_ids = EVIDENCE_ID.findall(resources)
            cited.update(resource_ids)
            if not resource_ids or any(i not in by_id for i in resource_ids):
                problems.append(f"{where}: every resource comes from the Evidence table; "
                                "cite the row that shows it exists and is current")
        time_text = fields.get("Time", "")
        if time_text.strip():
            hours = total_hours(time_text, f"{where} Time", problems)
            if hours is not None:
                total += hours
                check_basis(time_text, f"{where} Time", by_id, problems)
    return total, cited, problems, notes


def weekly_hours(text):
    """The first figure, or the low end of a range at the start: '6', '3-5',
    '8, net of two weeks' holiday'. Later numbers are commentary."""
    match = FIGURE.match(plain(text))
    if not match:
        return None, False
    low = to_float(match.group(1))
    if match.group(2):
        low = min(low, to_float(match.group(2)))
    return low, bool(match.group(2))


def per_day(text):
    """Whether Hours a week gives hours per day. The rule is in the docstring of this file."""
    text = plain(text)
    figure = FIGURE.match(text)
    after = text[figure.end():] if figure else text
    day = DAY_PHRASE.search(after)
    if not day:
        return False
    clause_end = CLAUSE_END.search(after)
    words = (after[:clause_end.start()] if clause_end else after).strip()
    # A bare number, with a clause ending straight after it, owns the clause that follows when that
    # opens with a time unit: '30 (minutes a day)'. With no unit there, what follows is commentary.
    owned = words or after[clause_end.end():].strip()
    if not words and not STARTS_WITH_TIME_UNIT.match(owned):
        return False
    # A week named before the day makes the day commentary, unless the figure counts something
    # else, which its words show by opening with anything but an hour unit ('5 days a week'). A
    # figure in minutes is not hours either, so '90 minutes a week (15 minutes a day)' is refused.
    return not (WEEK.search(after[:day.start()]) and STARTS_WITH_HOUR_UNIT.match(owned))


def check_budget(fields, goal, as_of, total, by_id, prose):
    """prose is the Verdict and Checks text, where a tight budget says what is
    cut first and a plan with no deadline says how many weeks it takes."""
    problems, notes = [], []
    budget = plain(fields.get("budget", "")).lower()
    if budget == "short":
        return ["Budget is short, and a path that cannot reach its standard is not a "
                "path. Plan for the smaller goal the hours do buy, if they accept it, or "
                "make the verdict NO PATH"], notes
    if budget not in BUDGETS:
        return [f"Budget is '{fields.get('budget', '')}'. It has to be fits, tight or "
                "unknown"], notes

    effort_text, effort = fields.get("effort", ""), None
    if not effort_text:
        problems.append("no 'Effort:' line at the top: the hours the evidence says the "
                        "standard takes from their starting point")
    else:
        effort = total_hours(effort_text, "Effort", problems)
        if effort is not None:
            check_basis(effort_text, "Effort", by_id, problems)
    if effort is not None and total + 0.01 < effort:
        problems.append(f"the milestones add up to {total:g} h and the Effort line says "
                        f"{effort:g} h. Either the path is missing work, or the Effort line "
                        "has to say why they need less")
    need = max(total, effort or 0)

    hours_text, deadline_text = goal.get("Hours a week", ""), goal.get("Deadline", "")
    hours_missing = plain(hours_text).upper().startswith("MISSING")
    deadline_plain = plain(deadline_text)
    deadline_missing = deadline_plain.upper().startswith("MISSING")
    no_deadline = deadline_plain.lower().startswith("none")
    deadline = parse_day(deadline_plain[:10])
    if not (deadline_missing or no_deadline or deadline):
        problems.append(f"Deadline is '{deadline_text}'. Use YYYY-MM-DD, none, or MISSING")
        return problems, notes
    if deadline and (not as_of or deadline <= as_of):
        problems.append(f"the deadline {deadline} is not after the plan's date {as_of}")
        return problems, notes
    if hours_missing or deadline_missing:
        if budget != "unknown":
            problems.append(f"Budget is {budget} but the "
                            f"{'hours a week are' if hours_missing else 'deadline is'} "
                            "missing. Without them it is unknown")
        return problems, notes
    if per_day(hours_text):
        problems.append(f"Hours a week is '{hours_text}'. Give hours a week, e.g. "
                        "'5 hours a week'")
        return problems, notes
    weekly, ranged = weekly_hours(hours_text)
    if not weekly:
        problems.append(f"Hours a week is '{hours_text}'. " + (
            "Write the number as 6, 1.5 or 1,5"
            if weekly is None and re.match(r"\s*\d", plain(hours_text))
            else "Start it with a number"))
        return problems, notes
    if ranged:
        notes.append(f"Hours a week is '{hours_text}'; the budget uses {weekly:g}, the "
                     "low end")
    if no_deadline:
        if budget != "fits":
            problems.append(f"Budget is {budget} with no deadline. Without one it fits, "
                            "and the Verdict says how many weeks it takes")
        if not re.search(r"\d+(?:\.\d+)?\s*weeks?\b", prose, re.I):
            problems.append(f"there is no deadline, and the Verdict does not say how many "
                            f"weeks it takes: about {need / weekly:.0f} at {weekly:g} h a week")
        return problems, notes
    if budget == "unknown":
        problems.append("Budget is unknown, but the hours a week and the deadline are both "
                        "given. Work it out")
        return problems, notes
    available = weekly * (deadline - as_of).days / 7
    if need > available:
        problems.append(f"Budget says {budget}, but the plan needs {need:g} h and "
                        f"{weekly:g} h a week to {deadline} gives {available:.0f} h. That is "
                        "short: plan for what the hours do buy, if they accept it, or make "
                        "the verdict NO PATH")
    elif budget == "fits" and need > available - weekly:
        problems.append(f"Budget says fits, but {need:g} h of {available:.0f} h leaves less "
                        "than a week spare. That is tight: say what is cut first")
    elif budget == "tight" and need <= available - weekly:
        problems.append(f"Budget says tight, but {need:g} h of {available:.0f} h leaves more "
                        "than a week spare. That fits")
    elif budget == "tight" and not re.search(r"\bcut", prose, re.I):
        problems.append("Budget is tight, and neither the Verdict nor the Checks says what "
                        "is cut first if a week is lost")
    return problems, notes


def check_verification(lines, rows, as_of, today):
    text = plain(" ".join(line.strip() for line in lines))
    head = CHECKED.search(text)
    counts = {word: re.search(rf"(\d+)\s+{word}", text, re.I)
              for word in ("upheld", "corrected", "dropped")}
    if not head or not all(counts.values()):
        return ["the Verification section has no line 'Checked N claims on YYYY-MM-DD: "
                "A upheld, B corrected, C dropped.' The fact review has not been recorded, "
                "so there is no sign it ran"]
    checked, day = int(head.group(1)), parse_day(head.group(2))
    upheld, corrected, dropped = (int(counts[w].group(1))
                                  for w in ("upheld", "corrected", "dropped"))
    problems = []
    if upheld + corrected + dropped != checked:
        problems.append(f"Verification: {upheld} + {corrected} + {dropped} is not {checked}")
    if upheld + corrected != len(rows):
        problems.append(f"Verification kept {upheld + corrected} claims and the Evidence "
                        f"table has {len(rows)}. Every row goes through the review, and "
                        "every dropped claim comes out of the table")
    if day and as_of and day < as_of:
        problems.append(f"the fact review ran on {day}, before the plan's date {as_of}. "
                        "Whatever changed since has not been checked")
    if day and day > today + datetime.timedelta(days=1):
        problems.append(f"the fact review is dated {day}, after today")
    details = [line for line in lines
               if re.match(r"^\s*(?:[-*+]|\d+[.)])\s+\S", line) and not CHECKED.search(plain(line))]
    if len(details) < corrected + dropped:
        problems.append(f"Verification counts {corrected} corrected and {dropped} dropped "
                        f"but lists {len(details)}. Give one line for each, saying what "
                        "changed or why it went")
    return problems


def list_items(lines):
    """The text of each bullet or numbered item, with any 'Label:' in front of it
    removed, since What would change the verdict reads '<missing>: <decision>'."""
    items = []
    for line in lines:
        match = re.match(r"^\s*(?:[-*+]|\d+[.)])\s+(.*)$", line)
        if match:
            text = plain(match.group(1))
            if ":" in text[:42]:
                text = re.sub(r"^(?:V\d+\.?\s*)?[^:]{1,40}:\s*", "", text)
            items.append(re.sub(r"^V\d+\.?\s*", "", text))
    return items


def check_no_path(text, header_lines, sections):
    problems = []
    extra = [name for name, _ in sections
             if name not in NO_PATH_SECTIONS + NO_PATH_OPTIONAL]
    if extra:
        problems.append("a NO PATH plan has only these sections: "
                        f"{', '.join(NO_PATH_SECTIONS + NO_PATH_OPTIONAL)}. Remove "
                        f"{', '.join(extra)}: a list of things to do, under any heading, "
                        "is a path")
    if any(re.match(r"^\s*[*_]{0,2}(?:Budget|Effort)\b", line, re.I) for line in header_lines):
        problems.append("a NO PATH plan has no Budget or Effort line")
    steps = r"(?:M\d+|Milestone|Step|Week|Phase|Day|Stage|Module|Lesson|Session)s?\b"
    heading = re.search(r"^#{3,}\s+[*_]{0,2}" + steps, text, re.M | re.I)
    label = re.search(r"^\s*(?:[-*+]|\d+[.)])?\s*\*\*" + steps, text, re.M | re.I)
    # Versions of the goal may say what each version is and what it takes, so
    # only Practice counts there; everywhere else Outcome and Time do too.
    fields_anywhere = r"^\s*[-*+]\s+[*_]{0,2}Practice[*_]{0,2}\s*:"
    fields_outside = r"^\s*[-*+]\s+[*_]{0,2}(?:Outcome|Time)[*_]{0,2}\s*:"
    outside = "\n".join("\n".join(lines) for name, lines in sections
                        if name not in NO_PATH_OPTIONAL)
    field = (re.search(fields_anywhere, text, re.M | re.I)
             or re.search(fields_outside, outside, re.M | re.I))
    if heading or label or field:
        problems.append("the verdict is NO PATH and the plan has milestones or steps. A "
                        "plan with no path carries none; if there is a path, the verdict "
                        "is PATH")
    for name in ("verdict", "versions of the goal", "what would change the verdict"):
        for item in list_items(section(sections, name) or []):
            if vague(item) == "fail":
                problems.append(f"'{item[:60]}' under {name.capitalize()} is an activity. "
                                "A NO PATH plan lists decisions and facts, not things to do")
    lines = section(sections, "verdict") or []
    first = next((line for line in lines if line.strip()), "")
    # The sentence may be bold, quoted or in a blockquote, or follow a short bold
    # label such as "**Why there is no path.**"; it still has to come first.
    candidates = [first, re.sub(r"^\s*>?\s*\*\*[^*]{1,60}\*\*", "", first)]
    candidates = [re.sub(r"^(?:[\s>*_\"'“”‘’]|verdict\s*:)*", "", c, flags=re.I)
                  for c in candidates]
    if not any(c.startswith(s) for c in candidates for s in NO_PATH_OPENINGS):
        problems.append("a NO PATH verdict opens by saying why, in one of these sentences: "
                        + "; ".join(f"'{s}.'" for s in NO_PATH_OPENINGS))
    change = section(sections, "what would change the verdict")
    if change is not None and not any(line.strip() for line in change):
        problems.append("'What would change the verdict' is empty: say what is missing, and "
                        "what would supply it")
    return problems


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("plan", help="the learning plan, as markdown")
    parser.add_argument("--today", help="today's date, YYYY-MM-DD (default: this "
                        "machine's clock)")
    parser.add_argument("--max-age-days", type=int, default=30,
                        help="how long a source read stays current (default 30)")
    args = parser.parse_args()

    today = parse_day(args.today) if args.today else datetime.date.today()
    if today is None:
        print(f"--today '{args.today}' is not YYYY-MM-DD", file=sys.stderr)
        return 2
    try:
        with open(args.plan, encoding="utf-8-sig") as handle:
            text = handle.read().replace("\r\n", "\n")
    except UnicodeDecodeError:
        print(f"{args.plan} is not UTF-8. Save it as UTF-8 and run this again",
              file=sys.stderr)
        return 2
    except OSError as error:
        print(f"cannot read {args.plan}: {error}", file=sys.stderr)
        return 2

    header, sections = split_sections(text)
    fields = header_fields(header)
    as_of, verdict, problems, notes = check_header(fields, today, args.max_age_days)

    evidence = section(sections, "evidence") or []
    rows, table_problems = evidence_rows(evidence)
    # The lines searched for template text. A quote may hold anything, so the Evidence table is
    # searched without its quotes.
    searched = [line for name, lines in sections if name != "evidence" for line in lines]
    searched += [line for line in evidence if not line.lstrip().startswith("|")]
    searched += [value for row in rows for column, value in row.items() if column != "quote"]
    leftover = template_text(header + searched)
    if leftover:
        problems.append("template text left in the plan: "
                        + ", ".join(f"'{item}'" for item in list(dict.fromkeys(leftover))[:4])
                        + ". Replace it with the plan's own words; put anything that only "
                        "looks like it in `backticks`")

    for name in (PATH_SECTIONS if verdict == "PATH" else NO_PATH_SECTIONS):
        if section(sections, name) is None:
            problems.append(f"no '## {name.capitalize()}' section")

    problems += table_problems
    by_id, more, extra = check_evidence(rows, as_of, today, args.max_age_days)
    problems += more
    notes += extra

    goal = bullet_fields(section(sections, "goal") or [], GOAL_FIELDS)
    more, extra = check_goal(goal, verdict, by_id)
    problems += more
    notes += extra

    verdict_lines = section(sections, "verdict")
    if verdict_lines is not None and not any(line.strip() for line in verdict_lines):
        problems.append("the Verdict section is empty. Say what the evidence and the hours "
                        "come to, or why there is no path")

    not_verified = section(sections, "not verified")
    if not_verified is not None and not any(line.strip() for line in not_verified):
        problems.append("'Not verified' is empty. Say what could not be established, or "
                        "write that everything the plan uses was confirmed")

    found, total = [], 0.0
    if verdict == "NO PATH":
        problems += check_no_path(text, header, sections)
    elif verdict == "PATH":
        checks = section(sections, "checks")
        if checks is not None:
            given = bullet_fields(checks, CHECKS_LINES)
            for name in CHECKS_LINES:
                if name not in given:
                    problems.append(f"the Checks section has no '- {name}:' line")
                elif not given[name]:
                    problems.append(f"the Checks section's '- {name}:' line is empty. Put its "
                                    "text on that line, or on the lines directly below it, "
                                    "indented two spaces or numbered")
        found = milestones(section(sections, "path") or [])
        total, cited, more, extra = check_milestones(found, by_id)
        problems += more
        notes += extra
        prose = " ".join((section(sections, "verdict") or []) + (checks or []))
        more, extra = check_budget(fields, goal, as_of, total, by_id, prose)
        problems += more
        notes += extra
        for name, lines in sections:
            if name not in ("evidence", "verification", "not verified"):
                cited |= set(EVIDENCE_ID.findall(" ".join(lines)))
        cited |= set(EVIDENCE_ID.findall(" ".join(header)))
        orphans = [rid for rid in by_id if rid not in cited]
        if orphans:
            notes.append(f"evidence nothing cites: {', '.join(orphans)}. Cut it, or say "
                         "what it supports")

    problems += check_verification(section(sections, "verification") or [], rows, as_of,
                                   today)

    if problems:
        print(f"{len(problems)} problem(s) to fix:\n", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        print("", file=sys.stderr)
    if notes:
        print(f"{len(notes)} thing(s) to look at:\n")
        for note in notes:
            print(f"  {note}")
        print("")

    confirmed = sum(1 for row in rows if row["status"] == "confirmed")
    summary = (f"{verdict or 'no verdict'}: {len(rows)} evidence row(s), {confirmed} "
               "confirmed")
    if verdict == "PATH":
        summary += f"; {len(found)} milestone(s), {total:g} h"
    print(summary)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
