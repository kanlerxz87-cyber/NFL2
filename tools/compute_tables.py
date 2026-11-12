#!/usr/bin/env python3
"""Compute the analytic tables used by the Bet Types, Correlation and Skill-vs-Luck pages.

Everything here is closed-form arithmetic on stated assumptions. No market data is
used, because none exists in this repository, so nothing produced here may be read as
a claim about what a book is offering. The point is to fix the *method* and show what
the method implies.

Model used for correlated legs (two-point common-shock model):
  A single game-state shock S takes +1 with probability 1/2 and -1 with probability 1/2.
  Conditional on S, leg i wins with probability  p_i(S) = p + s*S   (0 < s < min(p, 1-p)).
  Legs are conditionally independent given S, so
      P(all n legs win) = 1/2 * (p+s)^n + 1/2 * (p-s)^n
      Cov(leg_i, leg_j) = +s^2 for same-direction legs, -s^2 for opposite-direction legs
      rho = Cov / (p*(1-p))  =>  s = sqrt(|rho| * p * (1-p))
  Setting s = 0 recovers the independence baseline exactly, so the independence product
  is a special case of this model rather than a competing formula.
"""
import math, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
N_INVEST = 11.0   # risk 11 to win 10  => a -110 line
WIN = 10.0 / N_INVEST


def joint(p, s, n):
    return 0.5 * (p + s) ** n + 0.5 * (p - s) ** n


def shock(p, rho):
    return math.sqrt(abs(rho) * p * (1 - p))


def american(prob):
    dec = 1.0 / prob
    if dec >= 2:
        return "+%d" % round(100 * (dec - 1))
    return "%d" % round(-100 / (dec - 1))


def dec(prob):
    return 1.0 / prob


def sd_units(p):
    """Standard deviation, in units of profit, of one -110 wager that wins with prob p."""
    mu = WIN * p - (1 - p)
    ex2 = WIN * WIN * p + (1 - p)
    return math.sqrt(ex2 - mu * mu), mu


def n_needed(p, z):
    sd, mu = sd_units(p)
    if mu <= 1e-9:
        return None
    return ((z * sd) / mu) ** 2


def n_needed_power(p, z_alpha, z_beta):
    sd, mu = sd_units(p)
    if mu <= 1e-9:
        return None
    return ((z_alpha + z_beta) * sd / mu) ** 2


def prob_ahead(p, n):
    """Normal approximation to P(total profit > 0) after n bets at true win prob p."""
    sd, mu = sd_units(p)
    if mu <= 0:
        return 0.5 if mu == 0 else 0.0
    return 0.5 * (1 + math.erf((mu * math.sqrt(n)) / (sd * math.sqrt(2))))


def w(name, header, rows):
    with open(os.path.join(DATA, name), "w", encoding="utf-8") as fh:
        fh.write("|".join(header) + "\n")
        for r in rows:
            fh.write("|".join("" if v is None else v for v in r) + "\n")
    print("%-34s %d rows" % (name, len(rows)))


# --------------------------------------------------------------- parlays -----
hdr = ["case", "legs", "p_each", "rho_target", "shock_s", "joint_independence",
       "joint_model", "fair_dec_indep", "fair_dec_model", "fair_american_model",
       "overstatement_pct", "read"]
rows = []
for label, n, p, rho in [
    ("two-leg same-game stack (positively coupled)", 2, 0.53, 0.20),
    ("two-leg same-game stack (positively coupled)", 2, 0.53, 0.45),
    ("three-leg same-game combo (positively coupled)", 3, 0.53, 0.20),
    ("three-leg same-game combo (positively coupled)", 3, 0.53, 0.45),
    ("four-leg multi, treated as cross-game", 4, 0.53, 0.05),
    ("five-leg multi, treated as cross-game", 5, 0.53, 0.05),
    ("two teammates' receiving overs (negatively coupled)", 2, 0.53, -0.20),
    ("three teammates' receiving overs (negatively coupled)", 3, 0.53, -0.20),
    ("two-leg parlay of heavy favourites", 2, 0.80, 0.15),
    ("two-leg parlay of longshots", 2, 0.25, 0.15),
]:
    s = shock(p, rho)
    ji = p ** n
    jm = joint(p, s, n)
    if rho < 0:
        # opposite-direction coupling: one leg gets +s, the other -s, so the joint is
        # 1/2*(p+s)^(n-1)*(p-s) + 1/2*(p-s)^(n-1)*(p+s)
        jm = 0.5 * (p + s) ** (n - 1) * (p - s) + 0.5 * (p - s) ** (n - 1) * (p + s)
    over = 100.0 * (ji - jm) / jm
    rows.append([label, str(n), "%.2f" % p, "%.2f" % rho, "%.4f" % s, "%.4f" % ji, "%.4f" % jm,
                 "%.3f" % dec(ji), "%.3f" % dec(jm), american(jm), "%.1f" % over,
                 "independence %s the true joint by %s%% of the joint" %
                 ("overstates" if over > 0 else "understates", "%.1f" % abs(over))])
