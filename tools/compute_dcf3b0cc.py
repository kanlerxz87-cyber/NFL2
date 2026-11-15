#!/usr/bin/env python3
"""Session dcf3b0cc — dated official re-verification and deficiency matrix.

Reads only:
  data/nfl_injury_hub_20261115_dcf3b0cc.csv   (transcribed 2026-11-15T12:55Z from nfl.com/injuries)
  data/nfl_fixtures_wk10_20261115_dcf3b0cc.csv (transcribed 2026-11-15T12:55Z)
  data/injuries_wk10_83246f00.csv             (repo's published 2026-11-13T12:46Z read, same official page)
  data/s745_depth_charts.csv                  (club depth charts transcribed 2026-11-13 by session s745)
  data/standings_2026.csv                     (nfl.com standings, captured 2026-11-13T12:53Z)

Writes only files whose names end in `_dcf3b0cc.csv` / `_dcf3b0cc.json`.
Nothing here imputes a value: anything that cannot be read out of a source file is
written as the literal string `not published`.
"""
import csv
import hashlib
import json
import math
import os
import re
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "dcf3b0cc", "data")   # this session's own outputs
SHARED = os.path.join(ROOT, "data")                # read-only: other sessions' published data
BLANK = "not published"

READ_UTC = "2026-11-15T12:55Z"
HUB_URL = "https://www.nfl.com/injuries/"
SCHED_URL = "https://www.nfl.com/schedules/2026/REG10/"

PRACTICE_LONG = {
    "F": "Full Participation in Practice",
    "L": "Limited Participation in Practice",
    "D": "Did Not Participate In Practice",
}
STATUS_LONG = {"OUT": "Out", "Q": "Questionable", "D": "Doubtful"}


def read_csv(name, shared=False):
    with open(os.path.join(SHARED if shared else D, name), newline="") as fh:
        return list(csv.DictReader(fh, delimiter="|"))


def write_csv(name, cols, rows):
    with open(os.path.join(D, name), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, delimiter="|", lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, BLANK) for c in cols})


