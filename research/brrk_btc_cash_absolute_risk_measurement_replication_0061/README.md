# BRRK-BTC-CASH-ABSOLUTE-RISK-MEASUREMENT-REPLICATION-0061

Status: **NUMERICAL/DATA PREREGISTERED / NOT IMPLEMENTED / NOT RUN**

0061 is a new-ID measurement-corrected replication of the unresolved 0060 BTC-to-Cash absolute-risk mechanism question. It is not a rerun, repair or reconstruction of 0060 under the same ID.

The scientific state, dataset, eight targets, 20/60/120/240-day horizon family, full-sample Spearman and temporal recurrence rules are inherited unchanged from 0060. The sole measurement correction is the G4 dependence-aware inference layer: average-tie midrank scores are computed and standardized once on the full shared panel, and aligned 240-row moving-block resampling operates on the fixed score products rather than recomputing replicate-specific correlation denominators.

The preregistration freezes:

- immutable exposed DEVELOPMENT daily BTC dataset and payload hash;
- one fixed A1/A2/A3/S representation;
- all eight terminal-loss/adverse-excursion targets as co-primary;
- G1 minimum 1,440 shared origins;
- G2 all eight ordinary full-sample Spearman rho values > 0;
- G3 at least 3 of 4 chronological blocks positive in all eight cells;
- full-panel fixed-score observed statistic equality to ordinary Spearman within absolute tolerance 1e-12;
- aligned non-circular moving-block bootstrap length 240, 10,000 reps, seed 1844716895, NumPy linear/Type-7 q95;
- simultaneous one-sided lower bounds across all eight targets;
- strict gate short-circuit semantics so scientific no-information conditions persist as valid FAIL rather than protocol INVALID;
- lossless result persistence and exactly one future historical variant.

No historical 0061 target, association or bootstrap value has been computed during design or preregistration. Real market loading remains forbidden until implementation-only and a separately merged controlled-execution boundary are complete.

No BTC/Cash threshold, re-entry rule, hysteresis, gross map, strategy NAV, transaction-cost economics, CAGR/MDD optimization, signed target, volatility controller, drawdown controller, change detector, leverage or shorting is authorized under 0061.

A PASS can only authorize a new research ID for systematic state-to-gross translation. It does not validate a strategy or change canonical BRRK-0011, Phase 6, signing, order submission or production authority.
