#!/usr/bin/env python3
"""Week 10 injury-read lineage, delta publication and live spot-check.

Session arena/d8372691-nfl2. Reads only files already in this repository and writes four
derived CSVs. No network access, no value is inferred: every number is a count or a comparison
of two stored rows.

    python3 scripts/injury_lineage_d8372691.py           # write the outputs
    python3 scripts/injury_lineage_d8372691.py --check   # fail if outputs differ from inputs

Honest limits (also published as FL-90):
  * Every input is a hand transcription of nfl.com/injuries/. No input is a retained raw
    response, so the SHA-256 values below hash the repository copy, not official bytes.
  * The live spot-check file was transcribed by the agent from the rendered page text returned
    by the fetch tool, not from a byte capture.
"""
import csv
import hashlib
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OFFICIAL = "https://www.nfl.com/injuries/"

# Practice and game-status vocabularies as printed on the official hub. Any other string is an
# error: a silent pass-through is exactly the drift this script exists to catch.
PRACTICE = {
    "": "",
    "F": "F", "L": "L", "D": "D",
    "Full Participation in Practice": "F",
    "Limited Participation in Practice": "L",
    "Did Not Participate In Practice": "D",
}
GAME = {"": "", "OUT": "OUT", "Out": "OUT", "Q": "Q", "Questionable": "Q",
        "D": "D", "Doubtful": "D"}

# Reads in the order they were taken. "claim" is the statement the site currently makes about
# that file (empty when no page states a count for it).
READS = [
    dict(id="L1", label="12 Nov ingest (first hub read)", file="data/injuries_2026_wk10.csv",
         read_utc="2026-11-12T04:40Z", source="S-INJ", scope="full",
         claim="All 254 rows the league published for Week 10 (content/injuries.md)"),
    dict(id="L2", label="12 Nov second read (22:35Z refresh)", file="data/injuries_wk10_2026_hubrefresh.csv",
         read_utc="2026-11-12T22:35Z", source="S-INJ-2235", scope="full", claim=""),
    dict(id="L3", label="12 Nov club-by-club transcript (crosscheck)",
         file="crosscheck/data/live_wk10_injuries_2026-11-12.csv",
         read_utc="not recorded in file", source=OFFICIAL, scope="full", claim=""),
    dict(id="L4", label="13 Nov read (12:46Z)", file="data/injuries_wk10_83246f00.csv",
         read_utc="2026-11-13T12:46Z", source="S-INJ-1246", scope="full",
         claim="296 player-filings across 26 clubs (S-INJ-1246 register row)"),
    dict(id="L5", label="13 Nov s745 file (captured_utc recorded in file)", file="data/s745_injury_refresh.csv",
         read_utc="2026-11-13T12:45Z", source=OFFICIAL, scope="full", claim=""),
    dict(id="L6", label="13 Nov s2268 file", file="data/s2268_injuries_wk10_20261113.csv",
         read_utc="not recorded in file", source=OFFICIAL, scope="full", claim=""),
    dict(id="L7", label="15 Nov live read, four clubs", file="data/injuries_wk10_e733834d_20261115.csv",
         read_utc="2026-11-15T12:13Z", source="S-INJ-E733", scope="partial",
         claim="44 rows, WAS / NYG / NE / DET (S-INJ-E733 register row)"),
    dict(id="L8", label="15 Nov full hub read, 28 clubs (other session, 8dee7df7)",
         file="data/hub_read_8dee7df7.csv", read_utc="2026-11-15T12:51Z", source="S-INJ-8DEE",
         scope="full", claim="347 player rows, 28 clubs; LAC 19 rows and BAL 10 rows (the other session flags these as FL-81)"),
]
SPOT_FILE = "data/injury_live_chunk_d8372691.csv"
SCHEDULE = "data/schedule_2026_wk10.csv"
TEAMS = "data/teams.json"

# Each read is reconciled against one reference read: the earlier file it is meant to refresh.
REFERENCE = {"L1": None, "L2": "L1", "L3": "L2", "L4": "L2", "L5": "L4", "L6": "L4", "L7": "L4",
             "L8": "L4"}
SPOT_SOURCE = "S-INJ-D8"

OUT_LINEAGE = "data/injury_lineage_d8372691.csv"
OUT_CLUB = "data/injury_club_delta_d8372691.csv"
OUT_PLAYERS = "data/injury_delta_players_d8372691.csv"
OUT_SPOT = "data/injury_spotcheck_d8372691.csv"


