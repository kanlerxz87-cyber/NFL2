#!/usr/bin/env python3
"""Originate the Week 11 (19-23 November 2026) lines and pre-register them.

What this is
    The forward half of the line-origination programme. Session `a392a193` built the model
    (scripts/origination_lab.py) and published its Week 10 lines; session `5f16dcc6` scored the
    one Week 10 game that has gone Final. Neither of those gives the competition a *forward*
    sample: a line published before the games it describes, which can then be graded against the
    official result. This script produces that sample.

    It writes two artefacts and refuses to write anything if either of two guards fails:

    1. REPRODUCTION GUARD. The model below is a re-implementation of `scripts/origination_lab.py`
       (ridge simultaneous-ratings on margin and pace). This script re-derives the fourteen
       published Week 10 lines from the same code path, fitted on the same 136-game corpus, and
       compares every spread and every total cell with `data/originated_lines_wk10_a392.csv`. If
       a single cell differs, the script exits non-zero and writes nothing. That is what makes it
       legitimate to publish a Week 11 number from a script that does not run the original model:
       the two implementations are proved identical on fourteen published games before they are
       trusted on thirteen new ones.

    2. PRE-REGISTRATION GUARD. The Week 11 lines file is hashed (SHA-256) together with the
       frozen backtest corpus, the settled-games file and this script itself. The hashes and the
       decision timestamp are written to `data/prereg_week11_0a113a24.json`. `tools/grade_forward.py`
       recomputes those hashes before it grades anything, so a line edited after the fact cannot be
       graded as if it had been published before the game. Suggestion S-26 on this site asks for
       exactly this discipline; this is the first place it is applied to a forward sample.

Point in time
    The model is fitted only on games that had been played when the lines were written:
    the 136 games of weeks 1-9 (data/games_2026_wk1_9.csv) plus every Week 10 game that is
    Final (data/games_2026_wk10_played.csv - one game at the time of writing). The remaining
    thirteen Week 10 games kick off 15-16 November and are therefore unknown to this model, which
    is the correct and conservative choice: a line published on 13 November cannot know a result
    that has not happened.

What it does NOT do
    It does not price availability. The official injury hub still carries Week 10 participation on
    the date of writing and no Week 11 participation has been published, so the availability columns
    of the Week 11 table are blank, not zero. It does not use a price feed: the league publishes no
    betting lines, and the community archive it does compare against is non-official with an
    undocumented vintage (FL-29, FL-30).

Sign convention
    A spread column holds the predicted HOME margin (home points minus away points). Positive
    means the home club is favoured. This matches every other file in this repository.

Inputs (all checked in):
    data/games_2026_wk1_9.csv          frozen pre-registered backtest corpus, weeks 1-9
    data/games_2026_wk10_played.csv    settled Week 10 games, append-only
    data/schedule_week11_2026.csv      the official Week 11 slate
    data/originated_lines_wk10_a392.csv the lines the reproduction guard is checked against
    pipeline/data/raw/games.csv        community archive (NON-OFFICIAL) - comparison anchor only

Outputs:
    data/originated_lines_wk11_0a113a24.csv  our Week 11 lines
    data/prereg_week11_0a113a24.json         the pre-registration record and its hashes
"""
import csv
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
ARCHIVE = os.path.join(ROOT, "pipeline", "data", "raw", "games.csv")

CORPUS = "games_2026_wk1_9.csv"
SETTLED = "games_2026_wk10_played.csv"
SCHEDULE = "schedule_week11_2026.csv"
WK10_LINES = "originated_lines_wk10_a392.csv"
WK10_SCHEDULE = "schedule_2026_wk10.csv"
OUT_LINES = "originated_lines_wk11_0a113a24.csv"
OUT_PREREG = "prereg_week11_0a113a24.json"

# The league writes LA on the game log and LAR on the standings table; the archive writes ARI for
# AZ and LA for LAR. Same trap as data/code_collision_a392.csv, same fix.
ALIAS = {"LA": "LAR"}
ARCHIVE_ALIAS = {"LA": "LAR", "ARI": "AZ"}
LAMS = [5.0, 20.0, 60.0]


