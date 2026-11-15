#!/usr/bin/env python3
"""Publish the delta between two dated reads of the official Week 10 injury hub.

Inputs (read-only):
  data/injuries_wk10_83246f00.csv   the 13 Nov 2026 12:46Z read (296 rows, 26 clubs)
  data/hub_read_8dee7df7.csv        the 15 Nov 2026 12:51Z read (347 rows, 28 clubs), transcribed
                                    row by row from https://www.nfl.com/injuries/ (see FL-82)

Outputs (regenerated on every run):
  data/hub_delta_8dee7df7.csv       one row per club: row counts, designation counts, practice changes
  data/hub_new_rows_8dee7df7.csv    one row per player on the 15 Nov read who is absent from the 13 Nov read

The script fails (exit 1) if the invariants below break, so a changed input can never publish silently:
  * the 15 Nov read covers all 28 clubs on the Week 10 slate (14 games);
  * every row carries an nfl.com source;
  * no player on the 13 Nov read is missing from the 15 Nov read (the hub has only grown).
"""
import csv
import os
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
NOV13 = os.path.join(DATA, "injuries_wk10_83246f00.csv")
NOV15 = os.path.join(DATA, "hub_read_8dee7df7.csv")
OUT_DELTA = os.path.join(DATA, "hub_delta_8dee7df7.csv")
OUT_NEW = os.path.join(DATA, "hub_new_rows_8dee7df7.csv")
SRC15 = "S-INJ-8DEE"
SLATE_CLUBS = 28  # 14 Week 10 games on the hub: 28 clubs
# 13 Nov file uses a short status code for the Q/OUT cells; normalise before comparing.
STATUS_NORM = {"OUT": "Out", "Q": "Questionable", "D": "Doubtful", "": ""}


def read(path):
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="|"))


def main():
    old = read(NOV13)
    new = read(NOV15)
    problems = []

    clubs15 = {r["club"] for r in new}
    if len(clubs15) != SLATE_CLUBS:
        problems.append(f"15 Nov read covers {len(clubs15)} clubs, expected {SLATE_CLUBS}")
    no_source = [r for r in new if not r["source_url"].startswith("https://www.nfl.com/")]
    if no_source:
        problems.append(f"{len(no_source)} rows on the 15 Nov read lack an nfl.com source")

    key_old = {(r["team"], r["player"]): r for r in old}
    key_new = {(r["club"], r["player"]): r for r in new}
    missing = sorted(set(key_old) - set(key_new))
    if missing:
        problems.append(f"{len(missing)} players on the 13 Nov read are absent on 15 Nov: {missing[:5]}")

    clubs = sorted({r["team"] for r in old} | clubs15)
    rows_old = Counter(r["team"] for r in old)
    rows_new = Counter(r["club"] for r in new)
    des_old = Counter(r["team"] for r in old if r["status"])
    des_new = Counter(r["club"] for r in new if r["game_status"])
    out_new = Counter(r["club"] for r in new if r["game_status"] == "Out")
    q_new = Counter(r["club"] for r in new if r["game_status"] == "Questionable")
    d_new = Counter(r["club"] for r in new if r["game_status"] == "Doubtful")
    practice_changed = Counter()
    for k in set(key_old) & set(key_new):
        if key_old[k]["practice"] != key_new[k]["practice"]:
            practice_changed[k[0]] += 1
    new_rows = Counter(c for c, _ in set(key_new) - set(key_old))

    def state(count_old, count_new):
        if count_old == 0 and count_new > 0:
            return "no rows on 13 Nov (LAC and BAL were 'No Injuries Reported' on 12 Nov, FL-01); rows on 15 Nov"
        if count_old == 0 and count_new == 0:
            return "no rows on either read"
        return "rows on both reads"

    header = ["club", "rows_13nov", "rows_15nov", "rows_added_15nov", "rows_removed_15nov",
              "designated_13nov", "designated_15nov", "out_15nov", "questionable_15nov",
              "doubtful_15nov", "practice_changed_shared", "state_15nov_vs_13nov", "source"]
    delta_rows = []
    for c in clubs:
        delta_rows.append([
            c, rows_old[c], rows_new[c], new_rows[c], 0,
            des_old[c], des_new[c], out_new[c], q_new[c], d_new[c], practice_changed[c],
            state(rows_old[c], rows_new[c]),
            SRC15,
        ])
    tot = ["TOTAL", sum(rows_old.values()), sum(rows_new.values()), sum(new_rows.values()), 0,
           sum(des_old.values()), sum(des_new.values()), sum(out_new.values()),
           sum(q_new.values()), sum(d_new.values()), sum(practice_changed.values()),
           f"all {len(clubs15)} clubs on the Week 10 slate", SRC15]
    delta_rows.append(tot)
    if sum(rows_new.values()) != len(new):
        problems.append("club totals on the 15 Nov read do not sum to the row count")

    with open(OUT_DELTA, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="|", lineterminator="\n")
        w.writerow(header)
        w.writerows(delta_rows)

    new_header = ["club", "player", "pos", "injury", "practice", "game_status", "source"]
    with open(OUT_NEW, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="|", lineterminator="\n")
        w.writerow(new_header)
        for c, p in sorted(set(key_new) - set(key_old)):
            r = key_new[(c, p)]
            w.writerow([c, p, r["pos"], r["injury"], r["practice"], r["game_status"], SRC15])

    print(f"13 Nov rows {len(old)} across {len(rows_old)} clubs | 15 Nov rows {len(new)} across {len(clubs15)} clubs")
    print(f"rows added on 15 Nov {sum(new_rows.values())} | rows removed {len(missing)} | shared {len(set(key_old) & set(key_new))}")
    print(f"designations 13 Nov {sum(des_old.values())} | 15 Nov {sum(des_new.values())}")
    print(f"practice-code changes on shared rows {sum(practice_changed.values())}")
    if problems:
        for p in problems:
            print("FAIL:", p)
        return 1
    print("OK: invariants hold")
    return 0


if __name__ == "__main__":
    sys.exit(main())
