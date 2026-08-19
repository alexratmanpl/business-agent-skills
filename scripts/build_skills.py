#!/usr/bin/env python3
"""Validate and package the skills in this repository.

Finds every directory under skills/ that contains a SKILL.md, checks it, and
writes an installable <name>.skill archive for each. Any problem is a failure:
a skill that ships broken is worse than a build that stops.

Checks:
  - frontmatter parses, and has a name and a description
  - the name matches the directory it lives in, since that is what installs
  - every bundled file the body points at actually exists

The last check exists because the two real defects found in this repository were
both pointers to files that were never committed. A skill that references a
missing file does not fail loudly at runtime; the instruction is simply read and
nothing is found.

Usage: build_skills.py [--out dist] [--check-only]
"""

import argparse
import os
import re
import sys
import zipfile

SKILLS_DIR = "skills"
EXCLUDE_NAMES = {"__pycache__", ".DS_Store", "evals"}
EXCLUDE_SUFFIXES = (".pyc",)

# Only paths containing a slash are treated as bundled files. A bare filename in
# the prose is usually something the skill writes at runtime, not something it
# ships, and flagging those produces noise instead of findings.
PATH_PATTERN = re.compile(r"`([^`\n]*?/[^`\n]*?\.(?:md|py|sh|json|ya?ml|txt|csv))`")
LINK_PATTERN = re.compile(r"\[[^\]]*\]\(([^)\s]+/[^)\s]+)\)")


def find_skills(root):
    for dirpath, dirnames, filenames in os.walk(os.path.join(root, SKILLS_DIR)):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_NAMES]
        if "SKILL.md" in filenames:
            yield dirpath


def parse_frontmatter(text):
    if not text.startswith("---\n"):
        return None, "no frontmatter block"
    end = text.find("\n---", 4)
    if end == -1:
        return None, "frontmatter block is not closed"
    fields, key = {}, None
    for line in text[4:end].split("\n"):
        match = re.match(r"^([a-zA-Z_-]+):\s*(.*)$", line)
        if match:
            key = match.group(1)
            fields[key] = match.group(2).strip()
        elif key and line.startswith((" ", "\t")):
            fields[key] += " " + line.strip()
    return fields, None


def referenced_paths(body):
    found = set(PATH_PATTERN.findall(body)) | set(LINK_PATTERN.findall(body))
    cleaned = set()
    for path in found:
        path = re.sub(r"^\$\{[A-Z_]+\}/", "", path)  # ${CLAUDE_SKILL_DIR}/...
        if path.startswith(("http://", "https://", "/")):
            continue
        cleaned.add(path)
    return sorted(cleaned)


def check(skill_dir):
    problems = []
    name = os.path.basename(skill_dir)
    text = open(os.path.join(skill_dir, "SKILL.md"), encoding="utf-8").read()

    fields, error = parse_frontmatter(text)
    if error:
        return [f"{name}: {error}"]

    for required in ("name", "description"):
        if not fields.get(required):
            problems.append(f"{name}: frontmatter is missing {required}")

    if fields.get("name") and fields["name"] != name:
        problems.append(
            f"{name}: frontmatter name is '{fields['name']}' but the directory is "
            f"'{name}'. The directory name is what gets installed, so these must match")

    for path in referenced_paths(text):
        if not os.path.exists(os.path.join(skill_dir, path)):
            problems.append(f"{name}: points at '{path}', which is not in the skill")

    return problems


def package(skill_dir, out_dir):
    name = os.path.basename(skill_dir)
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, f"{name}.skill")
    count = 0
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for dirpath, dirnames, filenames in os.walk(skill_dir):
            dirnames[:] = [d for d in dirnames if d not in EXCLUDE_NAMES]
            for filename in sorted(filenames):
                if filename in EXCLUDE_NAMES or filename.endswith(EXCLUDE_SUFFIXES):
                    continue
                full = os.path.join(dirpath, filename)
                relative = os.path.relpath(full, skill_dir)
                archive.write(full, os.path.join(name, relative))
                count += 1
    return target, count


def main():
    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", default="dist", help="output directory (default dist)")
    parser.add_argument("--root", default=".", help="repository root (default .)")
    parser.add_argument("--check-only", action="store_true",
                        help="validate without writing archives")
    args = parser.parse_args()

    skill_dirs = sorted(find_skills(args.root))
    if not skill_dirs:
        print(f"no skills found under {SKILLS_DIR}/", file=sys.stderr)
        return 1

    problems = []
    for skill_dir in skill_dirs:
        problems.extend(check(skill_dir))

    if problems:
        print(f"{len(problems)} problem(s):\n", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        return 1

    for skill_dir in skill_dirs:
        name = os.path.basename(skill_dir)
        if args.check_only:
            print(f"ok  {name}")
            continue
        target, count = package(skill_dir, args.out)
        print(f"ok  {name} -> {target} ({count} file{'s' if count != 1 else ''})")

    print(f"\n{len(skill_dirs)} skill(s) checked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
