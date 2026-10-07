"""The page, through a browser: which sections are still drawn, and what the person sees where
one is not. The page is also read as text, for its example and its policy. These cases need
Playwright and a Chromium, and are skipped without them.

Run: python3 -I skills/careers/career-direction/evals/test_page.py
"""

import contextlib
import itertools
import json
import re
import sys
import tempfile
import time
import unittest
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None

# python -I leaves the folder of the script off the path, and the modules are beside it.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from harness import (
    BLOCK,
    CHOICES,
    DELETE,
    PAGE,
    family,
    first_pass,
    leaves,
    market_only,
    position,
    report,
)


# Everything the page shows or hides on its own. The example fills all of it.
IDS = ["shape", "s-evidence", "s-selling", "s-habits", "s-thread", "s-gaps", "s-constraints",
       "s-decisions", "s-corrections", "s-market", "s-skills", "s-families", "families-wrap", "skipped",
       "s-quadrant",
       "quadrant-wrap", "s-positions", "odds-note", "positions-wrap", "s-horizon", "ageing", "ages-well-wrap",
       "ages-badly-wrap", "clocks-wrap", "calendar-wrap", "s-glossary", "s-sources",
       "src-produced-wrap", "src-checked-wrap", "src-not-wrap"]
HORIZON = ["s-horizon", "ageing", "ages-well-wrap", "ages-badly-wrap", "clocks-wrap", "calendar-wrap"]
AGEING = ["ageing", "ages-well-wrap", "ages-badly-wrap"]

READ = """(ids) => ({
  shown: ids.filter(id => { const el = document.getElementById(id);
    return !!el && getComputedStyle(el).display !== "none" && el.offsetHeight > 0; }),
  error: document.getElementById("error").textContent,
  inError: document.querySelectorAll("#error *").length,
  title: document.getElementById("title").textContent,
  lede: document.getElementById("lede").textContent,
  skipped: document.getElementById("skipped").textContent,
  drawn: [...document.querySelectorAll("[hidden]")]
    .filter(el => getComputedStyle(el).display !== "none").map(el => el.id),
  hiddenIds: ids.filter(id => { const el = document.getElementById(id); return !!el && el.hidden; }),
  pwned: window.__pwned || null,
  handlers: document.querySelectorAll("[onerror]").length,
  images: document.querySelectorAll("img").length,
})"""

# name, edits, sections that must be gone, sections the banner must name ([] for no banner)
PAGE_CASES = [
    # One wrong type used to stop the page script, and every section after it was lost with
    # no word on screen. It costs the section it is in, and the page says which.
    ("shape as one string", [("shape", "One sentence.")], ["shape"], ["shape"]),
    ("constraints.hard as a string", [("constraints.hard", "A figure.")], ["s-constraints"], ["constraints"]),
    ("horizon.agesWell as a string", [("horizon.agesWell", "Accountability")], AGEING, ["ageing"]),
    ("families as an object", [("market.families", {"name": "x"})],
     ["families-wrap", "s-quadrant", "quadrant-wrap"], ["families", "quadrant"]),

    # The page reads null as absent and says nothing about it.
    ("horizon set to null", [("horizon", None)], HORIZON, []),

    # A column with nothing in it has no heading, and a section with nothing in it is not
    # there. Both used to draw as empty boxes, because a display rule beat the hidden attribute.
    ("agesBadly left out", [("horizon.agesBadly", DELETE)], ["ages-badly-wrap"], []),
    ("no ageing at all", [("horizon.agesWell", DELETE), ("horizon.agesBadly", DELETE)], AGEING, []),
    ("no shape", [("shape", [])], ["shape"], []),
    ("no evidence", [("evidence", [])], ["s-evidence"], []),
    ("no assets", [("selling", [])], ["s-selling"], []),
    ("no habits", [("habits", [])], ["s-habits"], []),
    ("no thread", [("thread", {"events": []})], ["s-thread"], []),
    ("no gaps", [("gaps", [])], ["s-gaps"], []),
    ("no constraints", [("constraints", {"hard": [], "soft": []})], ["s-constraints"], []),
    ("no decisions", [("decisions", [])], ["s-decisions"], []),
    ("no corrections", [("corrections", [])], ["s-corrections"], []),
    ("no market lines", [("market.lines", [])], ["s-market"], []),
    ("no skills", [("market.skills", [])], ["s-skills"], []),
    ("no positions", [("market.positions", [])], ["s-positions", "odds-note", "positions-wrap"], []),
    ("positions with no odds", [(f"market.positions[{i}].{key}", DELETE)
                                for i in range(3) for key in ("oddsNow", "oddsAfter")], ["odds-note"], []),
    ("no lanes", [("horizon.clocks.lanes", [])], ["clocks-wrap"], []),
    ("no calendar", [("horizon.calendar", [])], ["calendar-wrap"], []),
    ("no glossary", [("glossary", [])], ["s-glossary"], []),
    ("no line about what was cut", [("market.skipped", DELETE)], ["skipped"], []),
    ("an empty line about what was cut", [("market.skipped", "")], ["skipped"], []),
    ("no produced or checked sources", [("sources.produced", []), ("sources.checked", [])],
     ["src-produced-wrap", "src-checked-wrap"], []),
    ("no sources", [("sources", {})],
     ["s-sources", "src-produced-wrap", "src-checked-wrap", "src-not-wrap"], []),

    # A negative result is a result: every family cut still shows the reason, not the chart.
    ("every family cut", [("market.families", []), ("market.positions", DELETE)],
     ["families-wrap", "s-quadrant", "quadrant-wrap", "s-positions", "odds-note", "positions-wrap"], []),
]

# The sections of the page that can hide are the ones in its own markup: a list kept by hand would
# let a new section go untested.
HIDDEN_IDS = re.findall(r'<[^>]*\bid="([^"]+)"[^>]*\bhidden\b', PAGE)


# The text a person can read: what is left of the body once script, style and anything hidden are gone.
VISIBLE_TEXT = """() => {
  const body = document.body.cloneNode(true);
  body.querySelectorAll("script, style, [hidden]").forEach(el => el.remove());
  return body.textContent;
}"""

