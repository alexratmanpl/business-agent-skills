# Writing the brief

The rules behind **The brief** in `SKILL.md`. Read this while writing one.

It is read in the twenty minutes before a call, possibly on a phone, possibly by someone whose
second language it is, and always by someone who is nervous. Everything below follows from that.

- **One to two pages**, a thousand words at most. What is left out can be asked about; what is
  unread cannot.
- **Plain words.** The plainest word that carries the meaning — "money raised from investors",
  not "Series B". Keep a term of art only when they need it in the room, then explain it once,
  where it first appears. Cut business filler entirely.
- **Spell out every abbreviation on first use**, in one of the two conventional forms:
  "applicant tracking system (ATS)" or "ATS (applicant tracking system)". Names they already
  know — CV, CEO, HR — don't need it.
- **One idea per sentence.** Twenty-five words is a useful ceiling; past that, split it. Prefer
  the active form: shorter, and it names who acts.
- **Marked confidence**, because confident wrongness in an interview is expensive. A **fact**
  carries a source and a date. A company claim is attributed — *they say*. An estimate is
  labelled *roughly*. If something couldn't be established, say so rather than leaving a gap
  they'll fill with an assumption.
- **Glanceable.** Short sections. Questions in a numbered list. Scripted lines in block quotes so
  they can be found at speed. Bold only for what must not be missed — bold everywhere is bold
  nowhere.

`scripts/plain_check.py` enforces the length, sentence and abbreviation rules, and flags phrasing
that reads as machine-written. It is a checklist, not a judge. Where code cannot run, apply the
rules by hand.

The checker reads prose. It cannot see whether each question names the fact it came from, so read
the questions against those facts by hand before delivery. Weak prose is caught while reading; an
ungrounded question is caught in the room.
