---
name: pay-check
description: Work out what someone should be paid and what to say about it — comparing a salary, day rate or offer against the local market, converting between employment and contracting, and reopening a number already given. Use when someone mentions a salary, day rate, offer, pay rise, what to ask for, or a recruiter asking their expectations. Includes a calculator so the arithmetic is right. Money only — see company-research, role-fit, interview-prep.
compatibility: Bundles a calculator script needing code execution. Without it, do the arithmetic explicitly and show every step.
---

# Pay Check

Work out the number, and what to say about it.

## Use the calculator

`scripts/rate_calc.py` in this skill's directory — `${CLAUDE_SKILL_DIR}/scripts/rate_calc.py` in Claude Code. Run `--help` to see what it covers, and trust that over anything written here: the script is updated on its own and this file is not. Every subcommand repeats the inputs it used, so quote its numbers together with those assumptions.

It holds no market data and reaches no network. Rates, percentages and day counts all come from you, which is what makes a result reproducible and a wrong assumption visible rather than buried in the total.

If code can't run, do the arithmetic explicitly and show every step: working days assumed, whether holiday is paid, exchange rate used.

A day rate quoted without saying whether holiday is paid can be out by a tenth. A contract rate compared to an employed salary with no adjustment for holiday, sick pay, pension and employer taxes is not a comparison.

## Asking

Use whatever interactive choice mechanism the environment offers — tappable options where they exist, plain questions otherwise. One round, three questions at most.

**If nobody is watching** — a background job, a scheduled run, a delegated task in an agentic workspace — do not stall waiting for an answer. Take the most useful default, state the assumption plainly in the output, and carry on.

## Ask first

- The number and its unit — year, month, day, hour.
- **Employment or contracting**, and whether holiday is paid. Not comparable without adjustment.
- Where — the country, and where the employer is based if different.
- What they earn now, and what they want.
- **What's already been said.** A number given in screening is an anchor; the job is usually to reopen it, not set it.
- **How urgent.** No income and one live process is a weak position. This changes the advice more than any market data.

## Find the range

Search local rates for that role, level and contract type. Be specific about the city. Use several sources and give a range — published salary data is thin and skewed.

Note when an employer based somewhere expensive pays local rates somewhere cheaper. Common, not scandalous, worth asking about directly.

## Say where they stand

Above, at, or below — plainly. If they're below their own market, and especially below what they already earn, say so. People undersell themselves between jobs and nobody tells them.

Name the cause if visible. The usual sequence: left a job, recruiter approached, gave a number under pressure before knowing the scope, now anchored. Recoverable, and naming it helps.

## Reopening a number

The mechanism is scope, not regret:

> "We discussed a rate on the basis of role X. If the scope is what the requirements describe, I'd want to revisit the number so it matches the actual job."

Nobody reasonable objects. Asking for more with no reason attached doesn't work.

## If asked first

- **Give a range**, bottom at a number they'd accept. Fast, but caps the outcome.
- **Ask their band first.** Reasonable, sometimes refused.
- **Defer once**, then answer. Buys information, can read as evasive.

Whichever — have a number ready. Improvising under pressure is how people anchor low.

## Shares and options

At a private company, a lottery ticket, not pay. Never count it as salary. Ask about vesting, sale, and leaving — but the cash number is the number.

## Say this if it applies

Only one or two live processes weakens a position more than any script repairs. Three conversations beats any negotiating tactic.
