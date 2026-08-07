from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[3]
P5 = ROOT / "research" / "cycle_exit"
if str(P5) not in sys.path:
    sys.path.insert(0, str(P5))

import p5_1_event_taxonomy as taxonomy


TAXONOMY_PATH = P5 / "p5_1_event_taxonomy.json"


def _load() -> dict:
    return json.loads(TAXONOMY_PATH.read_text(encoding="utf-8"))


def _daily_closes(start: date, end: date, base: float = 100.0) -> dict[date, float]:
    values: dict[date, float] = {}
    day = start
    i = 0
    while day <= end:
        values[day] = base + i
        day += timedelta(days=1)
        i += 1
    return values


def test_p5_1_taxonomy_is_frozen_before_feature_selection_and_non_production():
    payload = _load()
    taxonomy.validate_taxonomy(payload)
    assert payload["contract_id"] == "P5.1-EVENT-TAXONOMY-V1"
    assert payload["status"] == "FROZEN_BEFORE_FEATURE_SELECTION"
    assert payload["base_main"] == "b61a368383d08b83d04a2aec52777cf31196efac"
    assert payload["roadmap_decision"] == "PRODUCT-CYCLE-EXIT-2026-08-05"
    assert payload["research_integrity"]["feature_or_model_performance_used_to_choose_windows"] is False
    assert payload["research_integrity"]["production_authorization"] == "NONE"


def test_required_2021_and_2025_roadmap_roles_are_present():
    payload = _load()
    roles = {event["roadmap_role"] for event in payload["events"] if event["required"]}
    assert roles == taxonomy.REQUIRED_ROADMAP_ROLES


def test_only_one_explicit_terminal_top_and_2025_is_not_silently_terminal():
    payload = _load()
    terminal = [event for event in payload["events"] if event["terminal_label"]]
    assert [event["event_id"] for event in terminal] == ["P5E-2021-NOV-TERMINAL-TOP"]
    assert all(
        not event["terminal_label"]
        for event in payload["events"]
        if event["year"] == 2025
    )


def test_taxonomy_has_multiple_non_top_high_volatility_controls():
    payload = _load()
    controls = [
        event
        for event in payload["events"]
        if event["event_class"] == "HIGH_VOLATILITY_NON_TOP_CONTROL"
    ]
    assert len(controls) >= payload["minimum_non_top_controls"] >= 3
    assert {event["year"] for event in controls} >= {2021, 2024, 2025}


def test_evaluation_buckets_measure_7_to_14_day_lead_without_forcing_it():
    payload = _load()
    assert payload["evaluation_buckets_relative_to_anchor_calendar_days"]["target_lead"] == [-14, -7]
    assert "not required" in payload["lead_time_policy"] or "not required" in payload["lead_time_policy"].lower()


