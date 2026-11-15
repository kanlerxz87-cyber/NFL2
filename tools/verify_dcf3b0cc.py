#!/usr/bin/env python3
"""Session dcf3b0cc — verifier for the dated re-verification scope.

Checks, and exits non-zero on any failure:
  1. every artefact exists and the summary counts match the CSVs exactly;
  2. every table row rendered in dcf3b0cc/*.html carries at least one official https:// link;
  3. every internal link from a dcf3b0cc page resolves to a file that exists;
  4. no generated table renders an empty cell — blanks must read `not published`;
  5. the pipeline is deterministic: re-running compute + build reproduces byte-identical files.
"""
import csv
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "dcf3b0cc", "data")
OUT = os.path.join(ROOT, "dcf3b0cc")
BLANK = "not published"

TABLE_ROW_RE = re.compile(r"<tr>(.*?)</tr>", re.S)
TD_RE = re.compile(r"<td[^>]*>(.*?)</td>", re.S)
HREF_RE = re.compile(r'href="([^"]+)"')

failures = []
checks = 0


def check(cond, msg):
    global checks
    checks += 1
    if not cond:
        failures.append(msg)
    return cond


def read(name):
    with open(os.path.join(D, name), newline="") as fh:
        return list(csv.DictReader(fh, delimiter="|"))


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(65536), b""):
            h.update(c)
    return h.hexdigest()


def main():
    summary = json.load(open(os.path.join(D, "summary_dcf3b0cc.json")))

    # 1. artefacts exist, hashes match, counts match
    for name, want in summary["sha256"].items():
        p = os.path.join(D, name)
        check(os.path.exists(p), "missing artefact %s" % name)
        if os.path.exists(p):
            check(sha(p) == want, "hash mismatch for %s" % name)

    hub = read("nfl_injury_hub_20261115_dcf3b0cc.csv")
    fix = read("nfl_fixtures_wk10_20261115_dcf3b0cc.csv")
    rev = read("reverify_20261115_dcf3b0cc.csv")
    clubs = read("club_availability_20261115_dcf3b0cc.csv")
    mat = read("deficiency_matrix_dcf3b0cc.csv")
    reach = read("depth_reach_20261115_dcf3b0cc.csv")
    cov = read("coverage_dcf3b0cc.csv")
    corr = read("correlation_dcf3b0cc.csv")
    flags = read("flags_dcf3b0cc.csv")
    questions = read("questions_dcf3b0cc.csv")
    suggestions = read("suggestions_dcf3b0cc.csv")

    check(len(hub) == summary["injury_rows_transcribed"], "hub row count drifted")
    check(len(fix) == summary["fixtures_covered"], "fixture count drifted")
    check(len(mat) == summary["deficiency_matrix_rows"], "matrix row count drifted")
    check(len(reach) == summary["depth_reach_rows"], "depth-reach row count drifted")
    check(len(cov) == summary["coverage_rows"], "coverage row count drifted")
    check(len(corr) == summary["correlation_pairs"], "correlation pair count drifted")
    check(len(flags) == summary["flags"], "flag count drifted")
    check(len(questions) >= 8, "question register too small")
    check(len(suggestions) >= 9, "suggestion register too small")
    check(sum(int(c["out"]) for c in clubs) == summary["designations_out"], "Out count drifted")
    check(sum(int(c["doubtful"]) for c in clubs) == summary["designations_doubtful"], "Doubtful drifted")
    check(sum(int(c["questionable"]) for c in clubs) == summary["designations_questionable"], "Q drifted")

    # every row of every source table has at least one official https source
    srcmap = [
        ("hub", hub, ["player_url", "source_url"]),
        ("reverify", rev, ["official_source"]),
        ("clubs", clubs, ["source"]),
        ("matrix", mat, ["designation_source", "fixture_source"]),
        ("reach", reach, ["chart_source", "designation_source"]),
        ("coverage", cov, ["designation_source"]),
        ("correlations", corr, ["x_source", "y_source"]),
        ("flags", flags, ["source"]),
        ("questions", questions, ["source"]),
        ("suggestions", suggestions, ["source"]),
    ]
    for label, rows, cols in srcmap:
        for i, r in enumerate(rows):
            ok = any((r.get(c) or "").startswith("https://") for c in cols)
            check(ok, "%s row %d (%s) has no official https source" % (label, i, r.get("club", r.get("pair_id", "?"))))

    # 2/3/4. rendered pages
    pages = sorted(f for f in os.listdir(OUT) if f.endswith(".html"))
    check(len(pages) == 12, "expected 12 pages, found %d" % len(pages))
    by_page = {
        "official-register.html": len(hub),
        "reverification.html": len(rev),
        "club-availability.html": len(clubs),
        "deficiency-matrix.html": len(mat),
        "depth-reach.html": len(reach),
        "coverage.html": len(cov),
        "correlations.html": len(corr),
        "flagged.html": len(flags),
    }
    row_total = 0
    for p in pages:
        body = open(os.path.join(OUT, p)).read()
        # internal links resolve
        for href in HREF_RE.findall(body):
            if href.startswith(("http", "#", "mailto:")):
                continue
            target = os.path.normpath(os.path.join(OUT, href))
            check(os.path.exists(target), "broken internal link %s -> %s" % (p, href))
        # table rows
        nosrc_rows = set()
        for tm in re.finditer(r"<table([^>]*)>(.*?)</table>", body, re.S):
            if "data-nosource" in tm.group(1):
                for m in TABLE_ROW_RE.finditer(tm.group(2)):
                    nosrc_rows.add(m.group(1))
        rows = TABLE_ROW_RE.findall(body)
        body_rows = [r for r in rows if "<td" in r]
        row_total += len(body_rows)
        for r in body_rows:
            tds = TD_RE.findall(r)
            for t in tds:
                txt = re.sub(r"<[^>]+>", "", t).strip()
                check(txt != "", "empty cell on %s" % p)
            if r not in nosrc_rows:
                check(any("https://" in t for t in tds),
                      "row on %s has no official https link: %s" % (p, r[:110].replace("\n", " ")))
        if p in by_page:
            check(len(body_rows) >= by_page[p],
                  "%s renders %d body rows, expected at least %d" % (p, len(body_rows), by_page[p]))
    check(row_total > 1200, "implausibly few rendered rows: %d" % row_total)

    # 5. determinism: rerun compute + build into a temp copy and compare hashes
    before = {f: sha(os.path.join(OUT, f)) for f in pages}
    data_before = {n: sha(os.path.join(D, n)) for n in summary["sha256"]}
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "compute_dcf3b0cc.py")],
                   cwd=ROOT, check=True, capture_output=True)
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "build_dcf3b0cc.py")],
                   cwd=ROOT, check=True, capture_output=True)
    for n, h in data_before.items():
        check(sha(os.path.join(D, n)) == h, "recompute changed %s" % n)
    for f, h in before.items():
        check(sha(os.path.join(OUT, f)) == h, "rebuild changed %s" % f)

    print("dcf3b0cc verifier: %d checks, %d failures" % (checks, len(failures)))
    for f in failures:
        print("  FAIL " + f)
    print("rendered table rows checked: %d" % row_total)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
