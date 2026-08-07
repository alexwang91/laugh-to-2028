from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RESULT_DIR = ROOT / "research" / "results" / "p5_2_feature_evidence"
OUT_DIR = ROOT / "research" / "analysis" / "p5_2_closeout"

SUMMARY_PATH = RESULT_DIR / "summary.json"
EVENT_PATH = RESULT_DIR / "event_feature_summary.csv"
COVERAGE_PATH = RESULT_DIR / "feature_coverage.csv"
PENDING_PATH = RESULT_DIR / "pending_features.csv"

TERMINAL = ["P5E-2021-NOV-TERMINAL-TOP"]
SECOND_WIND = ["P5E-2021-SUMMER-SECOND-WIND", "P5E-2025-AUG-NEW-HIGH"]
NONTERMINAL_TOPLIKE = [
    "P5E-2021-SPRING-MAJOR-TOP",
    "P5E-2025-JUNE-NEW-HIGH",
    "P5E-2025-OCT-NEW-HIGH-DELEVERAGING",
]
DETERIORATION = ["P5E-2025-LATE-DETERIORATION"]
PRIMARY_BUCKETS = ["target_lead", "near_event"]


def _require_result() -> dict:
    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    assert summary["status"] == "ONE_TIME_FROZEN_FEATURE_EVIDENCE_COMPLETE"
    assert summary["selection"]["feature_set_selected"] is False
    assert summary["selection"]["state_thresholds_selected"] is False
    assert summary["production_authorized"] is False
    return summary


def _median_abs_z(frame: pd.DataFrame, event_ids: list[str], bucket: str, feature: str) -> float:
    x = frame.loc[
        frame["event_id"].isin(event_ids)
        & frame["bucket"].eq(bucket)
        & frame["feature"].eq(feature),
        "robust_z_vs_controls",
    ].dropna()
    return float(x.abs().median()) if len(x) else float("nan")


def _median_signed_z(frame: pd.DataFrame, event_ids: list[str], bucket: str, feature: str) -> float:
    x = frame.loc[
        frame["event_id"].isin(event_ids)
        & frame["bucket"].eq(bucket)
        & frame["feature"].eq(feature),
        "robust_z_vs_controls",
    ].dropna()
    return float(x.median()) if len(x) else float("nan")


