"""Each case takes the example report, breaks it the way a real mistake would, and says what
must happen: the exit code, and the report paths the problem list names. A case that
expects exit 0 is as important as one that expects the opposite: a gate that blocks a
legitimate report sends people looking for a way round it.
"""

from harness import DELETE


# name, edits, expected exit code, text the problem list (stderr) must contain
CASES = [
    # The example is the contract, so it has to pass.
    ("the example passes", [], 0, []),

    # The page maps over lists and reads objects by key. A wrong type does not render wrongly: it
    # costs the section it is in, and the page names it. Nothing in the file says so until it is opened.
    ("shape as one string", [("shape", "One sentence about them.")], 1, ["shape"]),
    ("constraints.hard as a string", [("constraints.hard", "A figure.")], 1, ["constraints.hard"]),
    ("horizon.agesWell as a string", [("horizon.agesWell", "Accountability")], 1, ["horizon.agesWell"]),
    ("an evidence row that is a string", [("evidence", ["just text"])], 1, ["evidence[0]"]),
    ("families as an object", [("market.families", {"name": "x"})], 1, ["market.families"]),
    ("demandN as true", [("market.families[0].demandN", True)], 1,
     ["market.families[0].demandN", "true or false"]),
    ("demandN as text", [("market.families[0].demandN", "9")], 1, ["market.families[0].demandN"]),
    ("a step column as text", [("horizon.clocks.lanes[0].steps[0].at", "3")], 1, ["steps[0]"]),
    ("a step placed with true", [("horizon.clocks.lanes[0].steps[0].at", True)], 1, ["steps[0].at"]),
    ("a glossary entry that is not a pair", [("glossary", [["asset"]])], 1, ["glossary[0]"]),
    # The page treats null as absent, so the checker must too.
    ("a section set to null", [("horizon", None)], 0, []),

    # A count is a whole number of 0 or more. A step is a whole number of columns. The page reads 3.0 as 3.
    ("a demand below zero", [("market.families[0].demandN", -8)], 1,
     ["market.families[0].demandN", "-8", "0 or more"]),
    ("a demand with a fraction", [("market.families[0].demandN", 2.5)], 1, ["market.families[0].demandN"]),
    ("a skill count below zero", [("market.skills[0].countN", -4)], 1, ["market.skills[0].countN"]),
    ("a skill count with a fraction", [("market.skills[0].countN", 1.5)], 1, ["market.skills[0].countN"]),
    ("a count written with a decimal point", [("market.families[0].demandN", 9.0)], 0, []),
    ("a step written with a decimal point", [("horizon.clocks.lanes[0].steps[0].span", 3.0)], 0, []),
    ("a step with a fraction", [("horizon.clocks.lanes[0].steps[0].span", 2.5)], 1, ["steps[0].span"]),
    ("a step that starts on a fraction", [("horizon.clocks.lanes[0].steps[0].at", 1.5)], 1, ["steps[0].at"]),

    # A key the page does not read renders nothing, and the report still looks finished. The title
    # is built from the name, so a title of one's own is such a key.
    ("a mistyped key", [("gaps[0].weigth", "decides")], 1, ["gaps[0].weigth"]),
    ("a title key the page no longer reads", [("meta.title", "Jane Doe, where next")], 1, ["meta.title"]),

    # What the page draws as an empty chip, an empty cell or a default colour is not an
    # error to the page, so the checker is the only place anyone hears of it.
    ("a gap with no weight", [("gaps[0].weight", DELETE)], 1, ["gaps[0].weight"]),
    ("a gap weight that is not one of the three", [("gaps[0].weight", "decide")], 1,
     ["gaps[0].weight", "decides"]),
    ("a gap with an empty evidence cell", [("gaps[1].evidence", "")], 1, ["gaps[1].evidence"]),
    ("a habit with no tone", [("habits[0].tone", DELETE)], 1, ["habits[0].tone"]),
    ("a family with no ages", [("market.families[0].ages", DELETE)], 1,
     ["market.families[0].ages"]),
    ("ages given as a tone word", [("market.families[0].ages", "good")], 1,
     ["market.families[0].ages", "well"]),
    ("sourcing as free text", [("market.families[2].sourcing", "one agency")], 1,
     ["market.families[2].sourcing", "confirmed"]),
    ("a position with no status", [("market.positions[0].status", DELETE)], 1,
     ["market.positions[0].status"]),
    ("a step with no at", [("horizon.clocks.lanes[0].steps[0].at", DELETE)], 1, ["steps[0].at"]),

    # The one section a partial report cannot leave out. An empty list renders as nothing,
    # which is the silence it exists to prevent.
    ("no sources at all", [("sources", DELETE)], 1, ["sources.notConfirmed"]),
    ("sources without notConfirmed", [("sources.notConfirmed", DELETE)], 1, ["sources.notConfirmed"]),
    ("an empty notConfirmed", [("sources.notConfirmed", [])], 1, ["sources.notConfirmed"]),
    ("a notConfirmed of blank lines", [("sources.notConfirmed", [" ", ""])], 1, ["sources.notConfirmed"]),

    # The gates that were there before, kept so the next rewrite cannot lose one. Each
    # problem has to name the path of the field, because a row number alone sends the
    # reader counting.
    ("evidence with no source", [("evidence[0].src", "")], 1, ["evidence[0].src"]),
    ("a market line with no source", [("market.lines[0].src", DELETE)], 1, ["market.lines[0].src"]),
    ("a family with no pay", [("market.families[0].pay", DELETE)], 1, ["market.families[0].pay"]),
    ("a family with no entry bar", [("market.families[0].entryBar", DELETE)], 1,
     ["market.families[0].entryBar"]),
    ("a family with no sourcing mark", [("market.families[0].sourcing", DELETE)], 1,
     ["market.families[0].sourcing"]),
    ("a family with no counted demand", [("market.families[0].demandN", DELETE)], 1,
     ["market.families[0].demandN"]),
    ("a family with a demand note that is blank", [("market.families[0].demandNote", " ")], 1,
     ["market.families[0].demandNote"]),
    ("a forecast that nothing could disprove", [("horizon.shifts[0].falsifier", "")], 1,
     ["horizon.shifts[0].falsifier"]),
    ("a forecast with nothing already visible", [("horizon.shifts[0].alreadyVisible", "")], 1,
     ["horizon.shifts[0].alreadyVisible"]),
    ("a forecast with no source", [("horizon.shifts[0].src", "")], 1, ["horizon.shifts[0].src"]),
    ("a step outside the track", [("horizon.clocks.lanes[0].steps[0].span", 20)], 1, ["steps[0]"]),
    # The track has twelve columns: a step may end on the twelfth and go no further.
    ("a step that ends on the last column", [("horizon.clocks.lanes[0].steps[0].at", 8),
     ("horizon.clocks.lanes[0].steps[0].span", 4)], 0, []),
    ("a step that runs one past the last column", [("horizon.clocks.lanes[0].steps[0].at", 9),
     ("horizon.clocks.lanes[0].steps[0].span", 4)], 1, ["steps[0]"]),
    ("a step that starts before the first column", [("horizon.clocks.lanes[0].steps[0].at", -1)], 1,
     ["steps[0]"]),
    ("a step with no width", [("horizon.clocks.lanes[0].steps[0].span", 0)], 1, ["steps[0]"]),
    ("a step in the second lane", [("horizon.clocks.lanes[1].steps[0].at", 11),
     ("horizon.clocks.lanes[1].steps[0].span", 3)], 1, ["lanes[1].steps[0]"]),
    # Steps in a lane follow one another, and the page draws one that does not on a second row, with an
    # arrow that says "then" over a picture that says "at once". Touching is following.
    ("a step that starts inside the one before it", [("horizon.clocks.lanes[0].steps[1].at", 2)], 1,
     ["lanes[0].steps[1]"]),
    ("two steps on the same columns", [("horizon.clocks.lanes[0].steps[1].at", 0)], 1, ["lanes[0].steps[1]"]),
    ("a step listed before the one it overlaps", [("horizon.clocks.lanes[0].steps", [
        {"at": 3, "span": 5, "label": "later"}, {"at": 0, "span": 4, "label": "earlier"}])], 1, ["lanes[0].steps[1]"]),
    ("steps that touch", [("horizon.clocks.lanes[0].steps[1].at", 3)], 0, []),

    # A position belongs to a family on the list, and the page draws what it is given: a name that
    # differs by a letter is a family that is not there. A date a position closes on is the one thing the
    # reader needs of it. Odds are percentages, which is what the page sorts on.
    ("a position in a family that is not on the list", [("market.positions[0].family", "Planner")], 1,
     ["market.positions[0].family", "Production planner at a packaging converter"]),
    ("a position with no family", [("market.positions[0].family", DELETE)], 1, ["market.positions[0].family"]),
    ("a position that closes on no date", [("market.positions[0].statusDate", DELETE)], 1,
     ["market.positions[0].statusDate"]),
    ("a position that closes on a blank date", [("market.positions[0].statusDate", " ")], 1,
     ["market.positions[0].statusDate"]),
    ("a position that is open needs no date", [("market.positions[1].statusDate", DELETE)], 0, []),
    ("a position that has closed needs no date", [("market.positions[0].status", "closed"),
     ("market.positions[0].statusDate", DELETE)], 0, []),
    ("odds in words", [("market.positions[0].oddsNow", "about a third")], 1, ["market.positions[0].oddsNow"]),
    ("odds as a fraction", [("market.positions[0].oddsAfter", "0.3")], 1, ["market.positions[0].oddsAfter"]),
    ("odds with words after them", [("market.positions[0].oddsNow", "15% chance")], 1,
     ["market.positions[0].oddsNow"]),
    ("odds with words before them", [("market.positions[0].oddsNow", "about 15%")], 1,
     ["market.positions[0].oddsNow"]),
    ("odds as a range", [("market.positions[0].oddsNow", "10-20%")], 0, []),
    ("odds with a bound and an en dash", [("market.positions[0].oddsNow", "<5%"),
     ("market.positions[1].oddsNow", "10\u201320 %")], 0, []),
    ("odds with the other bound and both ways of saying about", [("market.positions[0].oddsNow", ">30%"),
     ("market.positions[1].oddsNow", "~15%"), ("market.positions[2].oddsNow", "\u224815%")], 0, []),

    ("a demand of zero is a count", [("market.families[0].demandN", 0)], 0, []),
    ("a full name", [("meta.name", "Jane Doe")], 1, ["meta.name"]),
    ("initials", [("meta.name", "J. D.")], 0, []),
    ("a first name", [("meta.name", "Jane")], 0, []),

    # The report is a file that gets forwarded, so what identifies a person stays out of it.
    # The patterns are a backstop for the common shapes, so a case is a shape and not a country.
    ("an email address", [("meta.footer", "Write to a.b@example.com.")], 1, ["meta.footer"]),
    ("an international phone number", [("meta.footer", "Call +44 7700 900123.")], 1, ["meta.footer"]),
    ("a domestic phone number", [("meta.lede", "Reach them on 07700 900123 after six.")], 1, ["meta.lede"]),
    ("a phone number in brackets", [("meta.footer", "Call (555) 123-4567.")], 1, ["meta.footer"]),
    ("a phone number with hyphens", [("meta.footer", "Call 555-123-4567.")], 1, ["meta.footer"]),
    ("a phone number in three groups", [("meta.footer", "Call 600 123 456.")], 1, ["meta.footer"]),
    ("a street address, number first", [("constraints.soft[0]", "Lives at 221B Baker Street.")], 1,
     ["constraints.soft[0]"]),
    ("a street address, Polish", [("constraints.soft[0]", "Lives at ul. Marszałkowska 10, Warszawa.")], 1,
     ["constraints.soft[0]"]),
    ("a street address, Czech", [("constraints.soft[0]", "Lives at Vinohradská 12, Praha 2.")], 1,
     ["constraints.soft[0]"]),
    ("a street address, German", [("constraints.soft[0]", "Lives at Hauptstraße 5, Berlin.")], 1,
     ["constraints.soft[0]"]),
    ("a street address, German abbreviated", [("constraints.soft[0]", "Lives at Hauptstr. 5, Berlin.")], 1,
     ["constraints.soft[0]"]),
    ("a street address, French", [("constraints.soft[0]", "Lives at 5 rue de Rivoli, Paris.")], 1,
     ["constraints.soft[0]"]),
    ("a street address, Spanish", [("constraints.soft[0]", "Lives at Calle Mayor 5, Madrid.")], 1,
     ["constraints.soft[0]"]),
    ("a street address, Italian", [("constraints.soft[0]", "Lives at Via Roma 12, Milano.")], 1,
     ["constraints.soft[0]"]),
    ("a street address, Dutch", [("constraints.soft[0]", "Lives at Kerkstraat 3, Utrecht.")], 1,
     ["constraints.soft[0]"]),
    ("a street address, German, in gasse", [("constraints.soft[0]", "Lives at Hauptgasse 7, Wien.")], 1,
     ["constraints.soft[0]"]),
    ("a street address, Czech, in -ova", [("constraints.soft[0]", "Lives at Karlova 12, Praha.")], 1,
     ["constraints.soft[0]"]),
    ("a street address with a non-ASCII capital", [("constraints.soft[0]", "Lives at Šumavská 4, Brno.")], 1,
     ["constraints.soft[0]"]),
    ("eight digits in groups are a date or a count", [("meta.footer", "Ref 1234 5678.")], 0, []),
    ("nine digits in groups are a phone number", [("meta.footer", "Ref 1234 56789.")], 1, ["meta.footer"]),
    ("fifteen digits in groups still are", [("meta.footer", "Ref 12345 67890 12345.")], 1, ["meta.footer"]),
    ("sixteen digits in groups are not", [("meta.footer", "Ref 12345 67890 123456.")], 0, []),
    ("a phone number with dots", [("meta.footer", "Call 600.123.456.")], 1, ["meta.footer"]),
    ("an email with a tag and capitals", [("meta.footer", "Write to Jane+jobs@Example.COM.")], 1,
     ["meta.footer"]),
    ("a LinkedIn profile in capitals", [("evidence[0].src", "LinkedIn.com/IN/someone-else")], 1,
     ["evidence[0].src"]),
    ("an older LinkedIn profile", [("evidence[0].src", "linkedin.com/pub/someone/1/2/3")], 1,
     ["evidence[0].src"]),
    ("a LinkedIn profile", [("evidence[0].src", "linkedin.com/in/someone-else")], 1, ["evidence[0].src"]),
    ("a GitHub profile mid-sentence", [("evidence[1].src", "github.com/rexample for the commit history")], 1,
     ["evidence[1].src"]),
    ("an X profile", [("evidence[1].src", "x.com/rexample, pinned post")], 1, ["evidence[1].src"]),
    ("a Twitter profile", [("evidence[1].src", "www.twitter.com/rexample")], 1, ["evidence[1].src"]),
    ("a XING profile", [("evidence[1].src", "xing.com/profile/Someone_Else")], 1, ["evidence[1].src"]),
    ("the first name followed by a surname", [("meta.name", "Jane"),
     ("meta.lede", "Jane Doe is deciding where next.")], 1, ["meta.lede"]),
    ("the first name followed by a verb", [("meta.name", "Jane"),
     ("meta.lede", "Jane decides where next.")], 0, []),

    # And what is not theirs stays in. A gate that blocks a real source sends the agent to
    # drop the source, which is the worse of the two failures.
    ("a job board as a source", [("market.lines[0].src", "jobs.netflix.com/search, 13 Sep")], 0, []),
    ("a file host as a source", [("market.lines[1].src", "dropbox.com/jobs, nine postings")], 0, []),
    ("an organisation on GitHub", [("market.lines[1].src", "github.com/orgs/acme, nine postings")], 0, []),
    ("a repository on GitHub", [("market.lines[1].src", "github.com/kubernetes/kubernetes, issues")], 0, []),
    ("a company page on LinkedIn", [("market.lines[1].src", "linkedin.com/company/acme, 13 Sep")], 0, []),
    ("a salary range, dates and counts", [("constraints.hard[0]",
     "Floor 45 000 - 52 000 a year, from 2026-09-19 until 19.09.2027, 40 employers.")], 0, []),
    # A date with a time, a range of dotted dates and a run of years are as long as a phone number and
    # read as what they are. A phone number beside one is still a phone number.
    ("a closing date with a time", [("meta.lede", "Closes 2026-10-23 12:00, per the employer page.")], 0, []),
    ("a count taken at a date and a time", [("meta.lede", "9 positions counted at 2026-10-01 09:30 UTC.")], 0, []),
    ("a range of dotted dates", [("meta.lede", "Open 1.10.2026-31.10.2026.")], 0, []),
    ("a dotted date with spaces", [("meta.lede", "As of 1. 10. 2026, 40 employers.")], 0, []),
    ("a run of years", [("meta.lede", "Annual reports 2024 2025 2026 were read.")], 0, []),
    ("a dotted date with a single-digit day and a time", [("meta.lede", "Closes 5.10.2026 14:30.")], 0, []),
    ("a run of years joined by hyphens", [("meta.lede", "Annual reports 2023-2024-2025 were read.")], 0, []),
    ("a run of years joined by dots", [("meta.lede", "Annual reports 2023.2024.2025 were read.")], 0, []),
    ("a run of years in the last century", [("meta.lede", "Roles held 1998 1999 2000.")], 0, []),
    ("a phone number after a date and a time", [("meta.lede", "Closes 2026-10-23 12:00. Call 600 123 456.")], 1,
     ["meta.lede"]),
    # The mask takes out a date or a run of years and nothing that only looks like one.
    ("a phone number with a group that looks like a year", [("meta.footer", "Call 0800 2020 123.")], 1,
     ["meta.footer"]),
    ("a hyphenated number that is not a date", [("meta.footer", "Call 0123-45-67-89.")], 1, ["meta.footer"]),
    ("the end of a longer number that looks like a date", [("meta.footer", "Ref 92026-10-05.")], 1,
     ["meta.footer"]),
    ("the start of a longer number that looks like a date", [("meta.footer", "Ref 2026-10-0512.")], 1,
     ["meta.footer"]),
    ("the end of a longer number that looks like two years", [("meta.footer", "Ref 0123-2019 2020 123.")], 1,
     ["meta.footer"]),
    ("the start of a longer number that looks like two years", [("meta.footer", "Ref 2019 2020-0123 123.")], 1,
     ["meta.footer"]),
    ("a phone number after a run of years", [("meta.lede", "Reports 2024 2025 2026. Call 600 123 456.")], 1,
     ["meta.lede"]),
    # A run of years is joined by what joins the digits of a number: a space, a dot or a hyphen. Years
    # joined by a slash are not taken out, so the first of them still counts with the number before it.
    ("a number beside years joined by a slash", [("meta.lede", "Call 420.7890 2024/2025.")], 1, ["meta.lede"]),
    ("a product and a phase with a number", [("selling[0].text",
     "Led the Windows 11 rollout and Phase 2 of the audit.")], 0, []),
    ("a citation, and a number after Via", [("selling[0].text",
     "Smith et al. 2019 found it. Via 3 referrals and 2 agencies.")], 0, []),
    # Pay is written with grouped digits, and a range of two grouped numbers is the length of a phone
    # number. A currency beside digits says which of the two it is.
    ("a pay range in spaced thousands", [("market.families[0].pay",
     "55 000-75 000 CZK, stated in 5 of 7 postings")], 0, []),
    ("a pay range without separators", [("market.families[0].pay", "30000-45000 Kč, stated in 5 of 7")], 0, []),
    ("a pay range in dotted thousands", [("market.families[0].pay", "36.000-44.000 EUR, stated in 5 of 7")], 0, []),
    ("a pay range after a currency sign", [("market.families[0].pay",
     "€45 000-52 000 a year, stated in 5 of 7")], 0, []),
    ("a posting address that ends in a number", [("market.lines[0].src",
     "jobs-pl.example/offer?id=3891234567, 13 Sep")], 0, []),
    ("a WhatsApp link", [("meta.footer", "Write to wa.me/447700900123.")], 1, ["meta.footer"]),
    ("a Telegram handle", [("meta.footer", "Find them at t.me/someone_else.")], 1, ["meta.footer"]),
    ("a street address, French, capitalised", [("constraints.soft[0]",
     "Lives at 12 Rue de la Paix, Paris.")], 1, ["constraints.soft[0]"]),

    # What is scanned is what a reader sees. A typeset number puts a no-break or a thin space
    # between its groups and a non-breaking hyphen or an en dash between its parts, and text copied
    # from a document or a page carries characters that draw nothing. Read as raw code points, each
    # of these goes through.
    ("a phone number with no-break spaces", [("meta.footer", "Call +420\u00a0603\u00a0123\u00a0456.")], 1,
     ["meta.footer"]),
    ("a phone number with narrow no-break spaces", [("meta.footer",
     "Call +33\u202f6\u202f12\u202f34\u202f56\u202f78.")], 1, ["meta.footer"]),
    ("a phone number with thin spaces", [("meta.footer", "Call 600\u2009123\u2009456.")], 1, ["meta.footer"]),
    ("a phone number with non-breaking hyphens", [("meta.footer", "Call 555\u2011123\u20114567.")], 1,
     ["meta.footer"]),
    ("a phone number with en dashes", [("meta.footer", "Call 555\u2013123\u20134567.")], 1, ["meta.footer"]),
    ("a phone number cut by a direction mark", [("meta.footer", "Call 07700\u202a900123.")], 1, ["meta.footer"]),
    ("an email cut by a zero-width space", [("meta.footer", "Write to jane\u200b@example.com.")], 1,
     ["meta.footer"]),
    ("an email in fullwidth characters", [("meta.footer", "Write to jane\uff20example.com.")], 1,
     ["meta.footer"]),
    ("an email with a soft hyphen in its domain", [("meta.footer", "Write to jane@exam\u00adple.com.")], 1,
     ["meta.footer"]),
    ("a profile link cut by a word joiner", [("evidence[0].src", "linkedin.com/\u2060in/someone-else")], 1,
     ["evidence[0].src"]),
    ("a surname behind a zero-width space", [("meta.name", "Jane"),
     ("meta.lede", "Jane\u200b Doe is deciding where next.")], 1, ["meta.lede"]),
    ("a no-break space is an ordinary space to a pay range", [("market.families[0].pay",
     "55\u00a0000-75\u00a0000 CZK, stated in 5 of 7 postings")], 0, []),

    # A sum is not a number to ring. Pay is written with grouped digits, and a range of two grouped
    # numbers is the length of a phone number whether or not a currency comes with it, before or after.
    ("a pay range of six-figure sums after a currency sign", [("market.families[0].pay",
     "€145 000-152 000 a year, stated in 5 of 7 postings")], 0, []),
    ("a pay range behind a currency code", [("market.families[0].pay",
     "CHF 95 000-110 000 a year, stated in 4 of 6 postings")], 0, []),
    ("a pay range with no currency at all", [("market.families[0].pay",
     "55 000-75 000 brutto, stated in 5 of 7 postings")], 0, []),
    ("a pay range with no currency, in half thousands", [("market.families[0].pay",
     "52 500-61 500 a year, stated in 5 of 7 postings")], 0, []),
    ("a pay range in dotted thousands with no currency", [("market.families[0].pay",
     "36.000-44.000 brutto, stated in 5 of 7 postings")], 0, []),
    ("a pay range in millions", [("market.families[0].pay",
     "1 200 000-1 500 000 a year, stated in 3 of 4 postings")], 0, []),
    ("a headcount range", [("market.lines[0].text",
     "Firms of 20 000-25 000 employees hire most of them.")], 0, []),
    ("a sum of three groups with its currency sign after it", [("market.families[0].pay",
     "600 123 456 $ in total, stated in 5 of 7 postings")], 0, []),
    ("a phone number with two groups of three and one of four", [("meta.footer", "Call 600 123 4567.")], 1,
     ["meta.footer"]),
    ("a phone number that follows a pay range", [("meta.footer",
     "Floor 55 000-75 000 CZK. Call 600 123 456.")], 1, ["meta.footer"]),

    # Where a reader's eye and a code point part company. Unicode folds most spaces into the ordinary one
    # and does not fold an ogham space mark, and a minus sign is not a dash to it. A first name with a mark
    # that draws nothing in it is still the first name.
    ("a phone number with ogham space marks", [("meta.footer", "Call +420\u1680603\u1680123\u1680456.")], 1,
     ["meta.footer"]),
    ("a phone number with minus signs", [("meta.footer", "Call 555\u2212123\u22124567.")], 1, ["meta.footer"]),
    ("a surname behind a first name with an invisible mark in it", [("meta.name", "Jane\u200b"),
     ("meta.lede", "Jane Doe is deciding where next.")], 1, ["meta.lede"]),

    # What is a sum and what is a number to ring. A pound is a currency like the others, a code that
    # ends a longer word is not one, and a number does not hide behind a bracket or run into a letter.
    ("a pay range after a pound sign", [("market.families[0].pay",
     "£145 000-152 000 a year, stated in 5 of 7 postings")], 0, []),
    ("a sum of three groups after its currency code", [("market.families[0].pay",
     "EUR 600 123 456 in total, stated in 5 of 7 postings")], 0, []),
    ("a revenue range with spaces around the dash", [("market.lines[0].text",
     "Firms with a revenue of €120 000 000 - 150 000 000 hire most of them.")], 0, []),
    ("a phone number after a name in capitals that ends in a currency code", [("meta.footer",
     "Ask AARON 600 123 456.")], 1, ["meta.footer"]),
    ("a phone number with a bracketed group in the middle", [("meta.footer", "Call +1 800 (555) 1234.")], 1,
     ["meta.footer"]),
    ("digits that run into a letter are a reference", [("meta.footer", "Ref 600 123 456B.")], 0, []),
    # A range of grouped thousands is a sum where it starts a number. The end of a longer number is digits.
    ("a phone number that ends like a range of grouped thousands", [("meta.footer",
     "Call +420-603 123-456 789.")], 1, ["meta.footer"]),
    ("a number whose last groups look like a range of grouped thousands", [("meta.footer",
     "Ref 1234 000-75 000.")], 1, ["meta.footer"]),

    # The data sits in a script element. A browser ends that element at an end tag in any case,
    # with a space or a slash after it, and reads on from there as markup, so a field that holds
    # one becomes a page of its own. The checker has to see what the browser sees. A plain less-than
    # sign is not markup and stays legal.
    ("an end tag in the data", [("meta.lede", "Fine.</script><img src=x onerror=alert(1)>")], 1, ["u003c"]),
    ("an end tag in capitals", [("meta.lede", "Fine.</SCRIPT><img src=x>")], 1, ["u003c"]),
    ("an end tag with a space", [("meta.lede", "Fine.</script ><img src=x>")], 1, ["u003c"]),
    ("an end tag with a slash", [("meta.lede", "Fine.</script/><img src=x>")], 1, ["u003c"]),
    ("a comment opener before a start tag", [("meta.lede", "Fine <!--<script> and more.")], 1, ["u003c"]),
    ("a start tag in the data", [("meta.lede", "Fine <script>")], 1, ["u003c"]),
    ("a start tag in a key", [("meta", {"name": "Ira", "<SCRIPT": "x"})], 1, ["u003c"]),
    ("a bare less-than sign", [("market.families[0].pay", "Under 34k (<34k) is out.")], 0, []),
    # A comment opener alone leaves the end tag where it was, so it is only text.
    ("a comment opener alone", [("meta.lede", "Fine <!-- and more.")], 0, []),

    # A name of two short words is a name. Initials are single letters.
    ("a short full name", [("meta.name", "Jo Li")], 1, ["meta.name"]),
    # An organisation's page is a source, and a person's is not.
    ("an organisation page on GitHub", [("market.lines[0].src", "github.com/orgs/acme, 13 Sep")], 0, []),
]

