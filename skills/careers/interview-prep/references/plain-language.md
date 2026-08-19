# Plain language rules for the brief

The brief is read in the twenty minutes before a call, possibly on a phone,
possibly by someone whose second language it is, and always by someone who is
nervous. Everything here follows from that.

## Length

One to two pages, around a thousand words at most. A brief nobody finishes is
worse than a short one that misses something: what is left out can be asked
about, what is unread cannot.

Short sections with headings. Anything longer than a screen gets split.

## Words

Use the plainest word that carries the meaning. "Money raised from investors",
not "Series B funding". "Use", not "utilise". "Talk to", not "engage with".

Keep a term of art only when the candidate will need it in the room. Then
explain it once, in the sentence where it first appears.

Cut business filler entirely — leverage, stakeholder, best practice, ecosystem,
robust, seamless. It adds length and carries nothing a reader can act on.

## Abbreviations

Spell out every abbreviation the first time, in one of the two conventional
forms: "applicant tracking system (ATS)" or "ATS (applicant tracking system)".
After that the short form is fine.

Names universally known to the reader — CV, CEO, HR, UK — do not need it.

## Sentences

One idea per sentence. Twenty-five words is a useful ceiling; past that, split
it. Two short sentences are read faster than one long one, and misread less
often.

Prefer the active form. "The hiring manager decides" rather than "the decision
is made by the hiring manager" — it is shorter and it names who acts.

## Marking confidence

Confident wrongness in an interview is expensive, so the three kinds of claim
must look different on the page:

- **Fact** — carries a source and a date.
- **They say** — the company's own claim, attributed. Never presented as fact.
- **Roughly** — an estimate, labelled as one.

If something could not be established, say so rather than leaving a gap the
reader fills in with an assumption.

## Layout

The brief is glanceable, not literary. Questions in a clean numbered list.
Scripted lines in block quotes so they can be found at speed. Bold only for the
handful of things that must not be missed — bold everywhere is bold nowhere.

## Checking it

`scripts/plain_check.py` flags long sentences, abbreviations used before they
are explained, jargon, and excess length. It is a checklist, not a judge: every
flag has legitimate exceptions. Fix what is genuinely unclear and leave the rest.
