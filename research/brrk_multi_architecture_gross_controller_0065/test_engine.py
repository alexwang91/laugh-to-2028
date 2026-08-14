from __future__ import annotations

import itertools

import numpy as np
import pandas as pd

from research.brrk_multi_architecture_gross_controller_0065.engine import (
    ARCHITECTURES,
    BASE_ARCHITECTURES,
    FAMILY_ORDER,
    _hmm_filtered_probabilities,
    _prediction_to_g,
    _quadratic_expand,
    count_balanced_blocks,
    deflated_sharpe_diagnostic,
    fit_model,
    frozen_configurations,
    pbo_cscv,
    portfolio_returns_from_g,
    simultaneous_mbb_lcbs,
    stack_weights,
)


def synthetic_panel(n: int = 320):
    rng = np.random.default_rng(650065)
    idx = pd.date_range("2020-01-01", periods=n, freq="D")
    latent = np.sin(np.linspace(0, 10, n)) + 0.35 * rng.normal(size=n)
    fam = {}
    for j, name in enumerate(FAMILY_ORDER):
        fam[name] = latent * (0.2 + 0.03 * j) + rng.normal(scale=0.8, size=n)
    families = pd.DataFrame(fam, index=idx)
    cells = {}
    for j in range(185):
        base = families.iloc[:, j % 17].to_numpy()
        cells[f"C{j:03d}"] = base + rng.normal(scale=0.5 + 0.002 * j, size=n)
    cells = pd.DataFrame(cells, index=idx)
    y = pd.Series(
        0.004 * families[FAMILY_ORDER[0]].to_numpy()
        - 0.003 * families[FAMILY_ORDER[9]].to_numpy()
        + 0.002 * families[FAMILY_ORDER[5]].to_numpy() * families[FAMILY_ORDER[12]].to_numpy()
        + rng.normal(scale=0.01, size=n),
        index=idx,
    )
    return cells, families, y


def test_frozen_method_and_grid_counts():
    cfg = frozen_configurations()
    assert len(ARCHITECTURES) == 8
    assert len(BASE_ARCHITECTURES) == 7
    assert sum(len(v) for v in cfg.values()) == 63
    assert [len(cfg[a]) for a in BASE_ARCHITECTURES] == [12, 12, 12, 4, 9, 8, 6]
    assert 63 + len(ARCHITECTURES) == 71


def test_quadratic_expansion_is_exactly_44_and_has_fixed_graph():
    _, families, _ = synthetic_panel(80)
    q, cols = _quadratic_expand(families)
    assert q.shape == (80, 44)
    assert len([c for c in cols if c.startswith("SQ::")]) == 17
    assert len([c for c in cols if c.startswith("X::")]) == 10


def test_all_seven_base_architectures_fit_and_predict_synthetic():
    cells, families, y = synthetic_panel(260)
    cfg = frozen_configurations()
    for arch in BASE_ARCHITECTURES:
        model = fit_model(arch, cfg[arch][0], cells.iloc[:220], families.iloc[:220], y.iloc[:220])
        pred = model.predict(cells.iloc[220:230], families.iloc[220:230])
        assert pred.shape == (10,)
        assert np.isfinite(pred).all(), arch
    a04 = fit_model("A04_THEORY_QUADRATIC_HESSIAN_RIDGE", cfg["A04_THEORY_QUADRATIC_HESSIAN_RIDGE"][0], cells.iloc[:220], families.iloc[:220], y.iloc[:220])
    h = np.asarray(a04.diagnostics["symmetric_quadratic_hessian"], dtype=float)
    assert h.shape == (17, 17)
    assert np.allclose(h, h.T)


def test_hmm_filter_is_causal_with_respect_to_future_rows():
    cells, families, y = synthetic_panel(280)
    cfg = frozen_configurations()["A07_HMM_REGIME_MIXTURE_RIDGE"][0]
    model = fit_model("A07_HMM_REGIME_MIXTURE_RIDGE", cfg, cells.iloc[:220], families.iloc[:220], y.iloc[:220])
    hmm = model.payload["hmm"]
    rng = np.random.default_rng(9)
    x = rng.normal(size=(20, 4))
    a = _hmm_filtered_probabilities(hmm, x)
    x2 = x.copy()
    x2[11:] += 25.0
    b = _hmm_filtered_probabilities(hmm, x2)
    assert np.allclose(a[:11], b[:11], atol=1e-12)
    assert np.allclose(a.sum(axis=1), 1.0)


