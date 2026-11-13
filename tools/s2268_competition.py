#!/usr/bin/env python3
"""Session 2268bfb2 - the pre-registered signal competition.

WHAT THIS IS
------------
A walk-forward scoring harness for candidate NFL signals, run against the frozen
weeks 1-9 corpus in data/games_2026_wk1_9.csv (136 games, every row carrying its own
official nfl.com game URL). It exists because the leaderboard on the site has never
scored anything: 14 strategies sat at "T0 - prospective, 0 of 14 gates" with every
performance cell reading "not published". This harness scores real strategies on real
settled games so the leaderboard has something true on it - and so the gates that still
block real-money staking are visible in public.

WHAT THIS IS NOT
----------------
It is not a betting record. No market price exists anywhere in this repository (Q-01 is
still open), so no closing line, no vig and therefore no CLV, no ROI and no units are
published. Every economics cell that would need a price is written as an empty string and
rendered as "not published". The competition ranks FORECAST AND SELECTION SKILL, which is
measurable without a price, and it says so.

THE THREE THINGS THAT REMOVE LUCK
---------------------------------
1. Split.    Coefficients are fitted on weeks 2-4 only and applied unchanged to the
             weeks 5-9 holdout. Nothing fitted ever sees a holdout game.
2. Point in time. Every team feature for a game is computed from games with a strictly
             smaller week number. A week 6 game knows weeks 1-5 and nothing else.
3. Pre-registration. The strategy definitions below are hashed (SHA-256) before any
             result is computed, the hash is written to data/s2268_preregistration.json,
             and this script refuses to run if the definitions ever change without the
             hash being re-cut. Adding a strategy after seeing results is the whole
             failure mode this exists to prevent; it now leaves a visible seam.

Then the statistics: exact binomial tests, Benjamini-Hochberg across the candidate set, a
seeded Monte Carlo that asks what ten coin-flipping selectors would have produced, and the
sample size each observed effect would need before it could be believed.

Deterministic: same inputs -> byte-identical outputs. The only randomness is the Monte
Carlo, seeded from a fixed constant.
"""

from __future__ import annotations

import csv
import datetime as _dt
import hashlib
import json
import math
import os
import random
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

CORPUS = os.path.join(DATA, "games_2026_wk1_9.csv")
WK10_PLAYED = os.path.join(DATA, "games_2026_wk10_played.csv")

FETCH_UTC = "2026-11-13T12:40Z"
SEED = 20261113
TRAIN_WEEKS = (2, 3, 4)          # where coefficients are fitted
HOLDOUT_WEEKS = (5, 6, 7, 8, 9)  # where everything is scored
PYTH_EXP = 2.37                  # pre-registered Pythagorean exponent
SHRINK_K = 30.0                  # pre-registered shrinkage constant, n/(n+K)

# What the shrinkage constant MEANS is part of the pre-registration, because an earlier
# cut of this harness shrank the fitted prediction toward zero instead of toward the
# do-nothing baseline and thereby made the totals model worse than knowing nothing.
SHRINK_RULE = (
    "Fitted predictions are shrunk TOWARD THE DO-NOTHING BASELINE, never toward zero: "
    "pred = baseline + (n_train / (n_train + K)) * (ols_prediction - baseline). "
    "The spread baseline is the point-in-time mean home margin (0.00 at a neutral site); "
    "the total baseline is the point-in-time league mean game total."
)
MC_DRAWS = 20000
BH_FDR = 0.10

# Corpus writes the Rams as LA; the rest of the repository writes LAR.
ALIAS = {"LA": "LAR", "LAR": "LA"}

# Official pages every published row points back at. Weeks 2-4 are the training window,
# weeks 5-9 the holdout; a measurement inherits its provenance from the games it used, and
# each of those games carries its own nfl.com page inside the frozen corpus.
W2 = "https://www.nfl.com/scores/2026/week-2"
W4 = "https://www.nfl.com/scores/2026/week-4"
W5 = "https://www.nfl.com/scores/2026/week-5"
W9 = "https://www.nfl.com/scores/2026/week-9"
GH_PRE = "https://github.com/kanlerxz87-cyber/NFL2/blob/main/data/s2268_preregistration.json"
GH_TOOL = "https://github.com/kanlerxz87-cyber/NFL2/blob/main/tools/s2268_competition.py"


# ----------------------------------------------------------------------------------
# Pre-registered definitions.  Editing this block changes the hash and the run will
# refuse to reproduce the published register until the hash is deliberately re-cut.
# ----------------------------------------------------------------------------------

STRATEGY_DEFS = [
    # id, name, track, market, family, rule, abstain rule, pre-registered note
    ("P-HOME", "Home side", "pick", "moneyline side", "venue",
     "Select the home team.",
     "Abstain on neutral-site games.",
     "The home-field control. Everything else has to beat this, not 50%."),
    ("P-AWAY", "Away side", "pick", "moneyline side", "venue",
     "Select the away team.",
     "Abstain on neutral-site games.",
     "Negative control. If the harness is sound this must not rank highly."),
    ("P-PD", "Point-differential favourite", "pick", "moneyline side", "level",
     "Select the team with the higher season-to-date points-scored-minus-allowed per game.",
     "Abstain when the two rates are within 0.50 points of each other.",
     "The obvious favourite signal; the bar any availability signal has to clear."),
    ("P-PYTH", "Pythagorean favourite", "pick", "moneyline side", "level",
     "Select the team with the higher Pythagorean expectation, exponent 2.37, from season-to-date points for and against.",
     "Abstain when the two expectations are within 0.020 of each other.",
     "The same idea with the blowout noise damped."),
    ("P-L3", "Last-three momentum", "pick", "moneyline side", "momentum",
     "Select the team with the better point differential over its last three games.",
     "Abstain if either team has fewer than three games played or the two are exactly equal.",
     "Short-window recency. Expected to be the noisiest real signal here."),
    ("P-REST", "Rest advantage", "pick", "moneyline side", "scheduling",
     "Select the team with more days since its previous game.",
     "Abstain unless the difference in rest is at least two days.",
     "Selective by construction: it only fires on bye and short-week mismatches."),
    ("P-CONTRA", "Contrarian dog", "pick", "moneyline side", "level",
     "Select the team with the WORSE season-to-date point differential per game.",
     "Abstain when the two rates are within 0.50 points of each other.",
     "Second negative control. It exists to price the multiple-comparisons problem."),
    ("P-SPREAD-MODEL", "Our originated spread", "pick", "moneyline side", "model",
     "Select the side our own fitted spread model favours (the sign of the predicted home margin).",
     "Abstain when the absolute predicted home margin is below 1.00 point.",
     "Uses the coefficients fitted on weeks 2-4 only."),
    ("P-FAV-DOG", "Home unless clearly worse", "pick", "moneyline side", "composite",
     "Select the home team unless the away team's point differential per game is better by more than 7.00 points.",
     "Abstain on neutral-site games.",
     "Home field plus a threshold, i.e. the simplest version of a real handicap model."),
    ("P-SOS", "Schedule-adjusted differential", "pick", "moneyline side", "level",
     "Select the team with the higher point differential per game after subtracting the average point differential per game of the opponents it has faced.",
     "Abstain when the two adjusted rates are within 0.50 points of each other.",
     "Strength of schedule, one iteration, no convergence."),
]

