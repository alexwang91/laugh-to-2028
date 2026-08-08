from __future__ import annotations

import argparse
import bisect
import hashlib
import importlib.metadata
import json
import math
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Mapping, Sequence

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

REPO_ROOT = Path(__file__).resolve().parents[2]
EXECUTION_ROOT = REPO_ROOT / "execution" / "plan-b-bot"
INTEGRATION_ROOT = REPO_ROOT / "research" / "integration"
if str(EXECUTION_ROOT) not in sys.path:
    sys.path.insert(0, str(EXECUTION_ROOT))
if str(INTEGRATION_ROOT) not in sys.path:
    sys.path.insert(0, str(INTEGRATION_ROOT))

from beta_bot.product_config import load_product_config  # noqa: E402
from beta_bot.target_engine import calculate_target  # noqa: E402
from beta_bot.target_math import (  # noqa: E402
    FrozenBRRKConfig,
    TARGET_ASSETS,
    apply_internal_v1_band,
    build_features_no_dominance,
    build_v1_raw,
    current_defensive_state,
    eligible_refit_dates,
    portfolio_returns_full,
)
from p3_1_data_contract_adapter import canonicalize_research_daily_history  # noqa: E402

from research.stablecoin_liquidity_0001.data_contract import parse_source_payload  # noqa: E402
from research.stablecoin_liquidity_0001.run_interface import (  # noqa: E402
    BASELINE_FEATURE_ORDER,
    FIRST_RELEASE_FIELDS,
    MIN_PASS_OOS,
    MIN_TRAINING_ROWS,
    PRIMARY_HAC_LAG,
    RESEARCH_ID,
    RUN_INTERFACE_ID,
    STABLECOIN_FEATURE_ORDER,
    canonical_daily_net_return,
    classify_primary_result,
    flatten_canonical_brrk_state,
    forward_20d_label,
    hac_newey_west_one_sided,
    label_realized_at,
    stablecoin_feature_for_decision,
    validate_first_release,
    validate_run_interface_contract,
)

EXPECTED_STABLECOIN_SHA256 = "7cffe6fb3a21e891082c06c60e91491edfbc78e9c01e2d549805815a646d9ffd"
EXECUTION_ID = "STABLECOIN-LIQUIDITY-0001-STAGE1-RUN-V1"
RUN_ONCE_MARKER = REPO_ROOT / "research" / "stablecoin_liquidity_0001" / "RUN_ONCE_STAGE1.marker"
EXECUTION_CONTRACT = REPO_ROOT / "research" / "stablecoin_liquidity_0001" / "STAGE1_EXECUTION.json"
CANDIDATE_END = datetime(2026, 7, 19, tzinfo=timezone.utc)
FINAL_DECISION_FOR_CANONICAL_DATA = "2026-08-08T00:00:00Z"
FROZEN_PARITY_DECISIONS = (
    "2022-12-15T00:00:00Z",
    "2023-10-25T00:00:00Z",
    "2024-08-06T00:00:00Z",
    "2025-04-10T00:00:00Z",
    "2025-11-15T00:00:00Z",
    "2026-08-03T00:00:00Z",
)
DEPENDENCY_LOCK = {
    "numpy": "2.5.1",
    "pandas": "3.0.3",
    "scipy": "1.18.0",
    "scikit-learn": "1.9.0",
    "hmmlearn": "0.3.3",
}


class Stage1ExecutionError(RuntimeError):
    pass


@dataclass(frozen=True)
class BatchState:
    decision_timestamp: datetime
    target_session: pd.Timestamp
    refit_session: pd.Timestamp
    target_weights: dict[str, float]
    state_vector: tuple[float, ...]


@dataclass(frozen=True)
class PairedRow:
    decision_timestamp: datetime
    baseline: tuple[float, ...]
    augmented_extra: tuple[float, float]
    label: float


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _canonical_json(value: Mapping[str, object]) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def _utc_midnight(value: str | datetime | pd.Timestamp) -> datetime:
    ts = pd.Timestamp(value)
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    else:
        ts = ts.tz_convert("UTC")
    if ts.hour or ts.minute or ts.second or ts.microsecond:
        raise Stage1ExecutionError(f"timestamp is not UTC midnight: {value!r}")
    return ts.to_pydatetime()


