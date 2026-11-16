#!/usr/bin/env python3
"""Retained, hashed captures of official NFL transaction pages (session 6eeab460, R2 / R6).

Scope: the official reserve-list and trades pages on nfl.com, one page per month of 2026.
Why: BL-13 (the 32-team roster and IR sweep) and BL-34 (roster turnover as a first-class event)
need every month's reserve and trade rows, not only November. The analysis sandbox cannot reach
nfl.com; GitHub-hosted runners can (see .github/workflows/capture.yml), so this tool runs there.

Per run, for every URL in PAGES:
  1. Fetch the page with a fixed User-Agent and a timeout. Never raises. The official tables are
     paginated 25 rows per page with an opaque cursor (`nfl-o-table-pagination__next`, `?after=...`),
     so the tool follows that Next Page link until none is present, up to MAX_PAGES. A chain that is
     still open at MAX_PAGES fails the row (schema_ok=no) rather than publishing a truncated month.
  2. Record UTC fetch time, HTTP status, byte count and SHA-256 of the raw bytes.
  3. Store the raw bytes under data/captures/<kind>/<YYYY-MM>/ only when that SHA-256 has not been
     stored before for that page. Files are named by UTC stamp and hash prefix and never overwritten.
  4. Append one row per fetch to data/roster_capture_manifest_6eeab460.csv (append-only, pipe-delimited).
  5. Check the structure it depends on (title, the six-column transaction header, a non-empty
     tbody and at least one player link). If any check fails the row says schema_ok=no and the run
     exits 1, so a changed page fails loudly instead of publishing a blank (BL-64).

What it does NOT do: it parses no rows into any published table. Parsing is tools/roster_parse_6eeab460.py.

Usage:
  python3 tools/roster_capture_6eeab460.py            fetch, store, append manifest, exit 0 / 1
  python3 tools/roster_capture_6eeab460.py --dry-run  fetch and print, write nothing
  python3 tools/roster_capture_6eeab460.py --months 11 fetch only the listed month numbers
"""
from __future__ import annotations

import argparse
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
MANIFEST = ROOT / "data" / "roster_capture_manifest_6eeab460.csv"

SEASON = 2026
KINDS = {
    "reserve_list": "https://www.nfl.com/transactions/league/reserve-list/{year}/{month:02d}",
    "trades": "https://www.nfl.com/transactions/league/trades/{year}/{month:02d}",
}

USER_AGENT = "NFL2-capture/1.0 (+https://github.com/kanlerxz87-cyber/NFL2; official-page archival)"
TIMEOUT_S = 60
RETRIES = 3

MAX_PAGES = 12

MANIFEST_FIELDS = [
    "fetch_utc", "kind", "season", "month", "page_seq", "source_url", "http_status", "bytes", "sha256",
    "stored_path", "new_content", "title", "header_ok", "tbody_rows", "player_links", "empty_state",
    "next_href", "schema_ok", "note",
]

TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)
# The six columns of the official transaction table, in order (verified on the 2026/11 page).
HEADER_RE = re.compile(
    r"<th[^>]*>\s*From\s*</th>.*?<th[^>]*>\s*To\s*</th>.*?<th[^>]*>\s*Date\s*</th>"
    r".*?<th[^>]*>\s*Name\s*</th>.*?<th[^>]*>\s*Position\s*</th>.*?<th[^>]*>\s*Transaction\s*</th>",
    re.I | re.S,
)
TBODY_RE = re.compile(r"<tbody[^>]*>(.*?)</tbody>", re.I | re.S)
ROW_RE = re.compile(r"<tr[^>]*>(.*?)</tr>", re.I | re.S)
# Player links are relative on the live page (href="/players/<slug>/"); absolute links are accepted too.
PLAYER_LINK_RE = re.compile(r"href=\"(?:https://www\.nfl\.com)?/players/[^\"]+\"", re.I)
EMPTY_STATE_RE = re.compile(r"No Transactions Available", re.I)
NEXT_RE = re.compile(r"<a[^>]*class=\"nfl-o-table-pagination__next\"[^>]*href=\"([^\"]+)\"|<a[^>]*href=\"([^\"]+)\"[^>]*class=\"nfl-o-table-pagination__next\"", re.I)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def page_urls(months: list[int]) -> list[tuple[str, int, str]]:
    out = []
    for kind, template in KINDS.items():
        for m in months:
            out.append((kind, m, template.format(year=SEASON, month=m)))
    return out


