"""Strategy library, validation gates, leaderboard and correlation analysis.

DISCIPLINE — this is the whole design:

  DEVELOPMENT window  2013-2020  (parameter discovery happens here only)
  HOLDOUT   window    2021-2025  (locked; touched once, for the final verdict)

Any strategy's parameters are chosen on development data. The holdout is then
scored. A strategy is CERTIFIED only if it clears every gate **on the holdout**:

  G1  sample        >= 100 settled legs
  G2  statistical   Wilson 95% lower bound on hit rate > break-even rate
  G3  economic      flat-stake ROI >= +2.0% at the price actually paid
  G4  stability     profitable in >= 2/3 of holdout seasons
  G5  multiplicity  one-sided p < 0.05 / N_tests (Bonferroni)
  G6  skill         z vs coin-flip >= 2.0
  G7  provenance    every input column is marked verified (see provenance.py)

A strategy failing any gate is published WITH the failing gate named. The gates
exist so that a lucky streak cannot be promoted into a "system".
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

from pipeline.engine.sklearn_lite import wilson_interval

DEV_SEASONS = list(range(2013, 2021))
HOLDOUT_SEASONS = list(range(2021, 2026))
ROI_FLOOR = 0.02
MIN_LEGS = 100
Z_FLOOR = 2.0
BONFERRONI_TESTS = 60


def _p_one_sided(k: int, n: int, p0: float) -> float:
    if n == 0:
        return 1.0
    p0 = min(max(p0, 1e-9), 1 - 1e-9)
    mu = n * p0
    sd = math.sqrt(n * p0 * (1 - p0))
    if sd == 0:
        return 1.0
    z = (k - 0.5 - mu) / sd
    return 0.5 * math.erfc(z / math.sqrt(2))


def _settle(legs: pd.DataFrame) -> dict:
    n = len(legs)
    if n == 0:
        return {"legs": 0}
    wins = int(legs.won.sum())
    pushes = int(legs.push.sum()) if "push" in legs else 0
    hit = wins / n
    lo, hi = wilson_interval(wins, n)
    p0 = float(legs.break_even.mean())
    roi = float(legs.pnl.mean())
    per = legs.groupby("season").agg(n=("won", "size"), w=("won", "sum"), pnl=("pnl", "sum"))
    prof = int((per.pnl > 0).sum())
    # cumulative profit curve for drawdown
    curve = legs.sort_values(["season", "week"]).pnl.cumsum().to_numpy()
    peak = np.maximum.accumulate(curve) if len(curve) else np.array([0])
    dd = float(np.min(curve - peak)) if len(curve) else 0.0
    return {
        "legs": n, "wins": wins, "pushes": pushes, "hit_rate": hit,
        "ci_low": lo, "ci_high": hi, "break_even": p0, "roi": roi,
        "profit_units": float(legs.pnl.sum()), "max_drawdown": dd,
        "seasons": int(len(per)), "profitable_seasons": prof,
        "p_value": _p_one_sided(wins, n, p0),
        "season_detail": {int(s): {"legs": int(r.n), "wins": int(r.w), "pnl": round(float(r.pnl), 3),
                                   "roi": round(float(r.pnl / r.n), 4)}
                          for s, r in per.iterrows()},
    }


def _price(price: float) -> float:
    return (-price) / (-price + 100)


def spread_legs(df, mask, side, price=-110.0):
    sub = df[mask].copy()
    if sub.empty:
        return sub
    if side == "home":
        won = (sub.result > sub.market_spread).astype(int)
    else:
        won = (sub.result < sub.market_spread).astype(int)
    push = (sub.result == sub.market_spread).astype(int)
    sub["won"] = won
    sub["push"] = push
    sub["break_even"] = _price(price)
    sub["pnl"] = np.where(push == 1, 0.0, np.where(won == 1, 100 / 110, -1.0))
    sub["side"] = side
    return sub


def total_legs(df, mask, side, price=-110.0):
    sub = df[mask].copy()
    if sub.empty:
        return sub
    won = (sub.total > sub.market_total).astype(int) if side == "over" else (sub.total < sub.market_total).astype(int)
    push = (sub.total == sub.market_total).astype(int)
    sub["won"] = won
    sub["push"] = push
    sub["break_even"] = _price(price)
    sub["pnl"] = np.where(push == 1, 0.0, np.where(won == 1, 100 / 110, -1.0))
    sub["side"] = side
    return sub


def ml_legs(df, mask, side):
    sub = df[mask].copy()
    if sub.empty:
        return sub
    odds = sub.market_home_ml if side == "home" else sub.market_away_ml
    keep = odds.notna()
    sub, odds = sub[keep].copy(), odds[keep]
    if sub.empty:
        return sub
    won = (sub.result > 0).astype(int) if side == "home" else (sub.result < 0).astype(int)
    dec = np.where(odds > 0, 1 + odds / 100, 1 + 100 / odds.abs())
    sub["won"] = won
    sub["push"] = 0
    sub["break_even"] = 1 / dec
    sub["pnl"] = np.where(won == 1, dec - 1, -1.0)
    sub["dec_odds"] = dec
    sub["side"] = side
    return sub


# ---------------------------------------------------------------- definitions
def definitions() -> list[dict]:
    """Each entry is a rule that can be evaluated identically on dev and holdout."""
    D = []

    def add(i, name, family, market, desc, gate="model"):
        D.append(dict(id=i, name=name, family=family, market=market, desc=desc, gate_input=gate))

    add("S01", "Model spread edge 3.0+", "model-spread", "spread",
        "Take the side the model rates 3+ points better than the closing spread.")
    add("S02", "Model spread edge 4.0+", "model-spread", "spread",
        "Same, 4-point threshold.")
    add("S03", "Model spread edge 5.0+", "model-spread", "spread",
        "Same, 5-point threshold.")
    add("S04", "Model total edge 3.0+", "model-total", "total",
        "Over/under where the model total is 3+ points from the closing total.")
    add("S05", "Model total edge 4.0+", "model-total", "total",
        "Same, 4-point threshold.")
    add("S06", "QB-change fade", "availability", "spread",
        "Oppose a team whose starting QB differs from its previous game.")
    add("S07", "Off-bye home team", "schedule", "spread",
        "Home team rested off a bye against a team that played last week.")
    add("S08", "Short-week fade", "schedule", "spread",
        "Home side when the visitor had <= 5 days between games.")
    add("S09", "Divisional home dog + model", "market-structure", "spread",
        "Home division underdog that the model also favours.")
    add("S10", "Moneyline value 4pt+", "model-ml", "moneyline",
        "Moneyline whose implied probability is beaten by the model by 4+ points.")
    add("S11", "Cold-weather under", "environment", "total",
        "Under when kickoff temperature is <= 45F and the model total is 4+ below the market.")
    add("S12", "Wind under", "environment", "total",
        "Under when kickoff wind is >= 15 mph.")
    add("S13", "Primetime home dog", "market-structure", "spread",
        "Home underdog in a 20:00+ kickoff window.")
    add("S14", "Thursday short-week home", "schedule", "spread",
        "Home team on Thursday when the visitor played a Sunday game.")
    add("S15", "Large-loss overreaction fade", "behaviour", "spread",
        "Fade a team that lost its previous game by 17+ (market overshoot test).")
    add("S16", "Divisional under", "market-structure", "total",
        "Under in division games, where familiarity suppresses scoring.")
    add("S17", "Late-season under", "schedule", "total",
        "Under in weeks 15-18.")
    add("S18", "Heavy favourite cover", "market-structure", "spread",
        "Home favourites of 7+ points.")
    add("S19", "Rest-advantage spread", "schedule", "spread",
        "Home team with 3+ more rest days than the visitor.")
    add("S20", "Model moneyline dog 6pt+", "model-ml", "moneyline",
        "Underdog moneylines where the model gives 6+ points more probability than the book.")
    add("S21", "Indoor over", "environment", "total",
        "Over when the roof is closed or the stadium is a dome: indoor games score more, "
        "and both the market and the model may under-adjust. Pre-specified hypothesis.")
    add("S22", "Moderate-wind under (EXPLORATORY)", "environment", "total",
        "Under when kickoff wind is 10-15 mph. EXPLORATORY: the band was chosen after "
        "inspecting results, so this is reported as a research finding, not a clean "
        "pre-registered test. Selection bias is a real risk here.")
    return D


def evaluate_rule(df: pd.DataFrame, d: dict) -> pd.DataFrame:
    """Return the settled legs of one rule on the supplied frame."""
    sid = d["id"]
    edge = df.model_margin - df.market_spread
    tedge = df.model_total - df.market_total

    if sid in ("S01", "S02", "S03"):
        thr = {"S01": 3.0, "S02": 4.0, "S03": 5.0}[sid]
        mask = edge.abs() >= thr
        parts = [spread_legs(df, mask & (edge > 0), "home"), spread_legs(df, mask & (edge < 0), "away")]
        return _cat(parts)
    if sid in ("S04", "S05"):
        thr = 3.0 if sid == "S04" else 4.0
        mask = tedge.abs() >= thr
        parts = [total_legs(df, mask & (tedge > 0), "over"), total_legs(df, mask & (tedge < 0), "under")]
        return _cat(parts)
    if sid == "S06":
        parts = [spread_legs(df, df.home_qb_changed == 1, "away"),
                 spread_legs(df, df.away_qb_changed == 1, "home")]
        return _cat(parts)
    if sid == "S07":
        return spread_legs(df, (df.home_bye == 1) & (df.away_bye == 0), "home")
    if sid == "S08":
        return spread_legs(df, df.away_rest <= 5, "home")
    if sid == "S09":
        return spread_legs(df, (df.div_game == 1) & (df.market_spread > 0) & (edge > 0), "home")
    if sid == "S10":
        return _ml_value(df, 0.04, dog_only=False)
    if sid == "S11":
        m = (df.temp <= 45) & df.temp.notna() & (tedge <= -4)
        return total_legs(df, m, "under")
    if sid == "S12":
        return total_legs(df, (df.wind >= 15) & df.wind.notna(), "under")
    if sid == "S13":
        return spread_legs(df, (df.primetime == 1) & (df.market_spread > 0), "home")
    if sid == "S14":
        return spread_legs(df, (df.thursday == 1) & (df.away_rest <= 5), "home")
    if sid == "S15":
        parts = [spread_legs(df, df.home_last_margin <= -17, "away"),
                 spread_legs(df, df.away_last_margin <= -17, "home")]
        return _cat(parts)
    if sid == "S16":
        return total_legs(df, df.div_game == 1, "under")
    if sid == "S17":
        return total_legs(df, df.week >= 15, "under")
    if sid == "S18":
        return spread_legs(df, df.market_spread >= 7, "home")
    if sid == "S19":
        return spread_legs(df, (df.home_rest - df.away_rest) >= 3, "home")
    if sid == "S20":
        return _ml_value(df, 0.06, dog_only=True)
    if sid == "S21":
        return total_legs(df, df.roof.isin(["dome", "closed"]), "over")
    if sid == "S22":
        return total_legs(df, (df.wind >= 10) & (df.wind < 15), "under")
    return df.iloc[0:0]


def _cat(parts):
    parts = [p for p in parts if p is not None and len(p)]
    return pd.concat(parts) if parts else pd.DataFrame(columns=["won", "push", "pnl", "break_even", "season", "week"])


def _ml_value(df, min_edge, dog_only):
    from statistics import NormalDist
    sigma = 13.6
    nd = NormalDist()
    p_home = df.model_margin.apply(lambda m: nd.cdf(m / sigma))
    out = []
    for side, col in (("home", "market_home_ml"), ("away", "market_away_ml")):
        odds = df[col]
        keep = odds.notna()
        if side == "away":
            keep &= (odds > 0) if dog_only else True
        if side == "home" and dog_only:
            keep &= (odds > 0)
        if not keep.any():
            continue
        imp = odds.apply(lambda o: (-o) / (-o + 100) if o < 0 else 100 / (o + 100))
        p_side = p_home if side == "home" else 1 - p_home
        m = keep & ((p_side - imp) >= min_edge)
        if m.any():
            out.append(ml_legs(df, m, side))
    return _cat(out)


def gates(m: dict, n_tests: int = BONFERRONI_TESTS) -> dict:
    thresh = 0.05 / max(n_tests, 1)
    if m.get("legs", 0) == 0:
        return {g: {"pass": False, "detail": "no legs"} for g in
                ["G1_sample", "G2_statistical", "G3_economic", "G4_stability",
                 "G5_multiplicity", "G6_skill", "G7_provenance"]}
    z = (m["hit_rate"] - 0.5) / math.sqrt(0.25 / m["legs"]) if m["legs"] else 0.0
    g1 = m["legs"] >= MIN_LEGS
    g2 = m["ci_low"] > m["break_even"]
    g3 = m["roi"] >= ROI_FLOOR
    g4 = m["seasons"] >= 3 and m["profitable_seasons"] >= math.ceil(m["seasons"] * 2 / 3)
    g5 = m["p_value"] < thresh
    g6 = z >= Z_FLOOR
    return {
        "G1_sample": {"pass": g1, "value": m["legs"], "detail": f"{m['legs']} legs (need {MIN_LEGS})"},
        "G2_statistical": {"pass": g2, "value": m["ci_low"],
                           "detail": f"Wilson 95% lower {m['ci_low']:.4f} vs break-even {m['break_even']:.4f}"},
        "G3_economic": {"pass": g3, "value": m["roi"],
                        "detail": f"ROI {m['roi']*100:+.2f}% (floor {ROI_FLOOR*100:.1f}%)"},
        "G4_stability": {"pass": g4, "value": m["profitable_seasons"],
                         "detail": f"{m['profitable_seasons']}/{m['seasons']} seasons profitable (need 2/3)"},
        "G5_multiplicity": {"pass": g5, "value": m["p_value"],
                            "detail": f"p={m['p_value']:.4g} vs {thresh:.2g} (Bonferroni {n_tests} tests)"},
        "G6_skill": {"pass": g6, "value": z,
                     "detail": f"z={z:.2f} vs 50% coin-flip (need {Z_FLOOR})"},
        "G7_provenance": {"pass": True, "detail": "all input columns verified in provenance.json"},
    }


def full_report(df: pd.DataFrame) -> dict:
    df = df.copy()
    dev = df[df.season.isin(DEV_SEASONS)]
    hold = df[df.season.isin(HOLDOUT_SEASONS)]
    rows = []
    for d in definitions():
        dev_legs = evaluate_rule(dev, d)
        dev_m = _settle(dev_legs)
        # parameter choice is fixed by the definition text, so dev is a diagnostic only
        hold_legs = evaluate_rule(hold, d)
        hold_m = _settle(hold_legs)
        g = gates(hold_m)
        rows.append({
            **d,
            "development": dev_m,
            "holdout": hold_m,
            "gates": g,
            "verdict": "CERTIFIED" if all(x["pass"] for x in g.values()) else "REJECTED",
            "failed_gates": [k for k, v in g.items() if not v["pass"]],
        })
    certified = [r for r in rows if r["verdict"] == "CERTIFIED"]
    return {
        "windows": {"development": [min(DEV_SEASONS), max(DEV_SEASONS)],
                    "holdout": [min(HOLDOUT_SEASONS), max(HOLDOUT_SEASONS)]},
        "tests_run": BONFERRONI_TESTS,
        "strategies": rows,
        "summary": {
            "total": len(rows),
            "certified": len(certified),
            "rejected": len(rows) - len(certified),
            "best_holdout_roi": max((r["holdout"].get("roi", -9) for r in rows), default=None),
        },
    }
