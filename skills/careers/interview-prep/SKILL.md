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
- **Who and what format.** A recruiter, a hiring manager, a technical assessment and a founder are four different conversations.
- **Applied or approached?** Approached means leverage. Say so; most people forget it.
- **What's already been said**, especially money. A number given in screening is an anchor.
- **How far the domain is from them.** Whether they could hold a conversation in this field or only recognise its words. Ask; job titles do not show it.

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

If one is unavailable, do that step inline and mention once at the end that a fuller version exists. `references/without-companions.md` says what to cover.

If they decline the fit check, say once that preparation built on an untested view of fit can prepare them for the wrong conversation — then respect the answer.

## Stance

- **Honest, not encouraging.** Believing a false version of your own fit makes you perform worse.
- **Never help them overclaim.**
- **Mind the whole situation.** No income, anchored below market, or only one live process — say so. That matters more than anything about this interview.

## Build

- **What to expect at this stage.** A recruiter checks basics, budget, motivation. A hiring manager checks whether you can do the job. A founder checks whether you understand the business. A technical assessment checks whether you can hold a position under scrutiny, not recite the material. Open with a stated decision, and treat each follow-up as a test of it rather than a request for more scope. Leave room for how it holds up as the system grows. Before the round, they should be able to say in one sentence what they'd decide and what they're giving up.
- **The domain, where it is unfamiliar.** Explain the field before the brief rests on it.
- **The two or three things to land.** Not everything good about them — the points that answer this employer's actual worry. Lead with the one that reframes the rest.
- **The opening move.** Any elephant — title mismatch, career break, unrelated-looking background — gets scripted for the first few minutes. Early is control; late is an apology.
- **The weak spot, in words.** What they did, where it stops, what they'd learn. Rehearse the version where the interviewer pushes twice — the same drill covers a decision they have to defend in a technical assessment.
- **Questions to ask.** Three to five, each built on a research fact absent from the company's marketing — a strategic tension, an odd decision, a competitor doing the opposite. Two good ones beat eight generic.
- **Practical now.** References, a tool worth a weekend, anything the advert says about applications, travel, timing.

`references/brief.md` holds what counts as the domain explained, and what disqualifies a question.

## After a round

What was asked, what landed, what didn't, what the questions reveal about what they actually care about, what to fix next. Update the brief.

If they used the record, ask them to paste what it copied out. Working from that beats working from recall, and the gap between the two grows by the hour.

## The brief

Open with the company, the role, which round this is, the date, and who they are meeting. Then the sections from **Build**, in that order. Leave space at the end for what **After a round** captures.

Mark confidence: a **fact** carries a source and a date, a company claim is attributed — *they say* — and an estimate is labelled *roughly*. If something couldn't be established, say so rather than leaving a gap they'll fill with an assumption. Read `references/brief.md` before writing one; it holds the writing rules.

If code can run, check it with `scripts/plain_check.py` in this skill's directory — `${CLAUDE_SKILL_DIR}/scripts/plain_check.py` in Claude Code. The checker cannot see whether each question names the fact it came from, so read the questions against those facts yourself.

Save it, present it, offer a Word version.

## The record, for the call itself

Build `interview-record.html` for any conversation where they will be told things they need later, a recruiter screening call included. Skip it for scheduling and logistics, and for a hands-on session — a live coding round needs a different shape entirely, not a page of question cards.

Set `RECORD_ID`, `QUESTIONS` and `SIGNALS` at the top of its script. Then work the page before handing it over, opening it the way they will open it. Add a question, mark one answered, and cycle a signal chip. Reload and confirm the notes survived, then run **Copy everything** and read what comes out. Read `references/record.md` before building one; it explains the three settings and why each test step is there.

## Several companies

Keep processes distinct — different employers need different framings. Only one or two live? Say so. It's the commonest cause of accepting a bad offer.
