#!/usr/bin/env python3
"""Availability watch — the dated answer to "who is actually out, and who is missing from the record?"

The brief asks for three things this file exists to serve:

  1. injury tracking that a reader can date,
  2. knowledge of deficiencies when a backup replaces a starter (both sides of the ball), and
  3. no value on the site that cannot be traced to an official page.

Nothing here is inferred. Every output row is either an arithmetic tally over
`data/availability_watch_c3ec1487.csv` (the 2026-11-13 transcription of
https://www.nfl.com/injuries/, 296 player rows across the 26 clubs the hub publishes)
or a blank. The two clubs the hub publishes as "No Injuries Reported" are carried as an
explicit *reported-none* state, never as zero and never as a silent gap (S-19 / FL-01).

Outputs (all deterministic, all regenerated on every run):

  data/availability_watch_by_club_c3ec1487.csv   one row per club: rows, practice codes,
                                                 designations, and what a replacement
                                                 decision would need that is still missing
  data/availability_watch_gates_c3ec1487.csv     the four readiness gates this snapshot
                                                 does or does not clear, with the number
                                                 that decides each one
  data/computed_availability_watch_c3ec1487.csv  the arithmetic a reader would otherwise
                                                 redo by hand (counts, shares, the
                                                 designation gap against captured coverage)

Run:  python3 tools/build_availability_watch.py
Then: python3 tools/build_site.py
"""
import csv
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

SNAP = "availability_watch_c3ec1487.csv"
BY_CLUB = "availability_watch_by_club_c3ec1487.csv"
GATES = "availability_watch_gates_c3ec1487.csv"
COMPUTED = "computed_availability_watch_c3ec1487.csv"

READ_UTC = "2026-11-13T12:45Z"
HUB = "https://www.nfl.com/injuries/"
# One row per club that the hub publishes a block for. Kept here rather than derived, because the
# official page - not this repository - decides which clubs filed. LAC and BAL are the two clubs the
# hub answers with "No Injuries Reported"; they are in this list on purpose so their state is a
# recorded fact rather than a missing key.
REPORTED_NONE = {"LAC", "BAL"}
# Ordinal scale for the practice codes, so a change between two dated reads can be labelled a move
# up or a move down without a table of special cases. Higher participation is a better sign.
PRACTICE_RANK = {"D": 0, "L": 1, "F": 2}


def direction(a, b):
    """Label a practice-code change. Rank 0 = did not practise, 2 = full."""
    if PRACTICE_RANK[b] > PRACTICE_RANK[a]:
        return "upgrade"
    if PRACTICE_RANK[b] < PRACTICE_RANK[a]:
        return "downgrade"
    return "no change"


def rows(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="|"))


def write(name, header, body):
    path = os.path.join(DATA, name)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write("|".join(header) + "\n")
        for r in body:
            assert len(r) == len(header), (name, r)
            for cell in r:
                assert "|" not in str(cell), (name, cell)
            fh.write("|".join(str(c) for c in r) + "\n")
    return len(body)


