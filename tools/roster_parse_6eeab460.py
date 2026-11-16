#!/usr/bin/env python3
"""Row-level parse of the retained official transaction captures (session 6eeab460, R3-R5).

Inputs (all in the repository, nothing fetched here):
  data/roster_capture_manifest_6eeab460.csv   one row per fetch; stored_path + sha256 per retained page
  data/captures/reserve_list/2026-MM/*.bin    retained raw bytes of nfl.com reserve-list pages
  data/captures/trades/2026-MM/*.bin          retained raw bytes of nfl.com trades pages
  data/s745_depth_charts.csv                  the depth register already published (club, slot, player, chart text)

Outputs:
  data/reserve_list_2026_6eeab460.csv   one row per distinct reserve-list transaction (R3)
  data/trades_2026_6eeab460.csv         one row per distinct trade line (R3)
  data/roster_events_6eeab460.csv       reserve + trade rows merged, dated, source-linked (R4)
  data/depth_versioning_6eeab460.csv    every depth-register row versioned against the roster events (R5)

Rules (the only rules applied; anything else stays blank):
  * Every value is read from the retained bytes or from the depth register. Nothing is filled in.
  * Club codes are the nfl.com club-logo code printed in the row's own From/To cell. The depth register
    writes the Rams as LAR where the official logo code is LA; that single alias is applied in the join only.
  * date_iso = the printed MM/DD with the season year from the page URL (2026). It is derived, not printed.
  * A depth row is versioned only when its chart date is printed as an explicit date in the register's own
    chart text (patterns in CHART_DATE_PATTERNS). Otherwise the row is 'undated' and nothing is inferred.
  * Name matching is exact after normalising case, punctuation and generational suffixes (D.J. = DJ).
    A player with no exact match is never matched by similarity.
"""
from __future__ import annotations

import csv
import hashlib
import html
import re
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from roster_capture_6eeab460 import MANIFEST, SEASON, KINDS  # noqa: E402  (single source of URL/schema)

OUT_RESERVE = ROOT / "data" / "reserve_list_2026_6eeab460.csv"
OUT_TRADES = ROOT / "data" / "trades_2026_6eeab460.csv"
OUT_EVENTS = ROOT / "data" / "roster_events_6eeab460.csv"
OUT_DEPTH = ROOT / "data" / "depth_versioning_6eeab460.csv"
DEPTH_REGISTER = ROOT / "data" / "s745_depth_charts.csv"

TBODY_RE = re.compile(r"<tbody[^>]*>(.*?)</tbody>", re.I | re.S)
ROW_RE = re.compile(r"<tr[^>]*>(.*?)</tr>", re.I | re.S)
CELL_RE = re.compile(r"<td[^>]*>(.*?)</td>", re.I | re.S)
TEAM_HREF_RE = re.compile(r'href="/teams/([^/"]+)/?"', re.I)
LOGO_RE = re.compile(r"clubs/logos/([A-Za-z]+)")
PLAYER_RE = re.compile(r'<a href="((?:https://www\.nfl\.com)?/players/[^"]+)"[^>]*>([^<]+)</a>', re.I)
DATE_RE = re.compile(r"^(\d{2})/(\d{2})$")

ALIAS_TO_REGISTER = {"LA": "LAR"}  # official logo code -> depth-register code (only alias needed)

CHART_DATE_PATTERNS = [
    (re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{2}|\d{4})\b"), "mdy"),
    (re.compile(r"\b(January|February|March|April|May|June|July|August|September|October|November|December|"
                r"Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\.?\s+(\d{1,2}),?\s+(\d{4})\b"), "monthname"),
]
_FULL = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october",
         "november", "december"]
MONTHS = {name: i for i, name in enumerate(_FULL, start=1)}
MONTHS.update({name[:3]: i for i, name in enumerate(_FULL, start=1)})
MONTHS["sept"] = 9
SUFFIXES = {"jr", "sr", "ii", "iii", "iv", "v"}

