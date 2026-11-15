#!/usr/bin/env python3
"""Capture a metadata-only fingerprint of the official NFL injury hub.

The HTTP response is hashed in memory and discarded. This program persists only
retrieval metadata, the raw-response SHA-256, aggregate table/row counts, and a
schema fingerprint. It deliberately does not retain or publish player rows or
raw page bytes; a digest alone is not sufficient for point-in-time replay.

The fetch uses the existing robots-aware, host-allowlisted collector. The
scheduled workflow treats a failed fetch or schema drift as an error and raises
an issue; the ledger row is retained for audit when possible.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit
from typing import Iterable

from collectors.q51.collect import Collector

SOURCE_URL = "https://www.nfl.com/injuries/"
EXPECTED_HEADERS = ("Player", "Position", "Injuries", "Practice Status", "Game Status")
LEDGER_FIELDS = (
    "capture_id",
    "retrieved_at_utc",
    "source_url",
    "final_url",
    "response_sha256",
    "injury_table_count",
    "injury_row_count",
    "schema_sha256",
    "schema_status",
    "previous_response_sha256",
    "change_from_previous",
    "conflict_flags",
    "raw_retained",
    "capture_status",
    "error",
    "source",
)
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class LedgerError(ValueError):
    """The append-only ledger is malformed or an existing capture would change."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _clean_error(value: object) -> str:
    """Map fetch exceptions to fixed codes; never publish untrusted exception text."""
    text = " ".join(str(value or "").casefold().split())
    if "robots.txt disallows" in text:
        return "robots_disallowed"
    if "robots access denied" in text:
        return "robots_access_denied"
    if "response exceeds size limit" in text:
        return "response_size_limit"
    if "host not in official allowlist" in text or "redirect outside official allowlist" in text \
            or "final redirect outside allowlist" in text:
        return "official_host_validation_failed"
    if "timed out" in text or "timeout" in text:
        return "fetch_timeout"
    return "fetch_error"


def _safe_final_url(value: object) -> str | None:
    """Keep only the official HTTPS host and path; drop query strings and fragments."""
    if not value:
        return ""
    try:
        parsed = urlsplit(str(value))
        hostname = parsed.hostname
    except ValueError:
        return None
    if parsed.scheme != "https" or hostname != "www.nfl.com":
        return None
    return "https://www.nfl.com" + (parsed.path or "/")


def _is_candidate_header(header: Iterable[str]) -> bool:
    labels = {str(cell).strip().casefold() for cell in header if str(cell).strip()}
    return "player" in labels or ("position" in labels and "injuries" in labels)


def inspect_document(doc) -> dict[str, object]:
    """Return counts and a schema digest only; never return names or cell contents."""
    candidates: list[tuple[str, ...]] = []
    schema_signatures: list[list[object]] = []
    matching = []
    malformed = 0
    row_count = 0
    expected = tuple(x.casefold() for x in EXPECTED_HEADERS)

    for table in getattr(doc, "tables", []):
        rows = table.get("rows", [])
        if not rows:
            continue
        header = tuple(str(x).strip() for x in rows[0].get("cells", []))
        row_widths = sorted({len(row.get("cells", [])) for row in rows})
        if _is_candidate_header(header):
            candidates.append(header)
            # Header names are schema metadata; body-cell values are never hashed
            # as a fallback when a recognizable header is absent.
            schema_signatures.append(["headers", list(header), row_widths])
        else:
            # A changed or missing header still changes the structural fingerprint
            # without folding a player name or any other cell value into the digest.
            schema_signatures.append(["table_shape", len(header), row_widths])
        if tuple(x.casefold() for x in header) == expected:
            matching.append(table)
            for row in rows[1:]:
                cells = row.get("cells", [])
                if len(cells) != len(EXPECTED_HEADERS):
                    malformed += 1
                if any(str(cell).strip() for cell in cells):
                    row_count += 1

    # Only schema headers and table-shape counts are fingerprinted. Cell contents
    # are never persisted or hashed individually, even if an expected header vanishes.
    schema_signatures.sort(key=lambda signature: json.dumps(signature, ensure_ascii=False, separators=(",", ":")))
    schema_payload = json.dumps(
        schema_signatures,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    schema_sha256 = hashlib.sha256(schema_payload).hexdigest()
    flags: list[str] = []
    if not matching:
        flags.append("NO_INJURY_TABLES")
    if any(tuple(x.casefold() for x in header) != expected for header in candidates):
        flags.append("UNEXPECTED_INJURY_HEADERS")
    if malformed:
        flags.append("ROW_WIDTH_MISMATCH")
    schema_status = "matched" if not flags else "drift"
    return {
        "injury_table_count": len(matching),
        "injury_row_count": row_count,
        "schema_sha256": schema_sha256,
        "schema_status": schema_status,
        "conflict_flags": flags,
    }


def load_ledger(path: str | Path) -> list[dict[str, str]]:
    path = Path(path)
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="|")
        if tuple(reader.fieldnames or ()) != LEDGER_FIELDS:
            raise LedgerError("ledger header does not match the pinned schema")
        records = list(reader)
    for index, row in enumerate(records, start=2):
        if None in row or any(value is None for value in row.values()):
            raise LedgerError(f"ledger row {index} has the wrong field count")
    return records


