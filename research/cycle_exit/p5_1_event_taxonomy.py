from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Iterable, Mapping


CONTRACT_ID = "P5.1-EVENT-TAXONOMY-V1"
ALLOWED_ANCHOR_RULES = {
    "BTC_CLOSE_MAX_IN_SEARCH_WINDOW",
    "BTC_CLOSE_MIN_IN_SEARCH_WINDOW",
    "MAX_10D_DRAWDOWN_END",
    "PARENT_EVENT_ANCHOR",
}
REQUIRED_ROADMAP_ROLES = {
    "spring first major top / May crash",
    "summer recovery / second-wind transition",
    "November terminal peak / bear transition",
    "June new-high phase",
    "August new-high phase",
    "October new-high and deleveraging phase",
    "subsequent late-2025 deterioration",
}


class TaxonomyError(ValueError):
    pass


@dataclass(frozen=True)
class ResolvedEvent:
    event_id: str
    event_class: str
    anchor_date: date
    search_window_start: date
    search_window_end: date
    outcome_window_end: date
    terminal_label: bool


def _as_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError) as exc:
        raise TaxonomyError(f"invalid YYYY-MM-DD date: {value!r}") from exc


def load_taxonomy(path: str | Path) -> dict:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_taxonomy(payload)
    return payload


def validate_taxonomy(payload: Mapping) -> None:
    if payload.get("contract_id") != CONTRACT_ID:
        raise TaxonomyError("unexpected contract_id")
    if payload.get("status") != "FROZEN_BEFORE_FEATURE_SELECTION":
        raise TaxonomyError("taxonomy must be frozen before feature selection")

    integrity = payload.get("research_integrity", {})
    required_integrity = {
        "event_windows_frozen_before_p5_2_feature_selection": True,
        "feature_or_model_performance_used_to_choose_windows": False,
        "feature_values_after_each_evaluation_date_may_not_be_used": True,
        "no_brrk_retune": True,
        "no_leverage_rescue": True,
    }
    for key, expected in required_integrity.items():
        if integrity.get(key) is not expected:
            raise TaxonomyError(f"research_integrity.{key} must be {expected!r}")
    if integrity.get("production_authorization") != "NONE":
        raise TaxonomyError("P5.1 cannot authorize production")

    events = payload.get("events")
    if not isinstance(events, list) or not events:
        raise TaxonomyError("events must be a non-empty list")

    ids: set[str] = set()
    roles: set[str] = set()
    class_counts: dict[str, int] = {}
    event_by_id: dict[str, Mapping] = {}
    required_classes = set(payload.get("required_event_classes", []))

    for event in events:
        event_id = event.get("event_id")
        if not isinstance(event_id, str) or not event_id:
            raise TaxonomyError("each event requires event_id")
        if event_id in ids:
            raise TaxonomyError(f"duplicate event_id: {event_id}")
        ids.add(event_id)
        event_by_id[event_id] = event

        event_class = event.get("event_class")
        if event_class not in required_classes:
            raise TaxonomyError(f"unknown event_class for {event_id}: {event_class}")
        class_counts[event_class] = class_counts.get(event_class, 0) + 1

        role = event.get("roadmap_role")
        if isinstance(role, str):
            roles.add(role)

        start = _as_date(event.get("search_window_start"))
        end = _as_date(event.get("search_window_end"))
        outcome_end = _as_date(event.get("outcome_window_end"))
        if start > end:
            raise TaxonomyError(f"search window inverted for {event_id}")
        if outcome_end < end and event.get("anchor_rule") != "PARENT_EVENT_ANCHOR":
            raise TaxonomyError(f"outcome window ends before search window for {event_id}")

        anchor_rule = event.get("anchor_rule")
        if anchor_rule not in ALLOWED_ANCHOR_RULES:
            raise TaxonomyError(f"invalid anchor rule for {event_id}: {anchor_rule}")
        if anchor_rule == "PARENT_EVENT_ANCHOR" and not event.get("parent_event_id"):
            raise TaxonomyError(f"parent_event_id required for {event_id}")

        terminal = event.get("terminal_label")
        if not isinstance(terminal, bool):
            raise TaxonomyError(f"terminal_label must be boolean for {event_id}")
        if terminal and event_class != "TERMINAL_TOP_BEAR_TRANSITION":
            raise TaxonomyError(f"terminal label assigned outside terminal class: {event_id}")
        if event_class == "TERMINAL_TOP_BEAR_TRANSITION" and not terminal:
            raise TaxonomyError(f"terminal class must carry terminal_label=true: {event_id}")

    missing_roles = REQUIRED_ROADMAP_ROLES - roles
    if missing_roles:
        raise TaxonomyError(f"missing required roadmap roles: {sorted(missing_roles)}")

    if class_counts.get("TERMINAL_TOP_BEAR_TRANSITION", 0) != 1:
        raise TaxonomyError("v1 taxonomy must contain exactly one explicit terminal top")
    if class_counts.get("HIGH_VOLATILITY_NON_TOP_CONTROL", 0) < int(
        payload.get("minimum_non_top_controls", 0)
    ):
        raise TaxonomyError("insufficient non-top high-volatility controls")

    for event in events:
        parent_id = event.get("parent_event_id")
        if parent_id and parent_id not in event_by_id:
            raise TaxonomyError(f"unknown parent_event_id for {event['event_id']}: {parent_id}")
        if parent_id == event.get("event_id"):
            raise TaxonomyError(f"self-parent event: {parent_id}")

    buckets = payload.get("evaluation_buckets_relative_to_anchor_calendar_days", {})
    expected_buckets = {
        "early_warning": [-28, -15],
        "target_lead": [-14, -7],
        "near_event": [-6, 0],
        "immediate_after": [1, 28],
        "medium_after": [29, 90],
    }
    if buckets != expected_buckets:
        raise TaxonomyError("evaluation buckets changed from frozen v1 contract")


