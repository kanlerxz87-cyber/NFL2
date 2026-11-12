"""Model calibration report.

Answers one question on its own page: is the number we publish actually a line,
or is it noise? Reports, by season and overall:

  MAE / RMSE        against the realised result (spread) and total
  bias              mean signed error (a persistent bias means the model is broken)
  correlation       Pearson r between prediction and outcome
  calibration       predicted P(home win) binned, versus the observed win rate
  versus market     the same metrics for the closing line, which is the benchmark
                    a line originator must beat to be useful

The market comparison is the honest scoreboard: our model currently does NOT beat
the close, and the page says so with the numbers attached.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from statistics import NormalDist


def _metrics(pred, actual) -> dict:
    pred = np.asarray(pred, float)
    act = np.asarray(actual, float)
    ok = np.isfinite(pred) & np.isfinite(act)
    pred, act = pred[ok], act[ok]
    if len(pred) == 0:
        return {}
    err = act - pred
    return {
        "n": int(len(pred)),
        "mae": round(float(np.abs(err).mean()), 3),
        "rmse": round(float(np.sqrt((err ** 2).mean())), 3),
        "bias": round(float(err.mean()), 3),
        "correlation": round(float(np.corrcoef(pred, act)[0, 1]), 4),
    }


def build(df: pd.DataFrame, sigma_margin: float = 13.248) -> dict:
    d = df.copy()
    d["p_home_model"] = [NormalDist().cdf(m / sigma_margin) for m in d.model_margin]
    overall = {
        "spread_model_vs_result": _metrics(d.model_margin, d.result),
        "spread_market_vs_result": _metrics(-d.market_spread, d.result),
        "total_model_vs_result": _metrics(d.model_total, d.total),
        "total_market_vs_result": _metrics(d.market_total, d.total),
    }
    by_season = []
    for s, g in d.groupby("season"):
        by_season.append({
            "season": int(s),
            "model_spread_mae": round(float((g.result - g.model_margin).abs().mean()), 3),
            "market_spread_mae": round(float((g.result + g.market_spread).abs().mean()), 3),
            "model_total_mae": round(float((g.total - g.model_total).abs().mean()), 3),
            "market_total_mae": round(float((g.total - g.market_total).abs().mean()), 3),
            "n": int(len(g)),
        })

    bins = [0, .2, .35, .5, .65, .8, 1.0]
    d["bin"] = pd.cut(d.p_home_model, bins, include_lowest=True)
    cal = (d.groupby("bin", observed=True)
           .agg(n=("home_win", "size"), predicted=("p_home_model", "mean"), actual=("home_win", "mean"))
           .reset_index())
    calibration = [{
        "bucket": f"{float(r.bin.left):.2f}-{float(r.bin.right):.2f}",
        "n": int(r.n), "predicted": round(float(r.predicted), 4),
        "observed": round(float(r.actual), 4),
        "error": round(float(r.actual - r.predicted), 4),
    } for r in cal.itertuples()]

    win_rate_when_model_agrees = {
        "favourite_covers": _metrics(d.model_margin.clip(lower=-99), d.result),
    }
    return {
        "sigma_used": sigma_margin,
        "overall": overall,
        "by_season": by_season,
        "calibration_table": calibration,
        "verdict": _verdict(overall),
        "note": "Model spread/total are walk-forward: each week is predicted from prior weeks "
                "only. Market columns are closing lines and are the benchmark. If the model's "
                "MAE is not lower than the market's, the model is not yet a better line than "
                "the closing number and should not be used to bet against it.",
    }


def _verdict(overall: dict) -> dict:
    ms = overall["spread_model_vs_result"]["mae"]
    km = overall["spread_market_vs_result"]["mae"]
    mt = overall["total_model_vs_result"]["mae"]
    kt = overall["total_market_vs_result"]["mae"]
    return {
        "spread_beats_market": bool(ms < km),
        "total_beats_market": bool(mt < kt),
        "spread_gap_points": round(ms - km, 3),
        "total_gap_points": round(mt - kt, 3),
        "statement": (
            f"The model's spread MAE is {ms:.2f} vs the market's {km:.2f} "
            f"({ms - km:+.2f} points worse). Total MAE {mt:.2f} vs {kt:.2f} "
            f"({mt - kt:+.2f}). The model is not yet sharper than the closing line, so "
            "it is presented as a line-origination baseline and a research instrument, "
            "not as a betting system."
        ),
    }
