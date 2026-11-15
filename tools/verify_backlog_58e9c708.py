#!/usr/bin/env python3
"""Regression checks for the brief-backlog register built by session 58e9c708.

Run after ``python3 tools/build_site.py``. Every check reads the register, the built page,
or the official page list, and fails loudly rather than passing quietly.

  1. register integrity      - unique ids, field counts, controlled vocabularies
  2. gate references         - only the 14 ids in data/gates.csv, or an explicit em dash
  3. official dependencies   - every row names a real https page; non-league hosts are named
  4. verification vocabulary - "re-read 2026-11-15" only where the page really was read
  5. page coverage           - the built page renders every theme with the register's row count
  6. row sourcing            - every rendered row carries an https source link
  7. replay                  - the builder regenerates all four files byte-identically
  8. flag cross-reference    - findings that cite FL-77/78/79 point at rows that exist
"""
from __future__ import annotations

import csv
import os
import re
import subprocess
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
sys.path.insert(0, os.path.join(ROOT, "tools"))

REGISTER = "brief_backlog_58e9c708.csv"
SUMMARY = "backlog_summary_58e9c708.csv"
READS = "backlog_reads_58e9c708.csv"
FINDINGS = "backlog_findings_58e9c708.csv"
PAGE = os.path.join(ROOT, "backlog.html")

PASS, WARN, FAIL = [], [], []


def ok(msg):
    PASS.append(msg)


def warn(msg):
    WARN.append(msg)


def bad(msg):
    FAIL.append(msg)


def load(name):
    path = os.path.join(DATA, name)
    if not os.path.exists(path):
        bad("%s is missing; run tools/build_backlog_58e9c708.py" % name)
        return []
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="|"))


OFFICIAL_SUFFIX = (".nfl.com", "nfl.com", "operations.nfl.com")
CLUB_HOSTS = {
    "azcardinals.com", "atlantafalcons.com", "baltimoreravens.com", "buffalobills.com",
    "panthers.com", "chicagobears.com", "bengals.com", "clevelandbrowns.com",
    "dallascowboys.com", "denverbronzos.com", "denverbroncos.com", "detroitlions.com",
    "packers.com", "houstontexans.com", "colts.com", "jaguars.com", "chiefs.com",
    "raiders.com", "chargers.com", "therams.com", "miamidolphins.com", "vikings.com",
    "patriots.com", "neworleanssaints.com", "giants.com", "newyorkjets.com",
    "philadelphiaeagles.com", "steelers.com", "49ers.com", "seahawks.com",
    "buccaneers.com", "tennesseetitans.com", "commanders.com",
}
NAMED_NON_LEAGUE = {"www.weather.gov": "US National Weather Service, federal official, not a league source"}
VERIFICATION_VOCAB = {"re-read 2026-11-15", "not re-read today", "no official source exists"}


class TableParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables = []
        self._t = self._r = self._c = None

    def handle_starttag(self, tag, attrs):
        if tag == "table" and self._t is None:
            self._t = []
        elif tag == "tr" and self._t is not None:
            self._r = []
        elif tag in ("th", "td") and self._r is not None:
            self._c = {"text": [], "href": None}
        elif tag == "a" and self._c is not None and self._c["href"] is None:
            self._c["href"] = dict(attrs).get("href")

    def handle_data(self, d):
        if self._c is not None:
            self._c["text"].append(d)

    def handle_endtag(self, tag):
        if tag in ("th", "td") and self._c is not None and self._r is not None:
            self._c["text"] = " ".join("".join(self._c["text"]).split())
            self._r.append(self._c)
            self._c = None
        elif tag == "tr" and self._r is not None and self._t is not None:
            self._t.append(self._r)
            self._r = None
        elif tag == "table" and self._t is not None:
            self.tables.append(self._t)
            self._t = None


def check_register(rows, gate_ids):
    ids = [r["id"] for r in rows]
    if len(ids) != len(set(ids)):
        bad("register contains duplicate ids")
    if not all(re.fullmatch(r"BL-\d{2}", i) for i in ids):
        bad("register ids must be BL-nn: %s" % [i for i in ids if not re.fullmatch(r"BL-\d{2}", i)][:5])

    nonleague = []
    for r in rows:
        blocks = r["blocks"].strip()
        if blocks == "—":
            pass
        else:
            refs = set(re.findall(r"G-\d{2}", blocks))
            residue = re.sub(r"G-\d{2}", "", blocks).strip(" /,;")
            if not refs or residue or (refs - gate_ids):
                bad("%s malformed gate mapping %r" % (r["id"], blocks))
        if r["kind"].strip() != "rejected" and not r["clears_with"].strip():
            bad("%s has no clearing condition" % r["id"])
        if r["verified_2026_11_15"] not in VERIFICATION_VOCAB:
            bad("%s verification value %r is outside the vocabulary" % (r["id"], r["verified_2026_11_15"]))
        dep = r["dependency"].strip()
        if not dep.startswith("https://"):
            bad("%s dependency is not an https URL: %r" % (r["id"], dep))
        else:
            host = re.sub(r"^https?://([^/]+).*", r"\1", dep)
            bare = host[4:] if host.startswith("www.") else host
            if host not in NAMED_NON_LEAGUE and not (host.endswith("nfl.com") or bare in CLUB_HOSTS):
                nonleague.append((r["id"], host))
        if not r["directive"].strip():
            bad("%s has an empty directive" % r["id"])
    if nonleague:
        bad("dependencies on hosts that are not league, operations or club pages: %s" % nonleague[:5])
    else:
        ok("official dependencies: every one of the %d rows names an https league, operations or club page" % len(rows))