def _normalize_closes(closes: Mapping[date | str, float]) -> dict[date, float]:
    normalized: dict[date, float] = {}
    for raw_day, raw_close in closes.items():
        day = raw_day if isinstance(raw_day, date) else _as_date(str(raw_day))
        value = float(raw_close)
        if value <= 0:
            raise TaxonomyError(f"non-positive BTC close on {day}: {value}")
        normalized[day] = value
    return normalized


def _require_contiguous_days(closes: Mapping[date, float], start: date, end: date) -> None:
    day = start
    while day <= end:
        if day not in closes:
            raise TaxonomyError(f"missing canonical BTC close for {day}")
        day += timedelta(days=1)


def _resolve_max_or_min(
    closes: Mapping[date, float], start: date, end: date, *, choose_max: bool
) -> date:
    _require_contiguous_days(closes, start, end)
    days = list(_date_range(start, end))
    chooser = max if choose_max else min
    target = chooser(closes[day] for day in days)
    return next(day for day in days if closes[day] == target)


def _resolve_max_10d_drawdown_end(
    closes: Mapping[date, float], start: date, end: date
) -> date:
    lookback_start = start - timedelta(days=9)
    _require_contiguous_days(closes, lookback_start, end)
    best_day: date | None = None
    best_drawdown: float | None = None
    for day in _date_range(start, end):
        trailing = [closes[day - timedelta(days=i)] for i in range(10)]
        peak = max(trailing)
        drawdown = closes[day] / peak - 1.0
        if best_drawdown is None or drawdown < best_drawdown:
            best_drawdown = drawdown
            best_day = day
    assert best_day is not None
    return best_day


def _date_range(start: date, end: date) -> Iterable[date]:
    day = start
    while day <= end:
        yield day
        day += timedelta(days=1)


def resolve_event_anchors(
    payload: Mapping, closes: Mapping[date | str, float]
) -> list[ResolvedEvent]:
    validate_taxonomy(payload)
    btc_closes = _normalize_closes(closes)
    resolved_dates: dict[str, date] = {}
    resolved: list[ResolvedEvent] = []

    unresolved = list(payload["events"])
    while unresolved:
        progressed = False
        for event in list(unresolved):
            event_id = event["event_id"]
            start = _as_date(event["search_window_start"])
            end = _as_date(event["search_window_end"])
            outcome_end = _as_date(event["outcome_window_end"])
            rule = event["anchor_rule"]

            if rule == "BTC_CLOSE_MAX_IN_SEARCH_WINDOW":
                anchor = _resolve_max_or_min(btc_closes, start, end, choose_max=True)
            elif rule == "BTC_CLOSE_MIN_IN_SEARCH_WINDOW":
                anchor = _resolve_max_or_min(btc_closes, start, end, choose_max=False)
            elif rule == "MAX_10D_DRAWDOWN_END":
                anchor = _resolve_max_10d_drawdown_end(btc_closes, start, end)
            else:
                parent_id = event["parent_event_id"]
                if parent_id not in resolved_dates:
                    continue
                anchor = resolved_dates[parent_id]

            resolved_dates[event_id] = anchor
            resolved.append(
                ResolvedEvent(
                    event_id=event_id,
                    event_class=event["event_class"],
                    anchor_date=anchor,
                    search_window_start=start,
                    search_window_end=end,
                    outcome_window_end=outcome_end,
                    terminal_label=event["terminal_label"],
                )
            )
            unresolved.remove(event)
            progressed = True

        if not progressed:
            blocked = [event["event_id"] for event in unresolved]
            raise TaxonomyError(f"unresolvable parent dependency: {blocked}")

    return resolved
