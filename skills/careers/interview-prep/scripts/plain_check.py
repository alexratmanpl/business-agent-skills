#!/usr/bin/env python3
"""Check a brief for the things that make it hard to read under pressure.

A checklist, not a judge. It reports and exits zero: every flag here has
legitimate exceptions, and a brief is for one reader in one situation. Read the
flags, fix what is genuinely unclear, ignore the rest.

Checks:
  long sentences     hard to parse quickly, especially in a second language
  abbreviations      used before being spelled out
  jargon             business filler that carries no information
  length             a brief is one to two pages, read in twenty minutes

Usage: plain_check.py BRIEF.md [--max-sentence-words 25] [--max-words 1000]
"""

import argparse
import re
import sys

# Filler with no legitimate use in a brief. Kept deliberately short: an advisory
# tool dies from noise, and a flag the reader disagrees with costs more than the
# one it catches. Words with a real use in context -- leverage as bargaining
# power, a robust test suite, a company's ecosystem -- are left out on purpose.
JARGON = {
    "circle back", "touch base", "move the needle", "low-hanging fruit",
    "deep dive", "going forward", "learnings", "ideate",
    "operationalise", "operationalize", "synergy", "synergies",
    "value-add", "best-in-class", "thought leader", "core competency",
    "north star", "utilise", "utilize",
    "world-class", "cutting-edge", "game-changing",
}

# Abbreviations a reader will not stumble over. Everything else gets flagged the
# first time it appears without an expansion.
KNOWN = {
    "CV", "CEO", "CTO", "CFO", "COO", "HR", "IT", "UK", "US", "USA", "EU",
    "VAT", "PDF", "OK", "AM", "PM", "Q1", "Q2", "Q3", "Q4", "AI",
}

ACRONYM = re.compile(r"\b([A-Z][A-Z0-9]{1,})\b")
SENTENCE_END = re.compile(r"(?<=[.!?])\s+")


def readable_lines(text):
    """Yield (line_number, text) for prose lines only.

    Code blocks, headings and table rows are skipped: none of them are read as
    sentences, and counting them produces flags nobody acts on.
    """
    in_code = False
    for number, line in enumerate(text.split("\n"), start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code or not stripped:
            continue
        if stripped.startswith(("#", "|", ">")) or set(stripped) <= set("-|: "):
            continue
        yield number, stripped


def check_sentences(lines, limit):
    for number, line in lines:
        body = re.sub(r"^[-*+]\s+|^\d+\.\s+", "", line)
        for sentence in SENTENCE_END.split(body):
            words = sentence.split()
            if len(words) > limit:
                preview = " ".join(words[:8])
                yield (number,
                       f"sentence of {len(words)} words (limit {limit}): {preview}...")


def check_abbreviations(text, lines):
    seen = set()
    for number, line in lines:
        for match in ACRONYM.finditer(line):
            token = match.group(1)
            if token in KNOWN or token in seen:
                continue
            seen.add(token)
            # Both conventional forms count as a definition:
            #   "applicant tracking system (ATS)"  -- acronym inside brackets
            #   "ATS (applicant tracking system)"  -- expansion inside brackets
            before = line[:match.start()].rstrip()
            after = line[match.end():].lstrip()
            if before.endswith("(") or after.startswith("("):
                continue
            yield number, f"'{token}' used without being spelled out"


def check_jargon(lines):
    for number, line in lines:
        lowered = line.lower()
        for term in sorted(JARGON):
            if re.search(rf"\b{re.escape(term)}\b", lowered):
                yield number, f"jargon: '{term}'"


def check_length(text, limit):
    words = len(text.split())
    if words > limit:
        pages = words / 500
        yield 0, (f"{words} words, roughly {pages:.1f} pages (limit {limit}). "
                  f"A brief is read in the twenty minutes before a call")


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("brief", help="the brief to check")
    parser.add_argument("--max-sentence-words", type=int, default=25)
    parser.add_argument("--max-words", type=int, default=1000)
    args = parser.parse_args()

    try:
        text = open(args.brief, encoding="utf-8").read()
    except OSError as error:
        print(f"cannot read {args.brief}: {error}", file=sys.stderr)
        return 2

    lines = list(readable_lines(text))

    findings = []
    findings += list(check_length(text, args.max_words))
    findings += list(check_sentences(lines, args.max_sentence_words))
    findings += list(check_abbreviations(text, lines))
    findings += list(check_jargon(lines))

    if not findings:
        print("nothing flagged")
        return 0

    for number, message in sorted(findings):
        where = f"line {number}" if number else "whole brief"
        print(f"{where}: {message}")

    print(f"\n{len(findings)} flag(s). None of these are errors — "
          f"fix what is genuinely unclear and leave the rest.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
