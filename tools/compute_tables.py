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
print("done")
