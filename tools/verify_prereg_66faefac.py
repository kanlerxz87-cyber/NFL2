#!/usr/bin/env python3
"""Verify the Week 10 pre-registration lock, and grade it if the slate has settled.

Gate G-11 says a strategy may not be edited inside a measurement window. A CSV in a git repo is
trivially editable, so this tool is the enforcement: it re-hashes the locked file and recomputes
every derived cell from the inputs, then fails if either has moved. After the games finish it grades
the calls against the official results in data/games_2026_wk10_played.csv.

Run it before and after any change to data/:

    python3 tools/verify_prereg_66faefac.py
"""
import csv, hashlib, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
LOCK = "prereg_wk10_66faefac.sha256"
FILE = "prereg_wk10_66faefac.csv"
THRESHOLD = 4


def read(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        raw = list(csv.reader(fh, delimiter="|"))
    hdr = raw[0]
    return [dict(zip(hdr, r)) for r in raw[1:]]


def main():
    fails, notes = [], []
    body = open(os.path.join(DATA, FILE), encoding="utf-8").read()
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
    lock_lines = [l for l in open(os.path.join(DATA, LOCK), encoding="utf-8") if not l.startswith("#")]
    if not lock_lines or lock_lines[0].split()[2] != digest:
        fails.append("the published hash does not match the file: %s vs %s"
                     % (lock_lines[0].split()[2] if lock_lines else "missing", digest))
    else:
        notes.append("lock holds: sha256 %s matches data/%s" % (digest[:16], FILE))

    pre = read(FILE)
    counts = {r["club"]: r for r in read("hub_club_counts_20261113_66faefac.csv")}
    played = {r["game_id"]: r for r in read("games_2026_wk10_played.csv")}
    orig = {r["game"]: r for r in read("originated_lines_wk10_a392.csv")}
    fair = {r["game_id"]: r for r in read("computed_fair_lines.csv")}

    def load(club):
        c = counts[club]
        return int(c["out"]) + int(c["dnp"])

    called = graded = hits = misses = 0
    for r in pre:
        d = load(r["away"]) - load(r["home"])
        if str(d) != r["load_delta"]:
            fails.append("%s: load_delta says %s, the club counts give %d" % (r["game_id"], r["load_delta"], d))
        expect_side = ("home" if d > 0 else "away") if abs(d) >= THRESHOLD else ""
        if r["side_taken"] != expect_side:
            fails.append("%s: side_taken %r but the locked rule at threshold %d says %r"
                         % (r["game_id"], r["side_taken"], THRESHOLD, expect_side or "no call"))
        if r["settled"] == "no" and expect_side:
            called += 1
        if r["settled"] == "no" and r["locked"] != "yes":
            fails.append("%s: an un-played fixture is not marked locked" % r["game_id"])
        if r["game_id"] in played:
            g = played[r["game_id"]]
            a, h = int(g["away_pts"]), int(g["home_pts"])
            margin = h - a                     # positive = home won by that many
            ours = orig.get(r["game_id"], {})
            if r["side_taken"] and ours:
                # our published spread, in the repo's own convention: a positive number means the
                # home side was favoured by that many points, so the home side covers when
                # margin > line, and the away side covers when margin < line.
                line = float(ours["our_spread_home_favoured"])
                graded += 1
                covered_home = margin > line
                won = (r["side_taken"] == "home" and covered_home) or (r["side_taken"] == "away" and not covered_home)
                hits += 1 if won else 0
                misses += 0 if won else 1
                notes.append("%s: graded post-hoc, call %s, our number %.2f, actual margin %+d -> %s"
                             % (r["game_id"], r["side_taken"], line, margin, "hit" if won else "miss"))
            if abs(float(fair.get(r["game_id"], {}).get("fair_spread_home", 0) or 0) - float(r["fair_spread_home"] or 0)) > 0.005:
                fails.append("%s: fair_spread_home drifted from data/computed_fair_lines.csv" % r["game_id"])
        elif r["settled"] != "no":
            fails.append("%s is marked settled but is not in data/games_2026_wk10_played.csv" % r["game_id"])
    if sum(1 for r in pre if float(r["stake_units"]) != 0) != 0:
        fails.append("a locked row carries a non-zero stake; gates G-01/G-07 are not passed, so staking stays 0")
    if not all(r["rule"] == "ST-15 v1" for r in pre):
        fails.append("a row carries a rule version other than ST-15 v1 - the window must not be edited")

    print("locked file: %d fixtures, %d called at threshold %d" % (len(pre), called, THRESHOLD))
    if graded:
        print("graded: %d calls, %d hit, %d miss (post-hoc rows are disclosed as not evidence)"
              % (graded, hits, misses))
    else:
        print("graded: nothing yet - no settled fixture carries a locked call")
    for n in notes:
        print("  note  " + n)
    for f in fails:
        print("  FAIL  " + f)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