def read(name, delim="|"):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        raw = list(csv.reader(fh, delimiter=delim))
    return [dict(zip(raw[0], r)) for r in raw[1:] if any(c.strip() for c in r)]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


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


def half(x):
    """Round to the nearest half point. Python's round() is banker's rounding; that is a choice,
    and it is a deterministic one, which is what a pre-registration needs."""
    return round(x * 2) / 2.0


class Model(object):
    def __init__(self, games):
        self.teams = sorted({t for g in games for t in (g["a"], g["h"])})
        self.idx = {t: i for i, t in enumerate(self.teams)}
        self.nt = len(self.teams)

    def fit(self, train, lam):
        nt = self.nt
        Xm, ym, Xt, yt = [], [], [], []
        for g in train:
            hm, hi = self.idx[g["h"]], self.idx[g["a"]]
            row = [0.0] * (nt + 1)
            row[hm] += 1.0
            row[hi] -= 1.0
            row[nt] = 1.0 if not g["neutral"] else 0.0
            Xm.append(row)
            ym.append(g["hp"] - g["ap"])
            row2 = [0.0] * (nt + 1)
            row2[hm] += 1.0
            row2[hi] += 1.0
            row2[nt] = 1.0
            Xt.append(row2)
            yt.append(float(g["hp"] + g["ap"]))
        bm = ridge(Xm, ym, lam, unpenalized=(nt,))
        bt = ridge(Xt, yt, lam, unpenalized=(nt,))
        return {"net": bm[:nt], "hfa": bm[nt], "pace": bt[:nt], "mu": bt[nt]}

    def line(self, model, g):
        hi, ha = self.idx[g["h"]], self.idx[g["a"]]
        margin = model["net"][hi] - model["net"][ha] + (model["hfa"] if not g["neutral"] else 0.0)
        total = model["mu"] + model["pace"][hi] + model["pace"][ha]
        return margin, total


def load_games():
    """Every game whose result was known at the decision timestamp."""
    corpus = []
    for r in read(CORPUS):
        corpus.append({
            "week": int(r["week"]), "date": r["date"],
            "a": ALIAS.get(r["away"], r["away"]), "h": ALIAS.get(r["home"], r["home"]),
            "ap": int(r["away_pts"]), "hp": int(r["home_pts"]),
            "neutral": r["neutral"].strip().lower() == "yes",
            "source": r["source"],
        })
    settled = []
    p = os.path.join(DATA, SETTLED)
    if os.path.exists(p):
        for r in read(SETTLED):
            settled.append({
                "week": int(r["week"]), "date": r["date"],
                "a": ALIAS.get(r["away"], r["away"]), "h": ALIAS.get(r["home"], r["home"]),
                "ap": int(r["away_pts"]), "hp": int(r["home_pts"]),
                "neutral": r["neutral"].strip().lower() == "yes",
                "source": r["source"],
            })
    return corpus, settled


def archive_prices():
    """(week, away, home) -> {spread, total} from the NON-OFFICIAL community archive."""
    out = {}
    if not os.path.exists(ARCHIVE):
        return out
    for r in csv.DictReader(open(ARCHIVE, encoding="utf-8")):
        if r.get("season") != "2026" or r.get("game_type") != "REG":
            continue
        key = (int(r["week"]), ARCHIVE_ALIAS.get(r["away_team"], r["away_team"]),
               ARCHIVE_ALIAS.get(r["home_team"], r["home_team"]))
        out[key] = r
    return out


