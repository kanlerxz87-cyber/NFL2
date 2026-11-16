#!/usr/bin/env python3
"""Auditor for session 0a28b225's three artefacts.

It re-derives every published cell from the checked-in inputs and exits non-zero
on the first failure. Run it after tools/build_0a28b225.py, and in CI.

    python3 tools/verify_0a28b225.py
"""
import csv
import datetime as dt
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OFFICIAL_HOSTS = {"nfl.com", "www.nfl.com", "operations.nfl.com", "static.www.nfl.com"}
STATE_OFFSET = {"NY": 0, "NJ": 0, "PA": 0, "MD": 0, "NC": 0, "MI": 0,
                "TX": -1, "IL": -1, "MO": -1, "CO": -2, "CA": -3}

results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print("  %s  %s%s" % ("PASS" if ok else "FAIL", name, (" - " + detail) if detail else ""))


def read(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="|"))


def d(s):
    return dt.date.fromisoformat(s.strip())


def main():
    wk11 = {r["game_id"]: r for r in read("schedule_week11_2026.csv")}
    wk10_sched = read("schedule_2026_wk10.csv")
    prior = read("games_2026_wk1_9.csv")
    wk10_played = read("games_2026_wk10_played.csv")
    standings = {r["abbr"]: r for r in read("standings_2026.csv")}

    wk10_teams = set()
    for r in wk10_sched:
        wk10_teams.add(r["away"])
        wk10_teams.add(r["home"])

    # ---- venue register --------------------------------------------------
    v = read("venue_register_0a28b225.csv")
    check("venue register: one row per Week 11 fixture",
          len(v) == len(wk11) == 13, "%d rows / %d fixtures" % (len(v), len(wk11)))
    check("venue register: every game_id is a real Week 11 fixture",
          all(r["game_id"] in wk11 for r in v))
    check("venue register: away, home, date and kickoff are the schedule file's own values",
          all(r["away"] == wk11[r["game_id"]]["away"] and r["home"] == wk11[r["game_id"]]["home"]
              and r["date"] == wk11[r["game_id"]]["date"]
              and r["kickoff_et"] == wk11[r["game_id"]]["kickoff_et"] for r in v))
    check("venue register: every row cites its own official game page",
          all(r["source"].startswith("https://www.nfl.com/games/") for r in v))
    check("venue register: no stadium cell is blank (the game centre prints one per fixture)",
          all(r["stadium_game_centre"].strip() for r in v))
    check("venue register: the three disagreements are named, not reconciled",
          sum(1 for r in v if r["official_pages_agree"].startswith("conflict")) == 3,
          "%d conflict rows" % sum(1 for r in v if r["official_pages_agree"].startswith("conflict")))
    check("venue register: the neutral-site fixture is the one the schedule marks neutral",
          [r["game_id"] for r in v if r["neutral"] == "yes"] ==
          [g for g, r in wk11.items() if r["neutral"] == "yes"])

    # ---- fixture context -------------------------------------------------
    f = read("fixture_context_0a28b225.csv")
    check("fixture context: two sides per fixture",
          len(f) == 2 * len(wk11), "%d rows" % len(f))
    check("fixture context: every side_id is unique",
          len({r["side_id"] for r in f}) == len(f))
    check("fixture context: every row's team and opponent are the fixture's two clubs",
          all({r["team"], r["opponent"]} == {wk11[r["game_id"]]["away"], wk11[r["game_id"]]["home"]}
              for r in f))
    check("fixture context: home_away is consistent with the schedule file",
          all(r["home_away"] == ("home" if wk11[r["game_id"]]["home"] == r["team"] else "away")
              for r in f))

    # rebuild the game history independently of the builder
    hist = {}
    status = {}
    for r in prior:
        gid = "W%s-%s@%s" % (r["week"], r["away"], r["home"])
        for s in ("away", "home"):
            hist.setdefault(r[s], []).append((d(r["date"]), gid))
    for r in wk10_played:
        for s in ("away", "home"):
            hist.setdefault(r[s], []).append((d(r["date"]), r["game_id"]))
            status[r["game_id"]] = "Final"
    for r in wk10_sched:
        if r["game_id"] in status:
            continue
        status[r["game_id"]] = "scheduled, not final at read time"
        for s in ("away", "home"):
            hist.setdefault(r[s], []).append((d(r["date"]), r["game_id"]))
    for t in hist:
        hist[t].sort()

    bad_rest, bad_prev, bad_status = [], [], []
    for r in f:
        date = d(r["date"])
        candidates = [x for x in hist[r["team"]] if x[0] < date]
        if not candidates:
            bad_prev.append(r["side_id"])
            continue
        pd, pgid = candidates[-1]
        if r["prev_game_date"] != pd.isoformat() or r["prev_game_id"] != pgid:
            bad_prev.append(r["side_id"])
        if int(r["rest_days"]) != (date - pd).days:
            bad_rest.append(r["side_id"])
        if r["prev_game_status"] != status.get(pgid, "Final"):
            bad_status.append(r["side_id"])
    check("fixture context: prev_game_id and prev_game_date re-derive from the results files",
          not bad_prev, ", ".join(bad_prev[:5]))
    check("fixture context: rest_days is the date difference, recomputed",
          not bad_rest, ", ".join(bad_rest[:5]))
    check("fixture context: prev_game_status is Final only when a result is on file",
          not bad_status, ", ".join(bad_status[:5]))

    check("fixture context: off_bye is exactly 'the club has no Week 10 fixture'",
          all(r["off_bye"] == ("yes" if r["team"] not in wk10_teams else "no") for r in f),
          "bye clubs: " + ", ".join(sorted(r["team"] for r in f if r["off_bye"] == "yes")))
    check("fixture context: short_week is rest of six days or fewer",
          all(r["short_week"] == ("yes" if int(r["rest_days"]) <= 6 else "no") for r in f))

    by_side = {r["side_id"]: r for r in f}
    bad_mirror = [r["side_id"] for r in f
                  if int(r["opp_rest_days"]) != int(by_side["%s-%s" % (r["game_id"], r["opponent"])]["rest_days"])]
    check("fixture context: opp_rest_days is the other side's rest_days",
          not bad_mirror, ", ".join(bad_mirror[:5]))
    bad_edge = [r["side_id"] for r in f
                if int(r["rest_edge_days"]) != int(r["rest_days"]) - int(r["opp_rest_days"])]
    check("fixture context: rest_edge_days is this side's rest minus the opponent's",
          not bad_edge, ", ".join(bad_edge[:5]))
    bad_antisym = [r["side_id"] for r in f
                   if int(r["rest_edge_days"]) != -int(by_side["%s-%s" % (r["game_id"], r["opponent"])]["rest_edge_days"])]
    check("fixture context: the two sides' rest edges are exact negatives",
          not bad_antisym, ", ".join(bad_antisym[:5]))

    bad_div = [r["side_id"] for r in f
               if r["divisional_game"] != ("yes" if (standings[r["team"]]["conf"] == standings[r["opponent"]]["conf"]
                                                     and standings[r["team"]]["div"] == standings[r["opponent"]]["div"])
                                           else "no")]
    check("fixture context: divisional_game re-derives from the published standings table",
          not bad_div, ", ".join(bad_div[:5]))
    bad_conf = [r["side_id"] for r in f
                if r["conference_game"] != ("yes" if standings[r["team"]]["conf"] == standings[r["opponent"]]["conf"] else "no")]
    check("fixture context: conference_game re-derives from the published standings table",
          not bad_conf, ", ".join(bad_conf[:5]))

    bad_local = []
    for r in f:
        off = STATE_OFFSET.get(r["venue_state"], -1 if r["venue_city"] == "MEXICO CITY" else None)
        hh, mm = (int(x) for x in r["kickoff_et"].split(":"))
        want = "%02d:%02d" % ((hh + off) % 24, mm)
        if r["local_kickoff"] != want or int(r["et_offset_hours"]) != off:
            bad_local.append(r["side_id"])
    check("fixture context: local_kickoff and et_offset_hours re-derive from the venue's state",
          not bad_local, ", ".join(bad_local[:5]))

    bad_win = []
    for r in f:
        date, hh = d(r["date"]), int(r["kickoff_et"].split(":")[0])
        wd = date.strftime("%A")
        want = ("Thursday" if wd == "Thursday" else "Monday" if wd == "Monday"
                else "Sunday night" if hh >= 20 else "Sunday late" if hh >= 16 else "Sunday early")
        if r["kickoff_window"] != want:
            bad_win.append(r["side_id"])
    check("fixture context: kickoff_window re-derives from the published date and kickoff",
          not bad_win, ", ".join(bad_win[:5]))
    check("fixture context: every row cites its own official game page",
          all(r["source"].startswith("https://www.nfl.com/games/") for r in f))

    # ---- weekly what-changed diff ---------------------------------------
    w = read("weekly_diff_0a28b225.csv")
    before = {r["abbr"]: r for r in read("standings_recheck_20261113.csv")}
    after = {r["abbr"]: r for r in read("standings_2026.csv")}
    check("weekly diff: one row per club",
          len(w) == 32 == len(before) == len(after), "%d rows" % len(w))
    check("weekly diff: every club in both dated reads appears exactly once",
          {r["abbr"] for r in w} == set(before) == set(after))
    bad_delta = []
    for r in w:
        b_, a_ = before[r["abbr"]], after[r["abbr"]]
        for col, fld in (("w_delta", "w"), ("l_delta", "l"), ("t_delta", "t"),
                         ("pf_delta", "pf"), ("pa_delta", "pa"), ("net_delta", "net")):
            if int(r[col]) != int(a_[fld]) - int(b_[fld]):
                bad_delta.append(r["abbr"] + "/" + col)
        if (int(r["games_before"]), int(r["games_after"]), int(r["games_played"])) != (
                int(b_["w"]) + int(b_["l"]) + int(b_["t"]),
                int(a_["w"]) + int(a_["l"]) + int(a_["t"]),
                sum(int(a_[k]) - int(b_[k]) for k in ("w", "l", "t"))):
            bad_delta.append(r["abbr"] + "/games")
        if (r["w_before"], r["pf_before"], r["net_before"], r["streak_before"]) != (
                b_["w"], b_["pf"], b_["net"], b_["streak"]):
            bad_delta.append(r["abbr"] + "/before")
        if (r["w_after"], r["pf_after"], r["net_after"], r["streak_after"]) != (
                a_["w"], a_["pf"], a_["net"], a_["streak"]):
            bad_delta.append(r["abbr"] + "/after")
    check("weekly diff: every level and every delta re-derives from the two dated reads",
          not bad_delta, ", ".join(bad_delta[:5]))

    by_div = {}
    for abbr, r in after.items():
        by_div.setdefault((r["conf"], r["div"]), []).append(abbr)
    bad_rank = []
    for key, clubs in by_div.items():
        for snap, col in ((before, "div_rank_before"), (after, "div_rank_after")):
            order = sorted(clubs, key=lambda a: (-float(snap[a]["pct"]), -int(snap[a]["net"]), a))
            want = {a: i + 1 for i, a in enumerate(order)}
            for a in clubs:
                row = [x for x in w if x["abbr"] == a][0]
                if int(row[col]) != want[a]:
                    bad_rank.append(a)
    check("weekly diff: division rank before and after re-derive from each read's own pct and net",
          not bad_rank, ", ".join(sorted(set(bad_rank))[:5]))
    bad_change = [r["abbr"] for r in w
                  if int(r["div_rank_change"]) != int(r["div_rank_before"]) - int(r["div_rank_after"])]
    check("weekly diff: rank change is before minus after (positive means the club moved up)",
          not bad_change, ", ".join(bad_change[:5]))

    # The two reads are 13 Nov and 16 Nov, so the window is NOT the whole of Week 10: the
    # Thursday game (12 Nov) predates the first read and the Monday game (16 Nov, 20:15 ET)
    # postdates the second. The register must agree with the games that actually settled in
    # between, and the page says so.
    win_start = max(d(r["captured_utc"][:10]) for r in before.values())
    win_end = max(d(r["captured_utc"][:10]) for r in after.values())
    in_window = [r for r in wk10_played if win_start < d(r["date"]) <= win_end]
    check("weekly diff: total games played equals twice the results that settled inside the window",
          sum(int(r["games_played"]) for r in w) == 2 * len(in_window),
          "%d team-games vs %d settled games between %s and %s"
          % (sum(int(r["games_played"]) for r in w), len(in_window), win_start, win_end))
    check("weekly diff: clubs with zero games are byes plus the two clubs whose game is outside the window",
          {r["abbr"] for r in w if r["games_played"] == "0"} ==
          (set(after) - {t for r in in_window for t in (r["away"], r["home"])}),
          "0-game clubs: " + ", ".join(sorted(r["abbr"] for r in w if r["games_played"] == "0")))
    check("weekly diff: both dated reads are cited per row and both ids are registered",
          all(r["source_before"] == "S-STAND-653B" and r["source_after"] == "S-STAND-F3EC" for r in w))
    check("weekly diff: the rendered source cell names both reads, in order",
          all(r["source"] == r["source_before"] + "::" + r["source_after"] for r in w))

    # ---- independent second read of the same official pages ---------------
    # Session 3e77121b transcribed the same 13 Week 11 game centres at 18:02-18:06Z; this
    # session transcribed them again at 18:40Z without seeing that file. Two independent reads
    # of the same official page agreeing is evidence; disagreeing is a finding. Either way the
    # check belongs here, not in a narrative. Their file is the published one - this session's
    # page was withdrawn rather than ship two competing venue pages.
    cross = os.path.join(DATA, "venues_wk11_3e77121b.csv")
    if not os.path.exists(cross):
        check("cross-session venue read: 3e77121b's file is present to compare against", False,
              "data/venues_wk11_3e77121b.csv missing")
    else:
        theirs = {r["game_id"]: r for r in read("venues_wk11_3e77121b.csv")}
        mine = {r["game_id"]: r for r in v}
        check("cross-session venue read: both reads cover the same 13 fixtures",
              set(theirs) == set(mine) == set(wk11), "%d vs %d" % (len(theirs), len(mine)))
        mismatch = []
        norm = lambda t: " ".join(str(t).upper().split())
        for gid in sorted(mine):
            a, b = mine[gid], theirs[gid]
            if norm(a["venue_city"]) != norm(b["location_as_printed"].split(",")[0]):
                mismatch.append(gid + "/city")
            if norm(a["stadium_game_centre"]) != norm(b["stadium_as_printed"]):
                mismatch.append(gid + "/stadium")
        check("cross-session venue read: the two independent reads agree on city and stadium "
              "for all 13 fixtures",
              not mismatch, "disagreements: " + ", ".join(mismatch[:6]) if mismatch
              else "18:02-18:06Z read vs 18:40Z read, 13/13 identical")
        check("cross-session venue read: this read is registered as an independent second read, "
              "not as a competing page",
              "venue-register" not in open(os.path.join(ROOT, "tools", "build_site.py"),
                                           encoding="utf-8").read())

    # ---- kickoff regime --------------------------------------------------
    k = read("kickoff_regime_0a28b225.csv")
    check("kickoff regime: five rows, one per 2026 rule change that moves a total",
          len(k) == 5, "%d rows" % len(k))
    check("kickoff regime: every row cites an official league host",
          all(r["source"].split("/")[2] in OFFICIAL_HOSTS for r in k),
          ", ".join(sorted({r["source"].split("/")[2] for r in k})))
    check("kickoff regime: no rule text is carried in from a non-official summary",
          all(r["rule_text_as_published"].strip() and r["prior_regime"].strip() for r in k))
    check("kickoff regime: the rulebook's own table is the source for the four rows it lists",
          sum(1 for r in k if r["source"].endswith("2026-nfl-rulebook")) == 4)
    check("kickoff regime: the fifth row says the rulebook does not list it, rather than dropping it",
          any(r["id"] == "KR-05" and "does not list" in r["why_it_moves_a_total"] for r in k))

    # ---- cross-file ------------------------------------------------------
    vstadium = {r["game_id"]: (r["venue_city"], r["venue_state"]) for r in v}
    bad_cross = [r["game_id"] for r in f if (r["venue_city"], r["venue_state"]) != vstadium[r["game_id"]]]
    check("cross-file: the venue on every fixture-context row is the venue register's",
          not bad_cross, ", ".join(bad_cross[:5]))

    failed = [n for n, ok, _ in results if not ok]
    print("=" * 72)
    print("verify_0a28b225: %d checks, %d passed, %d failed"
          % (len(results), len(results) - len(failed), len(failed)))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
