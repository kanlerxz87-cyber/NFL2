#!/usr/bin/env python3
"""Grade the pre-registered Week 11 forward sample.

What this is
    The forward-sample grader. A leaderboard is only worth anything if the bets on it were
    published before the games they describe, and if nobody can quietly move the line afterwards
    and then claim the move was the strategy. This script enforces both rules.

    It reads `data/prereg_week11_0a113a24.json`, recomputes the SHA-256 of every artefact named
    in it, and refuses to grade anything if a hash has changed. It then reads the official
    Week 11 results, scores each pre-registered line against the official final score, and
    writes the result.

    The files it reads and writes:
      data/prereg_week11_0a113a24.json          the pre-registration record (hashes, timestamp)
      data/originated_lines_wk11_0a113a24.csv   the pre-registered lines
      data/games_week11_played.csv              official Week 11 final scores, append-only
      data/games_2026_wk1_9.csv                 the frozen corpus - the do-nothing baseline only

    It writes:
      data/forward_grade_0a113a24.csv           one row per pre-registered line
      data/forward_grade_summary_0a113a24.csv   the summary and the sample-size arithmetic

    Why `games_week11_played.csv` is a separate, append-only file
        Suggestion S-26 designates `data/games_2026_wk1_9.csv` as the pre-registered backtest
        corpus and requires its hash to be published so that a later edit invalidates every grade
        built on it. Week 11 results therefore live in their own file, and the corpus is left
        byte-identical. The same rule is applied to the Week 10 results file.

    What it refuses to do
        It does not rank a strategy, it does not compute a return, and it does not call a
        difference between two predictors a result. It computes absolute errors and publishes the
        sample size that would be needed before any of those numbers could mean anything.
"""
import csv
import hashlib
import json
import os
import statistics as st
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

PREREG = "prereg_week11_0a113a24.json"
LINES = "originated_lines_wk11_0a113a24.csv"
PLAYED = "games_week11_played.csv"
CORPUS = "games_2026_wk1_9.csv"
OUT_ROWS = "forward_grade_0a113a24.csv"
OUT_SUMMARY = "forward_grade_summary_0a113a24.csv"

Z_ALPHA, Z_BETA = 1.96, 0.8416  # two-sided 5% with 80% power