# What a person, an agent or a page it read may put into a field. The payload closes an attribute,
# opens an element and runs script, so one that is written into the page unescaped shows as an
# element with a handler, and one that runs shows as window.__pwned.
XSS = 'bad"><img src=x onerror="window.__pwned=1">'


# Four positions with every ranking pulling a different way: a lane, an odds figure each way, evidence.
POSITIONS = [position("A", "open", "thin", "later", "10%", "20%"),
             position("B", "closes", "strong", "now", "30%", "40%"),
             position("C", "recurs", "some", "build", "50%", "35%"),
             position("D", "closed", "strong", "build", "5%", "60%")]


# field, the chip it colours, and the colour each value gives it
TONE_CHIPS = [
    ("habits[0].tone", "#habits .habit:nth-child(1) .chip", {"good": "good", "amb": "amb", "bad": "bad"}),
    ("gaps[0].weight", "#gaps tbody tr:nth-child(1) .chip", {"decides": "bad", "slows": "amb", "closes doors": "acc"}),
    ("thread.events[0].verdict", "#thread .tl-row:nth-child(1) .chip", {"confirms": "good", "fails": "bad", "start": "plain"}),
]


FAMILY_CHIPS = """() => [...document.querySelectorAll("#families tbody tr")].map(row =>
  [...row.querySelectorAll(".chip")].slice(0, 3).map(chip => [chip.textContent, chip.classList[1]]))"""

# Everything printed on the chart and every point on it, as boxes on the screen.
CHART_ALL = """() => {
  const box = el => { const r = el.getBoundingClientRect(); return [r.left, r.top, r.right, r.bottom]; };
  return { svg: box(document.querySelector("#quadrant svg")),
           texts: [...document.querySelectorAll("#quadrant text")].map(t => ({ text: t.textContent, box: box(t) })),
           dots: [...document.querySelectorAll("#quadrant circle")].map(c => box(c)) };
}"""

# The words on the page that run over two lines, which is a word broken in the middle. A hyphen or a slash
# is a place to break, so a word with one is left out.
BROKEN_WORDS = r"""() => {
  const broken = [];
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let node = walker.nextNode(); node; node = walker.nextNode()) {
    if (node.parentElement.closest("script, style, svg")) continue;
    for (const word of node.textContent.matchAll(/[^\s\-\u2013\u2014\/]+/g)) {
      const range = document.createRange();
      range.setStart(node, word.index); range.setEnd(node, word.index + word[0].length);
      const lines = new Set([...range.getClientRects()].filter(r => r.width > 0).map(r => Math.round(r.top)));
      if (lines.size > 1) broken.push(word[0]);
    }
  }
  return broken;
}"""

# Each chip on the page, its text and how far its text stands out from what is behind it (WCAG contrast).
CHIP_CONTRAST = """() => {
  const parse = s => s.match(/[\\d.]+/g).map(Number);
  const light = ([r, g, b]) => { const f = c => (c /= 255) <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b); };
  const behind = el => { for (; el; el = el.parentElement) { const c = parse(getComputedStyle(el).backgroundColor);
    if (c.length < 4 || c[3] > 0) return c; } return [255, 255, 255, 1]; };
  return [...document.querySelectorAll(".chip")].filter(el => el.offsetParent).map(el => {
    const a = light(parse(getComputedStyle(el).color)), b = light(behind(el));
    return [el.textContent.trim(), (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05)]; });
}"""

WHEN_CHIPS = """() => [...document.querySelectorAll("#positions tbody tr")].map(row => {
  const chip = row.querySelector("td:nth-last-child(2) .chip");
  return [row.querySelector(".pos-emp").textContent, chip.textContent, chip.classList[1]]; })"""

STEPS = """() => [...document.querySelectorAll("#lanes .lane")].map(lane =>
  [...lane.querySelectorAll(".step")].map(s =>
    [s.querySelector("b").textContent, s.style.gridColumn, s.classList.contains("nolink")]))"""

# What the market-only page shows in the places that carry a judgement about a person.
MARKET_ONLY_PROBE = """() => {
  const words = (selector) => [...document.querySelectorAll(selector)].map(el => el.textContent.trim());
  return {
    emptyChips: words(".chip").filter(text => text === "").length,
    families: words("#families th"),
    positions: words("#positions th"),
    filters: [...document.querySelectorAll("#filters button")].map(b => b.firstChild.textContent),
    sorts: words("#sorts button"),
  };
}"""


