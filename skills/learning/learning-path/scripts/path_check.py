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

What it cannot check: whether a quote is really on the page, whether two
sources are really independent, and whether a claim says no more than its
quote. That is the fact review in references/review.md.

A gate, not a checklist. Problems exit 1. Wording that is usually vague but has
real exceptions, and things worth a second look, are printed and exit 0. An
unreadable file or a bad argument exits 2. A date one day ahead is accepted,
since the plan and the machine checking it may sit in different time zones.

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
    r"\d+(?:\.\d+)?\s*(?:%|percent|s|secs?|seconds?|mins?|minutes?|h|hrs?|hours?|bpm|wpm|"
    r"km|m|metres?|meters?|kg|reps?|laps?|lengths?|words?|points?|marks?|/\s*\d+)\b|"
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
AMOUNT = re.compile(r"(\d+(?:\.\d+)?)\s*(h|hrs?|hours?|min|mins|minutes?)\b", re.I)
H_AND_MIN = re.compile(r"(\d+)\s*h\s*(\d{1,2})\b(?!\s*(?:h|hrs?|hours?)\b)", re.I)
RATE = re.compile(r"(?<![a-z])[x×]\s*\d|\d\s*[x×](?![a-z])|"
                  r"\b(?:a|per|each|every)\s+(?:week|day|session)\b|/\s*(?:week|day)",
                  re.IGNORECASE)


def parse_day(text):
    text = text.strip()
    if not DAY.match(text):
        return None
    try:
        return datetime.date.fromisoformat(text)
    except ValueError:
        return None


def loose_date(text):
    """2026, 2026-03 or 2026-03-14 as the earliest day it could mean, else None."""
    text = text.strip()
    for pattern, suffix in ((r"^\d{4}-\d{2}-\d{2}$", ""), (r"^\d{4}-\d{2}$", "-01"),
                            (r"^\d{4}$", "-01-01")):
        if re.match(pattern, text):
            return parse_day(text + suffix)
    return None


def plain(text):
    return text.replace("*", "").replace("_", " ").strip()


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
    """'- Name: value' bullets, with indented continuation lines appended."""
    wanted = {name.lower(): name for name in names}
    fields, current = {}, None
    for line in lines:
        match = re.match(r"^\s*[-*+]\s+[*_]{0,2}([A-Za-z][A-Za-z -]*?)[*_]{0,2}\s*:"
                         r"\s*[*_]{0,2}\s*(.*)$", line)
        if match and match.group(1).strip().lower() in wanted:
            current = wanted[match.group(1).strip().lower()]
            fields[current] = match.group(2).strip()
        elif current and line.startswith(("  ", "\t")) and line.strip():
            fields[current] += " " + line.strip()
        else:
            current = None
    return fields


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
    if not amounts:
        problems.append(f"{where}: '{text[:60]}' has no hours in it, e.g. '6 h'")
        return None
    value, unit = float(amounts[0][0]), amounts[0][1].lower()
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
    match = re.match(r"^\s*(\d+(?:\.\d+)?)(?:\s*(?:-|–|to)\s*(\d+(?:\.\d+)?))?",
                     plain(text))
    if not match:
        return None, False
    low = float(match.group(1))
    if match.group(2):
        low = min(low, float(match.group(2)))
    return low, bool(match.group(2))


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
    if re.search(r"\b(?:a|per|each|every)\s+day\b|\bdaily\b|/\s*day", hours_text, re.I):
        problems.append(f"Hours a week is '{hours_text}'. Give hours a week")
        return problems, notes
    weekly, ranged = weekly_hours(hours_text)
    if not weekly:
        problems.append(f"Hours a week is '{hours_text}'. Start it with a number")
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
    head = re.search(r"checked\s+(\d+)\s+claims?\s+on\s+(\d{4}-\d{2}-\d{2})", text, re.I)
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
    details = [line for line in lines if re.match(r"^\s*[-*+]\s+\S", line)]
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
    steps = r"(?:M\d|Milestone|Step|Week|Phase|Day|Stage|Module|Lesson|Session)\b"
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

    for name in (PATH_SECTIONS if verdict == "PATH" else NO_PATH_SECTIONS):
        if section(sections, name) is None:
            problems.append(f"no '## {name.capitalize()}' section")

    rows, more = evidence_rows(section(sections, "evidence") or [])
    problems += more
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
                if not given.get(name, "").strip():
                    problems.append(f"the Checks section has no '- {name}:' line")
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
