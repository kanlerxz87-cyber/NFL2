"""Build every artefact the site needs.

Run from the repository root:  python3 -m pipeline.build

Order matters: audit -> backtest -> calibration -> strategies -> luck -> correlation
-> props -> lines -> availability -> provenance -> site index. Every artefact carries
its own generated timestamp, its source list and a verified/unverified marker.
"""
from __future__ import annotations

import json
import os

import pandas as pd

from pipeline.common import OUT, DOCS_OUT, SOURCES, UPSTREAM, clean, sha256, utc_now, write_json, RAW
from pipeline.ingest import load_raw, audit
from pipeline.engine import backtest, calibration, strategies, luck, correlation, props, lines, availability


def _legs_for_luck(df: pd.DataFrame) -> tuple[list[dict], dict[str, pd.DataFrame]]:
    hold = df[df.season.isin(strategies.HOLDOUT_SEASONS)]
    defs = strategies.definitions()
    legs = {d["id"]: strategies.evaluate_rule(hold, d) for d in defs}
    return defs, legs


def build() -> dict:
    print("[1/9] ingesting + integrity audit")
    raw = load_raw()
    games = raw["games.csv"]
    aud = audit()
    write_json("audit.json", aud)

    print("[2/9] walk-forward backtest")
    bt = backtest.build(games)
    os.makedirs(os.path.join(os.path.dirname(OUT), "..", "pipeline", "out"), exist_ok=True)
    outdir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pipeline", "out")
    os.makedirs(outdir, exist_ok=True)
    bt.to_csv(os.path.join(outdir, "backtest.csv"), index=False)

    print("[3/9] calibration")
    cal = calibration.build(bt)
    write_json("calibration.json", cal)

    print("[4/9] strategy library + gates")
    rep = strategies.full_report(bt)
    rep["generated_utc"] = utc_now()
    rep["gate_definitions"] = {
        "G1_sample": f">= {strategies.MIN_LEGS} settled legs",
        "G2_statistical": "Wilson 95% lower bound on hit rate > break-even rate",
        "G3_economic": f"flat-stake ROI >= {strategies.ROI_FLOOR*100:.1f}%",
        "G4_stability": "profitable in >= 2/3 of holdout seasons",
        "G5_multiplicity": f"one-sided p < 0.05 / {strategies.BONFERRONI_TESTS} (Bonferroni)",
        "G6_skill": f"z vs coin-flip >= {strategies.Z_FLOOR}",
        "G7_provenance": "every input verified in provenance.json",
    }
    rep["reward_rules"] = {
        "idea": "Leaderboard with rewards so the best strategies surface on merit.",
        "points_formula": "points = ROI x 100 x sqrt(legs) x stability_factor - drawdown_penalty",
        "stability_factor": "profitable_seasons / seasons",
        "drawdown_penalty": "|max_drawdown| / 20",
        "payout_tiers": [
            {"tier": "Tier 1 (only if CERTIFIED)", "reward": "full allocation", "requires": "all 7 gates"},
            {"tier": "Tier 2 (research)", "reward": "paper-trading only", "requires": "G1-G3 pass, G4-G6 fail"},
            {"tier": "Tier 3 (rejected)", "reward": "no allocation, retained for learning", "requires": "G1 or G2 fail"},
        ],
        "note": "No strategy may be funded from a tier-2 or tier-3 slot regardless of its "
                "backtest ROI; this is the rule that stops lucky streaks receiving capital.",
    }
    write_json("strategies.json", rep)

    print("[5/9] luck / skill decomposition")
    defs, legs = _legs_for_luck(bt)
    lk = luck.decompose(defs, legs)
    lk["generated_utc"] = utc_now()
    write_json("luck.json", lk)

    print("[6/9] correlation + parlay maths")
    cor = correlation.build(bt)
    cor["generated_utc"] = utc_now()
    write_json("correlation.json", cor)

    print("[7/9] props + slate structure")
    pr = props.build(bt)
    pr["generated_utc"] = utc_now()
    write_json("props.json", pr)

    print("[8/9] originating lines for the current slate")
    ln = lines.current_slate(games)
    ln["ratings"] = lines.ratings_table(games, int(games[games.result.isna()].season.min()), 10)
    ln["generated_utc"] = utc_now()
    write_json("lines.json", ln)

    print("[9/9] availability + provenance")
    av = availability.build(raw["rosters.csv"])
    av["generated_utc"] = utc_now()
    write_json("availability.json", av)

    prov = _provenance()
    write_json("provenance.json", prov)

    index = {
        "generated_utc": utc_now(),
        "upstream_commit": UPSTREAM["commit"],
        "datasets": {
            "audit.json": "integrity audit, file hashes and irregularities",
            "calibration.json": "model accuracy versus the closing line",
            "strategies.json": "strategy library, validation gates, leaderboard, rewards",
            "luck.json": "variance, split-half and persistence tests",
            "correlation.json": "measured correlations and parlay pricing",
            "props.json": "player-prop scope, slate structure, parlay hold",
            "lines.json": "our own spread/total/moneyline for the upcoming slate",
            "availability.json": "injury load, depth vacancies, backup deficiency",
            "provenance.json": "every dataset, its source URL, hash and verification status",
        },
    }
    write_json("index.json", index)
    print("done ->", OUT)
    return index


