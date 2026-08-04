# Review verification scripts — 2026-08-04

Read-only audit tooling for [`docs/CODE_REVIEW_2026-08-04.md`](../../docs/CODE_REVIEW_2026-08-04.md).

These scripts change no strategy, no parameter and no committed result. They exist so that
every numeric claim in the review can be re-derived independently. They are **not** registered
experiments and must never be cited as promotion evidence.

| Script | Answers | Review section |
|---|---|---|
| `verify_band_drift.py` | Does `apply_band` + `run_portfolio` understate turnover by ignoring weight drift? | §2.0 |
| `verify_start_date_sensitivity.py` | How much of the headline result is the 2022-12-10 start date? Also reproduces the README table and prices the omitted cash yield. | §3.1, §3.8 |
| `verify_psr_dsr_mintrl.py` | Probabilistic / Deflated Sharpe and Minimum Track Record Length on the committed BRRK-0011 and V1 daily series. | §3.2 |

`verify_band_drift.py` and `verify_start_date_sensitivity.py` refetch Binance daily klines
(no key required, a few minutes). `verify_psr_dsr_mintrl.py` reads only committed CSV/JSON
under `research/results/` and runs offline.

```bash
pip install -r ../requirements.txt scipy
python verify_band_drift.py
python verify_start_date_sensitivity.py
python verify_psr_dsr_mintrl.py
```

## Results obtained on 2026-08-04

**Reproduction check** — `research/core/crypto_rotation_backtest.py` reproduces the published
V1 baseline to within rounding: $57,111 vs $57,116, CAGR 61.31% vs 61.25%, MDD -37.63% vs
-37.63%, Sharpe 1.295 vs 1.295. The committed numbers are faithful.

**Band drift (§2.0) — hypothesis rejected.** Repo-convention turnover 158.29 vs
drift-consistent 159.93 over 2021-05-01..2026-08-03; CAGR 44.70% vs 45.30%. The unbilled
drift trading is worth roughly 0.1%/yr and its sign favours the drift-consistent run. Not a
defect. The research/execution band *semantics* still differ — see review §3.6.

**Start-date sensitivity (§3.1).** Same gross<=1 V1 construction:

| start | years | CAGR | MDD | Sharpe | Calmar |
|---|---:|---:|---:|---:|---:|
| 2021-05-01 | 5.25 | 36.44% | -59.72% | 0.889 | 0.610 |
| 2022-12-10 (README) | 3.64 | 61.31% | -37.63% | 1.295 | 1.629 |
| 2024-01-01 | 2.58 | 23.90% | -37.63% | 0.720 | 0.635 |

**Statistical power (§3.2).** BRRK-0011: N=1332 days, annualised Sharpe 1.353, skew +0.567,
kurtosis 7.07. PSR(SR\*=0) = 99.57%, so "Sharpe > 0" is well established. But MinTRL to assert
annualised Sharpe > 1.0 at 95% confidence is **20.97 years** against 3.65 years available.

**BRRK-0011 vs V1 (§3.3).** Daily correlation 0.9948. Paired bootstrap (4000 resamples):
Sharpe difference +0.058, 95% CI [-0.046, +0.164]; Calmar difference 95% CI [-0.164, +0.599].
Neither excludes zero.
