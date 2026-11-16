#!/usr/bin/env python3
"""Retained, hashed captures of official NFL pages (session 7c23f22f, FL-88 / FL-90).

What it does, per run:
  1. Fetches each official URL in OFFICIAL_URLS with a fixed User-Agent and a timeout.
  2. Records the UTC fetch time, HTTP status, byte count and SHA-256 of the raw response bytes.
  3. Stores the raw bytes under data/captures/<slug>/ ONLY when that SHA-256 has not been stored
     before for that URL. Files are named by UTC time and hash prefix and are never overwritten.
  4. Appends one row per fetch to data/capture_manifest.csv (append-only; the file is never rewritten).
  5. Checks the response for the structure it expects (title + practice-status vocabulary). If the
     structure is missing the run exits 1 and the row says schema_ok=no, so a changed page fails loudly
     instead of publishing a blank.

What it does NOT do: it does not parse player rows into any published table, edit any published page,
or change any value. The drift counts in the manifest are vocabulary hit counts, not row parses.

Usage:  python3 tools/capture_official.py            (fetch, store, append manifest, exit 0/1)
        python3 tools/capture_official.py --dry-run  (fetch and print, write nothing)
"""
from __future__ import annotations

import csv
import hashlib
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CAPTURE_DIR = ROOT / "data" / "captures"
MANIFEST = ROOT / "data" / "capture_manifest.csv"

# Only official league pages. Add a URL here only after it has been read on nfl.com.
OFFICIAL_URLS = {
    "injuries_hub": "https://www.nfl.com/injuries/",
}

USER_AGENT = "NFL2-capture/1.0 (+https://github.com/kanlerxz87-cyber/NFL2; official-page archival)"
TIMEOUT_S = 60
RETRIES = 3

MANIFEST_FIELDS = [
    "fetch_utc", "slug", "source_url", "http_status", "bytes", "sha256", "stored_path",
    "new_content", "title", "title_has_injury_report", "practice_status_hits",
    "game_status_hits", "table_tags", "schema_ok", "note",
]

# Vocabulary the page is expected to carry (nfl.com hub, Week 10 2026 read).
PRACTICE_VOCAB = re.compile(
    r"Full Participation in Practice|Limited Participation in Practice|Did Not Participate In Practice"
)
GAME_VOCAB = re.compile(r"\b(Out|Questionable|Doubtful)\b")


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch(url: str) -> tuple[int, bytes, str]:
    """Return (http_status, raw_bytes, note). Retries transient failures; never raises."""
    last_note = ""
    for attempt in range(1, RETRIES + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,*/*"})
            with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
                return resp.status, resp.read(), ""
        except urllib.error.HTTPError as exc:  # server answered with an error status
            return exc.code, b"", f"HTTP error {exc.code}"
        except Exception as exc:  # network / TLS / timeout
            last_note = f"{type(exc).__name__}: {exc}"
            time.sleep(2 * attempt)
    return 0, b"", f"no response after {RETRIES} attempts ({last_note})"


def title_of(text: str) -> str:
    m = re.search(r"<title[^>]*>(.*?)</title>", text, re.I | re.S)
    if m:
        return re.sub(r"\s+", " ", m.group(1)).strip()
    m = re.search(r"^# (.+)$", text, re.M)  # markdown-rendered responses
    return m.group(1).strip() if m else ""


def read_manifest() -> list[dict]:
    if not MANIFEST.exists():
        return []
    with MANIFEST.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def stored_hashes(slug: str, rows: list[dict]) -> set[str]:
    return {r["sha256"] for r in rows if r["slug"] == slug and r["stored_path"]}


def run(dry_run: bool = False) -> int:
    rows_before = read_manifest()
    new_rows: list[dict] = []
    failures = 0

    for slug, url in OFFICIAL_URLS.items():
        fetched_at = utc_now()
        status, raw, note = fetch(url)
        row = {k: "" for k in MANIFEST_FIELDS}
        row.update({"fetch_utc": fetched_at, "slug": slug, "source_url": url,
                    "http_status": str(status), "bytes": str(len(raw))})

        if status != 200 or not raw:
            row.update({"schema_ok": "no", "note": note or f"status {status}"})
            failures += 1
            new_rows.append(row)
            print(f"FAIL {slug}: {row['note']}")
            continue

        digest = hashlib.sha256(raw).hexdigest()
        text = raw.decode("utf-8", errors="replace")
        title = title_of(text)
        practice_hits = len(PRACTICE_VOCAB.findall(text))
        game_hits = len(GAME_VOCAB.findall(text))
        table_tags = text.count("<table") + len(re.findall(r"^\|.*\|\s*$", text, re.M))
        has_title = "injury report" in title.lower() or "injur" in title.lower()
        schema_ok = has_title and practice_hits > 0 and game_hits > 0

        already = digest in stored_hashes(slug, rows_before + new_rows)
        stored = ""
        if not already and not dry_run:
            CAPTURE_DIR.joinpath(slug).mkdir(parents=True, exist_ok=True)
            stamp = fetched_at.replace(":", "").replace("-", "")
            name = f"{stamp}_{digest[:12]}.bin"
            path = CAPTURE_DIR / slug / name
            if path.exists():  # never overwrite an existing capture
                raise SystemExit(f"refusing to overwrite {path}")
            path.write_bytes(raw)
            stored = path.relative_to(ROOT).as_posix()

        row.update({
            "sha256": digest,
            "stored_path": stored,
            "new_content": "no" if already else "yes",
            "title": title,
            "title_has_injury_report": "yes" if has_title else "no",
            "practice_status_hits": str(practice_hits),
            "game_status_hits": str(game_hits),
            "table_tags": str(table_tags),
            "schema_ok": "yes" if schema_ok else "no",
            "note": "" if schema_ok else "expected title/practice/game vocabulary not all present",
        })
        if not schema_ok:
            failures += 1
        new_rows.append(row)
        print(f"{'OK  ' if schema_ok else 'FAIL'} {slug} {fetched_at} sha256={digest[:16]} "
              f"bytes={len(raw)} practice_hits={practice_hits} game_hits={game_hits} "
              f"new_content={row['new_content']}")

    if not dry_run and new_rows:
        write_header = not MANIFEST.exists()
        with MANIFEST.open("a", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=MANIFEST_FIELDS)
            if write_header:
                w.writeheader()
            w.writerows(new_rows)

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(run(dry_run="--dry-run" in sys.argv))
