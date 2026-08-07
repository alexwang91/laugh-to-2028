from __future__ import annotations

import hashlib
import json

import pandas as pd

import p5_1_event_taxonomy as taxonomy
import p5_2_features as features
import run_p5_2_feature_evidence as base


CORRECTION_ID = "P5.2-POST-COMPUTE-SERIALIZATION-R2"
PRIOR_RUN = 31217880218


def _series_frame(series: pd.Series, index_name: str, value_name: str) -> pd.DataFrame:
    """Convert a Series to a two-column frame without pandas-version-specific names= API."""
    frame = series.rename(value_name).to_frame()
    frame.index.name = index_name
    return frame.reset_index()


def _write_results_r2(contract: dict) -> dict:
    taxonomy_payload = taxonomy.load_taxonomy(base.TAXONOMY_PATH)
    daily = base._fetch_daily_panel(contract)
    btc4h = base._fetch_btc_4h(contract)
    resolved = taxonomy.resolve_event_anchors(
        taxonomy_payload,
        {idx.date(): float(value) for idx, value in daily["BTC"].items()},
    )
    feature_panel = features.build_feature_panel(daily, btc4h)
    summary_rows = base._summary_rows(feature_panel, resolved, taxonomy_payload, contract)
    coverage = base._coverage_rows(feature_panel, resolved, taxonomy_payload, contract)
    pending = base._pending_rows(contract)

    failed_coverage = coverage.loc[coverage["status"] != "PASS", "feature"].tolist()
    if failed_coverage:
        raise base.P52Error(f"frozen AVAILABLE_V1 feature coverage failed: {failed_coverage}")

    if base.RESULT_DIR.exists():
        raise base.P52Error("P5.2 result directory already exists")
    base.RESULT_DIR.mkdir(parents=True)

    hashes: dict[str, str] = {}
    daily_frame = daily.copy()
    daily_frame.index.name = "date"
    hashes["daily_close_panel.csv"] = base._write_csv(
        daily_frame.reset_index(), base.RESULT_DIR / "daily_close_panel.csv"
    )
    hashes["btc_4h_close.csv"] = base._write_csv(
        _series_frame(btc4h, "completion_boundary", "close"),
        base.RESULT_DIR / "btc_4h_close.csv",
    )
    feature_frame = feature_panel.copy()
    feature_frame.index.name = "date"
    hashes["feature_panel.csv"] = base._write_csv(
        feature_frame.reset_index(), base.RESULT_DIR / "feature_panel.csv"
    )

    resolved_frame = pd.DataFrame(
        [
            {
                "event_id": event.event_id,
                "event_class": event.event_class,
                "terminal_label": event.terminal_label,
                "anchor_date": event.anchor_date.isoformat(),
                "search_window_start": event.search_window_start.isoformat(),
                "search_window_end": event.search_window_end.isoformat(),
                "outcome_window_end": event.outcome_window_end.isoformat(),
            }
            for event in resolved
        ]
    )
    hashes["resolved_events.csv"] = base._write_csv(
        resolved_frame, base.RESULT_DIR / "resolved_events.csv"
    )
    hashes["event_feature_summary.csv"] = base._write_csv(
        summary_rows, base.RESULT_DIR / "event_feature_summary.csv"
    )
    hashes["feature_coverage.csv"] = base._write_csv(
        coverage, base.RESULT_DIR / "feature_coverage.csv"
    )
    hashes["pending_features.csv"] = base._write_csv(
        pending, base.RESULT_DIR / "pending_features.csv"
    )

    family_counts = summary_rows.groupby("family")["feature"].nunique().to_dict()
    payload = {
        "study_id": "P5.2-FEATURE-FAMILIES-V1",
        "status": "ONE_TIME_FROZEN_FEATURE_EVIDENCE_COMPLETE",
        "production_authorized": False,
        "taxonomy_contract": taxonomy_payload["contract_id"],
        "taxonomy_blob_sha": contract["taxonomy_blob_sha"],
        "feature_contract": contract["contract_id"],
        "data_window": [
            contract["canonical_price_data"]["fetch_start"],
            contract["canonical_price_data"]["fetch_end"],
        ],
        "available_feature_count": int(len(feature_panel.columns)),
        "family_feature_counts": {str(k): int(v) for k, v in family_counts.items()},
        "resolved_event_count": int(len(resolved)),
        "control_event_count": int(
            sum(e.event_class == "HIGH_VOLATILITY_NON_TOP_CONTROL" for e in resolved)
        ),
        "coverage_all_pass": bool((coverage["status"] == "PASS").all()),
        "pending_feature_count": int(len(pending)),
        "selection": {
            "feature_set_selected": False,
            "state_thresholds_selected": False,
            "status": "DESCRIPTIVE_EVIDENCE_ONLY",
        },
        "recovery_provenance": {
            "correction_id": CORRECTION_ID,
            "prior_failed_run": PRIOR_RUN,
            "economic_or_feature_definition_change": False,
            "observed_metrics_used_for_correction": False,
            "reason": "pandas 3.0 Series.reset_index does not accept names=; R2 uses rename/to_frame/index.name/reset_index with identical table semantics",
        },
        "artifact_sha256": hashes,
    }
    summary_path = base.RESULT_DIR / "summary.json"
    summary_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    digest = hashlib.sha256(summary_path.read_bytes()).hexdigest()
    (base.RESULT_DIR / "summary.sha256").write_text(digest + "\n", encoding="utf-8")
    print(f"P5.2 R2 feature evidence complete summary_sha256={digest}")
    return payload


def main() -> None:
    contract = base._load_contract()
    _write_results_r2(contract)


if __name__ == "__main__":
    main()