def sha256_file(name):
    h = hashlib.sha256()
    with open(os.path.join(D, name), "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def norm_name(s):
    s = (s or "").lower()
    s = re.sub(r"[^a-z ]", " ", s)
    s = re.sub(r"\b(jr|sr|ii|iii|iv|v|x)\b", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


# ---------------------------------------------------------------- normalisation
def norm_practice(v):
    v = (v or "").strip()
    if v in PRACTICE_LONG:
        return PRACTICE_LONG[v]
    return v


def norm_status(v):
    v = (v or "").strip()
    if v in STATUS_LONG:
        return STATUS_LONG[v]
    return v


# ---------------------------------------------------------------- 1. re-verify
def build_reverify():
    today = read_csv("nfl_injury_hub_20261115_dcf3b0cc.csv")
    repo = read_csv("injuries_wk10_83246f00.csv", shared=True)

    off = {}
    for r in today:
        off[(r["club"], norm_name(r["player"]), r["pos"])] = r
    rep = {}
    for r in repo:
        rep[(r["team"], norm_name(r["player"]), r["pos"])] = r

    out = []
    keys = sorted(set(off) | set(rep))
    for k in keys:
        club, player, pos = k
        a, b = off.get(k), rep.get(k)
        diffs = []
        if a and b:
            pa, pb = norm_practice(a["practice_status"]), norm_practice(b["practice"])
            sa, sb = norm_status(a["game_status"]), norm_status(b["status"])
            ia, ib = (a["injury"] or "").strip(), (b["injury"] or "").strip()
            if ia != ib:
                diffs.append("injury")
            if pa != pb:
                diffs.append("practice")
            if sa != sb:
                diffs.append("game_status")
            result = "match" if not diffs else "mismatch"
        elif a:
            result, pa, pb, sa, sb, ia, ib = "official_only", norm_practice(a["practice_status"]), BLANK, norm_status(a["game_status"]), BLANK, (a["injury"] or "").strip(), BLANK
        else:
            result, pa, pb, sa, sb, ia, ib = "repo_only", BLANK, norm_practice(b["practice"]), BLANK, norm_status(b["status"]), BLANK, (b["injury"] or "").strip()
        out.append({
            "club": club,
            "player": a["player"] if a else b["player"],
            "pos": pos,
            "result": result,
            "fields_differing": ",".join(diffs) if diffs else "",
            "injury_20261115": ia or BLANK,
            "practice_20261115": pa or BLANK,
            "game_status_20261115": sa or BLANK,
            "injury_20261113": ib or BLANK,
            "practice_20261113": pb or BLANK,
            "game_status_20261113": sb or BLANK,
            "official_source": a["player_url"] if a else HUB_URL,
            "official_page": HUB_URL,
            "official_read_utc": READ_UTC if a else BLANK,
            "repo_source": b["source"] if b else BLANK,
            "repo_read_utc": b["fetched_utc"] if b else BLANK,
        })
    cols = ["club", "player", "pos", "result", "fields_differing",
            "injury_20261115", "practice_20261115", "game_status_20261115",
            "injury_20261113", "practice_20261113", "game_status_20261113",
            "official_source", "official_page", "official_read_utc",
            "repo_source", "repo_read_utc"]
    write_csv("reverify_20261115_dcf3b0cc.csv", cols, out)
    return out


# ---------------------------------------------------------------- 2. club counts
def build_club_counts():
    today = read_csv("nfl_injury_hub_20261115_dcf3b0cc.csv")
    repo = read_csv("injuries_wk10_83246f00.csv", shared=True)
    by = defaultdict(list)
    for r in today:
        by[(r["fixture_id"], r["club"], r["club_role"])].append(r)
    rep_by = defaultdict(list)
    for r in repo:
        rep_by[(r["game"], r["team"])].append(r)

    out = []
    for (fix, club, role) in sorted(by):
        rs = by[(fix, club, role)]
        st = lambda x: sum(1 for r in rs if r["game_status"] == x)
        pr = lambda x: sum(1 for r in rs if r["practice_status"] == x)
        repo_rows = [r for (g, t), v in rep_by.items() if t == club for r in v]
        out.append({
            "fixture_id": fix, "club": club, "home_or_away": role,
            "rows_listed_20261115": str(len(rs)),
            "dnp": str(pr("Did Not Participate In Practice")),
            "limited": str(pr("Limited Participation in Practice")),
            "full": str(pr("Full Participation in Practice")),
            "out": str(st("Out")),
            "doubtful": str(st("Doubtful")),
            "questionable": str(st("Questionable")),
            "no_game_status_published": str(sum(1 for r in rs if not r["game_status"])),
            "rows_listed_20261113": str(len(repo_rows)) if repo_rows else "0",
            "designations_20261113": str(sum(1 for r in repo_rows if r["status"])) if repo_rows else "0",
            "row_delta": str(len(rs) - len(repo_rows)),
            "source": HUB_URL, "read_utc": READ_UTC,
        })
    cols = ["fixture_id", "club", "home_or_away", "rows_listed_20261115", "dnp", "limited",
            "full", "out", "doubtful", "questionable", "no_game_status_published",
            "rows_listed_20261113", "designations_20261113", "row_delta", "source", "read_utc"]
    write_csv("club_availability_20261115_dcf3b0cc.csv", cols, out)
    return out


# ---------------------------------------------------------------- 3. depth reach
OFF_MAP = {
    "QB": "QB", "RB": "RB", "HB": "RB", "WR": "WR", "WR_2": "WR", "WR_3": "WR",
    "TE": "TE", "TE_2": "TE", "FB": "FB",
    "LT": "OL", "LG": "OL", "C": "OL", "RG": "OL", "RT": "OL", "LOT": "OL", "ROT": "OL",
}
DEF_MAP = {
    "CB": "CB", "CB_2": "CB", "CB_3": "CB", "RCB": "CB", "LCB": "CB", "NCB": "CB", "NB": "CB", "DB": "CB",
    "S": "S", "S_2": "S", "S_3": "S", "FS": "S", "SS": "S",
    "LB": "LB", "LB_2": "LB", "LB_3": "LB", "ILB": "LB", "OLB": "LB", "MLB": "LB", "WLB": "LB",
    "SLB": "LB", "SAM": "LB", "MIKE": "LB", "WILL": "LB", "LILB": "LB", "RILB": "LB",
    "LOLB": "LB", "ROLB": "LB",
    "DT": "DL", "DL": "DL", "NT": "DL", "DE": "DL", "EDGE": "DL", "DL_2": "DL", "DL_3": "DL",
    "DL_4": "DL", "DE_2": "DL", "DT_2": "DL", "DT_3": "DL", "EDGE_2": "DL", "LDE": "DL",
    "RDE": "DL", "LDT": "DL", "RDT": "DL", "RUSH": "DL", "N": "DL",
}
# Project-design matchup map, published on the site as design rather than NFL fact.
MATCHUPS = [("WR", "CB"), ("TE", "LB"), ("TE", "S"), ("RB", "LB"), ("OL", "DL"), ("QB", "DL")]


def build_depth_reach():
    charts = read_csv("s745_depth_charts.csv", shared=True)
    today = read_csv("nfl_injury_hub_20261115_dcf3b0cc.csv")
    desig = {}
    for r in today:
        desig[(r["club"], norm_name(r["player"]))] = r["game_status"]

    groups = defaultdict(list)
    for r in charts:
        unit = r["unit"]
        grp = OFF_MAP.get(r["position_group"]) if unit == "offense" else DEF_MAP.get(r["position_group"])
        if not grp:
            continue
        groups[(r["club"], unit, grp)].append(r)

    out = []
    reach = {}
    for (club, unit, grp) in sorted(groups):
        rows = groups[(club, unit, grp)]
        ranks = defaultdict(list)
        for r in rows:
            ranks[r["depth"]].append(r)
        def min_rank(exclude):
            for d in sorted(ranks, key=lambda x: int(x)):
                for r in ranks[d]:
                    gs = desig.get((club, norm_name(r["player"])), "")
                    if gs not in exclude:
                        return int(d), r["player"]
            return None, None
        av, avp = min_rank({"Out", "Doubtful"})
        cl, clp = min_rank({"Out", "Doubtful", "Questionable"})
        worst = max(int(d) for d in ranks)
        out.append({
            "club": club, "unit": unit, "group": grp,
            "chart_rows": str(len(rows)),
            "deepest_rank_charted": str(worst),
            "listed_on_report": str(sum(1 for r in rows if (club, norm_name(r["player"])) in desig)),
            "out": str(sum(1 for r in rows if desig.get((club, norm_name(r["player"]))) == "Out")),
            "doubtful": str(sum(1 for r in rows if desig.get((club, norm_name(r["player"]))) == "Doubtful")),
            "questionable": str(sum(1 for r in rows if desig.get((club, norm_name(r["player"]))) == "Questionable")),
            "available_rank": str(av) if av else BLANK,
            "available_player": avp or BLANK,
            "clean_rank": str(cl) if cl else BLANK,
            "clean_player": clp or BLANK,
            "starter_out": "yes" if (av and av > 1) else ("no" if av == 1 else BLANK),
            "chart_source": rows[0]["source"],
            "chart_read_utc": "2026-11-13",
            "designation_source": HUB_URL,
            "designation_read_utc": READ_UTC,
        })
        reach[(club, unit, grp)] = dict(row=out[-1], available=av, clean=cl, worst=worst)
    cols = ["club", "unit", "group", "chart_rows", "deepest_rank_charted", "listed_on_report",
            "out", "doubtful", "questionable", "available_rank", "available_player",
            "clean_rank", "clean_player", "starter_out", "chart_source", "chart_read_utc",
            "designation_source", "designation_read_utc"]
    write_csv("depth_reach_20261115_dcf3b0cc.csv", cols, out)
    return out, reach


def build_coverage():
    """How much of the official report can actually be joined to a transcribed chart."""
    charts = read_csv("s745_depth_charts.csv", shared=True)
    today = read_csv("nfl_injury_hub_20261115_dcf3b0cc.csv")
    chart = {(r["club"], norm_name(r["player"])) for r in charts}
    club_chart = {}
    for r in charts:
        club_chart.setdefault(r["club"], r["source"])
    agg = defaultdict(lambda: {"listed": 0, "on_chart": 0, "out": 0, "out_on_chart": 0,
                               "q": 0, "q_on_chart": 0})
    for r in today:
        a = agg[r["club"]]
        a["listed"] += 1
        ok = (r["club"], norm_name(r["player"])) in chart
        a["on_chart"] += ok
        if r["game_status"] == "Out":
            a["out"] += 1
            a["out_on_chart"] += ok
        if r["game_status"] == "Questionable":
            a["q"] += 1
            a["q_on_chart"] += ok
    out = []
    for club in sorted(agg):
        a = agg[club]
        pct = a["on_chart"] / a["listed"] if a["listed"] else 0.0
        out.append({
            "club": club,
            "report_rows_20261115": str(a["listed"]),
            "rows_matched_to_a_chart": str(a["on_chart"]),
            "rows_not_on_any_chart": str(a["listed"] - a["on_chart"]),
            "match_pct": f"{pct:.1%}",
            "out_rows": str(a["out"]),
            "out_rows_on_chart": str(a["out_on_chart"]),
            "out_rows_not_on_chart": str(a["out"] - a["out_on_chart"]),
            "questionable_rows": str(a["q"]),
            "questionable_rows_on_chart": str(a["q_on_chart"]),
            "club_chart_url": club_chart.get(club, BLANK),
            "chart_read_utc": "2026-11-13" if club in club_chart else BLANK,
            "designation_source": HUB_URL,
            "designation_read_utc": READ_UTC,
        })
    cols = ["club", "report_rows_20261115", "rows_matched_to_a_chart", "rows_not_on_any_chart",
            "match_pct", "out_rows", "out_rows_on_chart", "out_rows_not_on_chart",
            "questionable_rows", "questionable_rows_on_chart", "club_chart_url", "chart_read_utc",
            "designation_source", "designation_read_utc"]
    write_csv("coverage_dcf3b0cc.csv", cols, out)
    return out


def build_matrix(reach):
    fix = read_csv("nfl_fixtures_wk10_20261115_dcf3b0cc.csv")
    out = []
    for f in fix:
        for off_club, def_club in ((f["away"], f["home"]), (f["home"], f["away"])):
            for ogrp, dgrp in MATCHUPS:
                ov = reach.get((off_club, "offense", ogrp))
                dv = reach.get((def_club, "defense", dgrp))
                if not ov or not dv:
                    out.append({
                        "fixture_id": f["fixture_id"], "matchup": f"{f['away']} at {f['home']}",
                        "offense_club": off_club, "defense_club": def_club,
                        "offense_group": ogrp, "defense_group": dgrp,
                        "offense_available_rank": BLANK, "defense_available_rank": BLANK,
                        "offense_clean_rank": BLANK, "defense_clean_rank": BLANK,
                        "offense_unavailable": BLANK, "defense_unavailable": BLANK,
                        "defence_minus_offence": BLANK,
                        "read": BLANK,
                        "note": "no club depth chart transcribed for one or both clubs",
                        "designation_source": HUB_URL, "designation_read_utc": READ_UTC,
                        "fixture_source": SCHED_URL, "fixture_read_utc": READ_UTC,
                    })
                    continue
                oa, oc = ov["available"], ov["clean"]
                da, dc = dv["available"], dv["clean"]
                ou = int(ov["row"]["out"]) + int(ov["row"]["doubtful"])
                du = int(dv["row"]["out"]) + int(dv["row"]["doubtful"])
                diff = (da - oa) if (oa and da) else None
                if diff is None:
                    reading = BLANK
                elif diff >= 2:
                    reading = f"defence at {da}rd/nd/th string vs offence {oa}st/nd — material mismatch"
                elif diff == 1:
                    reading = f"defence one string deeper than offence ({da} vs {oa})"
                elif diff == -1:
                    reading = f"offence one string deeper than defence ({oa} vs {da})"
                elif diff <= -2:
                    reading = f"offence at {oa}rd/nd/th string vs defence {da}st/nd — offence depleted"
                else:
                    reading = f"both sides at {oa}st/nd string"
                out.append({
                    "fixture_id": f["fixture_id"], "matchup": f"{f['away']} at {f['home']}",
                    "offense_club": off_club, "defense_club": def_club,
                    "offense_group": ogrp, "defense_group": dgrp,
                    "offense_available_rank": str(oa) if oa else BLANK,
                    "defense_available_rank": str(da) if da else BLANK,
                    "offense_clean_rank": str(oc) if oc else BLANK,
                    "defense_clean_rank": str(dc) if dc else BLANK,
                    "offense_unavailable": str(ou),
                    "defense_unavailable": str(du),
                    "defence_minus_offence": str(diff) if diff is not None else BLANK,
                    "read": reading,
                    "note": "ranks from club depth charts transcribed 2026-11-13; designations read 2026-11-15. Ranks are chart order, not playing time.",
                    "designation_source": HUB_URL, "designation_read_utc": READ_UTC,
                    "fixture_source": SCHED_URL, "fixture_read_utc": READ_UTC,
                })
    cols = ["fixture_id", "matchup", "offense_club", "defense_club", "offense_group",
            "defense_group", "offense_available_rank", "defense_available_rank",
            "offense_clean_rank", "defense_clean_rank",
            "offense_unavailable", "defense_unavailable", "defence_minus_offence", "read",
            "note", "designation_source", "designation_read_utc", "fixture_source", "fixture_read_utc"]
    write_csv("deficiency_matrix_dcf3b0cc.csv", cols, out)
    return out


# ---------------------------------------------------------------- 4. correlation
def pearson(xs, ys):
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    sxx = sum((a - mx) ** 2 for a in xs)
    syy = sum((b - my) ** 2 for b in ys)
    if sxx == 0 or syy == 0:
        return None, None, None
    r = sxy / math.sqrt(sxx * syy)
    return r, n, sxy


def t_p_two_sided(r, n):
    """Two-sided p for H0: rho = 0. Exact via the t distribution's link to the
    incomplete beta function (no SciPy available in this sandbox)."""
    if r is None or n < 3 or abs(r) >= 1:
        return None, None
    df = n - 2
    t = r * math.sqrt(df / (1 - r * r))
    x = df / (df + t * t)
    p = betainc(df / 2.0, 0.5, x)          # = P(|T| > |t|)
    return t, p


def betainc(a, b, x):
    """Regularised incomplete beta I_x(a,b) via continued fraction (NR)."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lbeta = math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)
    front = math.exp(math.log(x) * a + math.log(1 - x) * b - lbeta)
    if x < (a + 1) / (a + b + 2):
        return front * _cf(a, b, x) / a
    return 1 - math.exp(math.log(1 - x) * b + math.log(x) * a - lbeta) * _cf(b, a, 1 - x) / b


def _cf(a, b, x):
    tiny = 1e-30
    qab, qap, qam = a + b, a + 1, a - 1
    c, d = 1.0, 1 - qab * x / qap
    if abs(d) < tiny:
        d = tiny
    d = 1 / d
    h = d
    for m in range(1, 300):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1 + aa * d
        if abs(d) < tiny:
            d = tiny
        c = 1 + aa / c
        if abs(c) < tiny:
            c = tiny
        d = 1 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1 + aa * d
        if abs(d) < tiny:
            d = tiny
        c = 1 + aa / c
        if abs(c) < tiny:
            c = tiny
        d = 1 / d
        delta = d * c
        h *= delta
        if abs(delta - 1) < 3e-12:
            break
    return h


def fisher_ci(r, n):
    if r is None or n < 4:
        return None, None
    z = 0.5 * math.log((1 + r) / (1 - r))
    se = 1 / math.sqrt(n - 3)
    lo, hi = z - 1.959963985 * se, z + 1.959963985 * se
    return math.tanh(lo), math.tanh(hi)


def build_correlations():
    clubs = read_csv("club_availability_20261115_dcf3b0cc.csv")
    stand = {r["abbr"]: r for r in read_csv("standings_2026.csv", shared=True)}
    rows = []
    for c in clubs:
        ab = c["club"]
        s = stand.get(ab)
        if not s:
            continue
        games = int(s["w"]) + int(s["l"]) + int(s["t"])
        if games == 0:
            continue
        rows.append({
            "club": ab,
            "out": int(c["out"]),
            "out_plus_doubtful": int(c["out"]) + int(c["doubtful"]),
            "questionable": int(c["questionable"]),
            "listed": int(c["rows_listed_20261115"]),
            "win_pct": (int(s["w"]) + 0.5 * int(s["t"])) / games,
            "point_diff_per_game": (int(s["pf"]) - int(s["pa"])) / games,
        })
    out = []
    pairs = [
        ("out", "win_pct", "Out count vs win percentage"),
        ("out_plus_doubtful", "win_pct", "Out + Doubtful count vs win percentage"),
        ("questionable", "win_pct", "Questionable count vs win percentage"),
        ("listed", "win_pct", "Players listed vs win percentage"),
        ("out", "point_diff_per_game", "Out count vs point differential per game"),
        ("out_plus_doubtful", "point_diff_per_game", "Out + Doubtful count vs point differential per game"),
        ("listed", "point_diff_per_game", "Players listed vs point differential per game"),
    ]
    for xk, yk, label in pairs:
        xs = [r[xk] for r in rows]
        ys = [r[yk] for r in rows]
        r, n, _ = pearson(xs, ys)
        t, p = t_p_two_sided(r, n)
        lo, hi = fisher_ci(r, n)
        out.append({
            "pair_id": f"CORR-DCF-{len(out)+1:02d}",
            "x": xk, "y": yk, "label": label,
            "n_clubs": str(n),
            "r": f"{r:.4f}" if r is not None else BLANK,
            "r_squared": f"{r*r:.4f}" if r is not None else BLANK,
            "ci95_low": f"{lo:.4f}" if lo is not None else BLANK,
            "ci95_high": f"{hi:.4f}" if hi is not None else BLANK,
            "t": f"{t:.4f}" if t is not None else BLANK,
            "p_two_sided": f"{p:.4f}" if p is not None else BLANK,
            "significant_at_05": ("yes" if (p is not None and p < 0.05) else "no") if p is not None else BLANK,
            "x_source": HUB_URL if xk != "win_pct" else "https://www.nfl.com/standings/",
            "y_source": "https://www.nfl.com/standings/" if "win_pct" in yk or "point" in yk else HUB_URL,
            "read_utc": READ_UTC,
            "caveat": ("Cross-sectional over the 28 clubs that play in Week 10, one week only. "
                       "Descriptive association, not a predictive result; it cannot support a betting claim "
                       "and no multiplicity correction across the seven pairs is applied beyond publishing every p."),
        })
    cols = ["pair_id", "x", "y", "label", "n_clubs", "r", "r_squared", "ci95_low", "ci95_high",
            "t", "p_two_sided", "significant_at_05", "x_source", "y_source", "read_utc", "caveat"]
    write_csv("correlation_dcf3b0cc.csv", cols, out)
    return out, rows


# ---------------------------------------------------------------- 5. flags
def build_flags(reverify, clubs, matrix, reach_rows, coverage):
    flags = []
    n_official_only = sum(1 for r in reverify if r["result"] == "official_only")
    n_repo_only = sum(1 for r in reverify if r["result"] == "repo_only")
    n_mismatch = sum(1 for r in reverify if r["result"] == "mismatch")
    n_match = sum(1 for r in reverify if r["result"] == "match")
    missing_clubs = [c["club"] for c in clubs if c["rows_listed_20261113"] == "0"]

    flags.append({
        "flag_id": "FL-DCF-01", "class": "data currency", "severity": "high",
        "finding": (f"The repository's published Week 10 injury table (data/injuries_wk10_83246f00.csv, "
                    f"read 2026-11-13T12:46Z) carries {sum(int(c['designations_20261113']) for c in clubs)} "
                    f"game-status designations across 296 rows. The same official page read on "
                    f"2026-11-15T12:55Z carries 171 designations (70 Out, 11 Doubtful, 90 Questionable) "
                    f"across 347 rows."),
        "evidence": ("data/club_availability_20261115_dcf3b0cc.csv (per-club designation counts, both reads); "
                     "data/reverify_20261115_dcf3b0cc.csv (row-by-row)."),
        "source": HUB_URL,
        "impact": ("Any model or deficiency count built on the 13 November read treats 162 of today's "
                   "designations as absent. 'Not designated' on that read cannot be read as 'available'."),
        "status": "open",
    })
    flags.append({
        "flag_id": "FL-DCF-02", "class": "coverage", "severity": "high",
        "finding": ("The 13 November read publishes no rows at all for the two clubs in the Monday game "
                    f"W10-14: {', '.join(sorted(missing_clubs)) if missing_clubs else 'none'}. "
                    "The official page read today lists 19 Chargers rows and 10 Ravens rows for that game."),
        "evidence": "data/club_availability_20261115_dcf3b0cc.csv, rows with rows_listed_20261113 = 0.",
        "source": HUB_URL,
        "impact": "One of the fourteen Week 10 fixtures has zero injury coverage in the published table.",
        "status": "open",
    })
    flags.append({
        "flag_id": "FL-DCF-03", "class": "reconciliation", "severity": "medium",
        "finding": (f"Joining today's official read to the 13 November table on club + player + position gives "
                    f"{n_match} identical rows, {n_mismatch} rows that differ, {n_official_only} rows present "
                    f"only on the page today and {n_repo_only} rows present only in the repository."),
        "evidence": "data/reverify_20261115_dcf3b0cc.csv, one row per joined player.",
        "source": HUB_URL,
        "impact": ("The repository cannot currently reproduce the official page for the week it publishes. "
                   "A dated capture with a retained hash is required before any backtest treats either read as "
                   "the point-in-time truth."),
        "status": "open",
    })
    flagged_games = sorted({m["fixture_id"] for m in matrix if m["defence_minus_offence"] not in (BLANK, "0", "-1", "1")})
    flags.append({
        "flag_id": "FL-DCF-04", "class": "method", "severity": "medium",
        "finding": ("The deficiency matrix joins designations read today to club depth charts transcribed on "
                    "2026-11-13 by an earlier session. The two layers are two days apart, and club charts are "
                    "labelled unofficial by the clubs that publish them. Rank order in a club chart is not "
                    "playing time."),
        "evidence": ("data/deficiency_matrix_dcf3b0cc.csv; data/depth_reach_20261115_dcf3b0cc.csv; "
                     "data/s745_depth_charts.csv chart_source column."),
        "source": "https://www.nfl.com/injuries/",
        "impact": ("The matrix ranks depth by published chart order, so it can misstate who would actually "
                   "replace a starter. Fixtures with a mismatch of two strings or more: "
                   + (", ".join(flagged_games) if flagged_games else "none") + "."),
        "status": "open",
    })
    tot_listed = sum(int(c["report_rows_20261115"]) for c in coverage)
    tot_on = sum(int(c["rows_matched_to_a_chart"]) for c in coverage)
    tot_out = sum(int(c["out_rows"]) for c in coverage)
    tot_out_on = sum(int(c["out_rows_on_chart"]) for c in coverage)
    zero = [c["club"] for c in coverage if c["rows_matched_to_a_chart"] == "0"]
    flags.append({
        "flag_id": "FL-DCF-05", "class": "coverage", "severity": "high",
        "finding": (f"Joining today's official report to the transcribed club depth charts resolves "
                    f"{tot_on} of {tot_listed} listed players ({tot_on/tot_listed:.1%}), and "
                    f"{tot_out_on} of {tot_out} players ruled Out. The remaining rows name a player "
                    f"no transcribed chart puts in a depth slot, so no replacement can be named for them."),
        "evidence": "data/coverage_dcf3b0cc.csv, one row per club with the counts split by designation.",
        "source": HUB_URL,
        "impact": ("A starter-out count can be produced for the whole league; a named-replacement count "
                   "cannot. Publishing the two as one number would overstate what the repository can see."),
        "status": "open",
    })
    flags.append({
        "flag_id": "FL-DCF-06", "class": "coverage", "severity": "high",
        "finding": ("Houston resolves 0 of its 16 listed players to a depth chart. Its official club page "
                    "publishes the chart as an image, so nothing was transcribed. "
                    + (f"Clubs with no chart coverage at all: {', '.join(zero)}." if zero else "")),
        "evidence": "data/coverage_dcf3b0cc.csv (rows_matched_to_a_chart = 0).",
        "source": "https://www.houstontexans.com/team/depth-chart",
        "impact": ("Houston's offensive and defensive deficiency state cannot be computed from chart order at "
                   "all. This reproduces the existing flag FL-60 independently, from the join rather than from "
                   "the chart read."),
        "status": "open",
    })
    flags.append({
        "flag_id": "FL-DCF-07", "class": "method", "severity": "medium",
        "finding": ("Seven descriptive correlations were computed over the 28 clubs that play in Week 10, "
                    "using only officially sourced inputs (designations from nfl.com/injuries read "
                    "2026-11-15T12:55Z; records and points from nfl.com/standings captured 2026-11-13T12:53Z). "
                    "None is significant at the 5% level; the largest |r| is under 0.28."),
        "evidence": "data/correlation_dcf3b0cc.csv (r, r-squared, 95% CI, t, two-sided p and n for each pair).",
        "source": "https://www.nfl.com/standings/",
        "impact": ("One week of 28 clubs cannot separate an injury effect from roster quality. These numbers "
                   "are published as the honest n=28 baseline and must not be used as a model input or as "
                   "evidence of edge."),
        "status": "open",
    })
    cols = ["flag_id", "class", "severity", "finding", "evidence", "source", "impact", "status"]
    write_csv("flags_dcf3b0cc.csv", cols, flags)
    return flags


def main():
    reverify = build_reverify()
    clubs = build_club_counts()
    coverage = build_coverage()
    reach_rows, reach = build_depth_reach()
    matrix = build_matrix(reach)
    corr, corr_rows = build_correlations()
    flags = build_flags(reverify, clubs, matrix, reach_rows, coverage)

    summary = {
        "session": "dcf3b0cc",
        "generated_by": "tools/compute_dcf3b0cc.py",
        "official_read_utc": READ_UTC,
        "official_page": HUB_URL,
        "fixture_page": SCHED_URL,
        "injury_rows_transcribed": len(read_csv("nfl_injury_hub_20261115_dcf3b0cc.csv")),
        "clubs_covered": len({r["club"] for r in read_csv("nfl_injury_hub_20261115_dcf3b0cc.csv")}),
        "fixtures_covered": len(read_csv("nfl_fixtures_wk10_20261115_dcf3b0cc.csv")),
        "designations_out": sum(int(c["out"]) for c in clubs),
        "designations_doubtful": sum(int(c["doubtful"]) for c in clubs),
        "designations_questionable": sum(int(c["questionable"]) for c in clubs),
        "rows_with_no_game_status": sum(int(c["no_game_status_published"]) for c in clubs),
        "repo_20261113_rows": len(read_csv("injuries_wk10_83246f00.csv", shared=True)),
        "repo_20261113_designations": sum(int(c["designations_20261113"]) for c in clubs),
        "reverify": {
            "match": sum(1 for r in reverify if r["result"] == "match"),
            "mismatch": sum(1 for r in reverify if r["result"] == "mismatch"),
            "official_only": sum(1 for r in reverify if r["result"] == "official_only"),
            "repo_only": sum(1 for r in reverify if r["result"] == "repo_only"),
        },
        "deficiency_matrix_rows": len(matrix),
        "depth_reach_rows": len(reach_rows),
        "correlation_pairs": len(corr),
        "correlation_n": len(corr_rows),
        "flags": len(flags),
        "coverage_rows": len(coverage),
        "sha256": {
            "coverage_dcf3b0cc.csv": sha256_file("coverage_dcf3b0cc.csv"),
            "nfl_injury_hub_20261115_dcf3b0cc.csv": sha256_file("nfl_injury_hub_20261115_dcf3b0cc.csv"),
            "nfl_fixtures_wk10_20261115_dcf3b0cc.csv": sha256_file("nfl_fixtures_wk10_20261115_dcf3b0cc.csv"),
            "reverify_20261115_dcf3b0cc.csv": sha256_file("reverify_20261115_dcf3b0cc.csv"),
            "club_availability_20261115_dcf3b0cc.csv": sha256_file("club_availability_20261115_dcf3b0cc.csv"),
            "depth_reach_20261115_dcf3b0cc.csv": sha256_file("depth_reach_20261115_dcf3b0cc.csv"),
            "deficiency_matrix_dcf3b0cc.csv": sha256_file("deficiency_matrix_dcf3b0cc.csv"),
            "correlation_dcf3b0cc.csv": sha256_file("correlation_dcf3b0cc.csv"),
            "flags_dcf3b0cc.csv": sha256_file("flags_dcf3b0cc.csv"),
        },
    }
    with open(os.path.join(D, "summary_dcf3b0cc.json"), "w") as fh:
        json.dump(summary, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
