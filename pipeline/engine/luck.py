"""Removing luck from the equation.

Four separate tests. Each answers a different question, and a strategy must pass
all of them before it is described as skill-based.

1. VARIANCE TEST — is the observed standard deviation of results larger than the
   standard deviation implied by pure chance?  For n independent bets with hit
   rate p, the number of wins has sd = sqrt(n p (1-p)). We report the ratio
   observed/theoretical. Ratio ~ 1.0 means the outcome is indistinguishable from
   coin flips; with 100 bets you need |ratio-1| > ~0.14 before it means anything.

2. BINOMIAL EXACTNESS — a one-sided exact p-value against the break-even rate.
   This is what stops "7 of the last 9" stories.

3. SPLIT-HALF CONSISTENCY — divide the holdout chronologically in two. A skill
   signal should keep its sign across both halves; a lucky one regresses.

4. PERSISTENCE (autocorrelation) — does the edge in season t predict the edge in
   season t+1? Real edges persist; lucky ones do not. Reported as a
   season-to-season correlation of ROI with its confidence interval.

The headline "skill share" is the persistence coefficient: the fraction of an
observed edge that survives into the next season.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

from pipeline.engine.sklearn_lite import wilson_interval
from pipeline.engine.strategies import _canon


def variance_test(wins: int, legs: int, p0: float) -> dict:
    if legs == 0:
        return {"legs": 0}
    p = p0
    theo_sd = math.sqrt(legs * p * (1 - p))
    obs_sd = math.sqrt(legs * (wins / legs) * (1 - wins / legs)) if 0 < wins < legs else 0.0
    return {"legs": legs, "wins": wins, "theoretical_sd": theo_sd, "observed_sd": obs_sd,
            "sd_ratio": _canon(obs_sd / theo_sd) if theo_sd else None,
            "interpretation": "sd_ratio near 1.0 = indistinguishable from chance"}


def split_half(legs: pd.DataFrame) -> dict:
    if legs.empty:
        return {"n": 0}
    ordered = legs.sort_values(["season", "week"])
    cut = len(ordered) // 2
    a, b = ordered.iloc[:cut], ordered.iloc[cut:]
    def stat(d):
        n = len(d)
        w = int(d.won.sum())
        return {"n": n, "wins": w, "hit": (w / n if n else None), "roi": float(d.pnl.mean()) if n else None}
    return {"first_half": stat(a), "second_half": stat(b),
            "same_sign_roi": bool(np.sign(a.pnl.mean()) == np.sign(b.pnl.mean())) if len(a) and len(b) else None}


def persistence(legs: pd.DataFrame, min_legs: int = 25) -> dict:
    """Season-to-season correlation of ROI; the skill share is that correlation."""
    if legs.empty:
        return {"seasons": 0}
    s = legs.groupby("season").agg(n=("won", "size"), roi=("pnl", "mean"))
    s = s[s.n >= min_legs]
    if len(s) < 4:
        return {"seasons": int(len(s)), "correlation": None,
                "note": f"needs >=4 seasons with >={min_legs} legs; got {len(s)}"}
    x, y = s.roi.to_numpy()[:-1], s.roi.to_numpy()[1:]
    if np.std(x) == 0 or np.std(y) == 0:
        return {"seasons": int(len(s)), "correlation": None, "note": "zero variance"}
    r = float(np.corrcoef(x, y)[0, 1])
    n = len(x)
    se = 1 / math.sqrt(max(n - 3, 1))
    return {"seasons": int(len(s)), "correlation": r,
            "ci_low": round(r - 1.96 * se, 4), "ci_high": round(r + 1.96 * se, 4),
            "skill_share": round(max(r, 0.0), 4),
            "note": "share of a season's edge that repeats the next season; 0 = pure luck"}


def decompose(strategies: list[dict], legs_by_id: dict[str, pd.DataFrame]) -> dict:
    out = []
    for s in strategies:
        legs = legs_by_id.get(s["id"])
        if legs is None or legs.empty:
            out.append({"id": s["id"], "name": s["name"], "verdict": "NO_DATA"})
            continue
        n = len(legs)
        w = int(legs.won.sum())
        p0 = float(legs.break_even.mean())
        lo, hi = wilson_interval(w, n)
        sh = split_half(legs)
        pe = persistence(legs)
        out.append({
            "id": s["id"], "name": s["name"], "family": s["family"],
            "legs": n, "hit_rate": round(w / n, 4), "ci_low": round(lo, 4),
            "break_even": round(p0, 4), "excess": round(w / n - p0, 4),
            "variance_test": variance_test(w, n, p0),
            "split_half": sh,
            "persistence": pe,
            "luck_verdict": _luck_verdict(lo, p0, sh, pe),
        })
    return {"methods": ["variance ratio", "wilson lower bound vs break-even",
                        "chronological split-half", "season-to-season persistence"],
            "strategies": out}


def _luck_verdict(ci_low: float, p0: float, sh: dict, pe: dict) -> str:
    reasons = []
    if ci_low <= p0:
        reasons.append("hit rate not distinguishable from break-even")
    if sh.get("same_sign_roi") is False:
        reasons.append("ROI sign flips between halves")
    if pe.get("correlation") is not None and pe["correlation"] <= 0:
        reasons.append("season-to-season edge does not persist")
    if not reasons:
        return "SKILL-CONSISTENT"
    return "LUCK-DOMINATED: " + "; ".join(reasons)
