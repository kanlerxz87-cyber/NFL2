#!/usr/bin/env python3
"""Regression checks for the canonical decision-readiness table.

Run after ``python tools/build_site.py``. This checks that the landing page renders
exactly the current requirements register, that each row retains its project-brief
source label, and that project-design requirements are not presented as official NFL
facts. It also guards the separate 10-chart injury join / 31-of-32 chart-transcription
coverage figures against accidental conflation.
"""
from __future__ import annotations

import csv
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


class CheckError(Exception):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CheckError(message)


def load_pipe(name: str) -> list[dict[str, str]]:
    path = DATA / name
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="|"))
    require(bool(rows), f"{name}: missing header or data rows")
    return rows


class TableParser(HTMLParser):
    """Collect table cells and links, without depending on a third-party parser."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tables: list[list[list[dict[str, object]]]] = []
        self.table: list[list[dict[str, object]]] | None = None
        self.row: list[dict[str, object]] | None = None
        self.cell: dict[str, object] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "table" and self.table is None:
            self.table = []
        elif tag == "tr" and self.table is not None:
            self.row = []
        elif tag in ("th", "td") and self.row is not None:
            self.cell = {"text": [], "hrefs": []}
        elif tag == "a" and self.cell is not None:
            href = dict(attrs).get("href")
            if href:
                self.cell["hrefs"].append(href)  # type: ignore[union-attr]

    def handle_data(self, data: str) -> None:
        if self.cell is not None:
            self.cell["text"].append(data)  # type: ignore[union-attr]

    def handle_endtag(self, tag: str) -> None:
        if tag in ("th", "td") and self.cell is not None and self.row is not None:
            self.cell["text"] = " ".join("".join(self.cell["text"]).split())  # type: ignore[arg-type]
            self.row.append(self.cell)
            self.cell = None
        elif tag == "tr" and self.row is not None and self.table is not None:
            self.table.append(self.row)
            self.row = None
        elif tag == "table" and self.table is not None:
            self.tables.append(self.table)
            self.table = None


def cell_text(cell: dict[str, object]) -> str:
    return str(cell["text"])


def verify_register_and_gates() -> tuple[list[dict[str, str]], set[str]]:
    reqs = load_pipe("requirements.csv")
    gates = load_pipe("gates.csv")
    req_header = set(reqs[0])
    required = {"id", "requirement", "status", "blocks", "clears_with"}
    require(required <= req_header,
            f"requirements.csv missing fields: {sorted(required - req_header)}")
    ids = [r["id"].strip() for r in reqs]
    require(all(ids), "requirements.csv contains an empty requirement ID")
    require(len(ids) == len(set(ids)), "requirements.csv contains duplicate requirement IDs")

    gate_ids = {g["id"].strip() for g in gates}
    require(len(gate_ids) == len(gates), "gates.csv contains duplicate gate IDs")
    for row in reqs:
        require(row["blocks"].strip() and row["clears_with"].strip(),
                f"{row['id']}: blocks/clears_with must be explicit (use an em dash if none)")
        if row["blocks"].strip() == "—":
            continue
        refs = re.findall(r"G-\d{2}", row["blocks"])
        residue = re.sub(r"G-\d{2}", "", row["blocks"]).strip(" /,;")
        require(bool(refs) and not residue,
                f"{row['id']}: malformed gate mapping {row['blocks']!r}")
        missing = sorted(set(refs) - gate_ids)
        require(not missing, f"{row['id']}: unknown gate IDs {missing}")

    by_id = {r["id"]: r for r in reqs}
    hard_gate_ids = {g["id"].strip() for g in gates if g["class"].strip().lower() == "hard"}
    require(hard_gate_ids == set(re.findall(r"G-\d{2}", by_id["R-15"]["blocks"])),
            "R-15 must name every hard gate; update its scope if the gate register changes")
    require(by_id["R-16"]["blocks"].strip() == "—" and
            by_id["R-43"]["blocks"].strip() == "—",
            "R-16/R-43 must not map descriptive correlation to calibration or CLV gates")
    for rid in ("R-20", "R-21", "R-44"):
        require(set(re.findall(r"G-\d{2}", by_id[rid]["blocks"])) == {"G-02", "G-03"},
                f"{rid}: personnel coverage should map to join integrity and point-in-time correctness")

    brief = {row["id"]: row for row in load_pipe("sources.csv")}.get("S-BRIEF")
    require(brief is not None, "sources.csv is missing S-BRIEF")
    require(brief["kind"] == "owner-instruction" and brief["tier"] == "C",
            "S-BRIEF must remain classified as owner instruction, not an official NFL source")
    require("requirements.csv" in brief["url"], "S-BRIEF source link must point to the durable register")
    return reqs, gate_ids


def verify_coverage_disclosure() -> tuple[int, int, int, int]:
    relief = load_pipe("personnel_relief_club_83246f00.csv")
    relief_clubs = {r["club"] for r in relief if r["chart_url"].startswith("https://")}
    resolved = sum(int(r["resolved_to_chart"] or "0") for r in relief)
    filings = sum(int(r["listed"] or "0") for r in relief)

    summary = load_pipe("s745_depth_summary.csv")
    charted = {r["club"] for r in summary if r["chart_published"].strip().lower() == "yes"}
    require(len(summary) == 32, f"S745 summary should represent 32 clubs, found {len(summary)}")
    require("HOU" in {r["club"] for r in summary} and "HOU" not in charted,
            "S745 coverage must preserve Houston as the untranscribed club")
    chart_rows = load_pipe("s745_depth_charts.csv")
    slot_clubs = {r["club"] for r in chart_rows}
    require(slot_clubs == charted,
            "S745 chart-slot rows and chart_published summary clubs do not match")

    require(len(relief_clubs) == 10,
            f"10-chart personnel-relief join drifted: found {len(relief_clubs)} chart URLs")
    require(resolved == 85 and filings == 296,
            f"dated personnel-relief join drifted: {resolved}/{filings}, expected 85/296")
    require(len(charted) == 31,
            f"S745 chart transcription should be 31/32, found {len(charted)}/32")

    index_md = (ROOT / "content" / "index.md").read_text(encoding="utf-8").lower()
    req_md = (ROOT / "content" / "requirements.md").read_text(encoding="utf-8").lower()
    for label, text in (("content/index.md", index_md), ("content/requirements.md", req_md)):
        for needle in ("not official nfl facts", "not an nfl-published", "31 of 32", "10-chart"):
            require(needle in text, f"{label}: missing project-source/coverage disclosure {needle!r}")
    plain_index = re.sub(r"[*_`]+", "", index_md)
    require("does not establish 31/32" in plain_index,
            "landing page must explicitly say 31/32 chart transcription does not prove 31/32 starter joins")
    require(str(resolved) in index_md and str(filings) in index_md and str(len(relief_clubs)) in index_md,
            "landing page's personnel-relief counts do not match its dated source data")
    require(str(len(charted)) in index_md and "houston" in index_md,
            "landing page's separate chart-transcription coverage disclosure is incomplete")
    return len(relief_clubs), resolved, filings, len(charted)


def verify_landing_table(reqs: list[dict[str, str]]) -> None:
    directive = "csv data/requirements.csv"
    index_md = (ROOT / "content" / "index.md").read_text(encoding="utf-8")
    require(directive in index_md, "content/index.md no longer renders data/requirements.csv")
    require("source=S-BRIEF" in index_md, "landing requirements table lost its S-BRIEF source")
    for disclosure in ("not official NFL facts", "not verified by an NFL source"):
        require(disclosure.lower() in index_md.lower(),
                f"landing page missing required source-class disclosure: {disclosure}")

    html_path = ROOT / "index.html"
    require(html_path.exists(), "index.html is missing; run tools/build_site.py first")
    parser = TableParser()
    parser.feed(html_path.read_text(encoding="utf-8"))
    target = None
    for table in parser.tables:
        if not table:
            continue
        headers = [cell_text(cell) for cell in table[0]]
        if headers[:6] == ["ID", "Requirement", "Origin", "Status", "Gate that blocks it", "Number that clears it"]:
            target = table
            break
    require(target is not None, "built index.html has no decision-readiness table with expected columns")

    headers = [cell_text(cell) for cell in target[0]]
    require(headers == ["ID", "Requirement", "Origin", "Status", "Gate that blocks it", "Number that clears it", "Source"],
            f"landing table columns drifted: {headers}")
    body = target[1:]
    require(len(body) == len(reqs),
            f"landing table has {len(body)} rows but requirements.csv has {len(reqs)}")
    expected_ids = [row["id"].strip() for row in reqs]
    actual_ids = [cell_text(row[0]) for row in body if row]
    require(actual_ids == expected_ids,
            "landing table requirement IDs/order do not exactly match requirements.csv")
    by_id = {r["id"].strip(): r for r in reqs}
    for row in body:
        require(len(row) == len(headers), f"landing row has {len(row)} cells, expected {len(headers)}")
        rid = cell_text(row[0])
        require(cell_text(row[2]) == by_id[rid]["raised_in"],
                f"{rid}: landing Origin does not match requirements.csv")
        source = cell_text(row[6]).lower()
        require("owner project brief" in source and "owner-instruction" in source,
                f"{rid}: source cell must label the owner-instruction register reference")
        hrefs = row[6]["hrefs"]
        require(any("/data/requirements.csv" in str(href) for href in hrefs),
                f"{rid}: source cell has no link to the durable requirement register")


def main() -> int:
    try:
        reqs, gate_ids = verify_register_and_gates()
        relief_clubs, resolved, filings, charted = verify_coverage_disclosure()
        verify_landing_table(reqs)
    except (CheckError, KeyError, ValueError, OSError, csv.Error) as exc:
        print(f"FAIL decision-readiness coverage: {exc}", file=sys.stderr)
        return 1

    print("PASS decision-readiness source class: all landing rows link to S-BRIEF as owner instruction, not NFL evidence")
    print(f"PASS gate map: {len(gate_ids)} registered gates; all requirement references valid and correlation exceptions explicit")
    print(f"PASS depth coverage distinction: {relief_clubs} chart URLs / {resolved} of {filings} filings joined vs {charted} of 32 S745 chart pages transcribed")
    print(f"PASS landing coverage: all {len(reqs)} requirement IDs render once, in register order, with gate, clearing and source columns")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