def path(rel):
    return os.path.join(ROOT, rel)


def read_pipe(rel):
    with open(path(rel), newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="|"))


def sha256(rel):
    with open(path(rel), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def club_of(r):
    return (r.get("club") or r.get("team") or "").strip()


def game_status_of(r):
    return r["status"] if "status" in r else r.get("game_status", "")


def norm(r):
    """Normalise one player row to comparable codes. Unknown vocabulary raises."""
    practice_raw = r.get("practice", "").strip()
    status_raw = game_status_of(r).strip()
    if practice_raw not in PRACTICE:
        raise ValueError("unknown practice string %r for %s" % (practice_raw, r.get("player")))
    if status_raw not in GAME:
        raise ValueError("unknown game status %r for %s" % (status_raw, r.get("player")))
    return {
        "club": club_of(r),
        "player": r["player"].strip(),
        "pos": r.get("pos", "").strip(),
        "injury": r.get("injury", "").strip(),
        "practice": PRACTICE[practice_raw],
        "status": GAME[status_raw],
    }


def load_read(spec):
    raw = read_pipe(spec["file"])
    players, sentinels = [], []
    for r in raw:
        if not r.get("player", "").strip():
            # The s745 file carries "No Injuries Reported" blocks as rows with no player.
            sentinels.append(club_of(r))
            continue
        players.append(norm(r))
    return {"spec": spec, "players": players, "sentinels": sentinels, "file_rows": len(raw),
            "sha": sha256(spec["file"]), "by_key": {(p["club"], p["player"]): p for p in players}}


def playing_clubs():
    rows = read_pipe(SCHEDULE)
    clubs = set()
    for r in rows:
        clubs.add(r["away"].strip())
        clubs.add(r["home"].strip())
    return clubs


def all_clubs():
    with open(path(TEAMS), encoding="utf-8") as fh:
        return sorted(t["abbr"] for t in json.load(fh)["teams"])


def fields(p):
    return (p["injury"], p["practice"], p["status"])


def fmt_count(n):
    return str(n)


def write_csv(header, rows):
    buf = io.StringIO()
    w = csv.writer(buf, delimiter="|", lineterminator="\n")
    w.writerow(header)
    for r in rows:
        w.writerow(r)
    return buf.getvalue()


def build():
    reads = {s["id"]: load_read(s) for s in READS}
    playing = playing_clubs()
    clubs = all_clubs()
    if len(clubs) != 32:
        raise SystemExit("expected 32 clubs in %s, found %d" % (TEAMS, len(clubs)))
    if len(playing) != 28:
        raise SystemExit("expected 28 playing clubs in %s, found %d" % (SCHEDULE, len(playing)))

    L = reads
    keys = {k: set(v["by_key"]) for k, v in L.items()}
    clubs_with = {k: {p["club"] for p in v["players"]} for k, v in L.items()}
    counts = {k: {c: 0 for c in clubs} for k in L}
    for k, v in L.items():
        for p in v["players"]:
            counts[k][p["club"]] = counts[k].get(p["club"], 0) + 1

    # ---- 1. lineage ----------------------------------------------------------------
    lin_rows = []
    for rid in ["L1", "L2", "L3", "L4", "L5", "L6", "L7", "L8"]:
        v = L[rid]
        spec = v["spec"]
        n_players = len(v["players"])
        sentinel_clubs = set(v["sentinels"])
        if spec["scope"] == "full":
            absent = sorted(playing - clubs_with[rid] - sentinel_clubs)
        else:
            absent = ["not in this partial read"]
        claim_check = "no claim in repository"
        if rid == "L1":
            subset = keys["L1"] <= keys["L2"]
            extra = keys["L2"] - keys["L1"]
            per_club = {}
            for c, _ in extra:
                per_club[c] = per_club.get(c, 0) + 1
            detail = ", ".join("%s %d" % (c, per_club[c]) for c in sorted(per_club))
            claim_check = ("contradicted: %s all 254 rows are in L2, but L2 holds %d more players (%s); "
                           "the 254 file is not the full Week 10 hub as read at 12 Nov 22:35Z"
                           % ("yes," if subset else "NOT:", len(extra), detail))
        elif rid == "L4":
            ok = n_players == 296 and len(clubs_with["L4"]) == 26
            claim_check = ("matches: %d player rows across %d clubs" % (n_players, len(clubs_with["L4"]))
                           if ok else "contradicted: %d rows across %d clubs" % (n_players, len(clubs_with["L4"])))
        elif rid == "L8":
            lac = sum(1 for p in v["players"] if p["club"] == "LAC")
            bal = sum(1 for p in v["players"] if p["club"] == "BAL")
            ok = n_players == 347 and len(clubs_with["L8"]) == 28 and lac == 19 and bal == 10
            claim_check = ("matches: %d rows across %d clubs; LAC %d rows, BAL %d rows"
                           % (n_players, len(clubs_with["L8"]), lac, bal) if ok
                           else "contradicted: %d rows, %d clubs, LAC %d, BAL %d"
                           % (n_players, len(clubs_with["L8"]), lac, bal))
        elif rid == "L7":
            ok = n_players == 44 and len(clubs_with["L7"]) == 4
            claim_check = ("matches: %d rows across 4 clubs" % n_players if ok
                           else "contradicted: %d rows across %d clubs" % (n_players, len(clubs_with["L7"])))
        ref = REFERENCE[rid]
        if ref:
            # A partial read is only compared with the reference rows for the clubs it covers.
            ref_keys = keys[ref]
            if spec["scope"] == "partial":
                ref_keys = {k for k in ref_keys if k[0] in clubs_with[rid]}
            only_here = len(keys[rid] - ref_keys)
            only_ref = len(ref_keys - keys[rid])
            shared = keys[rid] & ref_keys
            diffs = sum(1 for k in shared if fields(L[rid]["by_key"][k]) != fields(L[ref]["by_key"][k]))
            recon = [ref, fmt_count(only_here), fmt_count(only_ref), fmt_count(diffs)]
        else:
            recon = ["none (first read)", "", "", ""]
        lin_rows.append([
            rid, spec["label"], spec["read_utc"], spec["source"], spec["file"], spec["scope"],
            fmt_count(n_players), fmt_count(len(v["sentinels"])), fmt_count(len(clubs_with[rid])),
            " ".join(absent) if absent else "none",
        ] + recon + [v["sha"], spec["claim"] or "none", claim_check])
    lineage = write_csv(
        ["read_id", "read", "read_utc", "source_id", "file", "scope", "player_rows",
         "no_injury_blocks", "clubs_with_players", "playing_clubs_without_rows", "reference_read",
         "players_only_here", "players_only_in_reference", "field_differences_on_shared",
         "sha256_repo_copy", "claim_in_repo", "claim_check"], lin_rows)

    # ---- 2. club delta -------------------------------------------------------------
    club_rows = []
    changes_24 = {c: 0 for c in clubs}
    changes_47 = {c: 0 for c in clubs}
    for key in keys["L2"] & keys["L4"]:
        if fields(L["L2"]["by_key"][key]) != fields(L["L4"]["by_key"][key]):
            changes_24[key[0]] += 1
    for key in keys["L7"] & keys["L4"]:
        if fields(L["L7"]["by_key"][key]) != fields(L["L4"]["by_key"][key]):
            changes_47[key[0]] += 1
    changes_48 = {c: 0 for c in clubs}
    for key in keys["L8"] & keys["L4"]:
        if fields(L["L8"]["by_key"][key]) != fields(L["L4"]["by_key"][key]):
            changes_48[key[0]] += 1
    partial = {c for c in clubs if c in clubs_with["L7"]} | set(
        p["club"] for p in L["L7"]["players"])
    for c in clubs:
        in_l7 = c in partial
        row = [
            c, "yes" if c in playing else "bye (not in Week 10 schedule)",
            fmt_count(counts["L1"][c]), fmt_count(counts["L2"][c]), fmt_count(counts["L4"][c]),
            fmt_count(counts["L4"][c] - counts["L2"][c]), fmt_count(counts["L5"][c]),
            fmt_count(counts["L6"][c]), fmt_count(counts["L7"][c]) if in_l7 else "",
            fmt_count(counts["L7"][c] - counts["L4"][c]) if in_l7 else "",
            fmt_count(changes_24[c]), fmt_count(changes_47[c]) if in_l7 else "",
            fmt_count(counts["L8"][c]), fmt_count(counts["L8"][c] - counts["L4"][c]),
            fmt_count(changes_48[c]),
            OFFICIAL,
        ]
        club_rows.append(row)
    club = write_csv(
        ["club", "week10_status", "rows_L1_254", "rows_L2_279", "rows_L4_296", "delta_L4_minus_L2",
         "rows_L5_s745", "rows_L6_s2268", "rows_L7_15nov", "delta_L7_minus_L4",
         "value_changes_L2_to_L4", "value_changes_L4_to_L7", "rows_L8_15nov_full",
         "delta_L8_minus_L4", "value_changes_L4_to_L8", "source"], club_rows)

    # ---- 3. player-level delta between the 12 Nov refresh and the 13 Nov read --------
    prow = []
    for key in sorted(keys["L2"] | keys["L4"]):
        a = L["L2"]["by_key"].get(key)
        b = L["L4"]["by_key"].get(key)
        if a and b and fields(a) == fields(b):
            continue
        if a and not b:
            change = "removed"
        elif b and not a:
            change = "added"
        else:
            change = "value changed"
        prow.append([
            change, key[0], key[1], (b or a)["pos"],
            a["injury"] if a else "", a["practice"] if a else "", a["status"] if a else "",
            b["injury"] if b else "", b["practice"] if b else "", b["status"] if b else "",
            OFFICIAL,
        ])
    players = write_csv(
        ["change", "club", "player", "pos", "injury_12nov_2235", "practice_12nov_2235",
         "status_12nov_2235", "injury_13nov_1246", "practice_13nov_1246", "status_13nov_1246",
         "source"], prow)

    # ---- 4. live spot-check against the four-club files ---------------------------------
    live_raw = read_pipe(SPOT_FILE)
    live = {}
    for r in live_raw:
        p = norm({"club": r["club"], "player": r["player"], "pos": r["pos"], "injury": r["injury"],
                  "practice": r["practice_live"], "status": r["status_live"]})
        live[(p["club"], p["player"])] = p
    live_keys = set(live)
    l7_keys = keys["L7"]
    l8 = L["L8"]["by_key"]
    if live_keys != {k for k in l7_keys} or len(live_raw) != 44:
        raise SystemExit("spot-check keys do not match the four-club file: live %d vs L7 %d"
                         % (len(live_keys), len(l7_keys)))
    spot_rows = []
    m7 = m4 = m8 = 0
    for key in sorted(live_keys, key=lambda k: (k[0], k[1])):
        lv = live[key]
        a = L["L7"]["by_key"][key]
        b = L["L4"]["by_key"].get(key)
        ok7 = fields(lv) == fields(a)
        ok4 = b is not None and fields(lv) == fields(b)
        c8 = l8.get(key)
        ok8 = c8 is not None and fields(lv) == fields(c8)
        m7 += ok7
        m4 += ok4
        m8 += ok8
        spot_rows.append([
            key[0], key[1], lv["pos"],
            lv["practice"], lv["status"], lv["injury"],
            a["practice"], a["status"],
            "yes" if ok7 else "no",
            (b["practice"] if b else ""), (b["status"] if b else ""),
            "yes" if ok4 else "no",
            "yes" if ok8 else "no",
            SPOT_SOURCE,
        ])
    spot = write_csv(
        ["club", "player", "pos", "live_practice", "live_status", "live_injury", "L7_practice",
         "L7_status", "L7_matches_live", "L4_practice", "L4_status", "L4_matches_live",
         "L8_matches_live", "source"],
        spot_rows)

    summary = {"L7_matches_live": m7, "L4_matches_live": m4, "L8_matches_live": m8,
               "live_rows": len(live_keys)}
    return {OUT_LINEAGE: lineage, OUT_CLUB: club, OUT_PLAYERS: players, OUT_SPOT: spot}, summary


def main(argv):
    outputs, summary = build()
    if "--check" in argv:
        bad = []
        for rel, text in outputs.items():
            current = open(path(rel), encoding="utf-8").read() if os.path.exists(path(rel)) else None
            if current != text:
                bad.append(rel)
        if bad:
            print("DRIFT: outputs differ from inputs:", ", ".join(bad))
            return 1
        print("injury lineage: %d outputs match their inputs; spot-check vs live: L7 %d/%d, L4 %d/%d, L8 %d/%d"
              % (len(outputs), summary["L7_matches_live"], summary["live_rows"],
                 summary["L4_matches_live"], summary["live_rows"],
                 summary["L8_matches_live"], summary["live_rows"]))
        return 0
    for rel, text in outputs.items():
        with open(path(rel), "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        print("wrote", rel, "(%d lines)" % (text.count("\n") - 1))
    print("spot-check vs live: L7 %d/%d, L4 %d/%d, L8 %d/%d"
          % (summary["L7_matches_live"], summary["live_rows"], summary["L4_matches_live"],
             summary["live_rows"], summary["L8_matches_live"], summary["live_rows"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