# A label is often written with no space after it, and the number starts where the label ends. A comma
# stays out of that: job boards put an id after one.
CASES += [
    ("a phone number glued to its label by a dot", [("meta.footer", "Tel.603 123 456 after six.")], 1,
     ["meta.footer"]),
    ("a phone number in one group glued to its label by a dot", [("meta.footer", "Mob.603123456 after six.")], 1,
     ["meta.footer"]),
    ("an id after a comma in a job board address", [("market.lines[0].src",
     "example-board.pl/praca/analist,oferta,1003834432, 6 Oct")], 0, []),
    ("an id after a slash in a job board address", [("market.lines[0].src",
     "example-board.cz/rpd/2000123456/, 6 Oct")], 0, []),
    ("an id after a hyphen in a job board address", [("market.lines[0].src",
     "example-board.com/jobs/view/analyst-at-acme-3891234567, 6 Oct")], 0, []),
    ("a phone number before a word that only starts like a currency code", [("meta.footer",
     "Call 600 123 456 EUROPE.")], 1, ["meta.footer"]),
]

# What a pay range is written in. A range of plain numbers is as long as a phone number, and a currency
# beside it, before or after, says which of the two it is.
CURRENCIES = ("CZK", "PLN", "EUR", "USD", "GBP", "CHF", "SEK", "NOK", "DKK", "HUF", "RON", "CAD", "AUD",
              "JPY", "INR", "CNY", "AED", "SGD", "HKD", "NZD", "ZAR", "BRL", "MXN", "TRY", "ILS", "UAH",
              "BGN", "RSD", "ISK", "KRW", "RUB", "Kč", "zł", "Ft", "lei", "kr",
              "€", "$", "£", "¥", "₹", "₺", "₽", "₩", "₴")
