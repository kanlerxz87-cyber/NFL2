"""Correlation values for parlays, player-prop combinations and leg selection.

Everything here is measured from realised results, not assumed:

* CORRELATION OF OUTCOMES — Pearson phi between two binary legs on the same game.
  A parlay prices legs as independent, so any |phi| > 0 is mispricing for the book
  or for the bettor depending on the sign.
* CORRELATION OF SIGNALS — between the model's edge on each market, which tells
  you whether your "two independent edges" are actually one edge counted twice.
* PARLAY MATHEMATICS — the difference between the independent price and the
  price implied by the measured joint probability, expressed in American odds.
  This is the number that decides whether a same-game parlay is worth taking.
"""
from __future__ import annotations

import itertools
import math

import numpy as np
import pandas as pd

PAIRS = [
    ("spread_home", "total_over"), ("spread_home", "home_ml"),
    ("total_over", "home_ml"), ("spread_home", "away_ml"),
]


def _phi(a: pd.Series, b: pd.Series) -> tuple[float, int]:
    d = pd.concat([a, b], axis=1).dropna()
    if len(d) < 30:
        return float("nan"), len(d)
    x, y = d.iloc[:, 0].to_numpy(), d.iloc[:, 1].to_numpy()
    if x.std() == 0 or y.std() == 0:
        return float("nan"), len(d)
    return float(np.corrcoef(x, y)[0, 1]), int(len(d))


def outcome_correlations(df: pd.DataFrame) -> dict:
    d = df.copy()
    d["spread_home"] = (d.result > d.market_spread).astype(float)
    d["spread_home"] = d.spread_home.where(d.result != d.market_spread)     # drop pushes
    d["total_over"] = (d.total > d.market_total).astype(float)
    d["total_over"] = d.total_over.where(d.total != d.market_total)
    d["home_ml"] = (d.result > 0).astype(float)
    d["away_ml"] = (d.result < 0).astype(float)
    rows = []
    for a, b in PAIRS:
        r, n = _phi(d[a], d[b])
        joint = float(((d[a] == 1) & (d[b] == 1)).sum()) / n if n else None
        pa = float((d[a] == 1).mean())
        pb = float((d[b] == 1).mean())
        rows.append({
            "leg_a": a, "leg_b": b, "n": n, "phi": None if math.isnan(r) else round(r, 4),
            "p_a": round(pa, 4), "p_b": round(pb, 4),
            "p_joint_observed": None if joint is None else round(joint, 4),
            "p_joint_independent": round(pa * pb, 4),
        })
    return {
        "source": "pipeline/out/backtest.csv (2013-2025 completed regular-season games)",
        "note": "phi = Pearson correlation between two binary leg outcomes. 0 means the "
                "parlay's independence assumption holds; anything else means a same-game "
                "parlay is mispriced relative to its own legs.",
        "pairs": rows,
    }


def signal_correlations(df: pd.DataFrame) -> dict:
    """Correlation between the model's own edges across markets."""
    e_spread = (df.model_margin - df.market_spread).to_numpy()
    e_total = (df.model_total - df.market_total).to_numpy()
    ok = np.isfinite(e_spread) & np.isfinite(e_total)
    r = float(np.corrcoef(e_spread[ok], e_total[ok])[0, 1])
    return {
        "n": int(ok.sum()),
        "spread_edge_vs_total_edge": round(r, 4),
        "interpretation": (
            "A spread edge and a total edge are close to independent, so combining them in "
            "one parlay genuinely diversifies risk." if abs(r) < 0.2 else
            "The spread and total edges move together: they are partly the same signal, so "
            "combining them double-counts your own model and does not diversify risk."),
    }


def parlay_pricing(pair: dict, american_a: int = -110, american_b: int = -110) -> dict:
    """Compare independent pricing with the price implied by the observed joint probability."""
    def dec(a):
        return 1 + (a / 100 if a > 0 else 100 / abs(a))

    def to_american(p):
        p = min(max(p, 1e-6), 1 - 1e-6)
        return round(-100 * p / (1 - p)) if p > 0.5 else round(100 * (1 - p) / p)

    d = dec(american_a) * dec(american_b)
    p_ind = 1 / d
    p_obs = pair["p_joint_observed"] or p_ind
    return {
        "independent_decimal": round(d, 4),
        "independent_american": to_american(p_ind),
        "implied_prob_independent": round(p_ind, 4),
        "implied_prob_from_observed": round(p_obs, 4),
        "fair_american_if_observed": to_american(p_obs),
        "price_error_pct": round((p_obs - p_ind) / p_ind * 100, 3),
        "comment": ("the book's independent pricing understates this parlay"
                    if p_obs > p_ind else
                    "the book's independent pricing overstates this parlay"),
    }


def build(df: pd.DataFrame) -> dict:
    oc = outcome_correlations(df)
    for p in oc["pairs"]:
        p["parlay"] = parlay_pricing(p)
    return {
        "outcomes": oc,
        "signals": signal_correlations(df),
        "limitations": [
            "Only game-level markets are measured here; player-prop outcomes need "
            "player-week data that is not available in this sandbox, so prop-to-prop "
            "correlations are published as UNVERIFIED rather than estimated.",
            "Correlations are measured on closing lines, which is the fairest post-hoc "
            "benchmark but is not the price every bettor actually got.",
        ],
    }