def _provenance() -> dict:
    files = []
    for name in ("games.csv", "rosters.csv", "teams.csv", "officials.csv", "win_totals.csv",
                 "closing_lines.csv", "initial_lines.csv", "sc_lines.csv", "standings.csv"):
        p = os.path.join(RAW, name)
        if os.path.exists(p):
            files.append({"file": name, "sha256": sha256(p), "bytes": os.path.getsize(p),
                          "url": "https://github.com/leesharpe/nfldata/blob/master/data/" + name,
                          "verified": True})
    for y in (2024, 2025, 2026):
        p = os.path.join(RAW, "injuries", f"injuries_{y}.csv")
        if os.path.exists(p):
            files.append({"file": f"injuries/injuries_{y}.csv", "sha256": sha256(p),
                          "bytes": os.path.getsize(p),
                          "url": "https://github.com/nflverse/nflverse-data/releases/tag/injuries",
                          "mirror": "https://github.com/Beexly/Sports/blob/main/data/nflverse/",
                          "verified": y != 2026,
                          "note": "2026 mirror lags the official page by one week; official "
                                  "cross-check at https://www.nfl.com/injuries/" if y == 2026 else None})
    p = os.path.join(RAW, "depth", "depth_charts_2024.parquet")
    if os.path.exists(p):
        files.append({"file": "depth/depth_charts_2024.parquet", "sha256": sha256(p),
                      "bytes": os.path.getsize(p),
                      "url": "https://github.com/nflverse/nflverse-data/releases/tag/depth_charts",
                      "mirror": "https://github.com/Beexly/Sports/blob/main/data/nflverse/",
                      "verified": True})
    p = os.path.join(RAW, "dfs", "DKSalaries_week9_main_2026-11-08.csv")
    if os.path.exists(p):
        files.append({"file": "dfs/DKSalaries_week9_main_2026-11-08.csv", "sha256": sha256(p),
                      "bytes": os.path.getsize(p),
                      "url": "DraftKings salary export (public DFS download)",
                      "verified": True,
                      "note": "Book's own export; availability flags are the book's, not the NFL's."})
    return {
        "generated_utc": utc_now(),
        "upstream": UPSTREAM,
        "official_sources": SOURCES,
        "files": files,
        "unavailable": [
            {"dataset": "player-prop line history", "status": "UNVERIFIED / unavailable",
             "why": "no licensed odds archive reachable from this environment"},
            {"dataset": "snap counts", "status": "unavailable",
             "why": "published only as release assets above the API size limit"},
            {"dataset": "depth charts for seasons other than 2024", "status": "unavailable",
             "why": "the only reachable mirror carries 2024"},
            {"dataset": "official NFL live injury JSON for all 32 teams", "status": "partial",
             "why": "official page text was captured for the current week but the machine "
                    "endpoint is blocked; weekly injury CSVs are used instead"},
        ],
    }


if __name__ == "__main__":
    idx = build()
    print(json.dumps(idx, indent=1))
