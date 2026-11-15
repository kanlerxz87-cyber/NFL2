#!/usr/bin/env python3
"""Row-by-row re-verification of the Week 10 injury hub for four clubs (session e733834d).

Inputs (both tracked):
  data/injuries_wk10_e733834d_20261115.csv  transcription of https://www.nfl.com/injuries/ as read
                                            by the agent (WAS, NYG, NE, DET blocks), 44 player rows
  data/injuries_wk10_83246f00.csv           the 13 Nov 2026 12:46Z read this repository publishes

Output:
  data/reverification_e733834d.csv          one row per official player row, MATCH or MISMATCH,
                                            with the fields that differ and the flag that records it

Run with --check to fail (exit 1) if the register on disk differs from a fresh comparison.
"""
import csv
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DATA = os.path.join(ROOT, "data")
OFFICIAL = os.path.join(DATA, "injuries_wk10_e733834d_20261115.csv")
PUBLISHED = os.path.join(DATA, "injuries_wk10_83246f00.csv")
OUT = os.path.join(DATA, "reverification_e733834d.csv")
SOURCE = "https://www.nfl.com/injuries/"
CLUBS = ("WAS", "NYG", "NE", "DET")
# Official per-club row counts as read on the page (checked against the transcription by verify.py).
OFFICIAL_COUNTS = {"WAS": 9, "NYG": 11, "NE": 15, "DET": 9}
# Which flag records a mismatch on each club. Both are in data/flags.csv.
FLAG_FOR_CLUB = {"NE": "FL-73", "DET": "FL-74"}


def read(path):
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="|"))


def key(r):
    return (r["team"].strip(), r["player"].strip())


def compare():
    off = [r for r in read(OFFICIAL)]
    pub = [r for r in read(PUBLISHED) if r["team"].strip() in CLUBS]
    pub_by = {key(r): r for r in pub}
    off_keys = {key(r) for r in off}
    out, mismatch_count = [], 0
    for i, r in enumerate(off, start=1):
        k = key(r)
        p = pub_by.get(k)
        fields = ("injury", "practice", "status")
        o_vals = {f: r[f].strip() for f in fields}
        if p is None:
            diffs = ["row absent from the published read"]
        else:
            diffs = [f for f in fields if o_vals[f] != p[f].strip()]
        fmt = lambda d: "injury=%s; practice=%s; status=%s" % (d["injury"] or "blank", d["practice"] or "blank", d["status"] or "blank")
        pub_txt = fmt({f: (p[f].strip() if p else "") for f in fields}) if p else "row absent"
        if diffs:
            mismatch_count += 1
            flag = FLAG_FOR_CLUB[r["team"]]
            names = {"injury": "injury", "practice": "practice code", "status": "game status"}
            what = ", ".join(names[d] for d in diffs)
            note = ("The 13 Nov read differs from the live page in %s. %s. Recorded in %s; the row is not edited in place."
                    % (what, "Live page: " + fmt(o_vals), flag))
            result = "MISMATCH"
        else:
            flag = ""
            note = "Identical on injury, practice code and game status."
            result = "MATCH"
        out.append({
            "id": "RV-E%02d" % i,
            "check": "%s %s" % (r["team"], r["player"]),
            "scope": "row %d of 44 on the four clubs read from the live page" % i,
            "published_value": pub_txt,
            "official_value": fmt(o_vals),
            "result": result,
            "note": note,
            "source": SOURCE,
        })
    unmatched = [k for k in pub_by if k not in off_keys]
    return out, mismatch_count, unmatched, off


def render(rows):
    cols = ["id", "check", "scope", "published_value", "official_value", "result", "note", "source"]
    lines = ["|".join(cols)]
    for r in rows:
        vals = [str(r[c]).replace("|", "/").replace("\n", " ") for c in cols]
        lines.append("|".join(vals))
    return "\n".join(lines) + "\n"


def main():
    rows, mismatches, unmatched, off = compare()
    text = render(rows)
    counts = {c: sum(1 for r in off if r["team"].strip() == c) for c in CLUBS}
    if counts != OFFICIAL_COUNTS:
        print("transcription row counts %s differ from the counts recorded on the page %s" % (counts, OFFICIAL_COUNTS))
        return 1
    if "--check" in sys.argv:
        with open(OUT, encoding="utf-8") as fh:
            on_disk = fh.read()
        if on_disk != text:
            print("data/reverification_e733834d.csv is stale; rerun tools/reverify_e733834d.py")
            return 1
        print("register matches a fresh comparison: %d rows, %d mismatches" % (len(rows), mismatches))
        return 0
    with open(OUT, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    print("wrote %d rows; %d mismatches; published rows not on the live page: %s" % (len(rows), mismatches, unmatched))
    return 0


if __name__ == "__main__":
    sys.exit(main())
