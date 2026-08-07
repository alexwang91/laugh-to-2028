from __future__ import annotations

"""R4 blinded post-start implementation correction for LEVERAGE-0040.

Run 31199392883 entered the cap>1 branch, but emitted and committed no candidate
metrics. It failed because the preregistered native-funding evaluation window
starts on 2023-06-18 while P3.3 session semantics require a 2023-06-17 decision
observation to produce the 2023-06-18 return session. The original funding panel
sliced its input frame at 2023-06-18 before the R1 session adapter could use the
required prior decision day.

R4 adds exactly one input/lookback day while keeping the evaluation/funding
window, funding observations, candidate caps, costs, stresses, gates, and every
selection rule unchanged.
"""

import hashlib
import json
from pathlib import Path

import run_leverage_0040_once_r3 as r3

base = r3.base

CORRECTION_PATH = Path(__file__).with_name(
    "LEVERAGE-0040-BLINDED-RUN-CORRECTION-R4.json"
)


def _funding_inputs_r4(prices, candidate_targets, matched_targets):
    input_start = base.COMMON_FUNDING_START - __import__("pandas").Timedelta(days=1)
    px = prices.loc[input_start : base.COMMON_FUNDING_END]
    if input_start not in px.index:
        raise RuntimeError(
            "R4 funding session alignment requires the prior decision day "
            f"{input_start.date()}"
        )
    if base.COMMON_FUNDING_START not in px.index:
        raise RuntimeError("R4 funding window start missing from price frame")
    ct = candidate_targets.reindex(px.index).ffill()
    mt = matched_targets.reindex(px.index).ffill()
    if ct.loc[input_start].isna().any() or mt.loc[input_start].isna().any():
        raise RuntimeError("R4 prior-day funding targets are unavailable")
    return px, ct, mt


def _funding_panel_r4(prices, candidate_targets, matched_targets, legacy_ref, native, proxy):
    px, ct, mt = _funding_inputs_r4(prices, candidate_targets, matched_targets)
    rows = {}
    for spike in base.FUNDING_SPIKES:
        m = base.simulate_p3_3_economic_path(
            mt,
            px,
            start=base.COMMON_FUNDING_START,
            end=base.COMMON_FUNDING_END,
            cost_bps=5.0,
            funding_blocks_by_session=native,
            adverse_funding_spike_multiplier=spike,
            base_btc_fully_spot=True,
        )
        c = base.simulate_p3_3_economic_path(
            ct,
            px,
            start=base.COMMON_FUNDING_START,
            end=base.COMMON_FUNDING_END,
            cost_bps=5.0,
            funding_blocks_by_session=native,
            adverse_funding_spike_multiplier=spike,
            matched_cap1_held=m.held_weights,
        )
        cm, mm = base.path_metrics(c), base.path_metrics(m)
        rows[str(spike)] = {
            "candidate": cm,
            "matched_cap1": mm,
            "pass": cm["end_multiple"] >= mm["end_multiple"]
            and cm["max_drawdown"] > -0.70,
        }

    ma = base.simulate_p3_3_economic_path(
        mt,
        px,
        start=base.COMMON_FUNDING_START,
        end=base.COMMON_FUNDING_END,
        cost_bps=5.0,
        funding_blocks_by_session=native,
        all_perp=True,
    )
    ca = base.simulate_p3_3_economic_path(
        ct,
        px,
        start=base.COMMON_FUNDING_START,
        end=base.COMMON_FUNDING_END,
        cost_bps=5.0,
        funding_blocks_by_session=native,
        all_perp=True,
    )
    allp = {
        "candidate": base.path_metrics(ca),
        "matched_cap1": base.path_metrics(ma),
    }
    allp["pass"] = allp["candidate"]["max_drawdown"] > -0.70

    mp = base.simulate_p3_3_economic_path(
        mt,
        px,
        start=base.COMMON_FUNDING_START,
        end=base.COMMON_FUNDING_END,
        cost_bps=5.0,
        funding_blocks_by_session=proxy,
        base_btc_fully_spot=True,
    )
    cp = base.simulate_p3_3_economic_path(
        ct,
        px,
        start=base.COMMON_FUNDING_START,
        end=base.COMMON_FUNDING_END,
        cost_bps=5.0,
        funding_blocks_by_session=proxy,
        matched_cap1_held=mp.held_weights,
    )
    proxy_report = {
        "role": "REPORT_ONLY_BINANCE_PROXY_NOT_HYPERLIQUID_LEVEL",
        "candidate": base.path_metrics(cp),
        "matched_cap1": base.path_metrics(mp),
    }
    return {
        "native_hyperliquid": rows,
        "all_perp_stress": allp,
        "binance_proxy_report_only": proxy_report,
        "pass": all(x["pass"] for x in rows.values()) and allp["pass"],
        "legacy_reference": legacy_ref,
    }


def _augment_r4_evidence() -> None:
    summary = base.RESULT_DIR / "summary.json"
    digest_file = base.RESULT_DIR / "summary.sha256"
    if not summary.exists():
        return
    payload = json.loads(summary.read_text(encoding="utf-8"))
    evidence = payload.setdefault("input_evidence", {})
    corrections = list(evidence.get("blinded_post_start_corrections", []))
    if "BLINDED-FUNDING-SESSION-005" not in corrections:
        corrections.append("BLINDED-FUNDING-SESSION-005")
    evidence["blinded_post_start_corrections"] = corrections
    evidence["runner_entrypoint"] = (
        "research/leverage_0040/run_leverage_0040_once_r4.py"
    )
    evidence["r4_correction_sha256"] = hashlib.sha256(
        CORRECTION_PATH.read_bytes()
    ).hexdigest()
    provenance = payload.setdefault("execution_provenance", {})
    provenance["r4_blinded_recovery"] = {
        "failed_run_id": 31199392883,
        "failed_head": "afcc1beb35f9d924cba6dd0330bdf8d290d8285c",
        "cap_gt_1_partial_computation_occurred": True,
        "candidate_metrics_emitted_before_failure": False,
        "candidate_metrics_committed_before_failure": False,
        "correction_basis": "preregistered funding window and frozen P3.3 session timing",
        "result_driven_retuning": False,
    }
    summary.write_text(
        json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8"
    )
    digest = hashlib.sha256(summary.read_bytes()).hexdigest()
    digest_file.write_text(digest + "\n", encoding="utf-8")
    print(f"LEVERAGE-0040 R4 immutable summary_sha256={digest}")


def main() -> None:
    base._funding_panel = _funding_panel_r4
    r3.main()
    _augment_r4_evidence()


if __name__ == "__main__":
    main()