w("computed_parlays.csv", hdr, rows)

# ----------------------------------------------------------- sample sizes ----
hdr = ["case", "p_true", "ev_per_bet_units", "sd_units", "n_95pct_confidence",
       "n_95pct_80pct_power", "bets_to_75pct_surely_ahead", "weeks_to_power_target_15_per_week", "read"]
rows = []
for label, p in [("breakeven at -110", 1.0 / (1.0 + WIN)), ("thin 53%", 0.53),
                 ("genuine 55%", 0.55), ("strong 57%", 0.57), ("fantasy 60%", 0.60)]:
    sd, mu = sd_units(p)
    n95 = n_needed(p, 1.645)
    npow = n_needed_power(p, 1.645, 0.842)
    if mu < 1e-9:
        mu = 0.0
        weeks = "n/a"
        read = "exactly breakeven: no sample size, however large, makes a zero edge provable"
        n75 = None
    else:
        # smallest n with P(ahead) >= 0.75 at this true edge
        n75 = next((n for n in range(1, 400001) if prob_ahead(p, n) >= 0.75), None)
        weeks = "%.0f" % ((npow or 0) / 15.0)
        read = "even at this edge, %s bets to be 75%% likely to be up" % ("{:,.0f}".format(n75 or 0))
    rows.append([label, "%.4f" % p, "%+.4f" % mu, "%.4f" % sd,
                 "{:,.0f}".format(n95) if n95 else "never",
                 "{:,.0f}".format(npow) if npow else "never",
                 "{:,.0f}".format(n75) if n75 else "never", weeks, read])
w("computed_sample_sizes.csv", hdr, rows)

# ------------------------------------------------ luck vs skill illustration -
hdr = ["bets", "prob_ahead_53", "prob_ahead_55", "prob_ahead_57", "prob_ahead_60", "read"]
rows = []
for n in [25, 50, 100, 200, 400, 1000, 2000, 5000]:
    cells = ["%d" % n]
    for p in (0.53, 0.55, 0.57, 0.60):
        cells.append("%.3f" % prob_ahead(p, n))
    cells.append("a 55%% bettor is still only %s likely to be ahead after %d bets" %
                 ("%.0f%%" % (100 * prob_ahead(0.55, n)), n))
    rows.append(cells)
w("computed_luck.csv", hdr, rows)

# ------------------------------------------------------------- vig / no-vig --
hdr = ["market", "price", "implied_prob", "two_sides_sum", "overround_pct", "no_vig_prob", "read"]
rows = []
for market, a, b in [("both sides -110", -110, -110), ("both sides -115", -115, -115),
                     ("-105 / -115", -105, -115), ("both sides -120", -120, -120),
                     ("-110 / -130", -110, -130)]:
    def imp(american_price):
        return (-american_price) / (100 - american_price) if american_price < 0 else 100.0 / (american_price + 100)
    ia, ib = imp(a), imp(b)
    s = ia + ib
    rows.append([market, "%s / %s" % (a, b), "%.4f / %.4f" % (ia, ib), "%.4f" % s,
                 "%.2f" % (100 * (s - 1)), "%.4f / %.4f" % (ia / s, ib / s),
                 "a bettor must clear %s%% to break even on this pair" % ("%.2f" % (100 * (1 - 1 / s)))])
w("computed_vig.csv", hdr, rows)

# ------------------------------------------- measured game-level correlation --
# Two entries in data/correlation.csv are measurable from data already in this repository: the 136
# settled results of weeks 1-9 carry both sides' final scores, which is exactly the joint outcome
# C-07 and C-08 need. These are *scores*, not prices, so what is measured is the correlation between
# real game outcomes - not between bet settlements, which would need a market archive. The
# distinction is stated in the read column and in the register row's verification cell.
def _pearson(x, y):
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    return sxy / math.sqrt(sxx * syy)


def _fisher(r, n):
    z = 0.5 * math.log((1 + r) / (1 - r))
    se = 1.0 / math.sqrt(n - 3)
    return z - 1.96 * se, z + 1.96 * se


def _inv(z):
    return (math.exp(2 * z) - 1) / (math.exp(2 * z) + 1)


import csv as _csv
with open(os.path.join(DATA, "games_2026_wk1_9.csv"), encoding="utf-8") as fh:
    _games = list(_csv.DictReader(fh, delimiter="|"))
