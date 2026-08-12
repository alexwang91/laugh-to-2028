from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from research.brrk_beta_handoff_0047 import engine as source_engine
from research.brrk_beta_btc_continuation_parameter_geometry_0058 import engine as scientific_engine


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INTERFACE_PATH = HERE / "RUN_INTERFACE.json"
SCHEMA_PATH = HERE / "RESULT_SCHEMA.json"
DATASET_SLICE_ID = "BRRK-LEADERSHIP-ROTATION-0048-EXPOSED-HIST-V1"
SCHEMA_ID = "BRRK-BETA-BTC-CONTINUATION-PARAMETER-GEOMETRY-0058-PRIMARY-RESULT-V1"


class ControlledRunError(RuntimeError):
    pass


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, (float, np.floating)):
        number = float(value)
        return number if math.isfinite(number) else None
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.ndarray):
        return [_json_safe(x) for x in value.tolist()]
    if isinstance(value, Mapping):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if hasattr(value, "item"):
        try:
            return _json_safe(value.item())
        except Exception:
            pass
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        _json_safe(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _sha256_json_file(path: Path) -> str:
    return hashlib.sha256(_canonical_bytes(_load_json(path))).hexdigest()


def _write_create_only(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(_json_safe(value), indent=2, ensure_ascii=False, allow_nan=False) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def _git(*args: str) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True, stderr=subprocess.STDOUT).strip()
    except subprocess.CalledProcessError as exc:
        raise ControlledRunError(f"Git command failed: git {' '.join(args)}\n{exc.output}") from exc


def _interface() -> dict[str, Any]:
    value = _load_json(INTERFACE_PATH)
    if value.get("research_id") != scientific_engine.RESEARCH_ID:
        raise ControlledRunError("RUN_INTERFACE research_id mismatch")
    if value.get("candidate_count") != len(scientific_engine.L_VALUES) * len(scientific_engine.KAPPA_VALUES):
        raise ControlledRunError("RUN_INTERFACE candidate_count mismatch")
    return value


def _schema() -> dict[str, Any]:
    value = _load_json(SCHEMA_PATH)
    if value.get("schema_id") != SCHEMA_ID or value.get("research_id") != scientific_engine.RESEARCH_ID:
        raise ControlledRunError("Unexpected 0058 result schema identity")
    return value


def _verify_expected_head(expected_head_sha: str) -> str:
    if not expected_head_sha:
        raise ControlledRunError("--expected-head-sha is mandatory")
    head = _git("rev-parse", "HEAD")
    if head != expected_head_sha:
        raise ControlledRunError(f"Git HEAD mismatch: expected {expected_head_sha}, got {head}")
    return head


def _verify_upstream_blobs(interface: Mapping[str, Any]) -> None:
    for path, expected in interface["immutable_upstream_git_blobs"].items():
        actual = _git("rev-parse", f"HEAD:{path}")
        if actual != expected:
            raise ControlledRunError(
                f"Immutable upstream blob mismatch for {path}: expected {expected}, got {actual}"
            )


def _verify_market_git_blob(interface: Mapping[str, Any]) -> None:
    frozen = interface["frozen_market_evidence"]
    actual = _git("rev-parse", f"HEAD:{frozen['path']}")
    if actual != frozen["git_blob_sha"]:
        raise ControlledRunError("Frozen market evidence git blob mismatch")


def _verify_market_wrapper(market: Path, interface: Mapping[str, Any]) -> str:
    frozen = interface["frozen_market_evidence"]
    configured = (ROOT / frozen["path"]).resolve()
    if market.resolve() != configured:
        raise ControlledRunError(f"Market path mismatch: expected {configured}, got {market.resolve()}")
    _verify_market_git_blob(interface)
    evidence = _load_json(market)
    actual_payload_sha = evidence.get("payload_sha256")
    if (
        actual_payload_sha != frozen["payload_sha256"]
        or actual_payload_sha != scientific_engine.EXPECTED_PAYLOAD_SHA256
    ):
        raise ControlledRunError("Frozen market payload SHA256 mismatch")
    return str(actual_payload_sha)


def _verify_runtime_names(result: Path, execution: Path, attempt: Path, marker: Path) -> None:
    actual = (result.name, execution.name, attempt.name, marker.name)
    expected = ("PRIMARY_RESULT.json", "EXECUTION.json", "RUN_ATTEMPT.marker", "RUN_ONCE.marker")
    if actual != expected:
        raise ControlledRunError(f"Runtime artifact filenames differ from frozen interface: {actual}")


def _verify_static_context(expected_head_sha: str) -> tuple[str, dict[str, Any]]:
    interface = _interface()
    _ = _schema()
    head = _verify_expected_head(expected_head_sha)
    _verify_upstream_blobs(interface)
    _verify_market_git_blob(interface)
    return head, interface


def _verify_controlled_context(market: Path, expected_head_sha: str) -> tuple[str, str]:
    head, interface = _verify_static_context(expected_head_sha)
    return head, _verify_market_wrapper(market, interface)


def _measurement_authority() -> dict[str, Any]:
    return {
        "canonical_strategy_changed": False,
        "phase6_changed": False,
        "production_authorized_components": [],
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
    }


def _authority() -> dict[str, Any]:
    return {
        "development_not_independent_oos": True,
        "researcher_exposed_history": True,
        "historical_execution_attempted": True,
        "declared_parameter_cells": len(scientific_engine.L_VALUES) * len(scientific_engine.KAPPA_VALUES),
        "actual_variants_evaluated": len(scientific_engine.L_VALUES) * len(scientific_engine.KAPPA_VALUES),
        "canonical_strategy_changed": False,
        "phase6_changed": False,
        "production_authorized_components": [],
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
        "same_id_rerun_allowed": False,
        "same_id_retuning_allowed": False,
        "same_id_rescue_allowed": False,
    }


def _scan_forbidden_metric_keys(value: Any, forbidden: Sequence[str], path: str = "root") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if str(key) == "authority":
                continue
            lowered = str(key).lower()
            hits = [token for token in forbidden if token.lower() in lowered]
            if hits:
                raise ControlledRunError(f"Forbidden non-preregistered metric key at {path}.{key}: {hits}")
            _scan_forbidden_metric_keys(child, forbidden, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for i, child in enumerate(value):
            _scan_forbidden_metric_keys(child, forbidden, f"{path}[{i}]")


def _require_exact_keys(value: Mapping[str, Any], expected: Sequence[str], label: str) -> None:
    actual = set(value.keys())
    wanted = set(expected)
    if actual != wanted:
        raise ControlledRunError(
            f"{label} key mismatch: missing={sorted(wanted-actual)} extra={sorted(actual-wanted)}"
        )


def _finite_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float, np.integer, np.floating)):
        raise ControlledRunError(f"{label} must be numeric")
    out = float(value)
    if not math.isfinite(out):
        raise ControlledRunError(f"{label} must be finite")
    return out


