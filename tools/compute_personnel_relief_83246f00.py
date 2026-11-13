#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Join the official injury report to each club's own published depth chart.

Deterministic and dependency-free. Reads three inputs and writes two tables:

  data/injuries_wk10_83246f00.csv          the 2026-11-13 read of nfl.com/injuries/
  data/depth_charts_wk10_83246f00.json     each club's own "Unofficial Depth Chart"
  data/schedule_2026_wk10.csv              game ids and sides (away/home)

  -> data/personnel_relief_wk10_83246f00.csv        one row per listed player, with his string
  -> data/personnel_relief_club_83246f00.csv        per club x side, 1st-string losses and the
                                                    string of the man who replaces them

What this script will NOT do, by design:

* It never infers a string. A player the club's chart does not list gets
  `not published`, and the row says so in its own column. There is no
  "probably 2nd string".
* It never infers who starts. The chart's 1st-string slot is the club's own
  publication of its intended starter; nothing here claims a player took a snap.
* It never treats a missing row as a fit player. `No Injuries Reported` is a
  separate row with its own meaning (S-19: it is not a zero).

Run: python3 tools/compute_personnel_relief_83246f00.py
"""
from __future__ import print_function

import csv
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

INJ = os.path.join(ROOT, "data", "injuries_wk10_83246f00.csv")
CHARTS = os.path.join(ROOT, "data", "depth_charts_wk10_83246f00.json")
SCHED = os.path.join(ROOT, "data", "schedule_2026_wk10.csv")
OUT_ROWS = os.path.join(ROOT, "data", "personnel_relief_wk10_83246f00.csv")
OUT_CLUB = os.path.join(ROOT, "data", "personnel_relief_club_83246f00.csv")

BLANK = "not published"

# Offensive positions as the injury hub writes them, and defensive ones, so a
# player's side can be stated from the hub's own position code alone.
OFF_POS = {"QB", "RB", "FB", "WR", "TE", "T", "G", "C", "OT", "OG", "OL", "LS_OFF"}
DEF_POS = {"DE", "DT", "NT", "EDGE", "LB", "ILB", "OLB", "MLB", "CB", "S", "SS", "FS", "DB", "NB"}
ST_POS = {"K", "P", "LS", "H", "PR", "KR"}

PRACTICE_WORD = {
    "F": "Full Participation in Practice",
    "L": "Limited Participation in Practice",
    "D": "Did Not Participate In Practice",
}

STATUS_WORD = {"OUT": "Out", "Q": "Questionable", "D": "Doubtful"}


def read_csv(path):
    with io.open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="|"))


def side_of(pos):
    """Side of the ball from the hub's own position code. Blank when the code is blank."""
    p = (pos or "").strip().upper()
    if not p:
        return BLANK
    if p in OFF_POS:
        return "offence"
    if p in DEF_POS:
        return "defence"
    if p in ST_POS:
        return "special teams"
    return BLANK


def slot_index(chart_side, player):
    """Where the club prints this player, as a 0-based slot. None when absent.

    A club that prints two names in one cell records both at that slot, so the
    slot of a cell's second name is the same index as the first. A club that
    prints a hole keeps the hole - WAS LB2 is ['Frankie Luvu', None, 'Kain
    Medrano'], so Medrano is 3rd string and the row can say so.
    """
    hits = []
    for unit_key, names in chart_side.items():
        for i, n in enumerate(names):
            if n and n.strip().lower() == player.strip().lower():
                hits.append((i, unit_key))
    if not hits:
        return None, []
    hits.sort()
    best = hits[0][0]
    also = ["%s slot %d" % (k, i + 1) for i, k in hits[1:]]
    return best, also


def ordinal(n):
    if n is None:
        return BLANK
    words = {0: "1st string", 1: "2nd string", 2: "3rd string", 3: "4th string"}
    return words.get(n, "%dth string" % (n + 1))


def unit_of(chart_side, player):
    for unit_key, names in chart_side.items():
        for n in names:
            if n and n.strip().lower() == player.strip().lower():
                return unit_key
    return BLANK


