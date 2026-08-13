import importlib.util
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("run0061", HERE / "run_once.py")
R = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(R)
S = R.schema()
TARGETS = S["target_keys"]
ORIGIN_FIELDS = S["origin_panel_fields"]
FIXED_FIELDS = S["fixed_score_panel_fields"]


def origin_rows(n):
    rows = []
    numeric = [k for k in ORIGIN_FIELDS if k not in ("origin_date", "chronological_block_id")]
    for i in range(n):
        row = {k: float(i + 1) for k in numeric}
        row["origin_date"] = f"{2020 + i // 365:04d}-{1 + (i % 365) // 31:02d}-{1 + (i % 28):02d}"
        row["chronological_block_id"] = 1 + min(3, (4 * i) // max(1, n))
        rows.append(row)
    rows.sort(key=lambda x: x["origin_date"])
    for i, row in enumerate(rows):
        row["origin_date"] = f"D{i:05d}"
    return rows


def diagnostics():
    return {
        "axis_target_spearman": {a: {k: 0.1 for k in TARGETS} for a in ("A1", "A2", "A3")},
        "axis_redundancy_matrix": [[1.0, 0.2, 0.1], [0.2, 1.0, 0.3], [0.1, 0.3, 1.0]],
        "axis_eigenvalues": [0.7, 0.9, 1.4],
        "axis_effective_rank": 2.8,
        "terminal_positive_rate_by_horizon": {"20": 0.4, "60": 0.5, "120": 0.6, "240": 0.7},
    }


def result(stage):
    n = 1000 if stage == "G1" else 1500
    rows = origin_rows(n)
    nulls = {k: None for k in TARGETS}
    full = dict(nulls)
    temporal = {str(b): dict(nulls) for b in range(1, 5)}
    fixed = dict(nulls)
    lcb = dict(nulls)
    gates = {"G0": True, "G1": n >= 1440, "G2": None, "G3": None, "G4": None}
    cls = R.scientific_engine.CLASS_SUPPORT
    tp = None
    eq = None
    q95 = None
    fixed_panel = None
    reason = "G2_G3_G4_NOT_EVALUATED_DUE_TO_G1_SUPPORT_FAILURE"
    if stage in ("G2", "G3", "G4_FAIL", "PASS"):
        full = {k: 0.2 for k in TARGETS}
        if stage == "G2":
            full[TARGETS[0]] = None
            gates["G2"] = False
            cls = R.scientific_engine.CLASS_INFO
            reason = "G3_G4_NOT_EVALUATED_DUE_TO_G2_NO_JOINT_DOWNSIDE_INFORMATION"
        else:
            gates["G2"] = True
            temporal = {str(b): {k: 0.2 for k in TARGETS} for b in range(1, 5)}
            tp = 2 if stage == "G3" else 4
            if stage == "G3":
                for b in ("3", "4"):
                    temporal[b][TARGETS[0]] = -0.1
                gates["G3"] = False
                cls = R.scientific_engine.CLASS_TEMPORAL
                reason = "G4_NOT_EVALUATED_DUE_TO_G3_TEMPORAL_INSTABILITY"
            else:
                gates["G3"] = True
                fixed = {k: 0.2 for k in TARGETS}
                eq = 0.0
                q95 = 0.1
                lcb = {k: (0.05 if stage == "PASS" else -0.05) for k in TARGETS}
                gates["G4"] = stage == "PASS"
                cls = R.scientific_engine.CLASS_PASS if stage == "PASS" else R.scientific_engine.CLASS_DEP
                reason = None
                fixed_panel = []
                for i, row in enumerate(rows):
                    x = {k: float(i + 1) for k in FIXED_FIELDS if k != "origin_date"}
                    x["origin_date"] = row["origin_date"]
                    fixed_panel.append(x)
    d = diagnostics()
    return {
        "schema_version": 1,
        "research_id": R.scientific_engine.RESEARCH_ID,
        "upstream_research_id": R.scientific_engine.UPSTREAM_RESEARCH_ID,
        "dataset_slice_ref": R.scientific_engine.DATASET_SLICE_REF,
        "payload_sha256": R.scientific_engine.EXPECTED_PAYLOAD_SHA256,
        "classification": cls,
        "gates": gates,
        "shared_origin_count": n,
        "shared_origin_start": rows[0]["origin_date"],
        "shared_origin_end": rows[-1]["origin_date"],
        "full_sample_rho_by_target": full,
        "temporal_block_rho_by_target": temporal,
        "temporal_positive_block_count": tp,
        "fixed_score_observed_by_target": fixed,
        "spearman_equivalence_max_abs_error": eq,
        "bootstrap_q95": q95,
        "simultaneous_lcb_by_target": lcb,
        "downstream_not_evaluated_reason": reason,
        **d,
        "origin_panel": rows,
        "fixed_score_panel": fixed_panel,
        "actual_variants_evaluated": 1,
        "portfolio_economics_executed": False,
        "btc_cash_gross_map_executed": False,
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
    }


def test_all_preregistered_scientific_outcomes_are_schema_persistable():
    for stage in ("G1", "G2", "G3", "G4_FAIL", "PASS"):
        R.validate_result(result(stage), S)


def test_short_circuit_nulls_are_enforced():
    x = result("G2")
    x["bootstrap_q95"] = 0.1
    with pytest.raises(R.ControlledRunError):
        R.validate_result(x, S)


def test_g4_requires_fixed_score_panel_and_finite_lcbs():
    x = result("PASS")
    x["fixed_score_panel"] = None
    with pytest.raises(R.ControlledRunError):
        R.validate_result(x, S)
    x = result("PASS")
    x["simultaneous_lcb_by_target"][TARGETS[0]] = None
    with pytest.raises(R.ControlledRunError):
        R.validate_result(x, S)


def test_authority_cannot_be_enabled():
    x = result("G1")
    x["production_authorized"] = True
    with pytest.raises(R.ControlledRunError):
        R.validate_result(x, S)


def test_result_hash_changes_on_tamper():
    x = result("G2")
    a = R.sha_json(x)
    x["classification"] = R.scientific_engine.CLASS_SUPPORT
    assert R.sha_json(x) != a