def _verify_dependencies() -> None:
    for package, expected in DEPENDENCY_LOCK.items():
        actual = importlib.metadata.version(package)
        if actual != expected:
            raise Stage1ExecutionError(f"dependency drift: {package}={actual}, expected {expected}")


def _verify_contracts() -> None:
    validate_run_interface_contract()
    marker = json.loads(RUN_ONCE_MARKER.read_text(encoding="utf-8"))
    if marker.get("research_id") != RESEARCH_ID:
        raise Stage1ExecutionError("run-once marker research_id mismatch")
    if marker.get("run_interface_id") != RUN_INTERFACE_ID:
        raise Stage1ExecutionError("run-once marker interface mismatch")
    if marker.get("stage1_execution_id") != EXECUTION_ID:
        raise Stage1ExecutionError("run-once marker execution_id mismatch")
    if marker.get("state") != "CLAIMED_BEFORE_RESULT_BEARING_EXECUTION":
        raise Stage1ExecutionError("run-once marker is not an irreversible pre-execution claim")
    contract = json.loads(EXECUTION_CONTRACT.read_text(encoding="utf-8"))
    if contract.get("execution_id") != EXECUTION_ID:
        raise Stage1ExecutionError("execution contract id mismatch")
    if contract.get("status") != "ARMED_NOT_EXECUTED":
        raise Stage1ExecutionError("execution contract is not armed")
    if contract.get("production_authorized") is not False:
        raise Stage1ExecutionError("execution contract cannot confer production authority")


def _verify_durability_receipt(receipt_path: Path, manifest_path: Path) -> dict[str, object]:
    receipt = json.loads(Path(receipt_path).read_text(encoding="utf-8"))
    manifest_hash = _sha256(Path(manifest_path).read_bytes())
    if receipt.get("manifest_sha256") != manifest_hash:
        raise Stage1ExecutionError("Binance durability receipt manifest SHA256 mismatch")
    if receipt.get("durable_backend") != "GITHUB_ACTIONS_ARTIFACT_V4":
        raise Stage1ExecutionError("unexpected Binance durable backend")
    for key in ("artifact_id", "artifact_url", "archived_at"):
        value = receipt.get(key)
        if not isinstance(value, str) or not value.strip():
            raise Stage1ExecutionError(f"Binance durability receipt missing {key}")
    return receipt


def _load_binance_capture(root: Path) -> tuple[dict[str, Sequence[tuple[str, Sequence[Sequence[object]]]]], object, pd.DataFrame]:
    root = Path(root)
    manifest_path = root / "BINANCE_STAGE1_CAPTURE_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("capture_id") != "STABLECOIN-LIQUIDITY-0001-STAGE1-BINANCE-CAPTURE-V1":
        raise Stage1ExecutionError("unexpected Binance capture manifest id")
    pages = manifest.get("pages")
    if not isinstance(pages, list) or not pages:
        raise Stage1ExecutionError("Binance capture manifest contains no pages")

    source_batches: dict[str, list[tuple[str, Sequence[Sequence[object]]]]] = {}
    expected_assets = {"BTC", "ETH", "SOL", "BNB", "XRP"}
    for asset in expected_assets:
        asset_pages = sorted(
            [page for page in pages if page.get("asset") == asset],
            key=lambda page: int(page.get("page_number", -1)),
        )
        if not asset_pages:
            raise Stage1ExecutionError(f"missing Binance pages for {asset}")
        combined: list[list[object]] = []
        expected_page = 0
        last_open: int | None = None
        for page in asset_pages:
            if int(page.get("page_number", -1)) != expected_page:
                raise Stage1ExecutionError(f"non-contiguous Binance page numbers for {asset}")
            expected_page += 1
            path = root / str(page.get("raw_relative_path"))
            raw = path.read_bytes()
            if _sha256(raw) != page.get("raw_sha256"):
                raise Stage1ExecutionError(f"Binance raw SHA mismatch for {path}")
            if len(raw) != int(page.get("raw_size_bytes", -1)):
                raise Stage1ExecutionError(f"Binance raw size mismatch for {path}")
            payload = json.loads(raw)
            if not isinstance(payload, list):
                raise Stage1ExecutionError(f"Binance page is not list: {path}")
            if len(payload) != int(page.get("row_count", -1)):
                raise Stage1ExecutionError(f"Binance page row count mismatch: {path}")
            for row in payload:
                if not isinstance(row, list) or len(row) < 7:
                    raise Stage1ExecutionError(f"malformed Binance kline row: {path}")
                open_ms = int(row[0])
                if last_open is not None and open_ms <= last_open:
                    raise Stage1ExecutionError(f"non-increasing Binance sessions for {asset}")
                last_open = open_ms
                combined.append(row)
        source_batches[asset] = [(f"{asset}USDT", combined)]

    if set(source_batches) != expected_assets:
        raise Stage1ExecutionError("Binance source asset set mismatch")
    dataset = canonicalize_research_daily_history(
        source_batches=source_batches,
        decision_timestamp=FINAL_DECISION_FOR_CANONICAL_DATA,
    )
    columns: dict[str, pd.Series] = {}
    for asset in ("BTC", "ETH", "SOL", "BNB", "XRP"):
        rows = dataset.closes_by_asset[asset]
        index = pd.to_datetime(
            np.asarray([int(row.session_open_ms) for row in rows], dtype=np.int64),
            unit="ms",
            utc=True,
        ).tz_localize(None)
        columns[asset] = pd.Series([float(row.close) for row in rows], index=index, dtype=float)
    prices = pd.DataFrame(columns).loc[:, ["BTC", "ETH", "SOL", "BNB", "XRP"]].sort_index()
    if prices.empty or prices.index.has_duplicates or prices.isna().any().any():
        raise Stage1ExecutionError("canonical Binance price frame is empty/duplicate/incomplete")
    return source_batches, dataset, prices


