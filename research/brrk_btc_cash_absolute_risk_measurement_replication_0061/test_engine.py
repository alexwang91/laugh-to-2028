import importlib.util
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("engine0061", HERE / "engine.py")
E = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(E)


def tied_panel(n=1600):
    s = np.repeat(np.arange(80), 20).astype(float)
    p = pd.DataFrame({"S": s[:n]})
    for j, k in enumerate(E.TARGET_KEYS):
        y = np.zeros(n)
        y[800:] = np.repeat(np.arange(40), 20)[:n-800]
        p[k] = y + j * 1e-9 * (y > 0)
    return p


def test_upstream_contract_identity():
    assert E._UPSTREAM.RESEARCH_ID == E.UPSTREAM_RESEARCH_ID
    assert tuple(E._UPSTREAM.TARGET_KEYS) == E.TARGET_KEYS
    assert E._UPSTREAM.EXPECTED_PAYLOAD_SHA256 == E.EXPECTED_PAYLOAD_SHA256


def test_fixed_score_spearman_identity_with_heavy_ties_and_long_zero_region():
    p = tied_panel()
    u, vs, observed, err = E.fixed_score_setup(p)
    assert u is not None and vs is not None and observed is not None
    assert err <= E.SPEARMAN_EQUIVALENCE_TOL
    for k in E.TARGET_KEYS:
        rho = E.ordinary_spearman(p["S"].to_numpy(), p[k].to_numpy())
        assert abs(observed[k] - rho) <= 1e-12


def test_constant_full_panel_coordinate_is_detected():
    p = tied_panel()
    p["S"] = 1.0
    u, vs, observed, err = E.fixed_score_setup(p)
    assert u is None and vs is None and observed is None and err is None
    p = tied_panel()
    p[E.TARGET_KEYS[0]] = 0.0
    u, vs, observed, err = E.fixed_score_setup(p)
    assert u is None and vs is None and observed is None and err is None


def test_fixed_score_bootstrap_is_finite_deterministic_and_simultaneous():
    p = tied_panel()
    u, vs, observed, _ = E.fixed_score_setup(p)
    a = E.fixed_score_bootstrap(u, vs, observed, reps=16, seed=E.BOOTSTRAP_SEED, block=240)
    b = E.fixed_score_bootstrap(u, vs, observed, reps=16, seed=E.BOOTSTRAP_SEED, block=240)
    assert a == b
    assert np.isfinite(a[0])
    assert len(a[1]) == 8
    assert all(np.isfinite(x) for x in a[1].values())


def test_repeated_fixed_score_rows_do_not_require_sample_variance():
    n = 1500
    u = np.ones(n)
    vs = {k: np.ones(n) for k in E.TARGET_KEYS}
    observed = {k: 1.0 for k in E.TARGET_KEYS}
    q95, lcbs = E.fixed_score_bootstrap(u, vs, observed, reps=4, seed=1, block=240)
    assert q95 == 0.0
    assert all(v == 1.0 for v in lcbs.values())


def test_mbb_indices_are_deterministic_length_preserving_and_allow_repeat_blocks():
    a = E._mbb_indices(1500, 240, np.random.default_rng(5))
    b = E._mbb_indices(1500, 240, np.random.default_rng(5))
    assert len(a) == 1500
    assert np.array_equal(a, b)
    assert a.min() >= 0 and a.max() < 1500


def test_engine_contains_no_execution_or_portfolio_authority():
    text = (HERE / "engine.py").read_text()
    assert "run_once.py" not in text
    assert "BTC/Cash threshold" not in text
    assert E.CLASS_PASS == "PASS_ABSOLUTE_RISK_INFORMATION_STAGE_ELIGIBLE"