def _close(actual: Any, expected: float, label: str, *, atol: float = 1e-10) -> float:
    value = _finite_number(actual, label)
    if not math.isclose(value, float(expected), rel_tol=1e-10, abs_tol=atol):
        raise ControlledRunError(f"{label} mismatch: expected {expected}, got {value}")
    return value


def _validate_surface(rows: Any, schema: Mapping[str, Any]) -> dict[tuple[int, float, float], Mapping[str, Any]]:
    if not isinstance(rows, list):
        raise ControlledRunError("surface table must be a list")
    lattice = schema["frozen_lattice"]
    Ls = [int(x) for x in lattice["L_values"]]
    ks = [float(x) for x in lattice["kappa_values"]]
    costs = [float(x) for x in lattice["cost_bps"]]
    expected_order = [(L, k, c) for c in costs for L in Ls for k in ks]
    if len(rows) != lattice["surface_rows"]:
        raise ControlledRunError("Lossless surface row count mismatch")
    out: dict[tuple[int, float, float], Mapping[str, Any]] = {}
    observed_order: list[tuple[int, float, float]] = []
    for n, row in enumerate(rows):
        if not isinstance(row, Mapping):
            raise ControlledRunError(f"surface row {n} must be an object")
        _require_exact_keys(row, schema["surface_row_keys"], f"surface row {n}")
        L = int(row["L"])
        k = float(row["kappa"])
        cost = float(row["cost_bps"])
        key = (L, k, cost)
        if L not in Ls or k not in ks or cost not in costs or key in out:
            raise ControlledRunError(f"surface lattice identity mismatch at row {n}")
        wealth = _finite_number(row["terminal_wealth"], f"surface {key} terminal_wealth")
        cagr = _finite_number(row["cagr"], f"surface {key} cagr")
        mdd = _finite_number(row["mdd"], f"surface {key} mdd")
        turnover = _finite_number(row["executed_l1_turnover"], f"surface {key} turnover")
        switches = row["state_switch_count"]
        beta_fraction = _finite_number(row["beta_holding_fraction"], f"surface {key} beta fraction")
        if wealth <= 0.0 or cagr <= -1.0 or not (-1.0 <= mdd <= scientific_engine.STRICT_TOL):
            raise ControlledRunError(f"surface economic domain invalid at {key}")
        expected_cagr = wealth ** (scientific_engine.ANNUALIZATION_DAYS / scientific_engine.HELD_PERIODS) - 1.0
        _close(cagr, expected_cagr, f"surface {key} CAGR", atol=1e-11)
        if turnover < 0.0 or isinstance(switches, bool) or not isinstance(switches, (int, np.integer)) or int(switches) < 0:
            raise ControlledRunError(f"surface turnover/switch domain invalid at {key}")
        if not (0.0 <= beta_fraction <= 1.0):
            raise ControlledRunError(f"surface beta fraction invalid at {key}")
        out[key] = row
        observed_order.append(key)
    if observed_order != expected_order:
        raise ControlledRunError("surface rows are not in frozen cost/L/kappa order")
    return out


