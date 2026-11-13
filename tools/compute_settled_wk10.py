#!/usr/bin/env python3
"""Score every settled Week 10 game against the predictions this repository published for it.

This is the first out-of-sample settlement the site has ever had. Everything else on the site is
either fitted in-sample (weeks 1-9) or a pre-game output that has not met a result. This script is
deliberately dumb: it reads the official result, reads the published predictions, subtracts, and
writes the difference. It never picks a winner between the predictors and it never rounds away an
uncomfortable number.

Why `games_2026_wk10_played.csv` exists instead of appending to `games_2026_wk1_9.csv`
--------------------------------------------------------------------------------------
Suggestion S-26 on this very site designates the weeks 1-9 file as the pre-registered backtest
corpus and requires its SHA-256 to be recorded so that a later edit invalidates every grade built
on it. Appending week 10 to it would break the pre-registration the site recommends. Week 10
results therefore live in their own append-only file, and the frozen corpus is left byte-identical.

Inputs (all checked in, all verified elsewhere):
  data/games_2026_wk10_played.csv      official final scores, one row per settled game
  data/originated_lines_wk10_a392.csv  the a392 origination lab's spread/total + archived price
  data/computed_fair_lines.csv         the points-only fair-line baseline (tools/compute_tables.py)
  data/games_2026_wk1_9.csv            the frozen weeks 1-9 corpus, used only for the null
                                       distribution and the do-nothing season-mean baseline

Outputs:
  data/settled_wk10_5f16dcc6.csv       one row per (game, predictor): prediction vs official result
  data/computed_settled_5f16dcc6.csv   the derived arithmetic and the sample-size verdict

Sign convention: a spread column holds the predicted HOME margin (home points minus away points).
Positive means the home club is favoured by that many points. This matches both source files.
"""
import csv
import os
import statistics as st

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

CORPUS = "games_2026_wk1_9.csv"
PLAYED = "games_2026_wk10_played.csv"
ORIGINATED = "originated_lines_wk10_a392.csv"
FAIRLINES = "computed_fair_lines.csv"
OUT_ROWS = "settled_wk10_5f16dcc6.csv"
OUT_COMPUTED = "computed_settled_5f16dcc6.csv"

S_SCORES = "https://www.nfl.com/scores/2026/week-10"
Z_ALPHA, Z_BETA = 1.96, 0.8416  # two-sided 5% with 80% power


def rd(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="|"))


