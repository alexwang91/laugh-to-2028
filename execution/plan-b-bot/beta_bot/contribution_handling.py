from __future__ import annotations

"""P3.4 weekly/manual contribution handling.

P3.4 does not invent a new allocation model. A manual deposit is observed as an
account-equity change, recorded without claiming source attribution, and is never
allowed to trigger an unscheduled intraday risk increase. At the next canonical
00:00 UTC daily decision, the fresh account equity is fed through the existing
P3.2 target engine and then the existing P3.3 rebalance control.
"""

from dataclasses import asdict, dataclass
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping

import pandas as pd

from .data_contract import CanonicalDailyDataset
from .product_config import ProductConfig, load_product_config
from .rebalance_control import (
    REBALANCE_CONTROL_VERSION,
    RebalanceControlPlan,
    calculate_rebalance_control,
)
from .target_engine import (
    TARGET_ENGINE_VERSION,
    TargetCalculationResult,
    calculate_target,
)


CONTRIBUTION_HANDLING_VERSION = "P3.4-EQUITY-CHANGE-DAILY-V1"
DEFAULT_POLICY_PATH = Path(__file__).resolve().parents[3] / "config" / "contribution_policy.json"
EQUITY_CHANGE_NUMERIC_TOLERANCE_USD = 1e-8


class ContributionHandlingError(RuntimeError):
    pass


def _finite_float(value: object, *, field: str) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ContributionHandlingError(f"{field} must be numeric") from exc
    if not math.isfinite(parsed):
        raise ContributionHandlingError(f"{field} must be finite")
    return parsed


def _utc_timestamp(value: object, *, field: str) -> pd.Timestamp:
    try:
        timestamp = pd.Timestamp(value)
    except Exception as exc:  # pragma: no cover - pandas error shapes vary
        raise ContributionHandlingError(f"{field} must be a valid timestamp") from exc
    if timestamp.tzinfo is None:
        raise ContributionHandlingError(f"{field} must be timezone-aware UTC")
    return timestamp.tz_convert("UTC")


def _canonical_timestamp(timestamp: pd.Timestamp) -> str:
    return timestamp.isoformat().replace("+00:00", "Z")


def _is_utc_daily_boundary(timestamp: pd.Timestamp) -> bool:
    timestamp = timestamp.tz_convert("UTC")
    return (
        timestamp.hour == 0
        and timestamp.minute == 0
        and timestamp.second == 0
        and timestamp.microsecond == 0
        and timestamp.nanosecond == 0
    )


def _next_daily_decision_at_or_after(observed_at: pd.Timestamp) -> pd.Timestamp:
    observed_at = observed_at.tz_convert("UTC")
    boundary = observed_at.normalize()
    if observed_at == boundary:
        return boundary
    return boundary + pd.Timedelta(days=1)


@dataclass(frozen=True)
class ContributionPolicy:
    schema_version: int
    policy_id: str
    equity_reference: str
    detection_rule: str
    positive_change_classification: str
    negative_change_classification: str
    daily_decision_timezone: str
    daily_decision_time: str
    intraday_action: str
    daily_allocation_path: tuple[str, ...]
    weekly_contribution_amount_role: str
    authorization: str

    def validate(self) -> None:
        expected = {
            "schema_version": 1,
            "policy_id": CONTRIBUTION_HANDLING_VERSION,
            "equity_reference": "PREVIOUS_ACCEPTED_DAILY_DECISION_ACCOUNT_EQUITY",
            "detection_rule": "OBSERVE_SIGNED_ACCOUNT_EQUITY_CHANGE_WITHOUT_SOURCE_ATTRIBUTION",
            "positive_change_classification": "CONTRIBUTION_CANDIDATE_NOT_CONFIRMED_TRANSFER",
            "negative_change_classification": "NEGATIVE_EQUITY_CHANGE_NOT_CONTRIBUTION",
            "daily_decision_timezone": "UTC",
            "daily_decision_time": "00:00:00",
            "intraday_action": "RECORD_ONLY_NO_TARGET_RECALCULATION_NO_RISK_INCREASE",
            "daily_allocation_path": (TARGET_ENGINE_VERSION, REBALANCE_CONTROL_VERSION),
            "weekly_contribution_amount_role": (
                "PRODUCT_ASSUMPTION_ONLY_NOT_DETECTION_THRESHOLD_NOT_SCHEDULE_TRIGGER"
            ),
            "authorization": "CONTRIBUTION_HANDLING_ONLY_NO_PRODUCTION_AUTHORIZATION",
        }
        actual = {
            "schema_version": self.schema_version,
            "policy_id": self.policy_id,
            "equity_reference": self.equity_reference,
            "detection_rule": self.detection_rule,
            "positive_change_classification": self.positive_change_classification,
            "negative_change_classification": self.negative_change_classification,
            "daily_decision_timezone": self.daily_decision_timezone,
            "daily_decision_time": self.daily_decision_time,
            "intraday_action": self.intraday_action,
            "daily_allocation_path": self.daily_allocation_path,
            "weekly_contribution_amount_role": self.weekly_contribution_amount_role,
            "authorization": self.authorization,
        }
        drift = [key for key, value in expected.items() if actual[key] != value]
        if drift:
            raise ContributionHandlingError(
                f"{CONTRIBUTION_HANDLING_VERSION} policy drift detected: {','.join(drift)}"
            )