CASES += [(f"a pay range after {code}", [("market.families[0].pay",
           f"{code} 6500000-9000000 a year, stated in 5 of 7 postings")], 0, [])
          for code in CURRENCIES]
CASES += [(f"a pay range before {code}", [("market.families[0].pay",
           f"6500000-9000000 {code} a year, stated in 5 of 7 postings")], 0, [])
          for code in CURRENCIES]
CASES += [("a phone number beside a code that is not a currency", [("meta.footer",
           "Call XYZ 6500000-9000000.")], 1, ["meta.footer"])]
# A number that ends a word is not a sum, so a currency after it belongs to the amount that follows.
CASES += [(f"a pay range after {label}", [("market.families[0].pay",
           f"{label} {pay} a year, stated in 5 of 7 postings")], 0, [])
          for label, pay in (("FY26", "\u20ac6500000-9000000"), ("Q3", "CZK 6500000-9000000"))]

# What comes after a run of combining marks is still read, and a run of spaces is one space.
CASES += [
    ("a phone number after a long run of combining marks", [("meta.footer",
     "e" + "\u0301" * 40 + " Call 603 123 456.")], 1, ["meta.footer"]),
    ("a surname behind two spaces", [("meta.name", "Jane"),
     ("meta.lede", "Jane  Doe is deciding where next.")], 1, ["meta.lede"]),
]

