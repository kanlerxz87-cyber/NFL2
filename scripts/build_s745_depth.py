#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Session 745f788e - build the all-club depth / deficiency register.

Two official inputs, one deterministic join:

  1. each club's own published depth chart  -> scripts/s745_depth_data.py
  2. the official NFL injury report         -> scripts/s745_injury_data.py

Outputs (all pipe-delimited, fixed field count, one official link per row):

  data/s745_depth_charts.csv        every published depth slot
  data/s745_depth_deficiencies.csv  per position group: starter, his injury state,
                                    who is next, how deep the club has to reach
  data/s745_depth_summary.csv       per-club roll-up
  data/s745_injury_refresh.csv      the 2026-11-13 read of the official injury page

Nothing is inferred. A club whose depth chart could not be read from an official
club page has no rows and appears in the summary with coverage 0.
"""

import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from s745_depth_data import CHARTS              # noqa: E402
from s745_injury_data import (ROWS, NO_INJURIES_REPORTED,      # noqa: E402
                              INJURY_SOURCE, INJURY_CAPTURED_UTC)

DATA = os.path.join(ROOT, "data")

# Clubs in the league, in the repo's canonical order (data/teams.json).
CLUBS = ["BUF", "MIA", "NE", "NYJ", "BAL", "CIN", "CLE", "PIT",
         "HOU", "IND", "JAX", "TEN", "DEN", "KC", "LV", "LAC",
         "DAL", "NYG", "PHI", "WAS", "CHI", "DET", "GB", "MIN",
         "ATL", "CAR", "NO", "TB", "AZ", "LAR", "SF", "SEA"]

INJURY_PAGE = INJURY_SOURCE

# The club page this session fetched for every club, charted or not. Houston is the one
# club whose official depth-chart page carries the chart as an image rather than a table,
# so it has a page but no rows - "page fetched" and "chart transcribed" are different facts.
CLUB_CHART_PAGE = {
    "HOU": "https://www.houstontexans.com/team/depth-chart",
}
DEPTH_SOURCE_NOTE = "nfl.com/teams/<club>/depth-chart returns 404 (published as FL-05); the club's own site is the only official chart"


# --------------------------------------------------------------------------- #
# game ids
# --------------------------------------------------------------------------- #
# The injury hub and the official schedule page are both official, and they list the
# same three games in a different order: the hub's 6th/7th/8th blocks are BUF@NYJ,
# MIA@IND, CAR@NO, while data/schedule_2026_wk10.csv numbers MIA@IND 6, CAR@NO 7,
# BUF@NYJ 8. The ids themselves are ours, not the league's, so there is no official
# value to be wrong about - but two files that disagree silently mis-join, and the
# schedule file is the one every other page on this site keys on (it carries game_url
# and drives the game labels). So: transcribe the hub in the hub's own order, and
# remap to the schedule's ids here, by the two clubs in the game. Published as FL-38.
def load_game_id_map():
    """hub game_id -> schedule game_id, matched on the clubs that appear in it."""
    path = os.path.join(DATA, "schedule_2026_wk10.csv")
    if not os.path.exists(path):
        return {}, {}
    with open(path, encoding="utf-8") as fh:
        sched = list(csv.DictReader(fh, delimiter="|"))
    by_clubs = {frozenset((r["away"], r["home"])): r["game_id"] for r in sched}
    by_one = {}
    for r in sched:
        for c in (r["away"], r["home"]):
            by_one.setdefault(c, r["game_id"])
    remap, notes = {}, {}
    hub = {}
    for (gid, club, _p, _s, _pos, _i, _pr, _st) in ROWS:
        hub.setdefault(gid, set()).add(club)
    for gid, clubs in hub.items():
        if by_clubs.get(frozenset(clubs)) == gid:
            continue                      # this id already agrees with the schedule
        target = by_clubs.get(frozenset(clubs))
        if target is None and len(clubs) == 1:
            target = by_one.get(next(iter(clubs)))   # a game with only one club filing
        if target and target != gid:
            remap[gid] = target
            notes[gid] = "hub lists %s here; the schedule page numbers that game %s" % (
                "/".join(sorted(clubs)), target)
    return remap, notes


GAME_ID_REMAP, GAME_ID_NOTES = load_game_id_map()


def game_id_for(gid):
    return GAME_ID_REMAP.get(gid, gid)


# --------------------------------------------------------------------------- #
# name normalisation for the join
# --------------------------------------------------------------------------- #

_SUFFIXES = {"jr", "sr", "ii", "iii", "iv", "v", "x"}


def norm(name):
    """Lowercase, drop punctuation and generational suffixes, collapse spaces."""
    s = name.lower()
    s = s.replace("\u2019", "'").replace("\u2018", "'")
    s = re.sub(r"[^a-z' ]+", " ", s)
    toks = [t for t in s.split() if t and t not in _SUFFIXES]
    return " ".join(toks).strip()


def split_alternates(name):
    """A club may print two men in one slot ('Davis Allen / Tyler Higbee')."""
    parts = re.split(r"\s*/\s*", name)
    return [p.strip() for p in parts if p.strip()]


# --------------------------------------------------------------------------- #
# 1. depth chart slots
# --------------------------------------------------------------------------- #

def build_chart_rows():
    rows = []
    for club in CLUBS:
        c = CHARTS.get(club)
        if not c:
            continue
        for unit in ("offense", "defense"):
            seen = {}
            for label, players in c[unit]:
                n = seen.get(label, 0) + 1
                seen[label] = n
                # keep the club's own label, disambiguated only when repeated
                group = label if n == 1 else "%s_%d" % (label, n)
                for idx, raw in enumerate(players, start=1):
                    if not raw or not raw.strip():
                        continue
                    for person in split_alternates(raw):
                        rows.append({
                            "club": club,
                            "unit": unit,
                            "position_group": group,
                            "position_label": label,
                            "depth": str(idx),
                            "player": person,
                            "chart_as_published": c.get("as_published", ""),
                            "source": c["source"],
                        })
    return rows


# --------------------------------------------------------------------------- #
# 2. injury index
# --------------------------------------------------------------------------- #

def build_injury_index():
    """club -> normalised name -> injury row."""
    idx = {}
    for (gid, club, player, slug, pos, inj, pract, status) in ROWS:
        idx.setdefault(club, {}).setdefault(norm(player), []).append({
            "game_id": gid, "player": player, "name": player, "slug": slug, "pos": pos,
            "injury": inj, "practice": pract, "status": status,
        })
    return idx


def lookup(idx, club, player):
    """Exact normalised match, else a unique last-name match inside the club."""
    m = idx.get(club, {})
    key = norm(player)
    if key in m:
        return m[key][0]
    last = key.split()[-1] if key else ""
    if not last:
        return None
    hits = []
    for k, v in m.items():
        if k.split() and k.split()[-1] == last:
            hits.append(v[0])
    if len(hits) == 1:
        return hits[0]
    return None


PRACTICE_TEXT = {"F": "Full Participation in Practice",
                 "L": "Limited Participation in Practice",
                 "D": "Did Not Participate In Practice"}


# --------------------------------------------------------------------------- #
# 3. the deficiency register
# --------------------------------------------------------------------------- #

def build_deficiency_rows(chart_rows, inj_idx):
    """One row per (club, unit, position group) that has a chart."""
    groups = {}
    order = []
    for r in chart_rows:
        key = (r["club"], r["unit"], r["position_group"])
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(r)

    out = []
    for key in order:
        club, unit, group = key
        slots = sorted(groups[key], key=lambda r: int(r["depth"]))
        chain = []
        for r in slots:
            hit = lookup(inj_idx, club, r["player"]) or {}
            chain.append({
                "depth": int(r["depth"]),
                "player": r["player"],
                # the name the league's own page prints, which is not always the name the
                # club's chart prints (Kevin Byard vs Kevin Byard III). Keeping both is what
                # makes the join checkable instead of merely plausible.
                "hit_name": hit.get("name", ""),
                "practice": hit.get("practice", ""),
                "status": hit.get("status", ""),
                "injury": hit.get("injury", ""),
                "on_report": bool(hit),
            })

        # how deep must the club reach to field a body the league has not ruled out?
        depth_reached = ""
        next_man = ""
        skipped = []
        for slot in chain:
            if slot["status"].lower() == "out":
                skipped.append(slot["player"])
                continue
            depth_reached = str(slot["depth"])
            next_man = slot["player"]
            break
        if not depth_reached:
            depth_reached = "vacant" if chain else ""
            next_man = ""
            skipped = [s["player"] for s in chain]
        if not any(s["depth"] == 1 for s in chain):
            # The club prints no first string for this group, so "how deep must it reach"
            # is not a question this chart can answer. Publishing a number here would mean
            # claiming a second-string body is a replacement for a starter who was never
            # printed, which is an inference - the row goes blank and carries the flag.
            depth_reached = ""
            next_man = ""

        starter = chain[0] if chain else None
        chain_len = max((s["depth"] for s in chain), default=0)

        # a "deficiency" is a group whose first-string man is ruled Out or is
        # absent from the club's chart entirely
        first_out = bool(starter and starter["status"].lower() == "out")
        vacant_first = not any(s["depth"] == 1 for s in chain)
        if not starter:
            tier = ""
        elif starter["status"].lower() == "out":
            tier = "out"
        elif starter["practice"] == "D":
            tier = "did not practice"
        elif starter["practice"] == "L":
            tier = "limited"
        elif starter["practice"] == "F":
            tier = "full"
        else:
            tier = "not on report"

        out.append({
            "club": club,
            "unit": unit,
            "position_group": group,
            "projected_starter": starter["player"] if starter else "",
            "starter_injury_name": (starter["hit_name"] if starter else ""),
            "starter_on_injury_report": ("yes" if starter and starter["on_report"] else
                                         ("no" if starter else "")),
            "starter_practice": PRACTICE_TEXT.get(starter["practice"], "") if starter else "",
            "starter_game_status": starter["status"] if starter else "",
            "depth_reached": depth_reached,
            "next_man_up": next_man,
            "players_skipped": "; ".join(skipped),
            "chain_length": str(chain_len) if chain_len else "",
            "starter_availability_tier": tier,
            "deficiency_flag": ("1st-string OUT" if first_out else
                                ("no 1st string published" if vacant_first else "")),
            "replacement_on_report": ("yes" if next_man and
                                      lookup(inj_idx, club, next_man) else
                                      ("no" if next_man else "")),
            "replacement_status": (lookup(inj_idx, club, next_man) or {}).get("status", "")
                                  if next_man else "",
            "injury_source": INJURY_PAGE,
            "chart_source": slots[0]["source"] if slots else "",
        })
    return out


# --------------------------------------------------------------------------- #
# 4. roll-up
# --------------------------------------------------------------------------- #

def build_summary(def_rows):
    out = []
    for club in CLUBS:
        mine = [r for r in def_rows if r["club"] == club]
        charted = bool(CHARTS.get(club))
        groups_out = sum(1 for r in mine if r["deficiency_flag"] == "1st-string OUT")
        vacant = sum(1 for r in mine if r["deficiency_flag"] == "no 1st string published")
        third = sum(1 for r in mine if r["depth_reached"] == "3")
        fourth = sum(1 for r in mine if r["depth_reached"] == "4")
        no_body = sum(1 for r in mine if r["depth_reached"] == "vacant")
        casc = sum(1 for r in mine if r["replacement_status"].lower() == "out")
        dnp = sum(1 for r in mine if r["starter_availability_tier"] == "did not practice")
        lim = sum(1 for r in mine if r["starter_availability_tier"] == "limited")
        off_dnp = sum(1 for r in mine if r["unit"] == "offense" and
                      r["starter_availability_tier"] == "did not practice")
        def_dnp = sum(1 for r in mine if r["unit"] == "defense" and
                      r["starter_availability_tier"] == "did not practice")
        offense_groups = sum(1 for r in mine if r["unit"] == "offense")
        defense_groups = sum(1 for r in mine if r["unit"] == "defense")
        out.append({
            "club": club,
            "chart_published": "yes" if charted else "no",
            "groups_charted": str(len(mine)),
            "offense_groups": str(offense_groups) if charted else "",
            "defense_groups": str(defense_groups) if charted else "",
            "groups_first_string_out": str(groups_out) if charted else "",
            "groups_reaching_3rd_string": str(third) if charted else "",
            "groups_reaching_4th_string": str(fourth) if charted else "",
            "groups_with_no_body_listed": str(no_body) if charted else "",
            "groups_no_1st_string_published": str(vacant) if charted else "",
            "groups_replacement_also_out": str(casc) if charted else "",
            "groups_starter_dnp": str(dnp) if charted else "",
            "groups_starter_limited": str(lim) if charted else "",
            "offense_groups_starter_dnp": str(off_dnp) if charted else "",
            "defense_groups_starter_dnp": str(def_dnp) if charted else "",
            "chart_source": CHARTS.get(club, {}).get("source", "")
                            or CLUB_CHART_PAGE.get(club, ""),
            "note": ("" if charted else
                     "no machine-readable depth chart on the club's official site"),
        })
    return out


# --------------------------------------------------------------------------- #
# 5. write
# --------------------------------------------------------------------------- #

def write_csv(path, header, rows):
    keys = [h for h in header]
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys, delimiter="|",
                           lineterminator="\n", extrasaction="raise")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in keys})


def main():
    chart_rows = build_chart_rows()
    inj_idx = build_injury_index()
    def_rows = build_deficiency_rows(chart_rows, inj_idx)
    summary = build_summary(def_rows)

    write_csv(os.path.join(DATA, "s745_depth_charts.csv"),
              ["club", "unit", "position_group", "position_label", "depth",
               "player", "chart_as_published", "source"],
              chart_rows)

    write_csv(os.path.join(DATA, "s745_depth_deficiencies.csv"),
              ["club", "unit", "position_group", "projected_starter",
             "starter_injury_name",
               "starter_on_injury_report", "starter_practice", "starter_game_status",
               "depth_reached", "next_man_up", "players_skipped", "chain_length",
               "starter_availability_tier", "deficiency_flag",
            "replacement_on_report", "replacement_status",
               "injury_source", "chart_source"],
              def_rows)

    write_csv(os.path.join(DATA, "s745_depth_summary.csv"),
              ["club", "chart_published", "groups_charted", "offense_groups",
               "defense_groups", "groups_first_string_out",
               "groups_reaching_3rd_string", "groups_reaching_4th_string",
               "groups_with_no_body_listed", "groups_no_1st_string_published",
               "groups_replacement_also_out", "groups_starter_dnp",
               "groups_starter_limited", "offense_groups_starter_dnp",
               "defense_groups_starter_dnp", "chart_source", "note"],
              summary)

    inj_rows = []
    for (gid, club, player, slug, pos, inj, pract, status) in ROWS:
        inj_rows.append({
            "game_id": game_id_for(gid), "club": club, "player": player,
            "player_url": "https://www.nfl.com/players/%s/" % slug,
            "pos": pos, "injury": inj,
            "practice": PRACTICE_TEXT.get(pract, ""),
            "game_status": status,
            "captured_utc": INJURY_CAPTURED_UTC,
            "source": INJURY_PAGE,
        })
    for gid, club in NO_INJURIES_REPORTED:
        inj_rows.append({
            "game_id": game_id_for(gid), "club": club, "player": "", "player_url": "",
            "pos": "", "injury": "", "practice": "",
            "game_status": "No Injuries Reported",
            "captured_utc": INJURY_CAPTURED_UTC,
            "source": INJURY_PAGE,
        })
    write_csv(os.path.join(DATA, "s745_injury_refresh.csv"),
              ["game_id", "club", "player", "player_url", "pos", "injury",
               "practice", "game_status", "captured_utc", "source"],
              inj_rows)

    clubs_charted = len(CHARTS)
    print("depth slots        : %d" % len(chart_rows))
    print("position groups    : %d" % len(def_rows))
    print("clubs charted      : %d of %d" % (clubs_charted, len(CLUBS)))
    print("injury rows        : %d (+%d 'No Injuries Reported' markers)"
          % (len(ROWS), len(NO_INJURIES_REPORTED)))
    outs = [r for r in def_rows if r["deficiency_flag"] == "1st-string OUT"]
    for src, dst in sorted(GAME_ID_REMAP.items()):
        print("game id remapped   : %s -> %s (%s)" % (src, dst, GAME_ID_NOTES.get(src, "")))
    print("groups w/ 1st OUT  : %d" % len(outs))
    print("groups to 3rd/4th  : %d / %d"
          % (sum(1 for r in def_rows if r["depth_reached"] == "3"),
             sum(1 for r in def_rows if r["depth_reached"] == "4")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
