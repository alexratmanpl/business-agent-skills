# Filling and shipping the report

## The file

One self-contained page, `assets/direction-report.html`. Copy it out of the skill folder and
fill the copy, never the template: left in the skill, a filled report is the next run's
example. Replace the data inside the copy's `report-data` block, `meta.eyebrow` and
`meta.footer` included, which say the example is invented, and change nothing else. That
block is strict JSON (JavaScript Object Notation): double quotes on every key and string, no
trailing commas, no comments. The page says so on screen when it is wrong. The page's script
is pinned by hash, so an edit to it blanks the page; the checker names the hash it needs.

Every section is optional and hides itself when empty, so a first pass of a whole reading
can ship with evidence, gaps and families alone. The exception is `sources.notConfirmed`,
what could not be established, which no report can leave out. Four sections are extras:
`habits` are what a buyer notices besides the skills, `thread` is the dated turns that show
one line through the career, `decisions` are questions only they can answer, and the
`glossary` spells out abbreviations.

A report that is the market only says so in `meta.lede`, and lists there which of these it
was not given: which skills are held, the floor, the place, the contract type they want. It
leaves out everything that needs the person: the sections `evidence`, `selling`, `gaps`,
`shape`, `habits` and `thread`, and in the rows the verdicts, `when`, odds, `worthTo` and
the clocks. Fill `evidence`, `selling` or `gaps` and it is a whole reading, which needs a
verdict on every family and a `when` on every position. With no `meta.name` its title reads
"Where next"; with someone present, a first name is fine, and the held and gap marks go in
`market.skills[].note`. They come from the record alone, and `meta.lede` says so.

## The contract

The example inside the page is the contract. Most keys explain themselves; a few do not.

- `meta.name` is a first name or initials. The page builds its title from it.
- `shape` is the one direction the families point to, in a sentence or two, and says whether
  it is reachable inside their profession.
- `constraints.hard` holds the figures that rule families out, `constraints.soft` the
  preferences, including what they want to be doing in ten years and what they refuse to
  keep doing.
- `demandN` is a count of open positions and is what the chart plots, so an estimate there
  is a lie with a dot on it. A family with no count that can be credited is left out of the
  table and named in `market.skipped`. `trend` is what the count did over time, with a cause
  only where a source gives one. The page always draws its column, so where nothing is known
  write `not established`. `market.asOf` is the date the counts were taken.
- `pay` is the range the best-paying grade pays, with its currency, how many postings stated
  it, the period and whether it is gross or net. Where a posting does not say, write "period
  not stated" or "gross or net not stated", and set it against their floor only on an
  assumption you name.
- `entryBar` is what the lowest rung pays, and what the best-paying grade demands in years,
  tickets and licences. Both, because a family priced only at its ceiling reads as reachable
  when it is not. Where no posting states one, write `not established`: that is a finding,
  and the family stays on the list. Where the postings show only one grade, put its pay in
  `pay`, what it demands in `entryBar`, and end `entryBar` with "one grade shown", adding
  "one posting" where that is all there is. A report with no clocks names a gate they cannot
  pass yet here.
- `sourcing` is `confirmed` when two independent sources each count the row, `unconfirmed`
  when one does. The chart draws an `unconfirmed` family as a hollow point.
- `buys` names the asset, the dominant one if a family buys more than one, and families that
  buy the same one are grouped under it. `why` is the reason this family is on the list.
  `ages` is how that asset ages: `well`, `badly`, or `mixed` where parts of it do each or
  nothing shows which.
- `weight` is what a gap costs: decides, slows, closes doors. Weigh it against the lead
  family, or against the family its `evidence` names when it matters to that one alone.
- A position's `evidence` is how well the seat itself is confirmed, not how well they fit
  it. The legend above the positions table, which sits in the page's markup and not in its
  data, gives the three grades, and an employer page counts only if it lists the seat
  itself. A position's `family` is the name of one of the families; a posting that fits none
  goes in `market.lines`.
- `status` is `open`, `closes`, `recurs` (posted again and again) or `closed`, and a closed
  posting that recurs is `recurs`. `statusDate` is the closing date for `closes`, the date
  it closed for `closed` where the posting shows one, and for the rest the date you saw the
  posting.
