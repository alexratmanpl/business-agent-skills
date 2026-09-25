# The plan: format and reasons

Read this before writing any plan, with a path or without one. Headings and field names are exact, because `scripts/path_check.py` reads them. It checks the format, the dates, the links and the arithmetic set out below; where code cannot run, apply them by hand. Whether a claim is true, and a milestone well chosen, is judgement: the fact review covers it.

## A plan with a path

```markdown
# Learning path: <the goal in one line>

As of: 2026-09-25
Verdict: PATH
Effort: 40 h (E2)
Budget: fits

## Goal
- Performance: <what they will be able to do>
- Standard: <the level, and who or what judges it> (E1)
- Conditions: <timed, unaided, live, on stage, in which language…>
- Deadline: 2026-12-15
- Hours a week: 6
- Starting point: <what the evidence shows> (E7)
- Use: <what it is for>

## Verdict
<Two to four sentences: the evidenced effort against the hours available, citing evidence IDs.>

## Evidence
| ID | Claim | Quote | Source | Tier | Published | Checked | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E1 | <one fact> | "<the source's words>" | [Title](https://…) | 1 | 2026-03 | 2026-09-25 | confirmed |

## Path
### M1. <short name>
- Outcome: <a performance someone could watch or mark>
- Practice: <what they do, how often, with what feedback>
- Check: <how it is judged, by whom, against which criteria>
- Evidence: E1, E3
- Time: 6 h (E4)
- Resources: <optional; each one with its evidence ID>

## Checks
- Rubric: …
- Reviews: …
- Exit check: …
- Re-plan when: …
- Spaced review: …

## Not verified
- <what could not be established, and what would settle it>

## Verification
Checked 14 claims on 2026-09-25: 11 upheld, 2 corrected, 1 dropped.
- E4 corrected: …
- Dropped: …
```

Other sections, such as Money or Schedule, may be added. The ones above may not be renamed.

### The header

- **As of** is today's date as YYYY-MM-DD, taken from the environment. A plan more than 30 days old is re-checked before anyone relies on it.
- **Verdict** is `PATH` or `NO PATH`.
- **Effort** is the hours the evidence says reaching the standard takes from their starting point: one total, citing its row or giving `(estimate: <basis>)`. When the evidence covers more than their gap, such as a whole level when they are part-way, say so. Label any pro-rating as your estimate. The milestones must add up to at least this.
- **Budget** compares what the plan needs with the hours available. The plan needs the larger of Effort and the milestones' total. The hours available are hours a week times the weeks to the deadline.
  - `fits`: it fits with a week's hours to spare. With no deadline, it always fits, and the Verdict says how many weeks it takes.
  - `tight`: it fits with less than a week spare. Say what is cut first.
  - `unknown`: the hours a week or the deadline is `MISSING`.

  There is no `short`. When the hours cannot reach the standard, the plan is either for the smaller goal they do buy, which they have accepted, or NO PATH.

### The Goal

Exactly these seven lines; others, such as Money, may follow them. A line that could not be established reads `MISSING`, followed by what is known.

- **Performance, Standard and Conditions** define the goal. If any is `MISSING`, `none` or `TBD`, the verdict is NO PATH.
- **Performance** names something they will do, not an activity (see the outcome rule below).
- **Standard** cites a confirmed row about the field, not a `learner` row. When nobody outside sets it, it reads `self-set:` followed by what someone could check.
- **Deadline** is YYYY-MM-DD after As of, `none` or `MISSING`.
- **Hours a week** starts with the number they can count on. Given a range, the budget uses its low end; anything after the first figure is commentary.

### Evidence

The columns and what makes a row confirmed are set out in `references/research.md`. Each row has its claim, quote, source, tier, publication date or version, and the day it was read. Rows from tiers 1 to 4 carry a link: a page, or a DOI. A search results page or a chatbot answer is never a source. A tier-3 or tier-4 row is confirmed only with two links. Dates are written YYYY, YYYY-MM or YYYY-MM-DD. Nothing is published or read after today, and nothing was read more than 30 days ago. Write a literal `|` inside a cell as `\|`.

### Milestones

Headings read `### M1. <short name>`. Other third-level headings are not milestones. Each milestone has these fields:

- **Outcome.** A performance, with its condition, so that a stranger could say whether it happened. "Hold a ten-minute conversation about work, unprepared" is an outcome; "learn conversational phrases" is an activity. An outcome may not open with an activity. Examples: learn, study, explore, master, attend, watch, read, practise, get familiar with, develop an understanding of, complete a course. The exception is an activity with a measurable condition attached, as in "learn a tune by ear in 30 minutes".
- **Practice.** What they do, how often, and with what feedback.
- **Check.** How the work is judged, by whom, against which criteria. A feeling, such as "feel confident", is not a check.
- **Evidence.** The rows it rests on. At least one is a confirmed row about the field.
- **Time.** One total in hours, before any bracket, citing its row or giving `(estimate: <basis>)`. A rate, such as "3 × 50 min a week", is not a total.
- **Resources**, when given, cite the rows that show each one exists and is current.