def next_man(chart_side):
    """The 2nd-string name in each unit, used to name who a 1st-string loss promotes.

    Returns a dict unit_key -> (slot, name) of the club's own second entry, or
    None where the club lists only one player at that unit.
    """
    out = {}
    for unit_key, names in chart_side.items():
        for i, n in enumerate(names):
            if i == 0:
                continue
            if n and n.strip():
                out[unit_key] = (i, n.strip())
                break
    return out


def cascade(chart_side, unit_key, hub_state):
    """Walk the club's own published order for one unit and report each rung's status.

    This is the deficiency measure the brief asks for, and it is deliberately a
    *report*, not a prediction: it states, rung by rung in the club's own order,
    whether that player appears on the official injury report today and with what
    practice code. It does not claim who starts. A wednesday DNP is not a Sunday
    absence, and the page says so.

    `hub_state` maps a lowercase player name to his practice code for this club.
    Returns (last_rung_clean, narrative) where last_rung_clean is the 1-based rung
    of the deepest player who is *not* on the report at all, or None.
    """
    names = [n for n in chart_side.get(unit_key, []) if n and n.strip()]
    if not names:
        return None, BLANK
    parts = []
    deepest_clean = None
    for i, n in enumerate(names, start=1):
        code = hub_state.get(n.strip().lower())
        if code is None:
            parts.append("%d. %s - not on the official report" % (i, n.strip()))
            deepest_clean = i
        else:
            parts.append("%d. %s - %s" % (i, n.strip(), PRACTICE_WORD.get(code, code)))
    return deepest_clean, "; ".join(parts)