def _validate_geometry(
    rows: Any,
    surface: Mapping[tuple[int, float, float], Mapping[str, Any]],
    schema: Mapping[str, Any],
) -> None:
    if not isinstance(rows, list):
        raise ControlledRunError("geometry table must be a list")
    lattice = schema["frozen_lattice"]
    Ls = [int(x) for x in lattice["L_values"]]
    ks = [float(x) for x in lattice["kappa_values"]]
    iLs = [int(x) for x in lattice["interior_L_values"]]
    iks = [float(x) for x in lattice["interior_kappa_values"]]
    costs = [float(x) for x in lattice["cost_bps"]]
    expected_order = [(L, k, c) for c in costs for L in iLs for k in iks]
    if len(rows) != lattice["geometry_rows"]:
        raise ControlledRunError("Lossless geometry row count mismatch")
    observed_order: list[tuple[int, float, float]] = []
    seen: set[tuple[int, float, float]] = set()
    L_index = {L: i for i, L in enumerate(Ls)}
    k_index = {k: j for j, k in enumerate(ks)}
    for n, row in enumerate(rows):
        if not isinstance(row, Mapping):
            raise ControlledRunError(f"geometry row {n} must be an object")
        _require_exact_keys(row, schema["geometry_row_keys"], f"geometry row {n}")
        L = int(row["L"])
        k = float(row["kappa"])
        cost = float(row["cost_bps"])
        key = (L, k, cost)
        if L not in iLs or k not in iks or cost not in costs or key in seen:
            raise ControlledRunError(f"geometry lattice identity mismatch at row {n}")
        seen.add(key)
        observed_order.append(key)
        i = L_index[L]
        j = k_index[k]
        JpL = math.log(float(surface[(Ls[i + 1], k, cost)]["terminal_wealth"]))
        JmL = math.log(float(surface[(Ls[i - 1], k, cost)]["terminal_wealth"]))
        Jpk = math.log(float(surface[(L, ks[j + 1], cost)]["terminal_wealth"]))
        Jmk = math.log(float(surface[(L, ks[j - 1], cost)]["terminal_wealth"]))
        J0 = math.log(float(surface[(L, k, cost)]["terminal_wealth"]))
        Jpp = math.log(float(surface[(Ls[i + 1], ks[j + 1], cost)]["terminal_wealth"]))
        Jpm = math.log(float(surface[(Ls[i + 1], ks[j - 1], cost)]["terminal_wealth"]))
        Jmp = math.log(float(surface[(Ls[i - 1], ks[j + 1], cost)]["terminal_wealth"]))
        Jmm = math.log(float(surface[(Ls[i - 1], ks[j - 1], cost)]["terminal_wealth"]))
        dL = (JpL - JmL) / 2.0
        dk = (Jpk - Jmk) / 2.0
        dLL = JpL - 2.0 * J0 + JmL
        dkk = Jpk - 2.0 * J0 + Jmk
        dLk = (Jpp - Jpm - Jmp + Jmm) / 4.0
        grad = math.sqrt(dL * dL + dk * dk)
        eigvals = np.linalg.eigvalsh(np.array([[dLL, dLk], [dLk, dkk]], dtype=np.float64))
        hnorm = float(np.max(np.abs(eigvals)))
        for field, expected in (
            ("D_L", dL),
            ("D_kappa", dk),
            ("D_LL", dLL),
            ("D_kk", dkk),
            ("D_Lk", dLk),
            ("gradient_norm", grad),
            ("hessian_spectral_norm", hnorm),
        ):
            _close(row[field], expected, f"geometry {key} {field}")
        stable = bool(
            grad <= scientific_engine.GRADIENT_THRESHOLD
            and hnorm <= scientific_engine.HESSIAN_THRESHOLD
        )
        if row["stable_cell"] is not stable:
            raise ControlledRunError(f"geometry stable-cell mismatch at {key}")
    if observed_order != expected_order:
        raise ControlledRunError("geometry rows are not in frozen cost/L/kappa order")


def _validate_path_row(row: Mapping[str, Any], expected_keys: Sequence[str], label: str) -> None:
    _require_exact_keys(row, expected_keys, label)
    if not isinstance(row["date"], str) or not row["date"].endswith("Z"):
        raise ControlledRunError(f"{label} date must be semantic UTC Z text")
    nav = _finite_number(row["nav"], f"{label} nav")
    dd = _finite_number(row["drawdown"], f"{label} drawdown")
    growth = _finite_number(row["held_period_growth"], f"{label} held growth")
    if nav <= 0.0 or growth <= 0.0 or not (-1.0 <= dd <= scientific_engine.STRICT_TOL):
        raise ControlledRunError(f"{label} path domain invalid")


def _best_static_from_paths(rows: list[Mapping[str, Any]], schema: Mapping[str, Any]) -> str:
    terminal: dict[str, float] = {}
    for name in schema["benchmark_enum"]:
        subset = [row for row in rows if row["benchmark"] == name]
        if len(subset) != scientific_engine.HELD_PERIODS:
            raise ControlledRunError(f"benchmark path row count mismatch for {name}")
        terminal[name] = float(subset[-1]["nav"])
    best = schema["benchmark_enum"][0]
    best_w = terminal[best]
    for name in schema["benchmark_enum"][1:]:
        if terminal[name] > best_w:
            best = name
            best_w = terminal[name]
    return str(best)


