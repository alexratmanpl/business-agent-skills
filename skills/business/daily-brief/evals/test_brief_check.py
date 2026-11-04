#!/usr/bin/env python3
"""Cases for scripts/brief_check.py. Run: python3 -I evals/test_brief_check.py"""

import importlib.util
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = importlib.util.spec_from_file_location(
    "brief_check", os.path.join(HERE, "..", "scripts", "brief_check.py"))
bc = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bc)

TODAY = "2026-11-04"

GOOD = """# Daily brief: PM, 2026-11-04

Window: 2026-11-04T08:00+01:00 to 2026-11-04T20:00+01:00
Persona: investor
Areas: economy, politics
Following: oil prices, hormuz

## Following

### oil prices
Brent rose about six percent after a tanker was attacked off Oman and two shippers paused Gulf transits. OPEC trimmed its demand forecast the same morning.
- [Brent jumps as Gulf shipping pauses](https://example.com/brent-jumps) — the fullest account of what the shippers said (Financial Times, 14:10)

### hormuz
Nothing significant since the last brief.

## Economy
The ECB held rates and said the next move depends on wage data due in December. Markets had priced a cut, so short-dated yields rose. Two large banks reported better margins than expected and raised guidance. Retail figures for October were flat. The euro gained against the dollar for a third day. A strike at a major port in the north has entered its second week.

Links:
- [ECB holds rates, points to December data](https://example.com/ecb-holds) — the primary statement and the press conference transcript (ECB press releases, 14:45)
- [Bank earnings beat on margins](https://example.com/bank-earnings) — the numbers in one table (CNBC Economy, 08:30)
- [Port strike enters second week](https://example.com/port-strike) — what is actually blocked and for how long (BBC Business, 11:05)

## Politics
Parliament passed the budget bill on second reading by a narrow margin. Two coalition members abstained, which the opposition called a sign of a split. The government denied it and said the third reading is set for next week. A regulator opened an inquiry into a large platform's advertising practices. The EU Commission published its work programme for the coming year.

Links:
- [Budget passes second reading](https://example.com/budget-second) — the vote breakdown by party (BBC Politics, 17:20)
- [Regulator opens platform inquiry](https://example.com/platform-inquiry) — the terms of reference, two pages (Politico Europe, 09:50)
- [Commission work programme](https://example.com/work-programme) — the primary document (Politico Europe, 12:00)

## Not read
- ft-home: returned 403; paywalled, headline feed only
"""


def run(text, today=TODAY):
    return bc.check(text, today)


class BriefCheckTests(unittest.TestCase):

    def test_good_brief_passes(self):
        problems, notes = run(GOOD)
        self.assertEqual(problems, [], problems)
        self.assertEqual(notes, [])

    def test_wrong_date(self):
        problems, _ = run(GOOD, today="2026-11-05")
        self.assertTrue(any("today is 2026-11-05" in p for p in problems))

    def test_too_few_sentences(self):
        text = GOOD.replace(
            "The ECB held rates and said the next move depends on wage data due in December. "
            "Markets had priced a cut, so short-dated yields rose. ", "")
        problems, _ = run(text)
        self.assertTrue(any("Economy: 4 sentences" in p for p in problems), problems)

    def test_too_few_links_fails_unless_quiet(self):
        text = GOOD.replace(
            "- [Port strike enters second week](https://example.com/port-strike) — what is actually blocked and for how long (BBC Business, 11:05)\n", "")
        problems, notes = run(text)
        self.assertTrue(any("Economy: 2 links" in p for p in problems), problems)
        quiet = text.replace("A strike at a major port", "It was a quiet day otherwise; a strike at a major port")
        problems, notes = run(quiet)
        self.assertEqual(problems, [], problems)
        self.assertTrue(any("quiet day" in n for n in notes))

    def test_link_without_reason(self):
        text = GOOD.replace(
            "— the numbers in one table (CNBC Economy, 08:30)", "— read more (CNBC Economy, 08:30)")
        problems, _ = run(text)
        self.assertTrue(any("not a reason" in p for p in problems), problems)

    def test_malformed_link_line(self):
        text = GOOD.replace(
            "- [Bank earnings beat on margins](https://example.com/bank-earnings) — the numbers in one table (CNBC Economy, 08:30)",
            "- https://example.com/bank-earnings")
        problems, _ = run(text)
        self.assertTrue(any("link line is not" in p for p in problems), problems)

    def test_duplicate_link(self):
        text = GOOD.replace("https://example.com/work-programme", "https://example.com/budget-second")
        problems, _ = run(text)
        self.assertTrue(any("appears twice" in p for p in problems), problems)

    def test_home_page_link(self):
        text = GOOD.replace("https://example.com/work-programme", "https://example.com/")
        problems, _ = run(text)
        self.assertTrue(any("home page" in p for p in problems), problems)

    def test_long_quote(self):
        text = GOOD.replace(
            "The euro gained against the dollar for a third day.",
            "The bank said \"we see no reason to move before the data give us a clearer picture of the wage dynamics in the first quarter\".")
        problems, _ = run(text)
        self.assertTrue(any("quote of" in p for p in problems), problems)

    def test_word_news(self):
        text = GOOD.replace("Retail figures for October were flat.", "In economic news, retail figures were flat.")
        problems, _ = run(text)
        self.assertTrue(any("'news' appears" in p for p in problems), problems)

    def test_forbidden_opener(self):
        text = GOOD.replace("Retail figures for October were flat.", "Meanwhile, retail figures were flat.")
        problems, _ = run(text)
        self.assertTrue(any("opens with 'meanwhile'" in p for p in problems), problems)

    def test_following_silence_must_stand_alone(self):
        text = GOOD.replace(
            "### hormuz\nNothing significant since the last brief.",
            "### hormuz\nNothing significant since the last brief. Although shipping rates did move.")
        problems, _ = run(text)
        self.assertTrue(any("stand alone" in p for p in problems), problems)

    def test_following_matches_header(self):
        text = GOOD.replace("Following: oil prices, hormuz", "Following: oil prices")
        problems, _ = run(text)
        self.assertTrue(any("the header says" in p for p in problems), problems)

    def test_areas_match_header(self):
        text = GOOD.replace("Areas: economy, politics", "Areas: economy")
        problems, _ = run(text)
        self.assertTrue(any("areas in the body" in p for p in problems), problems)

    def test_not_read_empty(self):
        text = GOOD.replace("- ft-home: returned 403; paywalled, headline feed only\n", "")
        problems, _ = run(text)
        self.assertTrue(any("Not read: empty" in p for p in problems), problems)

    def test_no_brief_shape(self):
        text = """# Daily brief: NO BRIEF, 2026-11-04

Window: none
Persona: none
Areas: none
Following: none

## Why
There are no settings yet, and nobody is here to answer the setup question.

## What would change it
- A daily-brief.json, or one answer: which persona?

## Not read
- No feeds tried.
"""
        problems, _ = run(text)
        self.assertEqual(problems, [], problems)
        broken = text.replace("## What would change it\n- A daily-brief.json, or one answer: which persona?\n\n", "")
        problems, _ = run(broken)
        self.assertTrue(any("What would change it" in p for p in problems), problems)

    def test_bad_title(self):
        problems, _ = run("# Brief for today\n\nWindow: none\n")
        self.assertTrue(problems and "title is not" in problems[0])


if __name__ == "__main__":
    sys.exit(unittest.main(verbosity=1))