BASE_FIELDS = ["row_id", "season", "month", "date_printed", "date_iso", "from_club", "to_club", "player",
               "player_url", "position", "transaction", "source", "source_url", "first_capture_utc",
               "first_capture_path", "last_capture_utc", "captures_holding_row", "capture_sha256"]
PAGE_SIZE = 25  # observed: every full nfl.com transaction page holds 25 rows; a shorter last page ends the table
OUT_COVERAGE = ROOT / "data" / "roster_coverage_6eeab460.csv"
OUT_SOURCES = ROOT / "data" / "sources.csv"
SOURCE_PREFIX = {"reserve_list": "S-6E-RES", "trades": "S-6E-TRD"}


def norm_name(name: str) -> str:
    toks = re.sub(r"[^a-z ]", "", name.lower().replace(".", "")).split()
    while toks and toks[-1] in SUFFIXES:
        toks.pop()
    return "".join(toks)


def parse_page(text: str) -> list[dict]:
    """Every populated row of one page, in printed order, with printed values only."""
    out = []
    for body in TBODY_RE.findall(text):
        for raw in ROW_RE.findall(body):
            cells = CELL_RE.findall(raw)
            if len(cells) < 6:
                continue
            def club(cell: str) -> tuple[str, str]:
                slug = TEAM_HREF_RE.search(cell)
                logo = LOGO_RE.search(cell)
                return (logo.group(1).upper() if logo else ""), (slug.group(1) if slug else "")
            from_code, from_slug = club(cells[0])
            to_code, to_slug = club(cells[1])
            date_printed = html.unescape(re.sub(r"<[^>]+>", "", cells[2])).strip()
            pm = PLAYER_RE.search(cells[3])
            player = html.unescape(pm.group(2)).strip() if pm else html.unescape(re.sub(r"<[^>]+>", "", cells[3])).strip()
            player_url = ("https://www.nfl.com" + pm.group(1) if pm and pm.group(1).startswith("/") else
                          (pm.group(1) if pm else ""))
            position = html.unescape(re.sub(r"<[^>]+>", "", cells[4])).strip()
            transaction = html.unescape(re.sub(r"<[^>]+>", "", cells[5])).strip()
            out.append({"from_club": from_code, "to_club": to_code, "from_slug": from_slug, "to_slug": to_slug,
                        "date_printed": date_printed, "player": player, "player_url": player_url,
                        "position": position, "transaction": transaction})
    return out


def iso_date(printed: str, season: int) -> str:
    m = DATE_RE.match(printed)
    if not m:
        return ""
    try:
        return date(season, int(m.group(1)), int(m.group(2))).isoformat()
    except ValueError:
        return ""


def read_manifest() -> list[dict]:
    with MANIFEST.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="|"))


def collect(kind: str) -> list[dict]:
    """Distinct rows of one kind across every retained page, with the capture evidence per row."""
    rows: dict[tuple, dict] = {}
    for m in read_manifest():
        if m["kind"] != kind or not m["stored_path"]:
            continue
        path = ROOT / m["stored_path"]
        raw = path.read_bytes()
        if m["sha256"] and hashlib.sha256(raw).hexdigest() != m["sha256"]:
            raise SystemExit(f"integrity failure: {m['stored_path']} does not match its manifest sha256")
        text = raw.decode("utf-8", errors="replace")
        per_page_seen: dict[tuple, int] = {}
        for r in parse_page(text):
            base = (m["month"], r["from_club"], r["to_club"], r["date_printed"], norm_name(r["player"]),
                    r["transaction"], r["position"])
            occ = per_page_seen.get(base, 0)
            per_page_seen[base] = occ + 1
            key = base + (occ,)
            if key not in rows:
                rows[key] = {"month": m["month"], "from_club": r["from_club"], "to_club": r["to_club"],
                             "from_slug": r["from_slug"], "to_slug": r["to_slug"],
                             "date_printed": r["date_printed"], "player": r["player"], "player_url": r["player_url"],
                             "position": r["position"], "transaction": r["transaction"],
                             "source": f"{SOURCE_PREFIX[kind]}-{m['month']}",
                             "source_url": KINDS[kind].format(year=SEASON, month=int(m["month"])),
                             "captures": [], "first": m["fetch_utc"], "last": m["fetch_utc"],
                             "first_path": m["stored_path"], "first_sha": m["sha256"]}
            rec = rows[key]
            rec["captures"].append(m["sha256"][:12])
            if m["fetch_utc"] < rec["first"]:
                rec["first"], rec["first_path"], rec["first_sha"] = m["fetch_utc"], m["stored_path"], m["sha256"]
            rec["last"] = max(rec["last"], m["fetch_utc"])
    out = sorted(rows.values(), key=lambda x: (x["month"], iso_date(x["date_printed"], SEASON), x["player"],
                                               x["from_club"], x["to_club"], x["transaction"]))
    for i, rec in enumerate(out, start=1):
        rec["row_id"] = f"{'RL' if kind == 'reserve_list' else 'TR'}{SEASON}-{rec['month']}-{i:03d}"
        rec["date_iso"] = iso_date(rec["date_printed"], SEASON)
        rec["captures_holding_row"] = str(len(set(rec["captures"])))
    return out


