from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import NormalDist
from typing import Mapping, Sequence

from .data_contract import SourcePoint

RUN_INTERFACE_PATH = Path(__file__).with_name("RUN_INTERFACE.json")
RUN_INTERFACE_ID = "STABLECOIN-LIQUIDITY-0001-RUN-INTERFACE-V1"
RESEARCH_ID = "STABLECOIN-LIQUIDITY-0001"
STABLECOIN_DATASET_REF = "STABLECOIN-LIQUIDITY-0001-DEFILLAMA-HIST-V1"
STABLECOIN_EXPOSURE_REF = "STABLECOIN-LIQUIDITY-0001-RAW-DATA-20260808T141719Z"
HORIZON_DAYS = 20
PRIMARY_HAC_LAG = 19
MIN_TRAINING_ROWS = 365
MIN_PASS_OOS = 730
LABEL_COST_BPS = 5.0
STABLECOIN_AVAILABILITY_LAG_DAYS = 2
TARGET_ASSETS = ("BTC", "ETH", "SOL", "BNB")
SEMANTIC_STATES = ("RISK_OFF", "BTC_LEAD", "MAJOR_ROTATION", "ALT_EXPANSION")
REGIME_FEATURES = (
    "btc_trend",
    "log_btc_rv30",
    "btc_drawdown_252",
    "major_breadth",
    "alt_breadth",
    "rel_strength_mean",
    "rel_strength_dispersion",
    "avg_corr30_btc",
)
BASELINE_FEATURE_ORDER = (
    "target_weight_BTC",
    "target_weight_ETH",
    "target_weight_SOL",
    "target_weight_BNB",
    "cash_share",
    "base_gross_target",
    "risk_probability_RISK_OFF",
    "risk_probability_BTC_LEAD",
    "risk_probability_MAJOR_ROTATION",
    "risk_probability_ALT_EXPANSION",
    "meta_scale",
    "defensive_scale",
    "regime_feature_btc_trend",
    "regime_feature_log_btc_rv30",
    "regime_feature_btc_drawdown_252",
    "regime_feature_major_breadth",
    "regime_feature_alt_breadth",
    "regime_feature_rel_strength_mean",
    "regime_feature_rel_strength_dispersion",
    "regime_feature_avg_corr30_btc",
    "v1_raw_gross_before_defense",
    "v1_raw_weight_BTC",
    "v1_raw_weight_ETH",
    "v1_raw_weight_SOL",
    "v1_raw_weight_BNB",
    "v1_btc_beta",
    "v1_btc_trend",
    "v1_btc_vol",
    "v1_score_ETH",
    "v1_score_SOL",
    "v1_score_BNB",
    "v1_asset_trend_BTC",
    "v1_asset_trend_ETH",
    "v1_asset_trend_SOL",
    "v1_asset_trend_BNB",
)
STABLECOIN_FEATURE_ORDER = (
    "stablecoin_growth_20d",
    "stablecoin_growth_acceleration_20d",
)
FIRST_RELEASE_FIELDS = (
    "research_id",
    "run_interface_id",
    "classification",
    "valid_oos_prediction_count",
    "mean_primary_loss_differential",
    "hac_max_lag",
    "hac_test_statistic",
    "hac_one_sided_p_value",
    "primary_result_digest",
)


class RunInterfaceError(RuntimeError):
    pass


@dataclass(frozen=True)
class StablecoinDecisionFeature:
    decision_timestamp: datetime
    metric_timestamp: datetime
    growth_20d: float
    acceleration_20d: float

    def vector(self) -> tuple[float, float]:
        return (self.growth_20d, self.acceleration_20d)


@dataclass(frozen=True)
class HACResult:
    n: int
    mean: float
    long_run_variance: float
    standard_error_mean: float | None
    test_statistic: float | None
    one_sided_p_value: float | None


