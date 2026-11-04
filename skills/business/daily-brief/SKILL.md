---
name: daily-brief
description: A short brief of what happened since the last one in the areas someone follows — 5 to 10 sentences and 3 to 5 links per area, read from a predefined source list plus their own favourite services. Use when someone asks what happened today, what they missed, for a morning or evening brief, or to set up or change what they follow. Reading the day only — one company in depth is company-research.
compatibility: Reading feeds needs web access; without it the result is NO BRIEF. The bundled checker needs code execution; without it, the rules in references/brief.md are applied by hand.
---

# Daily Brief

The core of the day for one person, twice a day: what mattered in the areas they follow, and the few links worth their time. It is the opposite of a feed.

## Stance

- **The shape is the product.** Five to ten sentences and three to five links per area, every time. Not more when the day was busy; not padded when it was quiet.
- **Silence over filler.** Nothing significant on a topic means one line saying so, never a weak match dressed up as a story.
- **Own words, open links.** No sentence is copied from a source. Every claim in the brief sits next to the link it came from. A quote is under fifteen words and one per source.
- **Coverage ranks.** A story several sources carried outranks one outlet's exclusive. The person's own sources count double; they chose them.
- **Since the last brief.** A story the previous brief carried is not repeated, however large.
- **Nothing from memory about events.** The feeds read in this run are the only source of what happened. Recall supplies context, never an event.

## Today's date and the window first

Take the date and time from the environment: the system clock, the conversation, the platform. The window runs from `last_brief` in the settings to now. With no `last_brief`, it is the last twelve hours. Name the edition: AM covers 20:00 to 08:00, PM covers 08:00 to 20:00, in the person's time zone.

## Settings

Look for daily-brief.json: in the working folder, in a connected folder, in memory, or pasted into the conversation as a settings line. Found, and they only asked for the brief: read it and go to **Read**, asking nothing. Not found, or they ask to set up or change what they follow: go to **Asking**. The file's shape, the settings line and the persona mapping are in `references/intake.md`.

**If nobody is watching** — a scheduled run, a delegated task — do not stall. With settings, build. Without them, deliver NO BRIEF and the one question that would set them up.

## Asking

Use whatever interactive choice mechanism the environment offers: tappable options where they exist, a plain question otherwise. Before the first question, read `references/intake.md`.

First, offer the personas in `assets/personas.json` as choices, plus "describe it yourself". A persona sets the areas, the sources and a few starter interests, so one tap does most of the work. Then one question: anything specific to follow (a team, a company, a topic, a region) and any favourite service to read alongside the defaults. Map free text to areas, interests and sources as the intake describes. Two questions at most. Then write daily-brief.json where they can keep it, show the one-line settings string, and go to **Read**.

Changing what they follow is the same step: adjust the file, show the new line, rebuild.

## Read

`assets/sources.json` lists feeds per area with a weight. The person's additions join with weight 2. Read each feed for their areas, taking only items inside the window. A feed that does not resolve is dropped and named under **Not read**, never guessed at. A paywalled item contributes its headline and link only.

**Stop when** every feed for their areas has been tried once. No second pass, and no general web search for what happened today: the source list is the editorial decision, and a search result is not on it.

## Build

Group items about the same event into one story. Rank stories by the number of sources that carried them, times source weight, times recency. Take the top eight to twelve per area; those are what the sentences cover, and the best link per top story is the link list. For each interest, take the stories whose headline or text matches it; with none, write the silence line. An item in **Following** does not reappear under its area.

Write the brief in the format `references/brief.md` sets out. Then run `scripts/brief_check.py` on it with `python3`, from the skill's folder (`${CLAUDE_SKILL_DIR}` in Claude Code), passing `--date` with the date taken at the start. **Stop when** it exits 0 and every note is acted on.

## Deliver

Write it as markdown, `daily-brief-DATE-EDITION.md`, and make sure they have it: attach it, save it beside the settings, or put it in the reply. Set `last_brief` in the settings to now. End with one line saying how to change what they follow. Nothing else: no offer of more, no extras.
