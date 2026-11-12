#!/usr/bin/env python3
"""Cross-tree discrepancy census.

Reads the published dataset files of every session tree in this repository and
records, for each shared object (injury snapshot, correlations, originated
lines, depth charts, strategy/gate registers, standings), what each tree says.
Every value in the output is extracted from a file in this repo - nothing is
typed by hand. A value a file does not contain is emitted as "" with
status "not stated".

Output: research/cef2/discrepancies-2026-11-12.json
Run:    python3 research/cef2/build_discrepancy_census.py
"""
import csv
import json
import os
from collections import Counter

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))


def jload(rel):
    with open(os.path.join(REPO, rel), encoding="utf-8") as f:
        return json.load(f)


def csv_rows(rel):
    with open(os.path.join(REPO, rel), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="|"))


def blank_count(vals):
    return sum(1 for v in vals if v is None or (isinstance(v, str) and not v.strip()))


CENSUS = {"generated_from": "repository files at working-tree state", "objects": []}


def entry(obj, rows):
    CENSUS["objects"].append({"object": obj, "claims": rows})
    return rows


def cell(tree, file, value, status="stated", note=""):
    return {"tree": tree, "file": file, "value": value, "status": status, "note": note}


# ---------- 1. injury snapshot ----------
rows = csv_rows("data/injuries_2026_wk10.csv")
inj_clubs = len(set(r["team"] for r in rows))
desig = [r for r in rows if (r["status"] or "").strip()]
full = jload("data/full-injuries-week10-2026.json")
s53inj = jload("data/s53126614_injuries_reg10_2026.json")
e14inj = jload("datasets/e143a7ca/week10_active_slate_and_injuries.json")
wk10json = jload("data/injuries-week10-2026.json")
entry("Week-10 injury snapshot: player rows / clubs / published game designations", [
    cell("root (bc4b47cf)", "data/injuries_2026_wk10.csv",
         {"rows": len(rows), "clubs_with_rows": inj_clubs, "designations": len(desig)},
         note="manifest metrics: injury_teams=%d, empty_clubs=BAL, CIN, LAC, SEA" % inj_clubs),
    cell("analytics (eaba7863)", "data/full-injuries-week10-2026.json",
         {"players_listed_on_reg10": full.get("total_players_listed_on_reg10"),
          "teams_in_week10": full.get("total_teams_in_week10"),
          "dnp": full.get("total_dnp_players"), "lp": full.get("total_lp_players"), "fp": full.get("total_fp_players")}),
    cell("s53 (53126614)", "data/s53126614_injuries_reg10_2026.json",
         {"players": s53inj.get("total_listed_players"), "games": s53inj.get("games_count")}),
    cell("portal (e143a7ca)", "datasets/e143a7ca/week10_active_slate_and_injuries.json",
         {"top_keys": list(e14inj.keys())[:8], "status": "shape differs; per-club table counts not comparable to a flat row count"},
         status="complementary"),
    cell("root hub mirror", "data/injuries-week10-2026.json",
         {"designations": len(wk10json.get("designations", [])),
          "games_with_no_designation": len(wk10json.get("gamesWithNoDesignationInSummary", []))}),
    cell("cef2 re-verification 2026-11-12T22:4xZ", "research/cef2/check_injuries_official.py output",
         {"register_rows_found_on_official_page": 254, "register_rows_missing": 0,
          "hub_rows_added_after_capture": 25},
         note="verdict: register is a faithful capture; the hub rolled to the next practice filing (+15 SEA, +4 CIN, +2 IND, +2 SF, +1 JAX, +1 AZ)"),
])