def _prior_successful(history: list[dict[str, str]], source_url: str) -> dict[str, str] | None:
    eligible = [
        row for row in history
        if row.get("source_url") == source_url
        and row.get("capture_status") in {"ok", "schema_drift"}
        and row.get("response_sha256")
    ]
    return max(eligible, key=lambda row: row.get("retrieved_at_utc", ""), default=None)


def build_record(entry: dict, doc, history: list[dict[str, str]], source_url: str = SOURCE_URL) -> dict[str, str]:
    retrieved_at = str(entry.get("retrieved_at") or utc_now())
    raw_final_url = str(entry.get("final_url") or "")
    final_url = _safe_final_url(raw_final_url)
    response_sha256 = str(entry.get("sha256") or "")
    flags: list[str] = []
    if raw_final_url and final_url is None:
        flags.append("FINAL_URL_INVALID")
        final_url = ""
    error = ""

    digest_valid = bool(SHA256_RE.fullmatch(response_sha256))
    if entry.get("status") != "retrieved" or doc is None or not digest_valid:
        if not digest_valid:
            response_sha256 = ""
        schema = {
            "injury_table_count": "",
            "injury_row_count": "",
            "schema_sha256": "",
            "schema_status": "unavailable",
            "conflict_flags": ["FETCH_FAILED"],
        }
        flags.extend(schema["conflict_flags"])
        error = _clean_error(entry.get("error") or "official source fetch failed")
    else:
        schema = inspect_document(doc)
        flags.extend(schema["conflict_flags"])

    prior = _prior_successful(history, source_url)
    previous_hash = prior.get("response_sha256", "") if prior else ""
    if final_url and prior and final_url != prior.get("final_url", ""):
        flags.append("FINAL_URL_CHANGED")
    if entry.get("status") != "retrieved" or doc is None or not response_sha256:
        change = "fetch_failed"
        capture_status = "failed"
    elif prior is None:
        change = "first_capture"
        capture_status = "ok" if schema["schema_status"] == "matched" and not flags else "schema_drift"
    elif response_sha256 == previous_hash and schema["schema_sha256"] == prior.get("schema_sha256", ""):
        change = "unchanged"
        capture_status = "ok" if schema["schema_status"] == "matched" and not flags else "schema_drift"
    elif schema["schema_sha256"] != prior.get("schema_sha256", ""):
        change = "schema_changed"
        flags.append("SCHEMA_CHANGED_FROM_PREVIOUS")
        capture_status = "schema_drift"
    else:
        change = "body_changed"
        capture_status = "ok" if schema["schema_status"] == "matched" and not flags else "schema_drift"

    for old in history:
        if old.get("source_url") == source_url and old.get("retrieved_at_utc") == retrieved_at:
            if old.get("response_sha256", "") != response_sha256:
                flags.append("SAME_TIMESTAMP_DIFFERENT_HASH")
                capture_status = "schema_drift"

    # Stable order and unique values make the ledger byte-reproducible for a given observation.
    flags = sorted(set(flags))
    id_time = retrieved_at.replace("-", "").replace(":", "")
    if response_sha256:
        short_hash = response_sha256[:12]
    else:
        failure_key = "|".join((source_url, retrieved_at, error)).encode("utf-8")
        short_hash = hashlib.sha256(failure_key).hexdigest()[:12]
    capture_id = f"{id_time}-{short_hash}"
    return {
        "capture_id": capture_id,
        "retrieved_at_utc": retrieved_at,
        "source_url": source_url,
        "final_url": final_url,
        "response_sha256": response_sha256,
        "injury_table_count": str(schema["injury_table_count"]),
        "injury_row_count": str(schema["injury_row_count"]),
        "schema_sha256": str(schema["schema_sha256"]),
        "schema_status": str(schema["schema_status"]),
        "previous_response_sha256": previous_hash,
        "change_from_previous": change,
        "conflict_flags": ";".join(flags),
        "raw_retained": "no",
        "capture_status": capture_status,
        "error": error,
        "source": source_url,
    }