def num(v):
    """Return a float, or None when the cell is deliberately blank on the site."""
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def main():
    played = rd(PLAYED)
    corpus = rd(CORPUS)
    orig = {r["game"]: r for r in rd(ORIGINATED)}
    fair = {r["game_id"]: r for r in rd(FAIRLINES)}

    # ---- the do-nothing baseline and the null distribution, from the frozen corpus only --------
    margins = [int(r["home_pts"]) - int(r["away_pts"]) for r in corpus]
    totals = [int(r["home_pts"]) + int(r["away_pts"]) for r in corpus]
    mean_margin = st.mean(margins)
    mean_total = st.mean(totals)
    naive_margin_err = [abs(m - mean_margin) for m in margins]
    naive_total_err = [abs(t - mean_total) for t in totals]

    def pctile(sample, value):
        """Percentile of `value` inside `sample`, and the count at or below it."""
        n = sum(1 for x in sample if x <= value)
        return 100.0 * n / len(sample), n

    rows = []
    for g in played:
        gid = g["game_id"]
        away_pts, home_pts = int(g["away_pts"]), int(g["home_pts"])
        act_margin = home_pts - away_pts
        act_total = home_pts + away_pts
        matchup = "%s %d - %s %d" % (g["away"], away_pts, g["home"], home_pts)

        o, f = orig.get(gid, {}), fair.get(gid, {})
        predictors = [
            ("our origination (a392 lab)", num(o.get("our_spread_home_favoured")),
             num(o.get("our_total")), "data/originated_lines_wk10_a392.csv"),
            ("points-only fair line", num(f.get("fair_spread_home")),
             num(f.get("fair_total")), "data/computed_fair_lines.csv"),
            ("archived community price", num(o.get("archive_spread_home_favoured")),
             num(o.get("archive_total")), "data/originated_lines_wk10_a392.csv"),
            ("do-nothing season mean", mean_margin, mean_total,
             "%s (weeks 1-9, %d games)" % (CORPUS, len(corpus))),
        ]
        for name, p_spread, p_total, origin in predictors:
            s_ae = "" if p_spread is None else "%.2f" % abs(act_margin - p_spread)
            t_ae = "" if p_total is None else "%.2f" % abs(act_total - p_total)
            rows.append({
                "game_id": gid,
                "week": g["week"],
                "matchup": matchup,
                "actual_away_pts": away_pts,
                "actual_home_pts": home_pts,
                "actual_home_margin": act_margin,
                "actual_total": act_total,
                "predictor": name,
                "predicted_spread_home": "" if p_spread is None else "%.2f" % p_spread,
                "predicted_total": "" if p_total is None else "%.2f" % p_total,
                "spread_abs_error": s_ae,
                "total_abs_error": t_ae,
                "prediction_origin": origin,
                "source": g["source"],
            })

    cols = ["game_id", "week", "matchup", "actual_away_pts", "actual_home_pts",
            "actual_home_margin", "actual_total", "predictor", "predicted_spread_home",
            "predicted_total", "spread_abs_error", "total_abs_error", "prediction_origin", "source"]
    with open(os.path.join(DATA, OUT_ROWS), "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, delimiter="|", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    # ---- the derived arithmetic: what one settled game does and does not establish -------------
    g = played[0]
    away_pts, home_pts = int(g["away_pts"]), int(g["home_pts"])
    act_margin, act_total = home_pts - away_pts, home_pts + away_pts
    o, f = orig.get(g["game_id"], {}), fair.get(g["game_id"], {})
    our_spread, our_total = num(o.get("our_spread_home_favoured")), num(o.get("our_total"))
    ar_spread, ar_total = num(o.get("archive_spread_home_favoured")), num(o.get("archive_total"))
    fl_spread, fl_total = num(f.get("fair_spread_home")), num(f.get("fair_total"))

    our_s_ae, our_t_ae = abs(act_margin - our_spread), abs(act_total - our_total)
    naive_s_ae, naive_t_ae = abs(act_margin - mean_margin), abs(act_total - mean_total)
    ar_s_ae, ar_t_ae = abs(act_margin - ar_spread), abs(act_total - ar_total)
    fl_s_ae, fl_t_ae = abs(act_margin - fl_spread), abs(act_total - fl_total)

    p_our_t, n_our_t = pctile(naive_total_err, our_t_ae)
    p_our_s, n_our_s = pctile(naive_margin_err, our_s_ae)
    p_naive_t, n_naive_t = pctile(naive_total_err, naive_t_ae)

    def n_needed(sd, delta):
        return ((Z_ALPHA + Z_BETA) ** 2) * (sd ** 2) / (delta ** 2)

    sd_t, sd_m = st.stdev(totals), st.stdev(margins)

    comp = [
        ("settled week 10 games", "1",
         "official Week 10 scores page, read %s" % g["captured_utc"],
         "only the Thursday-night game is Final; the other 13 kick off 15-16 November", S_SCORES),
        ("official result, W10-01",
         "%s %d at %s %d (home margin %+d, total %d)"
         % (g["away"], away_pts, g["home"], home_pts, act_margin, act_total),
         "transcribed from the official game centre",
         "the first result any line on this site has ever been scored against", g["source"]),
        ("our spread absolute error (pts)", "%.2f" % our_s_ae,
         "abs(actual home margin - our published spread)",
         "worse than a predictor that knows nothing about the teams", g["source"]),
        ("our total absolute error (pts)", "%.2f" % our_t_ae,
         "abs(actual total - our published total)",
         "the single best number on the page, and the one most likely to be luck", g["source"]),
        ("do-nothing season-mean spread error (pts)", "%.2f" % naive_s_ae,
         "abs(actual home margin - weeks 1-9 mean home margin (%.4f))" % mean_margin,
         "the bar our model has to clear", g["source"]),
        ("do-nothing season-mean total error (pts)", "%.4f" % naive_t_ae,
         "abs(actual total - weeks 1-9 mean total (%.4f))" % mean_total,
         "the bar our model has to clear", g["source"]),
        ("our spread vs the do-nothing baseline",
         "%+.2f pts (ours is worse)" % (our_s_ae - naive_s_ae),
         "our spread error minus the season-mean error",
         "our NYG -2.5 lean pointed the wrong way and cost 2.5 points against knowing nothing",
         g["source"]),
        ("our total vs the do-nothing baseline",
         "%+.4f pts (ours is better)" % (our_t_ae - naive_t_ae),
         "our total error minus the season-mean error",
         "our total (45.5) sat 0.43 pts off the league mean (%.4f) - the model added almost "
         "nothing to a number anyone could have written down" % mean_total, g["source"]),
        ("our spread vs the archived price", "%+.2f pts" % (our_s_ae - ar_s_ae),
         "both published NYG -2.5, so both missed by the same margin",
         "a tie is not a win; it means our origination agreed with the community price",
         g["source"]),
        ("our total vs the archived price",
         "%+.2f pts (ours is better)" % (our_t_ae - ar_t_ae),
         "our error %.2f against the archive's %.2f" % (our_t_ae, ar_t_ae),
         "the archive predicted 40.5 against a league mean of %.2f - it was the outlier here, "
         "not us" % mean_total, g["source"]),
        ("points-only fair line: spread / total error (pts)",
         "%.2f / %.2f" % (fl_s_ae, fl_t_ae),
         "same absolute-error arithmetic on data/computed_fair_lines.csv",
         "the simplest model on the site is also the worst on this game", g["source"]),
        ("how average was this game",
         "total landed %.4f pts from the weeks 1-9 mean; %d of %d games (%.1f%%) are that close "
         "or closer" % (naive_t_ae, n_naive_t, len(corpus), p_naive_t),
         "percentile of the game's own distance from the season mean, over the frozen corpus",
         "this is the finding: the game was unusually average, so every total predictor looked "
         "good on it", g["source"]),
        ("chance a naive total lands within %.2f pts" % our_t_ae,
         "%.1f%% (%d of %d games)" % (p_our_t, n_our_t, len(corpus)),
         "share of the %d verified games whose total sits within %.2f pts of the season mean"
         % (len(corpus), our_t_ae),
         "an error this small is rare, which is exactly why it must not be read as skill",
         g["source"]),
        ("chance a naive spread lands within %.2f pts" % our_s_ae,
         "%.1f%% (%d of %d games)" % (p_our_s, n_our_s, len(corpus)),
         "share of the %d verified games whose home margin sits within %.2f pts of the season mean"
         % (len(corpus), our_s_ae),
         "our spread error is the single most common kind of error in the league", g["source"]),
        ("games needed to detect a 1.0-pt total-MAE difference", "%.0f" % n_needed(sd_t, 1.0),
         "n = (z_a + z_b)^2 * SD^2 / delta^2 with SD = %.4f, 80%% power, two-sided 5%%" % sd_t,
         "about ten NFL seasons; one season is %d games" % len(corpus), S_SCORES),
        ("games needed to detect a 1.0-pt spread-MAE difference", "%.0f" % n_needed(sd_m, 1.0),
         "n = (z_a + z_b)^2 * SD^2 / delta^2 with SD = %.4f, 80%% power, two-sided 5%%" % sd_m,
         "one settled game is %.2f%% of that" % (100.0 / n_needed(sd_m, 1.0)), S_SCORES),
        ("verdict", "n=1 establishes nothing",
         "one settled observation against a required sample of about %.0f games"
         % n_needed(sd_m, 1.0),
         "the honest reading of this page is that the pipeline ran end to end and produced a "
         "number - it is not evidence that the number means anything yet", S_SCORES),
    ]
    with open(os.path.join(DATA, OUT_COMPUTED), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="|", lineterminator="\n")
        w.writerow(["metric", "value", "method", "read", "source"])
        for row in comp:
            w.writerow(row)

    print("wrote %s (%d rows) and %s (%d rows)" % (OUT_ROWS, len(rows), OUT_COMPUTED, len(comp)))


if __name__ == "__main__":
    main()