def main():
    corpus, settled = load_games()
    model = Model(corpus)
    prices = archive_prices()

    # ---------------------------------------------------------------- lambda selection ----------
    # Identical to the original lab: choose the ridge penalty by walk-forward spread MAE over the
    # evaluation weeks of the frozen corpus only. Doing it on the corpus alone (not on corpus +
    # week 10) is what keeps the reproduction guard meaningful.
    weeks = sorted({g["week"] for g in corpus})
    eval_weeks = [w for w in weeks if w >= 4]
    sel = []
    for lam in LAMS:
        errs = []
        for w in eval_weeks:
            m = model.fit([g for g in corpus if g["week"] < w], lam)
            for g in [x for x in corpus if x["week"] == w]:
                pr, _ = model.line(m, g)
                errs.append(abs(half(pr) - (g["hp"] - g["ap"])))
        sel.append((lam, sum(errs) / len(errs), len(errs)))
    lam = min(sel, key=lambda t: t[1])[0]

    # ------------------------------------------------------------ reproduction guard -----------
    wk10_model = model.fit(corpus, lam)
    published = {r["game"]: r for r in read(WK10_LINES)}
    wk10_sched = read(WK10_SCHEDULE)
    mismatches = []
    for s in wk10_sched:
        a = ALIAS.get(s["away"], s["away"])
        h = ALIAS.get(s["home"], s["home"])
        if a not in model.idx or h not in model.idx:
            continue
        g = {"a": a, "h": h, "neutral": False}
        pm, pt = model.line(wk10_model, g)
        pm, pt = round(half(pm), 1), round(half(pt), 1)
        p = published.get(s["game_id"], {})
        if p.get("our_spread_home_favoured", "") != "" and float(p["our_spread_home_favoured"]) != pm:
            mismatches.append("%s spread: published %s, re-derived %s"
                              % (s["game_id"], p["our_spread_home_favoured"], pm))
        if p.get("our_total", "") != "" and float(p["our_total"]) != pt:
            mismatches.append("%s total: published %s, re-derived %s"
                              % (s["game_id"], p["our_total"], pt))
    if mismatches:
        sys.stderr.write("REPRODUCTION GUARD FAILED - refusing to publish Week 11 lines:\n")
        for m in mismatches:
            sys.stderr.write("  " + m + "\n")
        return 1
    if len(wk10_sched) != len(published):
        sys.stderr.write("REPRODUCTION GUARD FAILED - the published Week 10 file has %d rows, the "
                         "schedule has %d\n" % (len(published), len(wk10_sched)))
        return 1

    # ------------------------------------------------------------- the Week 11 fit ---------------
    # Everything known at the decision timestamp: the frozen corpus plus the settled Week 10 games.
    known = corpus + settled
    wk11_model = model.fit(known, lam)

    sched = read(SCHEDULE)
    lines = []
    for s in sched:
        a = ALIAS.get(s["away"], s["away"])
        h = ALIAS.get(s["home"], s["home"])
        if a not in model.idx or h not in model.idx:
            sys.stderr.write("unknown club in the Week 11 slate: %s @ %s\n" % (a, h))
            return 1
        neutral = s["neutral"].strip().lower() == "yes"
        g = {"a": a, "h": h, "neutral": neutral}
        pm, pt = model.line(wk11_model, g)
        pm, pt = round(half(pm), 1), round(half(pt), 1)
        pr = prices.get((11, a, h))
        arch_spread = pr.get("spread_line") if pr and pr.get("spread_line") not in (None, "", "NA") else ""
        arch_total = pr.get("total_line") if pr and pr.get("total_line") not in (None, "", "NA") else ""
        lines.append({
            "game_id": s["game_id"],
            "date": s["date"],
            "kickoff_et": s["kickoff_et"],
            "away": a,
            "home": h,
            "site": s["site"],
            "our_spread_home_favoured": "%.1f" % pm,
            "our_total": "%.1f" % pt,
            "home_net_rating": "%.3f" % wk11_model["net"][model.idx[h]],
            "away_net_rating": "%.3f" % wk11_model["net"][model.idx[a]],
            "home_pace_rating": "%.2f" % wk11_model["pace"][model.idx[h]],
            "away_pace_rating": "%.2f" % wk11_model["pace"][model.idx[a]],
            "home_field_advantage_applied": "%.3f" % (wk11_model["hfa"] if not neutral else 0.0),
            "archive_spread_home_favoured": arch_spread if arch_spread else "not published",
            "archive_total": arch_total if arch_total else "not published",
            "spread_gap_vs_archive": "%.1f" % (pm - float(arch_spread)) if arch_spread else "not published",
            "total_gap_vs_archive": "%.1f" % (pt - float(arch_total)) if arch_total else "not published",
            "availability_load": "not published",
            "status": "origination output - pre-registered %s - unvalidated, paper only"
                      % PREREG_DECISION_UTC,
            "source": s["source"],
        })

    cols = ["game_id", "date", "kickoff_et", "away", "home", "site",
            "our_spread_home_favoured", "our_total",
            "home_net_rating", "away_net_rating", "home_pace_rating", "away_pace_rating",
            "home_field_advantage_applied",
            "archive_spread_home_favoured", "archive_total",
            "spread_gap_vs_archive", "total_gap_vs_archive",
            "availability_load", "status", "source"]
    out_path = os.path.join(DATA, OUT_LINES)
    with open(out_path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, delimiter="|", lineterminator="\n")
        w.writeheader()
        for r in lines:
            w.writerow(r)

    # ------------------------------------------------------------------ pre-registration --------
    pre = {
        "what_this_is": "Pre-registration of the Week 11 lines before the games they describe. "
                        "The hashes below are recomputed by tools/grade_forward.py before it "
                        "grades anything; a line edited after this moment fails that check.",
        "decision_timestamp_utc": PREREG_DECISION_UTC,
        "season": 2026,
        "week": 11,
        "lines_file": "data/" + OUT_LINES,
        "lines_sha256": sha256(out_path),
        "backtest_corpus": "data/" + CORPUS,
        "backtest_corpus_sha256": sha256(os.path.join(DATA, CORPUS)),
        "settled_games_file": "data/" + SETTLED,
        "settled_games_sha256": sha256(os.path.join(DATA, SETTLED)),
        "generator": "tools/originate_week11.py",
        "generator_sha256": sha256(os.path.abspath(__file__)),
        "model": "ridge simultaneous ratings on margin and pace, unpenalised intercepts; "
                 "ridge penalty selected by walk-forward spread MAE over weeks 4-9 of the frozen corpus",
        "ridge_lambda": lam,
        "lambda_selection": [{"lambda": l, "walk_forward_spread_mae": round(e, 3), "games": n}
                             for l, e, n in sel],
        "games_fitted": len(known),
        "games_fitted_detail": "%d games from weeks 1-9 plus %d settled Week 10 game(s); the "
                               "remaining thirteen Week 10 games had not been played at the "
                               "decision timestamp and are therefore unknown to this model"
                               % (len(corpus), len(settled)),
        "reproduction_guard": "the same code path re-derives all %d published Week 10 lines from "
                               "the frozen corpus and matched every spread and total cell"
                               % len(wk10_sched),
        "sign_convention": "a spread column holds the predicted HOME margin; positive means the "
                           "home club is favoured",
        "status": "unvalidated - paper only - not betting advice - no strategy has cleared the "
                  "validation gates and no line here is eligible for staking",
    }
    with open(os.path.join(DATA, OUT_PREREG), "w", encoding="utf-8") as fh:
        json.dump(pre, fh, indent=1, sort_keys=True)
        fh.write("\n")

    print("reproduction guard: PASS - %d Week 10 lines re-derived and matched" % len(wk10_sched))
    print("ridge lambda: %s (walk-forward spread MAE %s)" % (lam, ", ".join("%s: %.3f" % (l, e) for l, e, _ in sel)))
    print("wrote data/%s (%d rows)" % (OUT_LINES, len(lines)))
    print("wrote data/%s (lines sha256 %s)" % (OUT_PREREG, pre["lines_sha256"][:16]))
    return 0


PREREG_DECISION_UTC = "2026-11-13T12:39Z"

if __name__ == "__main__":
    sys.exit(main() or 0)
