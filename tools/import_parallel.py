#!/usr/bin/env python3
"""Import the parallel session's verified 2026 game log into this repo's pipe-CSV format,
and cross-check it against the standings table transcribed independently from nfl.com.

Input : data/games_2026.json        (written by session arena-009ec582 from the official
                                      week-by-week schedule pages; every row carries its own
                                      nfl.com game URL)
Output: data/games_2026_wk1_9.csv   (one row per completed game, source column = that URL)

The cross-check is the point of this script: a game log and a standings table pulled from two
different official pages must imply the same record for all 32 clubs. Anything that does not
reconcile is printed and must be flagged, never smoothed over.
"""
import json, sys, collections, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "games_2026.json"
OUT = ROOT / "data" / "games_2026_wk1_9.csv"


def read_pipe_csv(path):
    lines = [ln.rstrip("\n") for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    head = [h.strip() for h in lines[0].split("|")]
    rows = []
    for ln in lines[1:]:
        cells = ln.split("|")
        if len(cells) != len(head):          # same guard the site builder uses
            raise SystemExit("FIELD COUNT MISMATCH in %s: %s\n  %s" % (path.name, ln, cells))
        rows.append(dict(zip(head, [c.strip() for c in cells])))
    return head, rows


def main():
    blob = json.loads(SRC.read_text(encoding="utf-8"))
    games = blob["games"]
    meta_n = blob.get("meta", {}).get("games")

    cols = ["week", "date", "away", "home", "away_pts", "home_pts", "neutral", "source"]
    out_lines, bad = ["|".join(cols)], []
    for g in games:
        src = g.get("src", "")
        if not src.startswith("https://www.nfl.com/games/"):
            bad.append((g.get("date"), g.get("away"), g.get("home"), src))
        out_lines.append("|".join([
            str(g.get("week", "")), str(g.get("date", "")), str(g.get("away", "")), str(g.get("home", "")),
            "" if g.get("away_pts") in (None, "") else str(g["away_pts"]),
            "" if g.get("home_pts") in (None, "") else str(g["home_pts"]),
            "yes" if g.get("neutral") else "no", src,
        ]))
    OUT.write_text("\n".join(out_lines) + "\n", encoding="utf-8")

    # --- recount records from the log -------------------------------------------------
    rec = collections.defaultdict(lambda: {"w": 0, "l": 0, "t": 0, "pf": 0, "pa": 0, "n": 0})
    for g in games:
        a, h = g["away"], g["home"]
        ap, hp = int(g["away_pts"]), int(g["home_pts"])
        rec[a]["n"] += 1; rec[h]["n"] += 1
        rec[a]["pf"] += ap; rec[a]["pa"] += hp
        rec[h]["pf"] += hp; rec[h]["pa"] += ap
        if ap > hp:   rec[a]["w"] += 1; rec[h]["l"] += 1
        elif ap < hp: rec[h]["w"] += 1; rec[a]["l"] += 1
        else:         rec[a]["t"] += 1; rec[h]["t"] += 1

    # The two datasets were transcribed from different official pages and the league itself is
    # inconsistent about the Rams: the standings table codes them LAR, the schedule/game pages
    # code them LA. Normalising the alias here (and publishing it as a flag) is the only edit
    # this script makes; no score, record or total is adjusted.
    ALIAS = {"LA": "LAR"}
    rec = {ALIAS.get(k, k): v for k, v in rec.items()}

    head, standings = read_pipe_csv(ROOT / "data" / "standings_2026.csv")
    diffs = []
    for row in standings:
        ab = row["abbr"]
        r = rec.get(ab)
        if r is None:
            diffs.append((ab, "no games in log", "", ""))
            continue
        for field, key in (("w", "w"), ("l", "l"), ("t", "t"), ("pf", "pf"), ("pa", "pa")):
            if int(row[field]) != r[key]:
                diffs.append((ab, field, row[field], r[key]))
        if row["w"].strip() and r["w"] + r["l"] + r["t"] != r["n"]:
            diffs.append((ab, "games_vs_record", "%s+%s+%s" % (row["w"], row["l"], row["t"]), r["n"]))
        if r["n"] not in (8, 9):          # a 9-week slate with byes: nobody plays 7 or 10
            diffs.append((ab, "games_played", "8 or 9", r["n"]))
    orphan = sorted(set(rec) - {row["abbr"] for row in standings})
    wk = collections.Counter(g["week"] for g in games)
    print("games per week        : %s" % ", ".join("W%d=%d" % (w, wk[w]) for w in sorted(wk)))

    print("games imported        : %d rows -> %s" % (len(games), OUT.relative_to(ROOT)))
    print("meta.games disagrees  : meta says %s, array has %d" % (meta_n, len(games)))
    print("rows without nfl.com URL: %d" % len(bad))
    print("neutral-site games    : %d" % sum(1 for g in games if g.get("neutral")))
    print("weeks                 : %s" % ", ".join(str(w) for w in sorted({g["week"] for g in games})))
    tot_w = sum(r["w"] for r in rec.values()); tot_l = sum(r["l"] for r in rec.values())
    tot_pf = sum(r["pf"] for r in rec.values()); tot_pa = sum(r["pa"] for r in rec.values())
    print("log totals            : W=%d L=%d T=%d PF=%d PA=%d net=%d"
          % (tot_w, tot_l, sum(r["t"] for r in rec.values()), tot_pf, tot_pa, tot_pf - tot_pa))
    print("table totals          : W=%d L=%d T=%d PF=%d PA=%d"
          % (sum(int(r["w"]) for r in standings), sum(int(r["l"]) for r in standings),
             sum(int(r["t"]) for r in standings), sum(int(r["pf"]) for r in standings),
             sum(int(r["pa"]) for r in standings)))
    print("reconciliation        : %d mismatching cells, %d clubs in log but not in the standings table"
          % (len(diffs), len(orphan)))
    for d in diffs[:25]:
        print("   MISMATCH %s %s: standings=%s log=%s" % d)
    for o in orphan:
        print("   ORPHAN CLUB %s (%d games)" % (o, rec[o]["n"]))
    return 0 if not diffs and not orphan and not bad else 1


if __name__ == "__main__":
    sys.exit(main())