_home = [int(r["home_pts"]) for r in _games]
_away = [int(r["away_pts"]) for r in _games]
_margin = [h - a for h, a in zip(_home, _away)]
_total = [h + a for h, a in zip(_home, _away)]
_N = len(_games)

hdr = ["id", "quantity_a", "quantity_b", "n", "r", "r_squared", "t", "ci_low", "ci_high",
       "p_value_two_sided", "source_file", "read"]
rows = []
for cid, qa, qb, x, y, read in [
    ("C-07", "home team points", "away team points", _home, _away,
     "same-game coupled scoring: measured effect is small and the 95% interval spans zero"),
    ("C-08", "margin (home - away)", "total (home + away)", _margin, _total,
     "near-zero to slightly negative as the sign argument predicted; interval spans zero at n=136, "
     "so the magnitude is not established"),
]:
    if cid == "C-08":
        # the register names this pair "spread and total"; margin and spread are the same quantity
        # up to sign and the sign is irrelevant to a correlation coefficient
        pass
    r = _pearson(x, y)
    lo_z, hi_z = _fisher(r, _N)
    t = r * math.sqrt((_N - 2) / (1 - r * r))
    # two-sided p from the t distribution with n-2 df, via the regularised incomplete beta
    df = _N - 2
    xx = df / (df + t * t)
    # regularised incomplete beta I_x(df/2, 1/2) by continued fraction
    def _betacf(a, b, x, itmax=200):
        qab, qap, qam = a + b, a + 1, a - 1
        c, d = 1.0, 1 - qab * x / qap
        d = 1.0 / (d if abs(d) > 1e-30 else 1e-30)
        h = d
        for m in range(1, itmax + 1):
            m2 = 2 * m
            aa = m * (b - m) * x / ((qam + m2) * (a + m2))
            d = 1 + aa * d; d = 1.0 / (d if abs(d) > 1e-30 else 1e-30)
            c = 1 + aa / c; c = c if abs(c) > 1e-30 else 1e-30
            h *= d * c
            aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
            d = 1 + aa * d; d = 1.0 / (d if abs(d) > 1e-30 else 1e-30)
            c = 1 + aa / c; c = c if abs(c) > 1e-30 else 1e-30
            de = d * c
            h *= de
            if abs(de - 1) < 1e-12:
                break
        return h

    def _betai(a, b, x):
        if x <= 0: return 0.0
        if x >= 1: return 1.0
        lbeta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
        bt = math.exp(lbeta + a * math.log(x) + b * math.log(1 - x))
        if x < (a + 1) / (a + b + 2):
            return bt * _betacf(a, b, x) / a
        return 1 - bt * _betacf(b, a, 1 - x) / b

    p = _betai(df / 2.0, 0.5, xx)
    rows.append([cid, qa, qb, str(_N), "%+.4f" % r, "%.4f" % (r * r), "%+.3f" % t,
                 "%+.4f" % _inv(lo_z), "%+.4f" % _inv(hi_z), "%.4f" % p,
                 "data/games_2026_wk1_9.csv", read])
w("computed_correlation.csv", hdr, rows)
print("done")


# --------------------------------------- depth reach: who actually plays ------
# Requirement R-20/R-21 asks specifically about 2nd/3rd/4th-string players replacing starters. The
# repository holds verified club depth charts for four clubs (data/depth_charts.json) and the official
# Week 10 practice report for those clubs' players. Joining them answers the question directly, and the
# join is exact because it is a name match inside one club's own chart, not a cross-source inference.
#
# Rule, stated once so it can be argued with: a player is AVAILABLE if the official practice report
# lists him as a full participant, or does not list him at all (the report covers players with a
# reportable condition, so absence from it is not an injury claim). LIMITED and DNP players are treated
# as not available to start, which is the conservative reading - a limited participant may well play.
import json as _json
with open(os.path.join(DATA, "depth_charts.json"), encoding="utf-8") as fh:
    _dc = _json.load(fh)["depth_charts"]
with open(os.path.join(DATA, "injuries_2026_wk10.csv"), encoding="utf-8") as fh:
    _inj = list(_csv.DictReader(fh, delimiter="|"))
_report = {(r["team"], r["player"]): r for r in _inj}
_CODE = {"F": "full", "L": "limited", "D": "dnp", "": "not listed"}

hdr = ["club", "unit", "position_group", "depth_reached", "projected_starter",
       "starter_practice", "next_man_up", "next_man_practice", "chain_length",
       "players_skipped", "chart_source"]