def fetch(url: str) -> tuple[int, bytes, str]:
    """Return (http_status, raw_bytes, note). Retries transient failures; never raises."""
    last_note = ""
    for attempt in range(1, RETRIES + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,*/*"})
            with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
                return resp.status, resp.read(), ""
        except urllib.error.HTTPError as exc:
            return exc.code, b"", f"HTTP error {exc.code}"
        except Exception as exc:  # network / TLS / timeout
            last_note = f"{type(exc).__name__}: {exc}"
            time.sleep(2 * attempt)
    return 0, b"", f"no response after {RETRIES} attempts ({last_note})"


def parse_rows(text: str) -> list[tuple[str, str, str, str, str]]:
    """Every populated transaction row as (from_club, to_club, date_as_printed, player, transaction).
    Club slugs come from the team links; the player is the link text. Used for the coverage test only;
    the published tables are built by tools/roster_parse_6eeab460.py from the same bytes."""
    out = []
    for body in TBODY_RE.findall(text):
        for row in ROW_RE.findall(body):
            cells = re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)
            if len(cells) < 6:
                continue
            frm = re.search(r'href="/teams/([^/"]+)/?"', cells[0])
            to = re.search(r'href="/teams/([^/"]+)/?"', cells[1])
            name = re.search(r">([^<]+)</a>", cells[3])
            date = re.sub(r"<[^>]+>", "", cells[2]).strip()
            tx = re.sub(r"<[^>]+>", "", cells[5]).strip()
            nm = name.group(1).strip() if name else re.sub(r"<[^>]+>", "", cells[3]).strip()
            out.append((frm.group(1) if frm else "", to.group(1) if to else "", date, nm, tx))
    return out


def month_union(kind: str, month: int) -> set:
    """Distinct rows already held in retained bytes for this kind and month."""
    keys: set = set()
    folder = CAPTURE_DIR / kind / f"{SEASON}-{month:02d}"
    if folder.exists():
        for path in folder.glob("*.bin"):
            keys |= set(parse_rows(path.read_bytes().decode("utf-8", errors="replace")))
    return keys


def next_href(text: str, base_url: str) -> str:
    """Absolute URL of the Next Page link, or '' when this is the last page of the table."""
    from urllib.parse import urljoin
    m = NEXT_RE.search(text)
    if not m:
        return ""
    href = m.group(1) or m.group(2)
    return urljoin(base_url, href.replace("&amp;", "&"))


def inspect(text: str) -> dict:
    """Structural facts about one page. Counts are vocabulary/structure counts, not parsed rows."""
    m = TITLE_RE.search(text)
    title = re.sub(r"\s+", " ", m.group(1)).strip().replace("|", "/") if m else ""
    header_ok = bool(HEADER_RE.search(text))
    tb = TBODY_RE.findall(text)
    tbody_rows = 0
    if tb:
        tbody_rows = sum(1 for r in ROW_RE.findall(tb[-1]) if "<td" in r.lower())
    player_links = len(PLAYER_LINK_RE.findall(text))
    title_ok = any(w in title.lower() for w in ("transaction", "reserve", "trade"))
    empty_state = bool(EMPTY_STATE_RE.search(text))
    # A populated page carries the six-column table with rows and player links. An empty month carries
    # the explicit "No Transactions Available" block and no table. Anything else is a structure change.
    populated_ok = header_ok and tbody_rows > 0 and player_links > 0
    schema_ok = title_ok and (populated_ok or (empty_state and tbody_rows == 0))
    return {"title": title, "header_ok": header_ok, "tbody_rows": tbody_rows,
            "player_links": player_links, "empty_state": empty_state, "schema_ok": schema_ok,
            "title_ok": title_ok}


def read_manifest() -> list[dict]:
    if not MANIFEST.exists():
        return []
    with MANIFEST.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="|"))


def migrate_manifest_v1() -> None:
    """One-time, logged migration: the v1 manifest (first runner run, page 1 only, relative-link regex
    bug) is kept row for row. Its new columns are filled as page 1 and a note marks it as v1. No
    value in a v1 row is changed, and every v1 row's stored bytes stay in place."""
    if not MANIFEST.exists():
        return
    with MANIFEST.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh, delimiter="|"))
    if rows and "page_seq" in rows[0]:
        return
    for r in rows:
        r["page_seq"] = "1"
        r["empty_state"] = ""
        r["next_href"] = ""
        r["note"] = ("v1 row (first runner run, page 1 only; schema_ok=no reflects the v1 relative-link "
                     "regex, bytes valid): " + (r.get("note") or "")).strip()
    with MANIFEST.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=MANIFEST_FIELDS, delimiter="|", extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def run(months: list[int], dry_run: bool) -> int:
    """Fetch every month's pages. Page 1 is stored whenever its bytes are new. A later page is stored only
    when it adds rows that no retained capture of that month holds, and the chain stops at the first page
    that adds none. This bounds storage: the 25-row cursor returns repeats for some months (see FL-R2)."""
    if not dry_run:
        migrate_manifest_v1()
    rows_before = read_manifest()
    seen = {(r["source_url"], r["sha256"]) for r in rows_before if r.get("stored_path")}
    new_rows: list[dict] = []
    failures = 0

    for kind, month, base_url in page_urls(months):
        union = month_union(kind, month)
        url = base_url
        seq = 0
        while url and seq < MAX_PAGES:
            seq += 1
            fetched_at = utc_now()
            status, raw, note = fetch(url)
            row = {k: "" for k in MANIFEST_FIELDS}
            row.update({"fetch_utc": fetched_at, "kind": kind, "season": str(SEASON), "month": f"{month:02d}",
                        "page_seq": str(seq), "source_url": url, "http_status": str(status), "bytes": str(len(raw))})

            if status != 200 or not raw:
                row.update({"schema_ok": "no", "note": note or f"status {status}"})
                failures += 1
                new_rows.append(row)
                print(f"FAIL {kind} {SEASON}/{month:02d} p{seq}: {row['note']}")
                break

            digest = hashlib.sha256(raw).hexdigest()
            text = raw.decode("utf-8", errors="replace")
            facts = inspect(text)
            nxt = next_href(text, base_url)
            page_rows = set(parse_rows(text))
            added = page_rows - union
            union |= page_rows
            already = (url, digest) in seen
            store = (not already) and (seq == 1 or bool(added))
            stored = ""
            if store and not dry_run:
                folder = CAPTURE_DIR / kind / f"{SEASON}-{month:02d}"
                folder.mkdir(parents=True, exist_ok=True)
                stamp = fetched_at.replace(":", "").replace("-", "")
                path = folder / f"{stamp}_p{seq}_{digest[:12]}.bin"
                if path.exists():
                    raise SystemExit(f"refusing to overwrite {path}")
                path.write_bytes(raw)
                stored = path.relative_to(ROOT).as_posix()
                seen.add((url, digest))

            chain_stopped = seq > 1 and not added
            ok = facts["schema_ok"]
            if not ok:
                failures += 1
            if chain_stopped:
                note_txt = "cursor returned no row absent from retained captures; chain stopped (FL-R2)"
            elif not facts["schema_ok"]:
                note_txt = "expected title, six-column header with rows and player links, or the empty-state block"
            else:
                note_txt = f"distinct rows in month after this page: {len(union)}"
            row.update({
                "sha256": digest, "stored_path": stored,
                "new_content": "yes" if store else "no",
                "title": facts["title"], "header_ok": "yes" if facts["header_ok"] else "no",
                "tbody_rows": str(facts["tbody_rows"]), "player_links": str(facts["player_links"]),
                "empty_state": "yes" if facts["empty_state"] else "no", "next_href": nxt,
                "schema_ok": "yes" if ok else "no", "note": note_txt,
            })
            print(f"{kind} {SEASON}/{month:02d} p{seq}: {len(raw)} bytes sha256={digest[:12]} rows={facts['tbody_rows']} "
                  f"players={facts['player_links']} added={len(added)} stored={'yes' if store else 'no'} "
                  f"next={'yes' if nxt else 'no'} schema_ok={row['schema_ok']}")
            new_rows.append(row)
            if chain_stopped or not nxt:
                break
            url = nxt
        else:
            if url:  # loop exited because MAX_PAGES was reached with a Next link still open
                failures += 1
                new_rows[-1]["schema_ok"] = "no"
                new_rows[-1]["note"] = "pagination chain still open at MAX_PAGES"
                print(f"OPEN {kind} {SEASON}/{month:02d}: chain still open at MAX_PAGES={MAX_PAGES}")

    if not dry_run and new_rows:
        write_header = not MANIFEST.exists()
        with MANIFEST.open("a", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=MANIFEST_FIELDS, delimiter="|", extrasaction="ignore")
            if write_header:
                w.writeheader()
            for r in new_rows:
                w.writerow(r)
    print(f"done: {len(new_rows)} fetch rows, {failures} failure(s)")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--months", type=str, default="1,2,3,4,5,6,7,8,9,10,11",
                    help="comma-separated month numbers of the season year (default: all of 1-11)")
    ap.add_argument("--current-month", action="store_true",
                    help="scheduled mode: only the current UTC month of the season year")
    args = ap.parse_args(argv)
    months = [int(x) for x in args.months.split(",") if x.strip()]
    if args.current_month:
        months = [datetime.now(timezone.utc).month]
    return run(months, args.dry_run)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
