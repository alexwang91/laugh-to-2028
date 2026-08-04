import numpy as np
from scipy.optimize import minimize_scalar


def path_tail_risk_corrected(v1_paths: np.ndarray, scale: float) -> tuple[float, float]:
    port = scale * v1_paths
    nav = np.cumprod(np.maximum(1.0 + port, 1e-12), axis=1)
    terminal = nav[:, -1] - 1.0
    losses = -terminal
    q = float(np.quantile(losses, 0.95))
    tail = losses[losses >= q]
    cvar95 = float(tail.mean()) if len(tail) else q

    # Correct definition: the path begins at decision-time wealth=1.
    nav0 = np.concatenate([np.ones((len(nav), 1)), nav], axis=1)
    peaks = np.maximum.accumulate(nav0, axis=1)
    dd = nav0 / np.maximum(peaks, 1e-12) - 1.0
    max_dd = dd.min(axis=1)
    qdd = float(np.quantile(max_dd, 0.05))
    dd_tail = max_dd[max_dd <= qdd]
    cdar95 = float(-dd_tail.mean()) if len(dd_tail) else float(-qdd)
    return cvar95, cdar95


def expected_log_terminal(v1_paths: np.ndarray, scale: float) -> float:
    wealth = np.maximum(1.0 + scale * v1_paths, 1e-12)
    return float(np.mean(np.log(wealth).sum(axis=1)))


def safe_max_scale_corrected(v1_paths: np.ndarray, budget: float) -> tuple[float, float, float]:
    cvar1, cdar1 = path_tail_risk_corrected(v1_paths, 1.0)
    if cvar1 <= budget and cdar1 <= budget:
        return 1.0, cvar1, cdar1
    lo, hi = 0.0, 1.0
    for _ in range(28):
        mid = 0.5 * (lo + hi)
        cvar, cdar = path_tail_risk_corrected(v1_paths, mid)
        if cvar <= budget and cdar <= budget:
            lo = mid
        else:
            hi = mid
    cvar, cdar = path_tail_risk_corrected(v1_paths, lo)
    return float(lo), float(cvar), float(cdar)


def choose_scale_corrected(v1_paths: np.ndarray, budget: float) -> dict:
    safe_max, safe_cvar, safe_cdar = safe_max_scale_corrected(v1_paths, budget)
    cvar1, cdar1 = path_tail_risk_corrected(v1_paths, 1.0)
    if safe_max <= 1e-8:
        return {
            "scale": 0.0,
            "safe_max": 0.0,
            "expected_log20": 0.0,
            "scenario_cvar95": 0.0,
            "scenario_cdar95": 0.0,
            "full_scale_cvar95": cvar1,
            "full_scale_cdar95": cdar1,
        }
    result = minimize_scalar(
        lambda s: -expected_log_terminal(v1_paths, float(s)),
        bounds=(0.0, safe_max),
        method="bounded",
        options={"xatol": 1e-4},
    )
    candidates = [0.0, float(safe_max)]
    if result.success and np.isfinite(result.x):
        candidates.append(float(np.clip(result.x, 0.0, safe_max)))
    scores = [expected_log_terminal(v1_paths, s) for s in candidates]
    scale = float(candidates[int(np.argmax(scores))])
    cvar, cdar = path_tail_risk_corrected(v1_paths, scale)
    return {
        "scale": scale,
        "safe_max": float(safe_max),
        "expected_log20": float(max(scores)),
        "scenario_cvar95": float(cvar),
        "scenario_cdar95": float(cdar),
        "full_scale_cvar95": float(cvar1),
        "full_scale_cdar95": float(cdar1),
    }
