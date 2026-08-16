from __future__ import annotations

import unittest

from research.brrk_btc_sol_path_event_early_warning_execution_assured_0069 import engine
from research.brrk_btc_sol_path_event_execution_equivalence_0068 import execution_graph as graph


SCI_ARCH = {
    "P01": "P01_FAMILY_RIDGE_LOGIT",
    "P02": "P02_RAW_ELASTIC_NET_LOGIT",
    "P03": "P03_VALIDATION_SCREENED_SIGNAL_LOGIT",
    "P04": "P04_PCR_LOGIT",
    "P05": "P05_THEORY_QUADRATIC_LOGIT",
    "P06": "P06_SHALLOW_GBDT_CLASSIFIER",
}
SCI_TARGET = {
    "ANY_DOWN": "T1_ANY_DOWN",
    "MAJOR_DOWN": "T2_MAJOR_DOWN",
    "ANY_SIDEWAYS": "T3_ANY_SIDEWAYS",
    "LONG_SIDEWAYS": "T4_LONG_SIDEWAYS",
}


def selected_from_graph(nh, p07, p08):
    out = {}
    for asset, target, horizon, arch in nh:
        out[(SCI_ARCH[arch], asset, SCI_TARGET[target], horizon)] = {"qualification": True}
    for asset, target in p07:
        for horizon in graph.HORIZONS:
            out[("P07_DISCRETE_TIME_HAZARD_LOGIT", asset, SCI_TARGET[target], horizon)] = {"qualification": True}
    for asset, target, horizon in p08:
        out[("P08_STACKED_PROBABILITY_ENSEMBLE", asset, SCI_TARGET[target], horizon)] = {"stack_weights": {"qualification": 1.0}}
    return out


class ExecutionAssuranceTests(unittest.TestCase):
    def test_full_support_manifest_matches_0068_geometry(self):
        selected = selected_from_graph(graph.all_nonhazard_keys(), graph.all_p07_keys(), graph.all_p08_keys())
        actual = engine._manifest_from_selected_params(selected)
        expected = graph.build_downstream_manifest(graph.all_nonhazard_keys(), graph.all_p07_keys(), graph.all_p08_keys())
        self.assertEqual(actual["canonical_bytes"], expected["canonical_bytes"])
        self.assertEqual(actual["sha256"], expected["sha256"])
        self.assertEqual(actual["expected_economic_fit_calls"], 11904)
        self.assertEqual(actual["expected_p08_nnls_solves"], 40)

    def test_partial_support_is_manifest_derived(self):
        nh = list(graph.all_nonhazard_keys())[::2]
        p07 = list(graph.all_p07_keys())[::2]
        p08 = list(graph.all_p08_keys())[::2]
        manifest = engine._manifest_from_selected_params(selected_from_graph(nh, p07, p08))
        self.assertEqual(manifest["expected_economic_fit_calls"], 5952)
        self.assertEqual(manifest["expected_p08_nnls_solves"], 20)

    def test_runtime_accounting_releases_barrier_only_on_exact_match(self):
        manifest = graph.build_downstream_manifest(
            list(graph.all_nonhazard_keys())[::2],
            list(graph.all_p07_keys())[::2],
            list(graph.all_p08_keys())[::2],
        )
        tuning = {"__runtime__": {"fit_call_attempts": 31008, "nnls_solves": 20}}
        evaluation = {"__runtime__": {"fit_call_attempts": 5952}}
        evidence = engine._runtime_accounting(tuning, evaluation, manifest)
        self.assertTrue(evidence["inference_barrier_released"])
        self.assertTrue(evidence["terminal_trace_complete"])
        self.assertEqual(evidence["terminal_trace_count"], evidence["manifest_unit_count"])

    def test_runtime_accounting_fails_closed(self):
        manifest = graph.build_downstream_manifest(
            list(graph.all_nonhazard_keys())[::2],
            list(graph.all_p07_keys())[::2],
            list(graph.all_p08_keys())[::2],
        )
        with self.assertRaises(engine.ExecutionAssuranceError):
            engine._runtime_accounting(
                {"__runtime__": {"fit_call_attempts": 31008, "nnls_solves": 20}},
                {"__runtime__": {"fit_call_attempts": 11904}},
                manifest,
            )


if __name__ == "__main__":
    unittest.main()