def write(path: Path, fields: list[str], rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, delimiter="|", extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def table_rows(rows: list[dict]) -> list[dict]:
    out = []
    for r in rows:
        out.append({"row_id": r["row_id"], "season": str(SEASON), "month": f"{SEASON}-{r['month']}",
                    "date_printed": r["date_printed"], "date_iso": r["date_iso"],
                    "from_club": r["from_club"], "to_club": r["to_club"], "player": r["player"],
                    "player_url": r["player_url"], "position": r["position"], "transaction": r["transaction"],
                    "source": r["source"], "source_url": r["source_url"],
                    "first_capture_utc": r["first"], "first_capture_path": r["first_path"],
                    "last_capture_utc": r["last"], "captures_holding_row": r["captures_holding_row"],
                    "capture_sha256": r["first_sha"]})
    return out


def chart_date(text: str) -> str:
    """ISO date only when the register's chart text prints one explicitly; otherwise ''."""
    for pat, kind in CHART_DATE_PATTERNS:
        m = pat.search(text or "")
        if not m:
            continue
        try:
            if kind == "mdy":
                mo, d, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
                if y < 100:
                    y += 2000
            else:
                mo = MONTHS[m.group(1).lower()]
                d, y = int(m.group(2)), int(m.group(3))
            return date(y, mo, d).isoformat()
        except (ValueError, KeyError):
            return ""
    return ""


def depth_versioning(events: list[dict]) -> list[dict]:
    with DEPTH_REGISTER.open(newline="", encoding="utf-8") as fh:
        depth = list(csv.DictReader(fh, delimiter="|"))
    by_player: dict[str, list[dict]] = {}
    for e in events:
        by_player.setdefault(e["player_key"], []).append(e)
    out = []
    for i, d in enumerate(depth, start=1):
        club = ALIAS_TO_REGISTER.get(d["club"], d["club"])
        cdate = chart_date(d["chart_as_published"])
        key = norm_name(d["player"]) if d["player"] else ""
        relevant = []
        for e in by_player.get(key, []) if key else []:
            # departure from this club: a reserve placement by this club, or a trade out of it
            if e["club_from"] == club and e["event_type"] in ("reserve_injured", "trade"):
                relevant.append(e)
        if not d["player"]:
            status, ids = "blank_slot", ""
        elif not relevant:
            status, ids = "no_departure_in_captured_window", ""
        elif not cdate:
            status, ids = "undated_chart_cannot_version", ";".join(e["event_id"] for e in relevant)
        else:
            # Trades are permanent moves: a traded-out player still listed on a later chart is a conflict.
            # Reserve placements are not reversed in the reserve list (no activation rows are captured), so a
            # chart dated after a placement may simply post-date a return; that is reported, never called stale.
            trades_out = [e for e in relevant if e["event_type"] == "trade"]
            reserves = [e for e in relevant if e["event_type"] == "reserve_injured"]
            t_after = [e for e in trades_out if e["date_iso"] > cdate]
            t_before = [e for e in trades_out if e["date_iso"] < cdate]
            r_after = [e for e in reserves if e["date_iso"] > cdate]
            r_before = [e for e in reserves if e["date_iso"] < cdate]
            if t_after:
                status, ids = "stale_traded_out_after_chart", ";".join(e["event_id"] for e in t_after)
            elif t_before:
                status, ids = "conflict_traded_out_before_chart_still_listed", ";".join(e["event_id"] for e in t_before)
            elif r_after:
                status, ids = "candidate_reserve_placed_after_chart", ";".join(e["event_id"] for e in r_after)
            elif r_before:
                status, ids = "reserve_placed_before_chart_return_unverified", ";".join(e["event_id"] for e in r_before)
            else:
                status, ids = "same_day_as_chart_unresolved", ";".join(e["event_id"] for e in relevant)
        out.append({"depth_row": f"DR-{i:04d}", "club": d["club"], "unit": d["unit"],
                    "position_group": d["position_group"], "position_label": d["position_label"],
                    "depth": d["depth"], "player": d["player"], "chart_as_published": d["chart_as_published"],
                    "chart_date_iso": cdate, "versioning_status": status, "event_ids": ids,
                    "chart_source": d["source"]})
    return out


def chain_for(kind: str, month: str) -> list[dict]:
    """The most recent pagination chain for one kind and month: from its last page-1 fetch to the end."""
    rows_k = [m for m in read_manifest() if m["kind"] == kind and m["month"] == month]
    starts = [i for i, m in enumerate(rows_k) if m["page_seq"] == "1"]
    return rows_k[starts[-1]:] if starts else []


def coverage_rows(reserve: list[dict], trades: list[dict]) -> list[dict]:
    out = []
    for kind, rows in (("reserve_list", reserve), ("trades", trades)):
        for mo in range(1, 12):
            month = f"{mo:02d}"
            chain = chain_for(kind, month)
            distinct = sum(1 for r in rows if r["month"] == month)
            last = chain[-1] if chain else None
            if not chain:
                status, note = "not_fetched", "no capture row for this month"
            elif last["next_href"] == "" and (last["empty_state"] == "yes" or int(last["tbody_rows"] or 0) < PAGE_SIZE):
                if last["empty_state"] == "yes":
                    status, note = "complete_empty_month", "official 'No Transactions Available' block; zero rows printed"
                else:
                    status, note = "complete", f"last page holds {last['tbody_rows']} rows (< {PAGE_SIZE}) and no Next Page link"
            else:
                status = "incomplete"
                # 12 = roster_capture_6eeab460.MAX_PAGES (the cap the capture tool enforces)
                if last["page_seq"] == "1":
                    note = f"page 1 holds {PAGE_SIZE} rows and the chain was not followed further"
                elif int(last["page_seq"]) >= 12:
                    note = ("chain still open at MAX_PAGES=12: the Next Page cursor returned repeated page bytes, "
                            "and the last fetched page is full with a Next link (FL-121)")
                else:
                    note = f"last fetched page (p{last['page_seq']}) is full ({PAGE_SIZE} rows) and has a Next Page link"
            out.append({"kind": kind, "season": str(SEASON), "month": f"{SEASON}-{month}",
                        "chain_pages_fetched": str(len(chain)), "distinct_rows": str(distinct),
                        "last_page_rows": last["tbody_rows"] if last else "",
                        "last_page_next_link": "yes" if (last and last["next_href"]) else "no",
                        "coverage_status": status, "source": f"{SOURCE_PREFIX[kind]}-{month}",
                        "source_url": KINDS[kind].format(year=SEASON, month=mo), "note": note})
    return out


def write_sources(cov: list[dict]) -> None:
    """Idempotent: one registered official source per kind and month, appended if absent."""
    with OUT_SOURCES.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh, delimiter="|"))
    have = {r["id"] for r in rows}
    fields = ["id", "name", "org", "url", "kind", "tier", "accessed_utc", "used_for", "verified"]
    names = {"reserve_list": "2026 NFL Transactions — Reserve List", "trades": "2026 NFL Transactions — Trades"}
    add = []
    for c in cov:
        sid = c["source"]
        if sid in have:
            continue
        mrows = [m for m in read_manifest() if m["kind"] == c["kind"] and m["month"] == c["month"]]
        accessed = max((m["fetch_utc"] for m in mrows), default="")[:16] + "Z" if mrows else ""
        mo_name = datetime(SEASON, int(c["month"]), 1).strftime("%B")
        add.append({"id": sid, "name": f"{names[c['kind']]}, {mo_name} {SEASON} (month page)",
                    "org": "NFL.com (National Football League)", "url": c["source_url"],
                    "kind": "official-league", "tier": "A", "accessed_utc": accessed,
                    "used_for": (f"Raw-hash captures on GitHub runners (data/captures/{c['kind']}/{SEASON}-{c['month']}/); "
                                 f"{c['chain_pages_fetched']} fetch rows; coverage {c['coverage_status']}; "
                                 f"see data/roster_coverage_6eeab460.csv"),
                    "verified": "yes - retained bytes checked against manifest SHA-256 by tools/drift_alarm_6eeab460.py; "
                                "row-level parse in data/%s_2026_6eeab460.csv" % ("reserve_list" if c["kind"] == "reserve_list" else "trades")})
    if add:
        with OUT_SOURCES.open("a", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fields, delimiter="|", lineterminator="\n")
            for r in add:
                w.writerow(r)


