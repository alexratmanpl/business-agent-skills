"""What scripts/path_check.py must do with a plan: the cases, and the edits that make them.

Each case takes one of the two example plans in this folder, breaks it the way a real mistake
would, and says what must happen: the exit code, and the words the problem list uses. A case
that expects exit 0 is as important as one that expects 1: a gate that blocks a sound plan sends
people looking for a way round it.

The rule behind a case is in references/plan.md or in the docstring of the script. A comment
above a group of cases quotes it where the name alone would not.
"""

from collections import namedtuple

Case = namedtuple("Case", "name edits code problems notes options absent")


def case(name, edits, code, problems=(), notes=(), options=(), absent=()):
    """problems: text the problem list (stderr) must hold. notes: text stdout must hold.
    options: command-line options. absent: text the problem list must not hold."""
    return Case(name, edits, code, list(problems), list(notes), list(options), list(absent))


def line(prefix, new, nth=1):
    """An edit that replaces the nth line starting with prefix. None removes the line, and a
    string with line breaks in it becomes several lines."""
    def edit(text):
        lines, seen = text.split("\n"), 0
        for i, existing in enumerate(lines):
            if existing.startswith(prefix):
                seen += 1
                if seen == nth:
                    lines[i:i + 1] = [] if new is None else [new]
                    return "\n".join(lines)
        raise AssertionError(f"the plan has no line {nth} that starts {prefix!r}")
    return edit


def after(prefix, new):
    """An edit that adds lines after the first line that starts with prefix."""
    def edit(text):
        lines = text.split("\n")
        i = next(i for i, existing in enumerate(lines) if existing.startswith(prefix))
        return "\n".join(lines[:i + 1] + [new] + lines[i + 1:])
    return edit


def row(row_id, column, value):
    """An edit that sets one cell of the Evidence table, in the row with this ID."""
    def edit(text):
        lines = text.split("\n")
        header = next(i for i, existing in enumerate(lines) if existing.startswith("| ID |"))
        names = [c.strip().lower() for c in lines[header].strip("|").split("|")]
        for i, existing in enumerate(lines):
            if existing.startswith(f"| {row_id} |"):
                cells = [c.strip() for c in existing.strip("|").split("|")]
                cells[names.index(column.lower())] = value
                lines[i] = "| " + " | ".join(cells) + " |"
                return "\n".join(lines)
        raise AssertionError(f"the plan has no row {row_id}")
    return edit


def edited(text, edits):
    """The plan with each edit made: a function from the text to the text, or an (old, new)
    pair of strings. A pair whose old text is not in the plan is a mistake in the case."""
    for edit in edits:
        if callable(edit):
            text = edit(text)
        else:
            old, new = edit
            assert old in text, f"the plan does not hold {old!r}"
            text = text.replace(old, new, 1)
    return text


# The lines of the plan with a path that cases change often.
def hours(text):
    return line("- Hours a week:", f"- Hours a week: {text}")


def budget(word):
    return line("Budget:", f"Budget: {word}")


def effort(text):
    return line("Effort:", f"Effort: {text}")


def deadline(text):
    return line("- Deadline:", f"- Deadline: {text}")


def performance(text):
    return line("- Performance:", f"- Performance: {text}")


def standard(text):
    return line("- Standard:", f"- Standard: {text}")


def outcome(milestone, text):
    return line("- Outcome:", f"- Outcome: {text}", nth=milestone)


def time_of(milestone, text):
    return line("- Time:", f"- Time: {text}", nth=milestone)


def verification(text):
    """The line of the Verification section that gives the counts of the fact review."""
    return line("Checked 5 claims", text)


# A deadline so far off that the plan fits at almost any hours a week. A case that reads the hours
# wrongly then passes the budget, instead of failing it for another reason.
FAR = deadline("2035-01-31")
# The Verdict sentence that works out the budget, in the plan with a path.
BUDGET_SENTENCE = ("Five hours a week for the 18 weeks to the deadline gives 91 hours, "
        "so it fits with more than a week to spare.")
# The plan's milestones add up to 64 h (3 and 61). A case that sets the first Time to 1.5 h makes
# the total 62.5 h, which the Effort line (64 h) then disagrees with, so the checker names it.
TOTAL_PROBLEM = "milestones add up to 62.5 h"
# A new row for the Evidence table, cited by nothing.
UNCITED_ROW = ('| E5 | A recovery week comes every fourth week | "Every fourth week is a recovery week." '
               "| [Plan C](https://example.org/plan-c) | 2 | 2025-06 | 2026-09-24 | confirmed |")
OPENINGS = [
    "This goal is not defined enough to build a learning path.",
    "The standard could not be verified.",
    "Learning is not what stands between you and this goal.",
    "These hours cannot reach this standard.",
]