FORECAST_DEFS = [
    ("F-SPREAD-ZERO", "spread", "Predict a home margin of exactly 0.00.",
     "The do-nothing baseline. A model that cannot beat this has no value."),
    ("F-SPREAD-HFA", "spread",
     "Predict the point-in-time mean home margin over all prior non-neutral games; predict 0.00 at a neutral site.",
     "Home-field-only baseline."),
    ("F-SPREAD-MODEL", "spread",
     "Predict a + b * (home point differential per game minus away point differential per game), with HFA suppressed at neutral sites. a and b are fitted on weeks 2-4 only and then frozen.",
     "Our own originated spread."),
    ("F-TOTAL-MEAN", "total", "Predict the point-in-time league mean game total.",
     "The do-nothing baseline for totals."),
    ("F-TOTAL-NAIVE", "total",
     "Predict 0.5 * (home points per game + away points per game) + 0.5 * (home points allowed per game + away points allowed per game).",
     "Raw team-rate total with no regression toward the mean."),
    ("F-TOTAL-MODEL", "total",
     "Predict c + d * x where x is the F-TOTAL-NAIVE quantity. c and d are fitted on weeks 2-4 only and then frozen.",
     "Our own originated total, shrunk toward the league mean by the fit."),
]

# Same-game legs used for the measured correlation matrix. These are the legs a
# same-game parlay or a prop combination would be built from.
SGP_LEGS = [
    ("L1", "Home team wins"),
    ("L2", "Game total finishes over our originated total"),
    ("L3", "Home margin beats our originated spread"),
    ("L4", "Home team scores 24 or more"),
    ("L5", "Away team scores 24 or more"),
    ("L6", "Final margin is 7 points or fewer"),
]


# ----------------------------------------------------------------------------------
# statistics
# ----------------------------------------------------------------------------------