def build_feature_diagnostics(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for feature, sub in frame.groupby("feature", sort=True):
        family = str(sub["family"].iloc[0])
        row = {"feature": feature, "family": family}
        for bucket in PRIMARY_BUCKETS:
            row[f"{bucket}_terminal_z"] = _median_signed_z(frame, TERMINAL, bucket, feature)
            row[f"{bucket}_terminal_abs_z"] = _median_abs_z(frame, TERMINAL, bucket, feature)
            row[f"{bucket}_second_wind_median_z"] = _median_signed_z(frame, SECOND_WIND, bucket, feature)
            row[f"{bucket}_second_wind_median_abs_z"] = _median_abs_z(frame, SECOND_WIND, bucket, feature)
            row[f"{bucket}_nonterminal_toplike_median_z"] = _median_signed_z(frame, NONTERMINAL_TOPLIKE, bucket, feature)
            row[f"{bucket}_nonterminal_toplike_median_abs_z"] = _median_abs_z(frame, NONTERMINAL_TOPLIKE, bucket, feature)
            row[f"{bucket}_deterioration_z"] = _median_signed_z(frame, DETERIORATION, bucket, feature)
            row[f"{bucket}_deterioration_abs_z"] = _median_abs_z(frame, DETERIORATION, bucket, feature)

        primary = sub.loc[sub["bucket"].isin(PRIMARY_BUCKETS) & ~sub["event_id"].str.startswith("P5C-")]
        z = primary["robust_z_vs_controls"].dropna().astype(float)
        row["primary_valid_z_count"] = int(len(z))
        row["primary_median_abs_z"] = float(z.abs().median()) if len(z) else float("nan")
        row["primary_p90_abs_z"] = float(z.abs().quantile(0.90)) if len(z) else float("nan")
        row["primary_max_abs_z"] = float(z.abs().max()) if len(z) else float("nan")
        row["primary_abs_z_ge_1_count"] = int((z.abs() >= 1.0).sum())
        row["primary_abs_z_ge_2_count"] = int((z.abs() >= 2.0).sum())
        rows.append(row)
    return pd.DataFrame(rows).sort_values(["family", "feature"]).reset_index(drop=True)


def build_family_diagnostics(frame: pd.DataFrame) -> pd.DataFrame:
    primary = frame.loc[frame["bucket"].isin(PRIMARY_BUCKETS) & ~frame["event_id"].str.startswith("P5C-")].copy()
    primary["abs_z"] = primary["robust_z_vs_controls"].abs()
    rows = []
    for family, sub in primary.groupby("family", sort=True):
        z = sub["abs_z"].dropna().astype(float)
        rows.append(
            {
                "family": family,
                "valid_z_count": int(len(z)),
                "median_abs_z": float(z.median()) if len(z) else float("nan"),
                "p75_abs_z": float(z.quantile(0.75)) if len(z) else float("nan"),
                "p90_abs_z": float(z.quantile(0.90)) if len(z) else float("nan"),
                "max_abs_z": float(z.max()) if len(z) else float("nan"),
                "abs_z_ge_1_count": int((z >= 1.0).sum()),
                "abs_z_ge_2_count": int((z >= 2.0).sum()),
            }
        )
    return pd.DataFrame(rows).sort_values("median_abs_z", ascending=False).reset_index(drop=True)


def _rank_context(frame: pd.DataFrame, context: str, event_ids: list[str], bucket: str) -> list[dict]:
    sub = frame.loc[frame["event_id"].isin(event_ids) & frame["bucket"].eq(bucket)].copy()
    grouped = (
        sub.groupby(["feature", "family"], as_index=False)["robust_z_vs_controls"]
        .median()
        .dropna()
    )
    grouped["abs_z"] = grouped["robust_z_vs_controls"].abs()
    grouped = grouped.sort_values(["abs_z", "feature"], ascending=[False, True]).head(10)
    return [
        {
            "context": context,
            "bucket": bucket,
            "rank": rank,
            "feature": str(row.feature),
            "family": str(row.family),
            "median_robust_z": float(row.robust_z_vs_controls),
            "abs_median_robust_z": float(row.abs_z),
        }
        for rank, row in enumerate(grouped.itertuples(index=False), start=1)
    ]


def build_context_rankings(frame: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    groups = [
        ("TERMINAL", TERMINAL),
        ("SECOND_WIND", SECOND_WIND),
        ("NONTERMINAL_TOPLIKE", NONTERMINAL_TOPLIKE),
        ("DETERIORATION", DETERIORATION),
    ]
    for context, ids in groups:
        for bucket in PRIMARY_BUCKETS:
            rows.extend(_rank_context(frame, context, ids, bucket))
    return pd.DataFrame(rows)


def main() -> None:
    summary = _require_result()
    frame = pd.read_csv(EVENT_PATH)
    coverage = pd.read_csv(COVERAGE_PATH)
    pending = pd.read_csv(PENDING_PATH)

    assert coverage["status"].eq("PASS").all()
    assert len(frame["feature"].unique()) == summary["available_feature_count"] == 29
    assert len(pending) == summary["pending_feature_count"] == 6

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    feature_diag = build_feature_diagnostics(frame)
    family_diag = build_family_diagnostics(frame)
    rankings = build_context_rankings(frame)

    feature_diag.to_csv(OUT_DIR / "feature_diagnostics.csv", index=False, float_format="%.12g")
    family_diag.to_csv(OUT_DIR / "family_diagnostics.csv", index=False, float_format="%.12g")
    rankings.to_csv(OUT_DIR / "context_rankings.csv", index=False, float_format="%.12g")

    meta = {
        "source_study": summary["study_id"],
        "source_summary_sha256": (RESULT_DIR / "summary.sha256").read_text().strip(),
        "analysis_status": "POST_RESULT_DESCRIPTIVE_DIAGNOSTICS_ONLY",
        "selection_or_threshold_authority": "NONE",
        "primary_buckets": PRIMARY_BUCKETS,
        "event_groups": {
            "TERMINAL": TERMINAL,
            "SECOND_WIND": SECOND_WIND,
            "NONTERMINAL_TOPLIKE": NONTERMINAL_TOPLIKE,
            "DETERIORATION": DETERIORATION,
        },
        "important_limitation": "Only one explicit terminal event exists in P5.1 V1; terminal-specific rankings are hypothesis-generating and cannot establish cross-cycle terminal robustness.",
    }
    (OUT_DIR / "analysis_metadata.json").write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("P5.2 closeout descriptive diagnostics complete")


if __name__ == "__main__":
    main()
