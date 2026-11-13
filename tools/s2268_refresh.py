#!/usr/bin/env python3
"""Session 2268bfb2 - the 2026-11-13 refresh and the two structural defects it exposed.

Produces, from the dated register transcribed off the official hub at
data/s2268_injuries_wk10_20261113.csv:

  data/s2268_injury_delta_20261113.csv    every difference against the two registers
                                          already published in this repository
  data/s2268_gameid_collisions.csv        the Week 10 game-id disagreement between
                                          data/injuries_2026_wk10.csv and
                                          data/schedule_2026_wk10.csv
  data/s2268_coverage_20261113.csv        club-by-club coverage of the live hub

The transcription itself is a manual act: the official page was read at the timestamp in
FETCH_UTC and its rows were copied field for field. This script does not fetch. It only
diffs, counts and writes, so the arithmetic can be re-run and checked by anyone.
"""

from __future__ import annotations

import csv
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

FETCH_UTC = "2026-11-13T12:40Z"
HUB = "https://www.nfl.com/injuries/"
SCHEDULE_URL = "https://www.nfl.com/schedules/2026/by-week/week-10"

NEW = "s2268_injuries_wk10_20261113.csv"
PUBLISHED = "injuries_2026_wk10.csv"        # what the site's Injuries page renders
HUBREFRESH = "injuries_wk10_2026_hubrefresh.csv"  # a392's later re-fetch

VOCAB = {"OUT": "Out", "Q": "Questionable"}   # the hub prints Out / Questionable


def load(path):
    with open(os.path.join(DATA, path), newline="") as fh:
        return list(csv.DictReader(fh, delimiter="|"))


def norm(v):
    """Normalise the vocabulary difference without pretending it is a data change."""
    v = (v or "").strip()
    return VOCAB.get(v.upper(), v)


