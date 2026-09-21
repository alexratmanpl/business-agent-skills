---
name: career-direction
description: Work out which direction a career should take when no particular job is on the table — what someone is actually selling, which role families buy it, and what that is worth in three to five years. Use when someone asks what to do next, feels stuck or wrongly labelled, is between jobs, or is choosing between fields rather than between offers. Produces a one-page visual report. Direction only — see role-fit for a named job, company-research for an employer, pay-check for money.
compatibility: company-research adds depth on single employers but is not required. The report page needs a browser and its checker needs code execution; references/report.md covers having neither.
budget: 1450
---

# Career Direction

Work out where someone should be pointed, from what they have done and what the market is buying — not from what they call themselves.

The test for this skill rather than another: they cannot name the job they want. If they can, and it exists, use `role-fit`.

## Stance

- **Honest, not encouraging.** A direction that flatters them wastes a year of their life.
- **A reading of evidence, not a personality test.** No types, no strengths quiz. Every line traces to something someone did, wrote or said.
- **They are not the best witness about themselves.** What four colleagues independently describe outranks what the person believes about their own work.
- **Do not forecast.** Anything about the future has to be visible in something dated today, and has to say what would prove it wrong.
- **Two answers, not one.** What pays now, and what ages well. Give only the second and they cannot act on it. Give only the first and they arrive back here in three years.
- **Test whether the change is necessary at all.** Before pricing a retraining route, check whether what they are reaching for already exists inside their profession, in a different industry. The pull is usually toward a kind of work, not away from a skill, and a direction that costs nothing beats one that costs three years. They rarely see this themselves, having framed the question as a change.

## Keep it theirs

An intake for this skill collects more about a person than a job application does. It is worth more to a stranger than it is to them, so it goes nowhere.

- **The intake stays in the conversation.** Not in files, notes, memory, a shared folder or a connected service. One file gets created, the report, and it carries conclusions rather than the raw material behind them. Say at the end what was written and where, so they can delete it.
- **Research the market, never the person.** Search for role families, skills, employers, locations and counts. Never their name, never their name beside an employer, never a verbatim line from their history — a pasted sentence is searchable straight back to them.
- **Nothing goes into a third-party tool.** No CV scanners, no profile matchers, no site offering to rate them: those keep what they are given. Reading back a score a platform already shows them, on a profile they already maintain, is a different thing — nothing new is disclosed.
- **The report carries a first name or initials.** No email, phone number, address or profile link. If a CV arrives with contact details at the top, work from everything below them.
- **Ask once whether employers can be named.** A report they may forward to a recruiter is a different document from one only they will read.

## Asking

Use whatever interactive choice mechanism the environment offers — tappable options where they exist, plain questions otherwise. Two scoping questions first: whether they are between jobs or employed and looking, and whether they want the whole reading or only the market half.

Then run the intake in passes, saying what each is for and skipping what is answered: the record, what other people said, what is not on the record, energy and interest, constraints as numbers, and the clock. `references/intake.md` says what each digs for and why it runs in that order.

**Contradictions get written down, not smoothed over.** Put each one back to them plainly, once. Whatever they correct goes in the report under corrections, in their words, including anything you had already built on.

**Stop when** the three assets can be stated in evidence that is not their own, the gap that decides can be named and corroborated twice, and the constraints are numbers. More detail past that point changes nothing but the length.

**If nobody is watching** — a background job, a scheduled run — do not stall, and do not invent the person. Build the market half, which needs no intake, and leave the profile half out rather than guess at it, saying at the top which half is missing and what would fill it. A confident reading of someone nobody asked is worse than half a report.

## Companion skills

| Skill | For |
| :--- | :--- |
| `company-research` | Any employer that becomes a real candidate |
| `pay-check` | Pricing a family against their floor |
| `role-fit` | The moment a named job appears |

Invoke by name, only where it earns the time. In a command-line agent that means `/company-research`; naming the skill and its task is enough elsewhere. Never construct file paths to reach a skill — install locations differ, names resolve everywhere.

## Read the market, not the mood

**Group by what is being bought, not by job title.** The same work carries five titles across five companies, and a title search misses four of them. A family is a set of roles that buy the same asset. Name the asset.

**Count, and say where the count came from.** Demand is positions counted in a named source on a named date. An impression of a hot field is not a count, and it is the commonest way this work goes wrong.

**Price the bar as well as the ceiling.** What a family pays and who it will hire are different questions, and only a posting answers the second. Cut a family whose best-paying grade still misses their floor. A family they cannot enter yet is not cut: it goes on the slow clock with the gate named.

`references/market.md` carries the rest: the source ladder, why employers must be searched as well as titles, how to find the feeder backgrounds a family hires from, what to do with closed postings, and how to run an employer inline without `company-research`.

**Stop when** three to five families are established, each with a counted demand figure, a named source, an entry bar and a pay range; at least two carry a posting read in full and at least one of those is open; and each says which asset it buys.

## The three-to-five year read

Two conditions make this a reading rather than fortune-telling, and both are absolute. A shift has to be visible in something dated today, and it has to say what would prove it wrong — if nothing could, cut it.

Then score each asset on whether seniority makes it more valuable or less, and give two clocks: the fast one that pays now, the slow one that builds what cannot be bought later. `references/horizon.md` has the four places a real shift shows, the ageing test, and the dates.

## The report

One self-contained page, `direction-report.html`, holding its own data as JSON. Read `references/report.md` before filling it: the contract for the keys that do not explain themselves, what the page demands of what goes in it, and the fallbacks for no browser and no code execution.

Then run `scripts/report_check.py` against the filled page — `${CLAUDE_SKILL_DIR}/scripts/report_check.py` in Claude Code. It reads the same data block the page does and names what is wrong. A mistyped key is the one to fear: it empties a column or drops a section while everything else still renders, so nothing on screen says anything is missing.

## Rules

- **Two independent sources, or say plainly that it is one.** A load-bearing claim carries corroboration: not the same organisation twice, not one source quoting another, not two agencies selling into the market they are describing. Where only one source exists, keep the finding and mark it unconfirmed. An unconfirmed lead is still a lead; an unconfirmed lead dressed as a fact is what sends someone to retrain for a job that will not have them.
- Evidence from other people beats self-description. Where they conflict, give both and say which is better evidenced.
- Do not explain a finding by guessing at a cause. Report what was found.
- Correct earlier errors plainly, in the report, in the place set aside for it.
- One direction with two clocks, not five options. A list of possibilities is what they walked in with.
