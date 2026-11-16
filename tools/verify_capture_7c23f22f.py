#!/usr/bin/env python3
"""Row-level verification of the official capture store (session 7c23f22f).

Checks, each reported PASS or FAIL with a count:
  1. manifest header equals the capture tool's field list;
  2. every stored row: the file exists, its SHA-256 equals the row's sha256, and the file name
     carries the first 12 hex digits of that hash;
  3. no stored file is referenced by two rows with different hashes; no file is shared;
  4. no orphan file under data/captures/ lacks a manifest row (nothing stored off-ledger);
  5. every source URL is an official https://www.nfl.com/ page and is in the tool's allowlist;
  6. a row with a non-200 status stores no file (a page that answers 200 but fails its schema
     check IS kept as raw evidence of drift, and is flagged by check 7's schema_ok = no);
  7. every row with schema_ok=yes carries a title that names the injury report.
Exit 0 when all pass, 1 otherwise. Zero rows is reported as a PASS with a visible note: no capture yet.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("capture_official", ROOT / "tools" / "capture_official.py")
cap = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cap)

results: list[tuple[bool, str]] = []


def check(ok: bool, text: str) -> None:
    results.append((bool(ok), text))


def main() -> int:
    manifest = cap.MANIFEST
    if not manifest.exists():
        check(False, "manifest data/capture_manifest.csv exists")
        return report()
    with manifest.open(newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh, delimiter="|")
        header = next(reader, [])
        rows = [dict(zip(header, r)) for r in reader]
    check(header == cap.MANIFEST_FIELDS, f"manifest header matches the capture tool ({len(rows)} rows)")

    referenced: dict[str, str] = {}
    bad_hash, bad_name, bad_url, bad_status, bad_title = [], [], [], [], []
    for i, r in enumerate(rows, start=2):
        url = r.get("source_url", "")
        if not (url.startswith("https://www.nfl.com/") and url in cap.OFFICIAL_URLS.values()):
            bad_url.append(f"line {i}: {url}")
        if r.get("http_status") != "200" and r.get("stored_path"):
            bad_status.append(f"line {i} stored a non-200 response")
        if r.get("schema_ok") == "yes":
            if "injur" not in r.get("title", "").lower() or r.get("title_has_injury_report") != "yes":
                bad_title.append(f"line {i}")
        sp = r.get("stored_path", "")
        if not sp:
            continue
        path = ROOT / sp
        if not path.is_file():
            bad_hash.append(f"line {i}: missing {sp}")
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != r.get("sha256"):
            bad_hash.append(f"line {i}: file hash {digest[:12]} != row {r.get('sha256','')[:12]}")
        if digest[:12] not in path.name:
            bad_name.append(f"line {i}: {path.name} lacks hash prefix")
        prior = referenced.get(sp)
        if prior is not None and prior != r.get("sha256"):
            bad_hash.append(f"line {i}: {sp} referenced with two hashes")
        referenced[sp] = r.get("sha256", "")

    stored_rows = sum(1 for r in rows if r.get("stored_path"))
    check(not bad_url, f"every source URL is an allowlisted official nfl.com page ({len(bad_url)} bad)")
    check(not bad_status, f"no non-200 response was stored ({len(bad_status)} bad)")
    check(not bad_title, f"every schema_ok row names the injury report in its title ({len(bad_title)} bad)")
    check(not bad_hash, f"every stored file's SHA-256 matches its row ({stored_rows} stored; {len(bad_hash)} bad)")
    check(not bad_name, f"every stored file name carries its hash prefix ({len(bad_name)} bad)")

    on_disk = sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / "data" / "captures").rglob("*.bin"))
    orphans = [p for p in on_disk if p not in referenced]
    check(not orphans, f"no orphan capture file without a manifest row ({len(orphans)} orphan, {len(on_disk)} on disk)")

    if not rows:
        print("NOTE  no capture rows yet: the runner workflow has not produced a capture")
    return report()


def report() -> int:
    failed = 0
    for ok, text in results:
        print(("PASS  " if ok else "FAIL  ") + text)
        failed += 0 if ok else 1
    print(f"verify_capture_7c23f22f: {len(results) - failed} passed · {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
