import csv
import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from collectors.q51.collect import Document
from availability_monitor.capture import (
    LEDGER_FIELDS,
    LedgerError,
    append_immutable,
    build_record,
    capture_once,
    inspect_document,
    load_ledger,
)


GOOD_HTML = """
<h2>Injuries - WEEK 10</h2>
<table>
  <tr><th>Player</th><th>Position</th><th>Injuries</th><th>Practice Status</th><th>Game Status</th></tr>
  <tr><td>Example Player One</td><td>QB</td><td>Shoulder</td><td>Limited Participation in Practice</td><td>Questionable</td></tr>
  <tr><td>Example Player Two</td><td>WR</td><td></td><td>Full Participation in Practice</td><td></td></tr>
</table>
"""


def parse(html):
    doc = Document()
    doc.feed(html)
    doc.close()
    return doc


def entry(body=b"fixture", retrieved_at="2026-11-15T14:17:00Z", final_url="https://www.nfl.com/injuries/"):
    return {
        "url": "https://www.nfl.com/injuries/",
        "retrieved_at": retrieved_at,
        "status": "retrieved",
        "sha256": hashlib.sha256(body).hexdigest(),
        "final_url": final_url,
    }


class FingerprintTests(unittest.TestCase):
    def test_valid_injury_page_records_only_schema_and_aggregate_counts(self):
        summary = inspect_document(parse(GOOD_HTML))
        self.assertEqual(summary["injury_table_count"], 1)
        self.assertEqual(summary["injury_row_count"], 2)
        self.assertEqual(summary["schema_status"], "matched")
        self.assertRegex(summary["schema_sha256"], r"^[0-9a-f]{64}$")
        self.assertNotIn("Example Player One", repr(summary))

    def test_schema_fingerprint_exists_when_no_injury_table_is_detected(self):
        summary = inspect_document(parse("<table><tr><th>Different</th></tr><tr><td>x</td></tr></table>"))
        self.assertEqual(summary["injury_table_count"], 0)
        self.assertEqual(summary["schema_status"], "drift")
        self.assertRegex(summary["schema_sha256"], r"^[0-9a-f]{64}$")
        self.assertNotIn("Different", repr(summary))

    def test_unrecognized_table_cells_are_not_incorporated_into_schema_fingerprint(self):
        one = parse("<table><tr><td>Player One</td><td>Private medical note</td></tr><tr><td>A</td><td>B</td></tr></table>")
        two = parse("<table><tr><td>Player Two</td><td>Different private note</td></tr><tr><td>C</td><td>D</td></tr></table>")
        summary_one, summary_two = inspect_document(one), inspect_document(two)
        self.assertEqual(summary_one["schema_sha256"], summary_two["schema_sha256"])
        self.assertNotIn("Player One", repr(summary_one))
        self.assertNotIn("Private medical note", repr(summary_one))

    def test_header_drift_is_flagged_without_persisting_unexpected_header_text(self):
        doc = parse("""
        <table><tr><th>Player Name</th><th>Position</th><th>Injuries</th><th>Practice Status</th><th>Game Status</th></tr>
        <tr><td>Private Example</td><td>QB</td><td></td><td>Full</td><td></td></tr></table>
        """)
        summary = inspect_document(doc)
        self.assertEqual(summary["schema_status"], "drift")
        self.assertIn("NO_INJURY_TABLES", summary["conflict_flags"])
        self.assertNotIn("Private Example", repr(summary))

    def test_record_does_not_contain_player_rows_or_raw_body(self):
        body = GOOD_HTML.encode()
        record = build_record(entry(body), parse(GOOD_HTML), [])
        encoded = repr(record)
        self.assertEqual(record["raw_retained"], "no")
        self.assertEqual(record["capture_status"], "ok")
        self.assertNotIn("Example Player", encoded)
        self.assertNotIn("<table>", encoded)
        self.assertEqual(record["response_sha256"], hashlib.sha256(body).hexdigest())

    def test_changed_body_is_recorded_but_not_mistaken_for_schema_drift(self):
        old = build_record(entry(b"old"), parse(GOOD_HTML), [])
        new = build_record(entry(b"new", retrieved_at="2026-11-15T15:17:00Z"), parse(GOOD_HTML), [old])
        self.assertEqual(new["change_from_previous"], "body_changed")
        self.assertEqual(new["capture_status"], "ok")
        self.assertEqual(new["conflict_flags"], "")
        self.assertEqual(new["previous_response_sha256"], old["response_sha256"])

    def test_same_timestamp_different_hash_is_a_conflict(self):
        old = build_record(entry(b"old"), parse(GOOD_HTML), [])
        new = build_record(entry(b"new"), parse(GOOD_HTML), [old])
        self.assertIn("SAME_TIMESTAMP_DIFFERENT_HASH", new["conflict_flags"])
        self.assertEqual(new["capture_status"], "schema_drift")

    def test_schema_change_is_fail_closed_and_gets_an_alert_flag(self):
        old = build_record(entry(b"old"), parse(GOOD_HTML), [])
        changed = parse("""
        <table><tr><th>Player Name</th><th>Position</th><th>Injuries</th><th>Practice Status</th><th>Game Status</th></tr>
        <tr><td>Private Example</td><td>QB</td><td></td><td>Full</td><td></td></tr></table>
        """)
        new = build_record(entry(b"new", retrieved_at="2026-11-15T15:17:00Z"), changed, [old])
        self.assertEqual(new["change_from_previous"], "schema_changed")
        self.assertEqual(new["capture_status"], "schema_drift")
        self.assertIn("SCHEMA_CHANGED_FROM_PREVIOUS", new["conflict_flags"])
        self.assertNotIn("Private Example", repr(new))

    def test_schema_fingerprint_change_is_detected_even_with_same_response_hash(self):
        old = build_record(entry(b"same"), parse(GOOD_HTML), [])
        changed = parse("""
        <table><tr><th>Player Name</th><th>Position</th><th>Injuries</th><th>Practice Status</th><th>Game Status</th></tr>
        <tr><td>Private Example</td><td>QB</td><td></td><td>Full</td><td></td></tr></table>
        """)
        new = build_record(entry(b"same", retrieved_at="2026-11-15T15:17:00Z"), changed, [old])
        self.assertEqual(new["response_sha256"], old["response_sha256"])
        self.assertEqual(new["change_from_previous"], "schema_changed")
        self.assertEqual(new["capture_status"], "schema_drift")

    def test_redirect_change_is_a_conflict_not_a_silent_success(self):
        old = build_record(entry(b"old"), parse(GOOD_HTML), [])
        redirected = entry(b"new", retrieved_at="2026-11-15T15:17:00Z",
                           final_url="https://www.nfl.com/injuries/league/2026/reg10")
        new = build_record(redirected, parse(GOOD_HTML), [old])
        self.assertIn("FINAL_URL_CHANGED", new["conflict_flags"])
        self.assertEqual(new["capture_status"], "schema_drift")

    def test_final_url_query_and_fragment_are_removed(self):
        observed = entry(final_url="https://www.nfl.com/injuries/?player=PrivateExample#section")
        record = build_record(observed, parse(GOOD_HTML), [])
        self.assertEqual(record["final_url"], "https://www.nfl.com/injuries/")
        self.assertNotIn("PrivateExample", repr(record))

    def test_fetch_failure_has_no_fabricated_hash_or_row_counts(self):
        failed = {
            "url": "https://www.nfl.com/injuries/",
            "retrieved_at": "2026-11-15T14:17:00Z",
            "status": "failed",
            "error": "robots access denied",
        }
        record = build_record(failed, None, [])
        self.assertEqual(record["capture_status"], "failed")
        self.assertEqual(record["response_sha256"], "")
        self.assertEqual(record["injury_row_count"], "")
        self.assertIn("FETCH_FAILED", record["conflict_flags"])
        self.assertEqual(record["error"], "robots_access_denied")
        self.assertNotIn("robots access denied", repr(record))
        self.assertEqual(record["raw_retained"], "no")

    def test_parse_failure_keeps_only_a_valid_response_digest(self):
        body = b"private response bytes that are not retained"
        failed = entry(body)
        failed.update(status="failed", error="parser rejected response")
        record = build_record(failed, None, [])
        self.assertEqual(record["capture_status"], "failed")
        self.assertEqual(record["response_sha256"], hashlib.sha256(body).hexdigest())
        self.assertEqual(record["schema_sha256"], "")
        self.assertEqual(record["injury_table_count"], "")
        self.assertEqual(record["injury_row_count"], "")
        self.assertEqual(record["error"], "fetch_error")
        self.assertNotIn(body.decode(), repr(record))

    def test_capture_discards_body_and_never_enables_raw_storage(self):
        class FakeCollector:
            instances = []

            def __init__(self, out, raw_dir=None, delay=1.1):
                self.temp_dir = out
                self.raw_dir = raw_dir
                self.instances.append(self)

            def fetch(self, url, kind):
                return GOOD_HTML, parse(GOOD_HTML), entry(GOOD_HTML.encode())

        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "ledger.csv"
            with patch("availability_monitor.capture.Collector", FakeCollector):
                record, appended = capture_once(path, delay=0)
            self.assertTrue(appended)
            self.assertIsNone(FakeCollector.instances[-1].raw_dir)
            self.assertEqual(record["raw_retained"], "no")
            self.assertEqual(list(Path(td).iterdir()), [path])
            ledger_text = path.read_text(encoding="utf-8")
            self.assertNotIn("Example Player", ledger_text)
            self.assertNotIn("<table>", ledger_text)

    def test_ledger_is_append_only_and_identical_retry_is_idempotent(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "ledger.csv"
            record = build_record(entry(), parse(GOOD_HTML), [])
            self.assertTrue(append_immutable(path, record))
            original = path.read_bytes()
            self.assertFalse(append_immutable(path, record))
            self.assertEqual(path.read_bytes(), original)
            changed = dict(record)
            changed["injury_row_count"] = "999"
            with self.assertRaises(LedgerError):
                append_immutable(path, changed)
            with path.open(encoding="utf-8", newline="") as fh:
                self.assertEqual(tuple(next(csv.reader(fh, delimiter="|"))), LEDGER_FIELDS)
            self.assertEqual(len(load_ledger(path)), 1)
            self.assertEqual(path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
