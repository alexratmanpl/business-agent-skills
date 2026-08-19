---
name: interview-prep
description: Prepare for a specific job interview at any stage, and write a short plain-language brief to read beforehand. Use when someone mentions an interview coming up, a recruiter approach, a screening call, what to ask an interviewer, or how to handle a hard question about their background. Also use after a round to work out what it revealed. Works with companion skills company-research, role-fit and pay-check; falls back to working alone.
compatibility: Companion skills company-research, role-fit and pay-check add depth but are not required. The bundled checker needs code execution; its rules can be applied by hand instead.
---

# Interview Prep

Get them into the room knowing more than the average candidate, aware of their weak points, holding questions worth asking.

## Locate them first

Don't assume this starts at the beginning.

- **Stage** — deciding whether to bother, first call, between rounds, final, or just finished one.
- **Who and what format.** A recruiter, a hiring manager, a technical assessment and a founder need different preparation.
- **Applied or approached?** Approached means leverage. Say so; most people forget it.
- **What's already been said**, especially money. A number given in screening is an anchor.

Skip anything settled.

## Ask what they want done

Preparation can involve up to four pieces of work. Doing all of them uninvited is slow, expensive, and often repeats what they already have. **Ask before starting.**

Offer these as choices, multiple selection:

- Research the company
- Check how well they fit the job
- Work out what to say about money
- Just prepare the conversation — the rest is already done

If they've already researched the company, ask them to paste what they have rather than assuming. Do not go looking through the file system for earlier work; ask, and let them point you at it.

**If nobody is watching** — a background job, a scheduled run, a delegated task in an agentic workspace — don't stall. Do all four, and say at the top of the output which parts were assumed rather than requested.

## Companion skills

| Skill | For |
| :--- | :--- |
| `company-research` | Researching the employer |
| `role-fit` | Whether they match the job |
| `pay-check` | Anything about money |

**Invoke by name, only for the pieces they asked for.** In a command-line agent that means `/company-research`; in a chat or agentic interface, naming the skill and its task is enough. Never construct file paths — install locations differ, names resolve everywhere.

If one is unavailable, do that step inline and mention once at the end that a fuller version exists.

- *Without company-research:* what they do and who pays them, funding and health, real competitors and how each describes itself, reviews with sample sizes, leadership. Prefer originals; vendor market analysis is advertising.
- *Without role-fit:* read the advert for bold text, anything marked essential, anything twice, and the "isn't for you if" list. Sort into meets, doesn't, unclear, unusual advantage. Give a verdict and probability. Never help them overclaim.
- *Without pay-check:* find the local range for role, level and contract type; say where they sit; give a way to reopen a number by tying it to scope.

If they decline the fit check, say once that preparation built on an untested view of fit can prepare them for the wrong conversation — then respect the answer.

## Stance

- **Honest, not encouraging.** Believing a false version of your own fit makes you perform worse.
- **Never help them overclaim.**
- **Mind the whole situation.** No income, anchored below market, or only one live process — say so. That matters more than anything about this interview.

## Build

- **What to expect at this stage.** A recruiter checks basics, budget, motivation. A hiring manager checks whether you can do the job. A founder checks whether you understand the business.
- **The two or three things to land.** Not everything good about them — the points that answer this employer's actual worry. Lead with the one that reframes the rest.
- **The opening move.** Any elephant — title mismatch, career break, unrelated-looking background — gets scripted for the first few minutes. Early is control; late is an apology.
- **The weak spot, in words.** What they did, where it stops, what they'd learn. Rehearse the version where the interviewer pushes twice.
- **Questions to ask.** Three to five, each built on a research fact absent from the company's marketing — a strategic tension, an odd decision, a competitor doing the opposite. Anything answerable from the homepage is wasted. Two good ones beat eight generic.
- **Practical now.** References, a tool worth a weekend, anything the advert says about applications, travel, timing.

## After a round

What was asked, what landed, what didn't, what the questions reveal about what they actually care about, what to fix next. Update the brief.

## The brief

Structure: `brief-template.md`.

It is read in the twenty minutes before a call, possibly on a phone, possibly by someone whose second language it is, and always by someone who is nervous. Everything below follows from that.

- **One to two pages**, a thousand words at most. What is left out can be asked about; what is unread cannot.
- **Plain words.** The plainest word that carries the meaning — "money raised from investors", not "Series B". Keep a term of art only when they need it in the room, then explain it once, where it first appears. Cut business filler entirely.
- **Spell out every abbreviation on first use**, in one of the two conventional forms: "applicant tracking system (ATS)" or "ATS (applicant tracking system)". Names they already know — CV, CEO, HR — don't need it.
- **One idea per sentence.** Twenty-five words is a useful ceiling; past that, split it. Two short sentences are read faster than one long one, and misread less often. Prefer the active form: shorter, and it names who acts.
- **Marked confidence**, because confident wrongness in an interview is expensive. A **fact** carries a source and a date. A company claim is attributed — *they say*. An estimate is labelled *roughly*. If something couldn't be established, say so rather than leaving a gap they'll fill with an assumption.
- **Glanceable.** Short sections. Questions in a numbered list. Scripted lines in block quotes so they can be found at speed. Bold only for what must not be missed — bold everywhere is bold nowhere.

If code can run, check it with `scripts/plain_check.py` in this skill's directory — `${CLAUDE_SKILL_DIR}/scripts/plain_check.py` in Claude Code. It flags phrasing that reads as machine-written, abbreviations used before being spelled out, long sentences and excess length. A checklist, not a judge. Otherwise apply the rules by hand.

Save it, present it, offer a Word version.

## Several companies

Keep processes distinct — different employers need different framings. Only one or two live? Say so. It's the commonest cause of accepting a bad offer.
