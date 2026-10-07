"""What the checker and page cases share: the example report, the edits that break it, and the
commands that run the checker on a report. Nothing here imports the checker, so it can be
rewritten without touching a case.
"""

import base64
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


SKILL = Path(__file__).resolve().parent.parent
CHECKER = SKILL / "scripts" / "report_check.py"
PAGE = (SKILL / "assets" / "direction-report.html").read_text(encoding="utf-8")
BLOCK = re.compile(r'(<script type="application/json" id="report-data">)(.*?)(</script>)', re.S)

DELETE = object()


def apply(data, edits):
    """Edits are (path, value) pairs like ("gaps[0].weight", "slows"); DELETE removes."""
    for dotted, value in edits:
        *parents, last = re.findall(r"[^.\[\]]+", dotted)
        node = data
        for key in parents:
            node = node[int(key)] if key.isdigit() else node[key]
        key = int(last) if last.isdigit() else last
        if value is DELETE:
            del node[key]
        else:
            node[key] = value
    return data


def leaves(node, path=""):
    """(path, value) for every string and every number in the data, paths as apply() reads them."""
    if isinstance(node, dict):
        for key, value in node.items():
            yield from leaves(value, f"{path}.{key}" if path else key)
    elif isinstance(node, list):
        for i, value in enumerate(node):
            yield from leaves(value, f"{path}[{i}]")
    else:
        yield path, node


def report(edits=(), whole=None):
    """The example page with its data block edited, as text."""
    data = json.loads(BLOCK.search(PAGE).group(2))
    data = apply(data, edits) if whole is None else whole
    block = json.dumps(data, ensure_ascii=False, indent=1)
    return BLOCK.sub(lambda m: m.group(1) + "\n" + block + "\n" + m.group(3), PAGE, count=1)


def row_of(data, dotted):
    """The row at a path like market.families[0], read the way apply() reads it."""
    node = data
    for key in re.findall(r"[^.\[\]]+", dotted):
        node = node[int(key)] if key.isdigit() else node[key]
    return node


def market_only():
    """The example with everything only a conversation could fill taken out: the person, and
    every judgement about them. This is what a run with nobody to ask produces."""
    data = json.loads(BLOCK.search(PAGE).group(2))
    for key in ("shape", "evidence", "selling", "habits", "thread", "gaps", "constraints", "decisions",
                "corrections"):
        del data[key]
    del data["meta"]["name"]
    del data["horizon"]["clocks"]
    for shift in data["horizon"]["shifts"]:
        del shift["worthTo"]
    for skill in data["market"]["skills"]:
        skill.pop("note", None)
    for family in data["market"]["families"]:
        for key in ("verdict", "verdictTone", "note"):
            family.pop(key, None)
    for position in data["market"]["positions"]:
        for key in ("when", "oddsNow", "oddsAfter"):
            position.pop(key, None)
    return data


def check(page_text, *options):
    """Run the checker on a page given as text, or as bytes that are not text at all."""
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "report.html"
        if isinstance(page_text, bytes):
            path.write_bytes(page_text)
        else:
            path.write_text(page_text, encoding="utf-8")
        done = subprocess.run([sys.executable, str(CHECKER), str(path), *options],
                              capture_output=True, text=True, timeout=30)
    return done.returncode, done.stdout, done.stderr


def digest_of(page_text):
    """The digest a browser computes for the page's one script: SHA-256 of its text, in base64."""
    script = re.search(r"<script>(.*?)</script>", page_text, re.S).group(1)
    return base64.b64encode(hashlib.sha256(script.encode("utf-8")).digest()).decode()


# What each kind of row cannot do without, written from the contract rather than read from the
# checker. Anything else in a row may be left out, and the checker must not insist on it.
REQUIRED_KEYS = {
    "evidence[0]": ["title", "text", "src"],
    "selling[0]": ["title", "text"],
    "habits[0]": ["label", "tone", "text"],
    "thread.events[0]": ["year", "kind", "title"],
    "gaps[0]": ["gap", "weight", "evidence", "fix"],
    "decisions[0]": ["label", "text"],
    "market.lines[0]": ["text", "src"],
    "market.skills[0]": ["name", "countN"],
    "market.families[0]": ["name", "buys", "why", "demandN", "demandNote", "pay", "entryBar",
                           "sourcing", "trend", "ages", "verdict", "verdictTone"],
    "market.positions[0]": ["employer", "title", "family", "status", "evidence", "when"],
    "horizon.shifts[0]": ["title", "alreadyVisible", "src", "falsifier"],
    "horizon.clocks.lanes[0]": ["name"],
    "horizon.clocks.lanes[0].steps[0]": ["at", "span", "label"],
    "horizon.calendar[0]": ["date", "what"],
}

# The values the page colours, by field. Any other value renders as a grey chip that looks deliberate.
TONES = ["good", "amb", "bad", "acc", "plain"]
CHOICES = {
    "habits[0].tone": ["good", "amb", "bad"],
    "thread.events[0].kind": ["turn", "build", "test"],
    "thread.events[0].verdict": ["confirms", "fails", "start"],
    "gaps[0].weight": ["decides", "slows", "closes doors"],
    "market.families[0].ages": ["well", "mixed", "badly"],
    "market.families[0].verdictTone": TONES,
    "market.families[0].sourcing": ["confirmed", "unconfirmed"],
    "market.positions[0].status": ["open", "closes", "recurs", "closed"],
    "market.positions[0].evidence": ["strong", "some", "thin"],
    "market.positions[0].when": ["now", "build", "later"],
    "horizon.clocks.lanes[0].steps[0].tone": TONES,
}

# What a first pass may ship, by the contract: evidence, gaps and families, and what could not be confirmed.
def first_pass():
    data = json.loads(BLOCK.search(PAGE).group(2))
    return {"meta": {"name": data["meta"]["name"]}, "evidence": data["evidence"], "gaps": data["gaps"],
            "market": {"families": data["market"]["families"]},
            "sources": {"notConfirmed": data["sources"]["notConfirmed"]}}


def family(**changed):
    """A family of the example's, with the fields given changed."""
    data = json.loads(BLOCK.search(PAGE).group(2))
    return {**data["market"]["families"][0], "buys": "A", "name": "A", **changed}


def position(employer, status, evidence, when, now, after):
    return {"employer": employer, "title": "Role", "status": status, "evidence": evidence,
            "when": when, "oddsNow": now, "oddsAfter": after}
