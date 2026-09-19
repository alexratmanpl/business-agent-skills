# Writing the brief

The writing rules behind **The brief** in `SKILL.md`. Read this before writing one.

It is read in the twenty minutes before a call. Possibly on a phone, possibly by someone whose second language it is, and always by someone who is nervous. Everything below follows from that.

- **One to two pages**, a thousand words at most. What is left out can be asked about; what is unread cannot.
- **Plain words.** The plainest word that carries the meaning — "money raised from investors", not "Series B". Keep a term of art only when they need it in the room, then explain it once, where it first appears. Cut business filler entirely.
- **Spell out every abbreviation on first use**, in one of the two conventional forms: "applicant tracking system (ATS)" or "ATS (applicant tracking system)". Names they already know — CV, CEO, HR — don't need it.
- **One idea per sentence.** Twenty-five words is a useful ceiling; past that, split it. Prefer the active form: shorter, and it names who acts.
- **Glanceable.** Short sections. Questions in a numbered list. Scripted lines in block quotes so they can be found at speed. Bold only for what must not be missed — bold everywhere is bold nowhere.

`scripts/plain_check.py` enforces the length, sentence-length and abbreviation rules and flags machine-sounding phrasing. It is a checklist, not a judge. Where code cannot run, these rules are the fallback and are applied by hand.