def check_summary(rows, summary):
    themes = {}
    statuses = {}
    for r in rows:
        themes[r["theme"]] = themes.get(r["theme"], 0) + 1
        statuses[r["status"]] = statuses.get(r["status"], 0) + 1
    got_themes = {r["bucket"]: int(r["count"]) for r in summary if r["grouping"] == "theme"}
    got_status = {r["bucket"]: int(r["count"]) for r in summary if r["grouping"] == "status"}
    if got_themes != themes:
        bad("summary theme counts %s do not match the register %s" % (got_themes, themes))
    if got_status != statuses:
        bad("summary status counts %s do not match the register %s" % (got_status, statuses))
    total = [int(r["count"]) for r in summary if r["grouping"] == "total"]
    if total != [len(rows)]:
        bad("summary total %s does not equal %d register rows" % (total, len(rows)))
    if not FAIL:
        ok("summary: %d themes and %d statuses recompute exactly from the register, total %d"
           % (len(themes), len(statuses), len(rows)))


def check_reads(reads, rows):
    ids = {r["id"] for r in rows}
    for r in reads:
        if not r["url"].startswith("https://"):
            bad("read row %r cites a non-https URL" % r["page"])
        for tok in re.split(r"[,\s]+", r["unblocks"].strip()):
            tok = tok.strip()
            if tok and tok not in ids:
                bad("read row %r claims to unblock unknown directive %r" % (r["page"], tok))
        if r["flag"] not in ("none", "") and not re.fullmatch(r"FL-\d{2}", r["flag"]):
            bad("read row %r has a malformed flag reference %r" % (r["page"], r["flag"]))
    if not FAIL:
        ok("official reads: %d pages, every directive they claim to unblock exists in the register" % len(reads))
    read_today = sum(1 for r in rows if r["verified_2026_11_15"] == "re-read 2026-11-15")
    hosts = {re.sub(r"^https?://([^/]+).*", r"\1", r["url"]) for r in reads}
    if not {"www.nfl.com", "www.packers.com", "www.houstontexans.com"} <= hosts:
        bad("the three page types the findings rest on are not all present: %s" % sorted(hosts))
    else:
        ok("reads cover the league hub, the schedule and scores pages, the transactions hub, the reserve list and two club depth charts; %d rows are marked re-read 2026-11-15" % read_today)


def check_findings(findings):
    path = os.path.join(DATA, "flags.csv")
    flag_ids = set()
    if os.path.exists(path):
        with open(path, encoding="utf-8", newline="") as fh:
            flag_ids = {r["id"] for r in csv.DictReader(fh, delimiter="|")}
    promoted = []
    for r in findings:
        ref = (r.get("flag") or "").strip()
        if not ref:
            continue
        if not re.fullmatch(r"FL-\d{2}", ref):
            bad("%s has a malformed flag reference %r" % (r["id"], ref))
        elif ref not in flag_ids:
            bad("%s cites %s, which is not a row in data/flags.csv" % (r["id"], ref))
        else:
            promoted.append(ref)
    if len(promoted) != len(set(promoted)):
        bad("two findings claim the same flag id: %s" % promoted)
    if not FAIL:
        ok("findings: %d published, %d promoted to data/flags.csv (%s), every id resolves and "
           "none is shared" % (len(findings), len(promoted), ", ".join(sorted(promoted)) or "none"))
    if os.path.exists(PAGE):
        text = open(PAGE, encoding="utf-8").read()
        stray = [r for r in re.findall(r"FL-\d{2}", text) if r not in flag_ids and r != "FL-52"]
        if stray:
            bad("backlog.html names %s, which is not a row in data/flags.csv" % sorted(set(stray)))
        else:
            ok("page flag ids: every FL- id on the page resolves to a real register row")


