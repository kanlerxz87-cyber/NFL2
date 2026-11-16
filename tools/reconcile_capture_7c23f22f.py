#!/usr/bin/env python3
"""Row-by-row reconciliation of a retained official capture against a repository file (session 7c23f22f).

Input : the most recent manifest row with schema_ok = yes (data/capture_manifest.csv) and its stored bytes.
        The stored bytes are re-hashed and must equal the manifest hash, or the run fails.
Parse : every club table of the nfl.com injury page. The club abbreviation comes from the same page:
        each matchup strip pairs a clubs/logos/<ABBR> image with 'Go to <Nickname> page'. Exactly 28 pairs
        must be found, one per nickname, or the run fails.
Join  : (club abbreviation, player name) against a repository file (default:
        data/injuries_wk10_5de1805b_20261115.csv). Vocabulary is normalised to the register's codes:
          practice  Full Participation in Practice -> F ; Limited ... -> L ; Did Not Participate ... -> D ; blank -> blank
          status    Questionable -> Q ; Doubtful -> D ; Out -> OUT ; blank -> blank
        Anything else is written as found and reported as an unknown vocabulary term (it is never mapped by guess).
Output: data/capture_reconciliation_7c23f22f.csv (pipe-delimited, like every register), one row per captured or repository player, with the
        capture SHA-256 and the official player link. Nothing is edited in the repository file.

Usage: python3 tools/reconcile_capture_7c23f22f.py            (write the output)
       python3 tools/reconcile_capture_7c23f22f.py --check    (re-run and fail if the committed output differs)
"""
from __future__ import annotations

import csv
import hashlib
import html
import io
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "data" / "capture_manifest.csv"
REPO_FILE = ROOT / "data" / "injuries_wk10_5de1805b_20261115.csv"
OUT = ROOT / "data" / "capture_reconciliation_7c23f22f.csv"
OFFICIAL_HOST = "https://www.nfl.com"

# The repository file writes the Los Angeles Rams as LAR; the official page's own logo code is LA.
# This is the only club alias. It is applied to the repository key and disclosed in the output summary.
CLUB_ALIAS_REPO_TO_PAGE = {"LAR": "LA"}

PRACTICE = {
    "Full Participation in Practice": "F",
    "Limited Participation in Practice": "L",
    "Did Not Participate In Practice": "D",
    "": "",
}
STATUS = {"Questionable": "Q", "Doubtful": "D", "Out": "OUT", "": ""}

FIELDS = [
    "club", "player", "player_url", "pos_capture", "pos_repo", "injury_capture", "injury_repo",
    "practice_capture", "practice_repo", "status_capture", "status_repo", "in_capture", "in_repo",
    "match", "mismatch_fields", "capture_sha256", "repo_file",
]


def latest_capture() -> dict:
    with MANIFEST.open(newline="", encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(fh, delimiter="|") if r.get("schema_ok") == "yes" and r.get("stored_path")]
    if not rows:
        raise SystemExit("no schema-valid capture in data/capture_manifest.csv")
    return rows[-1]


def club_map(text: str) -> dict[str, str]:
    """nickname -> abbreviation, from the matchup strips of the same page."""
    pairs: dict[str, set[str]] = {}
    for m in re.finditer(r"clubs/logos/([A-Z]{2,3})\b", text):
        n = re.search(r'aria-label="Go to ([^"]+?) page"', text[m.end(): m.end() + 1200])
        if n:
            pairs.setdefault(n.group(1), set()).add(m.group(1))
    if len(pairs) != 28 or any(len(v) != 1 for v in pairs.values()):
        raise SystemExit(f"club map not 28 unique pairs: found {len(pairs)} nicknames")
    return {k: next(iter(v)) for k, v in pairs.items()}


def parse_tables(text: str, clubs: dict[str, str]) -> list[dict]:
    out = []
    for m in re.finditer(r'<table class="d3-o-table[^"]*">(.*?)</table>', text, re.S):
        spans = re.findall(r'<div class="d3-o-section-sub-title"><span>([^<]+)</span>', text[: m.start()])
        if not spans or spans[-1] not in clubs:
            raise SystemExit("a club table has no recognised club title")
        club = clubs[spans[-1]]
        tb = re.search(r"<tbody>(.*?)</tbody>", m.group(1), re.S)
        for r in re.findall(r"<tr>(.*?)</tr>", tb.group(1) if tb else "", re.S):
            cells = re.findall(r"<td[^>]*>(.*?)</td>", r, re.S)
            if len(cells) != 5:
                raise SystemExit(f"{club}: a player row has {len(cells)} cells, expected 5")
            href = re.search(r'href="(/players/[^"]+)"', cells[0])
            vals = [html.unescape(re.sub(r"<[^>]+>", "", c)).strip() for c in cells]
            out.append({
                "club": club, "player": vals[0], "player_url": OFFICIAL_HOST + href.group(1) if href else "",
                "pos": vals[1], "injury": vals[2], "practice_raw": vals[3], "status_raw": vals[4],
            })
    return out