def _validate_successful_measurement(measurement: Mapping[str, Any], schema: Mapping[str, Any]) -> None:
    _require_exact_keys(measurement, schema["successful_measurement_required_keys"], "successful measurement")
    if measurement["research_id"] != scientific_engine.RESEARCH_ID:
        raise ControlledRunError("measurement research_id mismatch")
    if measurement["classification"] == "INVALID_EXECUTION":
        raise ControlledRunError("successful measurement cannot use INVALID_EXECUTION")
    if measurement["actual_variants_evaluated"] != len(scientific_engine.L_VALUES) * len(scientific_engine.KAPPA_VALUES):
        raise ControlledRunError("0058 must evaluate the complete 108-cell surface")
    if measurement["path_date_semantics"] != schema["path_date_semantics"]:
        raise ControlledRunError("path date semantics mismatch")

    gates = measurement["gates"]
    if not isinstance(gates, Mapping):
        raise ControlledRunError("gates must be an object")
    _require_exact_keys(gates, schema["required_gate_keys"], "gates")
    if gates["G0_INTEGRITY"] is not True:
        raise ControlledRunError("successful measurement requires G0 integrity true")
    if not isinstance(gates["G1_PRIMARY_PLATEAU"], bool) or not isinstance(gates["G2_COST_ROBUSTNESS"], bool):
        raise ControlledRunError("G1/G2 must be booleans")
    if gates["G2_COST_ROBUSTNESS"]:
        for key in ("G3_ECONOMIC_RELEVANCE", "G4_TEMPORAL_ROBUSTNESS", "G5_DEPENDENCE_AWARE_ROBUSTNESS"):
            if not isinstance(gates[key], bool):
                raise ControlledRunError(f"{key} must be boolean when G2 passes")
    else:
        for key in ("G3_ECONOMIC_RELEVANCE", "G4_TEMPORAL_ROBUSTNESS", "G5_DEPENDENCE_AWARE_ROBUSTNESS"):
            if gates[key] is not None:
                raise ControlledRunError(f"{key} must be null when G2 fails")
    derived = scientific_engine.classification_from_gates(
        g1=gates["G1_PRIMARY_PLATEAU"],
        g2=gates["G2_COST_ROBUSTNESS"],
        g3=gates["G3_ECONOMIC_RELEVANCE"],
        g4=gates["G4_TEMPORAL_ROBUSTNESS"],
        g5=gates["G5_DEPENDENCE_AWARE_ROBUSTNESS"],
    )
    if derived != measurement["classification"]:
        raise ControlledRunError("classification does not match frozen G1-G5 precedence")

    surface = _validate_surface(measurement["surface_table_every_cell_every_cost"], schema)
    _validate_geometry(measurement["geometry_every_interior_cell_every_cost"], surface, schema)

    trace = measurement["plateau_trace"]
    if not isinstance(trace, Mapping):
        raise ControlledRunError("plateau_trace must be an object")
    _require_exact_keys(trace, schema["plateau_trace_keys"], "plateau_trace")
    for key in ("primary_5bps_components", "cost_coherent_components", "selected_component_cells", "component_ranking_trace"):
        if not isinstance(trace[key], list):
            raise ControlledRunError(f"plateau_trace {key} must be a list")
    argmax = trace["historical_argmax_descriptive_only"]
    if not isinstance(argmax, Mapping) or set(argmax) != {"L", "kappa", "terminal_wealth"}:
        raise ControlledRunError("historical argmax trace shape mismatch")
    primary_rows = [
        ((int(L), float(k)), float(surface[(int(L), float(k), 5.0)]["terminal_wealth"]))
        for L in schema["frozen_lattice"]["L_values"]
        for k in schema["frozen_lattice"]["kappa_values"]
    ]
    max_w = max(w for _, w in primary_rows)
    expected_argmax = min(key for key, w in primary_rows if w == max_w)
    if (int(argmax["L"]), float(argmax["kappa"])) != expected_argmax:
        raise ControlledRunError("historical argmax does not match frozen primary surface")
    _close(argmax["terminal_wealth"], max_w, "historical argmax terminal wealth")

    selected = trace["selected_representative"]
    candidate_rows = measurement["selected_representative_daily_path"]
    benchmark_rows = measurement["benchmark_daily_paths"]
    diagnostics = measurement["diagnostics"]
    if not isinstance(diagnostics, Mapping):
        raise ControlledRunError("diagnostics must be an object")
    _require_exact_keys(diagnostics, schema["diagnostic_keys"], "diagnostics")
    if diagnostics["historical_argmax_L"] != expected_argmax[0] or float(diagnostics["historical_argmax_kappa"]) != expected_argmax[1]:
        raise ControlledRunError("diagnostic historical argmax mismatch")
    _close(diagnostics["historical_argmax_terminal_wealth"], max_w, "diagnostic historical argmax wealth")

    if selected is None:
        if trace["selected_component_id"] is not None or trace["selected_component_cells"] or trace["medoid_distance_sum"] is not None:
            raise ControlledRunError("no-representative trace must have null/empty selected fields")
        if candidate_rows != [] or benchmark_rows != []:
            raise ControlledRunError("no-representative result must not impute selected or benchmark daily paths")
        if gates["G2_COST_ROBUSTNESS"] is not False:
            raise ControlledRunError("no representative requires G2 false")
        null_diag = (
            "selected_L", "selected_kappa", "selected_component_size", "selected_component_L_span",
            "selected_component_kappa_span", "selected_total_l1_turnover", "selected_switch_count",
            "selected_beta_holding_fraction", "average_state_spell_days", "median_state_spell_days",
            "longest_underperformance_interval_vs_5bps_B_STAR"
        )
        if any(diagnostics[k] is not None for k in null_diag):
            raise ControlledRunError("no-representative selected diagnostics must be null")
        for key in ("selected_terminal_wealth_by_cost", "selected_cagr_by_cost", "selected_mdd_by_cost", "calendar_year_returns_2021_partial_through_2026_partial"):
            if diagnostics[key] != {}:
                raise ControlledRunError("no-representative selected dictionary diagnostics must be empty")
    else:
        if not isinstance(selected, Mapping) or set(selected) != {"L", "kappa"}:
            raise ControlledRunError("selected representative shape mismatch")
        selected_key = (int(selected["L"]), float(selected["kappa"]))
        if selected_key[0] not in schema["frozen_lattice"]["L_values"] or selected_key[1] not in schema["frozen_lattice"]["kappa_values"]:
            raise ControlledRunError("selected representative is outside frozen lattice")
        if not isinstance(trace["selected_component_id"], str) or not trace["selected_component_cells"]:
            raise ControlledRunError("selected representative requires selected component trace")
        cell_pairs = {(int(x["L"]), float(x["kappa"])) for x in trace["selected_component_cells"]}
        if selected_key not in cell_pairs:
            raise ControlledRunError("selected medoid is not in selected component")
        if _finite_number(trace["medoid_distance_sum"], "medoid distance sum") < 0.0:
            raise ControlledRunError("medoid distance sum cannot be negative")
        if diagnostics["selected_L"] != selected_key[0] or float(diagnostics["selected_kappa"]) != selected_key[1]:
            raise ControlledRunError("selected diagnostics do not match selected representative")
        if diagnostics["selected_component_size"] != len(trace["selected_component_cells"]):
            raise ControlledRunError("selected component size diagnostic mismatch")
        if not isinstance(candidate_rows, list) or len(candidate_rows) != schema["frozen_counts"]["candidate_daily_rows_when_representative_exists"]:
            raise ControlledRunError("selected representative daily path row count mismatch")
        for i, row in enumerate(candidate_rows):
            if not isinstance(row, Mapping):
                raise ControlledRunError("selected daily path rows must be objects")
            _validate_path_row(row, schema["candidate_daily_path_keys"], f"candidate path row {i}")
            if row["state"] not in schema["state_enum"]:
                raise ControlledRunError("candidate path state mismatch")
            pre = _finite_number(row["pre_trade_nav"], f"candidate path {i} pre_trade_nav")
            turnover = _finite_number(row["executed_l1_turnover"], f"candidate path {i} turnover")
            cost = _finite_number(row["transaction_cost"], f"candidate path {i} transaction_cost")
            post = _finite_number(row["post_trade_nav"], f"candidate path {i} post_trade_nav")
            if pre <= 0.0 or post <= 0.0 or turnover < 0.0 or cost < 0.0:
                raise ControlledRunError("candidate trade path domain invalid")
        if not isinstance(benchmark_rows, list) or len(benchmark_rows) != schema["frozen_counts"]["benchmark_daily_rows_when_representative_exists"]:
            raise ControlledRunError("benchmark daily path row count mismatch")
        for i, row in enumerate(benchmark_rows):
            if not isinstance(row, Mapping):
                raise ControlledRunError("benchmark path rows must be objects")
            _validate_path_row(row, schema["benchmark_daily_path_keys"], f"benchmark path row {i}")
            if row["benchmark"] not in schema["benchmark_enum"]:
                raise ControlledRunError("benchmark path identity mismatch")
        selected_surface_5 = float(surface[(selected_key[0], selected_key[1], 5.0)]["terminal_wealth"])
        _close(candidate_rows[-1]["nav"], selected_surface_5, "selected daily terminal NAV")
        if not isinstance(diagnostics["selected_terminal_wealth_by_cost"], Mapping):
            raise ControlledRunError("selected terminal wealth by cost must be an object")
        for cost in schema["frozen_lattice"]["cost_bps"]:
            key = str(int(cost))
            _close(
                diagnostics["selected_terminal_wealth_by_cost"][key],
                float(surface[(selected_key[0], selected_key[1], float(cost))]["terminal_wealth"]),
                f"selected terminal wealth cost {key}",
            )
        turnover_sum = sum(float(row["executed_l1_turnover"]) for row in candidate_rows)
        _close(diagnostics["selected_total_l1_turnover"], turnover_sum, "selected turnover diagnostic")
        state_seq = [str(row["state"]) for row in candidate_rows]
        switch_count = sum(a != b for a, b in zip(state_seq[:-1], state_seq[1:]))
        if diagnostics["selected_switch_count"] != switch_count:
            raise ControlledRunError("selected switch-count diagnostic mismatch")
        beta_fraction = sum(x == "BETA" for x in state_seq) / len(state_seq)
        _close(diagnostics["selected_beta_holding_fraction"], beta_fraction, "selected beta fraction diagnostic")
        best_static_5 = _best_static_from_paths(benchmark_rows, schema)
        if measurement["best_static_by_cost_bps"].get("5") != best_static_5:
            raise ControlledRunError("best static 5bps does not match persisted benchmark paths")

    best_static = measurement["best_static_by_cost_bps"]
    if not isinstance(best_static, Mapping) or set(best_static) != {"5", "10", "20"}:
        raise ControlledRunError("best_static_by_cost_bps keys mismatch")
    if any(best_static[k] not in schema["benchmark_enum"] for k in ("5", "10", "20")):
        raise ControlledRunError("best_static_by_cost_bps contains unknown benchmark")

    robustness = measurement["robustness"]
    if not isinstance(robustness, Mapping):
        raise ControlledRunError("robustness must be an object")
    _require_exact_keys(robustness, schema["robustness_keys"], "robustness")
    if gates["G2_COST_ROBUSTNESS"]:
        block_stats = robustness["four_block_statistics"]
        means = robustness["bootstrap_means"]
        lcbs = robustness["bootstrap_lcbs"]
        q95 = robustness["bootstrap_q95"]
        if not isinstance(block_stats, list) or len(block_stats) != 4:
            raise ControlledRunError("temporal robustness block count mismatch")
        if not isinstance(means, list) or len(means) != 3 or not isinstance(lcbs, list) or len(lcbs) != 3:
            raise ControlledRunError("bootstrap vector length mismatch")
        block_values = [_finite_number(x, "temporal block statistic") for x in block_stats]
        mean_values = [_finite_number(x, "bootstrap mean") for x in means]
        lcb_values = [_finite_number(x, "bootstrap LCB") for x in lcbs]
        _ = mean_values
        _finite_number(q95, "bootstrap q95")
        expected_g4 = sum(x > scientific_engine.STRICT_TOL for x in block_values) >= scientific_engine.TEMPORAL_REQUIRED_WINS
        expected_g5 = min(lcb_values) > 0.0
        if gates["G4_TEMPORAL_ROBUSTNESS"] is not expected_g4:
            raise ControlledRunError("G4 does not match persisted temporal statistics")
        if gates["G5_DEPENDENCE_AWARE_ROBUSTNESS"] is not expected_g5:
            raise ControlledRunError("G5 does not match persisted bootstrap LCBs")
    else:
        if any(robustness[k] is not None for k in schema["robustness_keys"]):
            raise ControlledRunError("robustness fields must be null when G2 fails")

    for key, expected in schema["measurement_authority_invariants"].items():
        if measurement["authority"].get(key) != expected:
            raise ControlledRunError(f"measurement authority invariant mismatch: {key}")
    _scan_forbidden_metric_keys(measurement, schema["forbidden_metric_tokens"])


