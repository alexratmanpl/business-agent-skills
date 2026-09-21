#!/usr/bin/env python3
"""Check a filled direction report before it is handed over.

Reads the report-data block out of direction-report.html and looks for the
things that make a direction report worthless: a claim with no source, a
forecast with nothing that could disprove it, demand asserted rather than
counted, a role family missing its pay range, its entry bar or the mark saying
whether one source backs it or two, and somebody's contact details left in a
file they may forward.

It cannot tell evidence that is all self-assessment from evidence that is
sourced, because marking a source as their own is a legitimate answer. That
one is read by hand.

It also catches the failure the page cannot show you. Anything the renderer
does not recognise is skipped in silence, so one mistyped key -- "habbits", or
"gaps[0].weigth" -- drops a section or empties a column while the report still
looks finished. Every object the page reads is listed here for that reason.

Unlike the plain-language checker in interview-prep, this one is a gate, not a
checklist. Those flags are stylistic and have exceptions. These do not: a
source that is not there is not there. Structural and privacy problems exit 1;
length and vocabulary problems report and do not.

Usage: report_check.py direction-report.html [--max-field-words 45]
"""

import argparse
import json
import re
import sys

# Values the renderer knows. Anything else still renders, as a plain grey chip
# with no colour and no meaning, which is worse than an error because it looks
# deliberate. Checked rather than corrected: the fix depends on what was meant.
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

# Every object the page reads, including the ones inside lists. Leaving the list
# items out was the whole bug this check exists to prevent: gaps[0].weigth reads
# as an empty weight, the chip renders grey, and nothing anywhere says why.
KNOWN_KEYS = {
    "": {"meta", "shape", "evidence", "selling", "habits", "thread", "gaps",
         "constraints", "decisions", "corrections", "market", "horizon",
         "glossary", "sources"},
    "meta": {"name", "title", "date", "eyebrow", "lede", "footer"},
    "evidence[]": {"title", "text", "src"},
    "selling[]": {"title", "text"},
    "habits[]": {"label", "tone", "text"},
    "thread": {"intro", "events", "outro"},
    "thread.events[]": {"year", "kind", "title", "detail", "verdict", "verdictText"},
    "gaps[]": {"gap", "weight", "evidence", "fix", "cost"},
    "constraints": {"hard", "soft"},
    "decisions[]": {"label", "text"},
    "market": {"asOf", "lines", "skills", "families", "skipped", "positions"},
    "market.lines[]": {"text", "src"},
    "market.skills[]": {"name", "countN", "note"},
    "market.families[]": {"name", "buys", "why", "demandN", "demandNote", "pay",
                          "entryBar", "sourcing", "trend", "ages", "verdict",
                          "verdictTone", "note"},
    "market.positions[]": {"employer", "title", "loc", "family", "status", "statusDate",
                           "evidence", "oddsNow", "oddsAfter", "when", "note"},
    "horizon": {"note", "shifts", "agesWell", "agesBadly", "clocks", "calendar"},
    "horizon.shifts[]": {"title", "mechanism", "alreadyVisible", "src", "falsifier", "worthTo"},
    "horizon.clocks": {"title", "axis", "lanes"},
    "horizon.clocks.lanes[]": {"name", "sub", "steps"},
    "horizon.clocks.lanes[].steps[]": {"at", "span", "label", "detail", "tone"},
    "horizon.calendar[]": {"date", "what"},
    "sources": {"produced", "checked", "notConfirmed"},
}

# Things that identify a person rather than describe them. The report is a file
# that gets forwarded; a phone number in it travels with the file. Employer and
# source links are expected and are not flagged -- a personal profile is.
IDENTIFIERS = [
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.]{2,}"), "an email address"),
    (re.compile(r"(?<!\d)\+\d[\d\s().-]{7,}\d(?!\d)"), "a phone number"),
    (re.compile(r"(?:linkedin\.com/in/|github\.com/(?!orgs)[\w-]+/?$|x\.com/|twitter\.com/)", re.I),
     "a personal profile link"),
    (re.compile(r"\b\d{1,4}\s+[A-Z][a-z]+\s+(?:Street|St|Road|Rd|Avenue|Ave|Lane|ulice|ul\.)\b"),
     "a street address"),
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


def read_report(filename):
    text = open(filename, encoding="utf-8").read()
    match = re.search(
        r'<script[^>]*id="report-data"[^>]*>(.*?)</script>', text, re.S)
    if not match:
        return None, ["no <script id=\"report-data\"> block in this file"]
    try:
        return json.loads(match.group(1)), []
    except json.JSONDecodeError as error:
        return None, [f"the report data is not valid JSON: {error}. "
                      "JSON needs double quotes on every key and string, no "
                      "trailing commas and no comments"]


def check_sources(data):
    problems = []
    for i, item in enumerate(data.get("evidence", [])):
        if not str(item.get("src", "")).strip():
            problems.append(f"evidence[{i}] '{item.get('title', '?')}' names no source. "
                            "Write where it came from, or mark it self")
    for i, line in enumerate(data.get("market", {}).get("lines", [])):
        if not str(line.get("src", "")).strip():
            problems.append(f"market.lines[{i}] names no source")
    return problems