- `when` is how soon a position is worth applying for: now, build (after the fast clock's
  step), later (after the slow clock's). A seat that breaks a hard constraint, or that
  nothing they could build would open, is left out.
- `oddsNow` and `oddsAfter` are percentages, `15%` or `10-20%`: the page sorts on the
  largest number in them. Leave them out where nothing supports a figure.
- `at` and `span` place a step on a twelve-column track, counting columns from 0, and steps
  in a lane do not overlap. With N axis labels, label i (from 0) starts at column i×12÷N,
  rounded, so the columns need not be evenly spaced in time. On a phone each step shows the
  labels under its first and last column, so each label has to read on its own.
- `corrections` quote the claim they withdrew or narrowed, say what the record shows, and
  say what changed in the report. A claim they keep is not a correction, whatever reason
  they give: give both accounts in an `evidence` row and name the better-evidenced one, the
  dated or checkable one where both are theirs.
- `market.skipped` says which families were left out of the table, for the floor or for any
  other reason, and why, so nobody rediscovers them in a month. It shows even when nothing
  is left to chart. A cut that rests on one posting says so.

## Forwarding

A report that may be forwarded leaves out the floor, current pay, runway, notice period,
health, age, family circumstances and every employer's name, wherever it appears, and says
nothing about what was left out. Paraphrase requirement lines and titles: a quoted line is
searchable straight to the employer, so quotes belong in a report that stays private.
`employer` says only what kind of organisation it is, with no name, no size and nothing else
that would identify it, and the place goes in `loc`, as a city at most. The `constraints`
and the `corrections` keep the facts and leave out the reasons. Leave `market.skipped` out,
because what a cut family pays bounds the floor it missed; tell them in the conversation
which families were cut, for the floor or for length, and on how many postings. Findings
about named employers stay in the conversation. A private copy and a forwardable one are two
reports in two files, and the forwardable one is written from the facts, field by field,
never by deleting from the private one, whose sentences still carry what was left out.

## What the page demands

- **No prose in the analysis.** Cards, chips, tables, a timeline, two lanes and one chart.
  The lede and the shape may run to a few sentences; every other field is a phrase or two
  short sentences, and a point that needs a paragraph is not finished.
- **Every claim names its source**, and their own account is marked as their own: what other
  people say and what they say of themselves are different evidence. A person who is a
  source is named by role, never by name. `shape` and `selling` are your reading of the
  sources, and name none.
- **Nothing over forty-five words in a field**, and the whole report at most fifteen
  hundred: the checker notes both, and counts every word of every value, labels included.
  The example is a full one, every section filled, with three families, at about 1,450
  words: its fields average six words and only a few run past twenty, so write to that and
  treat forty-five as a ceiling. Each further family adds seventy to a hundred and fifty.
  Expect the first fill to run over. Tighten the longest fields first. Then cut in this
  order: the glossary (spell its abbreviations out in the rows), the thread, `decisions`,
  and the habits (move a red or amber one into `gaps` first). After the sections, cut the
  `note` and `cost` fields that quote no requirement line, state no unit and carry no held
  or gap mark. Then cut the weakest skill, shift and position rows: the one on the thinnest
  source or, for a skill, in the fewest postings. A family that will not fit goes in
  `market.skipped`, named, as left out for length; a report that may be forwarded says so in
  the conversation instead. Keep `corrections` and `sources.notConfirmed`.
- **Estimates say they are estimates.** Odds are estimates. Counts are not.
- **Unknown is not the same as absent**, and the reader has to be able to tell which one a
  silence is. What the intake could not settle, such as an unanswered question or a gap with
  one source, goes in `sources.notConfirmed`, stated as unknown.

## Before handing it over

A mistyped key is silent: the page draws an empty cell and the report looks finished. The
checker is what catches it. Four things it cannot do for you.

It cannot tell evidence that is entirely self-assessment from evidence that is sourced,
because marking a source as their own is a legitimate answer. Count those rows yourself, and
say in `meta.lede` when all of them are their own.

It finds the common shapes of an email address, a phone number, a street address and a
profile link, and no more. Read every value for one it missed, and for the name of anyone
but them.

It cannot read what a forwarded report gives away. If the report may be forwarded, read
every value in the finished file against the list of what to leave out, and do not save
those figures in a file to search with.

It cannot see the page. Open it the way they will open it, click a filter, toggle the theme,
and look at it at phone width. Check that every section you filled is on screen; one the
page could not draw is named in a banner at the top. If you cannot open it, say that you did
not. Screenshots are copies of the report: delete them when you have looked, or name them
when you say what was written.

## When there is no browser, and when there is no code

Where code cannot run, read the list at the top of `scripts/report_check.py` and its tables
(`SCHEMA`, `REQUIRED`, `ABOUT_THEM`, `PERSON`, `READING_ONLY` and `ENUMS`), and work them by
hand.

Where you have no browser, fill the page anyway and run the checker, which needs none; say
that you did not open it. Where they cannot open an HTML page, write the same sections as a
document instead, keeping the source marking, the gap weights and the two clocks. Only the
chart is lost, and it becomes one sentence: which families are hiring now, and which of
those still pay as seniority grows.

## Getting it to them

Attach or send the file, write it to a folder they have connected, or leave it in a folder
only they can read, never any project or a hosted page. Name the file for their first name
or initials, and say whether it is the forwardable one: a report that is not holds the
floor, the runway and the employers' names, and should not travel. The page holds its own
data inside it, so the file is the whole record: they can hand it to someone or delete it in
one move.

A run nobody is watching has no name to file the report under and nobody to hand it to: it
writes the file to the run's output folder as `market-scan-<date>.html`. Its final message
says where that is, whether the page was opened, which families were counted and which were
left out and why, and that the file can be deleted once read.
