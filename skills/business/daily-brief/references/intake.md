# Intake: personas, mapping and the settings file

Read this before the first question. The aim is to leave the conversation with a settings file after at most two questions. Most people cannot name a category; all of them can say what they do and what they care about.

## The first question: pick a persona

Offer every persona in `assets/personas.json` as a choice, each with its one-line `pitch`, plus the option "describe it yourself". A persona is a preset, not a label they must fit: accepting it sets `areas`, `sources` and `interests_starter`, and the second question adjusts from there.

When they describe themselves instead, map the description:

| They say | Persona | Then ask |
| :--- | :--- | :--- |
| invest, trade, markets, rates, my portfolio | `investor` | which markets or assets |
| my company, my startup, fundraising, product | `founder` | which sector and competitors |
| engineer, developer, I build, open source | `engineer` | which stack or ecosystem |
| politics, policy, elections, EU, regulation | `policy-watcher` | which countries or bodies |
| my team, the league, match, season | `sports-fan` | which team and league |
| research, papers, lab, science | `scientist` | which field |
| just keep me informed, a bit of everything | `generalist` | nothing more than the second question |

A description that fits two personas takes the areas of both and the sources of both, with the first one named as `persona`.

## The second question: specifics and favourites

One question, two parts, answered in free text or as tappable follow-ups where the environment offers them:

1. **Anything specific to follow?** A team, a company, a commodity, a region, a topic. Each becomes an interest. Normalise: lowercase, singular, no articles ("the oil price problem" becomes `oil prices`; "Ormuz" becomes `hormuz`). Two phrasings of one thing stay as two interests; the matcher is text overlap, and both will match.
2. **Any favourite service to read alongside the defaults?** A site, a newsletter, a feed. For a site, find its RSS or Atom feed (the `<link rel="alternate">` on its front page, or `/feed`, `/rss`); for a newsletter with no feed, say it cannot be read and leave it out. Each addition is a source with `weight: 2` under the area it best fits, or under a new area named after it.

Skip any part already answered. Do not ask a third question; what is still unknown is left at the persona's defaults, and the brief's last line tells them how to change it.

## The settings file

`daily-brief.json`, written where the person can keep it: the working folder, a connected folder, or memory where the platform has one. Keys are exact; `scripts/brief_check.py` does not read this file, but the next run does.

```json
{
  "persona": "investor",
  "areas": ["economy", "politics"],
  "interests": ["oil prices", "hormuz", "ecb"],
  "sources_added": [
    {"id": "my-obserwator", "area": "economy", "name": "Obserwator Finansowy", "url": "https://www.obserwatorfinansowy.pl/feed/", "weight": 2}
  ],
  "timezone": "Europe/Warsaw",
  "last_brief": "2026-11-04T08:00:00+01:00"
}
```

- `areas` are keys from `assets/sources.json`, plus any area created for an added source.
- `interests` are normalised phrases, at most ten. More than ten and the Following block stops being short; say so and ask which to keep.
- `timezone` is an IANA name. Without one, take it from the environment, or ask inside the second question.
- `last_brief` is set after every delivery. It is the only thing the skill writes back on an ordinary run.

## The settings line

Where no file can be kept, the same settings as one line the person can paste into a later conversation:

```
daily-brief: persona=investor; areas=economy,politics; interests=oil prices,hormuz,ecb; tz=Europe/Warsaw; last=2026-11-04T08:00+01:00
```

Added sources do not fit on the line; say that they will need to be named again.

## Privacy

Interests can be sensitive: a political party, a health topic, a court case. They stay in the settings file and the brief, both of which the person holds. Nothing from the intake is searched, logged or sent anywhere other than to the feeds themselves, which receive only ordinary requests.
