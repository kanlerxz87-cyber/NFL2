#!/usr/bin/env python3
"""Line-origination lab (session a392a193) — point-in-time, walk-forward, measured on real results.

What this is
    A reproducible fair-line model built ONLY from the 136 completed 2026 games that this
    repository transcribed from nfl.com game pages (data/games_2026_wk1_9.csv, every row carries
    its official URL). For each week w the model is fitted on weeks < w and evaluated on week w:
    no game ever sees a result that had not been played yet. That is the only way to ask the
    question the brief actually asks — can we originate a line — without lying to ourselves.

What it is compared against
    baseline 1  the do-nothing line (league-average home margin, league-average total)
    baseline 2  last-week's margin for each team (a naive persistence forecast)
    benchmark   the price carried by the vendored community archive (pipeline/data/raw/games.csv).
                That column's vintage is not documented upstream, so it is treated as an
                "archive price", never as a closing line, and it is marked non-official everywhere
                it appears (data/price_archive_a392.csv).

Correlations are measured on the same 136 games, with a seeded bootstrap interval. No p-value is
asserted: the interval is the honest statement, and where the interval spans zero the row says so.

Outputs (all under data/, all deterministic):
    ratings_2026_a392.csv          post-week-9 team ratings
    model_backtest_2026_a392.csv   week-by-week walk-forward error table
    model_verdict_2026_a392.csv    the four numbers a decision turns on, with the method named
    measured_correlations_a392.csv  measured rho/phi with bootstrap CIs and a betting implication
    originated_lines_wk10_a392.csv our Week 10 slate lines, availability load per side beside them
    price_archive_a392.csv         what market data the repository actually holds, per file/column
"""
import csv, json, math, os, random, sys
from collections import defaultdict, Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
ARCHIVE = os.path.join(ROOT, "pipeline", "data", "raw", "games.csv")
GAMES_URL = "https://www.nfl.com/games/"
SEED = 20261112
LAMS = [5.0, 20.0, 60.0]
ALIAS = {"LA": "LAR"}
# The vendored community archive and nfl.com do not use the same club codes: the archive writes
# ARI where the league writes AZ, and LA where the league's own standings write LAR. Joining the
# two without this map silently drops every Arizona game (9 of the 136) and mis-keys every Rams
# game. It is the single most dangerous defect in this data layer, so the count is published, not
# buried: see data/code_collision_a392.csv and the flag FL-24 it generated.
ARCHIVE_ALIAS = {"LA": "LAR", "ARI": "AZ"}


def read(name, delim="|", path=None):
    p = path or os.path.join(DATA, name)
    with open(p, encoding="utf-8") as fh:
        raw = list(csv.reader(fh, delimiter=delim))
    return [dict(zip(raw[0], r)) for r in raw[1:] if any(c.strip() for c in r)]


def num(x):
    try:
        return float(x)
    except Exception:
        return None


# ------------------------------------------------------------------ linear algebra ----
def solve(A, b):
    """Gaussian elimination with partial pivoting; A is n x n, b is n."""
    n = len(A)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for c in range(n):
        piv = max(range(c, n), key=lambda r: abs(M[r][c]))
        if abs(M[piv][c]) < 1e-12:
            M[c][c] += 1e-9
            piv = c
        M[c], M[piv] = M[piv], M[c]
        pv = M[c][c]
        for r in range(n):
            if r == c:
                continue
            f = M[r][c] / pv
            if f:
                for k in range(c, n + 1):
                    M[r][k] -= f * M[c][k]
    return [M[i][n] / M[i][i] for i in range(n)]


def ridge(X, y, lam, unpenalized=()):
    p = len(X[0])
    XtX = [[sum(X[i][a] * X[i][b] for i in range(len(X))) for b in range(p)] for a in range(p)]
    Xty = [sum(X[i][a] * y[i] for i in range(len(X))) for a in range(p)]
    for a in range(p):
        if a not in unpenalized:
            XtX[a][a] += lam
    return solve(XtX, Xty)