def _load_stablecoin_points(path: Path):
    raw = Path(path).read_bytes()
    digest = _sha256(raw)
    if digest != EXPECTED_STABLECOIN_SHA256:
        raise Stage1ExecutionError(f"Stablecoin raw SHA mismatch: {digest}")
    points = parse_source_payload(raw)
    if not points:
        raise Stage1ExecutionError("Stablecoin source contains no valid observations")
    return points


def _state_payload(
    target_session: pd.Timestamp,
    raw_row: pd.Series,
    diagnostics: Mapping[str, object],
    defensive: Mapping[str, object],
) -> tuple[dict[str, object], dict[str, float]]:
    defensive_scale = float(defensive["defensive_scale"])
    target_row = raw_row.astype(float) * defensive_scale
    target_row = target_row.clip(lower=0.0)
    gross = float(target_row.sum())
    if gross > 1.0 + 1e-10 or gross < -1e-12:
        raise Stage1ExecutionError(f"batch P3.2 gross invalid on {target_session}: {gross}")
    cash = float(np.clip(1.0 - gross, 0.0, 1.0))
    scores = diagnostics["scores"]
    trend = diagnostics["trend"]
    if not isinstance(scores, pd.DataFrame) or not isinstance(trend, Mapping):
        raise Stage1ExecutionError("batch V1 diagnostics shape mismatch")
    payload = {
        "target_weights": {asset: float(target_row[asset]) for asset in TARGET_ASSETS},
        "cash_share": cash,
        "base_gross_target": gross,
        "risk_state_probabilities": {
            state: float(value) for state, value in dict(defensive["posterior"]).items()
        },
        "meta_scale": float(defensive["meta_scale"]),
        "defensive_scale": defensive_scale,
        "feature_snapshot": {
            "regime_features": dict(defensive["feature_snapshot"]),
            "v1": {
                "raw_gross_before_defense": float(raw_row.abs().sum()),
                "raw_weights": {asset: float(raw_row[asset]) for asset in TARGET_ASSETS},
                "btc_beta": float(diagnostics["beta"].loc[target_session]),
                "btc_trend": float(diagnostics["btc_trend"].loc[target_session]),
                "btc_vol": float(diagnostics["btc_vol"].loc[target_session]),
                "scores": {
                    asset: float(scores.loc[target_session, asset]) for asset in ("ETH", "SOL", "BNB")
                },
                "asset_trends": {
                    asset: float(trend[asset].loc[target_session]) for asset in TARGET_ASSETS
                },
            },
        },
    }
    return payload, {asset: float(target_row[asset]) for asset in TARGET_ASSETS}