def main() -> int:
    reserve = collect("reserve_list")
    trades = collect("trades")
    cov = coverage_rows(reserve, trades)
    write(OUT_COVERAGE, ["kind", "season", "month", "chain_pages_fetched", "distinct_rows", "last_page_rows",
                         "last_page_next_link", "coverage_status", "source", "source_url", "note"], cov)
    write_sources(cov)
    write(OUT_RESERVE, BASE_FIELDS, table_rows(reserve))
    write(OUT_TRADES, BASE_FIELDS, table_rows(trades))

    events = []
    for r in reserve:
        events.append({"event_type": "reserve_injured", "club_from": r["from_club"], "club_to": r["to_club"],
                       "player": r["player"], "player_key": norm_name(r["player"]), "transaction": r["transaction"],
                       "date_iso": r["date_iso"], "date_printed": r["date_printed"], "source": r["source"],
                       "capture_sha256": r["first_sha"], "month": f"{SEASON}-{r['month']}"})
    for r in trades:
        events.append({"event_type": "trade", "club_from": r["from_club"], "club_to": r["to_club"],
                       "player": r["player"], "player_key": norm_name(r["player"]), "transaction": r["transaction"],
                       "date_iso": r["date_iso"], "date_printed": r["date_printed"], "source": r["source"],
                       "capture_sha256": r["first_sha"], "month": f"{SEASON}-{r['month']}"})
    events.sort(key=lambda e: (e["date_iso"], e["event_type"], e["player"]))
    for i, e in enumerate(events, start=1):
        e["event_id"] = f"EV{SEASON}-{i:03d}"
    ev_fields = ["event_id", "date_iso", "event_type", "club_from", "club_to", "player", "transaction",
                 "date_printed", "source", "capture_sha256", "month"]
    write(OUT_EVENTS, ev_fields, events)

    depth = depth_versioning(events)
    write(OUT_DEPTH, ["depth_row", "club", "unit", "position_group", "position_label", "depth", "player",
                      "chart_as_published", "chart_date_iso", "versioning_status", "event_ids", "chart_source"], depth)
    print(f"reserve rows {len(reserve)} · trade rows {len(trades)} · events {len(events)} · depth rows {len(depth)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
