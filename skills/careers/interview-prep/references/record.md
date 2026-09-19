# Filling and testing the record

How `interview-record.html` is filled and why its pre-delivery test is shaped the way it is. Read this before building one. `SKILL.md` settles whether to build one at all.

## The three things to set

- **`RECORD_ID`** — a short name for this interview, unique among the records this browser already holds. It is what keeps one employer's notes out of another's. Left empty, the page still works, saves nothing, and says so on screen.
- **`QUESTIONS`** — each is `[question, what the answer reveals]`. The second string is the point: mid-call they need to see what they are listening for, not a restatement of what they asked.
- **`SIGNALS`** — judgments formed across the whole conversation, not questions. Whether the work really happens here, whether the worry about their weak spot is real. One click records confirmed or not the case, so a judgment can be caught without breaking eye contact. These are the things nobody remembers by the end of a call.

On a recruiter screening call the signals matter more than the questions. Did they know the technical content of the role? Did they answer the money question or move past it? Could they name the hiring manager? The recruiter's own conduct is evidence about the employer.

The panels on the right take the same content as the brief: why this company, the weak spots said first, the harder questions held back. One preparation pass fills both.

## Why the test is what it is

Filling the arrays settles the content, not whether the page still works. Opening it and reading it proves nothing, because a control can work from a local file and fail in a viewer that sandboxes the page. That is why the test opens the page the way they will open it.

The reload matters because every other control can pass on a page that persists nothing. The copy-out matters because the shortcut is to try only what was edited, and the copy-out rarely is. It is also the input for **After a round** in a later session, instead of recall two days later.
