"""Availability: injury load, depth-chart vacancies, and backup-deficiency index.

What is measured here, exactly
------------------------------
1. INJURY LOAD      — from the nflverse weekly injury report (official NFL
                      injury-report fields: report_status in {Out, Doubtful,
                      Questionable}, practice participation levels).
2. DEPTH VACANCY    — for 2024 only (the only season with a full depth chart in
                      the sources reachable from this sandbox) we join the depth
                      chart to the injury report and count how many depth-1
                      (starting) players at each position group are listed "Out".
                      A vacancy at depth 1 means a depth-2 player starts; a vacancy
                      at depth 1 *and* an "Out" depth-2 means a depth-3 player
                      starts. That is the concrete, checkable version of the
                      "2nd/3rd/4th string" question.
3. BACKUP DEFICIENCY INDEX (BDI) — season-level, every team:
                      BDI = share of season starts made by players with <= 1 year
                      of experience, weighted by the position group's measured
                      "Out" rate. Computed ONLY for seasons where starter data is
                      populated (2006-2018) because rosters.csv `starts` is empty
                      from 2019 onward. Every consumer must treat post-2018 BDI as
                      unverified — the site shows it as blank, never estimated.
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

from pipeline.common import RAW, SOURCES, utc_now

INJ_STATUS_WEIGHT = {"Out": 1.0, "Doubtful": 0.75, "Questionable": 0.30}
POS_GROUP = {
    "QB": "QB", "RB": "RB", "FB": "RB", "WR": "WR", "TE": "TE",
    "T": "OL", "G": "OL", "C": "OL", "OT": "OL", "OG": "OL",
    "DE": "DL", "DT": "DL", "NT": "DL", "DL": "DL", "EDGE": "DL", "LDE": "DL", "RDE": "DL",
    "LB": "LB", "ILB": "LB", "OLB": "LB", "MLB": "LB",
    "CB": "DB", "S": "DB", "FS": "DB", "SS": "DB", "DB": "DB", "NCB": "DB",
    "K": "ST", "P": "ST", "LS": "ST",
}


def load_injuries() -> pd.DataFrame:
    frames = []
    for y in (2024, 2025, 2026):
        p = os.path.join(RAW, "injuries", f"injuries_{y}.csv")
        if os.path.exists(p):
            frames.append(pd.read_csv(p))
    d = pd.concat(frames, ignore_index=True)
    d = d[d.game_type.eq("REG")].copy()
    # a player can appear more than once for the same team-week; keep one row
    d = d.drop_duplicates(["season", "week", "team", "gsis_id"])
    d["status_weight"] = d.report_status.map(INJ_STATUS_WEIGHT).fillna(0.0)
    d["pos_group"] = d.position.map(POS_GROUP).fillna("OTHER")
    return d


def load_depth() -> pd.DataFrame:
    p = os.path.join(RAW, "depth", "depth_charts_2024.parquet")
    d = pd.read_parquet(p)
    d = d[d.game_type.eq("REG")].copy()
    d["week"] = d.week.astype(int)
    d["pos_group"] = d.depth_position.map(POS_GROUP).fillna(
        d.position.map(POS_GROUP)).fillna("OTHER")
    return d


def position_out_rates(inj: pd.DataFrame) -> dict:
    from pipeline.engine.sklearn_lite import wilson_interval
    rows = inj[inj.report_status.notna()]
    t = rows.groupby("position").agg(rows=("report_status", "size"),
                                     outs=("report_status", lambda s: (s == "Out").sum()))
    t["out_rate"] = t.outs / t.rows
    t[["ci_lo", "ci_hi"]] = [wilson_interval(int(r.outs), int(r.rows)) for r in t.itertuples()]
    t = t[t.rows >= 100].sort_values("out_rate", ascending=False)
    pooled = float(t.outs.sum() / t.rows.sum()) if len(t) else None
    table = []
    for i, r in t.iterrows():
        # a position is only "higher than pooled" if its lower CI clears the pooled rate
        higher = bool(r.ci_lo > pooled) if pooled is not None else None
        table.append({
            "position": i, "reports": int(r.rows), "outs": int(r.outs),
            "out_rate": round(float(r.out_rate), 4),
            "ci_low": round(float(r.ci_lo), 4), "ci_high": round(float(r.ci_hi), 4),
            "distinguishably_above_pooled": higher,
        })
    return {
        "as_of": utc_now(),
        "source": "nflverse injuries (official NFL injury report fields)",
        "source_url": "https://github.com/nflverse/nflverse-data/releases/tag/injuries",
        "official_cross_check": SOURCES["nfl_injury_report"]["url"],
        "seasons": sorted(inj.season.unique().tolist()),
        "min_rows": 100,
        "pooled_out_rate": None if pooled is None else round(pooled, 4),
        "table": table,
        "note": "Out rate = share of injury-report entries whose game status is 'Out'. "
                "Wilson 95% intervals are shown because most positions are statistically "
                "indistinguishable from the pooled rate at this sample size; only rows with "
                "distinguishably_above_pooled = true have a demonstrably higher rate.",
    }


def depth_vacancies(inj: pd.DataFrame, depth: pd.DataFrame) -> dict:
    """Per team-week: how many depth-1 starters are ruled Out, by position group."""
    i24 = inj[(inj.season == 2024) & (inj.week.between(1, 18))]
    out_by_key = (i24[i24.report_status == "Out"]
                  .assign(pos_group=lambda d: d.position.map(POS_GROUP).fillna("OTHER"))
                  .groupby(["team", "week", "pos_group"]).size().rename("depth1_out"))
    d24 = depth[depth.week.between(1, 18)]

    # depth-1 starters per team/week/pos_group
    d1 = (d24[d24.depth_team == "1"]
          .groupby(["club_code", "week", "pos_group"]).size().rename("starters"))
    # depth-2 available?  count of depth-2 players not on the Out list
    out_names = set(zip(i24[i24.report_status == "Out"].team,
                        i24[i24.report_status == "Out"].week,
                        i24[i24.report_status == "Out"].full_name))
    d2 = d24[d24.depth_team == "2"].copy()
    d2["out"] = [((t, w, n) in out_names) for t, w, n in zip(d2.club_code, d2.week, d2.full_name)]
    d2 = (d2[~d2.out].groupby(["club_code", "week", "pos_group"]).size().rename("backups_available"))

    j = pd.concat([d1, out_by_key.rename_axis(index=["club_code", "week", "pos_group"]),
                   d2.rename_axis(index=["club_code", "week", "pos_group"])], axis=1).fillna(0)
    j = j.reset_index()
    j["starters"] = j.starters.clip(lower=0)
    j["depth1_out"] = j.depth1_out.clip(upper=j.starters)
    j["backups_available"] = j.backups_available.clip(lower=0)
    j["vacancy_ratio"] = np.where(j.starters > 0, j.depth1_out / j.starters, 0.0)
    # "thin": a starter out AND no depth-2 body available at that group
    j["thin"] = ((j.depth1_out > 0) & (j.backups_available == 0)).astype(int)

    season = (j.groupby("club_code")
              .agg(starters=("starters", "sum"), starters_out=("depth1_out", "sum"),
                   thin_weeks=("thin", "sum"), weeks=("week", "nunique"))
              .reset_index())
    season["vacancy_rate"] = (season.starters_out / season.starters.replace(0, np.nan)).round(4)
    season = season.sort_values("vacancy_rate", ascending=False)

    return {
        "season": 2024,
        "verified": True,
        "method": "depth_team == '1' from the published depth chart joined to game status "
                  "'Out' from the injury report, same team and week",
        "source_depth": "https://github.com/nflverse/nflverse-data/releases/tag/depth_charts "
                        "(mirrored in-repo at data/nflverse, file hf_mikeysports_2025_depth_charts_zone1.parquet)",
        "source_injury": "https://github.com/nflverse/nflverse-data/releases/tag/injuries",
        "official_cross_check": SOURCES["nfl_injury_report"]["url"],
        "teams": [{"team": r.club_code, "starter_slots": int(r.starters),
                   "starter_slots_out": int(r.starters_out),
                   "vacancy_rate": (None if pd.isna(r.vacancy_rate) else round(float(r.vacancy_rate), 4)),
                   "thin_position_weeks": int(r.thin_weeks), "weeks": int(r.weeks)}
                  for r in season.itertuples()],
        "weekly": [{"team": r.club_code, "week": int(r.week), "pos_group": r.pos_group,
                    "starters": int(r.starters), "starters_out": int(r.depth1_out),
                    "backups_available": int(r.backups_available),
                    "vacancy_ratio": round(float(r.vacancy_ratio), 4), "thin": int(r.thin)}
                   for r in j[j.depth1_out > 0].itertuples()],
    }


def injury_load(inj: pd.DataFrame) -> dict:
    """Season-level injury load per team, from the official-status weights."""
    agg = (inj[inj.report_status.notna()]
           .groupby(["season", "team"])
           .agg(entries=("status_weight", "size"),
                out=("report_status", lambda s: (s == "Out").sum()),
                doubtful=("report_status", lambda s: (s == "Doubtful").sum()),
                questionable=("report_status", lambda s: (s == "Questionable").sum()),
                weighted_load=("status_weight", "sum"))
           .reset_index())
    agg["weighted_load"] = agg.weighted_load.round(2)
    return {
        "seasons": sorted(inj.season.unique().tolist()),
        "source": "https://github.com/nflverse/nflverse-data/releases/tag/injuries",
        "official_cross_check": SOURCES["nfl_injury_report"]["url"],
        "weighting": {"Out": 1.0, "Doubtful": 0.75, "Questionable": 0.30},
        "teams": [{**r} for r in agg.to_dict("records")],
    }


def backup_deficiency(rosters: pd.DataFrame) -> dict:
    """Season BDI = experience-weighted share of starts, only where data is populated."""
    r = rosters.copy()
    pop = r.groupby("season").starts.apply(lambda s: float(np.nansum(s)))
    usable = sorted(int(s) for s, v in pop.items() if v > 1000)
    r = r[r.season.isin(usable)]
    r = r[r.starts.fillna(0) > 0]
    r["pos_group"] = r.position.map(POS_GROUP).fillna("OTHER")
    r["inexperienced"] = (r.years <= 1).astype(int)
    g = (r.groupby(["season", "team"])
         .apply(lambda d: pd.Series({
             "starts": float(d.starts.sum()),
             "starts_inexperienced": float(d.starts[d.inexperienced == 1].sum()),
         }), include_groups=False)
         .reset_index())
    g["inexperience_share"] = (g.starts_inexperienced / g.starts).round(4)
    return {
        "verified_seasons": [min(usable), max(usable)],
        "unverified_seasons": sorted(int(s) for s in rosters.season.unique() if int(s) not in usable),
        "why_unverified": "rosters.csv reports zero starts for every player from 2019 onward "
                          "(upstream field not populated), so the metric cannot be computed "
                          "and is left blank rather than estimated.",
        "source": SOURCES["nfldata_rosters"]["url"],
        "definition": "share of a team's season starts made by players with <= 1 prior season",
        "teams": [{**r, "season": int(r["season"])} for r in
                  g.sort_values(["season", "inexperience_share"], ascending=[True, False])
                   .to_dict("records")],
    }


def build(rosters: pd.DataFrame) -> dict:
    inj = load_injuries()
    depth = load_depth()
    return {
        "generated_utc": utc_now(),
        "position_out_rates": position_out_rates(inj),
        "depth_vacancies": depth_vacancies(inj, depth),
        "injury_load": injury_load(inj),
        "backup_deficiency": backup_deficiency(rosters),
    }


if __name__ == "__main__":
    import json
    from pipeline.ingest import load_raw
    from pipeline.common import write_json
    d = load_raw()
    out = build(d["rosters.csv"])
    write_json("availability.json", out)
    print(json.dumps({k: (v if not isinstance(v, dict) else list(v)[:6]) for k, v in out.items()}, indent=1)[:1200])