def test_stack_is_nonnegative_and_sums_to_one():
    rng = np.random.default_rng(7)
    idx = pd.date_range("2022-01-01", periods=120, freq="D")
    y = pd.Series(rng.normal(size=120), index=idx)
    preds = {a: pd.Series(y.to_numpy() * (0.1 + 0.1 * j) + rng.normal(size=120), index=idx) for j, a in enumerate(BASE_ARCHITECTURES)}
    w = stack_weights(preds, y)
    assert set(w) == set(BASE_ARCHITECTURES)
    assert all(v >= 0 for v in w.values())
    assert abs(sum(w.values()) - 1.0) < 1e-12


def test_common_gross_mapping_bounds_and_direction():
    fitted = np.linspace(-2.0, 2.0, 101)
    g = _prediction_to_g(np.array([-10.0, 0.0, 10.0]), fitted)
    assert np.all((g >= 0.0) & (g <= 1.0))
    assert g[0] < g[1] <= g[2]
    assert g[2] == 1.0


def test_outer_cost_charged_on_first_derisk_and_no_leverage():
    idx = pd.date_range("2024-01-01", periods=3, freq="D")
    g = pd.Series([0.5, 0.5, 0.75], index=idx)
    base = pd.Series([0.0, 0.0, 0.0], index=idx)
    gross = pd.Series([1.0, 1.0, 1.0], index=idx)
    cash = pd.Series([0.0, 0.0, 0.0], index=idx)
    ret, extra = portfolio_returns_from_g(g, base, gross, cash)
    assert np.allclose(ret.to_numpy(), [-0.0005, 0.0, -0.00025])
    assert abs(extra["outer_turnover"] - 0.75) < 1e-12
    assert abs(extra["outer_transaction_cost_return_units"] - 0.00075) < 1e-12


def test_g_one_reconstructs_passive_cash_benchmark_formula():
    idx = pd.date_range("2024-01-01", periods=4, freq="D")
    g = pd.Series(1.0, index=idx)
    base = pd.Series([0.01, -0.02, 0.03, 0.00], index=idx)
    gross = pd.Series([0.8, 1.0, 0.5, 0.9], index=idx)
    cash = pd.Series([0.0001] * 4, index=idx)
    ret, extra = portfolio_returns_from_g(g, base, gross, cash)
    expected = base.to_numpy() + (1.0 - gross.to_numpy()) * 0.0001
    assert np.allclose(ret.to_numpy(), expected)
    assert extra["outer_turnover"] == 0.0


def test_simultaneous_mbb_is_deterministic_and_positive_for_clear_edge():
    rng = np.random.default_rng(123)
    d = {f"M{i}": 0.001 + rng.normal(scale=0.0002, size=240) for i in range(8)}
    q1, l1 = simultaneous_mbb_lcbs(d, block_length=20, reps=200, seed=650065)
    q2, l2 = simultaneous_mbb_lcbs(d, block_length=20, reps=200, seed=650065)
    assert q1 == q2
    assert l1 == l2
    assert all(v > 0 for v in l1.values())


def test_pbo_has_exactly_70_cscv_splits():
    rng = np.random.default_rng(44)
    methods = {f"M{i}": rng.normal(loc=i * 1e-5, scale=0.01, size=160) for i in range(8)}
    out = pbo_cscv(methods, slices=8)
    assert out["status"] == "OK"
    assert out["split_count"] == math_comb(8, 4) == 70
    assert 0.0 <= out["pbo"] <= 1.0


def math_comb(n, k):
    return len(list(itertools.combinations(range(n), k)))


def test_deflated_sharpe_diagnostic_is_bounded_probability():
    rng = np.random.default_rng(4)
    x = rng.normal(loc=0.001, scale=0.01, size=300)
    out = deflated_sharpe_diagnostic(x, 71)
    assert out["status"] == "OK"
    assert 0.0 <= out["deflated_sharpe_probability"] <= 1.0


def test_count_balanced_blocks_are_contiguous_and_complete():
    blocks = count_balanced_blocks(1332, 4)
    assert [len(x) for x in blocks] == [333, 333, 333, 333]
    assert np.array_equal(np.concatenate(blocks), np.arange(1332))
