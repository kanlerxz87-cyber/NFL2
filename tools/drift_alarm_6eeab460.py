#!/usr/bin/env python3
"""Drift alarm for the roster-event pipeline (BL-64, session 6eeab460, R6).

Exits 1 (and prints every failure) when any of these hold:
  A. Stored bytes: every manifest row with a stored_path has that file on disk and its SHA-256 matches.
  B. Stored structure: every stored page passes the capture tool's inspect() (official title, six-column
     header with player links) or is the official empty-state block. The v1 manifest's schema_ok flag is not
     used, because it reflects a known regex bug (see the manifest notes); the bytes are checked directly.
  C. Pinned headers: each parsed output has exactly the header this alarm pins. A renamed or dropped column
     fails here, not silently downstream.
  D. Required fields: no blank value in the columns that identify a row (date, player, source, capture hash,
     club). A blank here means a field went missing from the parse.
  E. Count consistency: each parsed kind has exactly the number of distinct rows held in its stored bytes.
     Row counts are NOT pinned to a constant, because a new month of captures legitimately changes them.
  F. Coverage: every kind and month 2026-01..2026-11 has a coverage verdict (complete or incomplete).

Run: python3 tools/drift_alarm_6eeab460.py   (used by .github/workflows/roster_capture_6eeab460.yml)
"""
import csv
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import roster_capture_6eeab460 as rc  # noqa: E402

DATA = ROOT / "data"
PINNED_HEADERS = {
    "reserve_list_2026_6eeab460.csv": ["row_id", "season", "month", "date_printed", "date_iso", "from_club", "to_club", "player", "player_url", "position", "transaction", "source", "source_url", "first_capture_utc", "first_capture_path", "last_capture_utc", "captures_holding_row", "capture_sha256"],
    "trades_2026_6eeab460.csv": ["row_id", "season", "month", "date_printed", "date_iso", "from_club", "to_club", "player", "player_url", "position", "transaction", "source", "source_url", "first_capture_utc", "first_capture_path", "last_capture_utc", "captures_holding_row", "capture_sha256"],
    "roster_events_6eeab460.csv": ["event_id", "date_iso", "event_type", "club_from", "club_to", "player", "transaction", "date_printed", "source", "capture_sha256", "month"],
    "depth_versioning_6eeab460.csv": ["depth_row", "club", "unit", "position_group", "position_label", "depth", "player", "chart_as_published", "chart_date_iso", "versioning_status", "event_ids", "chart_source"],
    "roster_coverage_6eeab460.csv": ["kind", "season", "month", "chain_pages_fetched", "distinct_rows", "last_page_rows", "last_page_next_link", "coverage_status", "source", "source_url", "note"],
}
REQUIRED = {
    "reserve_list_2026_6eeab460.csv": ["date_iso", "player", "transaction", "source_url", "capture_sha256"],
    "trades_2026_6eeab460.csv": ["date_iso", "player", "from_club", "to_club", "source_url", "capture_sha256"],
    "roster_events_6eeab460.csv": ["event_id", "date_iso", "event_type", "player", "source", "capture_sha256"],
    "depth_versioning_6eeab460.csv": ["club", "player", "versioning_status", "chart_source"],
}
KIND_FILE = {"reserve_list": "reserve_list_2026_6eeab460.csv", "trades": "trades_2026_6eeab460.csv"}


def read(name):
    with (DATA / name).open(encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh, delimiter="|")
        header = next(reader)
        return header, [dict(zip(header, r)) for r in reader]


def main():
    fails = []

    # A. stored bytes match the manifest hash
    manifest = rc.read_manifest() if rc.MANIFEST.exists() else []
    stored = [r for r in manifest if r.get("stored_path")]
    for r in stored:
        path = ROOT / r["stored_path"]
        if not path.exists():
            fails.append("A: stored file missing: %s" % r["stored_path"]); continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != r["sha256"]:
            fails.append("A: hash mismatch for %s (manifest %s, file %s)" % (r["stored_path"], r["sha256"][:12], digest[:12]))

    # B. every stored page is structurally valid (checked on the bytes, not on the v1 flag)
    checked_pages = 0
    # Only this pipeline's folders. data/captures/injuries_hub belongs to capture_official.py and has its own check.
    page_paths = sorted(p for kind in KIND_FILE for p in (rc.CAPTURE_DIR / kind).rglob("*.bin")
                        if (rc.CAPTURE_DIR / kind).exists())
    for path in page_paths:
        facts = rc.inspect(path.read_bytes().decode("utf-8", errors="replace"))
        checked_pages += 1
        if not (facts["schema_ok"] or facts["empty_state"]):
            fails.append("B: stored page fails structure check: %s" % path.relative_to(ROOT).as_posix())

    # C, D. pinned headers and required fields
    for name, expected in PINNED_HEADERS.items():
        header, rows = read(name)
        if header != expected:
            fails.append("C: %s header changed: %s" % (name, ", ".join(sorted(set(header) ^ set(expected))) or "column order"))
            continue
        for col in REQUIRED.get(name, []):
            blanks = sum(1 for r in rows if not r[col].strip())
            if blanks:
                fails.append("D: %s has %d blank %s value(s)" % (name, blanks, col))

    # E. parsed rows equal distinct rows held in stored bytes, per kind
    for kind, name in KIND_FILE.items():
        union = set()
        folder = rc.CAPTURE_DIR / kind
        if folder.exists():
            for path in folder.rglob("*.bin"):
                union |= set(rc.parse_rows(path.read_bytes().decode("utf-8", errors="replace")))
        _, rows = read(name)
        if len(rows) != len(union):
            fails.append("E: %s has %d rows, stored bytes hold %d distinct rows" % (name, len(rows), len(union)))

    # F. every kind and month has a coverage verdict
    _, cov = read("roster_coverage_6eeab460.csv")
    have = {(r["kind"], r["month"]) for r in cov if r["coverage_status"].strip()}
    for kind in ("reserve_list", "trades"):
        for m in range(1, 12):
            key = (kind, "2026-%02d" % m)
            if key not in have:
                fails.append("F: no coverage verdict for %s %s" % key)

    print("drift alarm: %d manifest rows (%d with stored bytes), %d stored pages inspected" % (len(manifest), len(stored), checked_pages))
    if fails:
        print("DRIFT DETECTED: %d failure(s)" % len(fails))
        for f in fails:
            print("  - " + f)
        return 1
    print("drift alarm: PASS (no drift)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