def main():
    inj = read_csv(INJ)
    charts = json.load(io.open(CHARTS, "r", encoding="utf-8"))["charts"]
    sched = read_csv(SCHED)

    game_of, side_in_game = {}, {}
    for g in sched:
        game_of[g["away"]] = g["game_id"]
        game_of[g["home"]] = g["game_id"]
        side_in_game[g["away"]] = "away"
        side_in_game[g["home"]] = "home"

    # per-club name -> practice code, so a cascade can ask "is this rung on the report?"
    hub_state = {}
    for r in inj:
        hub_state.setdefault(r["team"].strip(), {})[r["player"].strip().lower()] = r["practice"]

    rows = []
    for r in inj:
        club = r["team"].strip()
        chart = charts.get(club)
        pos = r["pos"].strip()
        side = side_of(pos)
        if chart is None:
            string, also, unit, replacement, chart_url, chart_state = (
                BLANK, "", BLANK, BLANK, BLANK, "club chart not transcribed this session")
        else:
            chart_url = chart["url"]
            chart_state = "transcribed"
            # Choose the chart side from the hub's position code; fall back to a
            # search of both sides only when the code is ambiguous, and record which.
            order = []
            if side == "offence":
                order = ["offence", "defence"]
            elif side == "defence":
                order = ["defence", "offence"]
            else:
                order = ["offence", "defence"]
            string = BLANK
            also, unit, replacement = "", BLANK, BLANK
            for s in order:
                idx, also_hits = slot_index(chart[s], r["player"])
                if idx is not None:
                    string, also = ordinal(idx), "; ".join(also_hits)
                    unit = unit_of(chart[s], r["player"])
                    if idx == 0:
                        nm = next_man(chart[s]).get(unit)
                        replacement = ("%s (%s)" % (nm[1], ordinal(nm[0]))) if nm else BLANK
                    break

        # the unit's full published order, rung by rung, against today's report
        cascade_txt, deepest_clean = BLANK, ""
        if chart is not None and unit != BLANK:
            chart_side = chart["offence"] if side != "defence" else chart["defence"]
            if unit in chart_side:
                deepest_clean, txt = cascade(chart_side, unit, hub_state.get(club, {}))
                if txt != BLANK:
                    cascade_txt = txt

        rows.append({
            "game": r["game"],
            "club": club,
            "side_in_game": side_in_game.get(club, BLANK),
            "player": r["player"],
            "pos": pos,
            "side": side,
            "injury": r["injury"],
            "practice": r["practice"],
            "practice_word": PRACTICE_WORD.get(r["practice"], BLANK) if r["practice"] else BLANK,
            "game_status": STATUS_WORD.get(r["status"], BLANK) if r["status"] else BLANK,
            "depth_unit": unit,
            "string": string,
            "also_listed_at": also,
            "next_man_up": replacement if string == "1st string" else BLANK,
            "unit_cascade": cascade_txt,
            "unit_clean_to_rung": (str(deepest_clean) if deepest_clean else (BLANK if cascade_txt == BLANK else "0")),
            "chart_url": chart_url,
            "injury_url": r["source"],
        })

    fields = ["game", "club", "side_in_game", "player", "pos", "side", "injury", "practice",
              "practice_word", "game_status", "depth_unit", "string", "also_listed_at",
              "next_man_up", "unit_cascade", "unit_clean_to_rung", "chart_url", "injury_url"]
    with io.open(OUT_ROWS, "w", encoding="utf-8", newline="\n") as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter="|", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    # ---- per club x side summary -------------------------------------------------
    clubs = sorted(game_of)
    summary = []
    for club in clubs:
        chart = charts.get(club)
        for side in ("offence", "defence", "special teams"):
            mine = [r for r in rows if r["club"] == club and r["side"] == side]
            listed = [r for r in mine if r["string"] != BLANK]
            firsts = [r for r in listed if r["string"] == "1st string"]
            first_d = [r for r in firsts if r["practice"] == "D"]
            first_lim = [r for r in firsts if r["practice"] == "L"]
            first_out = [r for r in firsts if r["game_status"] == "Out"]
            deep = [r for r in listed if r["string"] not in ("1st string",)]
            deep_d = [r for r in deep if r["practice"] == "D"]
            # the club's chart, and whether every listed player resolved
            unresolved = [r["player"] for r in mine if r["string"] == BLANK]
            if chart is None:
                state = "club chart not transcribed this session"
            elif not mine:
                state = "no players listed on the official hub at this read"
            elif not listed:
                state = "no listed player resolved to this club's chart"
            elif not unresolved:
                state = "every listed player resolved to the club's chart"
            else:
                state = "%d of %d listed players not on the club's chart" % (
                    len(unresolved), len(mine))
            summary.append({
                "game": game_of.get(club, BLANK),
                "club": club,
                "side": side,
                "listed": len(mine),
                "resolved_to_chart": len(listed),
                "first_string_listed": len(firsts),
                "first_string_dnp": len(first_d),
                "first_string_limited": len(first_lim),
                "first_string_designated_out": len(first_out),
                # who the club itself names behind a lost 1st-string player
                "relief_named": "; ".join(sorted(set(
                    r["next_man_up"] for r in firsts if r["next_man_up"] != BLANK
                ))) or BLANK,
                "deep_string_listed": len(deep),
                "deep_string_dnp": len(deep_d),
                "chart_state": state,
                "chart_url": (chart["url"] if chart else BLANK),
                "injury_url": "https://www.nfl.com/injuries/",
            })

    cfields = ["game", "club", "side", "listed", "resolved_to_chart", "first_string_listed",
               "first_string_dnp", "first_string_limited", "first_string_designated_out",
               "relief_named", "deep_string_listed", "deep_string_dnp", "chart_state",
               "chart_url", "injury_url"]
    with io.open(OUT_CLUB, "w", encoding="utf-8", newline="\n") as f:
        w = csv.DictWriter(f, fieldnames=cfields, delimiter="|", lineterminator="\n")
        w.writeheader()
        w.writerows(summary)

    # ---- report ------------------------------------------------------------------
    tr = sum(1 for r in rows if r["string"] != BLANK)
    print("personnel relief: %d listed players over %d clubs" % (len(rows), len(clubs)))
    print("  resolved to a club depth chart: %d" % tr)
    print("  clubs with a transcribed chart: %d of %d" % (len(charts), len(clubs)))
    print("  first-string players who did not practise: %d"
          % sum(1 for r in rows if r["string"] == "1st string" and r["practice"] == "D"))
    print("wrote %s (%d rows)" % (os.path.basename(OUT_ROWS), len(rows)))
    print("wrote %s (%d rows)" % (os.path.basename(OUT_CLUB), len(summary)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
