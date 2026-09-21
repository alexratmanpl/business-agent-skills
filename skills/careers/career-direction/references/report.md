# Filling and shipping the report

Read this at the step that writes the report. `SKILL.md` says to build it and to run the
checker; this says what goes in it and what to do when it cannot be opened.

## The file

One self-contained page: `direction-report.html`. Fill it by replacing the data inside its
`report-data` block and changing nothing else. That block is strict JSON (JavaScript
Object Notation): double quotes on every key and string, no trailing commas, no comments.
The page says so on screen when it is wrong.

Every section is optional and hides itself when empty, so a first pass can ship with
evidence, gaps and families alone. A first pass that ships that way still ends with what
could not be established — that is `sources.notConfirmed`, and it is the one section a
partial report cannot leave out.

## The contract

The example inside the page is the contract. Most keys explain themselves; a few do not.

- `demandN` is a count of open positions and is what the chart plots, so an estimate there
  is a lie with a dot on it.
- `pay` is what the family's best-paying reachable grade pays. `entryBar` is what its
  lowest rung pays and what that paying grade demands in years, tickets and licences —
  both, because a family priced only at its ceiling reads as reachable when it is not.
- `sourcing` is `confirmed` when two independent sources back the row, `unconfirmed` when
  one does.
- `weight` is what a gap costs: decides, slows, closes doors.
- `when` is how soon a position is worth applying for: now, build, later.
- `at` and `span` place a step on a twelve-column track, and the axis labels decide what a
  column means, so the columns need not be evenly spaced in time.

## What the page demands

- **No prose in the analysis.** Cards, chips, tables, a timeline, two lanes and one chart.
  The lede and the shape are the two places a sentence belongs; everywhere else, if a
  point needs a paragraph, the thinking behind it is not finished.
- **Every claim names its source**, and their own account is marked as their own. The
  difference between "four people said it" and "he says" is the whole value of the
  document.
- **Nothing over about forty-five words**, and the whole report under about fourteen
  hundred. It is read by someone deciding, not studying. The example is a full one, every
  section filled, at just over twelve hundred — so a report at the top of the
  three-to-five family range is close to the ceiling, and the way back under it is fewer
  families, not thinner rows.
- **Estimates say they are estimates.** Odds are estimates. Counts are not.
- **A gap with no weight** cannot be acted on.
- **Unknown is not the same as absent**, and the reader has to be able to tell which one a
  silence is.

## Before handing it over

The failures here are silent: a broken report looks finished. The checker is what catches
them, and `SKILL.md` says to run it. Two things it cannot do for you.

It cannot tell evidence that is entirely self-assessment from evidence that is sourced,
because marking a source as their own account is a legitimate answer. Count those rows
yourself.

It cannot see the page. Open it the way they will open it, click a filter, toggle the
theme, and look at it at phone width. Check that every section you filled is actually on
screen — a missing one is a mistyped key, not an empty life.

## When there is no browser, and when there is no code

Where code cannot run, work the checker's list by hand: a claim with no source, a forecast
with nothing dated behind it or nothing that could disprove it, demand asserted rather
than counted, a family missing its pay range, its entry bar or its corroboration mark,
contact details left in the file, a step outside the track, and any key the page does not
read.

Where no browser can open it, write the same sections as a document instead, keeping the
source marking, the gap weights and the two clocks. Only the chart is lost, and it becomes
one sentence: which families are hiring now, and which of those still pay at sixty.

## Getting it to them

Attach or send the file, write it to a folder they have connected, or leave it where they
can reach it, and tell them the filename either way. The page holds its own data inside
it, so the file is the whole record and they can hand it to someone or delete it in one
move.