def load_contribution_policy(path: Path | None = None) -> ContributionPolicy:
    raw = json.loads((path or DEFAULT_POLICY_PATH).read_text(encoding="utf-8"))
    policy = ContributionPolicy(
        schema_version=int(raw["schema_version"]),
        policy_id=str(raw["policy_id"]),
        equity_reference=str(raw["equity_reference"]),
        detection_rule=str(raw["detection_rule"]),
        positive_change_classification=str(raw["positive_change_classification"]),
        negative_change_classification=str(raw["negative_change_classification"]),
        daily_decision_timezone=str(raw["daily_decision_timezone"]),
        daily_decision_time=str(raw["daily_decision_time"]),
        intraday_action=str(raw["intraday_action"]),
        daily_allocation_path=tuple(str(item) for item in raw["daily_allocation_path"]),
        weekly_contribution_amount_role=str(raw["weekly_contribution_amount_role"]),
        authorization=str(raw["authorization"]),
    )
    policy.validate()
    return policy


@dataclass(frozen=True)
class EquityChangeObservation:
    baseline_decision_timestamp: str
    observed_at: str
    baseline_equity_usd: float
    observed_equity_usd: float
    equity_change_usd: float
    positive_equity_change_candidate_usd: float
    change_classification: str
    source_attributed: bool
    scheduled_daily_decision_timestamp: str
    observed_at_daily_boundary: bool
    requires_intraday_action: bool
    intraday_target_recalculation_allowed: bool
    intraday_risk_increase_allowed: bool
    contribution_candidate_pending: bool
    contribution_handling_version: str = CONTRIBUTION_HANDLING_VERSION
    production_authorized: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def canonical_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=True)

    def digest(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ContributionAwareDailyDecision:
    decision_timestamp: str
    observation_digest: str
    observed_equity_change_usd: float
    contribution_candidate_usd: float
    contribution_candidate_included: bool
    decision_account_equity_usd: float
    target_engine_version: str
    target_digest: str
    rebalance_control_version: str
    rebalance_control_digest: str
    target: TargetCalculationResult
    rebalance_control: RebalanceControlPlan
    contribution_handling_version: str = CONTRIBUTION_HANDLING_VERSION
    production_authorized: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision_timestamp": self.decision_timestamp,
            "observation_digest": self.observation_digest,
            "observed_equity_change_usd": self.observed_equity_change_usd,
            "contribution_candidate_usd": self.contribution_candidate_usd,
            "contribution_candidate_included": self.contribution_candidate_included,
            "decision_account_equity_usd": self.decision_account_equity_usd,
            "target_engine_version": self.target_engine_version,
            "target_digest": self.target_digest,
            "rebalance_control_version": self.rebalance_control_version,
            "rebalance_control_digest": self.rebalance_control_digest,
            "target": self.target.to_dict(),
            "rebalance_control": self.rebalance_control.to_dict(),
            "contribution_handling_version": self.contribution_handling_version,
            "production_authorized": self.production_authorized,
        }

    def canonical_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=True)

    def digest(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()


def observe_equity_change(
    *,
    baseline_decision_timestamp: object,
    baseline_equity_usd: object,
    observed_at: object,
    observed_equity_usd: object,
    policy: ContributionPolicy | None = None,
) -> EquityChangeObservation:
    """Record a signed equity change without attributing its economic source.

    A positive change is a contribution *candidate*, not proof of a deposit. This
    intentionally avoids trying to distinguish manual cash flow from mark-to-market
    PnL using account equity alone. The observation itself can never authorize an
    intraday target recalculation or risk increase.
    """
    active_policy = policy or load_contribution_policy()
    active_policy.validate()

    baseline_ts = _utc_timestamp(
        baseline_decision_timestamp,
        field="baseline_decision_timestamp",
    )
    if not _is_utc_daily_boundary(baseline_ts):
        raise ContributionHandlingError(
            "baseline_decision_timestamp must be an accepted 00:00 UTC daily decision"
        )
    observation_ts = _utc_timestamp(observed_at, field="observed_at")
    if observation_ts < baseline_ts:
        raise ContributionHandlingError("observed_at cannot precede baseline decision")

    baseline_equity = _finite_float(baseline_equity_usd, field="baseline_equity_usd")
    observed_equity = _finite_float(observed_equity_usd, field="observed_equity_usd")
    if baseline_equity <= 0 or observed_equity < 0:
        raise ContributionHandlingError(
            "baseline equity must be positive and observed equity must be non-negative"
        )

    delta = observed_equity - baseline_equity
    if abs(delta) <= EQUITY_CHANGE_NUMERIC_TOLERANCE_USD:
        delta = 0.0
        positive_candidate = 0.0
        classification = "NO_MATERIAL_NUMERIC_EQUITY_CHANGE"
    elif delta > 0:
        positive_candidate = float(delta)
        classification = active_policy.positive_change_classification
    else:
        positive_candidate = 0.0
        classification = active_policy.negative_change_classification

    scheduled = _next_daily_decision_at_or_after(observation_ts)
    # The baseline is already an accepted daily decision. Never schedule a second
    # decision at that same boundary, even if a new equity observation has the
    # identical 00:00 timestamp.
    if scheduled <= baseline_ts:
        scheduled = baseline_ts + pd.Timedelta(days=1)

    return EquityChangeObservation(
        baseline_decision_timestamp=_canonical_timestamp(baseline_ts),
        observed_at=_canonical_timestamp(observation_ts),
        baseline_equity_usd=baseline_equity,
        observed_equity_usd=observed_equity,
        equity_change_usd=float(delta),
        positive_equity_change_candidate_usd=positive_candidate,
        change_classification=classification,
        source_attributed=False,
        scheduled_daily_decision_timestamp=_canonical_timestamp(scheduled),
        observed_at_daily_boundary=_is_utc_daily_boundary(observation_ts),
        requires_intraday_action=False,
        intraday_target_recalculation_allowed=False,
        intraday_risk_increase_allowed=False,
        contribution_candidate_pending=positive_candidate > 0.0,
    )


def apply_at_daily_decision(
    *,
    observation: EquityChangeObservation,
    daily_dataset: CanonicalDailyDataset,
    account_equity_usd: object,
    current_positions_notional_usd: Mapping[str, object],
    approved_config: ProductConfig | None = None,
    policy: ContributionPolicy | None = None,
) -> ContributionAwareDailyDecision:
    """Include fresh equity through the unchanged P3.2 -> P3.3 daily chain.

    The contribution candidate amount is diagnostic only. The actual allocation is
    based on the *fresh full account equity* observed at the scheduled daily decision,
    so deposits, PnL and any other equity changes are treated consistently by the
    same target engine. No separate contribution allocation formula exists.
    """
    active_policy = policy or load_contribution_policy()
    active_policy.validate()
    decision_ts = _utc_timestamp(daily_dataset.decision_timestamp, field="daily_dataset.decision_timestamp")
    if not _is_utc_daily_boundary(decision_ts):
        raise ContributionHandlingError("daily_dataset decision must be exactly 00:00 UTC")

    scheduled_ts = _utc_timestamp(
        observation.scheduled_daily_decision_timestamp,
        field="observation.scheduled_daily_decision_timestamp",
    )
    if decision_ts != scheduled_ts:
        raise ContributionHandlingError(
            "equity-change observation may be applied only at its scheduled daily decision"
        )

    equity = _finite_float(account_equity_usd, field="account_equity_usd")
    if equity <= 0:
        raise ContributionHandlingError("account_equity_usd must be positive")

    config = approved_config or load_product_config()
    target = calculate_target(
        daily_dataset=daily_dataset,
        account_equity_usd=equity,
        current_positions=current_positions_notional_usd,
        approved_config=config,
    )
    if target.target_engine_version != TARGET_ENGINE_VERSION:
        raise ContributionHandlingError("P3.4 target-engine drift detected")

    control = calculate_rebalance_control(
        target=target,
        account_equity_usd=equity,
        current_positions_notional_usd=current_positions_notional_usd,
    )
    if control.control_version != REBALANCE_CONTROL_VERSION:
        raise ContributionHandlingError("P3.4 rebalance-control drift detected")

    return ContributionAwareDailyDecision(
        decision_timestamp=_canonical_timestamp(decision_ts),
        observation_digest=observation.digest(),
        observed_equity_change_usd=observation.equity_change_usd,
        contribution_candidate_usd=observation.positive_equity_change_candidate_usd,
        contribution_candidate_included=observation.contribution_candidate_pending,
        decision_account_equity_usd=equity,
        target_engine_version=target.target_engine_version,
        target_digest=target.digest(),
        rebalance_control_version=control.control_version,
        rebalance_control_digest=control.digest(),
        target=target,
        rebalance_control=control,
    )