def load_run_interface(path: Path = RUN_INTERFACE_PATH) -> dict[str, object]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_run_interface_contract(contract: Mapping[str, object] | None = None) -> None:
    data = dict(contract or load_run_interface())
    if data.get("run_interface_id") != RUN_INTERFACE_ID:
        raise RunInterfaceError("run interface id drifted")
    if data.get("research_id") != RESEARCH_ID:
        raise RunInterfaceError("run interface research id drifted")
    if data.get("status") != "FROZEN_NOT_EXECUTED":
        raise RunInterfaceError("run interface must remain FROZEN_NOT_EXECUTED before Stage-1")
    if data.get("production_authorized") is not False:
        raise RunInterfaceError("run interface cannot confer production authority")

    binding = data.get("dataset_binding")
    if not isinstance(binding, Mapping):
        raise RunInterfaceError("dataset binding missing")
    if binding.get("stablecoin_validation_dataset_ref") != STABLECOIN_DATASET_REF:
        raise RunInterfaceError("stablecoin dataset binding drifted")
    if binding.get("stablecoin_raw_exposure_ref") != STABLECOIN_EXPOSURE_REF:
        raise RunInterfaceError("stablecoin exposure binding drifted")

    baseline = data.get("baseline_state")
    if not isinstance(baseline, Mapping):
        raise RunInterfaceError("baseline state contract missing")
    if tuple(baseline.get("continuous_feature_order", ())) != BASELINE_FEATURE_ORDER:
        raise RunInterfaceError("baseline feature order drifted")
    if baseline.get("feature_count") != len(BASELINE_FEATURE_ORDER):
        raise RunInterfaceError("baseline feature count drifted")

    stablecoin = data.get("stablecoin_feature_alignment")
    if not isinstance(stablecoin, Mapping):
        raise RunInterfaceError("stablecoin feature contract missing")
    if tuple(stablecoin.get("feature_order", ())) != STABLECOIN_FEATURE_ORDER:
        raise RunInterfaceError("stablecoin feature order drifted")
    if stablecoin.get("lag_1d_or_3d_allowed") is not False:
        raise RunInterfaceError("LAG1/LAG3 rescue is forbidden")

    walk = data.get("walk_forward")
    if not isinstance(walk, Mapping):
        raise RunInterfaceError("walk-forward contract missing")
    if walk.get("minimum_training_rows") != MIN_TRAINING_ROWS:
        raise RunInterfaceError("minimum training rows drifted")
    if walk.get("minimum_valid_oos_predictions_for_pass") != MIN_PASS_OOS:
        raise RunInterfaceError("minimum pass OOS drifted")

    metric = data.get("primary_metric")
    if not isinstance(metric, Mapping) or not isinstance(metric.get("hac"), Mapping):
        raise RunInterfaceError("primary HAC contract missing")
    if metric["hac"].get("max_lag") != PRIMARY_HAC_LAG:
        raise RunInterfaceError("HAC lag drifted")

    release = data.get("result_release")
    if not isinstance(release, Mapping):
        raise RunInterfaceError("result release contract missing")
    if tuple(release.get("first_release_only", ())) != FIRST_RELEASE_FIELDS:
        raise RunInterfaceError("first-release field set drifted")


