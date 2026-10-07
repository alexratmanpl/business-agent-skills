#!/usr/bin/env python3
"""Cases for the report: the checker, through its command line, and the page, through a browser.

Each case takes the example report, breaks it the way a real mistake would, and says what must
happen. A case that expects exit 0, or a section still drawn, is as important as one that expects
the opposite: a gate that blocks a legitimate report sends people looking for a way round it.

    harness.py        what the cases share
    checker_cases.py  the table of cases for the checker
    test_checker.py   the checker
    test_page.py      the page; needs Playwright and a Chromium, and is skipped without them

Run: python3 -I skills/careers/career-direction/evals/test_report.py
"""

import sys
import unittest
from pathlib import Path

# python -I leaves the folder of the script off the path, and the modules are beside it.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_checker import ReportCheck
from test_page import ReportPage

if __name__ == "__main__":
    unittest.main()
