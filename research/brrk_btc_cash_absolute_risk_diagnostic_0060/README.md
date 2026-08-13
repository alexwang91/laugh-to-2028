# BRRK-BTC-CASH-ABSOLUTE-RISK-DIAGNOSTIC-0060

Status: **INVALID_EXECUTION / CLOSED / NO SCIENTIFIC CONCLUSION**.

0060 is a pure BTC-only absolute-risk mechanism diagnostic. It asks whether one fixed causal low-dimensional BTC risk state contains recurrent information about subsequent terminal BTC loss versus Cash and origin-relative pathwise adverse excursion.

## Frozen representation

The candidate count is exactly one. The state is the equal-weight mean of three fully required axes:

- A1: BTC fast/slow trend disagreement plus persistence;
- A2: trailing-60 high distance, sessions-since-high, and negative MA20 10-session slope;
- A3: RV10/RV30 acceleration, downside/upside semivolatility ratio, and negative-return share.

Each raw coordinate is causally standardized with trailing 252 completed sessions, minimum 60 valid observations, sample standard deviation ddof=1, zero standard deviation -> NaN, and clipping to [-3,+3]. Missing required coordinates invalidate the origin; no available-feature averaging or fitted weighting is allowed.

## Frozen targets and inference

All horizons 20/60/120/240 days are co-primary. Both target families are co-primary:

- terminal loss: `max(0,-log(BTC[t+h]/BTC[t]))`;
- adverse excursion: `max_{u=1..h} max(0,-log(BTC[t+u]/BTC[t]))`.

One identical complete-case origin set is used across all eight target cells. G1 requires at least 1,440 origins. G2 requires all eight full-sample Spearman correlations to be strictly positive. G3 requires at least 3 of 4 deterministic chronological blocks to have all eight correlations positive. G4 uses aligned non-circular moving-block bootstrap length 240, 10,000 replicates, seed 1844716895 and a centered-max simultaneous one-sided 95% LCB across all eight cells; every LCB must be strictly positive.

No minimum effect-size hurdle is imposed here because economic translation belongs to a later new research ID.

## Dataset and epistemic status

The only source is the immutable exposed daily Binance spot wrapper already used by the governed 0047/0048/0059 lineage. 0060 consumes BTC close only. History is DEVELOPMENT / researcher-exposed / not independent OOS. No refetch, replacement, fill, intraday extension or external-data addition is allowed.

## Firewalls

Under 0060 there is no BTC/Cash threshold, no gross map, no re-entry/hysteresis/holding rule, no strategy NAV, no CAGR/MDD/Calmar, no transaction-cost economics, no ETH/SOL/Beta signal, no on-chain or macro input, and no ML/HMM/changepoint model.

A PASS can only make a separately governed new-ID state-to-gross translation study eligible. A valid FAIL closes 0060 against same-ID feature/horizon/target/bootstrap/support rescue.

Production, signing and order-submission authority remain false.

## Immutable invalid closeout

The unique authorized DEVELOPMENT historical attempt crossed the durable attempt boundary and then failed the frozen controlled-result schema before any primary result or execution receipt could be persisted. The exact validator error was `lcb.terminal_loss_20 must be finite numeric`. No historical statistic may be reconstructed by recomputation. `RUN_ATTEMPT.marker` is preserved byte-for-byte; `PRIMARY_RESULT.json`, `EXECUTION.json` and `RUN_ONCE.marker` do not exist.

0060 therefore closes `INVALID_EXECUTION` with no conclusion for or against the BTC absolute-risk mechanism. Any corrected replication requires a new research ID. No BTC/Cash gross map, canonical change, Phase-6 change or production authority is created.
