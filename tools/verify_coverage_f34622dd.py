#!/usr/bin/env python3
"""Fail-closed verification for session f34622dd's artefacts.

This session added three datasets and one page:

  data/brief_traceability.csv          one row per clause of the owner brief
  data/hub_club_counts_f34622dd.csv    per-club delta of today's official injury read
  data/injuries_wk10_f34622dd_20261115.csv  the dated row-level read itself
  data/page_freshness_f34622dd.csv     the age of the evidence behind each page

The checks below exist because each artefact can fail in a way that is invisible to a reader:

  1. A coverage row can be added with a class outside the five defined values, or with no
     verifiable source. Both would make the summary table lie.
  2. The per-club delta table can stop reconciling to the published totals, which is exactly
     how a transcription of a web page silently loses rows.
  3. The transposed read can disagree with the live page's own stated totals.
  4. The freshness panel can silently start comparing a page against a different page.
  5. The page can stop rendering, or render a template marker.

Run from the repository root:  python3 tools/verify_coverage_f34622dd.py
Exit code 0 = all checks pass. Any failure prints and exits 1.
"""
import csv
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

CLASSES = {"covered", "partial", "blocked", "uncovered", "resolved"}
VERDICTS_PREFIX = ("current", "BEHIND")
# The live page read on 2026-11-15T12:56Z publishes these fixture-level totals. They are stated
# here so that the stored transcription is checked against the page's own shape and not only
# against itself.
EXPECTED_ROWS = 347
EXPECTED_CLUBS = 28
EXPECTED_FIXTURES = 14
WEEK10_CLUBS = 28  # 14 fixtures x 2 clubs

failures = []
checks = [0]


def ok(cond, msg):
    checks[0] += 1
    if not cond:
        failures.append(msg)


def rows(name):
    path = os.path.join(DATA, name)
    if not os.path.exists(path):
        failures.append("missing data file: %s" % name)
        return []
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="|"))


