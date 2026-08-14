from __future__ import annotations

import numpy as np
import pandas as pd

from research.brrk_btc_sol_path_event_early_warning_0066 import engine
from research.brrk_btc_sol_path_event_early_warning_0066 import event_engine as ee
from research.brrk_btc_sol_path_event_early_warning_0066 import models as mdl


def _synthetic_market(n: int = 900) -> dict[str, pd.DataFrame]:
    idx = pd.date_range("2020-01-01", periods=n, freq="D")
    rng = np.random.default_rng(660066)
    frames = {}
    for j, asset in enumerate(("BTC", "ETH", "SOL")):
        r = rng.normal(0.0007 - 0.0001 * j, 0.018 + 0.003 * j, n)
        # Deterministic adverse and sideways regions so path taxonomy is exercised.
        r[280:340] += -0.008 - 0.001 * j
        r[520:640] *= 0.08
        close = 100.0 * np.exp(np.cumsum(r))
        open_ = close * np.exp(rng.normal(0.0, 0.002, n))
        high = np.maximum(open_, close) * (1.0 + np.abs(rng.normal(0.004, 0.002, n)))
        low = np.minimum(open_, close) * (1.0 - np.abs(rng.normal(0.004, 0.002, n)))
        volume = np.exp(rng.normal(10.0, 0.4, n))
        frames[asset] = pd.DataFrame({
            "open": open_, "high": high, "low": low, "close": close,
            "volume": volume, "quote_volume": volume * close, "trades": np.maximum(1.0, volume / 1000.0),
        }, index=idx)
    return frames


def test_event_engine_price_only_and_warning_windows() -> None:
    frames = _synthetic_market()
    bundle = ee.build_event_atlas(frames)
    assert set(bundle.asset_indices) == {"BTC", "SOL"}
    assert set(bundle.risk_masks) == {("BTC", "DOWN"), ("BTC", "SIDEWAYS"), ("SOL", "DOWN"), ("SOL", "SIDEWAYS")}
    assert len(bundle.events) > 0
    assert {"event_type", "duration_grade", "H_star", "suppression_end_position"}.issubset(bundle.events.columns)
    idx = bundle.asset_indices["BTC"]
    y5 = ee.build_warning_labels(bundle, "BTC", "T1_ANY_DOWN", 5, idx)
    y10 = ee.build_warning_labels(bundle, "BTC", "T1_ANY_DOWN", 10, idx)
    both = y5.notna() & y10.notna()
    # Nested warning windows imply every 5D positive is also a 10D positive on common risk-set dates.
    assert ((y5[both] == 1.0) <= (y10[both] == 1.0)).all()
    for row in bundle.events.itertuples():
        assert int(row.H_star) in ee.SCAN_HORIZONS
        if row.event_type == "DOWN":
            assert row.duration_grade in ee.DOWN_GRADE_RANK
        else:
            assert row.duration_grade in ee.SIDEWAYS_GRADE_RANK


def _synthetic_features(n: int = 500):
    idx = pd.date_range("2021-01-01", periods=n, freq="D")
    rng = np.random.default_rng(660066)
    families = pd.DataFrame(rng.normal(size=(n, 17)), index=idx, columns=mdl.FAMILY_ORDER)
    cells = pd.DataFrame(rng.normal(size=(n, 185)), index=idx, columns=[f"cell_{i:03d}" for i in range(185)])
    signals = pd.concat([cells, families], axis=1)
    latent = 0.7 * families.iloc[:, 0] - 0.4 * families.iloc[:, 9] + 0.2 * families.iloc[:, 6] * families.iloc[:, 7]
    prob = 1.0 / (1.0 + np.exp(-latent.to_numpy()))
    y = pd.Series((rng.random(n) < prob).astype(float), index=idx)
    return cells, families, signals, y


