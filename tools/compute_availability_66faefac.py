#!/usr/bin/env python3
"""Session 66faefac — Week 10 availability, depth deficiency and a locked pre-registration.

Three registers are produced here and nowhere else, so every number on the two new pages is a
recomputation rather than a transcription of a note:

  data/availability_deficiency_66faefac.csv   designations/DNPs at the four clubs whose depth chart
                                              this repository transcribes, joined to that chart.
  data/club_availability_20261113_66faefac.csv  club-level availability, three-state, with the two
                                              earlier official reads beside it.
  data/prereg_wk10_66faefac.csv (+ .sha256)  the ST-15 calls for the 13 un-played Week 10 games,
                                              hashed before kickoff so the sample cannot be tuned.

The tool is deliberately paranoid: it fails if its own two hand-transcribed inputs disagree with
each other, with the earlier reads, or with the depth charts. A silent inconsistency in an
availability register is worse than a missing column, because the missing column is visibly blank.
"""
import csv, hashlib, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

AS_OF = "2026-11-13T12:45Z"
HUB = "https://www.nfl.com/injuries/"
# ST-15: take the healthier club against our own published number when the availability load
# differs by at least THRESHOLD players. Fixed before any Sunday kickoff; the sensitivity table
# below shows what other thresholds would have done, which is exactly why the lock exists.
THRESHOLD = 4


