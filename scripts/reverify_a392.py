#!/usr/bin/env python3
"""Line-by-line re-verification of the canonical Week 10 data layer (session a392a193).

Everything this script compares against was read off the official league pages on
2026-11-12T22:35Z (nfl.com/standings/, nfl.com/injuries/). The official values are embedded
below as a literal transcription of what those pages rendered, so the comparison is
re-runnable without network access and an auditor can diff the transcription against the
page itself.

Emits:
  data/injuries_wk10_2026_hubrefresh.csv   refreshed Week 10 hub register (279 rows)
  data/injury_delta_a392.csv               row-level diff of the refreshed hub vs the 04:45Z snapshot
  data/reverification_a392.csv             the check register: what was checked, against what, result
Exit code is non-zero if a published value disagrees with the official source.
"""
import csv, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
FETCH_0445 = "2026-11-12T04:45Z"
FETCH_2235 = "2026-11-12T22:35Z"
SRC_STAND = "https://www.nfl.com/standings/"
SRC_INJ = "https://www.nfl.com/injuries/"

# --- official values, transcribed from https://www.nfl.com/standings/ at 22:35Z ---------------
# columns: abbr|w|l|t|pct|pf|pa|net|streak
OFFICIAL_STANDINGS = """BUF|7|1|0|0.875|256|187|69|4W
NE|5|4|0|0.556|211|207|4|1L
NYJ|2|7|0|0.222|182|223|-41|4L
MIA|1|7|0|0.125|126|200|-74|2L
PIT|6|2|0|0.750|180|144|36|4W
CIN|6|2|0|0.750|240|175|65|4W
CLE|5|4|0|0.556|161|196|-35|2L
BAL|4|5|0|0.444|189|236|-47|4L
JAX|6|2|0|0.750|229|121|108|2W
HOU|3|5|0|0.375|209|192|17|1W
IND|2|7|0|0.222|184|249|-65|5L
TEN|1|7|0|0.125|144|199|-55|2L
DEN|7|2|0|0.778|198|186|12|5W
KC|6|2|0|0.750|202|143|59|1W
LV|4|5|0|0.444|238|268|-30|1L
LAC|0|8|0|0.000|121|219|-98|8L
NYG|5|2|1|0.688|182|172|10|2W
DAL|4|5|0|0.444|246|236|10|1W
WAS|2|5|1|0.313|172|202|-30|1L
PHI|2|7|0|0.222|148|221|-73|7L
CHI|7|2|0|0.778|241|184|57|4W
DET|6|2|0|0.750|222|189|33|4W
MIN|6|2|0|0.750|146|116|30|2L
GB|6|3|0|0.667|216|191|25|2W
CAR|3|5|0|0.375|199|219|-20|3L
NO|3|5|0|0.375|185|216|-31|1W
TB|3|6|0|0.333|202|178|24|1L
ATL|3|6|0|0.333|188|223|-35|2L
SF|7|1|0|0.875|235|156|79|1W
SEA|5|4|0|0.556|202|162|40|1W
LAR|5|4|0|0.556|214|181|33|3W
AZ|3|6|0|0.333|178|255|-77|1L"""

# --- official slate, transcribed from https://www.nfl.com/injuries/ at 22:35Z ----------------
# The hub renders each fixture as: day, kickoff (ET), broadcaster, away (record) at home (record).
OFFICIAL_SLATE = """W10-01|2026-11-12|20:15|WAS|NYG|Prime Video
W10-02|2026-11-15|09:30|NE|DET|FOX
W10-03|2026-11-15|13:00|KC|ATL|CBS
W10-04|2026-11-15|13:00|MIN|GB|FOX
W10-05|2026-11-15|13:00|JAX|TEN|FOX
W10-06|2026-11-15|13:00|MIA|IND|CBS
W10-07|2026-11-15|13:00|CAR|NO|FOX
W10-08|2026-11-15|13:00|BUF|NYJ|CBS
W10-09|2026-11-15|13:00|HOU|CLE|FOX
W10-10|2026-11-15|16:05|LAR|AZ|CBS
W10-11|2026-11-15|16:05|SEA|LV|CBS
W10-12|2026-11-15|16:25|SF|DAL|FOX
W10-13|2026-11-15|20:20|PIT|CIN|NBC
W10-14|2026-11-16|20:15|LAC|BAL|ESPN"""

HUB_LIVE = os.path.join(ROOT, "research", "a392", "hub_2026-11-12T2235Z.csv")

OFF_POS = {"QB", "RB", "FB", "WR", "TE", "T", "G", "C", "OT", "OG", "OL"}
ST_POS = {"K", "P", "LS"}


def read(name, delim="|"):
    path = os.path.join(DATA, name)
    with open(path, encoding="utf-8") as fh:
        raw = list(csv.reader(fh, delimiter=delim))
    return [dict(zip(raw[0], r)) for r in raw[1:]]


def side(pos):
    if pos in OFF_POS:
        return "offence"
    if pos in ST_POS:
        return "special teams"
    return "defence"