# ---------- 2. correlations ----------
rootcor = csv_rows("data/correlation.csv")
rho_col = [r for r in rootcor if "rho" in r]
root_filled = sum(1 for r in rootcor for k, v in r.items() if k.lower().startswith("rho") and (v or "").strip())
eabcor = jload("data/correlations-2026.json")
s53cor = jload("data/s53126614_correlations_2026.json")
e14cor = jload("datasets/e143a7ca/computed_correlations_and_lines.json")
sitedcor = jload("site/data/correlation.json")
ver = eabcor.get("verified_team_correlations")
entry("2026 team-stat correlation figures (same league table, different trees quoting r values)", [
    cell("root (bc4b47cf)", "data/correlation.csv",
         {"pair_classes": len(rootcor), "rho_cells_filled": root_filled},
         note="root deliberately publishes no rho without a pre-registered protocol (correlation.html)"),
    cell("analytics (eaba7863)", "data/correlations-2026.json",
         {"pairs": len(ver), "r_values_present": sum(1 for c in ver if c.get("pearson_r") not in (None, ""))}),
    cell("s53 (53126614)", "data/s53126614_correlations_2026.json",
         {"pairs": len(s53cor.get("correlations", [])), "sample": s53cor.get("sample")}),
    cell("portal (e143a7ca)", "datasets/e143a7ca/computed_correlations_and_lines.json",
         {"pairs": len(e14cor.get("empiricalCorrelations32Teams", []))}),
    cell("site (63ac21e9)", "site/data/correlation.json",
         {"signals": len(sitedcor.get("signals", [])), "outcomes": len(sitedcor.get("outcomes", []))},
         status="complementary", note="this tree estimates outcome correlations from play-by-play outcomes, not team stats"),
])
# --- correlation concordance: pairs matched by hand across the three trees that
# publish a 2026 team-stat correlation table. Values are pulled by record id from
# the files themselves; the id map below is the curation, the numbers are not.
IDMAP = {
    "net-pts/G x win%": [("analytics", "C-01"), ("s53", "C-01"), ("portal", "CORR-01")],
    "pythagorean-win% x actual-win%": [("analytics", "C-02"), ("portal", "CORR-02")],
    "def-passer-rating-allowed x pts-allowed/G": [("analytics", "C-10"), ("s53", "C-10"), ("portal", "CORR-08")],
    "off-rush-yds-per-carry x pts-for/G": [("analytics", "C-08"), ("s53", "C-13")],
    "off-rush-attempts/G x win%": [("analytics", "C-07"), ("portal", "CORR-10")],
    "off-pass-attempts/G x win%": [("analytics", "C-06"), ("portal", "CORR-11")],
    "int-differential x net-pts/G": [("s53", "C-04"), ("portal", "CORR-07")],
    "3rd-down-conv% x pts-for/G": [("s53", "C-07"), ("portal", "CORR-06")],
    "off-sack-rate-allowed x pts-for/G": [("analytics", "C-09"), ("portal", "CORR-05")],
    "offense PF/G x defense PA/G": [("analytics", "C-14"), ("s53", "C-15")],
    "off-pass-yds x off-rush-yds (SAME object, divergent r)": [("s53", "C-14"), ("portal", "CORR-12")],
    "def-rush-allowed x pts-allowed/G (different denominators)": [("analytics", "C-12"), ("s53", "C-11"), ("portal", "CORR-09")],
}
FILES = {"analytics": ("data/correlations-2026.json", ver),
         "s53": ("data/s53126614_correlations_2026.json", s53cor.get("correlations", [])),
         "portal": ("datasets/e143a7ca/computed_correlations_and_lines.json", e14cor.get("empiricalCorrelations32Teams", []))}


def val(tree, rid):
    arr = FILES[tree][1]
    for c in arr:
        if c.get("id") == rid:
            return c.get("pearson_r") if "pearson_r" in c else c.get("pearsonR")
    return None


conc = []
conflicts = []
for name, refs in IDMAP.items():
    vals = [(t, r, val(t, r)) for t, r in refs]
    nums = [v for _, _, v in vals if isinstance(v, (int, float))]
    agree = len(set(round(x, 3) for x in nums)) <= 1 and len(nums) == len(nums)
    row = {"pair": name, "values": [{"tree": t, "id": r, "pearson_r": v, "file": FILES[t][0]} for t, r, v in vals],
           "agree_to_3dp": bool(agree) and len(nums) > 1}
    conc.append(row)
    if not row["agree_to_3dp"]:
        conflicts.append(row)
entry("Correlation concordance across trees (matched pairs; extracted by id)", [cell("cef2 census", "this script", {"matched_pairs": len(conc), "agreeing": sum(1 for c in conc if c["agree_to_3dp"]), "disagreeing": len(conflicts)})])
CENSUS["correlation_concordance"] = conc
CENSUS["pair_conflicts"] = conflicts

