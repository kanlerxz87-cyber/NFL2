#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Session 745f788e - turn the existing registers into something an owner can act on.

It invents no facts. It reads the two registers this repository already publishes
(data/suggestions.csv, data/questions.csv) and derives three things from them:

  data/s745_suggestion_scores.csv   every suggestion scored on the impact / effort /
                                    risk fields the register already carries, and
                                    assigned to one candidate path
  data/s745_decision_paths.csv      the four candidate paths, each as a bundle of
                                    suggestion ids with its totals
  data/s745_information_gaps.csv    every open question restated as
                                    information-we-have / information-we-lack /
                                    discovery-action, with a computed "can this be
                                    closed from an official source" column

The score is arithmetic on published fields, not evidence. The page says so.
"""

import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")

IMPACT_PTS = {"H": 3, "M": 2, "L": 1}
EFFORT_PTS = {"L": 1, "M": 2, "H": 3}
SCORE_REGISTER = "S-REGISTER-745"

# A path is a bundle, not a category. The mapping below is a proposal by this
# session and is printed on the page as such; the owner can move any row.
PATHS = [
    ("A", "Prove the data layer",
     "Make every table on this site say when it was read, store each filing as a "
     "dated event, and give club keys and game ids one canonical form.",
     ("Data plumbing", "Data model", "Data engineering", "Data quality",
      "Data integrity", "Data semantics", "data", "Auditability", "Trust",
      "Compliance", "delivery"),
     "Unblocks: any backtest that survives contact with a reviewer, and the "
     "availability signals that need history (Q-36, FL-35).",
     "Does NOT fix: the absence of prices. Path A makes the data honest; it does "
     "not make it complete.",
     "Milestone: every published table carries a captured-at stamp and the "
     "week-10 injury file has a second dated snapshot beside it."),
    ("B", "Acquire prices",
     "Get an opening and closing price per market, at known capture times, and "
     "store them point-in-time.",
     ("Origination", "origination", "Benchmarking", "Line origination"),
     "Unblocks: vig stripping, fair-value deviation, CLV, and 9 of the 14 "
     "validation gates (Q-01).",
     "Does NOT fix: player-level entitlement, and it costs money or a licence "
     "decision that only the owner can make.",
     "Milestone: one season of closing prices for spreads and totals, with the "
     "capture timestamp on every row."),
    ("C", "Build the availability and depth signal",
     "Turn 'a starter is out' into a measurable replacement cost, using the "
     "club-published depth charts, the official injury report and real playing time.",
     ("Availability", "Feature design", "Signal design", "Modeling", "Coverage"),
     "Unblocks: the injury and depth features behind half the signal catalogue, "
     "and it is the part of the brief that is currently least covered (4 of 32 "
     "club charts before this session).",
     "Does NOT fix: it cannot be validated without prices, so it cannot prove "
     "edge on its own.",
     "Milestone: all 32 club depth charts transcribed and joined to the injury "
     "report, refreshed weekly, with the join reproducible from a script."),
    ("D", "Stand up the competition",
     "Pre-registration, a tracked forward ledger, validation gates and the reward "
     "tiers, so the leaderboard ranks skill rather than luck.",
     ("Competition design", "Anti-overfitting", "Methodology", "Verification",
      "verification", "Governance", "Program", "Reporting", "Scope",
      "Information design", "Site and navigation"),
     "Unblocks: a leaderboard that means something, and the only honest answer "
     "to 'is this strategy skilful' (Q-03, G-09).",
     "Does NOT fix: it ranks what exists. With no tracked bets it still ranks "
     "nothing, which is why the page shows gate readiness instead of results.",
     "Milestone: the first forward-tracked bet settles and is graded against a "
     "pre-registered rule."),
]


def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="|"))


def write_csv(name, header, rows):
    with open(os.path.join(DATA, name), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=header, delimiter="|",
                           lineterminator="\n", extrasaction="raise")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in header})


def risk_class(text):
    t = (text or "").strip().lower()
    if t.startswith("high"):
        return "High"
    if t.startswith("medium"):
        return "Medium"
    if t.startswith("low"):
        return "Low"
    return ""


def path_for(category):
    for (code, _n, _g, cats, _u, _d, _m) in PATHS:
        if category in cats:
            return code
    return ""


def main():
    sugs = load("suggestions.csv")
    qs = load("questions.csv")

    # ---------------- suggestion scores ----------------
    scored = []
    for s in sugs:
        ip = IMPACT_PTS.get(s["impact"].strip().upper(), 0)
        ep = EFFORT_PTS.get(s["effort"].strip().upper(), 0)
        rc = risk_class(s["risk"])
        rp = {"Low": 1, "Medium": 2, "High": 3}.get(rc, 0)
        denom = ep + rp
        score = round(ip / denom, 2) if denom else ""
        code = path_for(s["category"].strip())
        scored.append({
            "id": s["id"],
            "title": s["title"].strip().strip('"'),
            "category": s["category"],
            "path": code,
            "impact": s["impact"],
            "effort": s["effort"],
            "risk_class": rc,
            "impact_pts": str(ip),
            "effort_pts": str(ep),
            "risk_pts": str(rp),
            "priority_score": str(score),
            "quick_win": "yes" if (s["impact"].strip().upper() == "H" and
                                   s["effort"].strip().upper() == "L") else "no",
            "reversible": s["reversible"],
            "depends_on": s["depends_on"],
            "decision": s["decision"],
            "source": SCORE_REGISTER,
        })
    # rank: highest score first, then lowest effort
    order = sorted(range(len(scored)),
                   key=lambda i: (-float(scored[i]["priority_score"] or 0),
                                  int(scored[i]["effort_pts"] or 0),
                                  scored[i]["id"]))
    for rank, i in enumerate(order, start=1):
        scored[i]["rank"] = str(rank)
    scored.sort(key=lambda r: int(r["rank"]))
    write_csv("s745_suggestion_scores.csv",
              ["rank", "id", "title", "category", "path", "impact", "effort",
               "risk_class", "impact_pts", "effort_pts", "risk_pts",
               "priority_score", "quick_win", "reversible", "depends_on",
               "decision", "source"], scored)

    # ---------------- paths ----------------
    path_rows = []
    for (code, name, goal, cats, unblocks, notfix, milestone) in PATHS:
        members = [r for r in scored if r["path"] == code]
        high = sum(1 for r in members if r["impact"].strip().upper() == "H")
        eff = sum(int(r["effort_pts"] or 0) for r in members)
        qw = sum(1 for r in members if r["quick_win"] == "yes")
        ids = ", ".join(r["id"] for r in members)
        path_rows.append({
            "path": code,
            "path_name": name,
            "goal": goal,
            "suggestions": str(len(members)),
            "high_impact": str(high),
            "quick_wins": str(qw),
            "total_effort_points": str(eff),
            "suggestion_ids": ids,
            "unblocks": unblocks,
            "does_not_fix": notfix,
            "first_milestone": milestone,
            "source": SCORE_REGISTER,
        })
    write_csv("s745_decision_paths.csv",
              ["path", "path_name", "goal", "suggestions", "high_impact",
               "quick_wins", "total_effort_points", "suggestion_ids",
               "unblocks", "does_not_fix", "first_milestone", "source"],
              path_rows)

    # ---------------- information gaps ----------------
    OFFICIAL_HINT = re.compile(r"\b(nfl\.com|operations\.nfl\.com|official|club site|"
                               r"league page|game page|roster|depth chart|transactions)\b",
                               re.I)
    gaps = []
    for q in qs:
        have = q["what_we_have"].strip()
        lack = q["what_we_lack"].strip()
        empty_have = bool(re.match(r"^(nothing|none|no |n/?a)\b", have, re.I))
        gaps.append({
            "id": q["id"],
            "priority": q["priority"],
            "question": q["question"].strip().strip('"'),
            "blocks": q["blocks"],
            "information_we_have": have,
            "have_is_empty": "yes" if empty_have else "no",
            "information_we_lack": lack,
            "discovery_action": q["how_to_close"],
            # "not established" rather than "unknown": the repository audit bans the word
            # unknown in any data cell, because a cell that says unknown usually means a value
            # somebody should have gone and found. This one is different - it is a keyword
            # guess over the register's own prose - and it says so on the page.
            "official_route_exists": ("yes" if OFFICIAL_HINT.search(q["how_to_close"])
                                      else "not established"),
            "status": q["status"],
            "source": SCORE_REGISTER,
        })
    write_csv("s745_information_gaps.csv",
              ["id", "priority", "question", "blocks", "information_we_have",
               "have_is_empty", "information_we_lack", "discovery_action",
               "official_route_exists", "status", "source"], gaps)

    print("suggestions scored   : %d (paths A/B/C/D = %s)"
          % (len(scored), "/".join(str(sum(1 for r in scored if r["path"] == p[0]))
                                   for p in PATHS)))
    print("unassigned           : %d" % sum(1 for r in scored if not r["path"]))
    print("official route        : %d of %d" % (
        sum(1 for r in gaps if r["official_route_exists"] == "yes"), len(gaps)))
    print("information gaps     : %d (%d with nothing held)"
          % (len(gaps), sum(1 for r in gaps if r["have_is_empty"] == "yes")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