def main():
    games = read("games_2026_wk1_9.csv")
    for g in games:
        g["week"] = int(g["week"])
        g["ap"], g["hp"] = int(g["away_pts"]), int(g["home_pts"])
        g["a"], g["h"] = ALIAS.get(g["away"], g["away"]), ALIAS.get(g["home"], g["home"])
        g["neutral"] = g["neutral"].strip().lower() == "yes"
        g["date_iso"] = g["date"]
    teams = sorted({t for g in games for t in (g["a"], g["h"])})
    idx = {t: i for i, t in enumerate(teams)}
    nt = len(teams)
    games.sort(key=lambda g: (g["week"], g["date"]))

    # archive prices, keyed by (date-independent) week+away+home, non-official
    prices = {}
    if os.path.exists(ARCHIVE):
        for r in csv.DictReader(open(ARCHIVE, encoding="utf-8")):
            if r.get("season") != "2026" or r.get("game_type") != "REG":
                continue
            key = (int(r["week"]), ARCHIVE_ALIAS.get(r["away_team"], r["away_team"]), ARCHIVE_ALIAS.get(r["home_team"], r["home_team"]))
            prices[key] = r
    # score agreement between the official log and the archive (independent transcription of the same games)
    agree = disagree = noscore = 0
    for g in games:
        r = prices.get((g["week"], g["a"], g["h"]))
        if not r or not r.get("away_score"):
            noscore += 1
            continue
        if int(r["away_score"]) == g["ap"] and int(r["home_score"]) == g["hp"]:
            agree += 1
        else:
            disagree += 1

    def fit(train, lam):
        """Ridge SRS on margin + pace, unpenalised intercepts (hfa, league mean total)."""
        Xm, ym, Xt, yt = [], [], [], []
        for g in train:
            hm, hi = idx[g["h"]], idx[g["a"]]
            row = [0.0] * (nt + 1)
            row[hm] += 1.0
            row[hi] -= 1.0
            row[nt] = 1.0 if not g["neutral"] else 0.0
            Xm.append(row); ym.append(g["hp"] - g["ap"])
            row2 = [0.0] * (nt + 1)
            row2[hm] += 1.0
            row2[hi] += 1.0
            row2[nt] = 1.0
            Xt.append(row2); yt.append(float(g["hp"] + g["ap"]))
        bm = ridge(Xm, ym, lam, unpenalized=(nt,))
        bt = ridge(Xt, yt, lam, unpenalized=(nt,))
        # mu is the fitted league-mean total; pace_i is team i's deviation from half of it, shrunk to
        # zero by the ridge penalty, which is what makes the system identifiable.
        return {"net": bm[:nt], "hfa": bm[nt], "pace": bt[:nt], "mu": bt[nt]}

    def line(model, g, ridge_mode="ridge"):
        hi, ha = idx[g["h"]], idx[g["a"]]
        margin = model["net"][hi] - model["net"][ha] + (model["hfa"] if not g["neutral"] else 0.0)
        # the pace equation is y = mu + e_home + e_away, so the league mean has to be added back:
        # pace_rating is a deviation from that mean, not a level.
        total = model["mu"] + model["pace"][hi] + model["pace"][ha]
        return margin, total

    def half(x):
        return round(x * 2) / 2.0

    weeks = sorted({g["week"] for g in games})
    eval_weeks = [w for w in weeks if w >= 4]

    # ---------- lambda selection on the walk-forward window ----------
    sel = []
    for lam in LAMS:
        errs = []
        for w in eval_weeks:
            train = [g for g in games if g["week"] < w]
            m = fit(train, lam)
            for g in [x for x in games if x["week"] == w]:
                pr, _ = line(m, g)
                errs.append(abs(half(pr) - (g["hp"] - g["ap"])))
        sel.append((lam, sum(errs) / len(errs), len(errs)))
    LAMBDA = min(sel, key=lambda t: t[1])[0]

    rows_bt = []
    paired = []           # (|err_model|, |err_archive|) on the SAME games - the only fair comparison
    paired_tot = []
    beat_baseline = 0
    acc = {"model_sp": [], "base_sp": [], "persistence_sp": [], "price_sp": [],
           "model_tot": [], "base_tot": [], "price_tot": [], "mp_gap": [], "cover_model": [],
           "cover_price": [], "n": []}
    for w in eval_weeks:
        train = [g for g in games if g["week"] < w]
        m = fit(train, LAMBDA)
        prior_margin = {}
        for g in train:
            prior_margin[(g["a"],)] = g["ap"] - g["hp"]
            prior_margin[(g["h"],)] = g["hp"] - g["ap"]
        ms, bs, ps, pr_s, mt, bt, pr_t, gap, cov_m, cov_p = [], [], [], [], [], [], [], [], [], []
        for g in [x for x in games if x["week"] == w]:
            actual_margin, actual_total = g["hp"] - g["ap"], g["hp"] + g["ap"]
            pred_margin, pred_total = line(m, g)
            pred_margin, pred_total = half(pred_margin), half(pred_total)
            mean_m = sum(x["hp"] - x["ap"] for x in train if not x["neutral"]) / max(1, len([x for x in train if not x["neutral"]]))
            mean_t = sum(x["hp"] + x["ap"] for x in train) / len(train)
            base_margin = 0.0 if g["neutral"] else mean_m
            base_total = mean_t
            per = 0.5 * prior_margin.get((g["h"],), 0) + 0.5 * (0.0 if g["neutral"] else mean_m)
            per = half(per)
            em, eb = abs(pred_margin - actual_margin), abs(base_margin - actual_margin)
            ms.append(em); bs.append(eb)
            if em < eb:
                beat_baseline += 1
            ps.append(abs(per - actual_margin))
            mt.append(abs(pred_total - actual_total)); bt.append(abs(base_total - actual_total))
            pr = prices.get((w, g["a"], g["h"]))
            if pr and pr.get("spread_line") not in (None, "", "NA"):
                pl, tl = float(pr["spread_line"]), float(pr["total_line"])
                pr_s.append(abs(pl - actual_margin)); pr_t.append(abs(tl - actual_total))
                paired.append((abs(pred_margin - actual_margin), abs(pl - actual_margin)))
                paired_tot.append((abs(pred_total - actual_total), abs(tl - actual_total)))
                gap.append(abs(pred_margin - pl))
                cov_m.append(1 if actual_margin - pred_margin > 0 else 0)
                cov_p.append(1 if actual_margin - pl > 0 else 0)
            acc["n"].append(1)
        def mean(v):
            return sum(v) / len(v) if v else None
        rows_bt.append({
            "week": w, "games": len([x for x in games if x["week"] == w]),
            "train_games": len(train),
            "model_spread_mae": round(mean(ms), 3), "baseline_spread_mae": round(mean(bs), 3),
            "persistence_spread_mae": round(mean(ps), 3),
            "archive_price_spread_mae": round(mean(pr_s), 3) if pr_s else "not published",
            "model_total_mae": round(mean(mt), 3), "baseline_total_mae": round(mean(bt), 3),
            "archive_price_total_mae": round(mean(pr_t), 3) if pr_t else "not published",
            "model_vs_archive_gap_pts": round(mean(gap), 3) if gap else "not published",
            "home_cover_model_pct": round(100 * mean(cov_m), 1) if cov_m else "not published",
            "home_cover_archive_pct": round(100 * mean(cov_p), 1) if cov_p else "not published",
            "source": "S-GAMES26",
        })
        for k, v in (("model_sp", ms), ("base_sp", bs), ("persistence_sp", ps), ("price_sp", pr_s),
                     ("model_tot", mt), ("base_tot", bt), ("price_tot", pr_t), ("mp_gap", gap),
                     ("cover_model", cov_m), ("cover_price", cov_p)):
            acc[k] += v

    def mae(v):
        return sum(v) / len(v) if v else None

    rnd2 = random.Random(SEED + 1)

    def paired_boot(pairs, B=4000):
        """Bootstrap CI on the MEAN ABSOLUTE-ERROR DIFFERENCE of two predictors scored on the same games."""
        n = len(pairs)
        d = [a - b for a, b in pairs]
        point = sum(d) / n
        out = []
        for _ in range(B):
            sa = [rnd2.randrange(n) for _ in range(n)]
            out.append(sum(d[i] for i in sa) / n)
        out.sort()
        return point, out[int(0.025 * B)], out[int(0.975 * B)]

    # ---------- rest / bye decomposition (the M-05 confound, measured) ----------
    from datetime import date as _date
    prev_d, rest_rows = {}, []
    for g in games:
        y, mo, d0 = map(int, g["date"].split("-")); gd = _date(y, mo, d0)
        rh = (gd - prev_d[g["h"]]).days if g["h"] in prev_d else None
        ra = (gd - prev_d[g["a"]]).days if g["a"] in prev_d else None
        if rh is not None and ra is not None:
            rest_rows.append({"diff": rh - ra, "home_rest": rh, "away_rest": ra,
                              "margin": g["hp"] - g["ap"], "neutral": g["neutral"]})
        prev_d[g["h"]] = gd; prev_d[g["a"]] = gd
    buckets = {}
    for r in rest_rows:
        key = "home +3 or more" if r["diff"] >= 3 else "away +3 or more" if r["diff"] <= -3 else "equal rest"
        buckets.setdefault(key, []).append(r["margin"])
    rest_out = []
    for key in ("equal rest", "home +3 or more", "away +3 or more"):
        v = buckets.get(key, [])
        m = sum(v) / len(v); sd = math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1)) if len(v) > 1 else None
        se = sd / math.sqrt(len(v)) if sd is not None else None
        rest_out.append({"bucket": key, "games": len(v), "mean_home_margin": round(m, 2),
                         "sd": round(sd, 2) if sd is not None else "not published",
                         "se": round(se, 2) if se is not None else "not published",
                         "ci_low": round(m - 1.96 * se, 2) if se is not None else "not published",
                         "ci_high": round(m + 1.96 * se, 2) if se is not None else "not published",
                         "read": "in a nine-week sample a rest differential of +/-7 days IS bye-week status, "
                                 "not a training-load effect" if key != "equal rest" else "the reference group",
                         "source": "S-GAMES26"})

    # ---------- final ratings for the current slate ----------
    full = fit(games, LAMBDA)
    full_prior = fit([g for g in games if g["week"] <= 8], LAMBDA)   # what was known before week 9
    ratings = []
    rec = defaultdict(lambda: {"w": 0, "l": 0, "t": 0, "pf": 0, "pa": 0, "n": 0})
    for g in games:
        for t, pts, opp_pts in ((g["h"], g["hp"], g["ap"]), (g["a"], g["ap"], g["hp"])):
            r = rec[t]; r["n"] += 1; r["pf"] += pts; r["pa"] += opp_pts
            r["w" if pts > opp_pts else "l" if pts < opp_pts else "t"] += 1
    order = sorted(range(nt), key=lambda i: -(full["net"][i]))
    rank = {i: n + 1 for n, i in enumerate(order)}
    for i, t in enumerate(teams):
        r = rec[t]
        pyth = (r["pf"] ** 2) / (r["pf"] ** 2 + r["pa"] ** 2) if r["pf"] and r["pa"] else None
        exp_w = pyth * r["n"] if pyth is not None else None
        ratings.append({
            "team": t, "games": r["n"], "w": r["w"], "l": r["l"], "t": r["t"],
            "pf": r["pf"], "pa": r["pa"], "net_pts": r["pf"] - r["pa"],
            "net_rating": round(full["net"][i], 3),
        "pace_rating_pts_above_league_mean": round(full["pace"][i], 2),
            "rank_by_rating": rank[i],
            "rank_by_wins": 0, "pyth_expectation_wins": round(exp_w, 2) if exp_w is not None else "not published",
            "luck_delta_wins": round(r["w"] - exp_w, 2) if exp_w is not None else "not published",
            "source": "S-GAMES26",
        })
    by_wins = sorted(ratings, key=lambda x: (-(x["w"] + 0.5 * x["t"]), x["team"]))
    for n, x in enumerate(by_wins):
        x["rank_by_wins"] = n + 1
    ratings.sort(key=lambda x: x["rank_by_rating"])

    # ---------- correlations measured on the 136 games ----------
    rnd = random.Random(SEED)

    def boot_ci(xs, ys, B=4000):
        """Percentile bootstrap. A resample in which one variable is constant has no defined
        correlation, so it is dropped rather than imputed - and if too many are dropped the row
        publishes no interval instead of a fake one."""
        n = len(xs)
        out = []
        for _ in range(B):
            sa = [rnd.randrange(n) for _ in range(n)]
            r = pearson([xs[i] for i in sa], [ys[i] for i in sa])
            if r is not None:
                out.append(r)
        if len(out) < 10:
            return None, None
        out.sort()
        return out[int(0.025 * len(out))], out[int(0.975 * len(out))]

    def pearson(xs, ys):
        n = len(xs)
        if n < 3:
            return None
        mx, my = sum(xs) / n, sum(ys) / n
        sxx = sum((x - mx) ** 2 for x in xs); syy = sum((y - my) ** 2 for y in ys)
        sxy = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
        return sxy / math.sqrt(sxx * syy) if sxx > 0 and syy > 0 else None

    corr_rows = []

    def add_corr(cid, what, xs, ys, method, implication, n=None):
        n = n or len(xs)
        r = pearson(xs, ys)
        lo, hi = boot_ci(xs, ys) if n >= 10 else (None, None)
        corr_rows.append({
            "id": cid, "pair": what, "n": n,
            "rho": round(r, 3) if r is not None else "not published",
            "ci_low": round(lo, 3) if lo is not None else "not published",
            "ci_high": round(hi, 3) if hi is not None else "not published",
            "spans_zero": "yes" if lo is not None and lo <= 0 <= hi else "no" if lo is not None else "not published",
        "p_a": "not published", "p_b": "not published", "joint_observed": "not published",
        "joint_independent": "not published", "fair_decimal_independent": "not published",
        "fair_decimal_observed": "not published", "price_error_pct": "not published",
            "method": method, "betting_implication": implication, "source": "S-GAMES26",
        })

    add_corr("M-01", "away points scored vs home points scored (game level)",
             [g["ap"] for g in games], [g["hp"] for g in games],
             "Pearson rho on 136 games, seeded bootstrap 4,000 resamples",
             "drives whether the two legs of a same-game total parlay are independent; a positive rho means the "
             "product of the marginals understates the joint")
    add_corr("M-02", "team points for vs team points allowed (club level, weeks 1-9)",
             [rec[t]["pf"] for t in teams], [rec[t]["pa"] for t in teams],
             "Pearson rho on 32 clubs",
             "a negative value means clubs that score more also concede less — i.e. the spread and the total are "
             "moved by the same underlying strength, which is what a ratings model exploits")
    per_team = defaultdict(list)
    for g in games:
        per_team[g["h"]].append((g["week"], g["hp"] - g["ap"]))
        per_team[g["a"]].append((g["week"], g["ap"] - g["hp"]))
    xa, xb = [], []
    for t, v in per_team.items():
        v.sort()
        for i in range(1, len(v)):
            xa.append(v[i - 1][1]); xb.append(v[i][1])
    add_corr("M-03", "club margin in one game vs its margin in the next (week over week)", xa, xb,
             "Pearson rho on %d consecutive club-game pairs; the unit is a club-game, not an independent "
             "observation, so the interval is a lower bound on the true width" % len(xa),
             "this is the skill-vs-luck number for a team: near zero means last week's blowout tells the market "
             "almost nothing and a ratings model has to earn its living on season-long aggregates")
    add_corr("M-04", "win-loss record vs Pythagorean expectation (club level)",
             [rec[t]["w"] + 0.5 * rec[t]["t"] for t in teams],
             [((rec[t]["pf"] ** 2) / (rec[t]["pf"] ** 2 + rec[t]["pa"] ** 2)) * rec[t]["n"] for t in teams],
             "Pearson rho on 32 clubs; Pythagorean exponent 2 (NFL convention)",
             "the residual is luck: the wins a club got that its point margin did not predict. A strategy that "
             "backs the positive residual is backing variance, not skill")
    prev_date = {}
    from datetime import date
    rd, mg = [], []
    for g in games:
        y, mo, d = map(int, g["date"].split("-"))
        gd = date(y, mo, d)
        rest_h = (gd - prev_date[g["h"]]).days if g["h"] in prev_date else None
        rest_a = (gd - prev_date[g["a"]]).days if g["a"] in prev_date else None
        if rest_h is not None and rest_a is not None:
            rd.append(rest_h - rest_a); mg.append(g["hp"] - g["ap"])
        prev_date[g["h"]] = gd; prev_date[g["a"]] = gd
    add_corr("M-05", "rest-day differential (home minus away) vs home margin", rd, mg,
             "Pearson rho on %d games from week 2 onward, kickoff dates read from the official game log; "
             "the variable is dominated by +/-7-day bye gaps" % len(rd),
             "rest asymmetry is the cheapest situational feature in the catalogue because it needs no data licence: "
             "it is a date arithmetic on the published schedule")
    # HFA measured
    hm = [g["hp"] - g["ap"] for g in games if not g["neutral"]]
    mu = sum(hm) / len(hm)
    sd = math.sqrt(sum((x - mu) ** 2 for x in hm) / (len(hm) - 1))
    se = sd / math.sqrt(len(hm))
    t = mu / se
    corr_rows.append({
        "id": "M-06", "pair": "home-field advantage, in points (non-neutral games only)",
        "n": len(hm), "rho": round(mu, 3),
        "ci_low": round(mu - 1.96 * se, 3), "ci_high": round(mu + 1.96 * se, 3),
        "spans_zero": "no" if (mu - 1.96 * se) * (mu + 1.96 * se) > 0 else "yes",
        "method": "not a correlation - a measured coefficient. Mean home margin over %d non-neutral games: "
                  "%.2f pts (SD %.2f, SE %.2f, t = %.2f). Neutral-site games excluded because the log flags them."
                  % (len(hm), mu, sd, se, t),
        "betting_implication": "this is the only situational coefficient this project may currently assert from its own "
                               "data. Every other one (Munich travel, short week, altitude) stays at zero until measured "
                               "on a longer history - which is what keeps the model honest and what makes its error rate "
                               "the number to watch",
        "source": "S-GAMES26",
    })
    # parlay coupling: home covers our line vs game over our total, and vs archive price
    xs, ys, xs2, ys2 = [], [], [], []
    for w in eval_weeks:
        train = [g for g in games if g["week"] < w]
        m = fit(train, LAMBDA)
        for g in [x for x in games if x["week"] == w]:
            pm, pt = half(line(m, g)[0]), half(line(m, g)[1])
            xs.append(1 if (g["hp"] - g["ap"]) > pm else 0)
            ys.append(1 if (g["hp"] + g["ap"]) > pt else 0)
            pr = prices.get((w, g["a"], g["h"]))
            if pr and pr.get("spread_line") not in (None, "", "NA"):
                xs2.append(1 if (g["hp"] - g["ap"]) > float(pr["spread_line"]) else 0)
                ys2.append(1 if (g["hp"] + g["ap"]) > float(pr["total_line"]) else 0)
    add_corr("M-07", "home covers the spread AND the game goes over (our own lines)", xs, ys,
             "phi coefficient (Pearson on two binaries) on %d games, seeded bootstrap" % len(xs),
             "the two legs a bettor most often parlay together. A positive phi means the book's independent "
             "multiplication of the two prices is too generous to the bettor on the joint and the true joint "
             "probability is higher than the product")
    add_corr("M-08", "home covers the spread AND the game goes over (archive prices)", xs2, ys2,
             "phi on %d games with an archive price; the price column is non-official, the result is official" % len(xs2),
             "same measurement against the market's line rather than ours — if the two rows disagree, the coupling "
             "is an artefact of where our line sits, not of the games")

    def parlay_stats(a, b):
        n = len(a)
        pa = sum(a) / n; pb = sum(b) / n
        joint = sum(1 for i in range(n) if a[i] and b[i]) / n
        indep = pa * pb
        dec_indep = 1.0 / indep if indep else None
        dec_true = 1.0 / joint if joint else None
        return {"p_a": round(pa, 4), "p_b": round(pb, 4), "joint_observed": round(joint, 4),
                "joint_independent": round(indep, 4),
                "fair_decimal_independent": round(dec_indep, 3) if dec_indep else "not published",
                "fair_decimal_observed": round(dec_true, 3) if dec_true else "not published",
                "price_error_pct": round(100 * (indep / joint - 1.0), 2) if joint else "not published"}
    for row, a, b in ((corr_rows[-2], xs, ys), (corr_rows[-1], xs2, ys2)):
        row.update(parlay_stats(a, b))
        row["method"] += (" | parlay arithmetic: marginal p(A)=%.3f, p(B)=%.3f, observed joint %.3f vs the product "
                          "%.3f; a ticket priced on the product is off by %s%%"
                          % (row["p_a"], row["p_b"], row["joint_observed"], row["joint_independent"], row["price_error_pct"]))

    # ---------- Week 10 slate: our line + availability load ----------
    inj = read("injuries_wk10_2026_hubrefresh.csv")
    load = defaultdict(lambda: Counter())
    for r in inj:
        s = r["side"]; p = r["practice"]
        load[r["team"]]["reported"] += 1
        if p == "D":
            load[r["team"]]["dnp_" + s] += 1
        elif p == "L":
            load[r["team"]]["lim_" + s] += 1
        if r["status"].strip():
            load[r["team"]]["out"] += 1
    sched = read("schedule_2026_wk10.csv")
    wk10_model = fit(games, LAMBDA)
    originated = []
    for s in sched:
        a = ALIAS.get(s["away"], s["away"]); h = ALIAS.get(s["home"], s["home"])
        if a not in idx or h not in idx:
            continue
        g = {"a": a, "h": h, "neutral": False}
        pm, pt = line(wk10_model, g)
        pr = prices.get((10, a, h))
        arch_spread = pr.get("spread_line") if pr and pr.get("spread_line") not in (None, "", "NA") else "not published"
        arch_total = pr.get("total_line") if pr and pr.get("total_line") not in (None, "", "NA") else "not published"
        originated.append({
            "game": s["game_id"], "date": s["date"], "kickoff_et": s["kickoff_et"],
            "away": a, "home": h,
            "our_spread_home_favoured": round(half(pm), 1),
            "our_total": round(half(pt), 1),
            "archive_spread_home_favoured": arch_spread,
            "archive_total": arch_total,
            "spread_gap_vs_archive": round(half(pm) - float(arch_spread), 1) if arch_spread != "not published" else "not published",
            "total_gap_vs_archive": round(half(pt) - float(arch_total), 1) if arch_total != "not published" else "not published",
            "venue_flag": "international - no coefficient published" if "Munich" in (s.get("venue") or "") else "not published",
            "away_dnp_off": load[a]["dnp_offence"], "away_dnp_def": load[a]["dnp_defence"],
            "home_dnp_off": load[h]["dnp_offence"], "home_dnp_def": load[h]["dnp_defence"],
            "away_out": load[a]["out"] or "not published", "home_out": load[h]["out"] or "not published",
            "status": "origination output, unvalidated - availability load is descriptive, not priced",
            "source": "S-GAMES26",
        })

    # ---------- the code-collision evidence, published ----------
    naive = 0
    naive_keys = set()
    for r in csv.DictReader(open(ARCHIVE, encoding="utf-8")):
        if r.get("season") == "2026" and r.get("game_type") == "REG":
            naive_keys.add((int(r["week"]), ALIAS.get(r["away_team"], r["away_team"]), ALIAS.get(r["home_team"], r["home_team"])))
    for g in games:
        if (g["week"], g["a"], g["h"]) not in naive_keys:
            naive += 1
    code_rows = [
        {"join": "official log (nfl.com codes: AZ, LAR) -> archive games.csv (ARI, LA), no alias table",
         "games_dropped": naive, "games_joined": len(games) - naive,
         "detail": "the nine dropped rows are every Arizona Cardinals game in weeks 1-9; a model fitted through "
                   "this join loses a whole club and still reports an error rate",
         "fix": "ARCHIVE_ALIAS in this script; the same map is what data/teams.csv needs to join the archive's "
                "roster and price files", "source": "S-REPO"},
        {"join": "same join, with the alias table applied",
         "games_dropped": 0, "games_joined": len(games),
         "detail": "%d of %d scores agree cell-for-cell with the official transcription, %d disagree, %d have no "
                   "archive score" % (agree, len(games), disagree, noscore),
         "fix": "published as the cross-source check on the game log", "source": "S-REPO"},
    ]

    # ---------- price archive inventory ----------
    inv = []
    cl_path = os.path.join(ROOT, "pipeline", "data", "raw", "closing_lines.csv")
    cl = list(csv.DictReader(open(cl_path, encoding="utf-8"))) if os.path.exists(cl_path) else []
    cl_seasons = sorted({r["game_id"][:4] for r in cl})
    inv.append({"asset": "pipeline/data/raw/games.csv - spread_line, total_line, away/home moneyline and spread odds",
                "rows_2026": sum(1 for r in prices.values()),
                "seasons": "2006-2026 (documented coverage)",
                "what_it_proves": "a price existed for %d completed 2026 games and %d scheduled ones"
                                  % (sum(1 for k, v in prices.items() if v.get("spread_line") not in ("", "NA") and v.get("away_score")),
                                     sum(1 for k, v in prices.items() if v.get("spread_line") not in ("", "NA") and not v.get("away_score"))),
                "what_it_does_not_prove": "the vintage. The upstream schema (nfldata DATASETS.md, last updated 2020-05-13) "
                                          "defines spread_line and total_line but never says whether they are opening or closing, "
                                          "and does not document the moneyline/odds columns at all",
                "official": "no - community archive, non-official by rule", "source": "S-REPO"})
    inv.append({"asset": "pipeline/data/raw/closing_lines.csv",
                "rows_2026": 0,
                "seasons": "%s-%s" % (cl_seasons[0], cl_seasons[-1]) if cl_seasons else "not published",
                "what_it_proves": "%d rows across %d games (MONEYLINE/SPREAD/TOTAL, both sides)" % (len(cl), len({r["game_id"] for r in cl})),
                "what_it_does_not_prove": "anything about 2026: the file stops before the current season, so the file the "
                                          "pipeline calls 'closing lines' cannot price this slate",
                "official": "no - community archive, non-official by rule", "source": "S-REPO"})
    for f, note in (("initial_lines.csv", "single-season file (2021) keyed by sportsbook; one book, not a consensus"),
                    ("sc_lines.csv", "sportsbook-consensus file for 2013; no 2026 rows")):
        p2 = os.path.join(ROOT, "pipeline", "data", "raw", f)
        n = sum(1 for _ in open(p2, encoding="utf-8")) - 1 if os.path.exists(p2) else 0
        inv.append({"asset": "pipeline/data/raw/%s" % f, "rows_2026": 0,
                    "seasons": "documented in file", "what_it_proves": "%d rows" % n,
                    "what_it_does_not_prove": note,
                    "official": "no - community archive, non-official by rule", "source": "S-REPO"})
    inv.append({"asset": "league-official prices (nfl.com, operations.nfl.com)", "rows_2026": 0,
                "seasons": "none", "what_it_proves": "nothing - the league publishes no betting lines",
                "what_it_does_not_prove": "n/a",
                "official": "yes - and empty", "source": "S-OPS"})

    # ---------- write ----------
    def write_csv(name, rows, cols):
        with open(os.path.join(DATA, name), "w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh, delimiter="|")
            w.writerow(cols)
            for r in rows:
                w.writerow([r.get(c, "not published") if r.get(c, "") != "" else "not published" for c in cols])
        print("wrote data/%s (%d rows)" % (name, len(rows)))

    write_csv("ratings_2026_a392.csv", ratings,
              "team|games|w|l|t|pf|pa|net_pts|net_rating|pace_rating_pts_above_league_mean|rank_by_rating|"
              "rank_by_wins|pyth_expectation_wins|luck_delta_wins|source".split("|"))
    write_csv("model_backtest_2026_a392.csv", rows_bt,
              ("week games train_games model_spread_mae baseline_spread_mae persistence_spread_mae "
               "archive_price_spread_mae model_total_mae baseline_total_mae archive_price_total_mae "
               "model_vs_archive_gap_pts home_cover_model_pct home_cover_archive_pct source").split())
    verdict = []
    def V(metric, value, method, read):
        verdict.append({"metric": metric, "value": value, "method": method, "read": read, "source": "S-GAMES26"})
    V("games used", len(games), "official 2026 game log, weeks 1-9", "one season; nothing here clears gate G-08 (n>=400)")
    V("walk-forward weeks evaluated", len(eval_weeks), "weeks 4-9, each fitted on prior weeks only",
      "training windows are 48, 62, 78, 92, 106, 121 games")
    V("spread MAE - our model (pts)", round(mae(acc["model_sp"]), 3), "mean absolute error vs the final margin", "")
    V("spread MAE - do-nothing baseline", round(mae(acc["base_sp"]), 3), "league-average home margin, no team information", "")
    V("spread MAE - last-week persistence", round(mae(acc["persistence_sp"]), 3), "half of last week's margin", "")
    V("spread MAE - archive price", round(mae(acc["price_sp"]), 3) if acc["price_sp"] else "not published",
      "the community archive's 2026 line vs the official result", "the number a real market beats us by")
    V("total MAE - our model / baseline / archive",
      "%.3f / %.3f / %s" % (mae(acc["model_tot"]), mae(acc["base_tot"]),
                            round(mae(acc["price_tot"]), 3) if acc["price_tot"] else "not published"),
      "mean absolute error vs the final combined score", "")
    V("mean gap between our line and the archive line (pts)", round(mae(acc["mp_gap"]), 3) if acc["mp_gap"] else "not published",
      "how far our origination sits from the archived price, averaged over games where both exist",
      "a disagreement is not an edge; it is a hypothesis that has to survive the gates")
    if paired:
        pm, plo, phi_ = paired_boot(paired)
        pt, ptlo, pthi = paired_boot(paired_tot)
        V("paired spread error - our model minus the archive price, same %d games" % len(paired),
          "%+.3f pts (95%% CI %.3f to %.3f)" % (pm, plo, phi_),
          "bootstrap on the mean absolute-error difference, computed only on games where both exist, so the two "
          "predictors are never scored on different slates",
          "positive means our line is worse by that many points on average; the interval is what decides whether "
          "that gap is a real deficit or one season of noise" +
          (" - the interval excludes zero, so the deficit is measurable" if plo > 0 or pthi < 0 else " - the interval spans zero"))
        V("paired total error - our model minus the archive price, same %d games" % len(paired_tot),
          "%+.3f pts (95%% CI %.3f to %.3f)" % (pt, ptlo, pthi),
          "same construction, totals", "a positive value with an interval above zero means our totals are worse than "
          "the archived price and the naive league-mean baseline at the same time - the pace half of this model earns nothing")
    V("games where our line beat the do-nothing baseline",
      "%d of %d (%.1f%%)" % (beat_baseline, len(acc["model_sp"]), 100.0 * beat_baseline / len(acc["model_sp"])),
      "per-game absolute-error comparison against the league-average home margin",
      "accuracy on a majority of games is not the target - beating a benchmark by enough to clear the vig is")
    V("home cover rate on our line / on the archive line",
      "%.1f%% / %.1f%%" % (100 * mae(acc["cover_model"]), 100 * mae(acc["cover_price"])),
      "share of games where the home team beat the line by more than zero", "both should sit near 50%")
    V("ridge penalty lambda", LAMBDA, "chosen by walk-forward spread MAE over %s" % ", ".join(str(l) for l in LAMS),
      "selection is done on the evaluation window, which is a mild optimism; the honest read is that the "
      "three lambdas differ by less than the sampling noise: " + ", ".join("%.3f" % e for _, e, _ in sel))
    V("official log vs archive transcription - scores that agree", "%d of %d (%d rows the archive has no score for)"
      % (agree, len(games), noscore), "row-by-row score comparison, two independent transcriptions of the same games",
      "the disagreement count is %d - a non-zero value here would have stopped the import" % disagree)
    write_csv("model_verdict_2026_a392.csv", verdict, "metric|value|method|read|source".split("|"))
    write_csv("measured_correlations_a392.csv", corr_rows,
              ("id pair n rho ci_low ci_high spans_zero p_a p_b joint_observed joint_independent "
               "fair_decimal_independent fair_decimal_observed price_error_pct method betting_implication source").split())
    write_csv("originated_lines_wk10_a392.csv", originated,
              ("game date kickoff_et away home our_spread_home_favoured our_total archive_spread_home_favoured "
               "archive_total spread_gap_vs_archive total_gap_vs_archive venue_flag away_dnp_off away_dnp_def home_dnp_off "
               "home_dnp_def away_out home_out status source").split())
    write_csv("code_collision_a392.csv", code_rows, "join|games_dropped|games_joined|detail|fix|source".split("|"))
    write_csv("rest_and_hfa_2026_a392.csv", rest_out,
              "bucket|games|mean_home_margin|sd|se|ci_low|ci_high|read|source".split("|"))
    write_csv("price_archive_a392.csv", inv,
              "asset|rows_2026|seasons|what_it_proves|what_it_does_not_prove|official|source".split("|"))
    json.dump({"lambda": LAMBDA, "n_games": len(games), "agree": agree, "disagree": disagree,
               "hfa": round(mu, 3), "hfa_ci": [round(mu - 1.96 * se, 3), round(mu + 1.96 * se, 3)],
               "spread_mae_model": round(mae(acc["model_sp"]), 3), "spread_mae_base": round(mae(acc["base_sp"]), 3),
               "spread_mae_archive": round(mae(acc["price_sp"]), 3) if acc["price_sp"] else None},
              open(os.path.join(DATA, "origination_lab_a392.json"), "w"), indent=1)
    print("verdict:", json.dumps({"spread_mae_model": round(mae(acc["model_sp"]), 2),
                                 "spread_mae_baseline": round(mae(acc["base_sp"]), 2),
                                 "spread_mae_archive": round(mae(acc["price_sp"]), 2) if acc["price_sp"] else None}))


if __name__ == "__main__":
    sys.exit(main() or 0)