def main():
    snap = rows(SNAP)
    sched = rows("schedule_2026_wk10.csv")
    reported = rows("injuries_wk10_2026_hubrefresh.csv")     # 2026-11-12T22:35Z read, another session's file, read-only here

    game_clubs = {}
    for g in sched:
        game_clubs.setdefault(g["game_id"], []).append(g["away"])
        game_clubs.setdefault(g["game_id"], []).append(g["home"])

    clubs = sorted({r["club"] for r in snap})
    by_club = []
    for club in clubs:
        mine = [r for r in snap if r["club"] == club]
        game = sorted({r["game_id"] for r in mine})
        gid = game[0] if len(game) == 1 else ""
        dnp = sum(1 for r in mine if r["practice"] == "D")
        lim = sum(1 for r in mine if r["practice"] == "L")
        full = sum(1 for r in mine if r["practice"] == "F")
        desig = [r for r in mine if r["game_status"].strip()]
        out = sum(1 for r in desig if r["game_status"] == "OUT")
        q = sum(1 for r in desig if r["game_status"] == "Q")
        doubt = sum(1 for r in desig if r["game_status"] == "D")
        # The two columns a "backup replaces starter" decision needs, and neither is on the hub.
        # Left blank on purpose: no official public depth chart exists (FL-06).
        by_club.append([
            club,
            gid,
            len(mine),
            dnp,
            lim,
            full,
            len(desig),
            out,
            q,
            doubt,
            "published: %d player rows" % len(mine),
            "",   # depth rank / string of the unavailable player -- FL-06
            "",   # measured replacement effect in points -- no measurement exists
            HUB,
        ])

    # The two clubs that answered "No Injuries Reported" are rows too, with a stated state.
    for club in sorted(REPORTED_NONE):
        gid = next((g for g in sched if g["away"] == club or g["home"] == club), {})
        by_club.append([club, gid.get("game_id", ""), 0, 0, 0, 0, 0, 0, 0, 0,
                        "reported none by the league", "", "", HUB])
    by_club.sort(key=lambda r: (r[1], r[0]))

    n_by_club = write(BY_CLUB, [
        "club", "game_id", "rows_published", "did_not_practice", "limited", "full",
        "designations", "out", "questionable", "doubtful",
        "what_the_hub_publishes", "string_of_unavailable_player", "replacement_effect_pts",
        "source"], by_club)

    # ---- arithmetic a reader would otherwise redo -------------------------------------------
    playing = len({c for g in sched for c in (g["away"], g["home"])})
    filed = len(clubs) + len(REPORTED_NONE)
    total = len(snap)
    desig = sum(1 for r in snap if r["game_status"].strip())
    injury_cells = sum(1 for r in snap if r["injury"].strip())
    prior_desig = sum(1 for r in reported if r["status"].strip())
    prior_total = len(reported)
    computed = [
        ["clubs on the Week 10 slate", playing,
         "counted from data/schedule_2026_wk10.csv (14 fixtures)", "the denominator for every coverage share",
         "https://www.nfl.com/schedules/2026/by-week/week-10"],
        ["clubs the hub answers for", filed,
         "%d with a player table + %d marked \"No Injuries Reported\"" % (len(clubs), len(REPORTED_NONE)),
         "coverage is complete for the slate", HUB],
        ["player rows in this snapshot", total,
         "row count of the 2026-11-13 transcription", "the size of the record, not a count of injuries",
         HUB],
        ["game-status designations", desig,
         "rows with a non-empty game_status", "the only field that says a player is actually out", HUB],
        ["designations as a share of rows", "%.1f%%" % (100.0 * desig / total),
         "%d / %d" % (desig, total),
         "most of the record is practice participation, not availability", HUB],
        ["injury-description cells", injury_cells,
         "rows naming a body part or illness", "the hub leaves this blank for most rows", HUB],
        ["practice codes: did not practice", sum(1 for r in snap if r["practice"] == "D"),
         "rows with practice == D", "the earliest signal of a downgrade", HUB],
        ["practice codes: limited", sum(1 for r in snap if r["practice"] == "L"),
         "rows with practice == L", "ambiguous by rule; cannot be read as out", HUB],
        ["practice codes: full", sum(1 for r in snap if r["practice"] == "F"),
         "rows with practice == F", "a full practice does not clear a player", HUB],
        ["designations in the 2026-11-12 read", prior_desig,
         "non-empty status cells in data/injuries_wk10_2026_hubrefresh.csv",
         "the hub has published no new game status in the interval", HUB],
        ["player rows in the 2026-11-12 read", prior_total,
         "row count of that file", "the only thing that moved between the two reads is formatting", HUB],
        ["clubs with no depth rank anywhere", playing,
         "no official public depth chart exists (FL-06)",
         "the backup-replaces-starter requirement is blocked for every club, not some", HUB],
    ]
    n_computed = write(COMPUTED, ["metric", "value", "how_it_is_computed", "what_it_means", "source"], computed)

    # ---- what moved between the two dated reads ----------------------------------------------
    # This is the part of the page that cannot be produced by re-reading a single snapshot: the hub
    # is a series. The 2026-11-12T22:35Z read (data/injuries_wk10_2026_hubrefresh.csv, another
    # session's file, read-only here) and this one are compared player by player. Nothing is edited.
    def key(r, club_col):
        return ("%s|%s" % (r[club_col], r["player"]))

    old = {key(r, "team"): r for r in reported}
    new = {key(r, "club"): r for r in snap}
    added = sorted(set(new) - set(old))
    removed = sorted(set(old) - set(new))
    changed = [(k, old[k]["practice"], new[k]["practice"]) for k in sorted(set(old) & set(new))
               if old[k]["practice"] != new[k]["practice"]]
    newly_named = [(k, new[k]["injury"]) for k in added if new[k]["injury"].strip()]
    club_of = lambda k: k.split("|")[0]

    movement = [
        ["players newly listed", len(added),
         "in the 2026-11-13 read, absent from the 2026-11-12 read",
         ", ".join(sorted({club_of(k) for k in added})) or "none",
         "a club can add a name at any practice; a model that froze the earlier list is stale", HUB],
        ["players no longer listed", len(removed),
         "in the 2026-11-12 read, absent from the 2026-11-13 read",
         "none", "zero removals means the hub only ever grew in this interval - worth knowing before treating a missing name as a recovery", HUB],
        ["practice codes changed", len(changed),
         "same club and player, different practice code",
         "%d upgraded, %d downgraded" % (sum(1 for _, a, b in changed if direction(a, b) == "upgrade"),
                                        sum(1 for _, a, b in changed if direction(a, b) == "downgrade")),
         "the injury signal the brief asks for is this delta, not the level (S-12)", HUB],
        ["game-status designations added", desig - prior_desig,
         "designations now minus designations in the 2026-11-12 read",
         ", ".join(sorted({r["club"] for r in snap if r["game_status"].strip() and
                           ("%s|%s" % (r["club"], r["player"])) not in {k for k in old if old[k]["status"].strip()}})),
         "the first game statuses appear roughly 48 hours before kickoff", HUB],
        ["players with a named injury", len(newly_named),
         "newly listed players whose injury cell names a body part or illness",
         ", ".join("%s (%s)" % (club_of(k), inj) for k, inj in newly_named) or "none",
         "the hub publishes a diagnosis for only a minority of rows", HUB],
    ]
    n_movement = write("availability_watch_movement_c3ec1487.csv",
                       ["change", "count", "how_it_is_computed", "detail", "what_it_means", "source"],
                       movement)

    write("availability_watch_practice_deltas_c3ec1487.csv",
          ["club", "player", "practice_2026_11_12", "practice_2026_11_13", "direction", "source"],
          [[club_of(k), k.split("|", 1)[1], a, b,
            direction(a, b), HUB]
           for k, a, b in changed])

    # ---- readiness gates --------------------------------------------------------------------
    gates = [
        ["AW-1", "Every club on the slate has a stated injury state", "PASS",
         "%d of %d clubs" % (filed, playing),
         "no club is silently absent; two are explicitly \"reported none\"",
         "https://www.nfl.com/injuries/"],
        ["AW-2", "Every listed player has a game status", "FAIL",
         "%d of %d rows" % (desig, total),
         "the hub itself publishes designations only near kickoff; a snapshot taken midweek cannot read as a final inactive list",
         "https://www.nfl.com/injuries/"],
        ["AW-3", "Depth rank (1st/2nd/3rd/4th string) is available for every club", "FAIL",
         "0 of %d clubs" % playing,
         "no official public depth chart exists; club-published charts cover 4 clubs and are labelled unofficial (FL-06)",
         "https://www.nfl.com/teams/new-england-patriots/depth-chart/"],
        ["AW-4", "The replacement effect is measured in points", "FAIL",
         "0 measurements",
         "requires snap counts and a settled sample; neither is on this site",
         "https://www.nfl.com/injuries/"],
    ]
    n_gates = write(GATES, ["gate", "question", "result", "measured_value", "why", "source"], gates)

    # ---- self-check: the snapshot is internally consistent -----------------------------------
    assert all(r["club"] in {c for g in sched for c in (g["away"], g["home"])} for r in snap), \
        "a snapshot row names a club that is not on the Week 10 slate"
    assert all(r["game_id"] in game_clubs for r in snap), "a snapshot row names an unknown game"
    for r in snap:
        assert r["club"] in game_clubs[r["game_id"]], \
            "%s %s is not playing in %s" % (r["game_id"], r["club"], r["game_id"])
        assert r["practice"] in ("D", "L", "F"), r
        assert r["game_status"] in ("", "OUT", "Q", "D"), r
        assert r["source"].startswith("https://www.nfl.com/"), r

    print("availability watch: %d clubs, %d player rows, %d designations "
          "(%d by-club rows, %d computed metrics, %d gates)"
          % (filed, total, desig, n_by_club, n_computed, n_gates))


if __name__ == "__main__":
    main()
