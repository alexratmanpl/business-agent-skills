# Changelog

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow
[semantic versioning](https://semver.org/).

The version applies to the whole set. The skills release together, so one number identifies a
known-good combination rather than six lineages to keep in step.

No git tag is cut per version. The only published artifact is the `latest` prerelease, which
CI rebuilds from `master` on every push, so it always holds the newest state rather than a
named version.

## [Unreleased]

### Added

- `daily-brief`, a seventh skill, in the `business` category: the core of the day in the areas
  someone follows, in a fixed shape of five to ten sentences and three to five links per area,
  twice a day, since the last brief. It is the skill-sized sibling of a planned static service
  of the same shape, rethought for an agent: instead of a server pipeline and browser-side
  matching, the intake starts from a persona preset in `assets/personas.json` (investor,
  founder, engineer, policy-watcher, sports-fan, scientist, generalist), so one tap sets the
  areas, the sources and a few starter interests, and one more question adds specifics and the
  person's own favourite services. Settings live in a `daily-brief.json` the person keeps, or
  in a one-line settings string where no file can be kept; nothing about them is sent anywhere.
  The source list is the editorial decision: `assets/sources.json` by area, with weights, and
  no general web search for what happened. An interest with nothing to show gets one fixed line
  rather than a weak match. The word "news" is kept out of the brief on purpose.
- `daily-brief` ships `scripts/brief_check.py`, a gate on the brief's shape, with its cases in
  `evals/`. The intake and persona mapping, and the brief and NO BRIEF formats, live in
  `references/intake.md` and `references/brief.md`, read only at the step that needs them.
  `SKILL.md` is 834 words against the default budget.
- `career-direction`, a fifth skill: where to point a career when no particular job is on the
  table. It runs a six-pass intake, groups the market into families by the asset each one buys,
  and reads three to five years ahead without forecasting — every shift has to be visible in
  something dated and has to name what would prove it wrong. It is on the file layout in
  `AGENTS.md` from the start, under a declared `SKILL.md` budget of 1,275 words: the intake
  passes, market craft, horizon discipline and report contract live in four files under
  `references/`, each read only at the step that needs it.
- `career-direction` ships `assets/direction-report.html`, one self-contained page holding its own
  data as JSON, and `scripts/report_check.py`, a gate that reads that same data and fails on what
  makes a report worthless or unsafe to forward. Its cases, and the page's, are in `evals/`, which
  packaging leaves out.
- A privacy rule: the intake stays in the conversation, the market is researched without ever
  searching the person, and the report carries a first name or initials rather than contact
  details. The checker enforces the last of the three, for the common shapes of an email address,
  a phone number, a profile link, a street address and a surname.
- `learning-path`, a sixth skill and the first in a new `learning` category: a learning path to a
  defined goal in any field. It tests the goal before planning anything. When performance,
  standard or conditions are missing, it says so in a fixed sentence and digs. It offers concrete
  versions of the goal with their judges and sources, rather than planning around the gap. The
  standard comes from the body that sets it. Every source is dated against today's date, taken
  from the environment. A plan that cannot rest on verified evidence comes back as NO PATH, not as
  a list of things to try.
- Before any plan is delivered, a fresh reviewer, or a separate pass, opens every source and
  returns each claim as upheld, corrected or dropped. The plan records the counts.
- `learning-path` ships `scripts/path_check.py`, a gate that reads a drafted plan and names each
  problem it finds. Its cases are in `evals/`, which packaging leaves out. The skill is on the
  file layout from the start. The intake questions, the research method, the plan format and the
  review brief live in four files under `references/`.

### Changed

- `interview-prep` is the first skill moved onto the file layout in `AGENTS.md`. `SKILL.md` drops
  from 1,925 words to 1,119, by the counter the next entry describes; what it specified about
  writing a brief, filling `interview-record.html`, and working without the companion skills now
  lives in `references/brief.md`, `references/record.md` and `references/without-companions.md`,
  which are read only at the step that needs them. The packaged `interview-prep.skill` carries all
  three. The decisions stay in `SKILL.md`, and nothing was added.
- `SKILL.md` length is a per-skill budget enforced by `build_skills.py`, replacing a flat cap
  enforced by nothing. The default is 1,000 words; a skill needing more declares `budget:` in
  its frontmatter, so raising it shows up in the diff. `company-research` declares 1,400,
  `interview-prep` 1,150 and `career-direction` 1,275. `wc -w` is no longer the counter: it
  disagrees with itself across locales by the number of em dashes in the file.
- `AGENTS.md` lists `evals/`, which `build_skills.py` already left out of packaged skills, for the
  cases that test a skill's own script or page.

## [1.1.0] - 2026-09-13

Everything below shipped between 2026-08-18 and 2026-09-13 and was never recorded. `1.0.0` was
the repository scaffold: four skills with a description and no instructions behind them. This is
the first version where the skills do anything.

### Added

- `company-research`, `role-fit`, `pay-check` and `interview-prep` gained their instructions.
- `interview-prep` ships `interview-record.html`, a self-contained page for taking notes during
  a call, and `scripts/plain_check.py`, which flags long sentences, abbreviations used before
  being spelled out, machine phrasing and excess length in a drafted brief.
- `pay-check` ships `scripts/rate_calc.py` and `rates-example.json`, so the arithmetic is run
  rather than estimated.
- `scripts/build_skills.py` validates and packages every skill: frontmatter parses and has a
  name and description, the name matches the directory that gets installed, every bundled file
  the body points at exists, and the body is not still a placeholder. CI runs it on every pull
  request and publishes a rolling `latest` prerelease from `master`.
- A `No session links` check rejects any pull request whose commits, diff, title or description
  carry a Claude Code session link.

### Changed

- `company-research` keeps derived material out of a dossier's sourced sections and gives it a
  named place, on the grounds that reasoning from a company's own wording is still reasoning.
- `interview-prep` establishes how far the domain is from the candidate and closes that gap
  before the brief rests on it.
- `interview-prep` requires each question to name the research fact it came from, and widens the
  marketing exclusion to questions derived from adverts and press releases.
- `interview-prep` gives a technical assessment its own shape in **Build**, rather than naming it
  as a format and describing only the conversational ones.
- `interview-prep`'s pre-delivery checklist now includes reloading the record and confirming the
  notes are still there.

### Fixed

- `interview-record.html` persisted nothing. Save and load called `window.storage`, an API that
  exists on no surface the page is opened in; every call threw, every throw was swallowed, and
  the notes lived for one tab while the status line read "Kept in this tab only". They now use
  `localStorage`, each interview gets its own key derived from `RECORD_ID`, and a single refused
  write no longer disables saving for the rest of the call.
- `interview-record.html`'s controls failed in a sandboxed viewer: adding a question was blocked
  as a form submission, and the clipboard write was refused while the toast still said "Copied".