def repo_rows() -> dict[tuple[str, str], dict]:
    with REPO_FILE.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh, delimiter="|"))
    keyed: dict[tuple[str, str], dict] = {}
    for r in rows:
        team = CLUB_ALIAS_REPO_TO_PAGE.get(r["team"], r["team"])
        key = (team, r["player"])
        if key in keyed:
            raise SystemExit(f"repository file has a duplicate key {key}")
        keyed[key] = r
    return keyed


def build() -> tuple[list[dict], dict]:
    cap = latest_capture()
    path = ROOT / cap["stored_path"]
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != cap["sha256"]:
        raise SystemExit(f"stored capture {path.name} hash {digest[:12]} != manifest {cap['sha256'][:12]}")
    text = raw.decode("utf-8", errors="replace")
    clubs = club_map(text)
    captured = parse_tables(text, clubs)
    repo = repo_rows()

    unknown: set[str] = set()
    out_rows = []
    seen_keys = set()
    for c in captured:
        if any("|" in v for v in c.values()):
            raise SystemExit("a captured value contains the pipe delimiter")
        key = (c["club"], c["player"])
        if key in seen_keys:
            raise SystemExit(f"capture has a duplicate key {key}")
        seen_keys.add(key)
        if c["practice_raw"] not in PRACTICE:
            unknown.add(c["practice_raw"])
        if c["status_raw"] not in STATUS:
            unknown.add(c["status_raw"])
        cp = PRACTICE.get(c["practice_raw"], "?" + c["practice_raw"])
        cs = STATUS.get(c["status_raw"], "?" + c["status_raw"])
        r = repo.get(key)
        mism = []
        if r is None:
            mism = ["not in repository file"]
        else:
            if c["pos"] != r["pos"]:
                mism.append("pos")
            if c["injury"] != r["injury"]:
                mism.append("injury")
            if cp != r["practice"]:
                mism.append("practice")
            if cs != r["status"]:
                mism.append("status")
        out_rows.append({
            "club": c["club"], "player": c["player"], "player_url": c["player_url"],
            "pos_capture": c["pos"], "pos_repo": r["pos"] if r else "",
            "injury_capture": c["injury"], "injury_repo": r["injury"] if r else "",
            "practice_capture": cp, "practice_repo": r["practice"] if r else "",
            "status_capture": cs, "status_repo": r["status"] if r else "",
            "in_capture": "yes", "in_repo": "yes" if r else "no",
            "match": "yes" if not mism else "no", "mismatch_fields": ";".join(mism),
            "capture_sha256": digest, "repo_file": REPO_FILE.relative_to(ROOT).as_posix(),
        })
    for key, r in sorted(repo.items()):
        if key in seen_keys:
            continue
        out_rows.append({
            "club": key[0], "player": key[1], "player_url": "",
            "pos_capture": "", "pos_repo": r["pos"], "injury_capture": "", "injury_repo": r["injury"],
            "practice_capture": "", "practice_repo": r["practice"], "status_capture": "", "status_repo": r["status"],
            "in_capture": "no", "in_repo": "yes", "match": "no", "mismatch_fields": "not in capture",
            "capture_sha256": digest, "repo_file": REPO_FILE.relative_to(ROOT).as_posix(),
        })
    out_rows.sort(key=lambda x: (x["club"], x["player"]))
    summary = {
        "capture": cap["stored_path"], "sha256": digest, "clubs": len(set(clubs.values())),
        "captured": len(captured), "repo": len(repo),
        "matched": sum(1 for x in out_rows if x["match"] == "yes"),
        "mismatched_in_both": sum(1 for x in out_rows if x["in_capture"] == "yes" and x["in_repo"] == "yes" and x["match"] == "no"),
        "capture_only": sum(1 for x in out_rows if x["in_capture"] == "yes" and x["in_repo"] == "no"),
        "repo_only": sum(1 for x in out_rows if x["in_capture"] == "no"),
        "unknown_vocab": sorted(unknown),
        "alias_applied": sorted(f"{a}->{b}" for a, b in CLUB_ALIAS_REPO_TO_PAGE.items()
                                 if any(r["club"] == b for r in out_rows)),
    }
    return out_rows, summary


def render(rows: list[dict]) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=FIELDS, delimiter="|", lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue()


def main() -> int:
    rows, s = build()
    text = render(rows)
    print(f"capture {s['capture']} sha256={s['sha256'][:12]} clubs={s['clubs']} captured_rows={s['captured']} repo_rows={s['repo']}")
    print(f"matched={s['matched']} mismatched_in_both={s['mismatched_in_both']} capture_only={s['capture_only']} repo_only={s['repo_only']}")
    print(f"unknown vocabulary terms: {s['unknown_vocab'] or 'none'}; club alias applied to repo key: {s['alias_applied']}")
    if s["unknown_vocab"]:
        print("FAIL unknown vocabulary; not mapped by guess")
        return 1
    if "--check" in sys.argv:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != text:
            print("FAIL committed reconciliation differs from a fresh run")
            return 1
        print("reconciliation reproduces byte-for-byte")
        return 0
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