def append_immutable(path: str | Path, record: dict[str, str]) -> bool:
    """Append exactly once. Existing capture IDs may never be rewritten.

    Returns False when an identical record is already present. Any attempt to
    replace an existing capture with different fields raises LedgerError.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    history = load_ledger(path)
    for old in history:
        if old["capture_id"] == record["capture_id"]:
            if old == record:
                return False
            raise LedgerError(f"capture {record['capture_id']} already exists with different values")
    new_file = not path.exists() or path.stat().st_size == 0
    with path.open("a", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=LEDGER_FIELDS, delimiter="|", lineterminator="\n")
        if new_file:
            writer.writeheader()
        writer.writerow({field: record.get(field, "") for field in LEDGER_FIELDS})
    return True


def _error_entry(url: str, exc: Exception) -> dict[str, str]:
    return {
        "url": url,
        "retrieved_at": utc_now(),
        "status": "failed",
        "error": _clean_error(exc),
    }


def capture_once(ledger_path: str | Path, url: str = SOURCE_URL, delay: float = 1.1) -> tuple[dict[str, str], bool]:
    """Fetch, fingerprint, and append one row; never persist the response body."""
    history = load_ledger(ledger_path)
    try:
        # The collector's raw_dir is intentionally omitted. Its HTTP response is
        # hashed in memory and is never written to disk or uploaded as an artifact.
        with tempfile.TemporaryDirectory(prefix="nfl2-availability-fp-") as tmp:
            collector = Collector(out=tmp, raw_dir=None, delay=delay)
            text, doc, entry = collector.fetch(url, "injuries")
            del text
    except Exception as exc:  # preserve a failed attempt as a dated ledger row
        doc = None
        entry = _error_entry(url, exc)
    record = build_record(entry, doc, history, source_url=url)
    appended = append_immutable(ledger_path, record)
    return record, appended


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", default="data/availability_fingerprints.csv")
    parser.add_argument("--url", default=SOURCE_URL)
    parser.add_argument("--delay", type=float, default=1.1)
    args = parser.parse_args(argv)
    if args.url != SOURCE_URL:
        parser.error("source URL is pinned to the official NFL injury hub")
    try:
        record, appended = capture_once(args.ledger, args.url, args.delay)
    except Exception as exc:
        print(f"availability fingerprint ledger error: {_clean_error(exc)}", file=sys.stderr)
        return 2
    print(json.dumps({
        "capture_id": record["capture_id"],
        "retrieved_at_utc": record["retrieved_at_utc"],
        "response_sha256": record["response_sha256"] or None,
        "injury_table_count": record["injury_table_count"] or None,
        "injury_row_count": record["injury_row_count"] or None,
        "schema_status": record["schema_status"],
        "change_from_previous": record["change_from_previous"],
        "conflict_flags": record["conflict_flags"],
        "raw_retained": record["raw_retained"],
        "appended": appended,
    }, sort_keys=True))
    if record["change_from_previous"] in {"body_changed", "schema_changed"}:
        print("::notice::Official NFL injury-hub response changed; see the append-only fingerprint ledger.")
    if record["capture_status"] != "ok":
        print("::error::Official injury-hub capture failed or its schema changed; see the ledger and the alert issue.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