def build_batch_p3_2_states(prices: pd.DataFrame) -> dict[datetime, BatchState]:
    cfg = FrozenBRRKConfig()
    v1_raw, diagnostics = build_v1_raw(prices)
    features = build_features_no_dominance(prices, cfg)
    v1_banded = apply_internal_v1_band(v1_raw)
    v1_returns = portfolio_returns_full(prices, v1_banded)
    refits = eligible_refit_dates(features, cfg)
    if not refits:
        raise Stage1ExecutionError("no canonical P3.2 refit dates available")

    defensive_by_refit: dict[pd.Timestamp, dict[str, object]] = {}
    for refit in refits:
        r = pd.Timestamp(refit)
        defensive_by_refit[r] = current_defensive_state(
            prices.loc[:r], features.loc[:r], v1_returns.loc[:r], cfg
        )
        observed = pd.Timestamp(defensive_by_refit[r]["refit_date"])
        if observed != r:
            raise Stage1ExecutionError(f"defensive refit mismatch: expected {r}, got {observed}")

    refit_ns = [pd.Timestamp(value).value for value in refits]
    states: dict[datetime, BatchState] = {}
    for target_session in prices.index:
        ts = pd.Timestamp(target_session)
        pos = bisect.bisect_right(refit_ns, ts.value) - 1
        if pos < 0:
            continue
        raw_row = v1_raw.loc[ts, list(TARGET_ASSETS)]
        if raw_row.isna().any():
            continue
        refit = pd.Timestamp(refits[pos])
        defensive = defensive_by_refit[refit]
        try:
            payload, target_weights = _state_payload(ts, raw_row, diagnostics, defensive)
            vector = flatten_canonical_brrk_state(payload)
        except (KeyError, TypeError, ValueError, Stage1ExecutionError) as exc:
            raise Stage1ExecutionError(f"batch P3.2 state failed on {ts.date()}: {exc}") from exc
        decision = (ts.tz_localize("UTC") + pd.Timedelta(days=1)).to_pydatetime()
        states[decision] = BatchState(
            decision_timestamp=decision,
            target_session=ts,
            refit_session=refit,
            target_weights=target_weights,
            state_vector=vector,
        )
    if not states:
        raise Stage1ExecutionError("batch P3.2 state path is empty")
    return states


def verify_batch_parity(
    source_batches: Mapping[str, Sequence[tuple[str, Sequence[Sequence[object]]]]],
    batch_states: Mapping[datetime, BatchState],
) -> None:
    config = load_product_config()
    for decision_text in FROZEN_PARITY_DECISIONS:
        decision = _utc_midnight(decision_text)
        batch = batch_states.get(decision)
        if batch is None:
            raise Stage1ExecutionError(f"batch parity state missing for {decision_text}")
        dataset = canonicalize_research_daily_history(
            source_batches=dict(source_batches), decision_timestamp=decision_text
        )
        canonical = calculate_target(
            daily_dataset=dataset,
            account_equity_usd=10_000.0,
            current_positions={},
            approved_config=config,
        )
        canonical_vector = flatten_canonical_brrk_state(canonical.to_dict())
        if len(canonical_vector) != len(batch.state_vector):
            raise Stage1ExecutionError(f"batch parity feature count mismatch at {decision_text}")
        for index, (left, right) in enumerate(zip(batch.state_vector, canonical_vector)):
            if not math.isclose(left, right, rel_tol=0.0, abs_tol=2e-10):
                raise Stage1ExecutionError(
                    f"batch parity mismatch at {decision_text} feature={BASELINE_FEATURE_ORDER[index]} "
                    f"batch={left!r} canonical={right!r}"
                )
        if batch.target_session.strftime("%Y-%m-%d") != canonical.target_session:
            raise Stage1ExecutionError(f"batch target-session mismatch at {decision_text}")
        if batch.refit_session.strftime("%Y-%m-%d") != canonical.regime_refit_session:
            raise Stage1ExecutionError(f"batch refit-session mismatch at {decision_text}")


def _daily_net_returns(prices: pd.DataFrame, states: Mapping[datetime, BatchState]) -> dict[datetime, float]:
    result: dict[datetime, float] = {}
    ordered = sorted(states)
    state_by_decision = dict(states)
    for decision in ordered:
        previous_decision = decision - timedelta(days=1)
        if previous_decision not in state_by_decision:
            continue
        d = pd.Timestamp(decision).tz_convert("UTC").tz_localize(None)
        previous_session = d - pd.Timedelta(days=1)
        if d not in prices.index or previous_session not in prices.index:
            continue
        asset_returns = {
            asset: float(prices.loc[d, asset] / prices.loc[previous_session, asset] - 1.0)
            for asset in TARGET_ASSETS
        }
        result[decision] = canonical_daily_net_return(
            state_by_decision[decision].target_weights,
            state_by_decision[previous_decision].target_weights,
            asset_returns,
        )
    return result


