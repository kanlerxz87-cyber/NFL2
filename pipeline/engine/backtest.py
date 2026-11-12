"""Walk-forward backtest.

Produces one row per completed regular-season game containing ONLY information
that was available before kickoff (model ratings fitted on prior weeks, market
lines, rest days, venue, weather, quarterback identity, division flag) together
with the realised outcome. Every strategy in `strategies.py` is evaluated on
this table, so no strategy can see the future.

Output: pipeline/out/backtest.csv
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from pipeline.engine.ratings import fit_ratings, predict_game, fit_margin_to_prob

EVAL_SEASONS = list(range(2013, 2026))   # 2013-2025: full 17-week data + stable rules
DECAY = {"half_life": 8.0, "ridge": 6.0, "shrink_k": 8.0}


def _fit(games: pd.DataFrame, season: int, week: int) -> dict | None:
    """Time-decayed ridge fit, identical maths to engine.ratings.fit_ratings."""
    p = games[games.result.notna()]
    p = p[(p.season < season) | ((p.season == season) & (p.week < week))]
    p = p[p.season >= season - 4]
    if len(p) < 200:
        return None
    teams = sorted(set(p.home_team) | set(p.away_team))
    m = len(teams)
    idx = {t: i for i, t in enumerate(teams)}
    mu = float(p[["home_score", "away_score"]].to_numpy().mean())
    ne = p.location.eq("Neutral").to_numpy()
    hfa = float((p.home_score - p.away_score)[~ne].mean()) if (~ne).sum() > 50 else 2.0
    weeks_ago = ((season - p.season) * 18 + (week - p.week)).to_numpy()
    w = 0.5 ** (weeks_ago / DECAY["half_life"])
    n = len(p)
    X = np.zeros((2 * n, 2 * m))
    y = np.zeros(2 * n)
    sw = np.zeros(2 * n)
    hs, as_ = p.home_score.to_numpy(), p.away_score.to_numpy()
    home, away = p.home_team.to_numpy(), p.away_team.to_numpy()
    for r in range(n):
        hi, ai = idx[home[r]], idx[away[r]]
        X[2 * r, hi] = 1.0
        X[2 * r, m + ai] = 1.0
        X[2 * r + 1, ai] = 1.0
        X[2 * r + 1, m + hi] = 1.0
        y[2 * r] = hs[r] - mu - (0.0 if ne[r] else hfa / 2)
        y[2 * r + 1] = as_[r] - mu + (0.0 if ne[r] else hfa / 2)
        sw[2 * r] = sw[2 * r + 1] = 2.0 * w[r]
    A = X.T @ (X * sw[:, None]) + DECAY["ridge"] * np.eye(2 * m)
    theta = np.linalg.solve(A, X.T @ (y * sw))
    off, defa = theta[:m].copy(), theta[m:].copy()
    off -= off.mean()
    defa -= defa.mean()
    gc = pd.concat([p.home_team, p.away_team]).value_counts()
    sh = np.array([gc.get(t, 0) / (gc.get(t, 0) + DECAY["shrink_k"]) for t in teams])
    return {"idx": idx, "off": off * sh, "defa": defa * sh, "mu": mu, "hfa": hfa,
            "teams": teams, "n_games": int(n)}


def _predict(r: dict, home: str, away: str, neutral: bool, hr: float, ar: float):
    i = r["idx"]
    if home not in i or away not in i:
        return None
    hf = 0.0 if neutral else r["hfa"]
    rest = float(np.clip(0.06 * (hr - ar), -1.5, 1.5)) if np.isfinite(hr) and np.isfinite(ar) else 0.0
    hp = r["mu"] + hf / 2 + r["off"][i[home]] + r["defa"][i[away]] + rest / 2
    ap = r["mu"] - hf / 2 + r["off"][i[away]] + r["defa"][i[home]] - rest / 2
    return hp - ap, hp + ap


def build(games: pd.DataFrame, seasons: list[int] | None = None) -> pd.DataFrame:
    seasons = seasons or EVAL_SEASONS
    g = games[games.game_type.eq("REG") & games.result.notna()].copy()
    g = g.sort_values(["season", "week", "gameday"])
    out = []

    # rolling per-team context (all strictly prior to the game)
    prev_qb: dict[str, str] = {}
    last_margin: dict[str, float] = {}
    last_week: dict[str, int] = {}   # last week number each team played

    for season in seasons:
        season_games = g[g.season == season]
        for week in sorted(season_games.week.unique()):
            r = _fit(games, season, week)
            wk_rows = season_games[season_games.week == week]
            for _, row in wk_rows.iterrows():
                if r is None:
                    continue
                pr = _predict(r, row.home_team, row.away_team, row.location == "Neutral",
                              row.home_rest, row.away_rest)
                if pr is None:
                    continue
                pm, pt = pr
                home_qb, away_qb = row.home_qb_id, row.away_qb_id
                out.append({
                    "game_id": row.game_id, "season": int(season), "week": int(week),
                    "gameday": row.gameday, "home_team": row.home_team, "away_team": row.away_team,
                    "neutral": int(row.location == "Neutral"),
                    "div_game": int(row.div_game or 0),
                    "home_score": row.home_score, "away_score": row.away_score,
                    "result": row.result, "total": row.total,
                    "market_spread": row.spread_line, "market_total": row.total_line,
                    "market_home_ml": row.home_moneyline, "market_away_ml": row.away_moneyline,
                    "model_margin": pm, "model_total": pt,
                    "home_rest": row.home_rest, "away_rest": row.away_rest,
                    "home_qb": home_qb, "away_qb": away_qb,
                    "home_qb_changed": int(prev_qb.get(row.home_team, home_qb) != home_qb),
                    "away_qb_changed": int(prev_qb.get(row.away_team, away_qb) != away_qb),
                    "home_last_margin": last_margin.get(row.home_team, np.nan),
                    "away_last_margin": last_margin.get(row.away_team, np.nan),
                    "home_bye": int((week - last_week.get(row.home_team, week - 1)) >= 2),
                    "away_bye": int((week - last_week.get(row.away_team, week - 1)) >= 2),
                    "roof": row.roof, "surface": row.surface, "temp": row.temp, "wind": row.wind,
                    "primetime": int(str(row.gametime)[:2] in ("20", "21") if isinstance(row.gametime, str) else 0),
                    "weekday": row.weekday,
                    "thursday": int(row.weekday == "Thursday"),
                    "sunday_night": int(str(row.gametime) == "20:20"),
                    "monday": int(row.weekday == "Monday"),
                })
                prev_qb[row.home_team] = home_qb
                prev_qb[row.away_team] = away_qb
                last_margin[row.home_team] = row.result
                last_margin[row.away_team] = -row.result
                last_week[row.home_team] = int(week)
                last_week[row.away_team] = int(week)

    df = pd.DataFrame(out)
    df["home_win"] = (df.result > 0).astype(int)
    df["cover_home"] = np.where(df.result > df.market_spread, 1,
                                np.where(df.result < df.market_spread, 0, np.nan))
    df["over"] = np.where(df.total > df.market_total, 1,
                          np.where(df.total < df.market_total, 0, np.nan))
    return df


def calibrate_prob(df: pd.DataFrame) -> dict:
    """Fit margin -> P(home win) on the first half of the sample, report on the second.

    Keeping this strictly chronological is what stops the probability model from
    learning the answers it is later scored against.
    """
    seasons = sorted(df.season.unique())
    cut = seasons[len(seasons) // 2]
    train = df[df.season < cut]
    test = df[df.season >= cut]
    fit = fit_margin_to_prob(train.model_margin.to_numpy(), train.home_win.to_numpy())
    z = fit["intercept"] + fit["slope"] * test.model_margin.to_numpy()
    p = 1 / (1 + np.exp(-z))
    from sklearn_lite import brier, logloss  # local shim
    return {
        "fit": fit, "train_seasons": [int(min(train.season)), int(cut) - 1],
        "test_seasons": [int(cut), int(max(test.season))],
        "brier": brier(test.home_win.to_numpy(), p),
        "logloss": logloss(test.home_win.to_numpy(), p),
        "n_test": int(len(test)),
        "accuracy": float(((p > 0.5).astype(int) == test.home_win.to_numpy()).mean()),
    }


if __name__ == "__main__":
    import os
    from pipeline.common import RAW, sha256
    games = pd.read_csv(os.path.join(RAW, "games.csv"))
    df = build(games)
    os.makedirs("pipeline/out", exist_ok=True)
    df.to_csv("pipeline/out/backtest.csv", index=False)
    print(df.shape)
    print(df.groupby("season").size().to_dict())
    print("market spread coverage", df.market_spread.notna().mean().round(4))