def validate_result(result: Mapping[str, Any], schema: Mapping[str, Any] | None = None) -> None:
    schema = _schema() if schema is None else schema
    _require_exact_keys(result, schema["required_top_level_keys"], "PRIMARY_RESULT")
    if result["schema_id"] != schema["schema_id"] or result["research_id"] != scientific_engine.RESEARCH_ID:
        raise ControlledRunError("PRIMARY_RESULT identity mismatch")
    if result["dataset_slice_id"] != schema["dataset_slice_id"] or result["payload_sha256"] != schema["payload_sha256"]:
        raise ControlledRunError("PRIMARY_RESULT dataset identity mismatch")
    if result["classification"] not in schema["classification_enum"]:
        raise ControlledRunError("PRIMARY_RESULT classification is not frozen")
    for key, expected in schema["authority_invariants"].items():
        if result["authority"].get(key) != expected:
            raise ControlledRunError(f"PRIMARY_RESULT authority invariant mismatch: {key}")
    measurement = result["measurement"]
    if not isinstance(measurement, Mapping):
        raise ControlledRunError("PRIMARY_RESULT measurement must be an object")
    if result["classification"] == "INVALID_EXECUTION":
        _require_exact_keys(measurement, schema["invalid_measurement_required_keys"], "invalid measurement")
        if measurement["research_id"] != scientific_engine.RESEARCH_ID or measurement["classification"] != "INVALID_EXECUTION":
            raise ControlledRunError("invalid measurement identity mismatch")
        if measurement["actual_variants_evaluated"] != len(scientific_engine.L_VALUES) * len(scientific_engine.KAPPA_VALUES):
            raise ControlledRunError("invalid attempt must remain bound to the frozen 108-cell surface")
        for key, expected in schema["measurement_authority_invariants"].items():
            if measurement["authority"].get(key) != expected:
                raise ControlledRunError(f"invalid measurement authority mismatch: {key}")
    else:
        if measurement.get("classification") != result["classification"]:
            raise ControlledRunError("measurement/top-level classification mismatch")
        _validate_successful_measurement(measurement, schema)


