# Filling and testing the record

How `interview-record.html` works. Read this when building one.

## Why it exists at all

The brief prepares them. It does not help during the conversation: scrolling a document mid-call
loses your place, and there is nowhere to type.

A recruiter screening call earns one. It is short, but usually where the budget, the real scope,
the process and the timeline are named for the first time. On such a call the signals matter more
than the questions — whether they knew the technical content of the role, whether they answered
the money question or moved past it, whether they could name the hiring manager. The recruiter's
own conduct is evidence about the employer.

## The three things to set

One self-contained page, filled at the top of its script:

- **`RECORD_ID`** — a short name for this interview, unique among the records this browser
  already holds. It is what keeps one employer's notes out of another's. Left empty, the page
  still works, saves nothing, and says so on screen.
- **`QUESTIONS`** — each is `[question, what the answer reveals]`. The second string is the
  point: mid-call they need to see what they are listening for, not a restatement of what they
  asked.
- **`SIGNALS`** — judgments formed across the whole conversation, not questions. Whether the work
  really happens here, whether the worry about their weak spot is real. One click records
  confirmed or not the case, so a judgment can be caught without breaking eye contact. These are
  the things nobody remembers by the end of a call.

The panels on the right take the same content as the brief — why this company, the weak spots said
first, the harder questions held back. One preparation pass fills both; the brief is read
beforehand, the record is open during.

**Copy everything** produces plain text. That is the point of the whole thing: it comes back into
a later session as the input for **After a round**, instead of being reconstructed from memory two
days later.

## Work it before handing it over

Filling the arrays settles the content, not whether the page still works, and opening it and
reading it proves nothing — a control can work from a local file and fail in a viewer that
sandboxes the page. Open it the way they will open it, then add a question, mark one answered, and
cycle a signal chip. Reload the page and confirm the notes are still there, then run **Copy
everything** and read what comes out. The shortcut is to try only what was edited, and the
copy-out rarely is.
