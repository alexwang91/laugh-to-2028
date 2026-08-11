from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RID = "BRRK-LEADERSHIP-ROTATION-0048"
SLICE = "BRRK-LEADERSHIP-ROTATION-0048-EXPOSED-HIST-V1"
EVENT = "BRRK-LEADERSHIP-ROTATION-0048-DEVELOPMENT-DATA-REGISTRATION-20260811T125700Z"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class PreregistrationContractTest(unittest.TestCase):
    def test_preregistration_is_exactly_registered_and_not_run(self):
        prereg = load(HERE / "PREREGISTRATION.json")
        registry = load(ROOT / "config" / "research_registry.json")
        matches = [r for r in registry["records"] if r.get("research_id") == RID]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0], prereg)
        self.assertEqual(prereg["result_status"], "PREREGISTERED_NOT_RUN")
        self.assertEqual(prereg["declared_variant_budget"], 1)
        self.assertEqual(prereg["actual_variants_evaluated"], 0)
        self.assertEqual(prereg["parameter_candidate_count"], 1)
        self.assertFalse(prereg["production_authorized"])
        self.assertEqual(prereg["governed_path_prefixes"], ["research/brrk_leadership_rotation_0048/"])

    def test_dataset_declaration_is_exactly_registered_and_exposed_development(self):
        declaration = load(HERE / "DATASET_DECLARATION.json")
        registry = load(ROOT / "config" / "dataset_exposure_registry.json")
        slice_matches = [x for x in registry["dataset_slices"] if x.get("dataset_slice_id") == SLICE]
        event_matches = [x for x in registry["exposure_events"] if x.get("exposure_id") == EVENT]
        self.assertEqual(slice_matches, [declaration["dataset_slice"]])
        self.assertEqual(event_matches, [declaration["exposure_event"]])
        ds = declaration["dataset_slice"]
        self.assertEqual(ds["data_budget"], "DEVELOPMENT")
        self.assertEqual(ds["contamination_state"], "RESEARCHER_EXPOSED_HISTORY")
        self.assertTrue(ds["researcher_exposed_history"])
        self.assertTrue(ds["consumed"])
        self.assertIn("d1cd28bc76f2cd8ee0486287fc50b49e5451355a3e75132a2de5b30c15af3193", ds["dataset_version"])
        self.assertEqual(ds["end"], "2026-08-02T00:00:00Z")

    def test_frozen_candidate_and_core_constants(self):
        prereg = load(HERE / "PREREGISTRATION.json")
        decisions = "\n".join(prereg["researcher_decisions"])
        expected = [
            "h in {14,28,56}",
            "K1=t-19..t",
            "Position120",
            "quote_volume",
            "lambda is fixed at 1",
            "at least 365 eligible feature-valid fully matured training origins",
            "every 28 calendar days",
            "365 matured eligible shadow prediction/outcome pairs",
            "block length 56 ordered eligible formal-evaluation observations",
            "10000 replicates",
            "seed 4292549012",
            "internal knots 0.25,0.50,0.75",
            "exactly one breakpoint",
            "at least 12 complete sequential 56-observation blocks",
            "at least 3 of 4 blocks",
            "duration at least 14 calendar observations",
            "HIGH coverage>=10%",
        ]
        for token in expected:
            self.assertIn(token, decisions)

    def test_architecture_boundaries_and_no_portfolio_translation(self):
        prereg = load(HERE / "PREREGISTRATION.json")
        text = json.dumps(prereg, sort_keys=True)
        self.assertIn("BTC is a defensive anchor", prereg["economic_mechanism"])
        self.assertIn("No same-ID portfolio weights", text)
        self.assertIn("No universe expansion to BNB, UNI, AAVE", text)
        self.assertIn("No canonical BRRK modification", text)
        self.assertFalse(prereg["production_authorized"])

    def test_implementation_stage_has_engine_but_still_no_run_or_result_files(self):
        present = {p.name for p in HERE.iterdir() if p.is_file()}
        self.assertIn("engine.py", present)
        self.assertIn("test_engine_contract.py", present)
        self.assertIn("IMPLEMENTATION_BOUNDARY.json", present)
        forbidden = {
            "run_once.py",
            "RUN_INTERFACE.json",
            "PRIMARY_RESULT.json",
            "RESULT_SUMMARY.json",
            "EXECUTION.json",
            "RUN_ONCE.marker",
            "RESULT.md",
            "portfolio.py",
            "portfolio_result.json",
        }
        self.assertTrue(forbidden.isdisjoint(present), sorted(forbidden & present))
        boundary = load(HERE / "IMPLEMENTATION_BOUNDARY.json")
        self.assertEqual(boundary["stage"], "IMPLEMENTATION_ONLY_ZERO_RESULT")
        self.assertFalse(boundary["historical_scientific_execution_authorized"])
        self.assertEqual(boundary["actual_variants_evaluated"], 0)
        self.assertEqual(boundary["result_status"], "PREREGISTERED_NOT_RUN")
        self.assertFalse(boundary["production_authorized"])

    def test_dataset_source_is_0047_hash_bound_not_new_oos(self):
        declaration = load(HERE / "DATASET_DECLARATION.json")
        ds = declaration["dataset_slice"]
        self.assertIn("IMMUTABLE_0047_MARKET_EVIDENCE", ds["source"])
        self.assertIn("not independent OOS", ds["pit_publication_semantics"])
        prereg = load(HERE / "PREREGISTRATION.json")
        self.assertIn("RESEARCHER_EXPOSED_DEVELOPMENT_HISTORY", prereg["evidence_scorecard"]["temporal_novelty"])


if __name__ == "__main__":
    unittest.main()