def _build_result(market: Path, head: str, payload_sha: str) -> dict[str, Any]:
    schema = _schema()
    try:
        evidence = _load_json(market)
        source_frames = source_engine.frames_from_market_evidence(evidence)
        if set(source_frames) != set(scientific_engine.ASSETS):
            raise source_engine.FrozenProtocolError("0058 source loader did not return exact BTC/ETH/SOL set")
        frames = {asset: source_frames[asset] for asset in scientific_engine.ASSETS}
        measurement = scientific_engine.evaluate_frozen_contract(frames, payload_sha)
        classification = str(measurement["classification"])
    except (source_engine.FrozenProtocolError, scientific_engine.ParameterGeometryProtocolError) as exc:
        classification = "INVALID_EXECUTION"
        measurement = {
            "research_id": scientific_engine.RESEARCH_ID,
            "classification": classification,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "actual_variants_evaluated": len(scientific_engine.L_VALUES) * len(scientific_engine.KAPPA_VALUES),
            "authority": _measurement_authority(),
        }
    value = {
        "schema_id": schema["schema_id"],
        "research_id": scientific_engine.RESEARCH_ID,
        "dataset_slice_id": DATASET_SLICE_ID,
        "payload_sha256": payload_sha,
        "execution_head_sha": head,
        "classification": classification,
        "measurement": _json_safe(measurement),
        "authority": _authority(),
    }
    validate_result(value, schema)
    return value