def _finite(value: object, label: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise RunInterfaceError(f"{label} must be numeric") from exc
    if not math.isfinite(result):
        raise RunInterfaceError(f"{label} must be finite")
    return result


def _mapping(value: object, label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise RunInterfaceError(f"{label} must be a mapping")
    return value


def flatten_canonical_brrk_state(result: Mapping[str, object]) -> tuple[float, ...]:
    """Extract the frozen 35-column continuous P3.2 price/regime state.

    The function accepts ``TargetCalculationResult.to_dict()``-shaped data and
    deliberately excludes account state, string identifiers and diagnostics that
    are not part of the frozen continuous information set.
    """
    target = _mapping(result.get("target_weights"), "target_weights")
    probabilities = _mapping(result.get("risk_state_probabilities"), "risk_state_probabilities")
    snapshot = _mapping(result.get("feature_snapshot"), "feature_snapshot")
    regime = _mapping(snapshot.get("regime_features"), "regime_features")
    v1 = _mapping(snapshot.get("v1"), "feature_snapshot.v1")
    raw_weights = _mapping(v1.get("raw_weights"), "v1.raw_weights")
    scores = _mapping(v1.get("scores"), "v1.scores")
    asset_trends = _mapping(v1.get("asset_trends"), "v1.asset_trends")

    values: list[float] = []
    values.extend(_finite(target.get(asset), f"target_weight_{asset}") for asset in TARGET_ASSETS)
    values.append(_finite(result.get("cash_share"), "cash_share"))
    values.append(_finite(result.get("base_gross_target"), "base_gross_target"))
    values.extend(
        _finite(probabilities.get(state), f"risk_probability_{state}") for state in SEMANTIC_STATES
    )
    values.append(_finite(result.get("meta_scale"), "meta_scale"))
    values.append(_finite(result.get("defensive_scale"), "defensive_scale"))
    values.extend(_finite(regime.get(name), f"regime_feature_{name}") for name in REGIME_FEATURES)
    values.append(_finite(v1.get("raw_gross_before_defense"), "v1_raw_gross_before_defense"))
    values.extend(_finite(raw_weights.get(asset), f"v1_raw_weight_{asset}") for asset in TARGET_ASSETS)
    values.append(_finite(v1.get("btc_beta"), "v1_btc_beta"))
    values.append(_finite(v1.get("btc_trend"), "v1_btc_trend"))
    values.append(_finite(v1.get("btc_vol"), "v1_btc_vol"))
    values.extend(_finite(scores.get(asset), f"v1_score_{asset}") for asset in ("ETH", "SOL", "BNB"))
    values.extend(_finite(asset_trends.get(asset), f"v1_asset_trend_{asset}") for asset in TARGET_ASSETS)
    if len(values) != len(BASELINE_FEATURE_ORDER):
        raise RunInterfaceError("baseline state extraction produced wrong feature count")
    return tuple(values)


def _utc_midnight(value: datetime, label: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise RunInterfaceError(f"{label} must be timezone-aware")
    utc = value.astimezone(timezone.utc)
    if utc.hour or utc.minute or utc.second or utc.microsecond:
        raise RunInterfaceError(f"{label} must be exactly 00:00:00 UTC")
    return utc


def stablecoin_feature_for_decision(
    points: Sequence[SourcePoint],
    decision_timestamp: datetime,
) -> StablecoinDecisionFeature | None:
    decision = _utc_midnight(decision_timestamp, "decision_timestamp")
    metric = decision - timedelta(days=STABLECOIN_AVAILABILITY_LAG_DAYS)
    by_timestamp = {point.metric_timestamp: float(point.value) for point in points}
    required = (metric, metric - timedelta(days=20), metric - timedelta(days=40))
    if any(timestamp not in by_timestamp for timestamp in required):
        return None
    s0, s20, s40 = (by_timestamp[timestamp] for timestamp in required)
    if any(not math.isfinite(value) or value <= 0.0 for value in (s0, s20, s40)):
        return None
    g20 = math.log(s0) - math.log(s20)
    prior_g20 = math.log(s20) - math.log(s40)
    return StablecoinDecisionFeature(
        decision_timestamp=decision,
        metric_timestamp=metric,
        growth_20d=g20,
        acceleration_20d=g20 - prior_g20,
    )


def canonical_daily_net_return(
    target_weights: Mapping[str, object],
    previous_target_weights: Mapping[str, object],
    asset_returns: Mapping[str, object],
    *,
    cost_bps: float = LABEL_COST_BPS,
) -> float:
    target = {asset: _finite(target_weights.get(asset), f"target[{asset}]") for asset in TARGET_ASSETS}
    previous = {
        asset: _finite(previous_target_weights.get(asset), f"previous_target[{asset}]")
        for asset in TARGET_ASSETS
    }
    returns = {asset: _finite(asset_returns.get(asset), f"asset_return[{asset}]") for asset in TARGET_ASSETS}
    if any(value <= -1.0 for value in returns.values()):
        raise RunInterfaceError("asset return <= -1 invalidates label input")
    turnover = sum(abs(target[asset] - previous[asset]) for asset in TARGET_ASSETS)
    result = sum(target[asset] * returns[asset] for asset in TARGET_ASSETS)
    result -= turnover * _finite(cost_bps, "cost_bps") / 10000.0
    if not math.isfinite(result) or result <= -1.0:
        raise RunInterfaceError("daily net return is nonfinite or <= -1")
    return result


def forward_20d_label(
    daily_net_returns: Mapping[datetime, object],
    decision_timestamp: datetime,
) -> float | None:
    decision = _utc_midnight(decision_timestamp, "decision_timestamp")
    wealth = 1.0
    for offset in range(HORIZON_DAYS):
        timestamp = decision + timedelta(days=offset)
        if timestamp not in daily_net_returns:
            return None
        value = _finite(daily_net_returns[timestamp], f"daily_net_return[{timestamp.isoformat()}]")
        if value <= -1.0:
            raise RunInterfaceError("daily net return <= -1 invalidates forward label")
        wealth *= 1.0 + value
    return wealth - 1.0


def label_realized_at(decision_timestamp: datetime) -> datetime:
    return _utc_midnight(decision_timestamp, "decision_timestamp") + timedelta(days=HORIZON_DAYS)


def eligible_training_decisions(
    prior_decisions: Sequence[datetime],
    prediction_timestamp: datetime,
) -> tuple[datetime, ...]:
    prediction = _utc_midnight(prediction_timestamp, "prediction_timestamp")
    eligible: list[datetime] = []
    for value in prior_decisions:
        decision = _utc_midnight(value, "training_decision")
        if decision >= prediction:
            continue
        if label_realized_at(decision) <= prediction:
            eligible.append(decision)
    return tuple(sorted(eligible))


def hac_newey_west_one_sided(
    loss_differentials: Sequence[object],
    *,
    max_lag: int = PRIMARY_HAC_LAG,
) -> HACResult:
    values = [_finite(value, "loss_differential") for value in loss_differentials]
    n = len(values)
    if n == 0:
        raise RunInterfaceError("HAC requires at least one loss differential")
    if max_lag < 0:
        raise RunInterfaceError("HAC max_lag must be nonnegative")
    mean = sum(values) / n
    centered = [value - mean for value in values]

    def gamma(lag: int) -> float:
        if lag >= n:
            return 0.0
        return sum(centered[t] * centered[t - lag] for t in range(lag, n)) / n

    long_run = gamma(0)
    for lag in range(1, max_lag + 1):
        weight = 1.0 - lag / (max_lag + 1.0)
        long_run += 2.0 * weight * gamma(lag)
    if long_run <= 0.0 or not math.isfinite(long_run):
        return HACResult(
            n=n,
            mean=mean,
            long_run_variance=long_run,
            standard_error_mean=None,
            test_statistic=None,
            one_sided_p_value=None,
        )
    standard_error = math.sqrt(long_run / n)
    if standard_error <= 0.0 or not math.isfinite(standard_error):
        return HACResult(n, mean, long_run, None, None, None)
    statistic = mean / standard_error
    p_value = 1.0 - NormalDist().cdf(statistic)
    return HACResult(n, mean, long_run, standard_error, statistic, p_value)


def classify_primary_result(hac: HACResult) -> str:
    if hac.mean <= 0.0:
        return "FAIL_NO_INCREMENTAL_INFORMATION"
    if hac.n < MIN_PASS_OOS:
        return "INCONCLUSIVE"
    if hac.one_sided_p_value is None:
        return "INCONCLUSIVE"
    if hac.one_sided_p_value < 0.05:
        return "PASS_INCREMENTAL_INFORMATION"
    return "INCONCLUSIVE"


def validate_first_release(payload: Mapping[str, object]) -> None:
    keys = tuple(payload.keys())
    if set(keys) != set(FIRST_RELEASE_FIELDS) or len(keys) != len(FIRST_RELEASE_FIELDS):
        raise RunInterfaceError("first result release must contain exactly the frozen primary fields")
    if payload.get("research_id") != RESEARCH_ID:
        raise RunInterfaceError("first release research_id mismatch")
    if payload.get("run_interface_id") != RUN_INTERFACE_ID:
        raise RunInterfaceError("first release run_interface_id mismatch")
    if payload.get("hac_max_lag") != PRIMARY_HAC_LAG:
        raise RunInterfaceError("first release HAC lag mismatch")


def claim_run_once(marker_path: Path, execution_token: str) -> Path:
    if execution_token != "[STABLECOIN_STAGE1_EXECUTE_V1]":
        raise RunInterfaceError("invalid Stage-1 execution token")
    path = Path(marker_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = (
        json.dumps(
            {
                "schema_version": 1,
                "research_id": RESEARCH_ID,
                "run_interface_id": RUN_INTERFACE_ID,
                "stage1_execution_id": "STABLECOIN-LIQUIDITY-0001-STAGE1-RUN-V1",
                "state": "CLAIMED_BEFORE_RESULT_BEARING_EXECUTION",
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o444)
    with os.fdopen(fd, "wb", closefd=True) as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    return path