def check_horizon(data):
    problems = []
    for i, shift in enumerate(data.get("horizon", {}).get("shifts", [])):
        name = shift.get("title", "?")
        if not str(shift.get("falsifier", "")).strip():
            problems.append(f"horizon.shifts[{i}] '{name}' says nothing that would "
                            "prove it wrong. Without that it is a prediction, not a reading")
        if not str(shift.get("alreadyVisible", "")).strip():
            problems.append(f"horizon.shifts[{i}] '{name}' points at nothing already "
                            "visible. Name the dated thing it can be seen in today")
        if not str(shift.get("src", "")).strip():
            problems.append(f"horizon.shifts[{i}] '{name}' names no source")
    return problems


def check_demand(data):
    problems = []
    for i, family in enumerate(data.get("market", {}).get("families", [])):
        name = family.get("name", "?")
        if not isinstance(family.get("demandN"), (int, float)):
            problems.append(f"market.families[{i}] '{name}' has no counted demand. "
                            "demandN is how many open positions were counted, as a number")
        if not str(family.get("demandNote", "")).strip():
            problems.append(f"market.families[{i}] '{name}' does not say where the count "
                            "came from or when. Put the source and the date in demandNote")
        if not str(family.get("pay", "")).strip():
            problems.append(f"market.families[{i}] '{name}' has no pay range. A family "
                            "with no ceiling cannot be priced against anybody's floor")
        if not str(family.get("entryBar", "")).strip():
            problems.append(f"market.families[{i}] '{name}' has no entry bar. A family "
                            "priced only at its ceiling reads as reachable when it is not")
        if not str(family.get("sourcing", "")).strip():
            problems.append(f"market.families[{i}] '{name}' is not marked confirmed or "
                            "unconfirmed. One source is a lead, not a finding, and the "
                            "report has to say which this is")
    return problems


def check_identifiers(data):
    problems = []
    for path, value in walk(data):
        if not isinstance(value, str):
            continue
        found = [what for pattern, what in IDENTIFIERS if pattern.search(value)]
        if found:
            problems.append(f"{path or 'report'} contains what looks like {', '.join(found)}. "
                            "The report should carry nothing that identifies them")
    return problems


def check_keys(data):
    problems = []
    for path, node in walk(data):
        if not isinstance(node, dict):
            continue
        known = KNOWN_KEYS.get(generic(path))
        if known is None:
            problems.append(f"{path} is an object the page never looks at, so nothing "
                            "inside it renders")
            continue
        for key in node:
            if key not in known:
                problems.append(f"{path + '.' if path else ''}{key} is not a key the page "
                                f"reads, so it renders nothing. Expected one of: "
                                f"{', '.join(sorted(known))}")
    return problems


def check_clocks(data):
    """at and span are columns on a twelve-column track. Out of range, a step is
    clamped and silently lands somewhere it was not meant to."""
    problems = []
    for i, lane in enumerate(data.get("horizon", {}).get("clocks", {}).get("lanes", [])):
        for j, step in enumerate(lane.get("steps", [])):
            at, span = step.get("at"), step.get("span")
            where = f"horizon.clocks.lanes[{i}].steps[{j}] '{step.get('label', '?')}'"
            if not isinstance(at, int) or not isinstance(span, int):
                problems.append(f"{where} needs at and span as whole numbers of columns")
            elif at < 0 or span < 1 or at + span > 12:
                problems.append(f"{where} runs from column {at} for {span}, outside the "
                                "twelve-column track. It will be clamped and land wrong")
    return problems


def check_enums(data):
    notes = []
    for path, value in walk(data):
        if not isinstance(value, str):
            continue
        allowed = ENUMS.get(generic(path))
        if allowed and value not in allowed:
            notes.append(f"{path} is '{value}', which the page does not colour. "
                         f"Use one of: {', '.join(sorted(allowed))}")
    return notes


def check_length(data, limit, whole):
    """A direction report is read by someone deciding, not studying. Long fields
    are the failure mode: the report turns into prose and stops being scannable.
    The whole-report figure is the backstop: a report with every section filled
    comes to about twelve hundred words, so well past that is padding."""
    notes = []
    total = 0
    for path, value in walk(data):
        if not isinstance(value, str):
            continue
        words = len(value.split())
        total += words
        if words > limit:
            notes.append(f"{path} runs to {words} words. Over {limit} it reads as prose; "
                         "split it or cut it")
    if total > whole:
        notes.append(f"the whole report runs to {total} words, over {whole}. Every section "
                     "filled comes to about twelve hundred, so something here is padded")
    return notes, total


def check_name(data):
    """Initials are two tokens and name nobody; a full name is two tokens and names
    somebody. Counting tokens alone rejected the more private of the two."""
    name = str(data.get("meta", {}).get("name", "")).strip()
    parts = name.split()
    initials = bool(parts) and all(len(p.rstrip(".")) <= 1 for p in parts)
    if len(parts) > 1 and not initials:
        return [f"meta.name is '{name}'. A first name or initials is enough, and the "
                "report travels better without a full one"]
    return []


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("report", help="the filled direction-report.html")
    parser.add_argument("--max-field-words", type=int, default=45)
    parser.add_argument("--max-words", type=int, default=1400)
    args = parser.parse_args()

    data, problems = read_report(args.report)
    if data is None:
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        return 1

    problems = (check_sources(data) + check_horizon(data) + check_demand(data)
                + check_identifiers(data) + check_keys(data) + check_clocks(data)
                + check_name(data))
    notes = check_enums(data)
    length_notes, total = check_length(data, args.max_field_words, args.max_words)
    notes += length_notes

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

    sections = [k for k in KNOWN_KEYS[""] if data.get(k)]
    print(f"{len(sections)} section(s) filled: {', '.join(sorted(sections))}")
    print(f"{total} words in total, against a ceiling of {args.max_words}.")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