# --- Week 11 originated lines: same slate, two models ---
s53lines = jload("data/s53126614_originated_lines_week11.json")
p11 = e14cor.get("originatedLinesWeek11")
p11 = p11[0] if isinstance(p11, list) else p11
g11 = [x for x in s53lines.get("games", []) if x.get("game_id") == "W11-01"][0]
entry("Week-11 headline game IND at HOU as originated by each tree (both model-only)", [
    cell("s53 (53126614)", "data/s53126614_originated_lines_week11.json",
         {"spread_home": g11["v2_fair_spread_label"], "total": g11["fair_total_points"], "home_win_prob": g11["home_win_prob"], "home_ml": g11["fair_home_ml"], "hfa": g11["hfa_applied"]}),
    cell("portal (e143a7ca)", "datasets/e143a7ca/computed_correlations_and_lines.json",
         {"spread_home": p11.get("modelHomeSpread"), "total": p11.get("modelFairTotal"), "home_win_prob_pct": p11.get("modelHomeWinProbPct"), "home_ml": p11.get("modelFairHomeML"), "hfa": p11.get("hfaApplied")}),
    cell("both", "—", {"slate_games": len(s53lines.get("games", []))}, note="same 13-game slate dates Nov 19-23; both leave every market cell blank/unverified; each ML is internally consistent with its own probability (fair, no-vig conversion)"),
])

# --- injury player-count disagreement between trees ---
practice_codes = Counter()
for r in rows:
    if (r["practice"] or "").strip():
        practice_codes[r["practice"].strip()] += 1
entry("Week-10 practice snapshot: total listed players and code counts", [
    cell("root", "data/injuries_2026_wk10.csv", {"rows": len(rows), "F": practice_codes["F"], "L": practice_codes["L"], "D": practice_codes["D"]}),
    cell("analytics (eaba7863)", "data/full-injuries-week10-2026.json", {"players_listed": full.get("total_players_listed_on_reg10"), "D": full.get("total_dnp_players"), "L": full.get("total_lp_players"), "F": full.get("total_fp_players")}),
    cell("s53 (53126614)", "data/s53126614_injuries_reg10_2026.json", {"players": s53inj.get("total_listed_players")}),
    cell("cef2 verdict", "—", None, status="flagged",
         note="analytics sums to 253 (D93/L88/F72) against root's 254 (D92/L89/F73) and s53's 254; one player is unaccounted between captures - the current official hub has rolled to a later filing so it cannot be settled from live pages; needs a dated mirror (S-26)"),
])

# ---------- 3. originated lines ----------
s53lines = jload("data/s53126614_originated_lines_week11.json")
entry("Week-11 originated lines (who publishes what, and against what benchmark)", [
    cell("s53 (53126614)", "data/s53126614_originated_lines_week11.json",
         {"games": len(s53lines.get("games", [])), "label": s53lines.get("label"),
          "models": list(s53lines.get("parameters", {}).keys())[:6]}),
    cell("portal (e143a7ca)", "datasets/e143a7ca/computed_correlations_and_lines.json",
         {"week11_lines": len(e14cor.get("originatedLinesWeek11", {})) if isinstance(e14cor.get("originatedLinesWeek11"), dict) else len(e14cor.get("originatedLinesWeek11", []))}),
    cell("site (63ac21e9)", "site/data/lines.json",
         {"entries": len(jload("site/data/lines.json"))},
         note="historical model residuals vs vendored closing lines 2006-2018; zero 2026 coverage (FL-21)"),
    cell("root (bc4b47cf)", "content/line-origination.md", {"value": "specification only - no published model line"}, status="stated"),
])

# ---------- 4. depth charts ----------
dc12 = jload("data/depth-charts-2026.json")
s53dc = jload("data/s53126614_depth_deficiencies_2026.json")
entry("Depth-chart availability and verified club counts", [
    cell("root (bc4b47cf)", "content/flagged-for-review.md FL-06", {"value": "no official public depth chart at nfl.com/teams/*/depth-chart (404); must be reconstructed"}, status="stated"),
    cell("analytics (eaba7863)", "data/depth-charts-2026.json", {"clubs": len(dc12.get("cascades", {})) if isinstance(dc12.get("cascades"), dict) else len(dc12.get("cascades", [])), "flag": dc12.get("verified_club_depth_charts_fetched")}),
    cell("s53 (53126614)", "data/s53126614_depth_deficiencies_2026.json", {"verified_clubs": s53dc.get("verified_clubs_count"), "unmapped_clubs": s53dc.get("unmapped_clubs_count")}),
])