@unittest.skipUnless(sync_playwright, "needs Playwright and a Chromium")
class ReportPage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        try:
            cls.browser = cls.playwright.chromium.launch()
        except Exception as error:
            cls.playwright.stop()
            raise unittest.SkipTest(f"no Chromium to launch: {error}")
        cls.base = cls.render(report())

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    @classmethod
    def render(cls, text, probe=None):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "report.html"
            path.write_text(text, encoding="utf-8")
            page = cls.browser.new_page()
            errors, requests = [], []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.on("request", lambda request: requests.append(request.url))
            page.goto(path.as_uri())
            seen = page.evaluate(READ, IDS)
            seen["probe"] = page.evaluate(probe) if probe else None
            page.close()
        seen["errors"] = errors
        seen["outside"] = [url for url in requests if not url.startswith("file:")]
        return seen

    def assert_nothing_is_drawn_empty(self, got):
        """Whatever is not on the page is hidden, and nothing hidden is on it."""
        self.assertEqual(got["drawn"], [], "a hidden element is still on the page")
        self.assertEqual(sorted(set(IDS) - set(got["shown"])), sorted(got["hiddenIds"]),
                         "something is on the page with nothing in it")

    def test_the_example_draws_every_section_and_says_nothing(self):
        self.assertEqual(sorted(self.base["shown"]), sorted(IDS))
        self.assertEqual(self.base["error"], "")
        self.assertEqual(self.base["errors"], [])

    def test_the_file_asks_nobody_for_anything(self):
        self.assertEqual(self.base["outside"], [])

    def test_a_report_that_is_the_market_only_draws_the_market_and_nothing_empty(self):
        got = self.render(report(whole=market_only()), MARKET_ONLY_PROBE)
        person = {"shape", "s-evidence", "s-selling", "s-habits", "s-thread", "s-gaps", "s-constraints",
                  "s-decisions", "s-corrections", "clocks-wrap", "odds-note"}
        self.assertEqual(sorted(set(self.base["shown"]) - person), sorted(got["shown"]))
        self.assert_nothing_is_drawn_empty(got)
        self.assertEqual((got["title"], got["error"]), ("Where next", ""))
        self.assertEqual(got["probe"], {
            "emptyChips": 0,
            "families": ["Buys", "Family", "Why it is on the list", "Demand counted",
                         "Trend, and what drives it", "Ages"],
            "positions": ["Position", "Family", "Status", "Evidence", "Note"],
            "filters": ["All", "Recurring or closed"],
            "sorts": [],
        })

    def assert_the_chart_reads(self, seen, where=""):
        """Nothing printed on the chart is outside it, over a point, or over anything else printed on it."""
        left, top, right, bottom = seen["svg"]
        for item in seen["texts"]:
            l, t, r, b = item["box"]
            self.assertTrue(left <= l and r <= right and top <= t and b <= bottom,
                            f"{where}'{item['text']}' is outside the picture")
            for dl, dt, dr, db in seen["dots"]:
                self.assertTrue(r <= dl or dr <= l or b <= dt or db <= t, f"{where}'{item['text']}' is over a point")
        for i, one in enumerate(seen["texts"]):
            for other in seen["texts"][i + 1:]:
                (l1, t1, r1, b1), (l2, t2, r2, b2) = one["box"], other["box"]
                self.assertTrue(r1 <= l2 or r2 <= l1 or b1 <= t2 or b2 <= t1,
                                f"{where}'{one['text']}' and '{other['text']}' overlap")

    @classmethod
    @contextlib.contextmanager
    def opened(cls, text, width=1280, scheme="light"):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "report.html"
            path.write_text(text, encoding="utf-8")
            page = cls.browser.new_page(viewport={"width": width, "height": 900}, color_scheme=scheme)
            page.goto(path.as_uri())
            try:
                yield page
            finally:
                page.close()

    def test_the_positions_can_be_filtered_and_sorted(self):
        with self.opened(report([("market.positions", POSITIONS)])) as page:
            employers = lambda: page.eval_on_selector_all(
                "#positions .pos-emp", "els => els.map(e => e.textContent)")
            press = lambda group, label: page.locator(
                group + " button", has_text=re.compile("^" + label)).click()
            labels = page.eval_on_selector_all("#filters button", "els => els.map(e => e.textContent)")
            self.assertEqual(labels, ["All4", "Now1", "After one build2", "Later1", "Recurring or closed2"])
            self.assertEqual(employers(), ["B", "D", "C", "A"], "lane, then odds after the gaps")
            for label, expected in [("Now", ["B"]), ("After one build", ["D", "C"]), ("Later", ["A"]),
                                    ("Recurring or closed", ["D", "C"]), ("All", ["B", "D", "C", "A"])]:
                press("#filters", label)
                self.assertEqual(employers(), expected, label)
            for label, expected in [("Odds now", ["C", "B", "A", "D"]), ("After gaps", ["D", "B", "C", "A"]),
                                    ("Evidence", ["D", "B", "C", "A"]), ("Lane, then odds", ["B", "D", "C", "A"])]:
                press("#sorts", label)
                self.assertEqual(employers(), expected, label)

    def test_the_theme_button_flips_the_theme_and_back(self):
        with self.opened(report()) as page:
            theme = lambda: page.evaluate("document.documentElement.getAttribute('data-theme')")
            self.assertIsNone(theme(), "follows the system until it is pressed")
            page.click("#themer")
            first = theme()
            page.click("#themer")
            self.assertEqual({first, theme()}, {"dark", "light"})

    def test_text_that_reverses_what_follows_it_is_not_drawn(self):
        # A name can be made to read backwards, and so can anything after it.
        got = self.render(report([("meta.name", "\u202eIra"), ("meta.lede", "a\u2066b\u202ec")]))
        self.assertEqual((got["title"], got["lede"]), ("Ira, where next", "abc"))

    def test_the_title_is_built_from_the_name_and_nothing_else(self):
        got = self.render(report([("meta.name", "Sam"), ("meta.title", "Something else")]))
        self.assertEqual(got["title"], "Sam, where next")

    def test_cases(self):
        for name, edits, gone, told in PAGE_CASES:
            with self.subTest(name):
                got = self.render(report(edits))
                lost = sorted(set(self.base["shown"]) - set(got["shown"]))
                self.assertEqual(got["errors"], [], "the page script threw")
                self.assertEqual(lost, sorted(gone))
                self.assert_nothing_is_drawn_empty(got)
                named = re.search(r"reads: ([^.]*)\.", got["error"])
                self.assertEqual(named.group(1).split(", ") if named else [], told)
                if not told:
                    self.assertEqual(got["error"], "")

    def test_the_list_of_sections_is_the_pages_own(self):
        self.assertEqual(sorted(IDS), sorted(HIDDEN_IDS))

    def test_a_first_pass_draws_what_it_has_and_nothing_else(self):
        got = self.render(report(whole=first_pass()))
        self.assertEqual(sorted(got["shown"]), sorted([
            "s-evidence", "s-gaps", "s-families", "families-wrap", "s-quadrant", "quadrant-wrap",
            "s-sources", "src-not-wrap"]))
        self.assert_nothing_is_drawn_empty(got)
        self.assertEqual(got["error"], "")

    def test_every_sentence_of_the_example_is_on_the_page(self):
        data = json.loads(BLOCK.search(PAGE).group(2))
        with self.opened(report()) as page:
            drawn = " ".join(page.evaluate(VISIBLE_TEXT).split())
        missing = [path for path, value in leaves(data)
                   if isinstance(value, str) and len(value) >= 10 and " ".join(value.split()) not in drawn]
        self.assertEqual(missing, [], "in the data and not on the page")

    def test_tone_words_colour_the_chips_they_name(self):
        for path, selector, table in TONE_CHIPS:
            for value, expected in table.items():
                with self.subTest(f"{path} = {value}"):
                    with self.opened(report([(path, value)])) as page:
                        classes = page.eval_on_selector(selector, "el => [...el.classList]")
                    self.assertIn(expected, classes)

    def test_skills_are_listed_from_most_counted_with_bars_to_scale(self):
        skills = [{"name": "Few", "countN": 2}, {"name": "Most", "countN": 9}, {"name": "Some", "countN": 4}]
        with self.opened(report([("market.skills", skills)])) as page:
            rows = page.eval_on_selector_all("#skills .skillrow", """els => els.map(row => [
                row.querySelector("b").textContent, row.querySelector(".n").textContent,
                row.querySelector(".skillbar span").style.width])""")
        self.assertEqual(rows, [["Most", "9", "100%"], ["Some", "4", "44%"], ["Few", "2", "22%"]])

    def test_chips_say_how_much_to_trust_a_family(self):
        # demand counted, one source or two, and how the asset ages: three chips, three colours
        wanted = [(0, "confirmed", "well", [["0 counted", "bad"], ["confirmed", "good"], ["well", "good"]]),
                  (1, "unconfirmed", "mixed", [["1 counted", "bad"], ["unconfirmed", "amb"], ["mixed", "amb"]]),
                  (2, "confirmed", "badly", [["2 counted", "amb"], ["confirmed", "good"], ["badly", "bad"]]),
                  (4, "unconfirmed", "well", [["4 counted", "amb"], ["unconfirmed", "amb"], ["well", "good"]]),
                  (5, "confirmed", "mixed", [["5 counted", "good"], ["confirmed", "good"], ["mixed", "amb"]]),
                  (12, "unconfirmed", "badly", [["12 counted", "good"], ["unconfirmed", "amb"], ["badly", "bad"]])]
        families = [family(buys=f"Buys {i}", name=f"Family {i}", demandN=n, sourcing=source, ages=ages)
                    for i, (n, source, ages, _) in enumerate(wanted)]
        with self.opened(report([("market.families", families)])) as page:
            chips = page.evaluate(FAMILY_CHIPS)
            height = page.eval_on_selector_all("#quadrant circle", "els => els.map(e => Number(e.getAttribute('cy')))")
        self.assertEqual(chips, [chips_ for *_, chips_ in wanted])
        by = lambda ages: [y for y, (*_, a, _c) in zip(height, wanted) if a == ages]
        self.assertLess(max(by("well")), min(by("mixed")), "an asset that ages well is drawn above one that does not")
        self.assertLess(max(by("mixed")), min(by("badly")))

    def test_families_that_buy_the_same_thing_share_a_cell(self):
        first, second, third = json.loads(BLOCK.search(PAGE).group(2))["market"]["families"]
        self.assertEqual(first["buys"], third["buys"], "the example no longer has two that share")
        self.assertNotEqual(first["buys"], second["buys"])
        with self.opened(report()) as page:
            names = page.eval_on_selector_all("#families tbody td > strong", "els => els.map(e => e.textContent)")
            cells = page.eval_on_selector_all("#families td.grp", "els => els.map(e => [e.textContent, e.rowSpan])")
        self.assertEqual(names, [first["name"], third["name"], second["name"]])
        self.assertEqual(cells, [[first["buys"], 2], [second["buys"], 1]])

    def test_on_a_phone_the_chart_scrolls_instead_of_shrinking_past_reading(self):
        with self.opened(report(), width=390) as page:
            chart = page.eval_on_selector("#quadrant", """el => ({
                drawn: el.querySelector("svg").getBoundingClientRect().width,
                scrolls: el.scrollWidth > el.clientWidth })""")
            across = page.evaluate("document.documentElement.scrollWidth")
        self.assertGreaterEqual(chart["drawn"], 700, "the chart's text would be too small to read")
        self.assertTrue(chart["scrolls"])
        self.assertLessEqual(across, 390, "the page itself scrolls sideways")

    def test_printed_no_table_and_no_chart_runs_off_the_sheet(self):
        # On a screen a wide table scrolls inside its wrapper. Paper does not scroll, so what sits past the edge
        # of the sheet is lost: the verdict column, and the whole of a position's note.
        read = """() => {
            const inside = (inner, outer) => inner.getBoundingClientRect().right <= outer.getBoundingClientRect().right + 1
                && outer.scrollWidth <= outer.clientWidth + 1;
            return { tables: [...document.querySelectorAll(".tablewrap")].filter(w => w.offsetParent !== null)
                        .map(w => [w.querySelector("table").id, inside(w.querySelector("table"), w)]),
                     chart: inside(document.querySelector("#quadrant svg"), document.getElementById("quadrant")),
                     page: document.documentElement.scrollWidth }; }"""
        for width in (794, 718):   # an A4 sheet with no margin, and with the margin a browser leaves
            with self.subTest(width):
                with self.opened(report(), width=width) as page:
                    page.emulate_media(media="print")
                    seen = page.evaluate(read)
                self.assertEqual(sorted(name for name, _ in seen["tables"]),
                                 ["calendar", "families", "gaps", "positions"])
                self.assertEqual([name for name, fits in seen["tables"] if not fits], [],
                                 "a table runs off the sheet")
                self.assertTrue(seen["chart"], "the chart runs off the sheet")
                self.assertLessEqual(seen["page"], width, "the page is wider than the sheet")

    def test_printed_the_controls_are_left_off_and_a_frame_is_not_split_across_two_sheets(self):
        # The theme button and the filters work on a screen and mean nothing on paper. A chart that starts near
        # the foot of a sheet goes to the next one whole, and the sheet is the whole width.
        read = """() => ({
            controls: [...document.querySelectorAll(".themer, .bar")].map(el => getComputedStyle(el).display),
            frames: [...document.querySelectorAll(".frame")].map(el => getComputedStyle(el).breakInside),
            padding: getComputedStyle(document.body).paddingLeft })"""
        with self.opened(report(), width=794) as page:
            page.emulate_media(media="print")
            seen = page.evaluate(read)
        self.assertGreater(len(seen["controls"]), 1, "the page has controls to leave off")
        self.assertEqual(set(seen["controls"]), {"none"}, "a control is printed")
        self.assertTrue(seen["frames"], "the page has a frame to keep whole")
        self.assertEqual(set(seen["frames"]), {"avoid"}, "a frame may be cut by the edge of a sheet")
        self.assertEqual(seen["padding"], "0px", "the sheet has its own margin; the page adds none")

    def test_long_text_in_any_field_does_not_push_the_page_sideways(self):
        # A label that runs on, and a string with nowhere to break, in every text field at once. The chart
        # scrolls inside its own frame on purpose, so the page is what must stay put.
        data = json.loads(BLOCK.search(PAGE).group(2))
        for name, stuffing in [("a long label", "the way people write when they put it all into one label, " * 4),
                               ("no place to break", "x" * 120)]:
            edits = [(path, stuffing + value) for path, value in leaves(data)
                     if isinstance(value, str) and len(value) > 3 and path != "meta.name"]
            with self.subTest(name):
                with self.opened(report(edits), width=390) as page:
                    across = page.evaluate("document.documentElement.scrollWidth")
                self.assertLessEqual(across, 390, "the page scrolls sideways")

    def test_on_a_phone_no_word_of_the_report_breaks_in_the_middle(self):
        # Room for a long string must not come from squeezing a short label until it splits: "Fast", a
        # decision's two words and a heading are the places a narrow column does that.
        for name, text in [("the example", report()), ("the market only", report(whole=market_only()))]:
            for width in (390, 320):
                with self.subTest(f"{name} at {width}"):
                    with self.opened(text, width=width) as page:
                        self.assertEqual(page.evaluate(BROKEN_WORDS), [])

    def test_every_chip_is_readable_in_both_colour_schemes(self):
        # Chips are small and set in capitals, so their text has to stand out well: 4.5 to one is the floor.
        for scheme in ("light", "dark"):
            with self.subTest(scheme):
                with self.opened(report(), scheme=scheme) as page:
                    chips = page.evaluate(CHIP_CONTRAST)
                self.assertGreater(len(chips), 20)
                for text, ratio in chips:
                    self.assertGreaterEqual(ratio, 4.5, f"'{text}' reads at {ratio:.2f} to one in {scheme}")

    def test_on_a_phone_the_clock_steps_stack_at_the_width_of_their_lane(self):
        # Twelve columns across a phone leave each step a few words wide, so the steps come one under another.
        widths = """() => [...document.querySelectorAll("#lanes .lane")].map(lane => {
            const track = lane.querySelector(".track").getBoundingClientRect();
            return [...lane.querySelectorAll(".step")].map(s => [s.getBoundingClientRect().width, track.width]); })"""
        with self.opened(report(), width=390) as page:
            lanes = page.evaluate(widths)
        self.assertTrue(lanes and all(lanes), "no clock steps to measure")
        for lane in lanes:
            for step, track in lane:
                self.assertGreaterEqual(step, track - 2, "a step is narrower than its lane on a phone")
        with self.opened(report(), width=1280) as page:
            lanes = page.evaluate(widths)
        self.assertTrue(any(step < track - 2 for lane in lanes for step, track in lane),
                        "on a wide screen the steps sit side by side along the track")

    def test_a_long_chip_in_a_table_wraps_inside_its_cell(self):
        # A verdict is free text in a chip. It wraps to fit its column instead of making the row run on.
        said = "only worth it after the certificate and a year on the floor, if the budget allows it"
        verdict_chip = """() => { const chip = [...document.querySelectorAll("#families tbody .chip")]
            .find(c => c.textContent.startsWith("only worth it")); const r = chip.getBoundingClientRect();
            return [r.width, r.height]; }"""
        with self.opened(report([("market.families[0].verdict", said)])) as page:
            width, height = page.evaluate(verdict_chip)
        self.assertGreater(height, 40, "a long verdict stays on one line")
        self.assertLess(width, 400, "a long verdict makes its chip as wide as the sentence")

    def test_a_short_chip_stays_on_one_line(self):
        # Making room for long text must not squeeze a narrow column until a word breaks inside its chip.
        for width in (1280, 390):
            with self.subTest(width):
                with self.opened(report(), width=width) as page:
                    broken = page.eval_on_selector_all(".chip", """els => els
                        .filter(e => e.textContent.trim().length <= 10 && e.getBoundingClientRect().height > 30)
                        .map(e => e.textContent)""")
                self.assertEqual(broken, [])

    def test_a_family_note_with_no_verdict_is_headed_as_a_note(self):
        # A verdict is a judgement about a person. A market-only report may still say something about a family.
        noted = market_only()
        noted["market"]["families"][0]["note"] = "Four postings accept an equivalent system"
        judged = market_only()
        judged["market"]["families"][0].update({"verdict": "lead with this", "verdictTone": "good", "note": "A note"})
        last = "() => [...document.querySelectorAll('#families th')].pop().textContent"
        with self.opened(report(whole=noted)) as page:
            self.assertEqual(page.evaluate(last), "Note")
        with self.opened(report(whole=judged)) as page:
            self.assertEqual(page.evaluate(last), "Verdict")

    def test_a_chart_with_nothing_counted_is_still_drawn(self):
        with self.opened(report([("market.families", [family(demandN=0)])])) as page:
            self.assertEqual(page.locator("#quadrant circle").count(), 1, "the one family has a point")
            self.assertNotIn("NaN", page.inner_html("#quadrant"))

    def test_seventeen_families_do_not_hold_the_page_up(self):
        # Names are placed by a search over a few places each, and the page draws nothing until it ends. Left to
        # run to its end it takes seconds at fifteen points that sit close together, and minutes a few more. The
        # skill asks for three to five and the checker only notes a longer report, so what a page does with
        # more is its own business.
        families = [family(buys=str(i), name=f"Family number {i} with a name as long as the real ones are",
                           demandN=1 + i, ages="mixed", verdict=f"A verdict {i} of some length")
                    for i in range(17)]
        started = time.monotonic()
        with self.opened(report([("market.families", families)])) as page:
            names = page.eval_on_selector_all("#quadrant text", "els => els.map(e => e.textContent)")
        self.assertLess(time.monotonic() - started, 5, "the names took seconds to place")
        self.assertEqual(len([name for name in names if name.startswith("Family number")]), 17)

    def test_names_on_the_chart_clear_every_point_and_each_other_wherever_the_points_fall(self):
        # The example's own families, long names and verdicts and all. In one row is the worst case, since a
        # name is wider than the gap between neighbours; the rest are a few spreads across rows.
        example = json.loads(BLOCK.search(PAGE).group(2))["market"]["families"]
        same_row = [[(n, "mixed") for n in counts] for counts in itertools.product([2, 7, 14], repeat=3)]
        spread = [[(11, "well"), (5, "mixed"), (14, "badly")], [(14, "well"), (14, "mixed"), (14, "badly")],
                  [(0, "well"), (0, "well"), (14, "well")], [(14, "mixed"), (13, "mixed"), (12, "mixed")],
                  [(0, "badly"), (7, "badly"), (14, "badly")], [(14, "well"), (14, "well"), (14, "well")],
                  [(0, "mixed"), (0, "mixed"), (0, "mixed")], [(13, "well"), (14, "mixed"), (9, "mixed")]]
        for layout in same_row + spread:
            with self.subTest(layout):
                families = [{**one, "demandN": n, "ages": ages} for one, (n, ages) in zip(example, layout)]
                with self.opened(report([("market.families", families)])) as page:
                    self.assert_the_chart_reads(page.evaluate(CHART_ALL), f"{layout}: ")

    def test_chart_labels_stay_inside_the_picture_and_apart(self):
        points = [("Busiest family, with a long name", 14, "well"), ("Twin of the busiest, long name", 14, "well"),
                  ("Nothing counted", 0, "badly")]
        families = [family(buys=str(i), name=name, demandN=n, ages=ages, verdict=f"Verdict {i}")
                    for i, (name, n, ages) in enumerate(points)]
        with self.opened(report([("market.families", families)])) as page:
            seen = page.evaluate(CHART_ALL)
        self.assert_the_chart_reads(seen)
        self.assertIn("Verdict 0", [item["text"] for item in seen["texts"]], "a verdict is written by its point")

    def test_a_verdict_wider_than_its_name_is_kept_clear_of_the_next_point(self):
        # Where a name goes depends on how much room it takes, and a verdict under a short name is the wider of
        # the two. Three points a hand's width apart, so one verdict runs under the next point's name.
        verdict = "A verdict long enough to run under the next point as well"
        families = [family(buys=str(i), name=name, demandN=n, ages="mixed", verdict=verdict)
                    for i, (name, n) in enumerate([("A", 6), ("B", 7), ("C", 8)])]
        with self.opened(report([("market.families", families)])) as page:
            self.assert_the_chart_reads(page.evaluate(CHART_ALL))

    def test_the_good_corner_is_named_above_the_frame(self):
        # The names are set inside the frame, so the one label that is always drawn stays out of their way.
        with self.opened(report()) as page:
            caption = page.locator("#quadrant text", has_text="hiring now, and it keeps paying").bounding_box()
            corner = page.locator("#quadrant rect").first.bounding_box()
        self.assertLessEqual(caption["y"] + caption["height"], corner["y"])

    def test_families_with_the_same_count_and_ageing_do_not_hide_each_other(self):
        # Points that would sit on one another: the count is the horizontal place and stays put, the row is
        # only a band, so the later ones are moved up or down inside it.
        def draw(counts):
            families = [family(buys=str(i), name=f"Family {i}", demandN=n, ages="mixed", verdict=f"Verdict {i}",
                               sourcing="unconfirmed" if i % 2 else "confirmed") for i, n in enumerate(counts)]
            with self.opened(report([("market.families", families)])) as page:
                points = page.eval_on_selector_all(
                    "#quadrant circle", "els => els.map(e => [Number(e.getAttribute('cx')), Number(e.getAttribute('cy'))])")
                middle = page.eval_on_selector_all("#quadrant line.grid", "els => els.map(e => Number(e.getAttribute('y1')))")[1]
                return points, middle, page.evaluate(CHART_ALL)
        for counts in ([6, 6], [6, 7, 190], [6, 6, 6], [6, 6, 6, 6, 6]):
            with self.subTest(counts):
                points, middle, seen = draw(counts)
                for n in set(counts):
                    self.assertEqual(len({round(x) for (x, _), c in zip(points, counts) if c == n}), 1, "the count moved")
                for i, (x, y) in enumerate(points):
                    self.assertLess(abs(y - middle), 60, "a stacked point left its row")
                    for other_x, other_y in points[i + 1:]:
                        self.assertTrue(abs(x - other_x) >= 18 or abs(y - other_y) >= 18, "two points sit on one another")
                self.assert_the_chart_reads(seen)

    def test_a_count_from_one_source_is_drawn_hollow_and_the_caption_says_so(self):
        families = [family(buys="0", name="Two sources", sourcing="confirmed", ages="well"),
                    family(buys="1", name="One source", sourcing="unconfirmed", ages="well"),
                    family(buys="2", name="Silent", ages="well")]
        del families[2]["sourcing"]
        paint = """() => [...document.querySelectorAll("#quadrant circle")].map(c => {
            const s = getComputedStyle(c); return [s.fill, s.stroke]; })"""
        with self.opened(report([("market.families", families)])) as page:
            two, one, silent = page.evaluate(paint)
            caption = page.text_content("#quadrant-cap")
        self.assertNotEqual(two[0], two[1], "a filled point and its outline differ")
        self.assertEqual(one, [two[1], two[0]], "a hollow point swaps its fill and its outline")
        self.assertEqual(silent, two, "no claim about sources, no hollow point")
        self.assertIn("hollow", caption)
        with self.opened(report([("market.families", families[:1])])) as page:
            self.assertNotIn("hollow", page.text_content("#quadrant-cap"))

    def test_a_position_with_no_lane_the_page_knows_goes_last(self):
        rows = [position("Z", "open", "strong", "someday", "90%", "90%"),
                position("L", "open", "thin", "later", "10%", "10%"),
                position("B", "open", "thin", "build", "10%", "10%"),
                position("N", "open", "thin", "now", "10%", "10%")]
        with self.opened(report([("market.positions", rows)])) as page:
            chips = page.evaluate(WHEN_CHIPS)
        self.assertEqual(chips, [["N", "now", "good"], ["B", "after one build", "amb"],
                                 ["L", "later", "acc"], ["Z", "someday", "acc"]])

    def test_the_lane_sort_names_what_breaks_a_tie_within_a_lane(self):
        # With odds, the tie is broken by them. Without, only the evidence is left, and the button says so.
        rows = [{"employer": name, "title": "Role", "status": "open", "evidence": evidence, "when": when}
                for name, evidence, when in [("A", "thin", "now"), ("B", "strong", "now"),
                                              ("C", "some", "now"), ("D", "strong", "later")]]
        sorts = "els => els.map(e => e.textContent)"
        with self.opened(report([("market.positions", rows)])) as page:
            plain = page.eval_on_selector_all("#sorts button", sorts)
            order = page.eval_on_selector_all("#positions .pos-emp", "els => els.map(e => e.textContent)")
        with self.opened(report([("market.positions", POSITIONS)])) as page:
            odds = page.eval_on_selector_all("#sorts button", sorts)
        self.assertEqual(plain, ["Lane, then evidence", "Evidence"])
        self.assertEqual(order, ["B", "C", "A", "D"])
        self.assertEqual(odds[0], "Lane, then odds")

    def test_positions_that_tie_are_ordered_by_what_the_reader_needs_next(self):
        # One lane. Odds after the gaps first, a range read at its top; then odds now, evidence, the name.
        rows = [position("D", "open", "thin", "now", "10%", "50%"),
                position("C", "open", "thin", "now", "20%", "50%"),
                position("B", "open", "strong", "now", "20%", "50%"),
                position("A", "open", "strong", "now", "20%", "50%"),
                position("Top, by its range", "open", "thin", "now", "10%", "30-70%")]
        with self.opened(report([("market.positions", rows)])) as page:
            order = page.eval_on_selector_all("#positions .pos-emp", "els => els.map(e => e.textContent)")
        self.assertEqual(order, ["Top, by its range", "A", "B", "C", "D"])

    def test_clock_steps_run_in_order_on_the_track(self):
        lanes = [{"name": "One", "sub": "", "steps": [{"at": 8, "span": 2, "label": "third"},
                                                       {"at": 0, "span": 3, "label": "first"},
                                                       {"at": 3, "span": 3, "label": "second"}]},
                 {"name": "Two", "sub": "", "steps": [{"at": 12, "span": 3, "label": "late"},
                                                       {"at": 10, "span": 5, "label": "edge"}]}]
        with self.opened(report([("horizon.clocks.lanes", lanes)])) as page:
            lanes = page.evaluate(STEPS)
        # Steps that touch are linked, one with a gap after it is not, and a step off the end is held on it.
        self.assertEqual(lanes, [[["first", "1 / span 3", False], ["second", "4 / span 3", True],
                                  ["third", "9 / span 2", True]],
                                 [["edge", "11 / span 2", False], ["late", "12 / span 1", True]]])

    def test_axis_labels_sit_on_the_columns_they_name(self):
        with self.opened(report([("horizon.clocks.axis", ["now", "a", "b", "c"])])) as page:
            labels = page.eval_on_selector_all("#axislabels span", "els => els.map(e => [e.textContent, e.style.gridColumn])")
        self.assertEqual(labels, [["now", "1 / span 3"], ["a", "4 / span 3"], ["b", "7 / span 3"], ["c", "10 / span 3"]])

    def test_on_a_phone_each_clock_step_carries_its_own_dates(self):
        # The steps stack there, so an axis under them would name columns that are no longer in view.
        read = """() => ({
            axis: getComputedStyle(document.getElementById("axislabels")).display,
            when: [...document.querySelectorAll("#lanes .step .when")].map(w => [w.textContent, getComputedStyle(w).display]) })"""
        step = lambda at, span: {"at": at, "span": span, "label": f"from {at}"}
        # A step reads from the label under its first column to the one under its last, in the order it runs.
        # Four labels start on columns 0, 3, 6 and 9. Five do not divide twelve: they start on 0, 2, 5, 7 and 10.
        for axis, steps, wanted in [
                (["now", "a", "b", "c"], [step(9, 3), step(0, 3), step(4, 5)], ["now", "a → b", "c"]),
                (["v", "w", "x", "y", "z"], [step(7, 1), step(4, 1), step(10, 2)], ["w", "y", "z"])]:
            edits = [("horizon.clocks.axis", axis), ("horizon.clocks.lanes", [{"name": "One", "sub": "", "steps": steps}])]
            with self.subTest(axis):
                with self.opened(report(edits), width=390) as page:
                    phone = page.evaluate(read)
                with self.opened(report(edits), width=1280) as page:
                    wide = page.evaluate(read)
                self.assertEqual(phone["axis"], "none")
                self.assertEqual(phone["when"], [[when, "block"] for when in wanted])
                self.assertEqual(wide["axis"], "grid", "on a wide screen the axis stays under the lanes")
                self.assertEqual(wide["when"], [[when, "none"] for when in wanted])
        with self.opened(report([("horizon.clocks.axis", DELETE)]), width=390) as page:
            self.assertEqual(page.evaluate(read)["when"], [], "no axis, nothing to say about when")

    def test_the_header_and_footer_say_what_the_data_says_and_fall_back_when_it_is_silent(self):
        data = json.loads(BLOCK.search(PAGE).group(2))
        asof = data["market"]["asOf"]
        with self.opened(report()) as page:
            self.assertEqual(page.text_content("#foot"), f"{data['meta']['footer']} Market data as of {asof}.")
            self.assertTrue(page.text_content("#market-note").startswith(f"What the research supports, as of {asof}."))
        silent = [("meta.eyebrow", DELETE), ("evidence[0].src", DELETE), ("market.lines[0].src", DELETE)]
        with self.opened(report(silent)) as page:
            self.assertEqual(page.text_content("#eyebrow"), "Direction review")
            self.assertEqual(page.locator("#evidence .src").first.text_content(), "source not recorded")
            self.assertIn("source not recorded", page.locator("#lines .linecard").first.text_content())

    def test_small_things_are_drawn_the_way_they_are_read(self):
        data = json.loads(BLOCK.search(PAGE).group(2))
        self.assertGreater(len(data["shape"]), 1)
        with self.opened(report([("constraints.soft", [])])) as page:
            self.assertEqual(page.eval_on_selector_all("#constraints h4", "els => els.map(e => e.textContent)"), ["Hard"])
        with self.opened(report()) as page:
            numbered = page.eval_on_selector_all("#selling .n", "els => els.map(e => e.textContent)")
            labelled = page.eval_on_selector_all("#shape p", "els => els.map(p => !!p.querySelector('strong'))")
            terms = page.eval_on_selector_all("#glossary dt", "els => els.map(e => e.textContent)")
            meanings = page.eval_on_selector_all("#glossary dd", "els => els.map(e => e.textContent)")
            well = page.eval_on_selector_all("#ages-well .chip", "els => els.map(e => e.classList[1])")
            badly = page.eval_on_selector_all("#ages-badly .chip", "els => els.map(e => e.classList[1])")
        self.assertEqual(numbered, [f"Asset {i}" for i in range(1, len(data["selling"]) + 1)])
        self.assertEqual(labelled, [True] + [False] * (len(data["shape"]) - 1), "only the first is labelled")
        self.assertEqual((terms, meanings), ([t for t, _ in data["glossary"]], [m for _, m in data["glossary"]]))
        self.assertEqual((set(well), set(badly)), ({"good"}, {"bad"}))

    def test_what_was_typed_is_what_is_shown(self):
        typed = 'Tom & Jerry\'s "plan" <b>not bold</b> &lt;i&gt; &amp; done'
        with self.opened(report([("shape[0]", typed)])) as page:
            drawn = page.eval_on_selector("#shape p", "p => p.textContent.replace(/^The shape\\. /, '')")
            bold = page.eval_on_selector_all("#shape b", "els => els.length")
        self.assertEqual((drawn, bold), (typed, 0))

    def test_a_value_that_is_a_property_of_every_object_is_just_an_unknown_value(self):
        for word in ("constructor", "__proto__", "toString", "hasOwnProperty"):
            with self.subTest(word):
                with self.opened(report([(path, word) for path in CHOICES])) as page:
                    seen = page.evaluate("""() => ({
                        nan: document.querySelector("#quadrant").innerHTML.includes("NaN"),
                        empty: [...document.querySelectorAll(".chip")].filter(c => !c.textContent.trim()).length,
                        error: document.getElementById("error").textContent })""")
                self.assertEqual(seen, {"nan": False, "empty": 0, "error": ""})

    def test_a_negative_result_is_still_shown(self):
        got = self.render(report([("market.families", []), ("market.positions", DELETE)]))
        self.assertIn("s-families", got["shown"])
        self.assertNotEqual(got["skipped"].strip(), "")

    def assert_no_markup(self, got):
        self.assertEqual(got["errors"], [])
        self.assertIsNone(got["pwned"], "the payload ran")
        self.assertEqual((got["handlers"], got["images"]), (0, 0), "the payload became markup")

    def test_a_payload_in_every_text_field_never_becomes_markup(self):
        data = json.loads(BLOCK.search(PAGE).group(2))
        edits = [(path, XSS) for path, value in leaves(data) if isinstance(value, str)]
        self.assert_no_markup(self.render(report(edits)))

    def test_a_payload_in_every_number_field_never_becomes_markup(self):
        data = json.loads(BLOCK.search(PAGE).group(2))
        edits = [(path, XSS) for path, value in leaves(data) if isinstance(value, (int, float))]
        self.assertGreater(len(edits), 10, "the example has numbers to try")
        self.assert_no_markup(self.render(report(edits)))

    def test_what_the_parser_says_about_broken_data_is_text_not_markup(self):
        got = self.render(BLOCK.sub(lambda m: m.group(1) + "<i id=probe>x</i>" + m.group(3), PAGE, count=1))
        self.assertIn("not valid JSON", got["error"])
        self.assertEqual(got["inError"], 1, "the message became markup")

    def test_the_escaped_less_than_sign_is_shown_as_text(self):
        got = self.render(report([("meta.lede", "MARK")]).replace("MARK", "Fine.\\u003c/script\\u003e"))
        self.assertEqual((got["lede"], got["errors"], got["error"]), ("Fine.</script>", [], ""))

    def test_a_breakout_from_the_data_runs_nothing(self):
        # What the checker refuses, in a file nobody checked. The policy is the second lock.
        got = self.render(report([("meta.lede", "x</script><img src=x onerror=window.__pwned=1>")]))
        self.assertIsNone(got["pwned"], "the payload ran")

    def test_json_that_does_not_parse_is_said_on_screen(self):
        broken = BLOCK.sub(lambda m: m.group(1) + '{"meta": }' + m.group(3), PAGE, count=1)
        got = self.render(broken)
        self.assertEqual(got["errors"], [])
        self.assertIn("not valid JSON", got["error"])

    def test_json_that_is_not_an_object_is_said_on_screen(self):
        for text in ("[]", '"report"', "null", "7"):
            with self.subTest(text):
                got = self.render(BLOCK.sub(lambda m: m.group(1) + text + m.group(3), PAGE, count=1))
                self.assertEqual(got["errors"], [])
                self.assertIn("has to be an object", got["error"])


if __name__ == "__main__":
    unittest.main()
