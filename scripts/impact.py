#!/usr/bin/env python3
"""Summarise upstream's upgrade-impact notes for a range of releases.

Usage: impact.py <releases dir> <previous tag or ""> <target tag>

Prints JSON: the highest impact level of any release after <previous> up to
and including <target>, and one note per release that is not "none". With no
previous tag only the target release itself is looked at.

Upstream does not publish a note for every tag, and the one for a new release
can lag its tag by a day. A missing note for the target is therefore reported
(`target_note: false`) rather than treated as a finding.
"""

import json
import pathlib
import re
import sys

RANK = {"none": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}


def key(tag):
    return tuple(int(part) for part in re.findall(r"\d+", tag))


def field(text, name):
    match = re.search(rf"^{name}:\s*(.*)$", text, re.MULTILINE)
    return match.group(1).strip().strip("\"'") if match else ""


def main():
    directory, previous, target = pathlib.Path(sys.argv[1]), sys.argv[2], sys.argv[3]
    notes = []
    seen_target = False
    for path in sorted(directory.glob("v*.yaml"), key=lambda p: key(p.stem)):
        tag = path.stem
        if key(tag) > key(target):
            continue
        if previous and key(tag) <= key(previous):
            continue
        if not previous and tag != target:
            continue
        seen_target = seen_target or tag == target
        text = path.read_text()
        level = field(text, "impactLevel").lower()
        if level not in RANK:
            # a level this script does not know must not pass as harmless
            level = "high"
        if level != "none":
            notes.append({"version": tag, "level": level, "summary": field(text, "summary")})
    level = max((note["level"] for note in notes), key=RANK.get, default="none")
    print(json.dumps({"level": level, "target_note": seen_target, "notes": notes}, indent=2))


if __name__ == "__main__":
    main()