rows = []
for club in sorted(_dc):
    chart = _dc[club]
    for unit in ("offense", "defense"):
        for grp in sorted(chart.get(unit, {})):
            names = chart[unit][grp]
            if not names:
                continue
            reach, who = 0, None
            for i, nm in enumerate(names, 1):
                rec = _report.get((club, nm))
                st = rec["practice"] if rec else None
                if st in (None, "F"):
                    reach, who = i, nm
                    break
            if reach == 1:
                continue          # the starter is available; nothing replaced
            starter = names[0]
            srec = _report.get((club, starter))
            nrec = _report.get((club, who)) if who else None
            skipped = names[1:reach - 1] if who else names[1:]
            # A group with NO available body at any depth is a vacancy, not a shallow chain. It was
            # silently dropped in the first version of this table, which is why NE LG (starter
            # limited/out, backup did not practise) is now published rather than omitted.
            if who is None:
                rows.append([
                    club, unit, grp, "vacant", starter,
                    _CODE.get(srec["practice"]) if srec else "not listed",
                    "", "", str(len(names)), "; ".join(skipped),
                    chart.get("club_site", ""),
                ])
                continue
            rows.append([
                club, unit, grp, str(reach), starter,
                _CODE.get(srec["practice"]) if srec else "not listed",
                who, _CODE.get(nrec["practice"]) if nrec else "not listed",
                str(len(names)), "; ".join(skipped) if skipped else "none",
                chart.get("club_site", ""),
            ])
rows.sort(key=lambda r: (r[0], 0 if r[3] == "vacant" else 1, r[2]))
w("computed_depth_reach.csv", hdr, rows)


# --------------------------------------- originated Week 10 fair lines --------
# Stages 1-2 of the line-origination pipeline, computed from verified data only. This is the honest
# minimum: a points-based estimate of strength, and kickoff/venue context. It is deliberately NOT a
# betting recommendation and NOT a comparison to a market, because no market price exists in this
# repository (FL-10). What it establishes is that the pipeline's first two stages run end to end on
# data we actually have, and it publishes the per-game numbers so a reviewer can argue with them.
#
# Strength: points scored and allowed per game over the 136 verified games of weeks 1-9. That sample is
# chosen over the season-to-date standings because the standings have since absorbed week 10 results,
# which would leak the outcome of the games being priced.
import collections as _collections
with open(os.path.join(DATA, "games_2026_wk1_9.csv"), encoding="utf-8") as fh:
    _log = list(_csv.DictReader(fh, delimiter="|"))
with open(os.path.join(DATA, "schedule_2026_wk10.csv"), encoding="utf-8") as fh:
    _wk10 = list(_csv.DictReader(fh, delimiter="|"))

_ALIAS = {"LA": "LAR"}
_for, _against, _played = _collections.Counter(), _collections.Counter(), _collections.Counter()
for _g in _log:
    _a, _h = _ALIAS.get(_g["away"], _g["away"]), _ALIAS.get(_g["home"], _g["home"])
    _ap, _hp = int(_g["away_pts"]), int(_g["home_pts"])
    _for[_a] += _ap; _against[_a] += _hp; _played[_a] += 1
    _for[_h] += _hp; _against[_h] += _ap; _played[_h] += 1
_off = {t: _for[t] / _played[t] for t in _played}
_def = {t: _against[t] / _played[t] for t in _played}
_league = sum(_for.values()) / sum(_played.values())

hdr = ["game_id", "kickoff_et", "away", "home", "venue", "away_off_ppg", "away_def_ppg",
       "home_off_ppg", "home_def_ppg", "league_ppg", "home_field_pts", "fair_away_pts",
       "fair_home_pts", "fair_total", "fair_spread_home", "neutral_site", "games_in_sample",
       "input_note"]
rows = []
for _s in _wk10:
    _a, _h = _s["away"], _s["home"]
    _venue = _s["venue"]
    _neutral = "yes" if ("Munich" in _venue or "Mexico" in _venue
                         or "Tottenham" in _venue or "Wembley" in _venue) else "no"
    # home field is a fixed, published parameter, not a fitted one: zero at a neutral site, and the
    # league-wide scoring asymmetry otherwise. It is stated here so it can be argued with.
    _hfa = 0.0 if _neutral == "yes" else 2.5
    _fa = (_off[_a] + _def[_h]) / 2.0
    _fh = (_off[_h] + _def[_a]) / 2.0 + _hfa
    rows.append([
        _s["game_id"], _s["kickoff_et"], _a, _h, _venue,
        "%.2f" % _off[_a], "%.2f" % _def[_a], "%.2f" % _off[_h], "%.2f" % _def[_h],
        "%.2f" % _league, "%.1f" % _hfa, "%.2f" % _fa, "%.2f" % _fh,
        "%.2f" % (_fa + _fh), "%+.2f" % (_fh - _fa), _neutral,
        "%d-%d" % (min(_played[_a], _played[_h]), max(_played[_a], _played[_h])),
        "points-only baseline; no opponent adjustment, no availability weighting, no market comparison",
    ])
w("computed_fair_lines.csv", hdr, rows)
