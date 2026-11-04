#!/usr/bin/env python3
"""Check a drafted daily brief against the shape in references/brief.md.

Fails on what makes a brief not a brief: a missing header line, an area with
too few or too many sentences, a link list outside three to five, a link
without a reason, a duplicated link, a link to a home page or search page, a
quote of fifteen words or more, the word "news", a Following block that is
neither a match nor the exact silence line, and an empty Not read section.
A NO BRIEF document is checked against its own, smaller shape.

What it cannot check: whether the stories picked were the right ones, whether
a sentence paraphrases a source closely without matching it, and whether the
window actually corresponds to the feeds read. Those are judgement.

Usage: brief_check.py BRIEF.md --date YYYY-MM-DD
Exit 0 when the brief passes; notes are printed but do not fail it.
"""

import argparse
import re
import sys
from urllib.parse import urlparse

SILENCE = "Nothing significant since the last brief."
MIN_SENTENCES, MAX_SENTENCES = 5, 10
MIN_LINKS, MAX_LINKS = 3, 5
MAX_QUOTE_WORDS = 15
FORBIDDEN_WORDS = ("news",)
FORBIDDEN_OPENERS = ("in other news", "meanwhile", "also")
ISO = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?(?:Z|[+-]\d{2}:\d{2})"

TITLE = re.compile(r"^# Daily brief: (AM|PM|NO BRIEF), (\d{4}-\d{2}-\d{2})\s*$")
HEADER = {
    "Window": re.compile(r"^Window: (?:none|(" + ISO + r") to (" + ISO + r"))\s*$"),
    "Persona": re.compile(r"^Persona: \S.*$"),
    "Areas": re.compile(r"^Areas: \S.*$"),
    "Following": re.compile(r"^Following: \S.*$"),
}
LINK_LINE = re.compile(
    r"^- \[(?P<title>[^\]]+)\]\((?P<url>https?://[^)\s]+)\) — (?P<why>[^(]+?)\s*\((?P<src>[^,)]+), (?P<time>\d{2}:\d{2})\)\s*$")
ANY_LINK = re.compile(r"\]\((https?://[^)\s]+)\)")
QUOTE = re.compile(r"[\"“]([^\"”]{3,})[\"”]")
WORD = re.compile(r"[0-9A-Za-z]")


def sentences(text):
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if WORD.search(p)]


def split_sections(lines):
    """Return (preamble, [(heading, [lines])]) for '## ' headings."""
    preamble, sections, current = [], [], None
    for line in lines:
        if line.startswith("## "):
            current = (line[3:].strip(), [])
            sections.append(current)
        elif current is None:
            preamble.append(line)
        else:
            current[1].append(line)
    return preamble, sections


def split_sub(lines):
    subs, current, lead = [], None, []
    for line in lines:
        if line.startswith("### "):
            current = (line[4:].strip(), [])
            subs.append(current)
        elif current is None:
            lead.append(line)
        else:
            current[1].append(line)
    return lead, subs


def check_links(block_lines, where, seen, problems, notes):
    link_lines = [l for l in block_lines if l.startswith("- ")]
    for line in link_lines:
        m = LINK_LINE.match(line)
        if not m:
            problems.append(f"{where}: link line is not '- [Title](url) — why (Source, HH:MM)': {line.strip()[:80]}")
            continue
        url = m.group("url")
        if url in seen:
            problems.append(f"{where}: link appears twice in the brief: {url}")
        seen.add(url)
        parsed = urlparse(url)
        if parsed.path in ("", "/") and not parsed.query:
            problems.append(f"{where}: link points at a home page, not an article: {url}")
        if "search" in parsed.path.lower() or parsed.query.lower().startswith(("q=", "query=")):
            problems.append(f"{where}: link points at a search page: {url}")
        if m.group("why").strip().lower() in ("read more", "more", "details", "full story"):
            problems.append(f"{where}: '{m.group('why').strip()}' is not a reason to open the link")
    return len(link_lines)


def check_prose(text, where, problems):
    for q in QUOTE.findall(text):
        if len(q.split()) >= MAX_QUOTE_WORDS:
            problems.append(f"{where}: a quote of {len(q.split())} words; the limit is under {MAX_QUOTE_WORDS}")
    for s in sentences(text):
        low = s.strip().lower()
        for opener in FORBIDDEN_OPENERS:
            if low.startswith(opener):
                problems.append(f"{where}: a sentence opens with '{opener}'")
    for w in FORBIDDEN_WORDS:
        if re.search(rf"\b{w}\b", text, re.IGNORECASE):
            problems.append(f"{where}: the word '{w}' appears; the brief is the opposite of a feed")