def test_max_close_anchor_uses_earliest_tie():
    payload = {
        **_load(),
        "events": [
            {
                "event_id": "P5E-2021-SPRING-MAJOR-TOP",
                "year": 2021,
                "event_class": "LOCAL_MAJOR_TOP_NONTERMINAL",
                "search_window_start": "2021-03-15",
                "search_window_end": "2021-05-15",
                "anchor_rule": "BTC_CLOSE_MAX_IN_SEARCH_WINDOW",
                "outcome_window_end": "2021-07-31",
                "roadmap_role": "spring first major top / May crash",
                "terminal_label": False,
                "required": True,
            },
            {
                "event_id": "P5E-2021-SUMMER-SECOND-WIND",
                "year": 2021,
                "event_class": "SECOND_WIND_TRANSITION",
                "search_window_start": "2021-05-16",
                "search_window_end": "2021-07-31",
                "anchor_rule": "BTC_CLOSE_MIN_IN_SEARCH_WINDOW",
                "outcome_window_end": "2021-10-31",
                "roadmap_role": "summer recovery / second-wind transition",
                "terminal_label": False,
                "required": True,
            },
            {
                "event_id": "P5E-2021-NOV-TERMINAL-TOP",
                "year": 2021,
                "event_class": "TERMINAL_TOP_BEAR_TRANSITION",
                "search_window_start": "2021-10-01",
                "search_window_end": "2021-11-30",
                "anchor_rule": "BTC_CLOSE_MAX_IN_SEARCH_WINDOW",
                "outcome_window_end": "2022-03-31",
                "roadmap_role": "November terminal peak / bear transition",
                "terminal_label": True,
                "required": True,
            },
            {
                "event_id": "P5E-2025-JUNE-NEW-HIGH",
                "year": 2025,
                "event_class": "TEMPORARY_NEW_HIGH_PHASE",
                "search_window_start": "2025-05-01",
                "search_window_end": "2025-06-30",
                "anchor_rule": "BTC_CLOSE_MAX_IN_SEARCH_WINDOW",
                "outcome_window_end": "2025-08-31",
                "roadmap_role": "June new-high phase",
                "terminal_label": False,
                "required": True,
            },
            {
                "event_id": "P5E-2025-AUG-NEW-HIGH",
                "year": 2025,
                "event_class": "SECOND_WIND_NEW_HIGH_PHASE",
                "search_window_start": "2025-07-01",
                "search_window_end": "2025-08-31",
                "anchor_rule": "BTC_CLOSE_MAX_IN_SEARCH_WINDOW",
                "outcome_window_end": "2025-10-31",
                "roadmap_role": "August new-high phase",
                "terminal_label": False,
                "required": True,
            },
            {
                "event_id": "P5E-2025-OCT-NEW-HIGH-DELEVERAGING",
                "year": 2025,
                "event_class": "NEW_HIGH_DELEVERAGING_PHASE",
                "search_window_start": "2025-09-01",
                "search_window_end": "2025-10-31",
                "anchor_rule": "BTC_CLOSE_MAX_IN_SEARCH_WINDOW",
                "outcome_window_end": "2025-12-31",
                "roadmap_role": "October new-high and deleveraging phase",
                "terminal_label": False,
                "required": True,
            },
            {
                "event_id": "P5E-2025-LATE-DETERIORATION",
                "year": 2025,
                "event_class": "POST_DELEVERAGING_DETERIORATION",
                "search_window_start": "2025-10-01",
                "search_window_end": "2025-12-31",
                "anchor_rule": "PARENT_EVENT_ANCHOR",
                "parent_event_id": "P5E-2025-OCT-NEW-HIGH-DELEVERAGING",
                "outcome_window_end": "2025-12-31",
                "roadmap_role": "subsequent late-2025 deterioration",
                "terminal_label": False,
                "required": True,
            },
            {
                "event_id": "P5C-2024-MAR-MAY-MASKING",
                "year": 2024,
                "event_class": "HIGH_VOLATILITY_NON_TOP_CONTROL",
                "search_window_start": "2024-03-01",
                "search_window_end": "2024-05-15",
                "anchor_rule": "MAX_10D_DRAWDOWN_END",
                "outcome_window_end": "2024-08-31",
                "roadmap_role": "non-top control reusing the previously registered 2024 April masking/stress episode window",
                "terminal_label": False,
                "required": False,
            },
            {
                "event_id": "P5C-2021-JAN-FEB-HIGH-VOL",
                "year": 2021,
                "event_class": "HIGH_VOLATILITY_NON_TOP_CONTROL",
                "search_window_start": "2021-01-01",
                "search_window_end": "2021-02-28",
                "anchor_rule": "MAX_10D_DRAWDOWN_END",
                "outcome_window_end": "2021-05-15",
                "roadmap_role": "control-a",
                "terminal_label": False,
                "required": False,
            },
            {
                "event_id": "P5C-2021-SEP-HIGH-VOL",
                "year": 2021,
                "event_class": "HIGH_VOLATILITY_NON_TOP_CONTROL",
                "search_window_start": "2021-08-20",
                "search_window_end": "2021-10-15",
                "anchor_rule": "MAX_10D_DRAWDOWN_END",
                "outcome_window_end": "2021-11-30",
                "roadmap_role": "control-b",
                "terminal_label": False,
                "required": False,
            },
        ],
        "minimum_non_top_controls": 3,
    }
    start = date(2020, 12, 23)
    end = date(2025, 12, 31)
    closes = _daily_closes(start, end)
    closes[date(2021, 4, 10)] = 10000.0
    closes[date(2021, 4, 11)] = 10000.0
    resolved = taxonomy.resolve_event_anchors(payload, closes)
    spring = next(event for event in resolved if event.event_id == "P5E-2021-SPRING-MAJOR-TOP")
    assert spring.anchor_date == date(2021, 4, 10)


def test_parent_event_reuses_parent_anchor():
    payload = _load()
    closes = _daily_closes(date(2020, 12, 23), date(2025, 12, 31))
    resolved = taxonomy.resolve_event_anchors(payload, closes)
    by_id = {event.event_id: event for event in resolved}
    assert by_id["P5E-2025-LATE-DETERIORATION"].anchor_date == by_id[
        "P5E-2025-OCT-NEW-HIGH-DELEVERAGING"
    ].anchor_date


def test_missing_daily_btc_data_fails_closed():
    payload = _load()
    closes = _daily_closes(date(2020, 12, 23), date(2025, 12, 31))
    del closes[date(2021, 4, 1)]
    with pytest.raises(taxonomy.TaxonomyError, match="missing canonical BTC close"):
        taxonomy.resolve_event_anchors(payload, closes)
