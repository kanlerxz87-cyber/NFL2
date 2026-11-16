#!/usr/bin/env python3
"""Session 4e475b8b — standalone flag-register verifier (CR-58E9-06 / CR-58E9-07).

Deliberately does NOT touch tools/verify.py (owned by the open PR #71, session 1ef36c55).
Checks, in order:
  1. data/flags.csv parses; every row has exactly 8 fields; ids are unique and well-formed FL-<n>.
  2. The id sequence is contiguous from FL-01 to FL-<max>; the next free id is max+1 (the
     deterministic allocator every session should consult on origin/main before appending).
  3. Every flag row's source cell contains at least one https:// link (the brief: every table
     row carries a source link).
  4. Every FL-<n> reference appearing anywhere in data/*.csv, content/*.md, tools/*.py and
     scripts/*.py resolves to a row in data/flags.csv; every FL-DCF-<n> reference resolves to
     dcf3b0cc/data/flags_dcf3b0cc.csv. (Sound, not complete: only FL-prefixed ids are scanned.)
  5. Status vocabulary census (informational) — the file's free-text statuses are counted and
     printed so a later register decision (FL-76) starts from the real list.

Exit code 1 on any failure; prints PASS lines otherwise.
"""
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FLAGS = ROOT / "data" / "flags.csv"
DCF_FLAGS = ROOT / "dcf3b0cc" / "data" / "flags_dcf3b0cc.csv"
COLUMNS = ["id", "type", "severity", "finding", "evidence", "source", "decision_impact", "status"]

fails = []
oks = []


def check(cond, msg):
    (oks if cond else fails).append(msg)


def main():
    check(FLAGS.exists(), "data/flags.csv exists")
    rows = []
    with FLAGS.open(encoding="utf-8", newline="") as f:
        reader = csv.reader(f, delimiter="|")
        header = next(reader)
        check(header == COLUMNS, f"header is {COLUMNS}")
        for i, r in enumerate(reader, start=2):
            if len(r) != 8:
                fails.append(f"line {i}: {len(r)} fields, expected 8")
                continue
            rows.append(r)

    ids = [r[0] for r in rows]
    check(len(ids) == len(set(ids)), f"flag ids unique ({len(ids)} rows)")
    check(all(re.fullmatch(r"FL-\d+", i) for i in ids), "every id matches FL-<n>")
    nums = [int(i.split("-")[1]) for i in ids]
    gaps = [n for n in range(1, max(nums) + 1) if n not in nums]
    check(not gaps, f"id sequence contiguous FL-01..FL-{max(nums)}" + (f" — GAPS: {gaps}" if gaps else ""))
    print(f"PASS: {len(rows)} flag rows, ids FL-01..FL-{max(nums)}, next free id = FL-{max(nums) + 1}")

    no_src = [r[0] for r in rows if "https://" not in r[5]]
    check(not no_src, "every flag row's source cell carries an https:// link" + (f" — MISSING: {no_src}" if no_src else ""))

    statuses = {}
    for r in rows:
        statuses[r[7]] = statuses.get(r[7], 0) + 1
    print("STATUS VOCABULARY CENSUS (informational, feeds FL-76):")
    for s, n in sorted(statuses.items(), key=lambda kv: -kv[1]):
        print(f"  {n:4} × {s}")

    # registers for reference resolution
    reg_main = set(ids)
    reg_dcf = set()
    if DCF_FLAGS.exists():
        with DCF_FLAGS.open(encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f, delimiter="|"):
                reg_dcf.add(r.get("flag_id", ""))
    print(f"reference registers: data/flags.csv ({len(reg_main)} ids), dcf3b0cc register ({len(reg_dcf)} ids)")

    # FL-<n> resolves against the canonical register; FL-<n>-<suffix> (e.g. session 2268bfb2's
    # FL-2268-01) is a session-namespace id owned by another register and is out of scope here.
    pat = re.compile(r"\bFL-(\d+)\b(?!-)")
    pat_dcf = re.compile(r"\bFL-DCF-(\d+)\b")
    scanned = refs = bad = 0
    scan_files = list((ROOT / "data").glob("*.csv")) + list((ROOT / "content").glob("*.md")) + \
        list((ROOT / "tools").glob("*.py")) + list((ROOT / "scripts").glob("*.py")) + \
        [ROOT / "4e475b8b" / "index.html"]
    for path in scan_files:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        scanned += 1
        for m in pat.finditer(text):
            refs += 1
            if f"FL-{m.group(1)}" not in reg_main:
                bad += 1
                fails.append(f"{path.relative_to(ROOT)}: reference FL-{m.group(1)} resolves to no flag row")
        for m in pat_dcf.finditer(text):
            refs += 1
            if f"FL-DCF-{m.group(1)}" not in reg_dcf:
                bad += 1
                fails.append(f"{path.relative_to(ROOT)}: reference FL-DCF-{m.group(1)} resolves to no dcf3b0cc flag row")
    check(True, f"reference scan: {scanned} files, {refs} FL-prefixed references checked, {bad} unresolved")

    for msg in oks:
        print("PASS:", msg)
    if fails:
        print("FAIL:")
        for msg in fails:
            print("  -", msg)
        sys.exit(1)
    print("VERIFY_FLAGS: ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
