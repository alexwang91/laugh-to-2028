"""Shared statistical inference for backtest comparisons (backlog F10).

Every "A beats B" claim in this repo's history has needed a human to
re-derive whether the gap is real or noise -- BRRK-0011 vs V1 (daily
correlation 0.9948, Sharpe-difference 95% CI crossing zero), the
EXPOSURE-SMOOTH-0038 review (72.4% probability of improvement, CI crossing
zero), CARRY-PNL-0031 vs cash. This module makes that check a function call
instead of a one-off script, so it can be wired into any experiment's report.

Two independent tools, for two different questions:

**Probabilistic / Deflated Sharpe Ratio** (Bailey & Lopez de Prado, 2014,
"The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest
Overfitting and Non-Normality") answers *"how much do I trust this one
Sharpe number, given how much data I have and how many things I tried?"* --
a single-series question.

  PSR(SR*) = Phi[ (SR_hat - SR*) sqrt(N-1) / sqrt(1 - g3 SR_hat + (g4-1)/4 SR_hat^2) ]
  MinTRL   = 1 + [1 - g3 SR_hat + (g4-1)/4 SR_hat^2] (z_a / (SR_hat - SR*))^2
  SR*      = sqrt(V[SR_trials]) [ (1-g) Phi^-1(1 - 1/K) + g Phi^-1(1 - 1/(K e)) ]

**Paired bootstrap** answers *"is variant B actually better than variant A,
given they were tested on the same days?"* -- a two-series comparison
question, and the one that actually matters for "should we promote this."
It makes no distributional assumption and uses the same day-pairing the
strategies were run on, which PSR/DSR (built for a single series) cannot do.

All Sharpes in this module's function signatures are **per-day** unless a
parameter name says `_ann`. `TRADING_DAYS_PER_YEAR = 365` throughout, matching
every other Sharpe calculation in this repo.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Callable

import numpy as np
import pandas as pd
from scipy.stats import norm

TRADING_DAYS_PER_YEAR = 365.0
EULER_MASCHERONI = 0.5772156649015329


# --- Probabilistic / Deflated Sharpe Ratio ----------------------------------

def sample_moments(returns: pd.Series) -> dict[str, float]:
    """Daily Sharpe, skew and excess kurtosis, in the convention PSR expects."""
    r = returns.dropna().astype(float)
    if len(r) < 3:
        raise ValueError("need at least 3 observations for skew/kurtosis")
    std = float(r.std(ddof=1))
    return {
        "n": int(len(r)),
        "sharpe_daily": float(r.mean() / std) if std > 0 else float("nan"),
        "sharpe_annualized": float(r.mean() / std * math.sqrt(TRADING_DAYS_PER_YEAR)) if std > 0 else float("nan"),
        # pandas .kurtosis() returns *excess* kurtosis (normal = 0); PSR's
        # formula wants kurtosis on the g4 = 3 = normal convention, hence +3.
        "skew": float(r.skew()),
        "kurtosis": float(r.kurtosis() + 3.0),
    }


def probabilistic_sharpe_ratio(
    sharpe_hat_daily: float,
    sharpe_star_daily: float,
    n: int,
    skew: float,
    kurtosis: float,
) -> float:
    """P(true daily Sharpe > sharpe_star_daily), Bailey & Lopez de Prado (2014) eq. 1."""
    denom = math.sqrt(max(1.0 - skew * sharpe_hat_daily + (kurtosis - 1.0) / 4.0 * sharpe_hat_daily ** 2, 1e-12))
    z = (sharpe_hat_daily - sharpe_star_daily) * math.sqrt(max(n - 1, 0)) / denom
    return float(norm.cdf(z))


def min_track_record_length(
    sharpe_hat_daily: float,
    sharpe_star_daily: float,
    skew: float,
    kurtosis: float,
    confidence: float = 0.95,
) -> float:
    """Days of data needed to assert true daily Sharpe > sharpe_star_daily
    at the given confidence, holding the observed Sharpe/skew/kurtosis fixed.
    Returns inf if sharpe_hat_daily does not exceed sharpe_star_daily at all.
    """
    if sharpe_hat_daily <= sharpe_star_daily:
        return float("inf")
    z = norm.ppf(confidence)
    variance_term = 1.0 - skew * sharpe_hat_daily + (kurtosis - 1.0) / 4.0 * sharpe_hat_daily ** 2
    return 1.0 + max(variance_term, 1e-12) * (z / (sharpe_hat_daily - sharpe_star_daily)) ** 2


def expected_max_sharpe_under_trials(n_trials: int, sharpe_variance_across_trials: float) -> float:
    """E[max Sharpe from n_trials independent tries], for use as sharpe_star
    in a Deflated Sharpe Ratio calculation. Bailey & Lopez de Prado (2014) eq. 8."""
    if n_trials < 2:
        return 0.0
    a = norm.ppf(1.0 - 1.0 / n_trials)
    b = norm.ppf(1.0 - 1.0 / (n_trials * math.e))
    return math.sqrt(max(sharpe_variance_across_trials, 0.0)) * ((1.0 - EULER_MASCHERONI) * a + EULER_MASCHERONI * b)


def deflated_sharpe_ratio(
    returns: pd.Series,
    n_trials: int,
    sharpe_variance_across_trials_daily: float,
) -> dict[str, float]:
    """Full DSR pipeline for one series: PSR against the expected-max-Sharpe
    benchmark implied by having tried n_trials independent variants."""
    m = sample_moments(returns)
    sharpe_star = expected_max_sharpe_under_trials(n_trials, sharpe_variance_across_trials_daily)
    dsr = probabilistic_sharpe_ratio(m["sharpe_daily"], sharpe_star, m["n"], m["skew"], m["kurtosis"])
    return {
        "n_trials": int(n_trials),
        "sharpe_star_daily": float(sharpe_star),
        "sharpe_star_annualized": float(sharpe_star * math.sqrt(TRADING_DAYS_PER_YEAR)),
        "deflated_sharpe_ratio": float(dsr),
    }


def sharpe_confidence_report(
    returns: pd.Series,
    target_sharpe_annualized: float = 1.0,
    confidence: float = 0.95,
) -> dict[str, Any]:
    """One-stop PSR/MinTRL report for a single series, in annualized terms."""
    m = sample_moments(returns)
    target_daily = target_sharpe_annualized / math.sqrt(TRADING_DAYS_PER_YEAR)
    psr_zero = probabilistic_sharpe_ratio(m["sharpe_daily"], 0.0, m["n"], m["skew"], m["kurtosis"])
    psr_target = probabilistic_sharpe_ratio(m["sharpe_daily"], target_daily, m["n"], m["skew"], m["kurtosis"])
    mintrl_days = min_track_record_length(m["sharpe_daily"], target_daily, m["skew"], m["kurtosis"], confidence)
    return {
        "observations": m["n"],
        "years_at_365_25_days": float(m["n"] / 365.25),
        "sharpe_annualized": m["sharpe_annualized"],
        "skew": m["skew"],
        "kurtosis": m["kurtosis"],
        "psr_above_zero": float(psr_zero),
        "target_sharpe_annualized": float(target_sharpe_annualized),
        "psr_above_target": float(psr_target),
        "min_track_record_years": float(mintrl_days / 365.25) if math.isfinite(mintrl_days) else float("inf"),
    }


# --- Paired bootstrap for A/B comparisons -----------------------------------

def _cagr(nav: np.ndarray, periods_per_year: float = TRADING_DAYS_PER_YEAR) -> float:
    years = len(nav) / periods_per_year
    if years <= 0 or nav[-1] <= 0:
        return float("nan")
    return float(nav[-1] ** (1.0 / years) - 1.0)


def _sharpe_stat(x: np.ndarray) -> float:
    std = x.std(ddof=1)
    if std <= 1e-12:
        return float("nan")
    return float(x.mean() / std * math.sqrt(TRADING_DAYS_PER_YEAR))


def _calmar_stat(x: np.ndarray) -> float:
    nav = np.cumprod(1.0 + x)
    dd = float((nav / np.maximum.accumulate(nav) - 1.0).min())
    if dd >= 0:
        return float("nan")
    return float(_cagr(nav) / abs(dd))


STAT_FUNCTIONS: dict[str, Callable[[np.ndarray], float]] = {
    "sharpe": _sharpe_stat,
    "calmar": _calmar_stat,
}


@dataclass(frozen=True)
class BootstrapResult:
    statistic: str
    mean_difference: float
    ci_low: float
    ci_high: float
    confidence: float
    probability_b_better: float
    excludes_zero: bool
    n_resamples: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "statistic": self.statistic,
            "mean_difference_b_minus_a": self.mean_difference,
            "ci_low": self.ci_low,
            "ci_high": self.ci_high,
            "confidence": self.confidence,
            "probability_b_better": self.probability_b_better,
            "significant_at_confidence": self.excludes_zero,
            "n_resamples": self.n_resamples,
        }


def paired_bootstrap(
    returns_a: pd.Series,
    returns_b: pd.Series,
    statistic: str = "sharpe",
    n_resamples: int = 4000,
    confidence: float = 0.95,
    seed: int = 7,
) -> BootstrapResult:
    """Resample matched (a[t], b[t]) day-pairs with replacement and compare
    statistic(b) - statistic(a) across resamples. This is the tool for "is B
    actually better than A" -- it needs no distributional assumption and
    respects that a and b were run on the same calendar days (so their daily
    correlation, whatever it is, is preserved in every resample).

    `statistic` must be a key in STAT_FUNCTIONS ("sharpe" or "calmar").
    """
    if statistic not in STAT_FUNCTIONS:
        raise ValueError(f"unknown statistic {statistic!r}, expected one of {list(STAT_FUNCTIONS)}")
    stat_fn = STAT_FUNCTIONS[statistic]

    frame = pd.concat([returns_a.rename("a"), returns_b.rename("b")], axis=1).dropna()
    if len(frame) < 30:
        raise ValueError(f"only {len(frame)} paired observations; need at least 30 for a bootstrap to mean anything")
    a = frame["a"].to_numpy(float)
    b = frame["b"].to_numpy(float)
    n = len(frame)

    rng = np.random.default_rng(seed)
    diffs = np.empty(n_resamples, dtype=float)
    for i in range(n_resamples):
        idx = rng.integers(0, n, n)
        diffs[i] = stat_fn(b[idx]) - stat_fn(a[idx])
    diffs = diffs[np.isfinite(diffs)]
    if len(diffs) < n_resamples * 0.5:
        raise RuntimeError(
            f"too many non-finite resamples ({n_resamples - len(diffs)}/{n_resamples}); "
            "check for near-zero volatility or near-zero drawdown in a resampled path"
        )

    alpha = 1.0 - confidence
    lo, hi = np.percentile(diffs, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return BootstrapResult(
        statistic=statistic,
        mean_difference=float(diffs.mean()),
        ci_low=float(lo),
        ci_high=float(hi),
        confidence=confidence,
        probability_b_better=float((diffs > 0).mean()),
        excludes_zero=bool(lo > 0 or hi < 0),
        n_resamples=int(len(diffs)),
    )


def comparison_report(
    returns_a: pd.Series,
    returns_b: pd.Series,
    label_a: str = "A",
    label_b: str = "B",
    n_resamples: int = 4000,
    seed: int = 7,
) -> dict[str, Any]:
    """Full A-vs-B report: correlation plus bootstrap CIs on Sharpe and Calmar.

    This is the function to call to answer "does B beat A" -- wire it into an
    experiment's report so a promotion claim carries its own confidence
    interval instead of a bare point estimate.
    """
    frame = pd.concat([returns_a.rename("a"), returns_b.rename("b")], axis=1).dropna()
    sharpe_result = paired_bootstrap(returns_a, returns_b, "sharpe", n_resamples, seed=seed)
    calmar_result = paired_bootstrap(returns_a, returns_b, "calmar", n_resamples, seed=seed)
    return {
        "label_a": label_a,
        "label_b": label_b,
        "paired_observations": int(len(frame)),
        "daily_correlation": float(frame["a"].corr(frame["b"])),
        "sharpe": sharpe_result.to_dict(),
        "calmar": calmar_result.to_dict(),
        "interpretation": (
            f"{label_b} vs {label_a}: Sharpe difference 95% CI "
            f"[{sharpe_result.ci_low:+.4f}, {sharpe_result.ci_high:+.4f}] "
            f"({'excludes' if sharpe_result.excludes_zero else 'includes'} zero); "
            f"Calmar difference 95% CI [{calmar_result.ci_low:+.4f}, {calmar_result.ci_high:+.4f}] "
            f"({'excludes' if calmar_result.excludes_zero else 'includes'} zero)."
        ),
    }
