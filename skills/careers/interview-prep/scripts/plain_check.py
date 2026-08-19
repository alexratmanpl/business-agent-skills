#!/usr/bin/env python3
"""Check a brief for the things that make it hard to read under pressure.

A checklist, not a judge. It reports and exits zero: every flag here has
legitimate exceptions, and a brief is for one reader in one situation. Read the
flags, fix what is genuinely unclear, ignore the rest.

Checks:
  long sentences     hard to parse quickly, especially in a second language
  abbreviations      used before being spelled out
  machine phrasing   words and stock phrases that read as AI-written
  length             a brief is one to two pages, read in twenty minutes

Usage: plain_check.py BRIEF.md [--max-sentence-words 25] [--max-words 1000]
"""

import argparse
import re
import sys

# Vocabulary that reads as machine-written. These are words that are rare in
# ordinary speech but common in model output, so their presence is informative.
#
# Words like "significant", "crucial", "comprehensive" and "additionally" are
# deliberately absent. Corpus work on post-2023 academic writing found those rose
# alongside the others but kept rising after the tells became known, precisely
# because they are ordinary words whose presence tells you nothing. Flagging them
# produces noise, and a checklist that cries wolf stops being read.
TELLS = {
    "delve", "intricate", "tapestry", "realm", "pivotal",
    "underscore", "underscores", "underscoring", "testament", "foster",
    "harness", "illuminate", "bolster", "showcase", "showcasing",
    "myriad", "plethora", "nuanced", "meticulous", "meticulously",
    "transformative", "revolutionize", "revolutionise", "seamless",
    "seamlessly", "ever-evolving", "multifaceted", "paramount", "resonate",
    "elevate", "streamline", "unlock", "vibrant",
    "profound", "holistic", "cutting-edge", "game-changing", "world-class",
    "utilise", "utilize", "synergy", "synergies",
}

# Stock phrases. Stronger signals than any single word: a person writing notes
# for their own interview does not reach for these.
STOCK_PHRASES = {
    "it's worth noting", "it is worth noting",
    "it's important to note", "it is important to note",
    "that being said", "at its core", "to put it simply",
    "a key takeaway", "shed light on", "sheds light on",
    "underscores the importance", "in today's", "in conclusion",
    "when it comes to", "plays a crucial role", "plays a vital role",
    "the ever-evolving", "in the realm of", "navigating the complexities",
}

# "It's not X, it's Y" and "not just X, but Y". Catalogued by Wikipedia editors
# as negative parallelism: a rhetorical shape that sounds emphatic and asserts
# nothing. Rare in writing meant to be read once, under time pressure.
PARALLELISM = re.compile(
    r"\b(?:it's|it is|this is|that's|that is)\s+not\s+(?:just\s+)?[^.,;]{2,40}[,.]?\s*"
    r"(?:it's|it is|it)\b|\bnot\s+just\s+[^.,;]{2,40},?\s+but\b",
    re.IGNORECASE)

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


def check_tells(lines):
    for number, line in lines:
        lowered = line.lower()
        hit_phrases = [p for p in sorted(STOCK_PHRASES) if p in lowered]
        for phrase in hit_phrases:
            yield number, f"stock phrase: '{phrase}'"
        for term in sorted(TELLS):
            # A word already reported as part of a stock phrase is one problem,
            # not two. Reporting it twice pads the count and buries the rest.
            if any(term in phrase for phrase in hit_phrases):
                continue
            if re.search(rf"\b{re.escape(term)}\b", lowered):
                yield number, f"reads as machine-written: '{term}'"
        match = PARALLELISM.search(line)
        if match:
            yield number, (f"negative parallelism: '{match.group(0).strip()}' — "
                           f"sounds emphatic, asserts nothing")


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
    findings += list(check_tells(lines))

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