def write_csv(name, header, rows):
    with open(os.path.join(DATA, name), "w", newline="") as fh:
        w = csv.writer(fh, delimiter="|", lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def main():
    new = load(NEW)
    published = load(PUBLISHED)
    hubrefresh = load(HUBREFRESH)
    schedule = load("schedule_2026_wk10.csv")

    # ---- what the hub says, per club ------------------------------------------
    sched_pair = {r["game_id"]: (r["away"], r["home"]) for r in schedule}
    game_url = {r["game_id"]: r["game_url"] for r in schedule}
    played = {r["game_id"] for r in schedule if r["date"] <= "2026-11-12"}

    cov_rows = []
    counts = {}
    for r in new:
        counts.setdefault(r["team"], {"rows": 0, "dnp": 0, "out": 0})
        counts[r["team"]]["rows"] += 1
        if r["practice"] == "D":
            counts[r["team"]]["dnp"] += 1
        if r["status"]:
            counts[r["team"]]["out"] += 1
    declared_none = [("LAC", "W10-14"), ("BAL", "W10-14")]
    for team, cnt in sorted(counts.items()):
        gcode = next(g for g, (a, h) in sched_pair.items() if team in (a, h))
        cov_rows.append([team, gcode, cnt["rows"], cnt["dnp"], cnt["out"],
                         "rows published by the hub", game_url[gcode]])
    for team, gcode in declared_none:
        cov_rows.append([team, gcode, 0, 0, 0,
                         'the hub prints "No Injuries Reported" for this club',
                         game_url[gcode]])
    write_csv("s2268_coverage_20261113.csv",
              ["club", "game_id", "rows_on_hub", "did_not_participate", "designated",
               "note", "source"],
              cov_rows)

    # ---- delta against the two published registers -----------------------------
    def key(r):
        return (r["team"], r["player"])

    def game_of(r):
        # data/injuries_2026_wk10.csv names the column 'game'; mine names it 'game_id'.
        return r.get("game_id") or r.get("game") or ""

    new_k = {key(r): r for r in new}
    pub_k = {key(r): r for r in published}
    hub_k = {key(r): r for r in hubrefresh}

    delta = []
    for k in sorted(new_k):
        n = new_k[k]
        for label, other in (("data/injuries_2026_wk10.csv (the published Injuries page)", pub_k),
                             ("data/injuries_wk10_2026_hubrefresh.csv (a392 re-fetch)", hub_k)):
            o = other.get(k)
            if o is None:
                delta.append([game_of(n), n["team"], n["player"], n["pos"], "row added",
                              "", f"{n['practice']} / {n['injury']} / {n['status']}".strip(" /"),
                              label, HUB])
                continue
            diffs = []
            if o["practice"] != n["practice"]:
                diffs.append(f"practice {o['practice']} -> {n['practice']}")
            if norm(o["injury"]) != norm(n["injury"]):
                diffs.append(f"injury '{o['injury']}' -> '{n['injury']}'")
            if norm(o["status"]) != norm(n["status"]):
                diffs.append(f"status '{o['status']}' -> '{n['status']}'")
            if diffs:
                delta.append([game_of(n), n["team"], n["player"], n["pos"],
                              "field changed" if all("status" not in d or
                                                     (o["status"] and n["status"]) for d in diffs)
                              else "field changed",
                              " ; ".join(diffs), "", label, HUB])
    for label, other in (("data/injuries_2026_wk10.csv (the published Injuries page)", pub_k),
                         ("data/injuries_wk10_2026_hubrefresh.csv (a392 re-fetch)", hub_k)):
        for k in sorted(other):
            if k in new_k:
                continue
            o = other[k]
            delta.append([game_of(o), o["team"], o["player"], o["pos"], "row removed",
                          f"{o['practice']} / {o['injury']} / {o['status']}".strip(" /"),
                          f"no longer on the hub at {FETCH_UTC}", label, HUB])
    write_csv("s2268_injury_delta_20261113.csv",
              ["game_id", "club", "player", "pos", "change", "old_value", "new_value",
               "compared_against", "source"],
              delta)

    # ---- the game-id collision -------------------------------------------------
    pub_games = {}
    for r in published:
        pub_games.setdefault(r["game"], set()).add(r["team"])
    coll = []
    for gcode, pair in sorted(sched_pair.items()):
        sched_teams = set(pair)
        pub_teams = pub_games.get(gcode, set())
        if not pub_teams:
            coll.append([gcode, " ".join(sorted(sched_teams)), "not published",
                         "no rows", "the injury register has no rows for this game; the hub "
                         "prints No Injuries Reported for both clubs",
                         game_url[gcode]])
            continue
        if sched_teams == pub_teams:
            coll.append([gcode, " ".join(sorted(sched_teams)), " ".join(sorted(pub_teams)),
                         "match", "", game_url[gcode]])
            continue
        rotated = [g for g, pr in sched_pair.items() if set(pr) == pub_teams]
        if rotated and rotated[0] != gcode:
            coll.append([gcode, " ".join(sorted(sched_teams)), " ".join(sorted(pub_teams)),
                         "ROTATION - id names a different fixture",
                         "this id points at " + " @ ".join(sorted(pub_teams)) +
                         ", which the schedule file calls " + rotated[0] +
                         ". A join between the two files attaches a club's injuries to the "
                         "wrong opponent for three of the fourteen Week 10 games.",
                         game_url[gcode]])
            continue
        missing = sorted(sched_teams - pub_teams)
        coll.append([gcode, " ".join(sorted(sched_teams)), " ".join(sorted(pub_teams)),
                     "incomplete",
                     "one or both clubs have no rows in the injury register ("
                     + ", ".join(missing) + "); a collection gap, not a rotation",
                     game_url[gcode]])
    write_csv("s2268_gameid_collisions.csv",
              ["game_id", "teams_in_schedule_2026_wk10_csv", "teams_in_injuries_2026_wk10_csv",
               "verdict", "consequence", "source"],
              coll)

    n_mismatch = sum(1 for r in coll if r[3] != "match")
    n_rotation = sum(1 for r in coll if r[3].startswith("ROTATION"))
    summary = {
        "fetched_utc": FETCH_UTC,
        "rows_on_live_hub": len(new),
        "clubs_with_rows": len(counts),
        "clubs_declaring_none": [t for t, _ in declared_none],
        "rows_in_published_injuries_csv": len(published),
        "rows_in_hubrefresh_csv": len(hubrefresh),
        "delta_vs_published": len([d for d in delta
                                   if "published Injuries page" in d[7]]),
        "delta_vs_hubrefresh": len([d for d in delta if "hubrefresh" in d[7]]),
        "game_id_disagreements": n_mismatch,
        "game_id_rotations": n_rotation,
    }
    with open(os.path.join(DATA, "s2268_refresh_summary.json"), "w") as fh:
        import json
        json.dump(summary, fh, indent=2)
    import json
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