def main():
    sources = {r["id"]: r for r in rows("sources.csv")}
    official = {r["id"] for r in sources.values() if r["tier"] in ("A", "B")}

    # ---------------------------------------------------------------- coverage matrix
    cov = rows("brief_traceability.csv")
    ok(len(cov) >= 80, "brief_traceability.csv has only %d rows" % len(cov))
    ids = [r["id"] for r in cov]
    ok(len(ids) == len(set(ids)), "brief_traceability.csv has duplicate ids")
    clauses = [r["clause"].strip() for r in cov]
    dupes = {c for c in clauses if clauses.count(c) > 1}
    ok(not dupes, "duplicate clause text: %s" % sorted(dupes)[:3])
    for r in cov:
        ok(r["coverage_class"].strip() in CLASSES,
           "%s: coverage_class %r is outside the defined vocabulary %s"
           % (r["id"], r["coverage_class"], sorted(CLASSES)))
        src = r["source"].strip()
        ok(src.startswith("https://"), "%s: source is not an https URL: %r" % (r["id"], src))
        # A host with no dot is the signature of a URL that lost its domain in an edit: it looks
        # like a link, resolves nowhere, and sails past a check that only asks for "https://".
        host = src.split("//", 1)[1].split("/", 1)[0]
        ok("." in host, "%s: source host %r has no dot - the URL has lost its domain" % (r["id"], host))
        ok(host not in ("", "github.com") or "/kanlerxz87-cyber/NFL2" in src,
           "%s: github source does not point at this repository: %r" % (r["id"], src))
        if host.endswith("github.io"):
            ok("/NFL2" in src, "%s: github.io source is not this project's Pages site" % r["id"])
        ok(bool(r["evidence"].strip()), "%s: empty evidence cell" % r["id"])
        ok(bool(r["verification"].strip()), "%s: empty verification cell" % r["id"])
        ok("FL-..." not in r["evidence"], "%s: placeholder text left in evidence" % r["id"])
    # Every category must be represented and the five classes must all occur, otherwise the
    # headline summary on the page would silently describe a different matrix.
    cats = {r["category"] for r in cov}
    ok(len(cats) == 5, "expected 5 coverage categories, found %d" % len(cats))
    for cls in CLASSES:
        ok(any(r["coverage_class"].strip() == cls for r in cov),
           "no row has coverage_class %r; the summary would print a zero that is not real" % cls)

    # ------------------------------------------------------- the dated injury read
    new = rows("injuries_wk10_f34622dd_20261115.csv")
    ok(len(new) == EXPECTED_ROWS,
       "transcribed read has %d rows, expected %d (the live page's own count)"
       % (len(new), EXPECTED_ROWS))
    clubs = {r["team"] for r in new}
    ok(len(clubs) == EXPECTED_CLUBS,
       "transcribed read covers %d clubs, expected %d" % (len(clubs), EXPECTED_CLUBS))
    games = {r["game"] for r in new}
    ok(len(games) == EXPECTED_FIXTURES,
       "transcribed read covers %d fixtures, expected %d" % (len(games), EXPECTED_FIXTURES))
    ok(len(clubs) == WEEK10_CLUBS,
       "every club playing Week 10 must appear; %d of %d do" % (len(clubs), WEEK10_CLUBS))
    allowed_practice = {"F", "L", "D", ""}
    allowed_status = {"Out", "Questionable", "Doubtful", ""}
    for r in new:
        ok(r["practice"] in allowed_practice,
           "%s/%s: practice code %r is not one of F/L/D" % (r["team"], r["player"], r["practice"]))
        ok(r["status"] in allowed_status,
           "%s/%s: game status %r is not one of Out/Questionable/Doubtful"
           % (r["team"], r["player"], r["status"]))
        ok(r["source"].startswith("https://www.nfl.com/injuries/"),
           "%s/%s: row does not cite the official hub" % (r["team"], r["player"]))
        ok(bool(r["fetched_utc"].strip()),
           "%s/%s: row has no fetch time" % (r["team"], r["player"]))
    ok(len({r["fetched_utc"] for r in new}) == 1,
       "the read carries more than one fetch time; a single read must be stamped once")

    # -------------------------------------------------------- the per-club delta table
    delta = rows("hub_club_counts_f34622dd.csv")
    detail = [r for r in delta if r["club"] != "ALL 28 reporting clubs"]
    total = [r for r in delta if r["club"] == "ALL 28 reporting clubs"]
    ok(len(total) == 1, "the delta table must carry exactly one total row")
    ok(len(detail) == EXPECTED_CLUBS,
       "delta table has %d club rows, expected %d" % (len(detail), EXPECTED_CLUBS))
    s13 = sum(int(r["rows_13nov"]) for r in detail)
    s15 = sum(int(r["rows_15nov"]) for r in detail)
    ok(s15 == len(new), "delta table sums to %d rows on 15 Nov but the read holds %d" % (s15, len(new)))
    ok(int(total[0]["rows_15nov"]) == s15, "total row does not equal the sum of the club rows (15 Nov)")
    ok(int(total[0]["rows_13nov"]) == s13, "total row does not equal the sum of the club rows (13 Nov)")
    ok(int(total[0]["rows_added"]) == s15 - s13, "total 'added' does not equal the row difference")
    for r in detail:
        added = int(r["rows_added"])
        ok(added == int(r["rows_15nov"]) - int(r["rows_13nov"]),
           "%s: rows_added %d does not equal 15Nov minus 13Nov" % (r["club"], added))
        ok(added >= 0,
           "%s: rows_added is negative (%d). A later read of the same page cannot lose rows; "
           "this indicates a transcription that dropped part of the page" % (r["club"], added))
        ok(int(r["rows_removed"]) == 0,
           "%s: rows_removed is %s, expected 0" % (r["club"], r["rows_removed"]))
        ok(int(r["rows_15nov"]) == sum(1 for x in new if x["team"] == r["club"]),
           "%s: delta row count disagrees with the read file itself" % r["club"])
        ok(int(r["designations_15nov"]) ==
           sum(1 for x in new if x["team"] == r["club"] and x["status"].strip()),
           "%s: designation count disagrees with the read file itself" % r["club"])
        ok(int(r["dnp_15nov"]) ==
           sum(1 for x in new if x["team"] == r["club"] and x["practice"] == "D"),
           "%s: DNP count disagrees with the read file itself" % r["club"])
    # The two Monday-night clubs must be present with their "No Injuries Reported" declaration
    # recorded as rows, not silently omitted. If they vanish the delta table would be lying.
    for club in ("BAL", "LAC"):
        ok(club in {r["club"] for r in detail},
           "%s has been dropped from the delta table; the live page lists it" % club)

    # ------------------------------------------------------------- the freshness panel
    fresh = rows("page_freshness_f34622dd.csv")
    ok(len(fresh) >= 15, "freshness panel has only %d rows" % len(fresh))
    seen = set()
    for r in fresh:
        ok(r["page"] not in seen or r["page"] == "brief-coverage",
           "%s appears twice in the freshness panel" % r["page"])
        seen.add(r["page"])
        ok(r["verdict"].startswith(VERDICTS_PREFIX),
           "%s: verdict %r does not start with a defined state" % (r["page"], r["verdict"]))
        ok(r["own_read_source"] in sources,
           "%s: own_read_source %r is not a registered source" % (r["page"], r["own_read_source"]))
        ok(r["newest_read_source"] in sources,
           "%s: newest_read_source %r is not a registered source"
           % (r["page"], r["newest_read_source"]))
        ok(r["own_read_utc"] <= r["newest_read_utc"],
           "%s: own read (%s) is later than the 'newest read held' (%s), so the comparison is "
           "inverted" % (r["page"], r["own_read_utc"], r["newest_read_utc"]))
        if r["rows_withheld"].strip():
            ok(int(r["rows_withheld"]) >= 0,
               "%s: rows_withheld is negative" % r["page"])

    # ------------------------------------------------------------------ the built page
    page = os.path.join(ROOT, "brief-coverage.html")
    ok(os.path.exists(page), "brief-coverage.html was not generated")
    if os.path.exists(page):
        html = open(page, encoding="utf-8").read()
        ok("{{" not in html and "}}" not in html,
           "brief-coverage.html still contains an unexpanded template marker")
        ok(html.count("<table") >= 4, "brief-coverage.html carries fewer than four tables")
        for needle in ("Coverage class", "Rows withheld", "The full matrix"):
            ok(needle in html, "brief-coverage.html is missing the %r section" % needle)
        # every tbody row must carry an official/canonical link, same rule as the site auditor
        for m in re.finditer(r"<tr>(?:(?!</tr>).)*?</tr>", html, re.S):
            chunk = m.group(0)
            if "<td" not in chunk:
                continue
            ok("https://" in chunk, "a table row on brief-coverage.html carries no source link")

    print("verify_coverage_f34622dd: %d checks, %d failures" % (checks[0], len(failures)))
    for f in failures[:40]:
        print("  FAIL ", f)
    if len(failures) > 40:
        print("  ... and %d more" % (len(failures) - 40))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
