#!/usr/bin/env python3
"""
strategy_engine.py — deterministic modelling layer.

DESIGN RULES (documented so every number on the site is auditable)
  1. Every input is a transcribed official NFL.com value (data/games_2026.json,
     data/standings_raw.json, data/team_stats.json). Nothing is fetched here.
  2. Every derived quantity is a closed-form function of those inputs. Re-running
     this script reproduces identical output (no randomness, no fitted seed).
  3. Anything that is a MODEL OUTPUT is labelled `model` in the output JSON and is
     rendered on the site with a distinct badge. It is never presented as a market
     line, an official figure, or a fact.
  4. Sample size is stated on every score. n=9 team games is far too small for
     significance, so every strategy is reported with its power status.

WHY LUCK DECOMPOSITION LOOKS LIKE THIS
  Points scored is a small-sample, high-variance outcome. Two clubs with the same
  underlying quality can finish 7-2 and 4-5 because of (a) turnover luck, (b) one-score
  game luck, (c) schedule. We cannot observe fumbles-recovered-by-offense from the
  published data, so we use three *observable* proxies:
     - Pythagorean residual  : wins minus wins predicted by points scored/allowed
     - one-score residual    : record in games decided by <= 8 points minus expectation
     - turnover residual     : INT thrown vs INT made (both published per club)
  None of these is a complete measure of luck. Each is a *bias detector*: a club whose
  record is far ahead of its point differential is a candidate fade, not a confirmed one.
"""
import json, os, math, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data")
OUT = os.path.join(D, "derived")
os.makedirs(OUT, exist_ok=True)

def load(p):
    with open(os.path.join(D, p), encoding="utf-8") as f: return json.load(f)

games_doc  = load("games_2026.json")
stand_doc  = load("standings_raw.json")
stats_doc  = load("team_stats.json")
games, std, TS = games_doc["games"], stand_doc["standings"], stats_doc["teams"]

CLUBS = {s["team"]: s["name"] for s in std}
PYTH_EXP = 2.37          # Pythagorean exponent for NFL points; see methods page
ONE_SCORE_MARGIN = 8     # "one-score game" = final margin <= 8 points (a TD + 2pt)


def series(t):
    """Chronological (date, opponent, pts_for, pts_against, margin, win, week) for club t."""
    rows = []
    for g in games:
        if t not in (g["away"], g["home"]): continue
        home = g["home"] == t
        pf = g["home_pts"] if home else g["away_pts"]
        pa = g["away_pts"] if home else g["home_pts"]
        opp = g["away"] if home else g["home"]
        rows.append({"week": g["week"], "date": g["date"], "opp": opp, "home": home,
                     "pf": pf, "pa": pa, "margin": pf - pa,
                     "win": 1 if pf > pa else (0 if pf < pa else 0.5)})
    rows.sort(key=lambda r: (r["date"], r["week"]))
    return rows


SER = {t: series(t) for t in CLUBS}


def pythagorean_wins(pf, pa, n_games, exp=PYTH_EXP):
    """Expected win% from point differential. Ties are treated as half-wins."""
    if pf <= 0 or pa <= 0: return None
    p = (pf ** exp) / ((pf ** exp) + (pa ** exp))
    return p * n_games


# ---------------------------------------------------------------- club profile
profile = {}
for s in std:
    t = s["team"]; r = SER[t]; n = len(r)
    wins = sum(x["win"] for x in r)
    pyth = pythagorean_wins(s["PF"], s["PA"], n)
    one_score = [x for x in r if abs(x["margin"]) <= ONE_SCORE_MARGIN]
    os_w = sum(x["win"] for x in one_score)
    os_exp = len(one_score) * 0.5
    st = TS[t]
    ints_thrown = st["off_pass"][6]
    ints_made   = st["def_pass"][6]
    profile[t] = {
        "team": t, "name": CLUBS[t], "games": n,
        "wins": wins, "losses": s["L"], "ties": s["T"],
        "pf": s["PF"], "pa": s["PA"], "net": s["PF"] - s["PA"],
        "pf_pg": round(s["PF"] / n, 2), "pa_pg": round(s["PA"] / n, 2),
        "pyth_wins": round(pyth, 2) if pyth is not None else None,
        "pyth_residual": round(wins - pyth, 2) if pyth is not None else None,
        "one_score_games": len(one_score), "one_score_wins": os_w,
        "one_score_residual": round(os_w - os_exp, 2),
        "one_score_win_pct": round(os_w / len(one_score), 3) if one_score else None,
        "ints_thrown": ints_thrown, "ints_made": ints_made,
        "turnover_net": ints_made - ints_thrown,
        "off_pass_yds": st["off_pass"][4], "off_rush_yds": st["off_rush"][1],
        "def_pass_yds": st["def_pass"][4], "def_rush_yds": st["def_rush"][1],
        "off_ypa": st["off_pass"][3], "def_ypa": st["def_pass"][3],
        "off_rush_avg": st["off_rush"][2], "def_rush_avg": st["def_rush"][2],
        "sacks_taken": st["off_pass"][13], "sacks_made": st["def_pass"][13],
        "points_per_play_proxy": round(s["PF"] / (st["off_pass"][0] + st["off_rush"][0]), 3),
    }

