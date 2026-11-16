#!/usr/bin/env python3
"""Session e632af20: re-derive every arithmetic claim in data/reverification_e632af20.csv.

Read-only. Run: python3 tools/verify_e632af20.py

What it proves, from the checked-in files alone (no network):
  1. The 16 Nov hub snapshot is schema-clean and matches the 15 Nov reads cell for cell
     (the delta the register publishes must be exactly zero).
  2. Every Week 10 score in the register is the score in the official fixture map's game page
     and matches what the two official pages showed on 2026-11-16 (embedded below as the
     fetched-evidence table, one line per game, so a register typo cannot hide).
  3. The 16 Nov standings transcription equals the 13 Nov snapshot plus exactly the twelve
     Sunday results, club by club on W-L-T-PF-PA, and the league-wide zero-sum identities hold.
  4. Every Week 11 fixture row in the register matches data/schedule_week11_2026.csv on
     date, kickoff, clubs and broadcaster.
  5. The register cites only nfl.com sources and every row is populated.

Exit 0 and print a pass/fail tally; any failure exits 1.
"""
import csv
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

# Fetched 2026-11-16 from the official Week 10 scores page AND the Week 10 schedule page
# (both pages agreed line for line). Keyed by game id from data/schedule_2026_wk10.csv.
# None means the league published no final score at read time.
WK10_OFFICIAL = {
    "W10-01": ("WAS", "NYG", 24, 21),
    "W10-02": ("NE", "DET", 10, 35),
    "W10-03": ("KC", "ATL", 35, 13),
    "W10-04": ("MIN", "GB", 30, 10),
    "W10-05": ("JAX", "TEN", 40, 23),
    "W10-06": ("MIA", "IND", 22, 24),
    "W10-07": ("CAR", "NO", 20, 17),
    "W10-08": ("BUF", "NYJ", 31, 12),
    "W10-09": ("HOU", "CLE", 24, 27),
    "W10-10": ("LAR", "AZ", 34, 6),
    "W10-11": ("SEA", "LV", 21, 13),
    "W10-12": ("SF", "DAL", 46, 40),
    "W10-13": ("PIT", "CIN", 18, 38),
    "W10-14": None,  # LAC at BAL: kickoff 2026-11-16 20:15 ET, not final at read time
}

PASS, FAIL = [], []


def ok(msg):
    PASS.append(msg)


def bad(msg):
    FAIL.append(msg)


def rd(name):
    path = os.path.join(DATA, name)
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="|"))


def check_hub():
    new = rd("hub_read_e632af20_20261116.csv")
    old = rd("hub_read_8dee7df7.csv")
    alt = rd("injuries_wk10_5de1805b_20261115.csv")
    if len(new) != 347:
        bad("hub snapshot holds %d rows, expected 347" % len(new))
    else:
        ok("hub snapshot: 347 rows")
    pracs, stats = {"F", "L", "D", ""}, {"", "Out", "Questionable", "Doubtful"}
    for i, r in enumerate(new, 2):
        if r["practice"] not in pracs or r["game_status"] not in stats:
            bad("hub snapshot line %d: vocabulary drift (%r, %r)" % (i, r["practice"], r["game_status"]))
        if not r["source_url"].startswith("https://www.nfl.com/"):
            bad("hub snapshot line %d: no nfl.com source" % i)
        if r["read_utc"] != "2026-11-16T14:40Z":
            bad("hub snapshot line %d: read clock %s" % (i, r["read_utc"]))
    keyn = {(r["club"], r["player"]): r for r in new}
    keyo = {(r["club"], r["player"]): r for r in old}
    changed = [(k, f) for k in set(keyn) & set(keyo)
               for f in ("pos", "injury", "practice", "game_status") if keyn[k][f] != keyo[k][f]]
    if set(keyn) != set(keyo):
        bad("hub delta: population changed between 15 and 16 Nov (%d added, %d removed)"
            % (len(set(keyn) - set(keyo)), len(set(keyo) - set(keyn))))
    elif changed:
        bad("hub delta: %d cell(s) changed, register claims zero: %s" % (len(changed), changed[:5]))
    else:
        ok("hub delta vs 15 Nov 12:51Z: zero additions, zero removals, zero cell changes")
    norm = {"OUT": "Out", "Q": "Questionable", "D": "Doubtful", "": ""}
    keya = {(r["team"], r["player"]): r for r in alt}
    mism = [k for k in set(keyn) & set(keya)
            if (keya[k]["pos"], keya[k]["injury"], keya[k]["practice"], norm[keya[k]["status"]])
            != (keyn[k]["pos"], keyn[k]["injury"], keyn[k]["practice"], keyn[k]["game_status"])]
    if set(keyn) != set(keya) or mism:
        bad("hub snapshot disagrees with the independent 5de1805b read: %d row(s)" % len(mism))
    else:
        ok("hub snapshot agrees cell for cell with the independent 15 Nov 12:55Z read")


