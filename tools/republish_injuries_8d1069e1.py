#!/usr/bin/env python3
"""Republish the Week 10 injury table from the pinned official capture (session 8d1069e1, task T-8D1-01).

Closes FL-94: the published injury table still held the 12 November read, in which the three Detroit
designations were blank and the Rams block disagreed with the official page.

Input : the pinned capture data/captures/injuries_hub/20261116T143921Z_e2b4074a9837.bin (its SHA-256 must
        equal the manifest row) and data/schedule_2026_wk10.csv (club -> Week 10 game_id).
Parse : tools/reconcile_capture_7c23f22f.parse_tables, unchanged. 28 clubs, 347 player rows; any
        structural surprise aborts the run.
Output:
  data/injuries_2026_wk10.csv                       canonical table (same schema as before), now the 16 Nov read
  data/injuries_wk10_hub_20261116.csv               row-level audit file: raw page text, normalised codes, source, clock
  data/injuries_2026_wk10_superseded_12nov.csv   the previous canonical table, byte-for-byte, kept for history

Nothing is inferred: a blank in the capture stays blank; practice and game-status vocabulary is mapped only by the
exact table in reconcile_capture_7c23f22f.py; unknown vocabulary aborts the run.

Usage: python3 tools/republish_injuries_8d1069e1.py          (write)
       python3 tools/republish_injuries_8d1069e1.py --check  (fail if the committed outputs differ from a rebuild)
"""
from __future__ import annotations

import csv
import hashlib
import io
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reconcile_capture_7c23f22f as rc  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
CANON = DATA / "injuries_2026_wk10.csv"
AUDIT = DATA / "injuries_wk10_hub_20261116.csv"
ARCHIVE = DATA / "injuries_2026_wk10_superseded_12nov.csv"
SCHEDULE = DATA / "schedule_2026_wk10.csv"
CANON_FIELDS = ["game", "team", "player", "slug", "pos", "injury", "practice", "status"]
AUDIT_FIELDS = ["game", "team", "player", "slug", "pos", "injury", "practice_raw", "practice", "status_raw",
                "status", "fetch_utc", "source_url", "capture_sha256"]
FETCH_UTC = "2026-11-16T14:39:21Z"
SOURCE = rc.OFFICIAL_HOST + "/injuries/"
# The official page writes the Rams as LA; the repository's schedule and the old table use LAR.
PAGE_TO_REPO = {"LA": "LAR"}


def load() -> tuple[list[dict], str]:
    cap = rc.capture_row(rc.PINNED_CAPTURE)
    raw = (ROOT / cap["stored_path"]).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != cap["sha256"]:
        raise SystemExit("pinned capture hash does not match the manifest")
    text = raw.decode("utf-8", errors="replace")
    parsed = rc.parse_tables(text, rc.club_map(text))
    if len(parsed) != 347:
        raise SystemExit(f"expected 347 player rows, parsed {len(parsed)}")
    return parsed, digest


def game_index() -> dict[str, str]:
    idx: dict[str, str] = {}
    with SCHEDULE.open(encoding="utf-8") as fh:
        for g in csv.DictReader(fh, delimiter="|"):
            idx[g["home"]] = g["game_id"]
            idx[g["away"]] = g["game_id"]
    return idx


def build_rows() -> tuple[list[dict], list[dict], str]:
    parsed, digest = load()
    games = game_index()
    canon, audit = [], []
    for r in parsed:
        club = PAGE_TO_REPO.get(r["club"], r["club"])
        if club not in games:
            raise SystemExit(f"club {club} is not on the Week 10 schedule")
        practice_raw, status_raw = r["practice_raw"], r["status_raw"]
        if practice_raw not in rc.PRACTICE:
            raise SystemExit(f"unknown practice vocabulary {practice_raw!r} for {r['player']}: not mapped by guess")
        if status_raw not in rc.STATUS:
            raise SystemExit(f"unknown game-status vocabulary {status_raw!r} for {r['player']}: not mapped by guess")
        practice = rc.PRACTICE[practice_raw]
        status = rc.STATUS[status_raw]
        slug = r["player_url"].rstrip("/").rsplit("/", 1)[-1] if r["player_url"] else ""
        canon.append({"game": games[club], "team": club, "player": r["player"], "slug": slug, "pos": r["pos"],
                      "injury": r["injury"], "practice": practice, "status": status})
        audit.append({"game": games[club], "team": club, "player": r["player"], "slug": slug, "pos": r["pos"],
                      "injury": r["injury"], "practice_raw": practice_raw, "practice": practice,
                      "status_raw": status_raw, "status": status, "fetch_utc": FETCH_UTC,
                      "source_url": r["player_url"] or SOURCE, "capture_sha256": digest})
    canon.sort(key=lambda x: (x["game"], x["team"], x["player"]))
    audit.sort(key=lambda x: (x["game"], x["team"], x["player"]))
    return canon, audit, digest


def render(fields: list[str], rows: list[dict]) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields, delimiter="|", lineterminator="\n")
    w.writeheader()
    for r in rows:
        if any("|" in str(v) for v in r.values()):
            raise SystemExit("a value contains the pipe delimiter")
        w.writerow(r)
    return buf.getvalue()


def main() -> int:
    check = "--check" in sys.argv
    canon, audit, digest = build_rows()
    outputs = {
        CANON: render(CANON_FIELDS, canon),
        AUDIT: render(AUDIT_FIELDS, audit),
    }
    if check:
        bad = [str(p.relative_to(ROOT)) for p, txt in outputs.items()
               if not p.exists() or p.read_text(encoding="utf-8") != txt]
        if bad:
            print("republish drift: " + ", ".join(bad))
            return 1
        print(f"republish OK: {len(canon)} rows, capture {digest[:12]}")
        return 0
    if not ARCHIVE.exists():
        shutil.copyfile(CANON, ARCHIVE)  # keep the superseded 12 Nov table verbatim
    for p, txt in outputs.items():
        p.write_text(txt, encoding="utf-8")
    print(f"wrote {len(canon)} rows to {CANON.relative_to(ROOT)} and {AUDIT.relative_to(ROOT)}; "
          f"capture {digest[:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