def _runtime_paths_exist(*paths: Path) -> list[str]:
    return [path.name for path in paths if path.exists()]


def preflight(*, market: Path, result: Path, execution: Path, attempt: Path, marker: Path, expected_head_sha: str) -> dict[str, Any]:
    _verify_runtime_names(result, execution, attempt, marker)
    head, payload_sha = _verify_controlled_context(market, expected_head_sha)
    forbidden = _runtime_paths_exist(result, execution, marker)
    if forbidden:
        raise ControlledRunError(f"Preflight found existing output artifacts: {forbidden}")
    return {
        "research_id": scientific_engine.RESEARCH_ID,
        "status": "PREFLIGHT_ZERO_RESULT_PASS",
        "git_head_sha": head,
        "payload_sha256": payload_sha,
        "attempt_marker_exists": attempt.exists(),
        "result_exists": result.exists(),
        "execution_exists": execution.exists(),
        "final_marker_exists": marker.exists(),
        "candidate_count": len(scientific_engine.L_VALUES) * len(scientific_engine.KAPPA_VALUES),
        "actual_variants_evaluated": 0,
        "production_authorized": False,
    }


def start_attempt(*, market: Path, result: Path, execution: Path, attempt: Path, marker: Path, expected_head_sha: str) -> dict[str, Any]:
    _verify_runtime_names(result, execution, attempt, marker)
    head, payload_sha = _verify_controlled_context(market, expected_head_sha)
    existing = _runtime_paths_exist(attempt, result, execution, marker)
    if existing:
        raise ControlledRunError(f"Cannot start attempt with existing runtime artifacts: {existing}")
    value = {
        "research_id": scientific_engine.RESEARCH_ID,
        "dataset_slice_id": DATASET_SLICE_ID,
        "payload_sha256": payload_sha,
        "git_head_sha": head,
        "started_at_utc": _utc_now(),
        "candidate_count": len(scientific_engine.L_VALUES) * len(scientific_engine.KAPPA_VALUES),
        "expected_surface_rows": len(scientific_engine.L_VALUES) * len(scientific_engine.KAPPA_VALUES) * len(scientific_engine.COST_BPS),
        "expected_geometry_rows": (len(scientific_engine.L_VALUES) - 2) * (len(scientific_engine.KAPPA_VALUES) - 2) * len(scientific_engine.COST_BPS),
        "same_id_recomputation_allowed": False,
        "production_authorized": False,
    }
    _write_create_only(attempt, value)
    return value


def _verify_attempt(attempt: Path, *, head: str, payload_sha: str) -> dict[str, Any]:
    value = _load_json(attempt)
    if value.get("research_id") != scientific_engine.RESEARCH_ID:
        raise ControlledRunError("RUN_ATTEMPT.marker research_id mismatch")
    if value.get("dataset_slice_id") != DATASET_SLICE_ID or value.get("payload_sha256") != payload_sha:
        raise ControlledRunError("RUN_ATTEMPT.marker dataset identity mismatch")
    if value.get("git_head_sha") != head:
        raise ControlledRunError("RUN_ATTEMPT.marker HEAD mismatch")
    if value.get("candidate_count") != len(scientific_engine.L_VALUES) * len(scientific_engine.KAPPA_VALUES):
        raise ControlledRunError("RUN_ATTEMPT.marker candidate count mismatch")
    if value.get("same_id_recomputation_allowed") is not False:
        raise ControlledRunError("RUN_ATTEMPT.marker authority mismatch")
    return value