PATH_CASES = [
    case("the example passes", [], 0,
         notes=["PATH: 4 evidence row(s), 3 confirmed; 2 milestone(s), 64 h",
                "E2: confirmed by two tier-3 sources"]),

    # The header: the day the plan's facts were true, and a verdict.
    case("no As of", [line("As of:", None)], 1, ["As of"]),
    case("As of in the future", [line("As of:", "As of: 2026-09-27")], 1, ["after today"]),
    case("As of one day ahead, for another time zone",
         [line("As of:", "As of: 2026-09-26"),
          verification("Checked 5 claims on 2026-09-26: 3 upheld, 1 corrected, 1 dropped.")], 0),
    case("As of 30 days ago", [line("As of:", "As of: 2026-08-26")], 0),
    case("As of 31 days ago", [line("As of:", "As of: 2026-08-25")], 1, ["31 days ago"]),
    case("As of earlier than today is a note", [line("As of:", "As of: 2026-09-20")], 0,
         notes=["not today"]),
    case("a verdict that is neither PATH nor NO PATH", [line("Verdict:", "Verdict: MAYBE")], 1,
         ["PATH or NO PATH"]),

    # Every section a plan with a path has.
    case("no Goal section", [("## Goal\n", "## Aim\n")], 1, ["no '## Goal' section"]),
    case("no Verdict section", [("## Verdict\n", "## Summary\n")], 1, ["no '## Verdict' section"]),
    case("no Evidence section", [("## Evidence\n", "## Sources\n")], 1, ["no '## Evidence' section"]),
    case("no Path section", [("## Path\n", "## Plan\n")], 1, ["no '## Path' section"]),
    case("no Checks section", [("## Checks\n", "## Review\n")], 1, ["no '## Checks' section"]),
    case("no Not verified section", [("## Not verified\n", "## Gaps\n")], 1,
         ["no '## Not verified' section"]),
    case("no Verification section", [("## Verification\n", "## Review of the facts\n")], 1,
         ["no '## Verification' section"]),
    case("a section of its own is allowed",
         [("## Not verified\n", "## Money\n- Nothing to buy.\n\n## Not verified\n")], 0),

    # The Evidence table: a fact with no source, no date, or a source read too long ago.
    case("an ID used twice", [row("E3", "ID", "E2")], 1, ["the ID is used twice"]),
    case("an ID that is not E and a number", [row("E3", "ID", "X3")], 1, ["IDs are E1, E2"]),
    case("an empty quote", [row("E1", "Quote", "")], 1, ["the quote is empty"]),
    case("a tier that is not 1 to 4 or learner", [row("E1", "Tier", "5")], 1, ["tier is '5'"]),
    case("a status that is not confirmed or unconfirmed", [row("E1", "Status", "maybe")], 1,
         ["status is 'maybe'"]),
    case("a tier-1 row with no link", [row("E1", "Source", "the rulebook")], 1, ["no link"]),
    case("a search results page as a source",
         [row("E1", "Source", "[Search](https://www.google.com/search?q=half+marathon)")], 1,
         ["a search results page"]),
    case("a chatbot answer as a source",
         [row("E1", "Source", "[Chat](https://claude.ai/chat/abc)")], 1, ["a chatbot answer"]),
    case("a DOI is a link", [row("E1", "Source", "doi:10.1000/182")], 0),
    case("confirmed on one tier-3 source",
         [row("E2", "Source", "[Plan A](https://example.org/plan-a)")], 1,
         ["confirmed on one tier-3 source"]),
    case("unconfirmed on one tier-3 source",
         [row("E2", "Source", "[Plan A](https://example.org/plan-a)"),
          row("E2", "Status", "unconfirmed")], 0),
    case("a row that nothing cites is a note",
         [after("| E4 |", UNCITED_ROW),
          verification("Checked 6 claims on 2026-09-25: 4 upheld, 1 corrected, 1 dropped.")], 0,
         notes=["evidence nothing cites: E5"]),
    case("a pipe inside a cell, escaped",
         [row("E1", "Claim", "A half marathon is 21.0975 km \\| 13.1 mi")], 0),
    case("a pipe inside a cell, not escaped",
         [row("E1", "Claim", "A half marathon is 21.0975 km | 13.1 mi")], 1,
         ["cells where the header has"]),
    case("Published empty", [row("E1", "Published", "")], 1, ["Published is empty"]),
    case("Published as month and year in words", [row("E1", "Published", "November 2025")], 1,
         ["YYYY-MM"]),
    case("Published after today", [row("E1", "Published", "2026-10")], 1, ["after today"]),
    # plan.md: dates are written YYYY, YYYY-MM or YYYY-MM-DD. One in that shape has to be a real day.
    case("Published with a month that does not exist", [row("E1", "Published", "2025-13")], 1,
         ["Published is '2025-13', which is not a real date"]),
    case("Published with month 00", [row("E1", "Published", "2025-00")], 1, ["not a real date"]),
    case("Published with a day that does not exist", [row("E1", "Published", "2025-11-31")], 1,
         ["not a real date"]),
    case("Published on 29 February in a year without one", [row("E1", "Published", "2025-02-29")], 1,
         ["not a real date"]),
    case("Published as a range of years", [row("E1", "Published", "2025-26")], 1,
         ["which is not a real date. If it is a version, write it as 'v2025-26'"]),
    case("Published on 29 February in a leap year", [row("E1", "Published", "2024-02-29")], 0),
    case("Published as a year", [row("E1", "Published", "2025")], 0),
    case("Published as a version", [row("E1", "Published", "v2.1")], 0),
    case("Published as a version that begins with a year", [row("E1", "Published", "2025.04")], 0),
    case("Published as undated is a note", [row("E1", "Published", "undated")], 0,
         notes=["no date or version"]),
    case("Checked not a date", [row("E1", "Checked", "last week")], 1, ["Checked is 'last week'"]),
    case("Checked after today", [row("E1", "Checked", "2026-10-02")], 1,
         ["checked 2026-10-02, after today"]),
    case("Checked 31 days ago", [row("E1", "Checked", "2026-08-25")], 1, ["31 days ago"]),
    case("Checked 30 days ago", [row("E1", "Checked", "2026-08-26")], 0),
    case("a source read 87 days ago", [row("E1", "Checked", "2026-06-30")], 1, ["87 days ago"]),
    case("a longer limit lets that source stand", [row("E1", "Checked", "2026-06-30")], 0,
         options=["--max-age-days", "90"]),

    # The goal: seven lines, and three of them define it.
    case("a Goal line missing", [line("- Use:", None)], 1, ["no '- Use:' line"]),
    case("Performance MISSING while the verdict is PATH", [performance("MISSING")], 1,
         ["Goal 'Performance'"]),
    case("Standard none while the verdict is PATH", [standard("none")], 1, ["Goal 'Standard'"]),
    case("Conditions TBD while the verdict is PATH",
         [line("- Conditions:", "- Conditions: TBD")], 1, ["Goal 'Conditions'"]),
    case("Performance that is an activity", [performance("Learn about racing")], 1,
         ["an activity"]),
    case("Performance that starts like a descriptor",
         [performance("Understand the main points of a race briefing")], 0,
         notes=["opens with 'Understand'"]),
    case("a Standard that cites no evidence",
         [standard("A chip time under 2:00:00 on a course measured to the official distance")], 1,
         ["cites no confirmed evidence about the field"]),
    case("a Standard that cites only the learner's own row",
         [standard("A chip time under 2:00:00 on a measured course (E4)")], 1,
         ["cites no confirmed evidence about the field"]),
    case("a self-set Standard that someone could check",
         [standard("self-set: a chip time under 2:00:00, read from the official results")], 0),
    case("a self-set Standard that is a feeling",
         [standard("self-set: finishing and being happy with it")], 1,
         ["A feeling cannot be checked"]),
    case("a self-set Standard that says nothing", [standard("self-set")], 1,
         ["self-set but does not say how"]),
    case("a starting point not yet known is a note",
         [line("- Starting point:", "- Starting point: MISSING")], 0,
         notes=["the starting point is missing"]),

    # The milestones: each one a performance, a check, and the sources it rests on.
    case("no milestones", [("### M1. Diagnostic", "### Diagnostic"), ("### M2. Long", "### Long")], 1,
         ["no milestones"]),
    case("a milestone with no Check", [line("- Check:", None, nth=2)], 1,
         ["M2 'Long run of 16 km': '- Check:' is missing or empty"]),
    case("a Check that is a feeling", [line("- Check:", "- Check: They will feel confident", nth=2)], 1,
         ["is not a check"]),
    case("an Outcome that is an activity", [outcome(2, "Study pacing")], 1,
         ["is an activity, not a performance"]),
    # plan.md: an Outcome may not open with an activity, unless a measurable condition goes with it.
    case("an activity with a measurable condition is a note",
         [outcome(2, "Study the pacing table for 3 hours")], 0,
         notes=["the outcome opens with 'Study'"]),
    case("an activity with a percentage as its condition",
         [outcome(2, "Practice paper: score 70% or above")], 0,
         notes=["the outcome opens with 'Practice'"]),
    case("an activity with a percentage, written 70 %",
         [outcome(2, "Revise until a mock paper scores 70 %")], 0,
         notes=["the outcome opens with 'Revise'"]),
    case("an activity with a percentage at the end",
         [outcome(2, "Practise past papers to 70%")], 0,
         notes=["the outcome opens with 'Practise'"]),
    case("Performance that is an activity with a percentage",
         [performance("Practise past papers to 70%")], 0,
         notes=["Goal 'Performance' opens with 'Practise'"]),
    case("an activity with no condition at all", [outcome(2, "Practice paper questions")], 1,
         ["is an activity, not a performance"]),
    case("an activity with a number that is no measure", [outcome(2, "Practice paper 2")], 1,
         ["is an activity, not a performance"]),
    case("a milestone that cites a row the table lacks",
         [line("- Evidence:", "- Evidence: E2, E9", nth=2)], 1,
         ["cites E9, which the Evidence table does not have"]),
    case("a milestone that cites no row",
         [line("- Evidence:", "- Evidence: the club plan", nth=2)], 1, ["Evidence names no row"]),
    case("a milestone that rests only on unconfirmed rows",
         [row("E2", "Status", "unconfirmed"), row("E3", "Status", "unconfirmed")], 1,
         ["M2 'Long run of 16 km': rests on nothing confirmed about the field"]),
    case("a milestone that rests only on the learner's own record",
         [line("- Evidence:", "- Evidence: E4", nth=1)], 1,
         ["rests on nothing confirmed about the field"]),
    case("a resource that cites a row",
         [after("- Time: 61 h", "- Resources: The club's training plan (E3)")], 0),
    case("a resource with no row",
         [after("- Time: 61 h", "- Resources: The club's training plan")], 1,
         ["every resource comes from the Evidence table"]),
    case("a Time that is a rate", [time_of(2, "3 x 50 min a week (E2)")], 1,
         ["is a rate, not a total"]),
    case("a Time with two amounts", [time_of(2, "61 h or 60 h (E2)")], 1, ["holds 2 amounts"]),
    case("a Time with no hours", [time_of(2, "plenty (E2)")], 1, ["has no hours in it"]),
    case("a Time that cites nothing", [time_of(2, "61 h")], 1,
         ["cites no evidence and gives no estimate basis"]),
    case("a Time in hours and minutes", [time_of(1, "1 h 30 (estimate: two timed efforts)")], 1,
         [TOTAL_PROBLEM]),
    case("a Time in minutes", [time_of(1, "90 min (estimate: two timed efforts)")], 1,
         [TOTAL_PROBLEM]),
    case("a Time in minutes, in capitals", [time_of(1, "90 MIN (estimate: two timed efforts)")], 1,
         [TOTAL_PROBLEM]),
    # Numbers are read as people write them: a point or a comma for decimals (1.5 and 1,5), and a
    # comma for thousands (2,200). A number that is neither is a problem, not a guess.
    case("a Time with a decimal point", [time_of(1, "1.5 h (estimate: two timed efforts)")], 1,
         [TOTAL_PROBLEM]),
    case("a Time with a decimal comma", [time_of(1, "1,5 h (estimate: two timed efforts)")], 1,
         [TOTAL_PROBLEM]),
    case("a Time with two decimals after a comma",
         [time_of(1, "1,50 h (estimate: two timed efforts)")], 1, [TOTAL_PROBLEM]),
    case("a Time with a comma for thousands", [time_of(2, "1,061 h (E2)")], 1,
         ["the plan needs 1064 h"]),
    case("a Time with a comma for thousands after two digits", [time_of(2, "10,061 h (E2)")], 1,
         ["the plan needs 10064 h"]),
    case("an Effort with a comma for thousands",
         [effort("2,200 h (estimate: the pace E2 gives)")], 1, ["Effort line says 2200 h"]),
    case("hours a week with a decimal comma", [hours("2,5")], 1, ["2.5 h a week"]),
    case("hours a week with a comma before three digits", [FAR, hours("2,500")], 1,
         ["Hours a week is '2,500'. Write the number as"]),
    case("hours a week with a malformed number", [FAR, hours("1,5000")], 1,
         ["Hours a week is '1,5000'. Write the number as"]),
    case("hours a week with two decimal points", [FAR, hours("1.5.5")], 1,
         ["Hours a week is '1.5.5'. Write the number as"]),
    case("hours a week with a malformed number, in bold under a bold label",
         [FAR, line("- Hours a week:", "- **Hours a week:** **2,500**")], 1,
         ["Hours a week is '**2,500**'. Write the number as"], absent=["Start it with a number"]),
    case("a Time with a leading point", [time_of(1, ".5 h (estimate: two timed efforts)")], 1,
         ["has a number the checker cannot read"]),
] + [
    # A number written with a space, an apostrophe or a stray comma is a problem, not a guess.
    case(f"a Time written {spelling!a}", [FAR, time_of(2, f"{spelling} (E2)")], 1,
         ["has a number the checker cannot read"])
    for spelling in ("1 200 h", "1 200 H", "1 2000 h", "0,750 h", "1234,567 h", "1'200 h",
                     "1\u2019200 h", "1\u00a0200 h", ",5 h", "1.2.5 h")
] + [
    case("a Time with a zero before a comma and two digits",
         [time_of(1, "0,75 h (estimate: two timed efforts)")], 1, ["milestones add up to 61.75 h"]),
    case("a Time in days", [time_of(2, "2.5 days (E2)")], 1, ["has no hours in it"],
         absent=["cannot read"]),
    case("a Time with a number that is neither",
         [time_of(1, "1,5000 h (estimate: two timed efforts)")], 1,
         ["has a number the checker cannot read"]),
    # A figure the checker cannot read stays a problem when a readable one stands beside it.
    case("a Time with a zero before a comma and three digits, beside minutes",
         [time_of(1, "0,750 h and 6 min (estimate: two timed efforts)")], 1,
         ["has a number the checker cannot read"], absent=["holds 2 amounts"]),
    case("a Time with a comma and four digits, beside minutes",
         [time_of(1, "1,5000 h and 6 min (estimate: two timed efforts)")], 1,
         ["has a number the checker cannot read"], absent=["holds 2 amounts"]),
    # Only the figure that has the unit is read. A count beside it is not a figure of hours.
    case("a Time with a space-grouped count beside the hours",
         [time_of(2, "61 h over 2 000 flashcards (E2)")], 0),

    # The budget: the hours the evidence asks for against the hours there are.
    case("Budget short", [budget("short")], 1, ["Budget is short"]),
    case("Budget that is not one of the three", [budget("fine")], 1,
         ["It has to be fits, tight or unknown"]),
    case("no Effort line", [line("Effort:", None)], 1, ["no 'Effort:' line"]),
    case("Effort higher than the milestones add up to",
         [effort("70 h (estimate: the pace E2 gives)")], 1,
         ["milestones add up to 64 h and the Effort line says 70 h"]),
    case("Effort that is a rate", [effort("4 h a week (estimate: the pace E2 gives)")], 1,
         ["Effort: '4 h a week"]),
    case("Effort that cites nothing", [effort("64 h")], 1, ["Effort: '64 h' cites no evidence"]),
    case("Deadline that is not a date", [deadline("next spring")], 1,
         ["Use YYYY-MM-DD, none, or MISSING"]),
    case("Deadline before the plan's date", [deadline("2026-09-01")], 1,
         ["is not after the plan's date"]),
    case("hours a week MISSING while the budget says fits", [hours("MISSING")], 1,
         ["Budget is fits but the hours a week are missing"]),
    case("hours a week MISSING while the budget is unknown",
         [hours("MISSING"), budget("unknown")], 0),
    case("Deadline MISSING while the budget is unknown",
         [deadline("MISSING"), budget("unknown")], 0),
    case("hours a week that start with no number", [hours("a few")], 1, ["Start it with a number"]),
    # plan.md: Hours a week starts with the number they can count on, a week's worth. Anything
    # after the first figure is commentary. The docstring of the script says which days still count.
    case("hours a week given per day", [hours("1 hour a day")], 1,
         ["Give hours a week, e.g. '5 hours a week'"]),
    case("hours a week given per day, as a rate", [hours("1 h/day")], 1, ["Give hours a week"]),
    case("hours a week given per day, with per", [hours("1h per day")], 1, ["Give hours a week"]),
    case("hours a week given every day", [hours("30 minutes every day")], 1,
         ["Give hours a week"]),
    case("hours a week given as daily", [hours("1 hour daily")], 1, ["Give hours a week"]),
    # The day is looked for after the figure, so a word set straight against it is a day too.
    case("hours a week with a day word stuck to the figure", [FAR, hours("5a day")], 1,
         ["Give hours a week"]),
    case("hours a week with daily stuck to the figure", [FAR, hours("5daily")], 1,
         ["Give hours a week"]),
    case("hours a week given each day", [FAR, hours("1 hour each day")], 1, ["Give hours a week"]),
    case("hours a week given per day, as a range", [hours("1-2 hours a day")], 1,
         ["Give hours a week"]),
    case("hours a week given per day, as a range with an en dash", [FAR, hours("1–2 hours a day")],
         1, ["Give hours a week"]),
    case("hours a week given per day, as a range with spaces round an en dash",
         [FAR, hours("1 – 2 hours a day")], 1, ["Give hours a week"]),
    case("hours a week given per day, as a range with an em dash", [FAR, hours("1—2 hours a day")],
         1, ["Give hours a week"]),
    case("hours a week given per day, as a range with spaces round an em dash",
         [FAR, hours("1 — 2 hours a day")], 1, ["Give hours a week"]),
    case("hours a week given per day, as a range with spaces round two hyphens",
         [FAR, hours("1 -- 2 hours a day")], 1, ["Give hours a week"]),
    case("hours a week given per day, then per week", [hours("1 hour a day, 5 days a week")], 1,
         ["Give hours a week"]),
    case("hours a week given in minutes, then every day after a comma",
         [FAR, hours("30 minutes, every day")], 1, ["Give hours a week"]),
    case("hours a week given in hours, then every day in brackets",
         [FAR, hours("1 hour (every day)")], 1, ["Give hours a week"]),
    case("hours a week given in hours, then daily after a comma",
         [FAR, hours("1 hour, daily")], 1, ["Give hours a week"]),
    case("hours a week that start with a word, not a number", [hours("daily, about 5 hours")], 1,
         ["Hours a week is 'daily, about 5 hours'. Give hours a week"]),
    case("hours a week with commentary after the figure",
         [hours("5, net of two weeks' holiday")], 0),
    case("hours a week with hours and commentary that names no day",
         [hours("5 hours, net of two weeks' holiday")], 0),
    case("hours a week with commentary in brackets that names a day",
         [hours("5 (about an hour a day)")], 0),
    case("hours a week with commentary after a comma that names a day",
         [hours("5, about an hour a day")], 0),
    case("hours a week with commentary after a dash that names a day",
         [hours("5 — roughly 1 h/day on weekdays")], 0),
    case("hours a week with commentary after an en dash that names a day",
         [hours("5 – about an hour a day")], 0),
    case("hours a week with commentary after a hyphen that names a day",
         [hours("5 - about an hour a day")], 0),
    case("hours a week with commentary after a semicolon that names a day",
         [hours("5; about an hour a day")], 0),
    case("hours a week that say a week, with a day in the commentary",
         [hours("5 hours a week (about an hour a day)")], 0),
    # A bare number is read as weekly, so commentary after it passes even when it names only a day.
    case("hours a week as a bare number, with a frequency in the commentary",
         [hours("5 (every day)")], 0),
    # A time unit straight after a bare number is that number's, in brackets or not. "Week" has to be
    # a word of its own: "weekdays" says no week.
    case("hours a week given in minutes, with the unit in brackets",
         [FAR, hours("30 (minutes a day)")], 1, ["Give hours a week"]),
    case("hours a week given in hours, with the unit in brackets",
         [FAR, hours("2 (hours a day)")], 1, ["Give hours a week"]),
    case("hours a week given as a rate, in brackets", [FAR, hours("30 (min/day)")], 1,
         ["Give hours a week"]),
    case("hours a week with its unit in brackets and a week named",
         [hours("5 (hours a week)")], 0),
    case("hours a week in minutes on weekdays, then a day after a comma",
         [FAR, hours("30 minutes on weekdays, 1 hour a day at weekends")], 1,
         ["Give hours a week"]),
    case("hours a week that say a week as wk", [hours("5 h/wk (about an hour a day)")], 0),
    case("hours a week that say weekly", [hours("5 hours weekly (about an hour a day)")], 0),
    case("hours a week that say a week in capitals",
         [hours("5 Hours a Week (about an hour a day)")], 0),
    # A week named before a day makes the day commentary, whatever sits between them, when the
    # figure is in hours or a bare number.
    case("hours a week that say a week, then a day after a double hyphen",
         [hours("5 hours a week -- about an hour a day")], 0),
    case("hours a week that say a week, then a day after an equals sign",
         [hours("5 hours a week = about an hour a day")], 0),
    case("hours a week in an abbreviation with a full stop, then a week and a day",
         [hours("5 hrs. a week (about 1 hr. a day)")], 0),
    case("hours a week with the week in brackets, then a day after a comma",
         [hours("5 hours (weekly), about an hour a day")], 0),
    case("hours a week as a bare number, then a day after a double hyphen",
         [hours("5 -- about an hour a day")], 0),
    case("hours a week as a bare number a day", [FAR, hours("5 a day")], 1, ["Give hours a week"]),
    case("hours a week in hours, then a day, in capitals",
         [FAR, hours("1 Hour. Every day.")], 1, ["Give hours a week"]),
    case("hours a week in minutes, with the unit in brackets and in capitals",
         [FAR, hours("30 (Minutes a day)")], 1, ["Give hours a week"]),
    case("hours a week in minutes after a comma", [FAR, hours("30, minutes a day")], 1,
         ["Give hours a week"]),
    # Emphasis marks come off the field first. An underscore is a word character, so left on it
    # would hide the end of "day" from the pattern for a day, and a bold figure would not be one.
    case("hours a week with the day in italics", [FAR, hours("5 hours, _about an hour a day_")], 1,
         ["Give hours a week"]),
    case("hours a week with a bold figure under a bold label",
         [line("- Hours a week:", "- **Hours a week:** **5** hours a week")], 0),
    # Only a bare number takes the unit that follows it, and only a word that is one.
    case("hours a week that say a week, then a comment that opens with a unit",
         [hours("6 hours a week (min 1 hour a day)")], 0),
    case("hours a week with its unit in brackets and a week named, then a day",
         [hours("5 (hours a week), 1 h a day on weekdays")], 0),
    case("hours a week as a bare number, then a comment that opens with minimum",
         [hours("5 (minimum an hour a day)")], 0),
    case("hours a week with a day in the commentary that is not a day a week",
         [hours("5 hours, plus an extra day at weekends")], 0),
    case("hours a week with commentary that holds a word beginning with day",
         [hours("6 hours (evenings, after a daytime job)")], 0),
    # A full stop or a colon followed by a space ends the figure's clause, as a comma does. Inside
    # a number it does not.
    case("hours a week with a sentence of commentary after a full stop",
         [hours("5 hours a week. About an hour a day.")], 0),
    case("hours a week as a bare number, then a sentence", [hours("5. About an hour a day.")], 0),
    case("hours a week with commentary after a colon",
         [hours("5 hours a week: about an hour a day")], 0),
    case("hours a week as a bare number, then a colon and a sentence",
         [hours("5: about an hour a day")], 0),
    case("hours a week as hours and minutes a day", [FAR, hours("1:30 a day")], 1,
         ["Give hours a week"]),
    case("hours a week in minutes, abbreviated with a full stop", [FAR, hours("30 min. a day")], 1,
         ["Give hours a week"]),
    case("hours a week as a decimal a day", [FAR, hours("1.5 hours a day")], 1,
         ["Give hours a week"]),
    # A week lets the day after it through only for hours. A figure that counts something else
    # is not hours, and the week after it belongs to what it counts. Minutes are not hours: the
    # script does not turn them into hours, so a week of minutes lets nothing through.
    case("hours a week counted in days a week, then minutes a day",
         [FAR, hours("5 days a week, 30 minutes a day")], 1, ["Give hours a week"]),
    case("hours a week counted in times a week, then minutes a day",
         [FAR, hours("5 times a week, 30 minutes a day")], 1, ["Give hours a week"]),
    case("hours a week counted in days a week, then minutes a day, in capitals",
         [FAR, hours("5 Days a Week, 30 Minutes a Day")], 1, ["Give hours a week"]),
    case("hours a week counted in sessions that begin like a unit, then minutes a day",
         [FAR, hours("5 hard sessions a week, 30 minutes a day")], 1, ["Give hours a week"]),
    case("hours a week in minutes with a week named, then a day in brackets",
         [FAR, hours("90 minutes a week (15 minutes a day)")], 1, ["Give hours a week"]),
    case("hours a week in minutes, abbreviated, with a week named, then a day",
         [FAR, hours("90 min/wk, about 15 min a day")], 1, ["Give hours a week"]),
    # A bare number owns the unit that opens the next clause, so the week in that clause is a week
    # of minutes, and it lets no day through either.
    case("hours a week in minutes in brackets, with a week named, then a day",
         [FAR, hours("90 (minutes a week), about 15 minutes a day")], 1, ["Give hours a week"]),
    case("hours a week in minutes in brackets, abbreviated, with a week named, then a day",
         [FAR, hours("90 (min/wk), 15 min a day")], 1, ["Give hours a week"]),
    case("hours a week in hours in brackets, with a week named, then a day",
         [hours("5 (hours a week), about an hour a day")], 0),
    # Whatever follows the figure that is neither an hour unit nor the end of its clause makes it a
    # count of something else: a letter, as in "5x", or a mark such as "×", "+" or "/".
    case("hours a week counted with an x, then minutes a day",
         [FAR, hours("5x a week, 30 minutes a day")], 1, ["Give hours a week"]),
    case("hours a week counted with a times sign, then minutes a day",
         [FAR, hours("5× a week, 30 minutes a day")], 1, ["Give hours a week"]),
    case("hours a week counted with a plus sign, then minutes a day",
         [FAR, hours("5+ days a week, 30 minutes a day")], 1, ["Give hours a week"]),
    case("hours a week counted with a slash, then minutes a day",
         [FAR, hours("5/week, 30 min/day")], 1, ["Give hours a week"]),
    case("hours a week in hours with words before the week, then a day",
         [hours("5 hours of study a week, about an hour a day")], 0),
    # The one reading left that rejects commentary: words after the figure that name no week, then
    # a day. A bare number has no words after it, so what follows it is commentary.
    case("hours a week that name a time and no week, with a day in brackets",
         [FAR, hours("5 hours (about an hour a day)")], 1, ["Give hours a week"]),
    case("hours a week with other words after the figure and no week, then a day",
         [FAR, hours("6 hard sessions with a coach, about an hour a day")], 1,
         ["Give hours a week"]),
    case("hours a week with a day after an equals sign, which does not end the figure's words",
         [FAR, hours("5 = about an hour a day")], 1, ["Give hours a week"]),
    case("hours a week with a day after a slash, which does not end the figure's words",
         [FAR, hours("5 / about an hour a day")], 1, ["Give hours a week"]),
    case("hours a week with a hyphen spaced before it only, which does not end the figure's words",
         [FAR, hours("5 -about an hour a day")], 1, ["Give hours a week"]),
    case("hours a week with a hyphen spaced after it only, which does not end the figure's words",
         [FAR, hours("5- about an hour a day")], 1, ["Give hours a week"]),
    case("hours a week with a day in square brackets, which do not end the figure's words",
         [FAR, hours("5 [about an hour a day]")], 1, ["Give hours a week"]),
    case("hours a week with a day in curly brackets, which do not end the figure's words",
         [FAR, hours("5 {about an hour a day}")], 1, ["Give hours a week"]),
    case("hours a week with weeks, which are not a week, before the day",
         [FAR, hours("5 hours, net of two weeks' holiday, about an hour a day")], 1,
         ["Give hours a week"]),
    case("hours a week as a range uses the low end", [hours("3-5")], 1, ["3 h a week"]),
    case("hours a week as a range written with to", [hours("3 to 5")], 1, ["3 h a week"],
         notes=["the budget uses 3, the low end"]),
    case("hours a week as a range is a note", [hours("5-6")], 0,
         notes=["the budget uses 5, the low end"]),
    # A range joins its numbers with a hyphen, an en or em dash, two hyphens or "to". The budget
    # uses the lower number, so the larger one first shows which it is.
    case("hours a week as a range with an em dash, the larger number first",
         [hours("5 — 3 on weekdays")], 1, ["3 h a week"],
         notes=["the budget uses 3, the low end"]),
    case("hours a week as a range with two hyphens, the larger number first",
         [hours("5 -- 3 on weekdays")], 1, ["3 h a week"],
         notes=["the budget uses 3, the low end"]),
    case("budget unknown though hours and deadline are given", [budget("unknown")], 1,
         ["Work it out"]),
    case("budget fits but the hours do not reach", [hours("3")], 1, ["That is short"]),
    case("budget fits with less than a week spare", [hours("3.6")], 1,
         ["less than a week spare"]),
    case("budget tight, and the verdict says what is cut first",
         [hours("3.6"), budget("tight"),
          (BUDGET_SENTENCE,
           "At 3.6 hours a week it is tight. If a week is lost, the easy weeks are cut first.")],
         0),
    case("budget tight and nothing says what is cut", [hours("3.6"), budget("tight")], 1,
         ["says what is cut first"]),
    case("budget tight with a week or more to spare", [budget("tight")], 1, ["That fits"]),
    case("no deadline, and the verdict says how many weeks",
         [deadline("none"), (BUDGET_SENTENCE, "At five hours a week it takes about 13 weeks.")], 0),
    case("no deadline, and the verdict does not say how many weeks",
         [deadline("none"), (BUDGET_SENTENCE, "At five hours a week it takes a few months.")], 1,
         ["does not say how many weeks it takes"]),
    case("no deadline with a budget that is not fits",
         [deadline("none"), budget("tight"),
          (BUDGET_SENTENCE, "At five hours a week it takes about 13 weeks.")],
         1, ["Budget is tight with no deadline"]),

    # The checks: five lines, all required.
    case("no Rubric line", [line("- Rubric:", None)], 1, ["no '- Rubric:' line"]),
    case("no Reviews line", [line("- Reviews:", None)], 1, ["no '- Reviews:' line"]),
    case("no Exit check line", [line("- Exit check:", None)], 1, ["no '- Exit check:' line"]),
    case("no Re-plan when line", [line("- Re-plan when:", None)], 1, ["no '- Re-plan when:' line"]),
    case("no Spaced review line", [line("- Spaced review:", None)], 1,
         ["no '- Spaced review:' line"]),
    # plan.md: Reviews is the attempt review from review.md, written out in full, which is a list.
    case("Reviews as a numbered list, indented under the line",
         [line("- Reviews:", "- Reviews:\n  1. Read the attempt against the rubric.\n"
                             "  2. Name the one change to make.")], 0),
    case("Reviews as a numbered list, flush left under the line",
         [line("- Reviews:", "- Reviews:\n1. Read the attempt against the rubric.\n"
                             "2. Name the one change to make.")], 0),
    case("Reviews as a numbered list, indented by one space",
         [line("- Reviews:", "- Reviews:\n 1. Read the attempt against the rubric.\n"
                             " 2. Name the one change to make.")], 0),
    case("Reviews as numbered items with a bracket, flush left",
         [line("- Reviews:", "- Reviews:\n1) Read the attempt against the rubric.\n"
                             "2) Name the one change to make.")], 0),
    # A numbered item can never start a field, so it belongs to the field above it, in any section.
    case("Practice as a numbered list, flush left under the line",
         [line("- Practice:", "- Practice:\n1. Run 5 km easy.\n2. Run 5 km hard.")], 0),
    case("Conditions as a numbered list, flush left under the line",
         [line("- Conditions:", "- Conditions:\n1. Timed.\n2. Unaided.")], 0),
    case("Reviews as text on the line below, indented",
         [line("- Reviews:", "- Reviews:\n  Read each attempt against the rubric.")], 0),
    case("Reviews with nothing after it", [line("- Reviews:", "- Reviews:")], 1,
         ["'- Reviews:' line is empty", "indented two spaces or numbered"],
         absent=["no '- Reviews:' line"]),
    case("Reviews with a blank line before its text",
         [line("- Reviews:", "- Reviews:\n\n  Read each attempt against the rubric.")], 1,
         ["'- Reviews:' line is empty"], absent=["no '- Reviews:' line"]),
    case("Reviews with a line of spaces before its text",
         [line("- Reviews:", "- Reviews:\n   \n  Read each attempt against the rubric.")], 1,
         ["'- Reviews:' line is empty"], absent=["no '- Reviews:' line"]),
    case("Reviews with its text indented by one space",
         [line("- Reviews:", "- Reviews:\n Read each attempt against the rubric.")], 1,
         ["'- Reviews:' line is empty"], absent=["no '- Reviews:' line"]),
    case("Reviews followed by bullets that are flush left",
         [line("- Reviews:", "- Reviews:\n- Read the attempt against the rubric.\n"
                             "- Name the one change to make.")], 1,
         ["'- Reviews:' line is empty"], absent=["no '- Reviews:' line"]),
    # The marker of a numbered item is not part of the field's text. An empty item leaves the field
    # empty, and the words after the marker are the words the checks read.
    case("Reviews as an empty numbered item, flush left",
         [line("- Reviews:", "- Reviews:\n1. ")], 1,
         ["'- Reviews:' line is empty"], absent=["no '- Reviews:' line"]),
    case("Reviews as an empty numbered item, indented",
         [line("- Reviews:", "- Reviews:\n  1. ")], 1,
         ["'- Reviews:' line is empty"], absent=["no '- Reviews:' line"]),
    # A marker with nothing after it, not even a space (an editor that trims spaces leaves that), is
    # an empty item too. It adds nothing to the field's text, and an item with text after it counts.
    case("Reviews as an empty numbered item with nothing after the marker, flush left",
         [line("- Reviews:", "- Reviews:\n1.")], 1,
         ["'- Reviews:' line is empty"], absent=["no '- Reviews:' line"]),
    case("Reviews as an empty numbered item with nothing after the marker, flush left, then an "
         "item with text",
         [line("- Reviews:", "- Reviews:\n1.\n2. Read the attempt against the rubric.")], 0),
    case("Conditions as an empty numbered item", [line("- Conditions:", "- Conditions:\n1. ")], 1,
         ["Goal 'Conditions' is 'empty'"]),
    case("hours a week as an empty numbered item",
         [line("- Hours a week:", "- Hours a week:\n1. ")], 1,
         ["Hours a week is ''. Start it with a number"]),
    case("an Outcome that is an activity, as a numbered item",
         [line("- Outcome:", "- Outcome:\n1. Study pacing", nth=2)], 1,
         ["is an activity, not a performance"]),
    case("an Outcome that is an activity, as an indented item with a bracket",
         [line("- Outcome:", "- Outcome:\n  1) Study pacing", nth=2)], 1,
         ["is an activity, not a performance"]),
    case("Performance that is an activity, as a numbered item",
         [line("- Performance:", "- Performance:\n1. Learn about racing")], 1, ["an activity"]),
    case("hours a week as a numbered item",
         [line("- Hours a week:", "- Hours a week:\n1. 5 hours, weekday evenings")], 0),
    case("hours a week as an indented numbered item, then a day in its own words",
         [FAR, line("- Hours a week:", "- Hours a week:\n  1. 1 hour a day")], 1,
         ["Give hours a week"]),
    # A decimal at the start of a line is a number, not a marker.
    case("a Time on the line below, written 1.5 h",
         [line("- Time:", "- Time:\n  1.5 h (estimate: two timed efforts)")], 1, [TOTAL_PROBLEM]),

    # Text from the templates in plan.md, left in, reads as content to a check for "not empty".
    case("a placeholder left in the title",
         [line("# Learning path:", "# Learning path: <the goal in one line>")], 1,
         ["template text left in", "<the goal in one line>"]),
    case("a placeholder left in a milestone name", [line("### M1.", "### M1. <short name>")], 1,
         ["template text left in", "<short name>"]),
    case("a placeholder left in the Goal", [performance("<what they will be able to do>")], 1,
         ["template text left in"]),
    case("a placeholder left in Not verified",
         [line("- Whether the target pace", "- <what could not be established, and what would settle it>")],
         1, ["template text left in"]),
    case("an ellipsis left after a label in Checks", [line("- Rubric:", "- Rubric: …")], 1,
         ["template text left in", "Rubric: …"]),
    case("three dots left after a label in Verification", [line("- Dropped:", "- Dropped: ...")], 1,
         ["template text left in", "Dropped: ..."]),
    case("an ellipsis left after a bold label in Checks",
         [line("- Rubric:", "- **Rubric:** …")], 1, ["template text left in", "Rubric: …"]),
    case("three dots left after a bold label with its colon outside",
         [line("- Dropped:", "- **Dropped**: ...")], 1, ["template text left in", "Dropped: ..."]),
    case("a placeholder left in italics", [line("- Use:", "- Use: _<what it is for>_")], 1,
         ["template text left in the plan: '<what it is for>'"]),
    case("a link left as the template has it", [row("E1", "Source", "[Title](https://…)")], 1,
         ["template text left in the plan: 'https://…'"]),
    case("a link left as the template has it, with three dots",
         [row("E1", "Source", "[Title](https://...)")], 1,
         ["template text left in the plan: 'https://...'"]),
    case("angle brackets in a code span",
         [performance("Write a function that returns `<div>` markup")], 0),
    case("a generic type", [performance("Write a Stack<T> class in Java")], 0),
    case("an ellipsis in the middle of a sentence",
         [performance("Run 21.1 km on a road course … in under 2:00:00 without stopping")], 0),
    case("an ellipsis after a colon that goes on into a sentence",
         [performance("Meet the race rule: ...finish within the 3-hour cut-off")], 0),
    case("six placeholders left in the Goal",
         [line("- Use:", "- Use: <a> <b> <c> <d> <e> <f>")], 1,
         ["template text left in the plan: '<a>', '<b>', '<c>', '<d>'. Replace"],
         absent=["<e>"]),
    case("the same placeholder left twice", [line("- Use:", "- Use: <why> and <why>")], 1,
         ["template text left in the plan: '<why>'. Replace"]),
    case("the same placeholder left four times, then two more",
         [line("- Use:", "- Use: <a> <a> <a> <a> <b> <c>")], 1,
         ["template text left in the plan: '<a>', '<b>', '<c>'. Replace"]),
    case("a link in angle brackets",
         [line("- Use:", "- Use: A personal target, see <https://example.org/rules>")], 0),
    case("an address in angle brackets",
         [line("- Use:", "- Use: A personal target, ask <jane@example.org>")], 0),
    case("less-than and greater-than signs as comparisons",
         [performance("Run every 5 km split <6:10 and the last one >5:30")], 0),
    case("a placeholder left in an Evidence claim", [row("E1", "Claim", "<one fact>")], 1,
         ["template text left in", "<one fact>"]),
    case("an HTML tag in an Evidence claim, which only backticks clear",
         [row("E1", "Claim", "A half marathon is 21.0975 km <br> 13.1 mi")], 1,
         ["template text left in the plan: '<br>'", "`backticks`"]),
    case("a quote with angle brackets in the Evidence table",
         [row("E1", "Quote", '"Enter <Distance> in metres."')], 0),
    case("a quote with angle brackets in an indented row of the Evidence table",
         [row("E1", "Quote", '"Enter <Distance> in metres."'), ("\n| E1 |", "\n  | E1 |")], 0),

    # What was not verified, and the record of the fact review.
    case("Not verified empty", [line("- Whether the target pace", None)], 1,
         ["'Not verified' is empty"]),
    case("no Verification line", [verification(None)], 1,
         ["no line 'Checked N claims on YYYY-MM-DD"]),
    case("counts that do not add up",
         [verification("Checked 5 claims on 2026-09-25: 3 upheld, 1 corrected, 2 dropped.")],
         1, ["3 + 1 + 2 is not 5"]),
    case("kept claims that are not the rows in the table",
         [verification("Checked 6 claims on 2026-09-25: 4 upheld, 1 corrected, 1 dropped.")],
         1, ["Verification kept 5 claims and the Evidence table has 4"]),
    case("a fact review dated before the plan",
         [verification("Checked 5 claims on 2026-09-24: 3 upheld, 1 corrected, 1 dropped.")],
         1, ["before the plan's date"]),
    case("a fact review dated after today",
         [verification("Checked 5 claims on 2026-09-28: 3 upheld, 1 corrected, 1 dropped.")],
         1, ["after today"]),
    # plan.md: one line follows for each correction and each drop. A list item is a line; a bare
    # line cannot be told from a sentence of prose.
    case("corrections and drops as a numbered list",
         [("- E4 corrected:", "1. E4 corrected:"), ("- Dropped:", "2. Dropped:")], 0),
    case("corrections and drops as a numbered list with brackets",
         [("- E4 corrected:", "1) E4 corrected:"), ("- Dropped:", "2) Dropped:")], 0),
    case("corrections and drops as plain lines",
         [("- E4 corrected:", "E4 corrected:"), ("- Dropped:", "Dropped:")], 1,
         ["lists 0", "Give one line for each"]),
    case("a correction with no line", [line("- E4 corrected:", None)], 1,
         ["Verification counts 1 corrected and 1 dropped but lists 1"]),
    # The line with the counts is not one of the lines for the corrections and drops.
    case("the counts line as a numbered item, with no line for the correction",
         [verification("1. Checked 4 claims on 2026-09-25: 3 upheld, 1 corrected, 0 dropped."),
          line("- E4 corrected", None), line("- Dropped:", None)], 1,
         ["Verification counts 1 corrected and 0 dropped but lists 0"]),
    case("the counts line as a bullet, with no line for the correction",
         [verification("- Checked 4 claims on 2026-09-25: 3 upheld, 1 corrected, 0 dropped."),
          line("- E4 corrected", None), line("- Dropped:", None)], 1,
         ["Verification counts 1 corrected and 0 dropped but lists 0"]),
    case("the counts line as a bold bullet, with no line for the correction",
         [verification("- **Checked** 4 claims on 2026-09-25: 3 upheld, 1 corrected, 0 dropped."),
          line("- E4 corrected", None), line("- Dropped:", None)], 1,
         ["Verification counts 1 corrected and 0 dropped but lists 0"]),
    case("the counts line first in a numbered list",
         [verification("1. Checked 5 claims on 2026-09-25: 3 upheld, 1 corrected, 1 dropped."),
          ("- E4 corrected:", "2. E4 corrected:"), ("- Dropped:", "3. Dropped:")], 0),
    case("a correction line that begins with Checked",
         [("- E4 corrected:", "- Checked E4 against the page on 2026-09-25:")], 0),
]