def check_week10():
    sched = {r["game_id"]: r for r in rd("schedule_2026_wk10.csv")}
    played = {r["game_id"]: r for r in rd("games_2026_wk10_played.csv")}
    if set(sched) != set(WK10_OFFICIAL):
        bad("official evidence table and schedule_2026_wk10.csv disagree on game ids")
    for gid, ev in WK10_OFFICIAL.items():
        s = sched.get(gid)
        if not s:
            continue
        if ev is None:
            if gid in played:
                bad("%s is in the results file but the league published no final at read time" % gid)
            continue
        away, home, ap, hp = ev
        if (s["away"], s["home"]) != (away, home):
            bad("%s: fixture map says %s@%s, evidence says %s@%s" % (gid, s["home"], s["away"], home, away))
        p = played.get(gid)
        if p:
            if (int(p["away_pts"]), int(p["home_pts"])) != (ap, hp) or p["status"] != "Final":
                bad("%s: stored result %s-%s does not match the official %d-%d"
                    % (gid, p["away_pts"], p["home_pts"], ap, hp))
            elif (p["away"], p["home"]) != (away, home):
                bad("%s: stored fixture mismatch" % gid)
    n_played = sum(1 for g, ev in WK10_OFFICIAL.items() if ev and g in played)
    if len(played) != 1 or n_played != 1:
        bad("results feed holds %d rows; the register says one settled game is ingested" % len(played))
    else:
        ok("results feed: 1 of 13 finals ingested, and its score matches the official pages")
    finals = sum(1 for ev in WK10_OFFICIAL.values() if ev)
    if finals != 13:
        bad("evidence table holds %d finals, expected 13" % finals)
    else:
        ok("official evidence table: 13 finals and one pending kickoff, matching the two page reads")


def check_standings():
    old = {r["abbr"]: r for r in rd("standings_2026.csv")}
    new = {r["abbr"]: r for r in rd("standings_recheck_e632af20_20261116.csv")}
    if set(old) != set(new) or len(new) != 32:
        bad("standings re-check does not cover the same 32 clubs")
        return
    # the twelve Sunday results applied to the 13 Nov snapshot, from the evidence table
    sunday = [(gid, ev) for gid, ev in WK10_OFFICIAL.items() if ev and gid != "W10-01"]
    problems = []
    for abbr in sorted(new):
        o, n = old[abbr], new[abbr]
        dw = dl = dt = dpf = dpa = 0
        for gid, (away, home, ap, hp) in sunday:
            if abbr == away:
                dpf += ap; dpa += hp
                if ap > hp: dw += 1
                elif ap < hp: dl += 1
                else: dt += 1
            elif abbr == home:
                dpf += hp; dpa += ap
                if hp > ap: dw += 1
                elif hp < ap: dl += 1
                else: dt += 1
        want = (int(o["w"]) + dw, int(o["l"]) + dl, int(o["t"]) + dt,
                int(o["pf"]) + dpf, int(o["pa"]) + dpa)
        got = (int(n["w"]), int(n["l"]), int(n["t"]), int(n["pf"]), int(n["pa"]))
        if want != got:
            problems.append("%s: stored+results %s vs read %s" % (abbr, want, got))
        if int(n["pf"]) - int(n["pa"]) != int(n["net"]):
            problems.append("%s: net %s != pf-pa" % (abbr, n["net"]))
    if problems:
        bad("standings delta does not close for %d club(s): %s" % (len(problems), problems[:5]))
    else:
        ok("standings delta closes for all 32 clubs: 13 Nov snapshot plus the twelve Sunday results "
           "= the 16 Nov official read, on W-L-T-PF-PA")
    sw = sum(int(r["w"]) for r in new.values())
    sl = sum(int(r["l"]) for r in new.values())
    st = sum(int(r["t"]) for r in new.values())
    spf = sum(int(r["pf"]) for r in new.values())
    spa = sum(int(r["pa"]) for r in new.values())
    if sw != sl or spf != spa or st != 2:
        bad("zero-sum identities broken on the 16 Nov read: W=%d L=%d T=%d PF=%d PA=%d"
            % (sw, sl, st, spf, spa))
    else:
        ok("zero-sum identities hold on the 16 Nov read: SUM W = SUM L = %d, SUM T = %d, "
           "SUM PF = SUM PA = %d" % (sw, st, spf))
    return sw, st, spf