def build_paired_rows(
    prices: pd.DataFrame,
    states: Mapping[datetime, BatchState],
    stablecoin_points,
) -> list[PairedRow]:
    daily_net = _daily_net_returns(prices, states)
    rows: list[PairedRow] = []
    for decision in sorted(states):
        if decision > CANDIDATE_END:
            continue
        feature = stablecoin_feature_for_decision(stablecoin_points, decision)
        if feature is None:
            continue
        label = forward_20d_label(daily_net, decision)
        if label is None:
            continue
        if label_realized_at(decision) > datetime(2026, 8, 8, tzinfo=timezone.utc):
            continue
        baseline = tuple(float(value) for value in states[decision].state_vector)
        if len(baseline) != len(BASELINE_FEATURE_ORDER) or not all(math.isfinite(x) for x in baseline):
            continue
        extra = tuple(float(value) for value in feature.vector())
        if len(extra) != len(STABLECOIN_FEATURE_ORDER) or not all(math.isfinite(x) for x in extra):
            continue
        if not math.isfinite(float(label)):
            continue
        rows.append(PairedRow(decision, baseline, (extra[0], extra[1]), float(label)))
    if not rows:
        raise Stage1ExecutionError("no paired Stage-1 rows available")
    return rows


def run_walk_forward(rows: Sequence[PairedRow]) -> tuple[list[float], int]:
    ordered = sorted(rows, key=lambda row: row.decision_timestamp)
    differentials: list[float] = []
    for test_index, test in enumerate(ordered):
        train = [
            row
            for row in ordered[:test_index]
            if label_realized_at(row.decision_timestamp) <= test.decision_timestamp
        ]
        if len(train) < MIN_TRAINING_ROWS:
            continue
        x_base = np.asarray([row.baseline for row in train], dtype=float)
        x_aug = np.asarray([row.baseline + row.augmented_extra for row in train], dtype=float)
        y = np.asarray([row.label for row in train], dtype=float)
        test_base = np.asarray([test.baseline], dtype=float)
        test_aug = np.asarray([test.baseline + test.augmented_extra], dtype=float)
        if (
            x_base.shape[1] != len(BASELINE_FEATURE_ORDER)
            or x_aug.shape[1] != len(BASELINE_FEATURE_ORDER) + len(STABLECOIN_FEATURE_ORDER)
        ):
            raise Stage1ExecutionError("walk-forward design matrix column count drifted")
        if not (
            np.all(np.isfinite(x_base))
            and np.all(np.isfinite(x_aug))
            and np.all(np.isfinite(y))
            and np.all(np.isfinite(test_base))
            and np.all(np.isfinite(test_aug))
        ):
            raise Stage1ExecutionError("walk-forward contains nonfinite values")

        base_scaler = StandardScaler(with_mean=True, with_std=True).fit(x_base)
        aug_scaler = StandardScaler(with_mean=True, with_std=True).fit(x_aug)
        base_model = Ridge(alpha=1.0, fit_intercept=True, solver="svd", positive=False)
        aug_model = Ridge(alpha=1.0, fit_intercept=True, solver="svd", positive=False)
        base_model.fit(base_scaler.transform(x_base), y)
        aug_model.fit(aug_scaler.transform(x_aug), y)
        pred_base = float(base_model.predict(base_scaler.transform(test_base))[0])
        pred_aug = float(aug_model.predict(aug_scaler.transform(test_aug))[0])
        if not math.isfinite(pred_base) or not math.isfinite(pred_aug):
            raise Stage1ExecutionError("nonfinite OOS Ridge prediction")
        error_base = float(test.label) - pred_base
        error_aug = float(test.label) - pred_aug
        differentials.append(error_base * error_base - error_aug * error_aug)
    return differentials, len(differentials)