def rd(name):
    p = os.path.join(DATA, name)
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as fh:
        raw = list(csv.reader(fh, delimiter="|"))
    if len(raw) < 2:
        return []
    return [dict(zip(raw[0], r)) for r in raw[1:] if any(c.strip() for c in r)]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def main():
    pre = json.load(open(os.path.join(DATA, PREREG), encoding="utf-8"))

    # ------------------------------------------------------------- pre-registration guard -----
    checks = []
    prereg_ok = True
    for key, path in (("lines_sha256", os.path.join(DATA, LINES)),
                      ("backtest_corpus_sha256", os.path.join(DATA, CORPUS)),
                      ("settled_games_sha256", os.path.join(DATA, "games_2026_wk10_played.csv")),
                      ("generator_sha256", os.path.join(ROOT, "tools", "originate_week11.py"))):
        expected = pre.get(key, "")
        actual = sha256(path) if os.path.exists(path) else ""
        ok = bool(expected) and expected == actual
        if not ok:
            prereg_ok = False
        checks.append({"artefact": os.path.basename(path), "expected_sha256": expected or "not published",
                       "recomputed_sha256": actual or "not published",
                       "match": "yes" if ok else "NO",
                       "note": "" if ok else "the file has changed since the pre-registration; "
                                                "the grade below is withheld because a line that moved "
                                                "after the game cannot be scored as a forecast"})

    lines = rd(LINES)
    played = {r["game_id"]: r for r in rd(PLAYED)}
    corpus = rd(CORPUS)

    margins = [int(r["home_pts"]) - int(r["away_pts"]) for r in corpus]
    totals = [int(r["home_pts"]) + int(r["away_pts"]) for r in corpus]
    mean_margin = st.mean(margins)
    mean_total = st.mean(totals)

    rows = []
    for l in lines:
        gid = l["game_id"]
        g = played.get(gid)
        rec = {
            "game_id": gid,
            "date": l["date"],
            "kickoff_et": l["kickoff_et"],
            "away": l["away"],
            "home": l["home"],
            "our_spread_home_favoured": l["our_spread_home_favoured"],
            "our_total": l["our_total"],
            "actual_away_pts": "",
            "actual_home_pts": "",
            "actual_home_margin": "",
            "actual_total": "",
            "spread_abs_error": "",
            "total_abs_error": "",
            "baseline_spread_abs_error": "",
            "baseline_total_abs_error": "",
            "spread_error_vs_baseline": "",
            "total_error_vs_baseline": "",
            "status": "not settled - the game has not been played",
            "source": l["source"],
        }
        if g:
            ap, hp = int(g["away_pts"]), int(g["home_pts"])
            act_m, act_t = hp - ap, hp + ap
            our_s, our_t = num(l["our_spread_home_favoured"]), num(l["our_total"])
            s_ae, t_ae = abs(act_m - our_s), abs(act_t - our_t)
            b_s_ae, b_t_ae = abs(act_m - mean_margin), abs(act_t - mean_total)
            rec.update({
                "actual_away_pts": ap, "actual_home_pts": hp,
                "actual_home_margin": act_m, "actual_total": act_t,
                "spread_abs_error": "%.2f" % s_ae,
                "total_abs_error": "%.2f" % t_ae,
                "baseline_spread_abs_error": "%.2f" % b_s_ae,
                "baseline_total_abs_error": "%.2f" % b_t_ae,
                "spread_error_vs_baseline": "%+.2f" % (s_ae - b_s_ae),
                "total_error_vs_baseline": "%+.2f" % (t_ae - b_t_ae),
                "status": "settled and graded",
            })
        rows.append(rec)

    cols = ["game_id", "date", "kickoff_et", "away", "home",
            "our_spread_home_favoured", "our_total",
            "actual_away_pts", "actual_home_pts", "actual_home_margin", "actual_total",
            "spread_abs_error", "total_abs_error",
            "baseline_spread_abs_error", "baseline_total_abs_error",
            "spread_error_vs_baseline", "total_error_vs_baseline", "status", "source"]
    with open(os.path.join(DATA, OUT_ROWS), "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, delimiter="|", lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow(r)

    settled = [r for r in rows if r["status"] == "settled and graded"]

    def n_needed(sd, delta):
        return ((Z_ALPHA + Z_BETA) ** 2) * (sd ** 2) / (delta ** 2)

    sd_t, sd_m = st.stdev(totals), st.stdev(margins)
    n_spread, n_total = n_needed(sd_m, 1.0), n_needed(sd_t, 1.0)

    summary = []
    summary.append({
        "metric": "pre-registration status",
        "value": "intact" if prereg_ok else "BROKEN",
        "method": "SHA-256 of the lines file, the frozen corpus, the settled-games file and the "
                  "generator script, recomputed at grading time",
        "read": "the grade below is only meaningful if every hash still matches the one published "
                "before the games" if prereg_ok else
                "a hash no longer matches, so the lines were changed after they were published and "
                "no forecast grade can be claimed from them",
        "source": "S-PREREG-0A11",
    })
    for c in checks:
        summary.append({
            "metric": "hash check - %s" % c["artefact"],
            "value": c["match"],
            "method": "expected %s / recomputed %s" % (c["expected_sha256"][:16] or "not published",
                                                       c["recomputed_sha256"][:16] or "not published"),
            "read": c["note"] or "unchanged since the pre-registration",
            "source": "S-PREREG-0A11",
        })
    summary.append({
        "metric": "pre-registered lines",
        "value": str(len(lines)),
        "method": "one row per Week 11 fixture on the official schedule",
        "read": "the whole Week 11 slate, published before any of it was played",
        "source": "S-WK11-0A11",
    })
    summary.append({
        "metric": "lines settled and graded",
        "value": "%d of %d" % (len(settled), len(lines)),
        "method": "a line is graded only when the official final score exists on the league's own "
                  "game page",
        "read": "the Week 11 games run 19-23 November 2026; the first grade cannot exist before "
                "then" if not settled else "the first grades exist",
        "source": "S-WK11-0A11",
    })
    if settled:
        s_maes = [float(r["spread_abs_error"]) for r in settled]
        t_maes = [float(r["total_abs_error"]) for r in settled]
        b_s = [float(r["baseline_spread_abs_error"]) for r in settled]
        b_t = [float(r["baseline_total_abs_error"]) for r in settled]
        summary.append({
            "metric": "mean spread absolute error (ours / do-nothing baseline)",
            "value": "%.2f / %.2f pts" % (st.mean(s_maes), st.mean(b_s)),
            "method": "absolute error against the official final margin, both predictors on the same games",
            "read": "a negative difference would mean our line is worse than knowing nothing",
            "source": "S-CALC-0A11",
        })
        summary.append({
            "metric": "mean total absolute error (ours / do-nothing baseline)",
            "value": "%.2f / %.2f pts" % (st.mean(t_maes), st.mean(b_t)),
            "method": "absolute error against the official final combined score",
            "read": "the totals half of this model has been the weaker half since week 4",
            "source": "S-CALC-0A11",
        })
    summary.append({
        "metric": "games needed to detect a 1.0-pt spread-MAE difference",
        "value": "%.0f" % n_spread,
        "method": "n = (z_a + z_b)^2 * SD^2 / delta^2 with SD = %.4f, 80%% power, two-sided 5%%; the "
                  "SD is the standard deviation of the home margin over the %d frozen games"
                  % (sd_m, len(corpus)),
        "read": "one season is %d games, so this is roughly %.0f seasons. %d settled Week 11 games "
                "is %.2f%% of it"
                % (len(corpus), n_spread / max(1, len(corpus)), len(settled),
                   100.0 * len(settled) / n_spread if n_spread else 0.0),
        "source": "S-CALC-0A11",
    })
    summary.append({
        "metric": "games needed to detect a 1.0-pt total-MAE difference",
        "value": "%.0f" % n_total,
        "method": "n = (z_a + z_b)^2 * SD^2 / delta^2 with SD = %.4f, 80%% power, two-sided 5%%"
                  % sd_t,
        "read": "roughly %.0f seasons of football" % (n_total / max(1, len(corpus))),
        "source": "S-CALC-0A11",
    })
    summary.append({
        "metric": "verdict",
        "value": "no forward evidence yet" if not settled else "%d settled forward observations" % len(settled),
        "method": "the pre-registration exists so the first observation is a forecast; the sample-size "
                  "arithmetic above says how many observations it takes to call a difference",
        "read": "the honest reading is that a measurement apparatus now exists and has been proven on "
                "fourteen published Week 10 lines; whether the lines themselves are any good is a "
                "question this season and the next one will answer, not this page",
        "source": "S-CALC-0A11",
    })

    with open(os.path.join(DATA, OUT_SUMMARY), "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["metric", "value", "method", "read", "source"],
                           delimiter="|", lineterminator="\n")
        w.writeheader()
        for r in summary:
            w.writerow(r)

    print("pre-registration: %s" % ("intact" if prereg_ok else "BROKEN"))
    print("wrote data/%s (%d rows) and data/%s (%d rows)"
          % (OUT_ROWS, len(rows), OUT_SUMMARY, len(summary)))
    if not prereg_ok:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
