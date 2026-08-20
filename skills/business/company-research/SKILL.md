---
name: company-research
description: Research a company before joining, buying from, investing in, or competing with it. Use when someone asks what a company is really like, who its competitors are, whether it is doing well, or whether it is worth working for. Produces a plain-language dossier. Research only — see role-fit, interview-prep, pay-check for the rest.
---

# Company Research

Find out what a company is really like, beyond what it says about itself.

## Ask first

Use whatever interactive choice mechanism the environment offers — tappable options where they exist, plain questions otherwise. One round, three questions at most.

- Which company. Disambiguate common names.
- Why they are asking: joining, buying, selling, investing, competing. This decides what matters.
- How deep to go.

If nobody is watching — a background job, a scheduled run, a delegated task — do not wait for an answer. Take the most useful default, state the assumption in the output, and carry on.

## Find

**What they do.** Identify the product and the buyer. Keep reading until you can state who pays and what problem they are paying to solve. Record whether pricing is published and whether any customers are named. Report both as observations; do not infer a sales model or a stage from them.

**Money.** Funding amounts, dates and investors. Revenue and profit figures, with the source of each. For young companies, how long the funding covers at current spending, if that can be established. For established ones, published results, layoffs and legal proceedings. Record money raised and headcount together, with the ratio, and leave the reader to draw from it.

**Competitors.** For each candidate, establish who signs the cheque and which problem is solved. Where those differ from the company under research, the two are not competitors — say so. Record which have raised more money, and any acquisitions between them.

**Self-descriptions side by side.** Collect each competitor's one-line pitch. Note where the pitches agree and where one differs. A difference is a choice the company has made, and it is worth asking about.

**Working there.** Employee reviews, including local-language sites. Read by department. Give sample size and dates every time. If there are no reviews, report that there is no information rather than treating it as a verdict.

**People.** Leadership backgrounds and tenure. Compare the founding story against early filings and archived pages, and report any difference without explaining it. At small companies, record advisers and investors.

## When to stop

Research is done when each of these holds, at the depth agreed in the first question:

- You can state who pays and what problem they are paying to solve.
- The most recent funding round or filed accounts is recorded, with its date.
- At least two competitors are established, each with buyer and problem.
- Review counts and date range are recorded, or no reviews were found.
- Current leadership is recorded, with tenure where it is published.

Anything still unestablished at that point is a gap. Write it in the gaps section and stop looking. Continuing past this without a reason turns research into browsing.

## Where to look

Ordered by how hard the source is for a company to change. Work down the list.

**Records filed under obligation.** Company registries hold directors, ownership, filed accounts and charges over assets: Companies House in the UK, the state Secretary of State plus SEC EDGAR in the US, `justice.cz` and `ares.gov.cz` in the Czech Republic. Most countries have an equivalent — look for it before giving up. Court records cover litigation, insolvency and employment disputes; repeated cases of one kind matter more than any single case. Regulators publish licences, enforcement actions and inspection reports. Public procurement and grant databases give contract values with dates.

Accounts are filed months after the period they cover, so date them and treat them as historical. Small companies may file abbreviated accounts that omit revenue; record that as a gap.

**The company's own site.** Useful for what the company intends, weak as evidence. Take specifics — dates, names, numbers — and attribute the framing. Read the product pages, the pricing page, the customer stories and their dates, and the open roles with their locations, which show where the company is spending. Check the documentation and the status page: both show whether the product is in real use. Press releases are reliable for what was announced, and for amounts and dates.

**Company and engineering blogs.** Post frequency and dates show whether the company is still writing. Engineering posts name the technology in use and the problems being solved, in more detail than the marketing pages. Conference talks and published slides do the same. Record the author and the date.

**Social accounts and communities.** Company accounts show what is announced and how often. Posts by employees, especially engineers and executives, describe the work in more detail than the company site. Professional networks show headcount over time, open roles, arrivals and departures, and how long people stay. Forums, question sites, developer communities and local-language groups carry what customers and former staff say unprompted.

Treat everything here as one person speaking, not the company. Record who said it and when. One post is one account of events; the same detail from several unconnected people is worth more.

Any statement a company makes about its own performance is a claim. Write it as "they say".

**Press.** Prefer the original announcement to coverage of it. A named reporter with their own quotes is worth more than an unbylined summary. Market analysis published by a company that sells into that market is advertising — check whose site the figure came from before using it. Rankings and vendor lists are often paid or self-submitted. Revenue figures on data-broker profiles are modelled, not filed; say so if you use one.

**Employee reviews.** Give the sample size and the date range. Read by department, since departments often describe different companies and the average hides that. Look for the same specific detail repeated across reviews — a named policy, a reorganisation, a broken commitment. Local-language sites carry more reviews for local offices.

**Archived pages.** When a company has changed or removed something, the earlier version is a legitimate source, and the change itself is worth reporting.

## Write the dossier

Write it as markdown, saved as `company-dossier-NAME.md`. Markdown keeps it useful after this session: it can be reread, quoted, extended as more is learned, and passed to whatever needs it next without conversion.

Then make sure the user actually has it. Use whatever the environment offers — attach or send the file, write it to a folder they have connected, or leave it in the working directory if they can reach that. Tell them the filename either way, so it can be found again. If no file can reach them, put the dossier in the reply instead. A rendered version can be offered alongside the file where the environment displays one; it does not replace the file.

Sections: what they do, money, competitors, what makes them different, working there, people, risks, what could not be established. Anything derived rather than found goes after all of them, under its own heading, never inside one.

- **Plain words.** Explain any term of art on first use. Write "money raised from investors" rather than "Series B".
- **Mark confidence.** Every fact carries a source and a date. Company claims are attributed. Estimates are labelled as estimates. Anything not directly evidenced is marked as such wherever it appears. Nothing that is uncertain should read as settled.
- **Say when a fact is old.** Give the age of anything more than a year out of date. Funding, headcount and leadership all change, and a three-year-old figure is evidence about then, not now.
- **Report gaps.** End with what could not be established, so the reader knows what to ask about.
- **Keep your own reasoning apart from the findings.** Suggestions, recommendations, inferences and questions to put to the company are the one thing here with no source behind it, so it is the one thing that must not sit among the sourced sections or share their register. Put it under a final heading — *What this suggests: our reading, not sourced* — after the gaps. The test is whether someone skimming can tell which lines rest on a source and which are our own reasoning, without checking either. Material drawn from the company's own published wording is derived, not found: it belongs here, however closely it follows the source.

## Rules

- Prefer original documents: announcements, filings, regulators, court records, accounts.
- Give both versions when sources conflict, and say which is better evidenced.
- Do not explain a finding by guessing at a cause. Report what was found and leave it there.
- Correct earlier errors plainly, in the output, when they are noticed.