### Checks

All five lines are required.

- **Rubric.** Anchors from the standard's own descriptors. Where it has none, write anchors from what its judges say, and label them as yours.
- **Reviews.** Write out the attempt review from `references/review.md` in full. The plan travels without this skill.
- **Exit check.** The real assessment's format, conditions and pass mark, on material they have not practised on. If no unseen material exists in the real format, use the closest official material and say so under Not verified.
- **Re-plan when** two checks are missed in a row, the hours fall a week behind, the standard announces a revision, or the deadline moves. Re-planning means running the verdict again, not squeezing the same path into less time.
- **Spaced review.** Record each mistake in the same words every time it recurs, and revisit it at spaced intervals until it stops.

### Not verified, and Verification

- **Not verified** is never empty. If everything the plan uses was confirmed, it says so.
- **Verification** opens with the line `Checked N claims on YYYY-MM-DD: A upheld, B corrected, C dropped.` A, B and C add up to N. Upheld and corrected together equal the rows left in the Evidence table. The review is dated on or after As of. One line follows for each correction and each drop.

## A plan with no path

```markdown
# Learning path: <the goal as they put it>

As of: 2026-09-25
Verdict: NO PATH

## Goal
<the seven lines, with MISSING where it applies>

## Verdict
This goal is not defined enough to build a learning path. <why>

## Versions of the goal
<optional: each version, its judge and its evidence IDs>

## What would change the verdict
- <the missing line or fact>: <the decision or fact that would supply it>

## Evidence
## Not verified
## Verification
```

These sections and no others. No Budget or Effort line, and no milestones, steps, weeks or stages under any heading or bold label. Versions of the goal may say what each version takes, but never how to practise. The Verdict opens with one of these sentences:

- "This goal is not defined enough to build a learning path."
- "The standard could not be verified."
- "Learning is not what stands between you and this goal."
- "These hours cannot reach this standard." Use it when they have turned down the smaller goal the hours do buy.

No item in the Verdict, the Versions of the goal or What would change the verdict is an activity. What would change the verdict lists decisions and facts they can supply. The Evidence table holds what the research did find.

## Building the milestones

Work backward from the standard. Backward design sets the order: the desired results, then the evidence that will show them, then the learning (Wiggins & McTighe, *Understanding by Design*, 2005).

- **Weight by the evidence.** Share of the marks, how many postings name it, where examiner reports say candidates fail. Once prerequisites are in place, the heaviest gap comes first.
- **Start from a diagnostic** unless the starting point is already evidenced. It is the first milestone.
- **A check uses the standard's own criteria** wherever the standard publishes them, such as marking schemes, descriptors and rubrics, and says who applies them.
- **Resources come from the ledger.** Only what was checked to exist and to match the current version of the standard.

## Designing the practice

These are defaults from the research on learning, averaged across many studies. Effects vary with the material and the learner, so where the field has its own evidence, that wins.

- **Retrieve rather than reread.** Practice testing and distributed practice were rated high utility; rereading, highlighting and summarising were rated low (Dunlosky et al., 2013, doi:10.1177/1529100612453266). In real classrooms, quizzing had a medium effect on achievement, g = 0.499 (Yang et al., 2021, doi:10.1037/bul0000309).
- **Space it.** The best gap between sessions grows with how long the material must be kept. As a share of that time, it shrinks (Cepeda et al., 2008, doi:10.1111/j.1467-9280.2008.02209.x). For spaced retrieval practice, expanding gaps did no better than equal ones overall. They did better the more often learners were tested (Latimier et al., 2021, doi:10.1007/s10648-020-09572-8).
- **Feedback on the work, not the person.** Hattie and Timperley judge feedback about the person, such as praise, the least effective kind (2007, doi:10.3102/003465430298487). In one meta-analysis, over a third of feedback interventions lowered performance (Kluger & DeNisi, 1996, doi:10.1037/0033-2909.119.2.254).
- **Worked examples for novices.** What helps a beginner can hinder someone more experienced (Kalyuga et al., 2003, doi:10.1207/S15326985EP3801_4). Fade them: turn the worked steps into problems for the learner, one after another (Renkl & Atkinson, 2003, doi:10.1207/S15326985EP3801_3).
- **Interleave what is easily confused.** Mixing categories helped most where they looked alike, as with paintings. For word lists, blocking did better (Brunmair & Richter, 2019, doi:10.1037/bul0000209).
- **Promise practice, not results.** Deliberate practice explained 26% of the variation in performance in games and under 1% in professions (Macnamara et al., 2014, doi:10.1177/0956797614535810). How that study defined practice is disputed (Ericsson & Harwell, 2019, doi:10.3389/fpsyg.2019.02396).