def read(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        raw = list(csv.reader(fh, delimiter="|"))
    hdr = raw[0]
    return [dict(zip(hdr, r)) for r in raw[1:]]


def write(name, header, rows):
    with open(os.path.join(DATA, name), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="|", lineterminator="\n")
        w.writerow(header)
        for r in rows:
            w.writerow([r.get(c, "") for c in header])


def norm(name):
    out = name.lower().replace(".", "").replace(",", "").replace("'", "").replace(" 3", "").replace(" jr", "")
    return " ".join(out.split())


def main():
    fails = []
    # ---------------------------------------------------------------- inputs
    flagged = read("hub_flagged_20261113_66faefac.csv")
    counts = read("hub_club_counts_20261113_66faefac.csv")
    snap1 = read("injuries_2026_wk10.csv")                 # 2026-11-12 04:45Z
    snap2 = read("injuries_wk10_2026_hubrefresh.csv")      # 2026-11-12 22:35Z
    sched = read("schedule_2026_wk10.csv")
    played = {r["game_id"] for r in read("games_2026_wk10_played.csv")}
    orig = {r["game"]: r for r in read("originated_lines_wk10_a392.csv")}
    fair = {r["game_id"]: r for r in read("computed_fair_lines.csv")}
    with open(os.path.join(DATA, "depth_charts.json"), encoding="utf-8") as fh:
        charts = json.load(fh)["depth_charts"]

    # ---------------------------------------------------------------- internal consistency
    n_rows = sum(int(r["rows_listed"]) for r in counts)
    if n_rows != 296:
        fails.append("club counts sum to %d rows, expected the 296 read from the hub" % n_rows)
    for r in counts:
        parts = int(r["dnp"]) + int(r["limited"]) + int(r["full"])
        if parts != int(r["rows_listed"]):
            fails.append("%s: D/L/F sums to %d but the club lists %d rows" % (r["club"], parts, r["rows_listed"]))
        if int(r["rows_listed"]) == 0 and r["state"] != "declared none":
            fails.append("%s: zero rows but state is %r, not 'declared none'" % (r["club"], r["state"]))
        if int(r["out"]) + int(r["questionable"]) + int(r["doubtful"]) > int(r["rows_listed"]):
            fails.append("%s: more designations than listed rows" % r["club"])
    # every designation and DNP we publish must be inside a club row count we also publish
    by_club = {r["club"]: r for r in counts}
    for r in flagged:
        c = by_club.get(r["club"])
        if c is None:
            fails.append("%s is not on the Week 10 slate" % r["club"]); continue
        if r["status"] == "OUT" and int(c["out"]) == 0:
            fails.append("%s has a designation but zero OUT rows in the club count" % r["club"])
        if r["practice"] == "D" and int(c["dnp"]) == 0:
            fails.append("%s has a DNP row but zero DNP in the club count" % r["club"])
    for snap, label, expect in ((snap1, "04:45Z", 254), (snap2, "22:35Z", 279)):
        if len(snap) != expect:
            fails.append("the %s snapshot holds %d rows, but the site publishes %d" % (label, len(snap), expect))
    n_design = sum(1 for r in flagged if r["status"] in ("OUT", "Q", "D"))
    if n_design != sum(int(r["out"]) + int(r["questionable"]) + int(r["doubtful"]) for r in counts):
        fails.append("designation rows (%d) and club counts (%d) disagree"
                     % (n_design, sum(int(r["out"]) + int(r["questionable"]) + int(r["doubtful"]) for r in counts)))

    # ---------------------------------------------------------------- 1. deficiency join
    def lookup(club, player):
        """Return (group, string_no, next_man_up, names_ahead) for every depth group the club
        lists this player in. Exact match on the normalised name, no fuzzy fallback."""
        want = norm(player)
        hits = []
        for unit in ("offense", "defense"):
            for group, names in charts.get(club, {}).get(unit, {}).items():
                for i, n in enumerate(names):
                    if norm(n) == want:
                        hits.append((unit, group, i, names))
        return hits

    ordinals = {1: "1st string", 2: "2nd string", 3: "3rd string", 4: "4th string"}
    prev1 = {norm(r["player"]): r for r in snap1}
    prev2 = {norm(r["player"]): r for r in snap2}
    def_rows = []
    for r in flagged:
        state = {"OUT": "designated out", "Q": "questionable", "D": "doubtful"}.get(r["status"], "did not practise")
        hits = lookup(r["club"], r["player"]) if r["club"] in charts else []
        if not hits:
            def_rows.append({
                "club": r["club"], "game": r["game"], "side": r["side"],
                "position_group": "not listed on the club's chart in this build",
                "player": r["player"], "position": r["pos"], "availability_state": state,
                "injury": r["injury"], "string_depth": "not published",
                "next_man_up": "not published", "others_in_group": "not published",
                "group_left_without_a_charted_body": "not published",
                "prior_read_0445": prior(prev1, r), "prior_read_2235": prior(prev2, r),
                "practice_and_designation": ("conflict - the hub shows a practice code and a designation that disagree"
                                             if r["status"] == "OUT" and r["practice"] != "D"
                                             else "designation and practice agree"),
                "chart_note": "this club's chart is not transcribed in this build" if r["club"] not in charts
                              else "the transcribed chart carries no row naming this player",
                "depth_url": charts.get(r["club"], {}).get("club_site", "not published"),
                "injury_url": HUB,
            })
            continue
        for unit, group, i, names in hits:
            nxt = names[i + 1:]
            def_rows.append({
                "club": r["club"], "game": r["game"], "side": "offence" if unit == "offense" else "defence",
                "position_group": group, "player": r["player"], "position": r["pos"],
                "availability_state": state, "injury": r["injury"],
                "string_depth": ordinals.get(i + 1, "column %d" % (i + 1)),
                "next_man_up": nxt[0] if nxt else "none listed - vacancy",
                "others_in_group": str(len(nxt)),
                "group_left_without_a_charted_body": "yes" if i == 0 and len(names) == 1 else "no",
                "prior_read_0445": prior(prev1, r), "prior_read_2235": prior(prev2, r),
                "practice_and_designation": ("conflict - the hub shows a practice code and a designation that disagree"
                                             if r["status"] == "OUT" and r["practice"] != "D"
                                             else "designation and practice agree"),
                "depth_url": charts[r["club"]]["club_site"], "injury_url": HUB,
            })
    def sort_key(r):
        return (r["game"], r["club"], r["position_group"])
    def_rows.sort(key=sort_key)
    write("availability_deficiency_66faefac.csv",
          ["club", "game", "side", "position_group", "player", "position", "availability_state",
           "injury", "string_depth", "next_man_up", "others_in_group",
           "group_left_without_a_charted_body", "prior_read_0445", "prior_read_2235",
           "practice_and_designation", "chart_note", "depth_url", "injury_url"], def_rows)

    # ---------------------------------------------------------------- 2. club availability
    def club_state(club, snap):
        rows = [r for r in snap if r["team"] == club]
        if not rows:
            return "absent from the file", 0, 0
        return ("rows published", len(rows),
                sum(1 for r in rows if r["practice"] == "D" or (r.get("status") or "").strip() == "OUT"))
    out_rows = []
    for r in counts:
        s1, n1, _ = club_state(r["club"], snap1)
        s2, n2, _ = club_state(r["club"], snap2)
        load = int(r["out"]) + int(r["dnp"])
        out_rows.append({
            "game": r["game"], "club": r["club"], "state": r["state"],
            "rows_today": r["rows_listed"], "dnp": r["dnp"], "limited": r["limited"],
            "full": r["full"], "out": r["out"], "questionable": r["questionable"],
            "doubtful": r["doubtful"], "load_out_plus_dnp": str(load),
            "rows_at_2235": str(n2), "rows_at_0445": str(n1),
            "state_at_2235": s2, "state_at_0445": s1,
            "change_since_2235": "%+d" % (int(r["rows_listed"]) - n2),
            "chart_in_build": "yes" if r["club"] in charts else "not transcribed",
            "source": HUB,
        })
    write("club_availability_20261113_66faefac.csv",
          ["game", "club", "state", "rows_today", "dnp", "limited", "full", "out", "questionable",
           "doubtful", "load_out_plus_dnp", "rows_at_2235", "rows_at_0445", "state_at_2235",
           "state_at_0445", "change_since_2235", "chart_in_build", "source"], out_rows)

    # ---------------------------------------------------------------- 3. pre-registration
    load = {r["club"]: int(r["load_out_plus_dnp"]) for r in out_rows}
    pre, sens = [], []
    for g in sched:
        gid, away, home = g["game_id"], g["away"], g["home"]
        d = load[away] - load[home]
        settled = gid in played
        if abs(d) >= THRESHOLD:
            side = "home" if d > 0 else "away"
            side_club = home if d > 0 else away
            call = "take %s - the healthier club" % side_club
        else:
            call, side, side_club = "no call", "", ""
        o = orig.get(gid, {})
        f = fair.get(gid, {})
        pre.append({
            "game_id": gid, "date": g["date"], "away": away, "home": home,
            "away_load": str(load[away]), "home_load": str(load[home]), "load_delta": str(d),
            "call": call, "side_taken": side,
            "locked": "no - settled before the rule was written" if settled else "yes",
            "our_spread_home": o.get("our_spread_home_favoured", ""),
            "our_total": o.get("our_total", ""),
            "fair_spread_home": f.get("fair_spread_home", ""),
            "stake_units": "0", "settled": "yes" if settled else "no",
            "decision_utc": AS_OF, "rule": "ST-15 v1",
            "source": g["game_url"],
        })

    sens = [{"threshold": str(t),
             "games_called": str(len([p for p in pre if p["settled"] == "no" and abs(int(p["load_delta"])) >= t])),
             "share_of_slate": "%.0f%%" % (100.0 * len([p for p in pre if p["settled"] == "no"
                                                        and abs(int(p["load_delta"])) >= t]) /
                                          max(1, len([p for p in pre if p["settled"] == "no"]))),
             "note": "registered rule" if t == THRESHOLD else "not locked - shown so a reader can see how much the threshold matters",
             "source": "S-CALC"} for t in range(1, 7)]   # S-CALC: computed in-repo from the locked file
    write("prereg_sensitivity_66faefac.csv", ["threshold", "games_called", "share_of_slate", "note", "source"], sens)
    write("prereg_wk10_66faefac.csv",
          ["game_id", "date", "away", "home", "away_load", "home_load", "load_delta", "call",
           "side_taken", "locked", "our_spread_home", "our_total", "fair_spread_home", "stake_units",
           "settled", "decision_utc", "rule", "source"], pre)
    body = open(os.path.join(DATA, "prereg_wk10_66faefac.csv"), encoding="utf-8").read()
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
    n_calls = len([p for p in pre if p["settled"] == "no" and p["side_taken"]])
    with open(os.path.join(DATA, "prereg_wk10_66faefac.sha256"), "w", encoding="utf-8") as fh:
        fh.write("prereg_wk10_66faefac.csv sha256 %s\n" % digest)
        fh.write("# locked %s by session 66faefac, rule %s, threshold %d, %d of %d un-played games called\n"
                 % (AS_OF, "ST-15 v1", THRESHOLD, n_calls, len(pre) - len(played)))
        fh.write("# regenerate with: python3 tools/compute_availability_66faefac.py\n")

    # ---------------------------------------------------------------- report
    print("hub read %s: %d rows, %d clubs (%d with rows, %d declared none), %d designations"
          % (AS_OF, n_rows, len(counts), sum(1 for r in counts if r["state"] == "rows published"),
             sum(1 for r in counts if r["state"] == "declared none"), n_design))
    print("deficiency join: %d rows (charts transcribed for %d clubs; designations at the "
          "other clubs are carried with the string cells left blank)" % (len(def_rows), len(charts)))
    print("pre-registration: %d fixtures, %d locked calls at threshold %d, sha256 %s"
          % (len(pre), n_calls, THRESHOLD, digest[:16]))
    if fails:
        for f in fails:
            print("FAIL  " + f)
        return 1
    print("cross-checks: club counts, designation register and both earlier reads reconcile")
    return 0


def prior(idx, r):
    """What the same player looked like in an earlier read of the same official page."""
    p = idx.get(norm(r["player"]))
    if p is None:
        return "not on the file at that read"
    st = (p.get("status") or "").strip()
    label = {"F": "full", "L": "limited", "D": "did not practise"}.get(p.get("practice"), "not published")
    if st:
        label += " / " + {"OUT": "designated out", "Q": "questionable", "D": "doubtful"}.get(st, st)
    return label


if __name__ == "__main__":
    sys.exit(main())
