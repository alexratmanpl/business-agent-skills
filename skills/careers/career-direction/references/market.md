# Finding the families

The keys named here belong to the report: `references/report.md` explains those that need
it, and the example in `assets/direction-report.html` shows the rest.

## Where to look

Work down the sources, hardest to fake first. Employer career pages show where the money is
going. Job boards give counts; professional networks show who moved and when. Local-language
boards and public-sector portals carry roles the big boards never list. Recruiter posts and
communities say what the work is like.

**Search employers as well as titles.** Grouping by asset fails silently when it is only
half applied: nothing is absent from a keyword search's own results, so the search looks
finished. Build a list of employers who would plausibly buy the asset and read each one's
own job list whole. Expect the best-fitting role of a search to be one no keyword returned,
under a title nobody outside that company would think to type.

## An employer, with or without `company-research`

Where `company-research` runs, ask for its dossier in the reply and not as a file, because a
file named for an employer lists where they might apply. Where it is not installed or cannot
run here, do the employer step inline for each real candidate, an employer behind an open
position you read in full: one `market.lines` row each, or the conversation if the report
may be forwarded. Say once, when you hand the report over, that a fuller version exists.
With nobody to apply, no employer is a real candidate, so there is no employer step and
nothing to say. An employer done inline still needs: what they sell and who pays, funding or
results with dates, who competes, and what staff say with sample sizes; name a missing item
once, in `sources.notConfirmed`.

## Reading what you find

Write down in the conversation as you read, for each count its source, date, unit (positions
or listings) and any place filter, and for each pay its period and whether it is gross or
net. The report cannot be filled without them.

**Read the postings, not the salary guide.** Recruiter guides and market reports are
advertising for a placement business: useful for the ceiling, worthless for the gate. No
family goes on the list as reachable until real postings have been read and their
requirement lines quoted, or paraphrased where the report may be forwarded; a position's
`note` is where a quote goes.

**Count positions, not listings.** One advert on two boards, or under two titles, is one
position. Boards that syndicate each other are one source: take the original's count, and
give the larger figure in `demandNote`. Where independent sources differ, `demandN` is the
larger and `demandNote` gives both: counts from different sources are never added, nor are
counts for two search terms in one source, whose positions may overlap. Where a count cannot
be reduced to positions, say in `demandNote` that its unit is listings, or that the source
does not say.

Take a family's count from one source at a time, inside the place you were given. One
employer's own count may stand as `demandN` with `sourcing` `unconfirmed`, and `demandNote`
says whose it is. A title can span families, because its postings buy different assets. A
count for a title that no posting was read under goes under `sources.notConfirmed`, not into
a family. Where the postings read under it differ, or its count is visibly mixed, the count
goes to a family only when two postings read under that exact title, open or closed, buy
that family's asset, and until then goes under `sources.notConfirmed`. Where a source cannot
be filtered to the place, or does not say what it was filtered to, say so in `demandNote`,
or once in `meta.lede` when that holds for every count. A posting that leaves out its place
or its on-site days, or sits outside the place but is the only one read for its family, is
kept, and `loc` says so.

**Count the skills, not only the seats.** Read the requirement lines across the postings and
count which skills repeat, each position once. Where only a tally by listing exists, give it
and say in the skill's `note` that its unit is listings and how many were read. Where the
quoted lines do not reproduce a tally you hold, give the tally and name the mismatch under
`sources.notConfirmed`. This is the concrete part of the answer: a skill named in eight
positions out of nine is a fact about this month, not a trend. With a person in the
conversation, mark each one as already held or as a gap, because that is the list they can
act on tomorrow; for one held in part, say in its `note` what is missing. With nobody to
ask, mark none.

**Find the feeder backgrounds.** Where they cannot enter a family directly, employers keep a
list — spoken or not — of the previous jobs they accept as preparation. It is usually
written down in the industry's own "how to break into this" material. Find it, and where
there is a person in the conversation, check whether they are on it. Sometimes they are not,
and that is the finding: the money is real, the shortage is real, and the door is shut to
this person. Put what you find in `market.lines`, and name a path that is internal promotion
as such: it is not an entry route for someone outside that employer.

**Record closed and recurring postings.** A role that closed, or that is posted again and
again, is evidence that the seat exists, not an opportunity. Mark it `closed` or `recurs`
rather than counting it as live. A recurring advert inside a source's count stays in
`demandN`, which is the source's figure, and `demandNote` says so and gives the count
without it. One whose requirement lines name no skill or duty goes under
`sources.notConfirmed`, not into a family.

## When the sources run out

Stop searching when they do, not when the list looks finished. If fewer than three families
can be counted, fewer than two carry a posting read in full, or none of those postings is
open, report what stands and name what is missing in `sources.notConfirmed`. A short list
that says so is a finding; a padded one is not.

The report holds three families at the example's density, about 1,450 words
(`references/report.md` has the limits). Take notes in the conversation on four or five if
the sources give them, and expect the weakest to be left out for length.
