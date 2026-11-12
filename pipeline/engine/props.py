"""Player-prop and same-game-parlay structure.

Honest scope statement — read this before trusting any number here:

The prop *combos* module can only measure what it can verify. What exists in this
sandbox is:
  * one week of DraftKings salaries (Week 9, 2026 main slate) — gives team,
    game, position and price for every priced player;
  * one public projection feed for Week 9 (258 tickets) which is UNVERIFIED —
    it comes from a public repository, not from a sportsbook, and its own
    projection method cannot be audited here.
What does not exist: a historical player-prop line archive. Therefore:

  1. PROP-TO-PROP CORRELATION IS NOT ESTIMATED FROM OUTCOMES. It cannot be.
     Anything that claimed a number would be fabricated. The site publishes these
     rows as UNVERIFIED with the reason attached.
  2. What *can* be computed without prop history is the STRUCTURE of the same-game
     parlay: how many legs, what the book's independent pricing implies, and how
     much of the price is eaten by the vig compounding. That is arithmetic, and it
     is exact, so it is published.

The game-level correlations in correlation.py are the real, verified numbers for
correlated-leg pricing; use those for spread/total/moneyline combinations.
"""
from __future__ import annotations

import os

import pandas as pd

from pipeline.common import RAW

# Legs that are structurally correlated inside one game. Direction is the sign of
# the relationship, magnitude is deliberately NOT supplied — see docstring.
STRUCTURAL = [
    {"leg_a": "QB passing yards OVER", "leg_b": "WR receiving yards OVER", "sign": "+",
     "reason": "the same completions produce both; a parlay of the two is one bet on "
               "the passing game, not two independent bets."},
    {"leg_a": "QB passing TDs OVER", "leg_b": "WR/TE receiving TDs OVER", "sign": "+",
     "reason": "a touchdown pass is the receiving touchdown; the two legs are almost "
               "the same event."},
    {"leg_a": "RB rushing yards OVER", "leg_b": "Team total OVER", "sign": "+",
     "reason": "a run-heavy game script raises both."},
    {"leg_a": "RB rushing yards OVER", "leg_b": "WR receiving yards OVER", "sign": "-",
     "reason": "run-heavy and pass-heavy game scripts trade off against each other."},
    {"leg_a": "Team A moneyline", "leg_b": "Team A skill player OVER", "sign": "+",
     "reason": "winning teams run more plays and keep the ball."},
    {"leg_a": "Game total OVER", "leg_b": "QB passing yards OVER", "sign": "+",
     "reason": "a higher-scoring game is usually a higher-volume passing game."},
    {"leg_a": "Sacks OVER (defence)", "leg_b": "Opponent passing yards UNDER", "sign": "+",
     "reason": "sacks end drives and suppress passing volume."},
    {"leg_a": "Kicking points OVER", "leg_b": "Game total UNDER", "sign": "+",
     "reason": "field goals replace touchdowns in low-scoring games."},
]

# Empirical anchor: season-level, measured from data we DO have.
def team_game_correlation(df: pd.DataFrame) -> dict:
    """Correlation between a team's scoring and its opponent's, i.e. pace correlation."""
    import numpy as np
    h = df[["home_team", "home_score", "away_score", "total"]].copy()
    r = float(np.corrcoef(df.home_score, df.away_score)[0, 1])
    return {
        "n_games": int(len(df)),
        "corr_home_score_away_score": round(r, 4),
        "interpretation": (
            "Scores are positively correlated: games are largely a shared pace/tempo "
            "process, which is why 'team A over' and 'team B over' are not independent "
            "legs in a parlay." if r > 0.1 else
            "Scores are close to uncorrelated, so opposing team-total overs are closer "
            "to independent than the pace story implies."),
    }


def slate_structure() -> dict:
    p = os.path.join(RAW, "dfs", "DKSalaries_week9_main_2026-11-08.csv")
    if not os.path.exists(p):
        return {"available": False}
    d = pd.read_csv(p)
    d["game"] = d["Game Info"].astype(str).str.split(" ").str[0]
    d["team"] = d["game"].str.split("@").str[0]
    d["salary"] = pd.to_numeric(d.Salary, errors="coerce")
    games = (d.groupby("game").agg(players=("Name", "size"),
                                   qb=("Position", lambda s: (s == "QB").sum()),
                                   rb=("Position", lambda s: (s == "RB").sum()),
                                   wr=("Position", lambda s: (s == "WR").sum()),
                                   te=("Position", lambda s: (s == "TE").sum()))
             .reset_index())
    statuses = d.Status.fillna("active").value_counts().to_dict()
    return {
        "available": True,
        "source": "DraftKings main-slate salary export, Week 9 2026 (11/08/2026), "
                  "mirrored in-repo at pipeline/data/raw/dfs/",
        "verified": True,
        "rows": int(len(d)),
        "games": games.to_dict("records"),
        "status_counts": {str(k): int(v) for k, v in statuses.items()},
        "note_on_status": "IR / OUT / Q / D flags are the book's own availability "
                          "markers on this export. They are not the NFL's official "
                          "designations and must be cross-checked against the official "
                          "injury report before use.",
    }


def parlay_vig_scaling(max_legs: int = 6, american: int = -110) -> list[dict]:
    """How much of a parlay's payout the vig removes, leg by leg. Pure arithmetic."""
    dec_leg = 1 + (american / 100 if american > 0 else 100 / abs(american))
    p_leg = 1 / dec_leg
    rows = []
    for n in range(2, max_legs + 1):
        dec = dec_leg ** n
        p_book = 1 / dec
        p_fair_per_leg = 0.5
        p_fair = p_fair_per_leg ** n
        rows.append({
            "legs": n,
            "book_decimal_odds": round(dec, 4),
            "book_american": _to_american(p_book),
            "book_implied_prob": round(p_book, 6),
            "fair_implied_prob_50_50": round(p_fair, 6),
            "hold_pct": round((p_book - p_fair) / p_book * 100, 3),
            "fair_american": _to_american(p_fair),
        })
    return rows


def _to_american(p: float) -> int:
    p = min(max(p, 1e-9), 1 - 1e-9)
    return int(round(-100 * p / (1 - p))) if p > 0.5 else int(round(100 * (1 - p) / p))


def build(df: pd.DataFrame) -> dict:
    return {
        "prop_correlation": {
            "verified": False,
            "status": "UNVERIFIED",
            "why": "No historical player-prop line archive is reachable from this "
                   "environment. Prop-to-prop correlations therefore cannot be measured "
                   "from outcomes, and no number is published rather than an estimate.",
            "what_would_fix_it": [
                "A licensed prop-line history (e.g. a sportsbook API or a paid odds "
                "archive) for at least three seasons, with closing prices.",
                "Player-week box scores joined by game id, so each prop can be settled.",
                "Enough same-game prop pairs to estimate a phi coefficient per pair.",
            ],
            "structural_relationships_only": STRUCTURAL,
        },
        "team_score_correlation": team_game_correlation(df),
        "slate": slate_structure(),
        "parlay_vig": parlay_vig_scaling(),
        "recommendation": (
            "Until prop history exists, price player-prop combos with the structural "
            "sign map plus a wide safety margin, and treat the game-level correlations "
            "in correlation.json as the only verified correlation inputs."
        ),
    }