def check_week11():
    reg = {r["id"]: r for r in rd("reverification_e632af20.csv")}
    sched = rd("schedule_week11_2026.csv")
    problems = []
    for i, s in enumerate(sched, 1):
        rid = "RV632-%d" % (23 + i)
        r = reg.get(rid)
        if not r:
            problems.append("%s missing for %s" % (rid, s["game_id"]))
            continue
        text = r["check"] + " " + r["official_value"]
        if s["away"] not in text or s["home"] not in text:
            problems.append("%s does not name %s@%s" % (rid, s["away"], s["home"]))
        if s["date"] not in r["official_value"] and s["date"][5:] not in r["official_value"]:
            date_ok = any(m in r["official_value"] for m in _date_words(s["date"]))
            if not date_ok:
                problems.append("%s does not carry the fixture date %s" % (rid, s["date"]))
        hh, mm = s["kickoff_et"].split(":")
        hour12 = ((int(hh) + 11) % 12) + 1
        if "%d:%s" % (hour12, mm) not in r["official_value"]:
            problems.append("%s does not carry kickoff %s ET" % (rid, s["kickoff_et"]))
        tv0 = s["tv"].split(",")[0].strip()
        if not any(tok.lower() in r["official_value"].lower() for tok in (tv0, tv0.split()[0])):
            problems.append("%s does not carry broadcaster %s" % (rid, tv0))
    if problems:
        bad("Week 11 rows disagree with data/schedule_week11_2026.csv: %s" % problems[:5])
    else:
        ok("all 13 Week 11 register rows match data/schedule_week11_2026.csv on clubs, date, "
           "kickoff and broadcaster")


def _date_words(iso):
    months = ["January", "February", "March", "April", "May", "June", "July",
              "August", "September", "October", "November", "December"]
    y, m, d = iso.split("-")
    month, day = months[int(m) - 1], int(d)
    return ["%s %d" % (month, day), "%d %s" % (day, month),
            "%s %02d" % (month, day), "%02d %s" % (day, month)]


def check_register():
    reg = rd("reverification_e632af20.csv")
    ids = [r["id"] for r in reg]
    if len(ids) != len(set(ids)):
        bad("register has duplicate ids")
    for r in reg:
        if not r["source"].startswith("https://www.nfl.com"):
            bad("%s: source is not an nfl.com page" % r["id"])
        for k, v in r.items():
            if "|" in v:
                bad("%s.%s: unescaped pipe in cell" % (r["id"], k))
        if r["result"] not in ("MATCH", "NOT INGESTED", "PENDING", "FLAGGED", "DELTA"):
            bad("%s: unknown verdict %r" % (r["id"], r["result"]))
    flagged = [r for r in reg if r["result"] == "FLAGGED"]
    for r in flagged:
        if "FL-" not in r["note"]:
            bad("%s: flagged row cites no flag id" % r["id"])
    ok("register: %d rows, unique ids, nfl.com sources on every row, %d flagged rows each "
       "citing a flag id" % (len(reg), len(flagged)))
    return reg


def check_register_vs_evidence(reg):
    """The register's Week 10 result rows must state the same scores as the evidence table."""
    byid = {r["id"]: r for r in reg}
    problems = []
    for i, (gid, ev) in enumerate(sorted(WK10_OFFICIAL.items()), 1):
        rid = "RV632-%02d" % (6 + i)  # RV632-07..RV632-20
        r = byid.get(rid)
        if not r:
            problems.append("%s missing for %s" % (rid, gid))
            continue
        if ev is None:
            if r["result"] != "PENDING":
                problems.append("%s should be PENDING" % rid)
            continue
        away, home, ap, hp = ev
        want = "%s %d - %s %d" % (away, ap, home, hp)
        if want not in r["official_value"]:
            problems.append("%s does not state %r" % (rid, want))
        expect = "MATCH" if gid in {g for g, e in WK10_OFFICIAL.items() if e and g in
                                    {x["game_id"] for x in rd("games_2026_wk10_played.csv")}} \
            else "NOT INGESTED"
        if r["result"] != expect:
            problems.append("%s verdict %r, expected %r" % (rid, r["result"], expect))
    if problems:
        bad("register disagrees with the fetched-evidence table: %s" % problems[:5])
    else:
        ok("register Week 10 rows state exactly the fetched-evidence scores and verdicts")


def main():
    check_hub()
    check_week10()
    sw, st, spf = check_standings()
    reg = check_register()
    check_register_vs_evidence(reg)
    check_week11()
    print()
    for m in PASS:
        print("  PASS  %s" % m)
    for m in FAIL:
        print("  FAIL  %s" % m)
    print("\nverify_e632af20: %d passed · %d failed" % (len(PASS), len(FAIL)))
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