def test_all_base_classifier_interfaces() -> None:
    cells, families, signals, y = _synthetic_features()
    train, test = cells.index[:400], cells.index[400:]
    selected = list(signals.columns[:12])
    params = {
        "P01_FAMILY_RIDGE_LOGIT": {"C": 0.1},
        "P02_RAW_ELASTIC_NET_LOGIT": {"C": 0.1, "l1_ratio": 0.5},
        "P03_VALIDATION_SCREENED_SIGNAL_LOGIT": {"C": 1.0},
        "P04_PCR_LOGIT": {"n_components": 10, "C": 1.0},
        "P05_THEORY_QUADRATIC_LOGIT": {"C": 0.01},
        "P06_SHALLOW_GBDT_CLASSIFIER": {"max_depth": 1, "n_estimators": 50, "learning_rate": 0.03},
    }
    for arch, p in params.items():
        f = mdl.fit_classifier(arch, p, cells.loc[train], families.loc[train], signals.loc[train], y.loc[train], selected_signals=selected if arch.startswith("P03") else None)
        pred = f.predict_proba(cells.loc[test], families.loc[test], signals.loc[test])
        assert pred.shape == (len(test),)
        assert np.isfinite(pred).all()
        assert ((pred >= 0) & (pred <= 1)).all()
    assert mdl.quadratic_frame(families).shape[1] == 44


def test_hazard_stack_metrics_holm_and_percentiles() -> None:
    _, families, _, y = _synthetic_features()
    labels = {h: y.copy() for h in ee.WARNING_HORIZONS}
    hz = mdl.fit_hazard(families.iloc[:400], {h: labels[h].iloc[:400] for h in ee.WARNING_HORIZONS}, {"C": 0.1})
    p = hz.predict(families.iloc[400:], 10)
    assert np.isfinite(p).all()
    base = {a: np.clip(p + 0.01 * i, 0, 1) for i, a in enumerate(mdl.BASE_ARCHITECTURES)}
    w = mdl.stack_weights(base, y.iloc[400:].to_numpy())
    assert abs(sum(w.values()) - 1.0) < 1e-12
    m = mdl.binary_metrics(y.iloc[400:].to_numpy(), p, p, include_blocks=True)
    assert m["status"] == "OK" and len(m["chronological_blocks"]) == 4
    holm = mdl.holm_adjust({"a": 0.001, "b": 0.02, "c": 0.5})
    assert holm["a"]["holm_adjusted_p"] <= holm["b"]["holm_adjusted_p"] <= holm["c"]["holm_adjusted_p"]
    pct = mdl.empirical_percentile(np.array([0.1, np.nan, 0.9]), np.array([0.0, 0.5, 1.0]))
    assert np.isfinite(pct[[0, 2]]).all()
    assert np.isnan(pct[1])


def test_portfolio_math_and_no_leverage() -> None:
    idx = pd.date_range("2024-01-01", periods=120, freq="D")
    r = pd.Series(np.full(len(idx), 0.001), index=idx)
    gross = pd.Series(np.full(len(idx), 0.75), index=idx)
    rf = pd.Series(np.full(len(idx), 0.0001), index=idx)
    g = pd.Series(np.where(np.arange(len(idx)) % 30 < 5, 0.5, 1.0), index=idx)
    ret, extra = engine._portfolio_returns(g, r, gross, engine._cash_net(rf))
    nav = engine._nav(ret)
    assert np.isfinite(ret).all() and float(nav.iloc[-1]) > 0
    assert extra["average_total_gross"] <= 0.75 + 1e-12
    assert extra["outer_turnover"] > 0
    q95, lcbs = engine._economic_mbb({"a": np.full(200, 0.001), "b": np.full(200, 0.0005)})
    assert q95 is not None and set(lcbs) == {"a", "b"}


def test_frozen_variant_accounting() -> None:
    cfg = mdl.frozen_configurations()
    per_track = sum(len(cfg[a]) for a in mdl.BASE_ARCHITECTURES[:6])
    assert per_track == 40
    assert per_track * 40 + len(cfg["P07_DISCRETE_TIME_HAZARD_LOGIT"]) * 8 == 1632
    assert 1632 + 64 + 8 == 1704