def check_area(name, lines, seen, problems, notes):
    text = "\n".join(lines)
    if "Links:" not in text:
        problems.append(f"{name}: no 'Links:' line")
        return
    before, after = text.split("Links:", 1)
    para = [l for l in before.strip().split("\n") if l.strip() and not l.startswith("- ")]
    n = len(sentences(" ".join(para)))
    if n < MIN_SENTENCES or n > MAX_SENTENCES:
        problems.append(f"{name}: {n} sentences; the shape is {MIN_SENTENCES} to {MAX_SENTENCES}")
    check_prose(" ".join(para), name, problems)
    links = check_links(after.split("\n"), name, seen, problems, notes)
    quiet = re.search(r"\bquiet\b", before, re.IGNORECASE)
    if links < MIN_LINKS and quiet and links >= 1:
        notes.append(f"{name}: {links} link(s) on a quiet day")
    elif links < MIN_LINKS or links > MAX_LINKS:
        problems.append(f"{name}: {links} links; the shape is {MIN_LINKS} to {MAX_LINKS}")


def check_following(lines, seen, problems, notes, declared):
    lead, subs = split_sub(lines)
    if any(l.strip() for l in lead):
        problems.append("Following: text before the first '### interest' heading")
    names = [h for h, _ in subs]
    if declared and names != declared:
        problems.append(f"Following: interests are {names}, the header says {declared}")
    for heading, body in subs:
        text = "\n".join(body).strip()
        where = f"Following/{heading}"
        if text == SILENCE:
            continue
        if SILENCE in text:
            problems.append(f"{where}: the silence line must stand alone")
            continue
        prose = [l for l in body if l.strip() and not l.startswith("- ")]
        n = len(sentences(" ".join(prose)))
        if n < 1 or n > 5:
            problems.append(f"{where}: {n} sentences; one to five, or the silence line")
        check_prose(" ".join(prose), where, problems)
        links = check_links(body, where, seen, problems, notes)
        if links < 1 or links > 3:
            problems.append(f"{where}: {links} links; one to three")


def check_not_read(lines, problems):
    body = [l for l in lines if l.strip()]
    if not body:
        problems.append("Not read: empty; list each feed skipped or write 'All feeds read.'")
        return
    if len(body) == 1 and body[0].strip() in ("All feeds read.", "No feeds tried."):
        return
    for l in body:
        if not l.startswith("- "):
            problems.append(f"Not read: not a '- feed: reason' line: {l.strip()[:60]}")


def check(text, today):
    problems, notes = [], []
    lines = text.split("\n")
    if not lines or not TITLE.match(lines[0]):
        return [f"title is not '# Daily brief: <AM|PM|NO BRIEF>, YYYY-MM-DD': {lines[0][:60] if lines else ''}"], notes
    edition, date = TITLE.match(lines[0]).groups()
    if today and date != today:
        problems.append(f"title date is {date}; today is {today}")

    preamble, sections = split_sections(lines[1:])
    header = {}
    for key, pattern in HEADER.items():
        found = [l for l in preamble if l.startswith(key + ":")]
        if not found:
            problems.append(f"header line '{key}:' is missing")
            continue
        if not pattern.match(found[0]):
            problems.append(f"header line is malformed: {found[0][:60]}")
        header[key] = found[0].split(":", 1)[1].strip()

    titles = [h for h, _ in sections]
    if edition == "NO BRIEF":
        for required in ("Why", "What would change it", "Not read"):
            if required not in titles:
                problems.append(f"NO BRIEF: section '## {required}' is missing")
        for h, body in sections:
            if h == "Not read":
                check_not_read(body, problems)
        return problems, notes

    if header.get("Window", "none") == "none":
        problems.append("Window: 'none' is only for NO BRIEF")
    else:
        m = HEADER["Window"].match("Window: " + header["Window"])
        if m and m.group(1) >= m.group(2):
            problems.append("Window: start is not before end")

    declared_areas = [a.strip() for a in header.get("Areas", "").split(",") if a.strip()]
    declared_follow = [] if header.get("Following", "none") == "none" else \
        [i.strip() for i in header["Following"].split(",") if i.strip()]

    seen = set()
    area_titles = [h for h in titles if h not in ("Following", "Not read")]
    if [a.lower() for a in area_titles] != [a.lower() for a in declared_areas]:
        problems.append(f"areas in the body are {area_titles}; the header says {declared_areas}")
    if declared_follow and "Following" not in titles:
        problems.append("Following: header lists interests but the section is missing")
    if not declared_follow and "Following" in titles:
        problems.append("Following: section present but the header says none")
    if "Not read" not in titles:
        problems.append("section '## Not read' is missing")

    for h, body in sections:
        if h == "Following":
            check_following(body, seen, problems, notes, declared_follow)
        elif h == "Not read":
            check_not_read(body, problems)
        else:
            check_area(h, body, seen, problems, notes)
    return problems, notes


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("brief", help="the drafted brief, markdown")
    parser.add_argument("--date", help="today's date, YYYY-MM-DD, as taken at the start")
    args = parser.parse_args()
    text = open(args.brief, encoding="utf-8").read()
    problems, notes = check(text, args.date)
    for n in notes:
        print(f"note  {n}")
    if problems:
        print(f"{len(problems)} problem(s):", file=sys.stderr)
        for p in problems:
            print(f"  {p}", file=sys.stderr)
        return 1
    print("ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
