# Literature Review — 2026-08-04

Purpose: record external research used to motivate future experiments without retroactively tuning existing results.

## Findings that directly support the current architecture

### 1. Entry timing dominates allocation complexity in crypto
Vynyavskyy, Kitzler, Haslhofer & Yaish (2026), *Modern Portfolio Theory in the Crypto-Wilderness* (AFT 2026 / arXiv:2605.20528), reconstructs more than 116M Ethereum accounts over 2015–2025. The paper reports that entry month explains roughly 70–79% of the variance in realized returns and that mean-variance optimization does not reliably improve realized performance relative to simpler approaches.

Implication for this project: prioritize regime/cycle entry-exit control and simple concentrated alpha over increasingly elaborate cross-sectional mean-variance allocation.

### 2. Explicit regime models are more convincing as risk overlays than alpha engines
Subanthran (2026), *Persistent Latent States and Asymmetric Volatility: Why Explicit Regime Detection Fails to Outperform a Momentum-Volatility Baseline* (SSRN 6864738), reports that an ensemble of explicit regime models consistently improves maximum drawdown but significantly underperforms a momentum-volatility baseline in Sharpe.

Implication: retain frozen V1 trend/relative-strength alpha; use HMM only to control risk. This is exactly the architecture that produced BRRK-0006.

### 3. Downside risk is more appropriate than symmetric variance for crypto
Li, Liu & Yan (2026), *Performance-based regularization for downside-risk cryptocurrency portfolios: Evidence from mean-lower partial moment strategies*, Pacific-Basin Finance Journal 97, develops a regularized mean-LPM framework and reports stronger and more stable OOS performance, especially in drawdowns.

Liu, Lassance, Vanduffel & Yao (2026), *Distributionally Robust Downside Risk Optimization* (SSRN 6446118), combines lower partial moments with Wasserstein distributional robustness.

Implication: a future risk experiment should estimate downside risk / lower partial moments and estimation uncertainty rather than add another symmetric volatility gate.

### 4. Conformal calibration is a promising way to control model overconfidence
Schmitt (2026), *Taming Tail Risk in Financial Markets: Conformal Risk Control for Nonstationary Portfolio VaR* (arXiv:2602.03903 / SSRN 6172999), proposes time-decayed and regime-weighted conformal calibration of risk forecasts under drift.

Li, Liu, Wang & Zhu (2026), *Forecasting Realized Volatility Intervals with Pooled Conformal Calibration* (SSRN 6944142), pools cross-sectional forecast errors to improve simultaneous volatility coverage during common shocks.

Implication: instead of trusting raw HMM/scenario tail estimates, calibrate realized exceedance errors sequentially. This is a candidate after the current factor-ensemble test.

### 5. Change-point methods should be simple and sequential before considering RL
Tsaknaki, Lillo & Mazzarisi (2024), *Bayesian Autoregressive Online Change-Point Detection with Time-Varying Parameters* (arXiv:2407.16376), develops real-time Bayesian change-point detection with time-varying dependence.

Polson & Yu (2026), *Transfer Learning for Change-point Problems: A GBC Markov-embedded Approach* (SSRN 6965742), links Markov-embedded change-point models with penalized trend filtering.

Implication: test low-degree-of-freedom sequential detectors before any reinforcement-learning layer. CYCLE-0002 therefore uses a symmetric standardized CUSUM and introduces no new threshold.

### 6. Re-optimization itself can create overfitting
Goyal (2026), *When Does Risk-Managed Momentum Add Value?* (SSRN 7143882), reports that walk-forward re-optimization can degrade OOS performance and that crash guards face a protection-versus-whipsaw tradeoff.

Implication: fixed parameter families and preregistered sensitivity grids are preferable to optimizing thresholds on the 2022–2026 window.

## Methods deliberately deferred

- Deep RL / HMM-RL: potentially useful but not justified by the small number of independent crypto regimes; too many degrees of freedom at this stage.
- Large neural return forecasters: sample size is deceptive because daily observations inside a regime are strongly dependent.
- Full Markowitz/Black-Litterman replacement of V1: recent crypto evidence suggests entry timing and common beta dominate fine allocation, and prior internal tests show concentrated Top-2 style rotation is stronger than broad diversification.
- More leverage: prior internal experiments show alpha/risk-state quality is the bottleneck, not the gross cap.

## Current research queue

1. BRRK-MVP-0007-FACTOR-ENSEMBLE — equal-weight PCA 3/4/5 state-model averaging; no PnL weighting.
2. CYCLE-0002-SYMMETRIC-CUSUM — symmetric sequential recovery release; same k/h as capitulation arm.
3. If 0007 confirms model-specification risk: consider sequential conformal calibration of risk forecasts rather than selecting a winning HMM specification.
4. If further downside control is needed: test a preregistered LPM/semivariance risk estimator as a risk-only module, not as an alpha signal.
