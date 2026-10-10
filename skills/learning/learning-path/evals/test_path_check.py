#!/usr/bin/env python3
"""scripts/path_check.py, through its command line.

    path-plan.md     a plan with a path; it passes
    no-path-plan.md  a plan with no path; it passes
    path_cases.py    the cases: each breaks one of the plans and says what must happen
    this file        runs them, and the checks that need more than a broken plan

The two plans are invented to test the checker: the people, sources and links are made up, and
nothing in them is to be relied on. They are short plans that pass; a real plan writes the
attempt review out in full.

Run: python3 -I skills/learning/learning-path/evals/test_path_check.py
"""

import re
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
# python -I leaves the folder of the script off the path, and path_cases.py is beside it.
sys.path.insert(0, str(HERE))

from path_cases import NO_PATH_CASES, PATH_CASES, edited, hours, line  # noqa: E402

SKILL = HERE.parent
CHECKER = SKILL / "scripts" / "path_check.py"
PATH_PLAN = (HERE / "path-plan.md").read_text(encoding="utf-8")
NO_PATH_PLAN = (HERE / "no-path-plan.md").read_text(encoding="utf-8")
TODAY = "2026-09-25"
# The templates in plan.md are schematic: placeholders for words, and example numbers that do not
# add up. The checker has these problems with them, and no others. A name that plan.md changes and
# the checker does not follow adds a problem or swaps one for another. Each fragment is a pattern,
# so that an example number in plan.md can change without the test failing.
TEMPLATE_PROBLEMS = {
    "with a path": [
        "template text left in the plan",
        r"cites E\d+, which the Evidence table does not have",
        "every resource comes from the Evidence table",
        r"Time: '[^']*' cites no evidence",
        r"Effort: '[^']*' cites no evidence",
        r"the milestones add up to [\d.]+ h and the Effort line says [\d.]+ h",
        r"Verification kept \d+ claims and the Evidence table has \d+",
    ],
    "with no path": [
        "template text left in the plan",
        "the Evidence section has no table",
        *[f"the Goal section has no '- {name}:' line" for name in
          ("Performance", "Standard", "Conditions", "Deadline", "Hours a week", "Starting point",
           "Use")],
        "the Verification section has no line 'Checked N claims",
    ],
}


def run(*arguments):
    """The checker with these arguments: (exit code, stdout, stderr)."""
    done = subprocess.run([sys.executable, "-I", str(CHECKER), *arguments], capture_output=True,
                          text=True, timeout=60)
    return done.returncode, done.stdout, done.stderr


def check(plan, *options):
    """Run the checker on a plan given as text, or as bytes that are not text at all."""
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "learning-path-test.md"
        if isinstance(plan, bytes):
            path.write_bytes(plan)
        else:
            path.write_text(plan, encoding="utf-8")
        return run(str(path), "--today", TODAY, *options)


def examples_in_help(heading):
    """The indented lines under the one line of --help that ends with this heading."""
    lines = run("--help")[1].split("\n")
    starts = [i for i, text in enumerate(lines) if text.rstrip().endswith(heading)]
    assert len(starts) == 1, f"--help has {len(starts)} lines that end {heading!r}, not one"
    found = []
    for text in lines[starts[0] + 1:]:
        if not text.startswith("    "):
            break
        found.append(text.strip())
    return found


def templates():
    """The two plans references/plan.md shows: with a path, then with none."""
    text = (SKILL / "references" / "plan.md").read_text(encoding="utf-8")
    blocks = re.findall(r"```markdown\n(.*?)```", text, re.S)
    assert len(blocks) == 2, "plan.md no longer shows one plan with a path and one with none"
    return blocks


