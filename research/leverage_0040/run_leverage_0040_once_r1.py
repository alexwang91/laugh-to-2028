from __future__ import annotations

"""Corrected pre-result entrypoint for the one-time LEVERAGE-0040 study.

Contract workflow #1 proved, before any cap>1 candidate construction, that the
initial wiring incorrectly tried to infer BRRK defensive scale from two
independently banded published holdings paths.  This R1 entrypoint fixes only
that implementation wiring and the corresponding evaluation-session timing:

* rebuild frozen V1 raw targets and BRRK-0011 defensive scale from the
  authoritative research source;
* keep XRP feature-only while target/tradable assets remain BTC/ETH/SOL/BNB;
* interpret a requested evaluation start as a return-session start, so the
  first decision occurs one UTC day earlier.

No LEVERAGE-0040 cap>1 result existed before this file was committed.
"""

import hashlib
import json
from pathlib import Path
import sys

import pandas as pd

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
CORE = RESEARCH / "core"
HYBRID = RESEARCH / "hybrid_meta"
REGIME = RESEARCH / "regime_kelly"
DISPERSION = RESEARCH / "dispersion_overlay"
for p in (RESEARCH, CORE, HYBRID, REGIME, DISPERSION, HERE):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import crypto_rotation_backtest as bt  # noqa: E402
from config import RegimeKellyConfig  # noqa: E402
from features_no_dominance import build_features_no_dominance  # noqa: E402
from run_dispersion_overlay import build_brrk0011_scale  # noqa: E402
from walkforward_v1_meta import (  # noqa: E402
    END as FROZEN_END,
    START as FROZEN_START,
    build_benchmark_v1,
    portfolio_returns_full,
)
import run_leverage_0040_once as base  # noqa: E402
import study_core as core  # noqa: E402


FEATURE_ASSETS = ("BTC", "ETH", "SOL", "BNB", "XRP")
_feature_prices_cache: pd.DataFrame | None = None
_target_authority_meta: dict[str, object] = {}


def _feature_prices_sha256(frame: pd.DataFrame) -> str:
    payload = frame.to_csv(index=True, float_format="%.12f", lineterminator="\n").encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _fetch_prices_corrected() -> pd.DataFrame:
    global _feature_prices_cache
    bt.START_DATE = FROZEN_START
    bt.END_DATE = str(FROZEN_END.date())
    feature_prices = pd.DataFrame(
        {asset: bt.fetch_daily(f"{asset}USDT") for asset in FEATURE_ASSETS}
    ).dropna().sort_index().loc[:FROZEN_END]
    required = pd.date_range(feature_prices.index.min(), base.FULL_END, freq="D")
    if not required.isin(feature_prices.index).all():
        raise RuntimeError("feature-price history is not contiguous through study end")
    if base.FULL_END not in feature_prices.index:
        raise RuntimeError("feature-price history does not reach frozen study end")
    _feature_prices_cache = feature_prices.loc[:, list(FEATURE_ASSETS)].copy()
    return _feature_prices_cache.loc[:, list(core.ASSETS)].copy()


def _load_frozen_targets_corrected():
    global _target_authority_meta
    if _feature_prices_cache is None:
        _fetch_prices_corrected()
    assert _feature_prices_cache is not None

    cfg = RegimeKellyConfig(hmm_restarts=3, hmm_iter=250)
    feature_prices = _feature_prices_cache.loc[:, list(cfg.assets)].copy()
    if tuple(cfg.assets) != FEATURE_ASSETS:
        raise RuntimeError(
            f"frozen BRRK feature universe drifted: expected={FEATURE_ASSETS} actual={tuple(cfg.assets)}"
        )

    features = build_features_no_dominance(feature_prices, cfg)
    v1_raw_all = build_benchmark_v1(feature_prices)
    v1_banded_for_model = bt.apply_band(v1_raw_all, 0.05)
    v1_returns_model, _, _ = portfolio_returns_full(feature_prices, v1_banded_for_model)
    defensive_scale, decision_dates, decisions = build_brrk0011_scale(
        feature_prices,
        features,
        v1_returns_model,
        cfg,
    )
    if not decision_dates:
        raise RuntimeError("frozen BRRK authority returned no decision dates")

    evaluation_start = pd.Timestamp(decision_dates[0]) + pd.Timedelta(days=1)
    if evaluation_start != base.FULL_START:
        raise RuntimeError(
            f"frozen BRRK evaluation start drifted: expected={base.FULL_START.date()} "
            f"actual={evaluation_start.date()}"
        )
    if ((defensive_scale < -1e-12) | (defensive_scale > 1.0 + 1e-12)).any():
        raise RuntimeError("authoritative rebuilt defensive scale left frozen [0,1] range")

    v1_raw = v1_raw_all.loc[:, list(core.ASSETS)].copy()
    brrk_raw = v1_raw.mul(defensive_scale.reindex(v1_raw.index), axis=0)
    if (brrk_raw.abs().sum(axis=1) > 1.0 + 1e-9).any():
        raise RuntimeError("rebuilt raw BRRK target gross exceeded 1.0")

    _target_authority_meta = {
        "feature_assets": list(FEATURE_ASSETS),
        "target_assets": list(core.ASSETS),
        "first_decision_date": str(pd.Timestamp(decision_dates[0]).date()),
        "evaluation_start_session": str(evaluation_start.date()),
        "decision_count": int(len(decision_dates)),
        "feature_price_frame_sha256": _feature_prices_sha256(feature_prices),
        "last_decision": decisions[-1],
        "published_banded_weights_used_for_scale": False,
    }
    return v1_raw, brrk_raw, defensive_scale.reindex(v1_raw.index).astype(float)


def _simulate_p3_3_session_start(*args, **kwargs):
    if "start" not in kwargs:
        raise RuntimeError("P4 study simulator requires explicit evaluation-session start")
    evaluation_start = pd.Timestamp(kwargs["start"])
    kwargs = dict(kwargs)
    kwargs["start"] = evaluation_start - pd.Timedelta(days=1)
    path = core.simulate_p3_3_economic_path(*args, **kwargs)
    if len(path.returns) and pd.Timestamp(path.returns.index[0]) != evaluation_start:
        raise RuntimeError(
            f"P3.3 session timing drift: expected first return {evaluation_start.date()} "
            f"got {pd.Timestamp(path.returns.index[0]).date()}"
        )
    return path


def _augment_immutable_result() -> None:
    summary = base.RESULT_DIR / "summary.json"
    digest_file = base.RESULT_DIR / "summary.sha256"
    if not summary.exists():
        return
    payload = json.loads(summary.read_text(encoding="utf-8"))
    evidence = payload.setdefault("input_evidence", {})
    evidence["raw_target_authority"] = _target_authority_meta
    evidence["runner_entrypoint"] = "research/leverage_0040/run_leverage_0040_once_r1.py"
    evidence["preflight_corrections"] = [
        "PREFLIGHT-RAW-TARGET-001",
        "PREFLIGHT-SESSION-TIMING-002",
    ]
    summary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    digest = hashlib.sha256(summary.read_bytes()).hexdigest()
    digest_file.write_text(digest + "\n", encoding="utf-8")
    print(f"LEVERAGE-0040 R1 immutable summary_sha256={digest}")


def main() -> None:
    base._fetch_prices = _fetch_prices_corrected
    base._load_frozen_targets = _load_frozen_targets_corrected
    base.simulate_p3_3_economic_path = _simulate_p3_3_session_start
    base.main()
    _augment_immutable_result()


if __name__ == "__main__":
    main()