def build_primary_result(differentials: Sequence[float]) -> dict[str, object]:
    hac = hac_newey_west_one_sided(differentials, max_lag=PRIMARY_HAC_LAG)
    classification = classify_primary_result(hac)
    payload_without_digest: dict[str, object] = {
        "research_id": RESEARCH_ID,
        "run_interface_id": RUN_INTERFACE_ID,
        "classification": classification,
        "valid_oos_prediction_count": hac.n,
        "mean_primary_loss_differential": hac.mean,
        "hac_max_lag": PRIMARY_HAC_LAG,
        "hac_test_statistic": hac.test_statistic,
        "hac_one_sided_p_value": hac.one_sided_p_value,
    }
    digest = _sha256(_canonical_json(payload_without_digest))
    payload = {**payload_without_digest, "primary_result_digest": digest}
    validate_first_release(payload)
    if set(payload) != set(FIRST_RELEASE_FIELDS):
        raise Stage1ExecutionError("primary result release contains non-frozen fields")
    return payload


def execute(
    *,
    stablecoin_raw: Path,
    binance_root: Path,
    binance_receipt: Path,
    output: Path,
) -> None:
    _verify_dependencies()
    _verify_contracts()
    manifest_path = Path(binance_root) / "BINANCE_STAGE1_CAPTURE_MANIFEST.json"
    _verify_durability_receipt(binance_receipt, manifest_path)
    source_batches, _, prices = _load_binance_capture(binance_root)
    stablecoin_points = _load_stablecoin_points(stablecoin_raw)

    # Every gate above is provenance/data only. The expensive canonical state path
    # begins here, and Ridge remains forbidden until batch parity succeeds.
    states = build_batch_p3_2_states(prices)
    verify_batch_parity(source_batches, states)

    paired = build_paired_rows(prices, states, stablecoin_points)
    differentials, count = run_walk_forward(paired)
    if count != len(differentials):
        raise Stage1ExecutionError("walk-forward OOS count mismatch")
    result = build_primary_result(differentials)
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    raw = _canonical_json(result) + b"\n"
    if output_path.exists():
        raise Stage1ExecutionError("primary result output already exists")
    output_path.write_bytes(raw)
    print("PRIMARY_RESULT_WRITTEN", flush=True)


def self_test() -> None:
    _verify_dependencies()
    _verify_contracts()
    rng = np.random.default_rng(20260808)
    x = rng.normal(size=(MIN_TRAINING_ROWS + 5, len(BASELINE_FEATURE_ORDER)))
    extra = rng.normal(size=(MIN_TRAINING_ROWS + 5, len(STABLECOIN_FEATURE_ORDER)))
    y = 0.01 * x[:, 0] + 0.02 * extra[:, 0] + rng.normal(scale=0.01, size=len(x))
    dates = [datetime(2025, 1, 1, tzinfo=timezone.utc) + timedelta(days=i) for i in range(len(x))]
    rows = [
        PairedRow(
            decision_timestamp=dates[i],
            baseline=tuple(float(v) for v in x[i]),
            augmented_extra=(float(extra[i, 0]), float(extra[i, 1])),
            label=float(y[i]),
        )
        for i in range(len(x))
    ]
    differentials, count = run_walk_forward(rows)
    if count <= 0 or not differentials:
        raise Stage1ExecutionError("self-test produced no OOS predictions")
    hac = hac_newey_west_one_sided(differentials)
    if hac.n != count:
        raise Stage1ExecutionError("self-test HAC count mismatch")
    synthetic_result = {
        "research_id": RESEARCH_ID,
        "run_interface_id": RUN_INTERFACE_ID,
        "classification": classify_primary_result(hac),
        "valid_oos_prediction_count": hac.n,
        "mean_primary_loss_differential": hac.mean,
        "hac_max_lag": PRIMARY_HAC_LAG,
        "hac_test_statistic": hac.test_statistic,
        "hac_one_sided_p_value": hac.one_sided_p_value,
        "primary_result_digest": "0" * 64,
    }
    validate_first_release(synthetic_result)
    print("STAGE1_SELF_TEST_PASS", flush=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--stablecoin-raw", type=Path)
    parser.add_argument("--binance-root", type=Path)
    parser.add_argument("--binance-receipt", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    if args.self_test:
        self_test()
        return 0
    required = (args.stablecoin_raw, args.binance_root, args.binance_receipt, args.output)
    if any(value is None for value in required):
        raise Stage1ExecutionError("execution requires stablecoin raw, Binance root/receipt and output")
    execute(
        stablecoin_raw=args.stablecoin_raw,
        binance_root=args.binance_root,
        binance_receipt=args.binance_receipt,
        output=args.output,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