# ---------------------------------------------------------------- EPA-free efficiency ratings
# We have no play-by-play, so "efficiency" here is points per game adjusted for
# opponent scoring environment (a league-mean correction, not a fitted model).
lg_pf = sum(p["pf_pg"] for p in profile.values()) / len(profile)
lg_pa = sum(p["pa_pg"] for p in profile.values()) / len(profile)
for t, p in profile.items():
    p["off_rating"] = round(p["pf_pg"] - lg_pf, 2)
    p["def_rating"] = round(lg_pa - p["pa_pg"], 2)
    p["net_rating"] = round(p["off_rating"] + p["def_rating"], 2)

# ---------------------------------------------------------------- simple power rating
# Net rating blended 60/40 with point differential per game: two independent
# views of the same construct, averaged to reduce single-metric noise.
for t, p in profile.items():
    pdpg = p["net"] / p["games"]
    p["power"] = round(0.6 * p["net_rating"] + 0.4 * pdpg, 2)


# ================================================================ CORRELATION
def pearson(xs, ys):
    n = len(xs)
    if n < 3: return None
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if dx == 0 or dy == 0: return None
    return num / (dx * dy)


def spearman(xs, ys):
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]: j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1): r[order[k]] = avg
            i = j + 1
        return r
    return pearson(ranks(xs), ranks(ys))


def tstat(r, n):
    if r is None or abs(r) >= 1 or n < 3: return None
    return r * math.sqrt((n - 2) / (1 - r * r))


PAIRS = [
    ("off_rating","win_pct","Points-scored rating vs win percentage"),
    ("def_rating","win_pct","Points-allowed rating vs win percentage"),
    ("net_rating","win_pct","Net points rating vs win percentage"),
    ("power","win_pct","Composite power rating vs win percentage"),
    ("turnover_net","win_pct","Turnover differential vs win percentage"),
    ("pyth_residual","win_pct","Pythagorean residual vs win percentage (luck proxy)"),
    ("one_score_residual","win_pct","One-score residual vs win percentage (luck proxy)"),
    ("off_pass_yds","win_pct","Passing yards vs win percentage"),
    ("off_rush_yds","win_pct","Rushing yards vs win percentage"),
    ("def_pass_yds","win_pct","Passing yards allowed vs win percentage"),
    ("def_rush_yds","win_pct","Rushing yards allowed vs win percentage"),
    ("sacks_made","win_pct","Sacks made vs win percentage"),
    ("sacks_taken","win_pct","Sacks allowed vs win percentage"),
    ("off_ypa","win_pct","Offensive yards/attempt vs win percentage"),
    ("def_ypa","win_pct","Defensive yards/attempt allowed vs win percentage"),
]
for p in profile.values():
    p["win_pct"] = round(p["wins"] / p["games"], 4)

corr = []
for a, b, label in PAIRS:
    xs = [profile[t][a] for t in CLUBS]
    ys = [profile[t][b] for t in CLUBS]
    r = pearson(xs, ys); rho = spearman(xs, ys); t = tstat(r, len(xs))
    corr.append({
        "x": a, "y": b, "label": label, "n": len(xs),
        "pearson_r": round(r, 4) if r is not None else None,
        "spearman_rho": round(rho, 4) if rho is not None else None,
        "t_stat": round(t, 3) if t is not None else None,
        "r_squared": round(r * r, 4) if r is not None else None,
        "p_approx_two_sided": round(2 * (1 - _cdf(abs(t))), 4) if t is not None else None if False else None,
    })
corr.sort(key=lambda c: -(abs(c["pearson_r"]) if c["pearson_r"] is not None else 0))
