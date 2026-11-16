"""Re-derive the 3e77121b tables from the checked-in inputs. Exit 1 on any failure.

Checks the Week 11 venue file against the schedule file and the official game-centre URLs,
and the per-team view against the 16 Nov injury-hub read, the reserve list and the named-starter
articles. Every number is recomputed here; nothing is copied from the generated file.
"""
import csv
import os
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import team_view_3e77121b as tv  # noqa: E402

FAILS = []
PASSES = [0]


def check(cond, msg):
    if cond:
        PASSES[0] += 1
    else:
        FAILS.append(msg)


def read(p):
    with open(os.path.join(ROOT, p), encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="|"))


def verify_venues():
    v = read("data/venues_wk11_3e77121b.csv")
    s = {r["game_id"]: r for r in read("data/schedule_week11_2026.csv")}
    check(len(v) == 13, "venue file has %d rows, expected 13" % len(v))
    check(len({r["game_id"] for r in v}) == len(v), "venue game_id not unique")
    check(set(r["game_id"] for r in v) == set(s), "venue ids differ from schedule ids")
    for r in v:
        x = s.get(r["game_id"])
        if x is None:
            continue
        for a, b, what in [(r["date"], x["date"], "date"), (r["kickoff_et"], x["kickoff_et"], "kickoff"),
                           (r["away"], x["away"], "away"), (r["home"], x["home"], "home"),
                           (r["network_as_printed"], x["tv"], "network")]:
            check(a == b, "%s %s: venue file %r != schedule %r" % (r["game_id"], what, a, b))
        check(r["source"] == "https://www.nfl.com/games/" + x["game_url"],
              "%s: source is not the official game-centre URL of the schedule row" % r["game_id"])
        check(r["location_as_printed"].strip() != "" and r["stadium_as_printed"].strip() != "",
              "%s: blank location or stadium" % r["game_id"])
        check(r["read_window_utc"].startswith("2026-11-16T18:0"), "%s: read window outside the 16 Nov session" % r["game_id"])
    return v


def verify_team_view():
    rows = read("data/team_view_3e77121b.csv")
    check(len(rows) == 32, "team view has %d rows, expected 32" % len(rows))
    check(len({r["club"] for r in rows}) == len(rows), "team view club codes not unique")
    hub = read("data/hub_read_e632af20_20261116.csv")
    by = {}
    for r in hub:
        by.setdefault(r["club"], []).append(r)
    on_hub = set(by)
    byes = {r["club"] for r in rows if r["club"] in tv.OFFICIAL_WEEK10_BYES}
    check(byes == tv.OFFICIAL_WEEK10_BYES, "bye clubs in the view are not the four official Week 10 byes")
    check(not (on_hub & tv.OFFICIAL_WEEK10_BYES), "a Week 10 bye club has hub rows")
    check(set(r["club"] for r in rows) - on_hub == tv.OFFICIAL_WEEK10_BYES,
          "clubs with no hub block are not exactly the four official byes")
    tot = Counter()
    for r in rows:
        c = r["club"]
        if c in tv.OFFICIAL_WEEK10_BYES:
            check(all(r[k] == "" for k in ["hub_rows", "out", "doubtful", "questionable", "designated_total",
                                            "did_not_practice", "limited", "full"]),
                  "%s is a bye but has counts (must be blank, never 0)" % c)
            continue
        hr = by[c]
        dist = Counter(x["game_status"] for x in hr)
        prac = Counter(x["practice"] for x in hr)
        exp = {"hub_rows": len(hr), "out": dist["Out"], "doubtful": dist["Doubtful"],
               "questionable": dist["Questionable"], "did_not_practice": prac["D"],
               "limited": prac["L"], "full": prac["F"]}
        exp["designated_total"] = exp["out"] + exp["doubtful"] + exp["questionable"]
        for k, val in exp.items():
            check(r[k] == str(val), "%s %s: file %r, recomputed %r" % (c, k, r[k], val))
        check(int(r["designated_total"]) == int(r["out"]) + int(r["doubtful"]) + int(r["questionable"]),
              "%s designated_total is not out+doubtful+questionable" % c)
        check(r["did_not_practice"] and int(r["did_not_practice"]) + int(r["limited"]) + int(r["full"]) == int(r["hub_rows"]),
              "%s practice codes do not sum to rows" % c)
        for k in exp:
            tot[k] += exp[k]
    check(tot["hub_rows"] == len(hub), "rows across clubs %d != hub rows %d" % (tot["hub_rows"], len(hub)))
    check(tot["out"] == sum(1 for x in hub if x["game_status"] == "Out"), "Out total does not match hub")
    check(tot["designated_total"] == sum(1 for x in hub if x["game_status"] in ("Out", "Doubtful", "Questionable")),
          "designated total does not match hub")
    check(tot["designated_total"] == 171, "designated total %d != 171 (the count the injury page publishes)" % tot["designated_total"])
    check(tot["out"] == 70, "Out total %d != 70" % tot["out"])
    for r in rows:
        check(r["source"].startswith("https://www.nfl.com/"), "%s: source is not nfl.com" % r["club"])
    named = {r["club"] for r in rows if r["starter_change_named_by_league_week10"]}
    check(named == {"SEA", "MIA", "CLE", "AZ"}, "named-starter rows are %s, expected SEA, MIA, CLE, AZ" % sorted(named))
    for r in rows:
        if r["starter_change_named_by_league_week10"]:
            check("https://www.nfl.com/" in r["starter_change_named_by_league_week10"],
                  "%s named-starter cell has no NFL.com link" % r["club"])
    res = read("data/reserve_list_capture_f3ec0ff8.csv")
    n_names = sum(r["reserve_list_november"].count(" (") for r in rows if not r["reserve_list_november"].startswith("none"))
    check(n_names == len(res), "reserve names in view (%d) != reserve capture rows (%d)" % (n_names, len(res)))
    return rows


def main():
    verify_venues()
    verify_team_view()
    print("verify_3e77121b: %d passed · %d failed" % (PASSES[0], len(FAILS)))
    for f in FAILS:
        print("  FAIL:", f)
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
