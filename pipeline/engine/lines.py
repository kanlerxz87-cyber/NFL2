"""Line origination for the upcoming slate.

For every scheduled game with no result yet we publish OUR OWN number:

    spread      model margin, expressed as the home-team handicap
                (negative = home favoured, matching games.csv conventions)
    total       model total
    moneyline   fair American price from the calibrated margin->probability model,
                plus a 4.5% hold so the two sides form a real two-way market
    over/under  fair prices with the same hold

Two other numbers sit beside them and are never mixed up with them:

    consensus close   the market line from games.csv (the benchmark we are judged
                      against). Present only when the upstream file has it.
    confidence        how much of the input data is verified. For the current slate
                      the injury feed lags and there is no opening line for most
                      games, so confidence is reported as LOW and the reason is
                      printed, not hidden.

Nothing is inferred. If a team has no rating (expansion or missing history), the
game is omitted and listed as unrated.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from pipeline.engine.ratings import fit_ratings, predict_game, prob_to_american, prob_to_spread
from pipeline.engine.backtest import _fit, _predict
from statistics import NormalDist

HOLD = 0.045
# Realised standard deviation of (actual margin - model margin) on the walk-forward
# backtest 2013-2025, computed by pipeline/engine/calibration.py. Recompute with
# `python3 -m pipeline.engine.calibration` rather than editing by hand.
SIGMA_MARGIN = 13.248
SIGMA_TOTAL = 13.682


def _two_way(p: float, hold: float = HOLD) -> tuple[int, int]:
    """Convert a fair probability into a two-way price pair carrying `hold`."""
    p_a = min(max(p, 1e-4), 1 - 1e-4)
    p_b = 1 - p_a
    # de-vigged fair prices, then add the hold symmetrically in probability space
    a = p_a * (1 + hold)
    b = p_b * (1 + hold)
    s = a + b
    return prob_to_american(a / s), prob_to_american(b / s)


def current_slate(games: pd.DataFrame, injuries: pd.DataFrame | None = None) -> dict:
    pending = games[(games.result.isna())].copy()
    if pending.empty:
        return {"games": [], "note": "no scheduled games found upstream"}

    seasons = sorted(pending.season.unique())
    out, unrated = [], []

    for season in seasons:
        sg = pending[pending.season == season]
        weeks = sorted(sg.week.unique())
        for week in weeks[:2]:           # only the nearest two weeks are actionable
            wg = sg[sg.week == week]
            r = _fit(games, int(season), int(week))
            if r is None:
                continue
            for _, row in wg.sort_values("gameday").iterrows():
                pr = _predict(r, row.home_team, row.away_team, row.location == "Neutral",
                              row.home_rest if pd.notna(row.home_rest) else 7.0,
                              row.away_rest if pd.notna(row.away_rest) else 7.0)
                if pr is None:
                    unrated.append({"game_id": row.game_id, "home": row.home_team,
                                    "away": row.away_team,
                                    "reason": "team not present in the fitted rating window"})
                    continue
                margin, total = pr
                p_home = NormalDist().cdf(margin / SIGMA_MARGIN)
                ml_home, ml_away = _two_way(p_home)
                ml = row.home_moneyline if pd.notna(row.home_moneyline) else None
                ml_away_market = row.away_moneyline if pd.notna(row.away_moneyline) else None
                out.append({
                    "game_id": row.game_id,
                    "season": int(season), "week": int(week), "gameday": str(row.gameday),
                    "kickoff_et": str(row.gametime) if pd.notna(row.gametime) else None,
                    "home": row.home_team, "away": row.away_team,
                    "venue": "neutral" if row.location == "Neutral" else "home",
                    "stadium": row.stadium,
                    "our_spread_home": round(float(-margin), 2),
                    "our_total": round(float(total), 2),
                    "home_win_prob": round(float(p_home), 4),
                    "our_ml_home": ml_home, "our_ml_away": ml_away,
                    "our_over": _two_way(0.5)[0], "our_under": _two_way(0.5)[1],
                    "market_spread_home": None if pd.isna(row.spread_line) else float(-row.spread_line),
                    "market_total": None if pd.isna(row.total_line) else float(row.total_line),
                    "market_ml_home": None if ml is None else int(ml),
                    "market_ml_away": None if ml_away_market is None else int(ml_away_market),
                    "edge_vs_market_spread": (None if pd.isna(row.spread_line)
                                              else round(float(-margin) - float(-row.spread_line), 2)),
                    "edge_vs_market_total": (None if pd.isna(row.total_line)
                                             else round(float(total) - float(row.total_line), 2)),
                    "rating_games_used": r["n_games"],
                    "confidence": _confidence(row),
                    "confidence_reason": _confidence_reason(row),
                    "sources": {
                        "schedule": "games.csv (leesharpe/nfldata)",
                        "ratings": "pipeline/engine/ratings.py fitted on prior weeks only",
                    },
                })
    return {
        "generated_for": f"season {seasons[0] if len(seasons)==1 else seasons}, nearest two weeks",
        "hold_applied": HOLD,
        "probability_model": f"normal approximation on the margin model, sigma = {SIGMA_MARGIN} "
                             "points (realised residual sigma from the walk-forward backtest, "
                             "recomputed by pipeline/engine/calibration.py)",
        "games": out,
        "unrated": unrated,
        "coverage_note": "Market columns are filled only where the upstream file already "
                         "carries a posted number; blank means the market price is not in "
                         "the source, not that the game has no market.",
    }


def _confidence(row) -> str:
    have_market = pd.notna(row.spread_line) and pd.notna(row.total_line)
    return "MEDIUM" if have_market else "LOW"


def _confidence_reason(row) -> str:
    if pd.notna(row.spread_line) and pd.notna(row.total_line):
        return ("A market line is present in the source, so our number can be compared to a "
                "benchmark. Injury-report data for this week may still be incomplete.")
    return ("No market line is present in the source for this game yet, and the injury feed "
            "for this week is not final; the number is model-only and unbenchmarked.")


def ratings_table(games: pd.DataFrame, season: int, week: int) -> dict:
    r = fit_ratings(games, season, week)
    if not r.get("ok"):
        return {"available": False, "reason": r.get("reason")}
    rows = []
    for t in r["teams"]:
        rows.append({
            "team": t, "offense": round(r["off"][t], 2), "defense_allowed": round(r["defa"][t], 2),
            "net": round(r["off"][t] - r["defa"][t], 2),
            "games_in_window": r["games_per_team"].get(t, 0),
        })
    rows.sort(key=lambda x: -x["net"])
    return {
        "available": True, "through": f"{season} week {week - 1}",
        "league_average_points": round(r["mu"], 2),
        "home_field_points": round(r["hfa"], 2),
        "window_seasons": r["window"], "games_used": r["n_games"],
        "sigma_residual": round(r["sigma"], 3),
        "method": "time-decayed ridge (half-life 8 weeks, ridge 6.0, shrink k=8)",
        "teams": rows,
    }