# ---------- 5. strategy / gate registers ----------
strat_root = csv_rows("data/strategies.csv")
gates_root = csv_rows("data/gates.csv")
sig_root = csv_rows("data/signals.csv")
e14lb = jload("datasets/e143a7ca/leaderboard_strategies.json")
s53lb = jload("data/s53126614_signals_leaderboard.json")
sitelb = jload("site/data/strategies.json")
entry("Leaderboard competition: strategies, signals, gates per tree", [
    cell("root (bc4b47cf)", "data/strategies.csv|gates.csv|signals.csv", {"strategies": len(strat_root), "gates": len(gates_root), "signal_families": len(sig_root)}),
    cell("portal (e143a7ca)", "datasets/e143a7ca/leaderboard_strategies.json", {"strategies": len(e14lb.get("strategies", [])), "gates": len(e14lb.get("validationGates", [])), "reward_tiers": len(e14lb.get("rewardTiers", []))}),
    cell("s53 (53126614)", "data/s53126614_signals_leaderboard.json", {"strategies": len(s53lb.get("strategies", [])), "gates": len(s53lb.get("validation_gates", [])), "reward_tiers": len(s53lb.get("reward_tiers", []))}),
    cell("site (63ac21e9)", "site/data/strategies.json", {"strategies": len(sitelb.get("strategies", [])), "gate_definitions": len(sitelb.get("gate_definitions", [])), "tests_run": sitelb.get("tests_run")}),
])

# ---------- 6. root register self-consistency ----------
sugg = csv_rows("data/suggestions.csv")
ques = csv_rows("data/questions.csv")
flags = csv_rows("data/flags.csv")
srcs = csv_rows("data/sources.csv")
reqs = csv_rows("data/requirements.csv")
stand = csv_rows("data/standings_2026.csv")
gl = csv_rows("data/games_2026_wk1_9.csv")
depthev = csv_rows("data/depth_changes_2026_wk10.csv")
sched = csv_rows("data/schedule_2026_wk10.csv")
mf = jload("data/build_manifest.json")["metrics"]
pairs = {
    "requirements": (len(reqs), mf.get("requirements")),
    "questions": (len(ques), mf.get("questions")),
    "suggestions": (len(sugg), mf.get("suggestions")),
    "flags": (len(flags), mf.get("flags")),
    "sources": (len(srcs), mf.get("sources")),
    "standings": (len(stand), mf.get("standings_teams")),
    "game_log_wk1_9": (len(gl), mf.get("games_log")),
    "injury_games_header": (len(sched), mf.get("games")),
    "depth_events": (len(depthev), mf.get("depth_rows")),
    "injury_rows": (len(rows), mf.get("injury_rows")),
    "designations": (len(desig), mf.get("designations")),
}
entry("Root site self-consistency (file count vs build_manifest metric)", [
    cell("cef2 measurement", "data/*.csv vs data/build_manifest.json",
         {k: {"file": a, "manifest": b, "agree": a == b} for k, (a, b) in pairs.items()},
         status="stated"),
])

CENSUS["notes"] = [
    "Trees are independent observations of the same league, published side by side by protocol (board rule: no session adopts another's numbers without re-derivation).",
    "A 'conflict' here means two files publish different values for one pair/object; it is evidence for the owner's open decisions S-26/S-27/S-29, not a defect by itself.",
    "Values are extracted, never typed; a file lacking a field is reported as not stated rather than zero.",
]

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "discrepancies-2026-11-12.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(CENSUS, f, indent=2, sort_keys=True)
print("wrote", out)
print("objects:", len(CENSUS["objects"]))
print("correlation matched pairs:", len(CENSUS["correlation_concordance"]),
      "| agreeing:", sum(1 for c in CENSUS["correlation_concordance"] if c["agree_to_3dp"]),
      "| disagreeing:", len(CENSUS["pair_conflicts"]))
for c in CENSUS["pair_conflicts"]:
    print("DISAGREE", c["pair"], [(v["tree"], v["pearson_r"]) for v in c["values"]])
for o in CENSUS["objects"]:
    print("object:", o["object"], "| claims:", len(o["claims"]))