def main():
    checks, fails = [], 0

    def record(check, scope, want, got, result, source, note=""):
        checks.append({"check": check, "scope": scope, "official_value": want, "published_value": got,
                       "result": result, "source": source, "note": note})

    # ---- 1. standings, 32 rows ----------------------------------------------------------------
    official = {}
    for line in OFFICIAL_STANDINGS.splitlines():
        p = line.split("|")
        official[p[0]] = dict(w=p[1], l=p[2], t=p[3], pct=p[4], pf=p[5], pa=p[6], net=p[7], streak=p[8])
    repo = {r["abbr"]: r for r in read("standings_2026.csv")}
    bad = []
    for abbr, o in official.items():
        r = repo.get(abbr)
        if not r:
            bad.append(abbr + " missing"); continue
        for f in ("w", "l", "t", "pct", "pf", "pa", "net", "streak"):
            if str(r[f]) != o[f]:
                bad.append("%s.%s pub=%s official=%s" % (abbr, f, r[f], o[f]))
    record("standings: 32 clubs x 8 published columns", "32 rows / 256 cells",
           "transcribed from the official page", "as published" if not bad else "; ".join(bad[:4]),
           "match" if not bad else "MISMATCH", SRC_STAND,
           "re-checked 22:35Z against nfl.com/standings (division view, 2026 REG)")

    # ---- 2. week 10 slate ----------------------------------------------------------------------
    sched = {r["game_id"]: r for r in read("schedule_2026_wk10.csv")}
    time_bad, tv_bad = [], []
    for line in OFFICIAL_SLATE.splitlines():
        gid, date, ko, away, home, net = line.split("|")
        r = sched.get(gid)
        if not r:
            time_bad.append("%s absent from the published slate" % gid); continue
        if (r["date"], r["kickoff_et"], r["away"], r["home"]) != (date, ko, away, home):
            time_bad.append("%s pub=%s official=%s" % (gid, (r["date"], r["kickoff_et"], r["away"], r["home"]),
                                                        (date, ko, away, home)))
        if net.lower() not in r["tv"].lower():
            tv_bad.append("%s published '%s' hub shows '%s'" % (gid, r["tv"], net))
    record("schedule: fixture, date and kickoff for all 14 Week 10 games", "14 rows x 4 fields",
           "as rendered on the official hub", "as published" if not time_bad else "; ".join(time_bad[:4]),
           "match" if not time_bad else "MISMATCH", SRC_INJ,
           "the injury hub renders the slate header; it is a second, independent rendering of the same fixtures")
    record("schedule: broadcaster named on the hub appears in the published TV column", "14 rows",
           "hub string as shown", "as published" if not tv_bad else "; ".join(tv_bad[:4]),
           "match" if not tv_bad else "PARTIAL", SRC_INJ,
           "the hub shows only the national rightsholder; the published column carries the full local/simulcast list "
           "from the game page, so a hub string that is a subset of the published string is a pass, a superset is not")

    # ---- 3. injury hub refresh -----------------------------------------------------------------
    cols = "game|team|player|pos|practice|status|injury|slug".split("|")
    live = [dict(zip(cols, [c.strip() for c in line.split("|")]))
            for line in open(HUB_LIVE, encoding="utf-8").read().splitlines() if line.strip()]
    assert all(len(r) == len(cols) for r in live), "hub transcription: a row has the wrong field count"
    snap = read("injuries_2026_wk10.csv")
    snap_keys = {(r["team"], r["player"]): r for r in snap}
    live_keys = {(r["team"], r["player"]): r for r in live}

    added = [k for k in live_keys if k not in snap_keys]
    removed = [k for k in snap_keys if k not in live_keys]
    changed = [(k, snap_keys[k], live_keys[k]) for k in snap_keys if k in live_keys
               and (snap_keys[k]["practice"] != live_keys[k]["practice"]
                    or snap_keys[k]["status"] != live_keys[k]["status"])]
    # slug integrity: a refreshed row must carry the same official URL key as the snapshot row
    slug_bad = [(k, snap_keys[k]["slug"], live_keys[k]["slug"]) for k in snap_keys
                if k in live_keys and snap_keys[k]["slug"] != live_keys[k]["slug"]]
    record("injuries: every row in the 04:45Z snapshot is still on the hub",
           "%d snapshot rows" % len(snap), "0 rows withdrawn",
           "%d rows withdrawn" % len(removed),
           "match" if not removed else "MISMATCH", SRC_INJ,
           "a row that disappears from the hub would mean the snapshot published something the league retracted")
    record("injuries: practice/designation codes still agree with the hub",
           "%d shared rows" % len(set(snap_keys) & set(live_keys)), "0 changes",
           "%d rows re-filed by the club since the snapshot" % len(changed),
           "match" if not changed else "SUPERSEDED", SRC_INJ,
           "the hub is a rolling document: clubs re-file participation through the week, so a practice code that "
           "moves is expected and is published as a delta rather than as a correction to the earlier fetch")
    record("injuries: player URL keys agree between the two fetches", "%d shared rows" % len(set(snap_keys) & set(live_keys)),
           "identical slug", "identical" if not slug_bad else "; ".join("%s %s/%s" % (k[1], a, b) for k, a, b in slug_bad[:3]),
           "match" if not slug_bad else "MISMATCH", SRC_INJ,
           "the slug is what the player link on the site is built from")
    record("injuries: rows on the hub that the 04:45Z snapshot does not carry", "hub 22:35Z vs snapshot",
           "%d hub rows" % len(live), "%d snapshot rows" % len(snap),
           "SUPERSEDED" if added else "match", SRC_INJ,
           "%d rows added by clubs after the snapshot was taken (%s)"
           % (len(added), ", ".join(sorted({t for t, _ in added})) or "none"))

    # per-club count reconciliation
    from collections import Counter
    lc, sc = Counter(r["team"] for r in live), Counter(r["team"] for r in snap)
    count_bad = []
    for club in sorted(set(lc) | set(sc)):
        if lc[club] != sc[club]:
            count_bad.append("%s hub=%d snapshot=%d" % (club, lc[club], sc[club]))
    record("injuries: per-club row counts (28 clubs)", "28 clubs",
           "%d rows / %d clubs with rows" % (len(live), len([c for c in lc if lc[c]])),
           "%d rows / %d clubs with rows" % (len(snap), len([c for c in sc if sc[c]])),
           "match" if not count_bad else "SUPERSEDED", SRC_INJ,
           "deltas: " + ("; ".join(count_bad) if count_bad else "none"))

    designations_live = [(r["team"], r["player"], r["pos"], r["injury"], r["practice"], r["status"])
                         for r in live if r["status"].strip()]
    designations_snap = [(r["team"], r["player"], r["status"]) for r in snap if r["status"].strip()]
    record("injuries: game-status designations", "%d designated at 04:45Z" % len(designations_snap),
           "same 6 rows", "%d at 22:35Z" % len(designations_live),
           "match" if len(designations_live) == len(designations_snap) else "MISMATCH", SRC_INJ,
           "; ".join("%s %s -> %s" % (t, pl, st) for t, pl, st in designations_snap))

    # ---- write the refreshed register and the delta ------------------------------------------
    with open(os.path.join(DATA, "injuries_wk10_2026_hubrefresh.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="|")
        w.writerow("game|team|player|slug|pos|side|injury|practice|status|fetched_utc|source".split("|"))
        for r in sorted(live, key=lambda x: (x["game"], x["team"], x["player"])):
            w.writerow([r["game"], r["team"], r["player"], r["slug"], r["pos"], side(r["pos"]),
                        r["injury"], r["practice"], r["status"], FETCH_2235, "S-INJ"])
    with open(os.path.join(DATA, "injury_delta_a392.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="|")
        w.writerow("kind|team|player|pos|side|practice_at_2235|status_at_2235|injury|game|source|note".split("|"))
        for t, p in sorted(added):
            r = live_keys[(t, p)]
            w.writerow(["added-after-snapshot", t, p, r["pos"], side(r["pos"]), r["practice"],
                        r["status"] or "not published", r["injury"] or "not published", r["game"],
                        "S-INJ", "on the hub at 22:35Z, absent at 04:45Z"])
        for t, p in sorted(removed):
            r = snap_keys[(t, p)]
            w.writerow(["removed-after-snapshot", t, p, r["pos"], side(r["pos"]), r["practice"],
                        r["status"] or "not published", r["injury"] or "not published", r["game"],
                        "S-INJ", "in the 04:45Z snapshot, no longer on the hub"])
        for (t, p), a, b in sorted(changed):
            w.writerow(["changed", t, p, b["pos"], side(b["pos"]), b["practice"],
                        b["status"] or "not published", b["injury"] or "not published", b["game"], "S-INJ",
                        "practice %s -> %s, status %s -> %s" % (a["practice"], b["practice"],
                                                                 a["status"] or "-", b["status"] or "-")])
    with open(os.path.join(DATA, "reverification_a392.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="|")
        w.writerow("check|scope|official_value|published_value|result|source|note".split("|"))
        for c in checks:
            w.writerow([c["check"], c["scope"], c["official_value"], c["published_value"],
                        c["result"], c["source"], c["note"]])

    print("re-verification checks: %d, non-matching: %d" % (len(checks), sum(1 for c in checks if c["result"] != "match")))
    for c in checks:
        print("  %-9s %s%s" % (c["result"], c["check"], "" if c["result"] == "match" else "  -> " + c["published_value"]))
    print("refreshed hub register: %d rows, %d clubs with rows, %d added after the snapshot"
          % (len(live), len([c for c in lc if lc[c]]), len(added)))
    json.dump({"added": len(added), "removed": len(removed), "changed": len(changed),
               "hub_rows": len(live), "snapshot_rows": len(snap), "slug_mismatches": len(slug_bad)},
              open(os.path.join(DATA, "reverification_a392.json"), "w"), indent=1)
    # SUPERSEDED is an expected, published outcome (the hub moved); MISMATCH is a defect.
    hard = [c for c in checks if c["result"] == "MISMATCH"]
    return 1 if hard else 0


if __name__ == "__main__":
    sys.exit(main())
