"""Mutation tests for the strategy falsification companion builder."""
from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("strategy_review_builder", HERE / "build.py")
assert SPEC and SPEC.loader
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)


class StrategyReviewBuilderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.register = builder.read_register()
        cls.data = builder.read_records()

    def clone(self):
        return copy.deepcopy(self.data)

    def test_all_strategy_ids_match_once_in_register_order(self):
        rows = builder.validate(self.register, self.clone())
        self.assertEqual(len(rows), 15)
        rendered = builder.render(self.register, rows)
        self.assertEqual(builder.check_internal_links(rendered), 26)

    def test_missing_strategy_is_rejected(self):
        data = self.clone()
        data["strategies"].pop(3)
        with self.assertRaisesRegex(ValueError, "cover each strategy exactly once"):
            builder.validate(self.register, data)

    def test_duplicate_strategy_is_rejected(self):
        data = self.clone()
        data["strategies"][4] = copy.deepcopy(data["strategies"][3])
        with self.assertRaisesRegex(ValueError, "duplicate strategy IDs"):
            builder.validate(self.register, data)

    def test_changed_register_identity_is_rejected(self):
        data = self.clone()
        data["strategies"][0]["name"] = "edited label"
        with self.assertRaisesRegex(ValueError, "differs from the source strategy register"):
            builder.validate(self.register, data)

    def test_nonofficial_input_domain_is_rejected(self):
        data = self.clone()
        data["strategies"][0]["official_input_url"] = "https://example.org/injuries"
        with self.assertRaisesRegex(ValueError, "approved official host"):
            builder.validate(self.register, data)

    def test_blank_official_link_must_be_flagged(self):
        data = self.clone()
        data["strategies"][0]["official_input_url"] = ""
        data["strategies"][0]["official_source_status"] = "No details supplied"
        with self.assertRaisesRegex(ValueError, "explicitly flagged or not applicable"):
            builder.validate(self.register, data)

    def test_missing_two_sided_field_is_rejected(self):
        data = self.clone()
        del data["strategies"][0]["what_would_change_our_mind"]
        with self.assertRaisesRegex(ValueError, "missing fields"):
            builder.validate(self.register, data)

    def test_performance_metrics_are_rejected(self):
        data = self.clone()
        data["strategies"][0]["roi"] = "0.0"
        with self.assertRaisesRegex(ValueError, "performance field"):
            builder.validate(self.register, data)

    def test_dangling_local_link_is_rejected(self):
        document = '<a href="../../does-not-exist.html">broken</a>'
        with self.assertRaisesRegex(ValueError, "broken local link"):
            builder.check_internal_links(document)


if __name__ == "__main__":
    unittest.main(verbosity=2)