class PathCheck(unittest.TestCase):
    def run_cases(self, cases, plan):
        for each in cases:
            with self.subTest(each.name):
                code, out, err = check(edited(plan, each.edits), *each.options)
                self.assertNotIn("Traceback", out + err, "the checker crashed")
                self.assertEqual(code, each.code, f"{each.name}: exit {code}\n{err}{out}")
                for fragment in each.problems:
                    self.assertIn(fragment, err)
                for fragment in each.notes:
                    self.assertIn(fragment, out)
                for fragment in each.absent:
                    self.assertNotIn(fragment, err)

    def test_a_plan_with_a_path(self):
        self.run_cases(PATH_CASES, PATH_PLAN)

    def test_a_plan_with_no_path(self):
        self.run_cases(NO_PATH_CASES, NO_PATH_PLAN)

    def test_the_templates_in_plan_md_use_the_names_the_checker_looks_for(self):
        # plan.md says headings and field names are exact because the checker reads them.
        for (name, expected), template in zip(TEMPLATE_PROBLEMS.items(), templates()):
            with self.subTest(name):
                code, out, err = check(template)
                self.assertEqual(code, 1, "a template is not a finished plan")
                self.assertRegex(err, rf"(?<!\d){len(expected)} problem\(s\) to fix")
                for fragment in expected:
                    self.assertRegex(err, fragment)

    def test_a_file_that_cannot_be_read_exits_2(self):
        with tempfile.TemporaryDirectory() as folder:
            for name, arguments, fragment in [
                    ("a file that is not there", [str(Path(folder) / "none.md")], "cannot read"),
                    ("a folder", [folder], "cannot read"),
                    ("no file named", [], "usage"),
                    ("a day that is not one", [str(HERE / "path-plan.md"), "--today", "2026-13-45"],
                     "is not YYYY-MM-DD")]:
                with self.subTest(name):
                    code, out, err = run(*arguments)
                    self.assertEqual(code, 2, err)
                    self.assertIn(fragment, err.lower() if fragment == "usage" else err)
        with self.subTest("a file that is not UTF-8"):
            code, out, err = check("# Learning path: caf\xe9\n".encode("latin-1"))
            self.assertEqual(code, 2)
            self.assertIn("not UTF-8", err)

    def test_a_file_the_checker_cannot_make_sense_of_is_a_problem_not_a_crash(self):
        for name, plan in [("an empty file", ""), ("only blank lines", "\n" * 50),
                           ("control characters", b"\x00\x01\x02" * 100),
                           ("one pipe after another", "|" * 100000)]:
            with self.subTest(name):
                code, out, err = check(plan)
                self.assertNotIn("Traceback", out + err)
                self.assertEqual(code, 1)

    def test_a_long_list_under_a_field_is_read_without_stalling(self):
        # Joining a field's lines one at a time copies the text each time, so the time grew faster
        # than the number of lines. The list is long enough for that growth to show, and the limit
        # far above the time the checker takes now, so that a busy machine still passes. Both lists
        # are indented, which the checker from before read as the field's text; a list flush left
        # it did not read.
        for name, item in [("indented", "  step {}"), ("indented and numbered", "  {}. step")]:
            with self.subTest(name):
                steps = "\n".join(item.format(i) for i in range(1, 400001))
                plan = edited(PATH_PLAN, [line("- Reviews:", "- Reviews:\n" + steps)])
                started = time.monotonic()
                code, out, err = check(plan)
                self.assertEqual(code, 0, err)
                self.assertLess(time.monotonic() - started, 20)

    def test_a_byte_order_mark_and_windows_line_endings_do_not_matter(self):
        for name, plan in [("with a path", PATH_PLAN), ("with no path", NO_PATH_PLAN)]:
            with self.subTest(name):
                code, out, err = check(b"\xef\xbb\xbf" + plan.replace("\n", "\r\n").encode("utf-8"))
                self.assertEqual(code, 0, err)

    def test_help_lists_the_template_check_and_what_the_script_cannot_check(self):
        code, out, err = run("--help")
        self.assertEqual(code, 0)
        self.assertIn("template text left", out)
        self.assertIn("What it cannot check", out)

    def test_the_examples_in_help_do_what_help_says(self):
        for heading, code in (("these pass:", 0), ("these are refused:", 1)):
            examples = examples_in_help(heading)
            self.assertGreaterEqual(len(examples), 2, f"--help lists too few examples: {heading}")
            for example in examples:
                with self.subTest(example):
                    got, out, err = check(edited(PATH_PLAN, [hours(example)]))
                    self.assertEqual(got, code, err)
                    if code:
                        self.assertIn("Give hours a week", err)


if __name__ == "__main__":
    unittest.main()