# A surname comes after a particle as often as not, in lower case.
CASES += [(f"a surname behind {particle}", [("meta.name", "Jane"),
           ("meta.lede", f"Jane {particle} Dijk is deciding where next.")], 1, ["meta.lede"])
          for particle in ("van", "von", "de", "der", "den", "da", "di", "del", "la", "le", "du", "dos", "ter",
                           "ten", "los", "las", "de la", "van der")]
CASES += [("the first name followed by a particle and a verb", [("meta.name", "Jane"),
           ("meta.lede", "Jane van decides where next.")], 0, [])]
# Some are written close up, with the surname after the particle and no space.
CASES += [(f"a surname behind {particle} written close up", [("meta.name", "Jane"),
           ("meta.lede", f"Jane {particle}{surname} is deciding where next.")], 1, ["meta.lede"])
          for particle, surname in (("de", "Leon"), ("van", "Dijk"), ("di", "Marco"))]
# A surname is quoted whole, hyphen and apostrophe included, so the run can find it.
CASES += [
    ("a surname with a hyphen", [("meta.name", "Jane"),
     ("meta.lede", "Jane Doe-Smith is deciding where next.")], 1, ["meta.lede", "'Jane Doe-Smith'"]),
    ("a surname with an apostrophe", [("meta.name", "Jane"),
     ("meta.lede", "Jane O'Neil is deciding where next.")], 1, ["meta.lede", "'Jane O'Neil'"]),
]
# A name is the same name however its accents are written, as a letter and a mark or as the one character,
# and a Vietnamese letter can carry two marks.
CASES += [
    ("a first name with an accent that is a mark of its own", [("meta.name", "Zoe\u0308"),
     ("meta.lede", "Zo\u00eb Doe is deciding where next.")], 1, ["meta.lede"]),
    ("a first name with two marks on one letter", [("meta.name", "Vie\u0323\u0302t"),
     ("meta.lede", "Vi\u1ec7t Doe is deciding where next.")], 1, ["meta.lede"]),
]

# A date is taken out of what the checker reads as a phone number at the edges of what a date can be, and no
# further. Counting the hour after it, each of these is as long as a phone number, so what the mask leaves in
# is what the checker flags.
CASES += [(f"{date} is a date", [("meta.footer", f"Closes {date} 12:00.")], 0, [])
          for date in ("2026-01-01", "2026-09-09", "2026-10-25", "2026-12-31", "1999-10-05", "2000-01-31",
                       "01.01.2026", "09.09.2026", "25.10.2026", "31.12.1999", "1.12.2026", "9.10.2026")]
CASES += [(f"{date} is only shaped like one", [("meta.footer", f"Call {date} 123.")], 1, ["meta.footer"])
          for date in ("2026-13-05", "2026-00-05", "2026-10-32", "2026-10-00", "1899-10-05", "2126-10-05",
                       "32.10.2026", "0.10.2026", "5.13.2026", "05.00.2026", "5.10.1899", "5.10.2126")]