def evaluate_after_attempt(*, market: Path, result: Path, execution: Path, attempt: Path, marker: Path, expected_head_sha: str) -> dict[str, Any]:
    _verify_runtime_names(result, execution, attempt, marker)
    head, payload_sha = _verify_controlled_context(market, expected_head_sha)
    if not attempt.exists():
        raise ControlledRunError("RUN_ATTEMPT.marker must exist before parameter-surface evaluation")
    existing = _runtime_paths_exist(result, execution, marker)
    if existing:
        raise ControlledRunError(f"Cannot evaluate with existing output artifact: {existing}")
    attempt_value = _verify_attempt(attempt, head=head, payload_sha=payload_sha)
    value = _build_result(market, head, payload_sha)
    _write_create_only(result, value)
    execution_value = {
        "research_id": scientific_engine.RESEARCH_ID,
        "dataset_slice_id": DATASET_SLICE_ID,
        "payload_sha256": payload_sha,
        "git_head_sha": head,
        "started_at_utc": attempt_value["started_at_utc"],
        "completed_at_utc": _utc_now(),
        "classification": value["classification"],
        "actual_variants_evaluated": len(scientific_engine.L_VALUES) * len(scientific_engine.KAPPA_VALUES),
        "attempt_marker_sha256": _sha256_json_file(attempt),
        "primary_result_sha256": _sha256_json_file(result),
        "same_id_rerun_allowed": False,
        "same_id_retuning_allowed": False,
        "same_id_rescue_allowed": False,
        "production_authorized": False,
    }
    _write_create_only(execution, execution_value)
    return value


def finalize_marker_only(*, market: Path, result: Path, execution: Path, attempt: Path, marker: Path, expected_head_sha: str) -> dict[str, Any]:
    _verify_runtime_names(result, execution, attempt, marker)
    head, interface = _verify_static_context(expected_head_sha)
    payload_sha = str(interface["frozen_market_evidence"]["payload_sha256"])
    if marker.exists():
        raise ControlledRunError("RUN_ONCE.marker already exists")
    missing = [path.name for path in (attempt, result, execution) if not path.exists()]
    if missing:
        raise ControlledRunError(f"Cannot finalize marker; missing persisted artifacts: {missing}")
    attempt_value = _verify_attempt(attempt, head=head, payload_sha=payload_sha)
    result_value = _load_json(result)
    validate_result(result_value)
    if result_value.get("execution_head_sha") != head or result_value.get("payload_sha256") != payload_sha:
        raise ControlledRunError("PRIMARY_RESULT identity mismatch during finalize")
    execution_value = _load_json(execution)
    if execution_value.get("research_id") != scientific_engine.RESEARCH_ID or execution_value.get("git_head_sha") != head:
        raise ControlledRunError("EXECUTION identity mismatch")
    if execution_value.get("payload_sha256") != payload_sha or execution_value.get("classification") != result_value.get("classification"):
        raise ControlledRunError("EXECUTION result identity mismatch")
    if execution_value.get("actual_variants_evaluated") != len(scientific_engine.L_VALUES) * len(scientific_engine.KAPPA_VALUES):
        raise ControlledRunError("EXECUTION candidate-count mismatch")
    attempt_hash = _sha256_json_file(attempt)
    result_hash = _sha256_json_file(result)
    if execution_value.get("attempt_marker_sha256") != attempt_hash:
        raise ControlledRunError("Attempt marker hash mismatch")
    if execution_value.get("primary_result_sha256") != result_hash:
        raise ControlledRunError("Primary result hash mismatch")
    value = {
        "research_id": scientific_engine.RESEARCH_ID,
        "dataset_slice_id": DATASET_SLICE_ID,
        "payload_sha256": payload_sha,
        "git_head_sha": head,
        "finalized_at_utc": _utc_now(),
        "classification": result_value["classification"],
        "actual_variants_evaluated": len(scientific_engine.L_VALUES) * len(scientific_engine.KAPPA_VALUES),
        "attempt_marker_sha256": attempt_hash,
        "primary_result_sha256": result_hash,
        "execution_sha256": _sha256_json_file(execution),
        "finalized_without_remeasurement": True,
        "same_id_rerun_allowed": False,
        "same_id_retuning_allowed": False,
        "same_id_rescue_allowed": False,
        "production_authorized": False,
    }
    if attempt_value.get("same_id_recomputation_allowed") is not False:
        raise ControlledRunError("Attempt marker no longer forbids recomputation")
    _write_create_only(marker, value)
    return value


def _default_paths() -> dict[str, Path]:
    return {
        "market": ROOT / "research/brrk_beta_handoff_0047/evidence/MARKET_EVIDENCE.json",
        "result": HERE / "PRIMARY_RESULT.json",
        "execution": HERE / "EXECUTION.json",
        "attempt": HERE / "RUN_ATTEMPT.marker",
        "marker": HERE / "RUN_ONCE.marker",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="0058 controlled exactly-once parameter-geometry execution state machine")
    parser.add_argument("command", choices=("preflight", "start-attempt", "evaluate", "finalize"))
    parser.add_argument("--expected-head-sha", required=True)
    defaults = _default_paths()
    for name, path in defaults.items():
        parser.add_argument(f"--{name}", type=Path, default=path)
    args = parser.parse_args()
    kwargs = {
        "market": args.market,
        "result": args.result,
        "execution": args.execution,
        "attempt": args.attempt,
        "marker": args.marker,
        "expected_head_sha": args.expected_head_sha,
    }
    if args.command == "preflight":
        value = preflight(**kwargs)
    elif args.command == "start-attempt":
        value = start_attempt(**kwargs)
    elif args.command == "evaluate":
        value = evaluate_after_attempt(**kwargs)
    else:
        value = finalize_marker_only(**kwargs)
    print(json.dumps(_json_safe(value), indent=2, ensure_ascii=False, allow_nan=False))


if __name__ == "__main__":
    main()
