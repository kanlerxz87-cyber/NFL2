"""Team strength ratings and line-origination model.

Parameterisation (fitted only on games strictly before the target game):

    home_points = mu + hfa/2 + off[home] + defa[away] + rest_term/2
    away_points = mu - hfa/2 + off[away] + defa[home] - rest_term/2

  mu        league-average points per team
  hfa       home-field advantage in points (estimated from prior data, not assumed)
  off[t]    points scored above league average by team t
  defa[t]   points ALLOWED above league average by team t  (positive = leaky defence)

Both rating blocks are sum-zero identified. Estimation is ridge-regularised least
squares, followed by sample-size shrinkage toward the mean (8 games -> 0.5 weight).
Keeping hfa inside mu keeps the *total* prediction unbiased, which matters because
totals are half of the betting market.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

RIDGE = 6.0
WINDOW_SEASONS = 4
SHRINK_K = 8.0


def regression_to_mean(n_games: float, k: float = SHRINK_K) -> float:
    return n_games / (n_games + k)


def _prior(games: pd.DataFrame, through_season: int, through_week: int) -> pd.DataFrame:
    p = games[games.result.notna()]
    p = p[(p.season < through_season) |
          ((p.season == through_season) & (p.week < through_week))]
    return p[p.season >= through_season - WINDOW_SEASONS].copy()


def fit_ratings(games: pd.DataFrame, through_season: int, through_week: int) -> dict:
    prior = _prior(games, through_season, through_week)
    if len(prior) < 200:
        return {"ok": False, "reason": f"only {len(prior)} prior games", "n": int(len(prior))}

    teams = sorted(set(prior.home_team) | set(prior.away_team))
    m = len(teams)
    idx = {t: i for i, t in enumerate(teams)}

    mu = float(prior[["home_score", "away_score"]].to_numpy().mean())
    neutral = prior.location.eq("Neutral")
    hfa = float((prior.home_score - prior.away_score)[~neutral].mean()) if (~neutral).sum() > 50 else 2.0

    n = len(prior)
    X = np.zeros((2 * n, 2 * m))
    y = np.empty(2 * n)
    hs = prior.home_score.to_numpy()
    as_ = prior.away_score.to_numpy()
    home = prior.home_team.to_numpy()
    away = prior.away_team.to_numpy()
    neutral_arr = neutral.to_numpy()
    for r in range(n):
        hi, ai = idx[home[r]], idx[away[r]]
        X[2 * r, hi] = 1.0
        X[2 * r, m + ai] = 1.0
        X[2 * r + 1, ai] = 1.0
        X[2 * r + 1, m + hi] = 1.0
        y[2 * r] = hs[r] - mu - (0.0 if neutral_arr[r] else hfa / 2)
        y[2 * r + 1] = as_[r] - mu + (0.0 if neutral_arr[r] else hfa / 2)

    A = X.T @ X + RIDGE * np.eye(2 * m)
    theta = np.linalg.solve(A, X.T @ y)
    off, defa = theta[:m], theta[m:]
    off -= off.mean()
    defa -= defa.mean()
    resid = y - X @ np.concatenate([off, defa])

    gcount = pd.concat([prior.home_team, prior.away_team]).value_counts()
    shrink = {t: regression_to_mean(float(gcount.get(t, 0))) for t in teams}

    # Per-team evidence for the "verified vs unverified" flag
    gp = gcount.reindex(teams).fillna(0).astype(int).to_dict()

    return {
        "ok": True,
        "teams": teams,
        "off": {t: float(off[i] * shrink[t]) for i, t in enumerate(teams)},
        "defa": {t: float(defa[i] * shrink[t]) for i, t in enumerate(teams)},
        "mu": mu, "hfa": hfa,
        "n_games": int(n),
        "window": [int(through_season - WINDOW_SEASONS), int(through_season)],
        "rmse": float(np.sqrt((resid ** 2).mean())),
        "sigma": float(resid.std()),
        "games_per_team": {k: int(v) for k, v in gp.items()},
    }


def predict_game(r: dict, home: str, away: str, neutral: bool = False,
                 home_rest: float | None = None, away_rest: float | None = None) -> dict | None:
    if not r.get("ok") or home not in r["off"] or away not in r["off"]:
        return None
    h = 0.0 if neutral else r["hfa"]
    rest = 0.0
    if home_rest is not None and away_rest is not None and np.isfinite(home_rest) and np.isfinite(away_rest):
        rest = float(np.clip(0.06 * (home_rest - away_rest), -1.5, 1.5))
    hp = r["mu"] + h / 2 + r["off"][home] + r["defa"][away] + rest / 2
    ap = r["mu"] - h / 2 + r["off"][away] + r["defa"][home] - rest / 2
    return {
        "home_points": float(hp), "away_points": float(ap),
        "margin": float(hp - ap), "total": float(hp + ap),
        "neutral": bool(neutral), "rest_adjustment": float(rest),
        "home_off": r["off"][home], "away_off": r["off"][away],
        "home_defa": r["defa"][home], "away_defa": r["defa"][away],
    }


def fit_margin_to_prob(margins, home_wins) -> dict:
    m = np.asarray(margins, float)
    w = np.asarray(home_wins, float)
    ok = np.isfinite(m) & np.isfinite(w)
    m, w = m[ok], w[ok]
    if len(m) < 100:
        s = max(float(np.std(m)), 1e-6)
        return {"slope": 1.0 / (s * 1.7), "intercept": 0.0, "n": int(len(m)),
                "method": "normal-approximation (sample < 100)"}
    slope, intercept = 0.14, 0.0
    for _ in range(80):
        z = intercept + slope * m
        p = 1 / (1 + np.exp(-z))
        Wd = p * (1 - p) + 1e-9
        g = np.array([np.sum(w - p), np.sum((w - p) * m)])
        H = np.array([[np.sum(Wd), np.sum(Wd * m)], [np.sum(Wd * m), np.sum(Wd * m * m)]])
        step = np.linalg.solve(H, g)
        intercept += step[0]
        slope += step[1]
        if np.max(np.abs(step)) < 1e-10:
            break
    return {"slope": float(slope), "intercept": float(intercept), "n": int(len(m)),
            "method": "newton-raphson logistic regression on margin"}


def american_to_decimal(odds: float) -> float | None:
    if odds is None or not np.isfinite(odds):
        return None
    return 1 + (odds / 100 if odds > 0 else 100 / abs(odds))


def american_to_prob(odds: float) -> float | None:
    if odds is None or not np.isfinite(odds) or odds == 0:
        return None
    return (-odds) / (-odds + 100) if odds < 0 else 100 / (odds + 100)


def prob_to_american(p: float) -> int:
    p = min(max(p, 1e-4), 1 - 1e-4)
    return int(round(-100 * p / (1 - p))) if p > 0.5 else int(round(100 * (1 - p) / p))


def prob_to_spread(p_home: float, sigma: float) -> float:
    from statistics import NormalDist
    z = NormalDist().inv_cdf(min(max(p_home, 1e-4), 1 - 1e-4))
    return float(-z * sigma)