def _betacf(a, b, x):
    tiny, eps, itmax = 1e-30, 3e-16, 300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < tiny:
        d = tiny
    d = 1.0 / d
    h = d
    for m in range(1, itmax + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < tiny:
            d = tiny
        c = 1.0 + aa / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < tiny:
            d = tiny
        c = 1.0 + aa / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            break
    return h


def betainc(a, b, x):
    """Regularised incomplete beta I_x(a,b)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    lbeta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
    front = math.exp(lbeta + a * math.log(x) + b * math.log1p(-x))
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _betacf(a, b, x) / a
    return 1.0 - math.exp(lbeta + b * math.log1p(-x) + a * math.log(x)) * _betacf(b, a, 1.0 - x) / b


def binom_pmf(k, n, p):
    if k < 0 or k > n:
        return 0.0
    return math.exp(math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)
                    + k * math.log(p) + (n - k) * math.log1p(-p))


def binom_two_sided(k, n, p=0.5):
    """Exact two-sided binomial test: P(X as or less likely than observed)."""
    if n == 0:
        return 1.0
    obs = binom_pmf(k, n, p)
    if obs == 0.0:
        return 0.0
    total = 0.0
    for i in range(n + 1):
        pi = binom_pmf(i, n, p)
        if pi <= obs * (1.0 + 1e-9):
            total += pi
    return min(1.0, total)


def t_two_sided(t, df):
    if df <= 0:
        return 1.0
    x = df / (df + t * t)
    return betainc(df / 2.0, 0.5, x)


def pearson(xs, ys):
    n = len(xs)
    if n < 3:
        return 0.0, 0, 1.0
    mx = sum(xs) / n
    my = sum(ys) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    sxx = sum((a - mx) ** 2 for a in xs)
    syy = sum((b - my) ** 2 for b in ys)
    if sxx <= 0 or syy <= 0:
        return 0.0, n, 1.0
    r = sxy / math.sqrt(sxx * syy)
    r = max(-0.999999, min(0.999999, r))
    if abs(r) >= 1.0:
        return r, n, 0.0
    t = r * math.sqrt((n - 2) / (1 - r * r))
    return r, n, t_two_sided(t, n - 2)


def phi(a, b):
    """Phi coefficient for two 0/1 series; equals Pearson r for binary data."""
    n = len(a)
    if n == 0:
        return 0.0, 0, 1.0
    return pearson([1.0 if v else 0.0 for v in a], [1.0 if v else 0.0 for v in b])


def benjamini_hochberg(pvals, fdr=BH_FDR):
    """Returns (adjusted_flags, adjusted_p) - flags True where the null is rejected."""
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    adj = [0.0] * m
    prev = 1.0
    for rank, idx in enumerate(reversed(order), start=1):
        k = m - rank + 1
        val = min(prev, pvals[idx] * m / k)
        adj[idx] = val
        prev = val
    thresh = 0.0
    flags = [False] * m
    for rank, idx in enumerate(order, start=1):
        if pvals[idx] <= fdr * rank / m:
            thresh = rank
    for rank, idx in enumerate(order, start=1):
        if rank <= thresh:
            flags[idx] = True
    return flags, adj


def required_n(p_obs, p_null, alpha=0.05, power=0.80):
    """Two-sided one-sample proportion test, normal approximation."""
    d = abs(p_obs - p_null)
    if d <= 0:
        return ""
    z_a, z_b = 1.959963985, 0.8416212336
    num = z_a * math.sqrt(p_null * (1 - p_null)) + z_b * math.sqrt(p_obs * (1 - p_obs))
    return int(math.ceil((num / d) ** 2))


# ----------------------------------------------------------------------------------
# data
# ----------------------------------------------------------------------------------

def load_corpus():
    rows = []
    with open(CORPUS, newline="") as fh:
        for r in csv.DictReader(fh, delimiter="|"):
            rows.append({
                "week": int(r["week"]),
                "date": r["date"],
                "away": r["away"],
                "home": r["home"],
                "away_pts": int(r["away_pts"]),
                "home_pts": int(r["home_pts"]),
                "neutral": r["neutral"] == "yes",
                "source": r["source"],
            })
    rows.sort(key=lambda r: (r["week"], r["date"], r["home"]))
    return rows


def team_state(rows, upto_week):
    """Per-team aggregates using only games with week < upto_week."""
    st = defaultdict(lambda: {"gp": 0, "pf": 0, "pa": 0, "last": None,
                              "recent": [], "opp": [], "home_pd": [0, 0], "away_pd": [0, 0]})
    for g in rows:
        if g["week"] >= upto_week:
            continue
        for side, other in (("home", "away"), ("away", "home")):
            s = st[g[side]]
            s["gp"] += 1
            s["pf"] += g[side + "_pts"]
            s["pa"] += g[other + "_pts"]
            s["recent"].append((g["week"], g[side + "_pts"] - g[other + "_pts"]))
            s["opp"].append(g[other])
            s["last"] = max(s["last"] or g["date"], g["date"])
            key = "home_pd" if side == "home" else "away_pd"
            s[key][0] += g[side + "_pts"] - g[other + "_pts"]
            s[key][1] += 1
    out = {}
    for team, s in st.items():
        gp = max(1, s["gp"])
        pf, pa = s["pf"], s["pa"]
        pyth = (pf ** PYTH_EXP) / ((pf ** PYTH_EXP) + (pa ** PYTH_EXP)) if (pf + pa) > 0 else 0.5
        recent = sorted(s["recent"], key=lambda t: -t[0])[:3]
        l3 = sum(v for _, v in recent) / len(recent) if recent else 0.0
        opp_pd = []
        for o in s["opp"]:
            os_ = st.get(o)
            if os_ and os_["gp"]:
                opp_pd.append((os_["pf"] - os_["pa"]) / os_["gp"])
        out[team] = {
            "gp": s["gp"],
            "pd_pg": (pf - pa) / gp,
            "pf_pg": pf / gp,
            "pa_pg": pa / gp,
            "pyth": pyth,
            "l3": l3,
            "sos": (sum(opp_pd) / len(opp_pd)) if opp_pd else 0.0,
            "last": s["last"],
            "home_pd_pg": (s["home_pd"][0] / s["home_pd"][1]) if s["home_pd"][1] else 0.0,
            "away_pd_pg": (s["away_pd"][0] / s["away_pd"][1]) if s["away_pd"][1] else 0.0,
        }
    return out


def _d(s):
    y, m, d = (int(x) for x in s.split("-"))
    return _dt.date(y, m, d)


def rest_days(state, team, game_date):
    """Whole days between the team's most recent prior game and this one.

    Computed with the calendar, not with an arithmetic approximation: an earlier cut of
    this file used y*365.25 + m*30.6 + d, which is not monotone across month boundaries
    and produced nonsense rest figures. Recorded in COORDINATION.md.
    """
    last = state.get(team, {}).get("last")
    if not last:
        return None
    return (_d(game_date) - _d(last)).days


def build_rows(corpus):
    """One record per game with strictly point-in-time features attached."""
    out = []
    for g in corpus:
        st = team_state(corpus, g["week"])
        h, a = st.get(g["home"]), st.get(g["away"])
        if h is None or a is None or h["gp"] == 0 or a["gp"] == 0:
            continue  # week 1: nothing is known yet
        rh = rest_days(st, g["home"], g["date"])
        ra = rest_days(st, g["away"], g["date"])
        prior = [x for x in corpus if x["week"] < g["week"] and not x["neutral"]]
        prior_tot = [x for x in corpus if x["week"] < g["week"]]
        out.append({
            "game": g,
            "week": g["week"],
            "date": g["date"],
            "home": g["home"],
            "away": g["away"],
            "neutral": g["neutral"],
            "home_pts": g["home_pts"],
            "away_pts": g["away_pts"],
            "hfa_pt": (sum(x["home_pts"] - x["away_pts"] for x in prior) / len(prior)) if prior else 0.0,
            "mean_total_pt": (sum(x["home_pts"] + x["away_pts"] for x in prior_tot) / len(prior_tot)) if prior_tot else 0.0,
            "h": h,
            "a": a,
            "rest_home": rh,
            "rest_away": ra,
            "margin": g["home_pts"] - g["away_pts"],   # home margin
            "total": g["home_pts"] + g["away_pts"],
            "home_won": 1 if g["home_pts"] > g["away_pts"] else (0 if g["home_pts"] < g["away_pts"] else -1),
            "source": g["source"],
        })
    return out


def ols(xs, ys):
    n = len(xs)
    if n < 3:
        return 0.0, 0.0
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx <= 0:
        return 0.0, my
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    b = sxy / sxx
    return b, my - b * mx


# ----------------------------------------------------------------------------------
# signals
# ----------------------------------------------------------------------------------

def naive_total(r):
    return 0.5 * (r["h"]["pf_pg"] + r["a"]["pf_pg"]) + 0.5 * (r["h"]["pa_pg"] + r["a"]["pa_pg"])


def spread_feature(r):
    return r["h"]["pd_pg"] - r["a"]["pd_pg"]


def fit_models(rows):
    """Fit on weeks 2-4, then freeze.

    The shrinkage blends the fitted prediction toward the DO-NOTHING BASELINE, not toward
    zero. An earlier cut shrank the intercept toward zero, which pushed every prediction
    away from the league mean and made the totals model worse than knowing nothing
    (MAE 18.76 vs 11.18). Recorded in COORDINATION.md; the rule is now part of the
    pre-registration hash so it cannot drift again without the hash being re-cut.
    """
    train = [r for r in rows if r["week"] in TRAIN_WEEKS]
    hold = [r for r in rows if r["week"] in HOLDOUT_WEEKS]
    non_neutral_train = [r for r in train if not r["neutral"]]

    xs = [spread_feature(r) for r in non_neutral_train]
    ys = [float(r["margin"]) for r in non_neutral_train]
    b_raw, a_raw = ols(xs, ys)
    shrink = len(non_neutral_train) / (len(non_neutral_train) + SHRINK_K)
    xt = [naive_total(r) for r in train]
    yt = [float(r["total"]) for r in train]
    d_raw, c_raw = ols(xt, yt)
    shrink_t = len(train) / (len(train) + SHRINK_K)
    coefs = {
        "spread_a_raw": a_raw, "spread_b_raw": b_raw,
        "total_c_raw": c_raw, "total_d_raw": d_raw,
        "n_train_spread": len(non_neutral_train), "n_train_total": len(train),
        "n_holdout": len(hold), "shrink_spread": shrink, "shrink_total": shrink_t,
    }
    return coefs


def pred_spread_model(r, c):
    """HFA baseline + shrunk (fitted - HFA). HFA is suppressed at a neutral site."""
    gap = spread_feature(r)
    if r["neutral"]:
        return c["shrink_spread"] * (c["spread_b_raw"] * gap)
    base = r["hfa_pt"]
    return base + c["shrink_spread"] * ((c["spread_a_raw"] + c["spread_b_raw"] * gap) - base)


def pred_total_model(r, c):
    base = r["mean_total_pt"]
    return base + c["shrink_total"] * ((c["total_c_raw"] + c["total_d_raw"] * naive_total(r)) - base)


def pred_spread_hfa(r, c):
    return 0.0 if r["neutral"] else r["hfa_pt"]


def forecast_predictors(r, c):
    return {
        "F-SPREAD-ZERO": 0.0,
        "F-SPREAD-HFA": pred_spread_hfa(r, c),
        "F-SPREAD-MODEL": pred_spread_model(r, c),
        "F-TOTAL-MEAN": r["mean_total_pt"],
        "F-TOTAL-NAIVE": naive_total(r),
        "F-TOTAL-MODEL": pred_total_model(r, c),
    }


def pick_side(r, c):
    """Returns {strategy_id: 'home' | 'away' | None}."""
    out = {}
    gap = r["h"]["pd_pg"] - r["a"]["pd_pg"]
    pyth_gap = r["h"]["pyth"] - r["a"]["pyth"]
    l3_gap = r["h"]["l3"] - r["a"]["l3"]
    sos_h = r["h"]["pd_pg"] - r["h"]["sos"]
    sos_a = r["a"]["pd_pg"] - r["a"]["sos"]

    out["P-HOME"] = None if r["neutral"] else "home"
    out["P-AWAY"] = None if r["neutral"] else "away"
    out["P-PD"] = "home" if gap > 0.5 else ("away" if gap < -0.5 else None)
    out["P-PYTH"] = "home" if pyth_gap > 0.020 else ("away" if pyth_gap < -0.020 else None)
    out["P-L3"] = ("home" if l3_gap > 0 else ("away" if l3_gap < 0 else None)
                   if (r["h"]["gp"] >= 3 and r["a"]["gp"] >= 3) else None)
    rh, ra = r["rest_home"], r["rest_away"]
    if rh is None or ra is None or abs(rh - ra) < 2:
        out["P-REST"] = None
    else:
        out["P-REST"] = "home" if rh > ra else "away"
    out["P-CONTRA"] = "away" if gap > 0.5 else ("home" if gap < -0.5 else None)
    pm = pred_spread_model(r, c)
    out["P-SPREAD-MODEL"] = ("home" if pm > 1.0 else ("away" if pm < -1.0 else None))
    out["P-FAV-DOG"] = (None if r["neutral"] else ("away" if gap < -7.0 else "home"))
    out["P-SOS"] = "home" if (sos_h - sos_a) > 0.5 else ("away" if (sos_h - sos_a) < -0.5 else None)
    return out


# ----------------------------------------------------------------------------------
# output helpers
# ----------------------------------------------------------------------------------

def write_csv(name, header, rows):
    path = os.path.join(DATA, name)
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, delimiter="|", lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)
    return path


def fmt(v, nd=2):
    if v == "" or v is None:
        return ""
    if isinstance(v, str):
        return v
    if isinstance(v, int):
        return str(v)
    return f"{v:.{nd}f}"


def sha_defs():
    blob = json.dumps({"strategies": STRATEGY_DEFS, "forecasts": FORECAST_DEFS,
                       "legs": SGP_LEGS, "train": TRAIN_WEEKS, "holdout": HOLDOUT_WEEKS,
                       "pyth": PYTH_EXP, "shrink_K": SHRINK_K, "shrink_rule": SHRINK_RULE,
                       "seed": SEED},
                      sort_keys=True).encode()
    return hashlib.sha256(blob).hexdigest()


# ----------------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------------

def main():
    corpus = load_corpus()
    rows = build_rows(corpus)
    coefs = fit_models(rows)
    hold = [r for r in rows if r["week"] in HOLDOUT_WEEKS]
    digest = sha_defs()

    # ---- pre-registration -------------------------------------------------------
    prereg_path = os.path.join(DATA, "s2268_preregistration.json")
    if os.path.exists(prereg_path):
        with open(prereg_path) as fh:
            known = json.load(fh).get("definitions_sha256")
        if known != digest:
            raise SystemExit(
                "the strategy definitions changed after they were pre-registered.\n"
                f"  recorded : {known}\n  computed : {digest}\n"
                "Re-cut the hash deliberately (delete data/s2268_preregistration.json) "
                "and say so in COORDINATION.md; do not quietly move the goalposts.")
    with open(prereg_path, "w") as fh:
        json.dump({
            "session": "2268bfb2",
            "definitions_sha256": digest,
            "frozen_at_utc": FETCH_UTC,
            "train_weeks": list(TRAIN_WEEKS),
            "holdout_weeks": list(HOLDOUT_WEEKS),
            "corpus": "data/games_2026_wk1_9.csv (136 games, weeks 1-9, 2026)",
            "n_strategies": len(STRATEGY_DEFS),
            "n_forecasts": len(FORECAST_DEFS),
            "note": "Definitions hashed before any result was computed. The scorer refuses "
                    "to run if the hash does not match, so adding a strategy after seeing "
                    "the leaderboard is a visible act, not a silent one.",
        }, fh, indent=2)

    # ---- register ---------------------------------------------------------------
    write_csv("s2268_strategy_register.csv",
              ["id", "name", "track", "market", "family", "selection_rule",
               "abstention_rule", "pre_registration_note", "definitions_sha256", "source"],
              [[d[0], d[1], d[2], d[3], d[4], d[5], d[6], d[7], digest, GH_PRE]
               for d in STRATEGY_DEFS])

    # ---- decisions --------------------------------------------------------------
    decisions = []
    picks_by_game = defaultdict(dict)
    for r in hold:
        p = pick_side(r, coefs)
        for sid, side in p.items():
            if side is None:
                continue
            if r["home_won"] == -1:
                result = "push"      # a tied game settles no side bet
            else:
                won = 1 if ((side == "home" and r["home_won"] == 1) or
                            (side == "away" and r["home_won"] == 0)) else 0
                result = won
            if result != "push":
                picks_by_game[(r["week"], r["home"], r["away"])][sid] = result
            decisions.append({
                "week": r["week"], "date": r["date"], "game": f"{r['away']} @ {r['home']}",
                "strategy": sid, "side": side, "won": result, "source": r["source"],
            })
    write_csv("s2268_holdout_decisions.csv",
              ["week", "date", "game", "strategy", "side_selected", "result", "source"],
              [[d["week"], d["date"], d["game"], d["strategy"], d["side"],
                ("push" if d["won"] == "push" else ("win" if d["won"] else "loss")), d["source"]]
               for d in decisions])

    # rest audit - every decision the rest signal made, with the days it saw
    rest_rows = []
    for r in hold:
        if r["rest_home"] is None or r["rest_away"] is None:
            continue
        p = pick_side(r, coefs)
        if p["P-REST"] is None:
            continue
        sel, oth = ("home", "away") if p["P-REST"] == "home" else ("away", "home")
        rs = r["rest_" + sel]
        ro = r["rest_" + oth]
        res = "push" if r["home_won"] == -1 else ("win" if ((sel == "home" and r["home_won"] == 1) or
                                                            (sel == "away" and r["home_won"] == 0)) else "loss")
        rest_rows.append([r["week"], r["date"], f"{r['away']} @ {r['home']}", r[sel], rs, r[oth], ro,
                          abs(rs - ro), res, r["source"]])
    write_csv("s2268_rest_audit.csv",
              ["week", "date", "game", "team_selected", "rest_days_selected",
               "team_other", "rest_days_other", "rest_gap", "result", "source"],
              rest_rows)

    # ---- pick scoring -----------------------------------------------------------
    rng = random.Random(SEED)
    strat_ids = [s[0] for s in STRATEGY_DEFS]
    pick_rows, pvals = [], []
    per_strat = {}
    for sid in strat_ids:
        ds = [d for d in decisions if d["strategy"] == sid and d["won"] != "push"]
        n = len(ds)
        hits = sum(d["won"] for d in ds)
        if n == 0:
            pick_rows.append([sid, 0, 0, "", "", "", "", "", "", "", "", "", ""])
            pvals.append(1.0)
            per_strat[sid] = {"n": 0, "hits": 0, "rate": 0.0}
            continue
        rate = hits / n
        p = binom_two_sided(hits, n, 0.5)
        pvals.append(p)
        base_null = 0.5
        ll = -(sum(math.log(max(1e-12, rate)) for _ in range(hits)) +
               sum(math.log(max(1e-12, 1 - rate)) for _ in range(n - hits))) / n if 0 < hits < n else (
            0.0 if hits == n else float("inf"))
        ll = min(ll, 50.0)
        req = required_n(rate, base_null)
        per_strat[sid] = {"n": n, "hits": hits, "rate": rate, "p": p, "ll": ll, "req": req}
        pick_rows.append([sid, n, hits, fmt(rate, 4), fmt(rate - 0.5, 4), fmt(p, 4),
                          "", fmt(ll, 4), "", fmt(req) if req else "",
                          "", ""])  # placeholders filled after BH / MC

    bh_flags, bh_adj = benjamini_hochberg(pvals, BH_FDR)

    # Monte Carlo: ten independent coin-flip selectors with the same n as ours.
    ns = [per_strat[s]["n"] for s in strat_ids]
    best_rates = []
    for _ in range(MC_DRAWS):
        best = 0.0
        for n in ns:
            if n == 0:
                continue
            k = sum(1 for _ in range(n) if rng.random() < 0.5)
            best = max(best, k / n)
        best_rates.append(best)
    best_rates.sort()
    def mc_percentile(x):
        lo, hi = 0, len(best_rates)
        while lo < hi:
            mid = (lo + hi) // 2
            if best_rates[mid] < x:
                lo = mid + 1
            else:
                hi = mid
        return lo / len(best_rates)
    mc_best_mean = sum(best_rates) / len(best_rates)
    mc_best_p95 = best_rates[int(0.95 * len(best_rates))]
    actual_best = max((per_strat[s]["rate"] for s in strat_ids if per_strat[s]["n"]), default=0.0)

    # per-strategy: what ONE coin-flipping selector with the same n would produce
    single_pct = {}
    for s_ in strat_ids:
        n_ = per_strat[s_]["n"]
        if not n_:
            single_pct[s_] = ""
            continue
        draws = sorted(sum(1 for _ in range(n_) if rng.random() < 0.5) / n_
                       for _ in range(MC_DRAWS // 2 or 1))
        x = per_strat[s_]["rate"]
        lo, hi = 0, len(draws)
        while lo < hi:
            mid = (lo + hi) // 2
            if draws[mid] < x:
                lo = mid + 1
            else:
                hi = mid
        single_pct[s_] = lo / len(draws)

    for i, sid in enumerate(strat_ids):
        s = per_strat[sid]
        if not s["n"]:
            continue
        pick_rows[i][6] = fmt(bh_adj[i], 4)
        pick_rows[i][7] = "yes" if bh_flags[i] else "no"
        pick_rows[i][10] = fmt(mc_percentile(s["rate"]), 4)
        pick_rows[i][11] = fmt(1.0 - (1.0 - s["rate"]) ** 1, 4) if False else ""

    # rebuild cleanly with the right column order
    pick_rows = []
    for i, sid in enumerate(strat_ids):
        s = per_strat[sid]
        name = next(x[1] for x in STRATEGY_DEFS if x[0] == sid)
        if not s["n"]:
            pick_rows.append([sid, name, 0, 0, "", "", "", "", "", "", "", "", "", "", "", ""])
            continue
        pick_rows.append([
            sid, name, s["n"], s["hits"], fmt(s["rate"], 4), fmt(s["rate"] - 0.5, 4),
            fmt(s["p"], 4), fmt(bh_adj[i], 4), "yes" if bh_flags[i] else "no",
            fmt(s["ll"], 4), fmt(s["req"]) if isinstance(s["req"], int) else "",
            fmt(mc_percentile(s["rate"]), 4), fmt(single_pct[sid], 4), "", "",
        ])
    write_csv("s2268_pick_scores.csv",
              ["id", "name", "decisions", "wins", "hit_rate", "edge_over_coin_flip",
               "binomial_p_two_sided", "bh_adjusted_p", "survives_fdr_0_10",
               "log_loss", "required_n_for_80pct_power",
               "monte_carlo_percentile_best_of_ten", "monte_carlo_percentile_single_selector",
               "roi_units_per_100", "closing_line_value",
               "source_first_week", "source_last_week", "sample_scope"],
              [[r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[12],
                r[13], r[14], W5, W9, "weeks 5-9 holdout"] for r in pick_rows])

    # ---- forecast scoring -------------------------------------------------------
    fc_rows = []
    for fid, track, rule, note in FORECAST_DEFS:
        actual = [float(r["margin"] if track == "spread" else r["total"]) for r in hold]
        preds = [forecast_predictors(r, coefs)[fid] for r in hold]
        errs = [p - a for p, a in zip(preds, actual)]
        mae = sum(abs(e) for e in errs) / len(errs)
        rmse = math.sqrt(sum(e * e for e in errs) / len(errs))
        bias = sum(errs) / len(errs)
        flat = len(set(round(p, 10) for p in preds)) <= 1
        r, n, pv = pearson(preds, actual)
        fc_rows.append([fid, track, len(hold), fmt(mae), fmt(rmse), fmt(bias),
                        "" if flat else fmt(r, 4), "" if flat else fmt(r * r, 4),
                        "" if flat else fmt(pv, 5), "", "", rule, note])
    # paired comparisons: our model vs each baseline, on the same games
    base_spread = next(x for x in fc_rows if x[0] == "F-SPREAD-ZERO")
    base_total = next(x for x in fc_rows if x[0] == "F-TOTAL-MEAN")
    for row in fc_rows:
        fid, track = row[0], row[1]
        actual = [float(r["margin"] if track == "spread" else r["total"]) for r in hold]
        preds_m = [forecast_predictors(r, coefs)[fid] for r in hold]
        preds_b = [forecast_predictors(r, coefs)["F-SPREAD-ZERO" if track == "spread" else "F-TOTAL-MEAN"] for r in hold]
        wins = sum(1 for pm, pb, a in zip(preds_m, preds_b, actual) if abs(pm - a) < abs(pb - a))
        losses = sum(1 for pm, pb, a in zip(preds_m, preds_b, actual) if abs(pm - a) > abs(pb - a))
        if fid in ("F-SPREAD-ZERO", "F-TOTAL-MEAN"):
            row[9], row[10] = "", ""   # a baseline cannot beat itself
        else:
            row[9] = fmt(wins / len(hold), 4)
            row[10] = fmt(binom_two_sided(wins, wins + losses, 0.5), 4) if (wins + losses) else ""
    write_csv("s2268_forecast_scores.csv",
              ["id", "track", "games_scored", "mae", "rmse", "mean_bias",
               "pearson_r_vs_actual", "r_squared", "p_value",
               "beats_baseline_rate", "beats_baseline_binomial_p", "rule", "note",
               "source_first_week", "source_last_week", "sample_scope"],
              [[r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[12],
                W5, W9, "weeks 5-9 holdout"] for r in fc_rows])

    # ---- forecast coefficient table --------------------------------------------
    coef_rows = [
        ["spread_intercept_unshrunk", fmt(coefs["spread_a_raw"], 4),
         "weeks 2-4, non-neutral games", coefs["n_train_spread"],
         fmt(coefs["shrink_spread"], 4),
         "Applied as baseline + k * (this - baseline); baseline is the point-in-time mean home margin"],
        ["spread_slope_on_pd_gap_unshrunk", fmt(coefs["spread_b_raw"], 4),
         "weeks 2-4, non-neutral games", coefs["n_train_spread"],
         fmt(coefs["shrink_spread"], 4), "Slope on home PD/game minus away PD/game"],
        ["total_intercept_unshrunk", fmt(coefs["total_c_raw"], 4), "weeks 2-4, all games",
         coefs["n_train_total"], fmt(coefs["shrink_total"], 4),
         "Applied as baseline + k * (this - baseline); baseline is the point-in-time league mean total"],
        ["total_slope_on_team_rate_unshrunk", fmt(coefs["total_d_raw"], 4),
         "weeks 2-4, all games", coefs["n_train_total"], fmt(coefs["shrink_total"], 4),
         "Slope on half the sum of both teams' points-for and points-allowed rates"],
        ["pythagorean_exponent", fmt(PYTH_EXP, 4), "not fitted - pre-registered", "", "", ""],
        ["shrinkage_constant_K", fmt(SHRINK_K, 2), "not fitted - pre-registered", "", "", ""],
        ["shrinkage_rule", SHRINK_RULE, "not fitted - pre-registered", "", "", "part of the hash"],
        ["monte_carlo_seed", SEED, "not fitted - pre-registered", "", "", ""],
    ]
    write_csv("s2268_model_coefficients.csv",
              ["term", "value", "fitted_on", "n_train", "shrinkage_applied", "note",
               "source_first_training_week", "source_last_training_week"],
              [r + [W2, W4] for r in coef_rows])

    # ---- correlations: predictors vs outcomes -----------------------------------
    corr_rows = []
    sp_pred = [pred_spread_model(r, coefs) for r in hold]
    to_pred = [pred_total_model(r, coefs) for r in hold]
    sp_act = [float(r["margin"]) for r in hold]
    to_act = [float(r["total"]) for r in hold]
    for label, xs, ys in [("originated spread vs actual home margin", sp_pred, sp_act),
                          ("originated total vs actual game total", to_pred, to_act),
                          ("naive team-rate total vs actual game total", [naive_total(r) for r in hold], to_act),
                          ("point-differential gap vs actual home margin", [spread_feature(r) for r in hold], sp_act)]:
        r_, n_, p_ = pearson(xs, ys)
        corr_rows.append([label, n_, fmt(r_, 4), fmt(r_ * r_, 4), fmt(p_, 5), "weeks 5-9 holdout"])
    write_csv("s2268_predictor_correlations.csv",
              ["relationship", "n", "pearson_r", "r_squared", "p_value", "sample_scope",
               "source_first_week", "source_last_week"],
              [[r[0], r[1], r[2], r[3], r[4], r[5], W5, W9] for r in corr_rows])

    # ---- same-game leg correlation matrix (the SGP / prop-combo exhibit) --------
    leg_vals = {}
    for lid, _ in SGP_LEGS:
        vals = []
        for r, sp, tp in zip(hold, sp_pred, to_pred):
            if lid == "L1":
                vals.append(r["home_won"])
            elif lid == "L2":
                vals.append(1 if r["total"] > tp else 0)
            elif lid == "L3":
                vals.append(1 if r["margin"] > sp else 0)
            elif lid == "L4":
                vals.append(1 if r["home_pts"] >= 24 else 0)
            elif lid == "L5":
                vals.append(1 if r["away_pts"] >= 24 else 0)
            else:
                vals.append(1 if abs(r["margin"]) <= 7 else 0)
        leg_vals[lid] = vals
    sgp_rows = []
    for i, (lid_a, desc_a) in enumerate(SGP_LEGS):
        for lid_b, desc_b in SGP_LEGS[i + 1:]:
            r_, n_, p_ = phi(leg_vals[lid_a], leg_vals[lid_b])
            pa = sum(leg_vals[lid_a]) / n_
            pb = sum(leg_vals[lid_b]) / n_
            sgp_rows.append([f"{lid_a} x {lid_b}", desc_a, desc_b, n_,
                             fmt(pa, 4), fmt(pb, 4), fmt(pa * pb, 4),
                             "", fmt(r_, 4), fmt(p_, 4)])
    # joint (actual both-legs-hit) rate fills column 8
    for row in sgp_rows:
        a, b = row[0].split(" x ")
        joint = sum(1 for x, y in zip(leg_vals[a], leg_vals[b]) if x and y) / len(leg_vals[a])
        row[7] = fmt(joint, 4)
    write_csv("s2268_sgp_correlations.csv",
              ["pair", "leg_a", "leg_b", "n", "rate_a", "rate_b",
               "rate_if_independent", "actual_joint_rate", "phi_correlation", "p_value",
               "source_first_week", "source_last_week"],
              [[r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], W5, W9]
               for r in sgp_rows])

    # ---- strategy outcome correlation matrix (parlay building block) ------------
    strat_corr = []
    for i, sa in enumerate(strat_ids):
        for sb in strat_ids[i + 1:]:
            common = [k for k in picks_by_game if sa in picks_by_game[k] and sb in picks_by_game[k]]
            if len(common) < 10:
                strat_corr.append([f"{sa} x {sb}", len(common), "", "", "", "", "too few common decisions to estimate"])
                continue
            va = [picks_by_game[k][sa] for k in common]
            vb = [picks_by_game[k][sb] for k in common]
            ra = sum(va) / len(va)
            rb = sum(vb) / len(vb)
            r_, n_, p_ = phi(va, vb)
            strat_corr.append([f"{sa} x {sb}", n_, fmt(ra, 4), fmt(rb, 4), fmt(ra * rb, 4),
                               fmt(sum(1 for x, y in zip(va, vb) if x and y) / n_, 4),
                               fmt(r_, 4)])
    write_csv("s2268_strategy_correlations.csv",
              ["pair", "n_common_decisions", "rate_a", "rate_b",
               "rate_if_independent", "actual_both_win_rate", "phi_correlation",
               "source_first_week", "source_last_week"],
              [[r[0], r[1], r[2], r[3], r[4], r[5], r[6], W5, W9] for r in strat_corr])

    # ---- parlays ----------------------------------------------------------------
    # Parlays are built DISJOINT: within a week the games a strategy bet are taken in
    # corpus order and grouped into consecutive pairs (or triples) that share no game.
    # That makes each parlay an independent observation, so the binomial test against the
    # independent-product rate is actually valid. The overlapping enumeration that a
    # careless build would use (every pair of games in a week) is counted too, and
    # published, and labelled as what it is: several hundred parlays built from a few
    # dozen games, sharing legs, whose p-values would be nonsense.
    by_week = defaultdict(list)
    for (wk, h, a), d in picks_by_game.items():
        by_week[wk].append((sorted([str(h), str(a)]), d))
    for wk in by_week:
        by_week[wk].sort()

    def disjoint_parlays(size, strat_list):
        """Returns (parlays, hits, marginal_product_sum, games_reused_flag)."""
        parlays, hits, prod = 0, 0, 0.0
        for wk, items in sorted(by_week.items()):
            usable = [(k, d) for k, d in items if all(x in d for x in strat_list)]
            i = 0
            while i + size <= len(usable):
                chunk = usable[i:i + size]
                i += size
                if len({tuple(c[0]) for c in chunk}) != size:
                    continue
                parlays += 1
                ok = all(chunk[j][1][strat_list[j]] if len(strat_list) > 1 else chunk[j][1][strat_list[0]]
                         for j in range(size))
                hits += 1 if ok else 0
                pr = 1.0
                for j in range(size):
                    sid = strat_list[j] if len(strat_list) > 1 else strat_list[0]
                    pr *= per_strat[sid]["rate"] if per_strat[sid]["n"] else 0.0
                prod += pr
        return parlays, hits, prod

    parlay_rows = []
    for sid in strat_ids:
        for size in (2, 3):
            n_par, hits, prod = disjoint_parlays(size, [sid])
            if n_par < 5:
                parlay_rows.append(["disjoint", size, sid, "", "", n_par, "no", "", "", "", "",
                                    "fewer than five disjoint parlays can be formed; not published"])
                continue
            rate = hits / n_par
            indep = prod / n_par
            parlay_rows.append(["disjoint", size, sid, "", "", n_par, "no", fmt(rate, 4),
                                fmt(indep, 4), fmt(rate - indep, 4),
                                fmt(binom_two_sided(hits, n_par, indep), 4),
                                "each parlay uses a different game, so the observations are independent"])
    for i, sa in enumerate(strat_ids):
        for sb in strat_ids[i + 1:]:
            n_par, hits, prod = disjoint_parlays(2, [sa, sb])
            if n_par < 5:
                parlay_rows.append(["disjoint", 2, sa, sb, "", n_par, "no", "", "", "", "",
                                    "fewer than five disjoint parlays can be formed; not published"])
                continue
            rate = hits / n_par
            indep = prod / n_par
            parlay_rows.append(["disjoint", 2, sa, sb, "", n_par, "no", fmt(rate, 4),
                                fmt(indep, 4), fmt(rate - indep, 4),
                                fmt(binom_two_sided(hits, n_par, indep), 4),
                                "the two legs come from different games, so the binomial test is valid"])

    # the overlapping enumeration, published and labelled
    overlap = 0
    for wk, items in by_week.items():
        for (ka, da), (kb, db) in [(x, y) for x in items for y in items]:
            if ka == kb:
                continue
            for sid in strat_ids:
                if sid in da and sid in db:
                    overlap += 1
    parlay_rows.append(["overlapping enumeration", 2, "any single strategy", "", "", overlap, "yes",
                        "", "", "", "",
                        "Every in-week pair of games is crossed, so each game appears in many "
                        "parlays at once. The count is real, the sample size is not: any p-value "
                        "computed on these rows would treat shared legs as fresh evidence. "
                        "Published so the number is on the record and nobody re-derives it "
                        "believing it is 800 observations."])
    write_csv("s2268_parlays.csv",
              ["construction", "legs", "strategy_a", "strategy_b", "strategy_c",
               "parlays_formed", "legs_shared_between_parlays", "actual_hit_rate",
               "rate_if_independent", "correlation_gap", "binomial_p_vs_independent", "note",
               "source_first_week", "source_last_week"],
              [[r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11], W5, W9]
               for r in parlay_rows])

    # ---- luck -------------------------------------------------------------------
    luck_rows = [
        ["holdout games scored", len(hold), "", "weeks 5-9 of the frozen 2026 corpus", ""],
        ["candidate strategies scored", len(strat_ids), "", "two of them are deliberate negative controls", ""],
        ["coin-flip null", "0.5000", "", "a side selector must beat this before anything else matters", ""],
        ["best hit rate achieved", fmt(actual_best, 4), "", "across all ten candidates", ""],
        ["Monte Carlo draws", MC_DRAWS, "", f"seeded {SEED}", ""],
        ["Monte Carlo mean best-of-ten rate", fmt(mc_best_mean, 4), "",
         "what ten coin flippers produce by chance alone", ""],
        ["Monte Carlo 95th percentile best-of-ten rate", fmt(mc_best_p95, 4), "",
         "one in twenty runs of pure luck beats this", ""],
        ["is the observed best beyond the luck 95th percentile",
         "yes" if actual_best > mc_best_p95 else "no", "",
         "the single most important number on this page", ""],
        ["expected false positives at p<0.05 with ten candidates", "0.50", "",
         "0.05 x 10, before any correction", ""],
        ["Benjamini-Hochberg FDR", fmt(BH_FDR, 2), "", "applied across the ten candidates", ""],
        ["candidates surviving FDR", sum(1 for f in bh_flags if f), "", "", ""],
        ["price feed present in the repository", "no", "", "Q-01 still open", ""],
        ["ROI per 100 units", "", "", "not published - needs a closing price", ""],
        ["closing line value", "", "", "not published - needs a closing price", ""],
        ["player prop archive", "", "", "not published - no prop line history exists here", W9],
    ]
    write_csv("s2268_luck.csv",
              ["measure", "value", "unit", "note", "source"],
              [r[:4] + [W9 if r[4] == "" else r[4]] for r in luck_rows])

    # ---- gates ------------------------------------------------------------------
    n_bh = sum(1 for f in bh_flags if f)
    gate_rows = [
        ["G-C1", "point-in-time features", "hard", "every strategy",
         "Each decision uses only games with a strictly smaller week number",
         "0 look-ahead rows", "PASS", "enforced by construction: build_rows() cannot see future weeks"],
        ["G-C2", "fit/test separation", "hard", "both fitted models",
         f"Coefficients fitted on weeks {TRAIN_WEEKS[0]}-{TRAIN_WEEKS[-1]} only, frozen, then applied to weeks {HOLDOUT_WEEKS[0]}-{HOLDOUT_WEEKS[-1]}",
         "no holdout game in any fit", "PASS", f"{coefs['n_train_spread']} spread rows and {coefs['n_train_total']} total rows in the fit"],
        ["G-C3", "pre-registration hash", "hard", "all candidates",
         "Definitions hashed before scoring; the scorer refuses to run on a changed hash",
         "hash matches", "PASS", digest[:32] + "..."],
        ["G-C4", "minimum decisions", "hard", "every strategy",
         "At least 40 scored decisions on the holdout",
         "n >= 40", "PASS" if all(per_strat[s]["n"] >= 40 for s in strat_ids) else "FAIL",
         f"smallest n = {min(per_strat[s]['n'] for s in strat_ids)}"],
        ["G-C5", "luck separation", "hard", "every strategy",
         "Benjamini-Hochberg adjusted p below 0.10 against the coin-flip null",
         "at least one candidate survives",
         "PASS" if n_bh >= 1 else "FAIL",
         f"{n_bh} of {len(strat_ids)} candidates survive"],
        ["G-C6", "beat the naive baseline", "hard", "both fitted models",
         "Out-of-sample MAE lower than the do-nothing baseline, paired on the same games",
         "MAE(model) < MAE(baseline)",
         "PASS" if float(next(x for x in fc_rows if x[0] == "F-SPREAD-MODEL")[3]) <
                   float(next(x for x in fc_rows if x[0] == "F-SPREAD-ZERO")[3]) else "FAIL",
         "spread model vs the zero baseline"],
        ["G-C7", "price feed entitlement", "hard", "any staking tier",
         "A licensed market price feed exists and every price is stored with its capture time",
         "feed present in data/sources.csv", "BLOCKED",
         "Q-01 open; no odds source is reachable and no market data is stored. ROI, CLV and units stay blank."],
        ["G-C8", "leg correlation published", "hard", "parlays and prop combos",
         "Every parlay and same-game combination publishes a measured correlation for its legs",
         "a phi value for every pair", "BLOCKED",
         "Game-level legs are measured here. Player-prop legs are not: no prop-line archive exists."],
        ["G-C9", "forward paper tracking", "hard", "promotion past T0",
         "At least 50 forward-tracked paper bets settled, each with a decision timestamp",
         "50 settled", "BLOCKED",
         "One Week 10 game has settled; the tracking register starts at zero."],
        ["G-C10", "two full seasons elapsed", "hard", "scaled staking",
         "Two complete seasons of forward results before any stake is scaled",
         "2 seasons", "BLOCKED", "The corpus is nine weeks of one season."],
    ]
    write_csv("s2268_gates.csv",
              ["id", "gate", "class", "applies_to", "test", "pass_criterion", "result", "evidence",
               "enforced_in"],
              [[r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], GH_TOOL] for r in gate_rows])

    # ---- leaderboard / rewards --------------------------------------------------
    order = sorted([s for s in strat_ids if per_strat[s]["n"]],
                   key=lambda s: (per_strat[s]["ll"], -per_strat[s]["n"]))
    lb_rows = []
    for rank, sid in enumerate(order, start=1):
        s = per_strat[sid]
        name = next(x[1] for x in STRATEGY_DEFS if x[0] == sid)
        i = strat_ids.index(sid)
        lb_rows.append([
            rank if n_bh else "unranked", sid, name, "single", "T0 - research, unstaked",
            fmt(s["n"]), fmt(s["hits"]), fmt(s["rate"], 4), fmt(s["ll"], 4),
            fmt(s["p"], 4), "yes" if bh_flags[i] else "no",
            "", "", "", "0.00",
            "listed for research only; carries no stake and earns nothing",
            "G-C7, G-C9, G-C10",
        ])
    write_csv("s2268_leaderboard.csv",
              ["rank", "id", "name", "bet_type", "tier", "decisions", "wins", "hit_rate",
               "log_loss", "binomial_p", "survives_fdr", "roi_units_per_100",
               "closing_line_value", "max_drawdown", "stake_multiplier",
               "reward_earned", "gates_blocking",
               "source_first_week", "source_last_week"],
              [[r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[12],
                r[13], r[14], r[15], r[16], W5, W9] for r in lb_rows])

    reward_rows = [
        ["T0", "Research listing", "0.00", "no stake",
         "Scored out of sample on a frozen holdout and published with its full statistics",
         "G-C1, G-C2, G-C3, G-C4", "OPEN",
         f"{len(order)} strategies listed; ranking shown only if a candidate clears G-C5"],
        ["T1", "Paper tracking", "0.00", "no stake",
         "50 forward-tracked paper bets settled with a decision timestamp each, graded automatically",
         "G-C9 forward paper tracking", "BLOCKED",
         "One Week 10 game has settled; the register is at zero"],
        ["T2", "Small stake", "0.25 units", "quarter Kelly fraction of the T3 stake",
         "200 settled tracked bets, positive after an assumed -110 vig, and a licensed price feed",
         "G-C7 price feed, G-C8 leg correlation", "BLOCKED",
         "No price feed exists, so no ROI can be computed and no vig can be beaten on paper"],
        ["T3", "Scaled stake", "1.00 units", "the reference stake",
         "Two full seasons forward, drawdown inside the published limit, capacity stated",
         "G-C10 two seasons elapsed", "BLOCKED",
         "Nine weeks of one season exist"],
        ["T4", "Extended stake", "4.00 units", "four times the reference stake",
         "T3 held for a further full season with no gate regression",
         "T3 plus one more season", "BLOCKED", "Nothing has reached T3"],
    ]
    write_csv("s2268_rewards.csv",
              ["tier", "name", "stake_multiplier", "stake_rule", "requirement",
               "gates", "status", "evidence", "defined_in"],
              [[r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], GH_TOOL] for r in reward_rows])

    summary = {
        "session": "2268bfb2",
        "definitions_sha256": digest,
        "corpus_games": len(corpus),
        "holdout_games": len(hold),
        "train_games_spread": coefs["n_train_spread"],
        "train_games_total": coefs["n_train_total"],
        "decisions_scored": len(decisions),
        "strategies": len(strat_ids),
        "best_hit_rate": round(actual_best, 4),
        "mc_mean_best": round(mc_best_mean, 4),
        "mc_p95_best": round(mc_best_p95, 4),
        "survivors_fdr": n_bh,
        "spread_model_mae": float(next(x for x in fc_rows if x[0] == "F-SPREAD-MODEL")[3]),
        "spread_baseline_mae": float(next(x for x in fc_rows if x[0] == "F-SPREAD-ZERO")[3]),
        "total_model_mae": float(next(x for x in fc_rows if x[0] == "F-TOTAL-MODEL")[3]),
        "total_baseline_mae": float(next(x for x in fc_rows if x[0] == "F-TOTAL-MEAN")[3]),
    }
    with open(os.path.join(DATA, "s2268_competition_summary.json"), "w") as fh:
        json.dump(summary, fh, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