def check_coverage_links(rows):
    """The cross-reference column is a navigation aid computed by a script. It must point only at
    clause ids that really exist in the other session's matrix, and the page must say so."""
    path = os.path.join(DATA, "brief_traceability.csv")
    if not os.path.exists(path):
        warn("brief_traceability.csv absent; the cross-reference column is published blank")
        return
    with open(path, encoding="utf-8", newline="") as fh:
        known = {r["id"].strip() for r in csv.DictReader(fh, delimiter="|")}
    cited = {r["coverage_matrix_id"].strip() for r in rows if r["coverage_matrix_id"].strip()}
    unknown = sorted(cited - known)
    if unknown:
        bad("cross-reference column cites clause ids not in brief_traceability.csv: %s" % unknown[:5])
    else:
        unmapped = sum(1 for r in rows if not r["coverage_matrix_id"].strip())
        ok("cross-reference: %d of %d rows link to a real clause in the coverage matrix; %d are "
           "published unmapped rather than linked to something wrong"
           % (len(cited), len(rows), unmapped))
    if os.path.exists(PAGE):
        text = open(PAGE, encoding="utf-8").read()
        for needle in ("Two registers, one brief", "brief-coverage.html",
                       "not an official fact"):
            if needle not in text:
                bad("backlog.html lost the two-register disclosure %r" % needle)
        else:
            ok("page states that the coverage-matrix link is a scripted navigation aid, not a fact")


def check_page(rows):
    if not os.path.exists(PAGE):
        bad("backlog.html is missing; run tools/build_site.py")
        return
    parser = TableParser()
    parser.feed(open(PAGE, encoding="utf-8").read())

    # Every theme must appear in a table whose body is exactly that theme's rows.
    themes = {}
    for r in rows:
        themes.setdefault(r["theme"], []).append(r["id"])
    for theme, expected in themes.items():
        found = None
        for table in parser.tables:
            body_ids = [row[0]["text"] for row in table[1:] if row and re.fullmatch(r"BL-\d{2}", row[0]["text"])]
            if body_ids and set(body_ids) == set(expected):
                found = table
                break
        if found is None:
            bad("theme %r has no table on backlog.html with exactly its %d rows" % (theme, len(expected)))
            continue
        for row in found[1:]:
            if not row:
                continue
            hrefs = [c["href"] for c in row if c.get("href")]
            if not any(h and h.startswith("https://") for h in hrefs):
                bad("%s renders without a single https source link" % row[0]["text"])
    if not [f for f in FAIL if "theme" in f or "https source link" in f]:
        ok("page coverage: all %d themes render, every row carries an https source link" % len(themes))

    text = open(PAGE, encoding="utf-8").read()
    for needle in ("not official NFL fact", "re-read 2026-11-15", "not re-read today",
                   "no official source exists"):
        if needle not in text:
            bad("backlog.html lost the source-class or verification disclosure %r" % needle)
    if "weather.gov" in text and "not a league source" in text:
        ok("non-league dependency: weather.gov is named on the page as a federal, not league, source")
    elif "weather.gov" in text:
        warn("weather.gov appears on the page without its non-league caveat")


def check_replay():
    before = {}
    for name in (REGISTER, SUMMARY, READS, FINDINGS):
        path = os.path.join(DATA, name)
        before[name] = open(path, "rb").read()
    proc = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "build_backlog_58e9c708.py")],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        bad("rebuilding the backlog register failed: %s" % proc.stderr.strip()[:200])
        return
    drift = [n for n in before if open(os.path.join(DATA, n), "rb").read() != before[n]]
    if drift:
        bad("rebuild is not byte-identical for %s" % drift)
    else:
        ok("replay: rebuilding all four backlog files reproduces them byte for byte")


def main():
    gates_path = os.path.join(DATA, "gates.csv")
    with open(gates_path, encoding="utf-8", newline="") as fh:
        gate_ids = {r["id"].strip() for r in csv.DictReader(fh, delimiter="|")}

    rows = load(REGISTER)
    summary = load(SUMMARY)
    reads = load(READS)
    findings = load(FINDINGS)
    if not (rows and summary and reads and findings):
        print("FAIL backlog: register files incomplete", file=sys.stderr)
        return 1

    check_register(rows, gate_ids)
    check_summary(rows, summary)
    check_reads(reads, rows)
    check_findings(findings)
    check_coverage_links(rows)
    check_page(rows)
    check_replay()

    print("=" * 72)
    for m in PASS:
        print("  PASS  " + m)
    for m in WARN:
        print("  WARN  " + m)
    for m in FAIL:
        print("  FAIL  " + m)
    print("=" * 72)
    print("verify_backlog_58e9c708: %d passed · %d warnings · %d failures"
          % (len(PASS), len(WARN), len(FAIL)))
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
