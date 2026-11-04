# The brief: format and reasons

Read this before writing any brief, NO BRIEF included. Headings and header lines are exact, because `scripts/brief_check.py` reads them. Where code cannot run, apply every rule below by hand. Whether a story was the right one to pick is judgement; the rules below cover the shape.

## A brief

```markdown
# Daily brief: PM, 2026-11-04

Window: 2026-11-04T08:00+01:00 to 2026-11-04T20:00+01:00
Persona: investor
Areas: economy, politics
Following: oil prices, hormuz

## Following

### oil prices
Brent rose about six percent after a tanker was attacked off the Omani coast and two shippers paused Gulf transits. OPEC's monthly report, out the same morning, trimmed its demand forecast for the second time this year.
- [Brent jumps as Gulf shipping pauses](https://…) — the fullest account of what the shippers actually said (FT, 14:10)
- [OPEC monthly oil market report](https://…) — the primary document, two pages of tables (OPEC, 09:00)

### hormuz
Nothing significant since the last brief.

## Economy
<five to ten sentences, one paragraph>

Links:
- [Title](https://…) — why this one is worth opening (Source, HH:MM)
- [Title](https://…) — … (Source, HH:MM)
- [Title](https://…) — … (Source, HH:MM)

## Politics
<five to ten sentences, one paragraph>

Links:
- …

## Not read
- ft-home: returned 403; paywalled front page, headline feed only
- (or) All feeds read.
```

### The header

- The title is `# Daily brief: <AM|PM>, <YYYY-MM-DD>`. The date is the day the brief is delivered, taken from the environment.
- **Window** gives both ends as ISO 8601 with an offset, oldest first. The end is now; the start is `last_brief` or twelve hours before.
- **Persona**, **Areas** and **Following** repeat the settings so the brief travels without them. `Following:` reads `none` when there are no interests, and the `## Following` section is then left out.

### Following

One `### <interest>` per interest, in the order of the settings, using the interest's normalised text as the heading. Under it, either:

- one to five sentences and one to three links, for the stories that matched, or
- exactly the line `Nothing significant since the last brief.`

A story that appears here does not appear again under its area.

### Areas

One `## <Area>` per area in the settings, title-cased, in the settings' order. Each has one paragraph of five to ten sentences, a blank line, the line `Links:`, and three to five link lines. Fewer than three stories worth a link is allowed only when the paragraph says the area was quiet; then the link list may have one or two entries, and the checker reports it as a note, not a failure.

A sentence covers one story, or the relation between two. The paragraph reads as prose, not as a list of headlines joined by full stops: say what happened, what it changed, and what is still open.

### Link lines

`- [Title](https://…) — <why read this> (<Source>, <HH:MM>)`

- The title is the article's own, or a shortened version of it.
- The reason is one clause that says what the reader gets from opening it: the primary document, the fullest account, the other side, the numbers. "Read more" is not a reason.
- The source is the feed's `name` from `assets/sources.json` or the person's addition; the time is the item's published time in the person's zone.
- No link appears twice in a brief. No link points at a search results page, a home page, or a social post.

### Not read

Never empty. One line per feed that was skipped or failed, with the reason, or the single line `All feeds read.` This is how the person learns their favourite service was not actually read.

## Writing rules the checker tests

- A sentence in the brief must not match a sentence in any source verbatim. Quotes are under fifteen words, one per source, in quotation marks.
- The word "news" does not appear in the brief. The product is the opposite of a feed, and the word pulls the prose toward one.
- No sentence begins "In other news", "Meanwhile" or "Also". Each story earns its sentence or is cut.
- A link's reason and a sentence may repeat a fact; they may not repeat each other's wording.

## NO BRIEF

```markdown
# Daily brief: NO BRIEF, 2026-11-04

Window: none
Persona: none
Areas: none
Following: none

## Why
<one of the sentences below, then one line of detail>

## What would change it
- <the setting or access that is missing>

## Not read
- <every feed tried, or "No feeds tried."
```

The **Why** opens with one of:

- "There are no settings yet, and nobody is here to answer the setup question."
- "No feed could be read." Use it when every feed in their areas failed; a brief built from one surviving feed is a brief, with the rest under Not read.
- "There is no web access in this environment."