NO_PATH_CASES = [
    case("the example passes", [], 0, notes=["NO PATH: 1 evidence row(s), 1 confirmed"]),
    case("Versions of the goal left out",
         [line("## Versions of the goal", None), line("- V1.", None), line("- V2.", None)], 0),
    case("an extra section", [("## Not verified\n", "## Next steps\n- Book a class.\n\n## Not verified\n")], 1,
         ["a NO PATH plan has only these sections"]),
    case("a Budget line", [after("Verdict:", "Budget: unknown")], 1, ["no Budget or Effort line"]),
    case("an Effort line", [after("Verdict:", "Effort: 40 h (E1)")], 1, ["no Budget or Effort line"]),

    # The opening: why there is no path, in one of four sentences, before anything else.
    case("the Verdict opens without saying why",
         [(OPENINGS[0], "Here is what I found.")], 1, ["opens by saying why"]),
] + [
    # The example opens with the first of them.
    case(f"the Verdict opens with '{opening}'", [(OPENINGS[0], opening)], 0)
    for opening in OPENINGS[1:]
] + [
    case("the Verdict opens in bold", [(OPENINGS[0], f"**{OPENINGS[0]}**")], 0),
    case("the Verdict opens after a bold label",
         [(OPENINGS[0], f"**Why there is no path.** {OPENINGS[0]}")], 0),
    case("the Verdict empty", [line("This goal is not defined", None)], 1,
         ["the Verdict section is empty"]),
    case("What would change the verdict empty",
         [line("- The performance:", None), line("- The conditions:", None)], 1,
         ["'What would change the verdict' is empty"]),
    case("Not verified empty", [line("- Whether the pass mark", None)], 1,
         ["'Not verified' is empty"]),
    case("no Verification line", [line("Checked 1 claim", None)], 1,
         ["no line 'Checked N claims on YYYY-MM-DD"]),
    case("no Evidence table at all",
         [line("| ID |", None), line("| --- |", None), line("| E1 |", None)], 1,
         ["the Evidence section has no table"]),
    case("no rows, and a review of none",
         [line("| E1 |", None),
          line("Checked 1 claim", "Checked 0 claims on 2026-09-25: 0 upheld, 0 corrected, 0 dropped.")],
         0),

    # plan.md: no milestones, steps, weeks or stages under any heading or bold label, and no
    # practice; Versions of the goal may say what a version takes, but never how to practise.
    case("a milestone heading", [after("## Versions of the goal", "### M1. Start")], 1,
         ["milestones or steps"]),
    case("a tenth milestone heading", [after("## Versions of the goal", "### M10. Finish")], 1,
         ["milestones or steps"]),
    case("a step heading", [after("## Versions of the goal", "### Step 1")], 1,
         ["milestones or steps"]),
    case("a week as a bold label", [after("## Versions of the goal", "**Week 1:** Cook one meal")], 1,
         ["milestones or steps"]),
    case("a Practice field", [after("## Versions of the goal", "- Practice: cook every day")], 1,
         ["milestones or steps"]),
    case("an Outcome field outside Versions of the goal",
         [after("## What would change the verdict", "- Outcome: a dinner for six")], 1,
         ["milestones or steps"]),
    case("an Outcome field inside Versions of the goal",
         [after("## Versions of the goal", "- Outcome: a dinner for six\n- Time: about 40 h")], 0),
] + [
    case(f"a {kind} '{words}'", [after("## Versions of the goal", text)], 1, ["milestones or steps"])
    for words in ("Milestones", "Steps", "Weeks 1-4", "Phases", "Days 1 to 5", "Stages", "Modules",
                  "Lessons", "Sessions")
    for kind, text in (("heading", f"### {words}"), ("bold label", f"**{words}:** cook one meal"))
] + [
    case("a heading that only starts like a step word",
         [after("## Versions of the goal", "### Weekly shop")], 0),
    # Documented limit (--help): wording is read by its shape, in some sections only. These two
    # shapes of a to-do list under What would change the verdict still pass.
    case("a heading 'Next steps' over a to-do under What would change the verdict",
         [after("## What would change the verdict", "### Next steps\n- Buy a beginner book")], 0),
    case("a bold label 'Meanwhile' over a to-do under What would change the verdict",
         [after("## What would change the verdict", "**Meanwhile:**\n- Buy a beginner book")], 0),
    case("a version under a heading", [after("## Versions of the goal", "### Version A")], 0),
    case("a stage named in the Verdict's prose",
         [("so nothing could show it was reached.",
           "so nothing could show it was reached. The exam has four stages.")], 0),

    # plan.md: no item in the Verdict, the Versions of the goal or What would change the verdict
    # is an activity.
    case("an activity in the Versions of the goal",
         [line("- V1.", "- V1. Learn about knife skills")], 1,
         ["under Versions of the goal is an activity"]),
    case("an activity in What would change the verdict",
         [line("- The conditions:", "- Watch a cooking course")], 1,
         ["under What would change the verdict is an activity"]),
    case("an activity in the Verdict",
         [after("This goal is not defined", "- Read a cookbook")], 1,
         ["under Verdict is an activity"]),

    # Text from the templates in plan.md, left in.
    case("a placeholder left in the Verdict",
         [("so nothing could show it was reached.", "so nothing could show it was reached. <why>")], 1,
         ["template text left in", "<why>"]),
    case("a placeholder left in Not verified",
         [line("- Whether the pass mark", "<as in a plan with a path>")], 1,
         ["template text left in"]),
    case("a placeholder left in Versions of the goal",
         [after("## Versions of the goal",
                "<optional: each version, its judge and its evidence IDs>")], 1,
         ["template text left in"]),
    case("a placeholder line left above the Evidence table",
         [after("## Evidence", "<the Evidence table as in a plan with a path, with no rows when "
                               "the research found nothing>")], 1,
         ["template text left in", "<the Evidence table as in a plan with a path"]),
]
