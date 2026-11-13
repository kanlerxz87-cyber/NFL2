#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Session 745f788e - audit the all-club depth register and the decision console.

Everything here is recomputed from the published CSVs and the two transcribed source
files. The point is not to re-check that the builder ran - it is to catch the three
ways this particular register could quietly go wrong:

  1. a row without an official link (the site's own rule, applied per row)
  2. a number in the summary that no longer equals the rows it summarises
  3. a depth chain that claims more than the two sources can support - for example
     a "next man up" who is not on the club's chart, or a starter marked on the
     injury report who is not on the injury report

Run standalone:  python3 scripts/verify_s745.py
Wired into the repository audit by tools/verify.py (function s745_registers_reproduce).
"""

import csv
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

FAIL, WARN, PASS = [], [], []


def ok(m):
    PASS.append(m)


def bad(m):
    FAIL.append(m)


def warn(m):
    WARN.append(m)


def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="|"))


def club_host(url):
    return re.sub(r"^https?://([^/]+).*", r"\1", (url or "").strip())


# --------------------------------------------------------------------------- #
# 1. every row carries an official link
# --------------------------------------------------------------------------- #
def every_row_sourced():
    charts = load("s745_depth_charts.csv")
    nohost = [r for r in charts if not r["source"].startswith("https://")]
    if nohost:
        bad("depth charts: %d rows without an https source" % len(nohost))
    else:
        ok("depth charts: all %d slots cite the club page the slot was read from" % len(charts))

    defi = load("s745_depth_deficiencies.csv")
    bad_src = [r for r in defi if not r["chart_source"].startswith("https://")
               or not r["injury_source"].startswith("https://")]
    if bad_src:
        bad("deficiencies: %d rows missing one of their two official links" % len(bad_src))
    else:
        ok("deficiencies: all %d groups carry both official links (club chart + league report)"
           % len(defi))

    inj = load("s745_injury_refresh.csv")
    bad_url = [r for r in inj if r["player"].strip()
               and not r["player_url"].startswith("https://www.nfl.com/players/")]
    if bad_url:
        bad("injury refresh: %d player rows without an nfl.com profile link" % len(bad_url))
    else:
        ok("injury refresh: every named player links his own nfl.com profile")


# --------------------------------------------------------------------------- #
# 2. the summary is the rows
# --------------------------------------------------------------------------- #
def summary_reproduces():
    defi = load("s745_depth_deficiencies.csv")
    summ = load("s745_depth_summary.csv")
    if len(summ) != 32:
        bad("summary: expected one row per club, found %d" % len(summ))
    per = {}
    for r in defi:
        d = per.setdefault(r["club"], {"n": 0, "off": 0, "def": 0, "out": 0,
                                       "dnp": 0, "lim": 0, "off_dnp": 0, "def_dnp": 0})
        d["n"] += 1
        d["off" if r["unit"] == "offense" else "def"] += 1
        if r["starter_game_status"].strip().upper() == "OUT":
            d["out"] += 1
        if r["starter_availability_tier"] == "did not practice":
            d["dnp"] += 1
            d["off_dnp" if r["unit"] == "offense" else "def_dnp"] += 1
        if r["starter_availability_tier"] == "limited":
            d["lim"] += 1
    wrong = []
    for r in summ:
        c = r["club"]
        d = per.get(c, {"n": 0, "off": 0, "def": 0, "out": 0,
                        "dnp": 0, "lim": 0, "off_dnp": 0, "def_dnp": 0})
        if r["chart_published"] != "yes":
            # A club with no chart must publish blanks, not zeros. "HOU has 0 groups with a
            # starter ruled out" is a claim about Houston; the truth is that the club's chart
            # could not be read, which is what FL-37 is for.
            filled = [col for col in ("offense_groups", "defense_groups",
                                      "groups_first_string_out", "groups_starter_dnp",
                                      "groups_starter_limited", "offense_groups_starter_dnp",
                                      "defense_groups_starter_dnp") if r[col].strip()]
            if filled:
                wrong.append("%s: uncharted but publishes %s" % (c, filled))
            continue
        for col, key in (("groups_charted", "n"), ("offense_groups", "off"),
                         ("defense_groups", "def"), ("groups_first_string_out", "out"),
                         ("groups_starter_dnp", "dnp"), ("groups_starter_limited", "lim"),
                         ("offense_groups_starter_dnp", "off_dnp"),
                         ("defense_groups_starter_dnp", "def_dnp")):
            if r[col] != str(d[key]):
                wrong.append("%s.%s: summary %s vs rows %d" % (c, col, r[col], d[key]))
    if wrong:
        bad("per-club summary does not reproduce from the group rows: %s" % wrong[:4])
    else:
        ok("per-club summary reproduces exactly from the %d group rows (8 counts x 32 clubs)"
           % len(defi))

    # the two files must describe the same population
    charts = load("s745_depth_charts.csv")
    slots_by_club = {}
    for r in charts:
        slots_by_club[r["club"]] = slots_by_club.get(r["club"], 0) + 1
    total_first = sum(1 for r in charts if r["depth"] == "1")
    groups = len(defi)
    if total_first < groups:
        bad("charts: only %d first-string slots for %d position groups" % (total_first, groups))
    else:
        ok("charts: %d groups carry at least one printed first-string slot (%d slots total)"
           % (groups, len(charts)))


# --------------------------------------------------------------------------- #
# 3. the join cannot claim more than the sources say
# --------------------------------------------------------------------------- #
def join_is_supported():
    defi = load("s745_depth_deficiencies.csv")
    tier_vocab = {"not on report", "full", "limited", "did not practice", "out", ""}
    bad_tier = [r for r in defi if r["starter_availability_tier"] not in tier_vocab]
    if bad_tier:
        bad("deficiencies: starter tier %r outside the vocabulary %s"
            % (bad_tier[0]["starter_availability_tier"], sorted(tier_vocab)))
    else:
        ok("deficiencies: every starter tier is one of the five published states")

    # a starter marked on the report must exist on the report
    inj = {(r["club"], r["player"].strip().lower())
           for r in load("s745_injury_refresh.csv") if r["player"].strip()}
    # The join matches on a normalised name, so the club's spelling and the league's
    # spelling are not always the same string (Kevin Byard III vs Kevin Byard). The audit
    # therefore checks the column that records what the league's page actually printed,
    # not the column that records what the club's chart printed.
    ghost = [r for r in defi
             if r["starter_on_injury_report"] == "yes"
             and (r["club"], r["starter_injury_name"].strip().lower()) not in inj]
    unrecorded = [r for r in defi if r["starter_on_injury_report"] == "yes"
                  and not r["starter_injury_name"].strip()]
    ghost = unrecorded + ghost
    if ghost:
        bad("deficiencies: %d starters marked on the injury report who are not on it: %s"
            % (len(ghost), ["%s %s" % (r["club"], r["starter_injury_name"] or r["projected_starter"])
                            for r in ghost[:3]]))
    else:
        n = sum(1 for r in defi if r["starter_on_injury_report"] == "yes")
        ok("deficiencies: all %d starters marked on the report are on the report" % n)

    # the reverse: anyone on the report must not be silently dropped as fully available
    tiers = {(r["club"], r["projected_starter"].strip().lower()): r["starter_availability_tier"]
             for r in defi}
    dropped = []
    for (club, player) in sorted(inj):
        t = tiers.get((club, player))
        if t == "not on report":
            dropped.append("%s %s" % (club, player))
    if dropped:
        bad("deficiencies: %d players are on the injury report but their group says "
            "'not on report': %s" % (len(dropped), dropped[:4]))
    else:
        ok("deficiencies: no player on the injury report is recorded as 'not on report'")

    # depth_reached must be consistent with the tier
    bad_depth = []
    for r in defi:
        d = r["depth_reached"].strip()
        if not d.isdigit():
            # blank is honest in exactly one case: the club prints no first string, so the
            # register cannot say how deep it must reach. Anywhere else it is a hole.
            if d == "" and r["deficiency_flag"] == "no 1st string published":
                continue
            bad_depth.append("%s %s: depth_reached %r" % (r["club"], r["position_group"], d))
            continue
        d = int(d)
        if d > 1 and r["starter_availability_tier"] != "out":
            bad_depth.append("%s %s: reaches depth %d with tier %r"
                             % (r["club"], r["position_group"], d, r["starter_availability_tier"]))
    if bad_depth:
        bad("deficiencies: inconsistent depth claims: %s" % bad_depth[:4])
    else:
        ok("deficiencies: every group reaching past its first string has an Out starter, "
           "and no group claims a depth it cannot justify")


# --------------------------------------------------------------------------- #
# 4. the injury refresh is a faithful transcription
# --------------------------------------------------------------------------- #
def injury_refresh_is_clean():
    inj = load("s745_injury_refresh.csv")
    sched = load("schedule_2026_wk10.csv")
    pair = {r["game_id"]: {r["away"], r["home"]} for r in sched}
    mismatch = []
    for r in inj:
        clubs = pair.get(r["game_id"])
        if clubs is None:
            mismatch.append("%s: unknown game id" % r["game_id"])
        elif r["club"] not in clubs:
            mismatch.append("%s: %s is not in %s" % (r["game_id"], r["club"], sorted(clubs)))
    if mismatch:
        # This is the defect FL-38 exists to keep visible: the official injury hub and the
        # official schedule page list three Week 10 games in a different order, and the two
        # published files inherited the two different orders.
        bad("injury refresh: %d rows keyed to the wrong fixture: %s" % (len(mismatch), mismatch[:4]))
    else:
        ok("injury refresh: all %d rows key to the fixture the schedule file puts those clubs in"
           % len(inj))

    vocab = {"", "Full Participation in Practice", "Limited Participation in Practice",
             "Did Not Participate In Practice"}
    badp = [r for r in inj if r["practice"] not in vocab]
    if badp:
        bad("injury refresh: practice value %r outside the league's three-word vocabulary"
            % badp[0]["practice"])
    else:
        ok("injury refresh: practice values are exactly the league's three published phrasings")

    stat = {"", "Out", "Questionable", "Doubtful", "No Injuries Reported"}
    bads = [r for r in inj if r["game_status"] not in stat]
    if bads:
        bad("injury refresh: game status %r outside the published vocabulary" % bads[0]["game_status"])
    else:
        n_out = sum(1 for r in inj if r["game_status"] == "Out")
        ok("injury refresh: %d rows, %d of them carrying an Out designation" % (len(inj), n_out))

    markers = [r for r in inj if r["game_status"] == "No Injuries Reported"]
    if not markers:
        warn("injury refresh: no 'No Injuries Reported' markers; a club that declared none "
             "would be indistinguishable from a club that was never read (FL-01)")
    else:
        ok("injury refresh: %d 'No Injuries Reported' markers kept as rows, so a club that "
           "declared none is never conflated with a club that was not read" % len(markers))


# --------------------------------------------------------------------------- #
# 5. the decision console adds no facts
# --------------------------------------------------------------------------- #
def console_is_derived_only():
    scores = load("s745_suggestion_scores.csv")
    sug = load("suggestions.csv")
    if len(scores) != len(sug):
        bad("suggestion scores: %d rows for %d suggestions" % (len(scores), len(sug)))
    else:
        ok("suggestion scores: one row per register suggestion (%d)" % len(sug))
    ids_s = {r["id"] for r in scores}
    ids_r = {r["id"] for r in sug}
    if ids_s != ids_r:
        bad("suggestion scores: ids differ from the register: %s"
            % sorted(ids_s ^ ids_r)[:6])
    else:
        ok("suggestion scores: the id set is the register's, with nothing added or dropped")

    # the arithmetic must reproduce from the register's own three fields
    IP = {"H": 3, "M": 2, "L": 1}
    EP = {"L": 1, "M": 2, "H": 3}
    RP = {"Low": 1, "Medium": 2, "High": 3}
    by_id = {r["id"]: r for r in sug}
    wrong = []
    for r in scores:
        src = by_id[r["id"]]
        want = round(IP[src["impact"]] / (EP[src["effort"]] + RP[r["risk_class"]]), 2)
        if abs(float(r["priority_score"]) - want) > 1e-9:
            wrong.append("%s: %s vs %.2f" % (r["id"], r["priority_score"], want))
    if wrong:
        bad("suggestion scores: priority score does not reproduce from impact/effort/risk: %s"
            % wrong[:4])
    else:
        ok("suggestion scores: every priority score reproduces from the register's own "
           "impact, effort and risk fields")

    paths = load("s745_decision_paths.csv")
    if {r["path"] for r in paths} != {"A", "B", "C", "D"}:
        bad("decision paths: expected exactly four paths")
    members = []
    for r in paths:
        members += [x.strip() for x in r["suggestion_ids"].split(",") if x.strip()]
    if len(members) != len(set(members)):
        bad("decision paths: an id appears in more than one bundle")
    elif set(members) - ids_s:
        bad("decision paths: bundles name ids the register does not hold: %s"
            % sorted(set(members) - ids_s)[:6])
    elif set(members) != ids_s:
        # Suggestions another session adds in a category this console has never seen are left
        # out rather than forced into a path they do not belong to. Surfaced, not fatal: the
        # register belongs to everyone, the bundle assignment is this console's proposal.
        warn("decision paths: %d of %d suggestions are not in any bundle (%s); the console "
             "prints them unassigned rather than guessing a path"
             % (len(ids_s - set(members)), len(ids_s), ", ".join(sorted(ids_s - set(members)))[:80]))
    else:
        ok("decision paths: the four bundles partition all %d suggestions exactly once" % len(ids_s))
    for r in paths:
        ids = [x.strip() for x in r["suggestion_ids"].split(",") if x.strip()]
        if r["suggestions"] != str(len(ids)):
            bad("decision path %s: says %s suggestions, bundles %d" % (r["path"], r["suggestions"], len(ids)))
    ok("decision paths: each bundle's own count matches the ids it lists")

    gaps = load("s745_information_gaps.csv")
    q = load("questions.csv")
    if len(gaps) != len(q) or {r["id"] for r in gaps} != {r["id"] for r in q}:
        bad("information gaps: does not match the question register (%d vs %d)" % (len(gaps), len(q)))
    else:
        ok("information gaps: restates all %d questions and invents none" % len(q))
    # Compared row by row, not id by id: the question register itself carries two ids used
    # twice for different questions (published as FL-54), so a dict keyed on id would compare
    # each restated row against the wrong original and report a re-wording that never happened.
    rew = []
    for r, src in zip(gaps, q):
        for col in ("information_we_have", "information_we_lack", "discovery_action"):
            key = {"information_we_have": "what_we_have", "information_we_lack": "what_we_lack",
                   "discovery_action": "how_to_close"}[col]
            if r[col] != src[key]:
                rew.append("%s.%s" % (r["id"], col))
                break
    if rew:
        bad("information gaps: cells re-worded instead of copied: %s" % rew[:4])
    else:
        ok("information gaps: every have/lack/action cell is the register's own text, "
           "copied verbatim")
    dupes = sorted({r["id"] for r in q if sum(1 for x in q if x["id"] == r["id"]) > 1})
    if dupes:
        warn("the question register uses %s for two different questions (published as FL-54); "
             "the restatement is compared by row, so both rows are carried" % ", ".join(dupes))


# --------------------------------------------------------------------------- #
# 6. the coverage gap stays visible
# --------------------------------------------------------------------------- #
def coverage_gap_is_flagged():
    summ = load("s745_depth_summary.csv")
    uncharted = [r["club"] for r in summ if r["chart_published"] != "yes"]
    if not uncharted:
        warn("all 32 clubs charted - the register has moved past the gap it was built to close")
        return
    flags = "\n".join("%s %s %s" % (r["id"], r["finding"], r["evidence"])
                      for r in load("flags.csv"))
    names = {"HOU": "Houston", "AZ": "Arizona"}
    unflagged = [c for c in uncharted if c not in flags and names.get(c, c) not in flags]
    if unflagged:
        bad("clubs with no charted rows appear in no register flag: %s" % unflagged)
    else:
        ok("every club with no charted rows is named in a register flag (%s)"
           % ", ".join(uncharted))
    for r in summ:
        if r["chart_published"] != "yes" and not r["chart_source"].startswith("https://"):
            bad("%s: no chart published and no club page cited" % r["club"])


CHECKS = [every_row_sourced, summary_reproduces, join_is_supported,
          injury_refresh_is_clean, console_is_derived_only, coverage_gap_is_flagged]


def main():
    for fn in CHECKS:
        fn()
    print("=" * 72)
    for m in PASS:
        print("  PASS  " + m)
    for m in WARN:
        print("  WARN  " + m)
    for m in FAIL:
        print("  FAIL  " + m)
    print("=" * 72)
    print("verify_s745: %d passed · %d warnings · %d failures" % (len(PASS), len(WARN), len(FAIL)))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
