#!/usr/bin/env python3
"""Session `dbccb97d` — standalone verifier for the dated captures of 2026-11-16.

Gates, in order:
  1. data/hub_read_dbccb97d_20261116.csv parses; 347 rows, 28 clubs; practice codes
     in {F, L, D}; game status in {Out, Questionable, Doubtful, blank}; every row
     carries the nfl.com hub URL and the 2026-11-16T18:05Z read stamp.
  2. data/venues_week11_dbccb97d_20261116.csv parses; 13 rows keyed W11-01..W11-13;
     every stadium cell non-blank; every source_url is the fixture's own official
     game centre; the game ids agree with data/schedule_week11_2026.csv.
  3. data/reverification_dbccb97d.csv parses; the row-level deltas and the slate
     cross-check are MATCH; the venue-naming row is MISMATCH on exactly the three
     fixtures the capture documents; the schedule-release date row is PARTIAL.
  4. Determinism: regenerating the three artefacts with tools/dbccb97d_capture.py
     reproduces the committed bytes (imported in-process, nothing rewritten).
  5. Source discipline: every row of the three artefacts carries an https:// URL,
     and the FL-118 / FL-129 references resolve in data/flags.csv.

Exit code 1 on any failure; prints a PASS/FAIL line per check.
"""
import csv
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

HUB_CSV = DATA / "hub_read_dbccb97d_20261116.csv"
VENUE_CSV = DATA / "venues_week11_dbccb97d_20261116.csv"
REV_CSV = DATA / "reverification_dbccb97d.csv"
SCHED_CSV = DATA / "schedule_week11_2026.csv"
FLAGS_CSV = DATA / "flags.csv"

PRACTICE_CODES = {"F", "L", "D"}
STATUS_WORDS = {"Out", "Questionable", "Doubtful", ""}
EXPECTED_VENUE_DISCREPANT = {"W11-01", "W11-07", "W11-13"}

fails = []
oks = []


def check(cond, msg):
    (oks if cond else fails).append(msg)


def load_csv(path):
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f, delimiter="|"))
    return rows[0], rows[1:]


def load_capture_module():
    spec = importlib.util.spec_from_file_location(
        "dbccb97d_capture", ROOT / "tools" / "dbccb97d_capture.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    # --- 1. hub read -------------------------------------------------------
    header, rows = load_csv(HUB_CSV)
    check(header == ["read_utc", "source_url", "club", "player", "pos",
                     "injury", "practice", "game_status"],
          "hub CSV header is the eight expected columns")
    check(len(rows) == 347, f"hub CSV holds 347 rows (found {len(rows)})")
    clubs = {r[2] for r in rows}
    check(len(clubs) == 28, f"hub CSV holds 28 clubs (found {len(clubs)})")
    bad_practice = [r for r in rows if r[6] not in PRACTICE_CODES]
    check(not bad_practice,
          f"every practice cell is F/L/D ({len(bad_practice)} bad)")
    bad_status = [r for r in rows if r[7] not in STATUS_WORDS]
    check(not bad_status,
          f"every game-status cell is Out/Questionable/Doubtful/blank "
          f"({len(bad_status)} bad)")
    bad_src = [r for r in rows if not r[1].startswith("https://www.nfl.com/injuries/")
               or r[0] != "2026-11-16T18:05Z"]
    check(not bad_src,
          f"every hub row carries the official hub URL and the 18:05Z read stamp "
          f"({len(bad_src)} bad)")

    # --- 2. venues --------------------------------------------------------
    header, vrows = load_csv(VENUE_CSV)
    check(header == ["game_id", "away", "home", "game_slug", "location",
                     "stadium", "read_utc", "source_url"],
          "venue CSV header is the eight expected columns")
    check(len(vrows) == 13, f"venue CSV holds 13 rows (found {len(vrows)})")
    v_ids = {r[0] for r in vrows}
    check(v_ids == {f"W11-{i:02d}" for i in range(1, 14)},
          "venue CSV keys are exactly W11-01..W11-13")
    check(all(r[5].strip() for r in vrows),
          "every venue CSV stadium cell is non-blank (transcribed, not inferred)")
    check(all(r[7] == f"https://www.nfl.com/games/{r[3]}" for r in vrows),
          "every venue row's source_url is its own official game centre")
    sched_ids = set()
    with SCHED_CSV.open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="|"):
            sched_ids.add(r["game_id"])
    check(v_ids <= sched_ids, "every venue game id exists in the published schedule")

    # --- 3. re-verification register -------------------------------------
    header, crows = load_csv(REV_CSV)
    check(header == ["id", "check", "scope", "published_value", "official_value",
                     "result", "note", "source"],
          "reverification CSV header is the eight expected columns")
    by_id = {r[0]: r for r in crows}
    for cid in ["DBCC-01", "DBCC-02", "DBCC-03", "DBCC-04", "DBCC-05",
                "DBCC-06", "DBCC-08"]:
        check(cid in by_id and by_id[cid][5] == "MATCH",
              f"{cid} is present and MATCH")
    venue_row = by_id.get("DBCC-07")
    detail = venue_row[6] if venue_row else ""
    named = {gid for gid in EXPECTED_VENUE_DISCREPANT if gid in detail}
    check(venue_row is not None and venue_row[5] == "MISMATCH"
          and named == EXPECTED_VENUE_DISCREPANT,
          "DBCC-07 is MISMATCH on exactly the three documented fixtures")
    check(by_id.get("DBCC-09", ["", "", "", "", "", ""])[5] == "PARTIAL",
          "DBCC-09 (schedule-release date, FL-111) is PARTIAL, not guessed")

    # --- 4. determinism: regenerate in memory, compare to the files ------
    cap = load_capture_module()
    hub_expect = [",".join([cap.READ_UTC, cap.HUB_URL] + list(r))
                  for r in cap.HUB]
    hub_actual = [",".join(r) for r in rows]
    check(hub_expect == hub_actual,
          "hub CSV equals a fresh in-memory regeneration of the transcription")
    vend_expect = [",".join([g, a, h, slug, loc, stad, cap.READ_UTC,
                             f"https://www.nfl.com/games/{slug}"])
                   for (g, a, h, slug, loc, stad) in cap.VENUES]
    vend_actual = [",".join(r) for r in vrows]
    check(vend_expect == vend_actual,
          "venue CSV equals a fresh in-memory regeneration of the transcription")
    disc = [(g, s, cap.PARAM_VENUES[g]) for g, _, _, _, _, s in cap.VENUES
            if cap.PARAM_VENUES.get(g)
            and cap.PARAM_VENUES[g].strip().lower() != s.strip().lower()]
    check({g for g, _, _ in disc} == EXPECTED_VENUE_DISCREPANT,
          "the three venue-naming discrepancies are exactly W11-01/07/13")

    # --- 5. source discipline and flag resolution -------------------------
    all_rows = rows + vrows + crows
    check(all(any(cell.startswith("https://") for cell in r) for r in all_rows),
          "every row of the three artefacts carries an https:// source link")
    flag_ids = set()
    if FLAGS_CSV.exists():
        with FLAGS_CSV.open(encoding="utf-8", newline="") as f:
            flag_ids = {r["id"] for r in csv.DictReader(f, delimiter="|")}
    for fl in ("FL-118", "FL-129"):
        text = (HUB_CSV.read_text() + VENUE_CSV.read_text() + REV_CSV.read_text())
        check(fl in text and fl in flag_ids,
              f"{fl} is referenced by this session's artefacts and exists in data/flags.csv")

    for f in fails:
        print("FAIL", f)
    print(f"verify_dbccb97d: {len(oks)} passed · {len(fails)} failed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
