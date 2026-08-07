# BRRK Current State

Last updated: 2026-08-07
Status: **authoritative current-state handoff**

## Executive state

```text
Phase 0                         COMPLETE / MERGED
Phase 1                         COMPLETE / MERGED
Phase 2                         COMPLETE / MERGED
Phase 3                         COMPLETE / MERGED
P4.1 defensive scaler          COMPLETE / MERGED / frozen [0,1]
LEVERAGE-0039                  STOPPED PRE-RUN / NO RESULT
LEVERAGE-0040                  COMPLETE / IMMUTABLE / NO_PROMOTION
LEVERAGE-0041                  COMPLETE / IMMUTABLE / NO_PROMOTION
Phase 4 leverage research      FAIL_STOP / no eligible >1 candidate
P4.6 production leverage gate  NOT ENTERED / BLOCKED by no candidate
P5.1 event taxonomy            COMPLETE / MERGED / FROZEN
P5.2 feature families          COMPLETE / IMMUTABLE EVIDENCE / DESCRIPTIVE CLOSEOUT
P5.3 state model               NEXT
P5.4-P5.6                      NOT STARTED
Phase 6 integrated shadow      NOT STARTED
Phase 7 limited live long      NOT STARTED / explicit approval required
Phase 8 bear-short research    NOT STARTED
production authorization       NONE
```

`production_authorized_components = []`

Current production gross cap remains `1.0`.

## Phase 4 immutable truth

`LEVERAGE-0040` and `LEVERAGE-0041` are complete immutable `NO_PROMOTION` studies. No research cap, operating drawdown budget or prospective P4.6 cap was selected. Do not rerun, rescue, retune, reinterpret or reuse either experiment ID.

LEVERAGE-0041 result commit:

`8ea784830cfffbf892a258cb329d437725d41982`

LEVERAGE-0041 immutable summary SHA256:

`e41a5895263e7aa9206df9fa99fcbb71e5f937abc4746a567fbeb462cca88d17`

## P5.1 immutable taxonomy truth

P5.1 merged in PR #97 on main `86497cdd663a89ca4d54c898b7acbac1cc07d836`.

Contract:

`P5.1-EVENT-TAXONOMY-V1`

Taxonomy blob SHA:

`73d010666fbfd957ec15214a00883a90a8adba5a`

Required 2021/2025 events and four high-volatility non-top controls were frozen before feature selection. Only 2021 November is explicitly terminal in V1. Search windows, anchor rules and evaluation buckets remain immutable for P5.2/P5.3 use.

## P5.2 immutable feature-evidence truth

Contract:

`P5.2-FEATURE-FAMILIES-V1`

Immutable result commit:

`61d585afb64afbe3ead6422e7e62cde6c59fad40`

Immutable summary SHA256:

`3f6dc3c512d22ac8f71d43ed155f2602cd40d5caf3d617c0e130e170727e0627`

Final evidence state:

```text
status                    ONE_TIME_FROZEN_FEATURE_EVIDENCE_COMPLETE
available features        29
coverage                   ALL PASS
resolved events            11
non-top controls           4
pending data sources       6
feature_set_selected       false
state_thresholds_selected  false
selection.status           DESCRIPTIVE_EVIDENCE_ONLY
production_authorized      false
```

The six explicit `DATA_SOURCE_PENDING` items are:

- BTC dominance;
- broad-market breadth;
- comparable 2021/2025 historical funding;
- historical open interest;
- fixed historical basis/premium panel;
- continuous liquidation proxy.

No unnamed or favorable proxy substitutes them.

### R2 recovery

Original run `31217880218` passed the frozen authority guard and failed only during CSV serialization because pandas 3.0 rejected `Series.reset_index(names=...)`. Validator and result commit were skipped; no immutable result existed.

Audited correction `P5.2-POST-COMPUTE-SERIALIZATION-R2` changed only serialization syntax and changed no feature/event/lookback/bucket/coverage/research definition. No observed feature metric was used to choose the correction.

R2 run `31218363897` completed calculation, immutable validation and result commit successfully.

### P5.2 descriptive closeout

Formal closeout:

`docs/P5_2_FEATURE_EVIDENCE_CLOSEOUT.md`

Derived diagnostics:

`research/analysis/p5_2_closeout/`

The closeout analyzer is non-authorizing and proves the immutable P5.2 result directory is byte-for-byte unchanged before/after analysis.

Key structural conclusions for P5.3:

1. no single family or indicator is sufficient for a cycle-top model;
2. realized-volatility state is strong regime context but appears across terminal, second-wind, nonterminal-toplike and deterioration cases, so it is not a terminal trigger by itself;
3. ETH/BTC relative leadership is strong in terminal **and** second-wind/nonterminal structures, requiring a distinct `LATE_BULL_ROTATION` state rather than automatic de-risk;
4. price-versus-RSI rank divergence is the strongest 2021 terminal target-lead hypothesis, but there is only one explicit terminal event, so it cannot be treated as cross-cycle validation;
5. breadth acceleration is useful transition-shape evidence but is not terminal-specific in the lead window;
6. raw daily/4h RSI level alone is insufficient; it is more defensible as one part of a multi-family exhaustion/failure state;
7. distance from the trailing high contains useful second-wind versus top-like state context;
8. discrete breadth/consolidation variables with zero control MAD cannot be judged solely by robust-z rankings.

P5.2 selected **no final feature set and no threshold**. Those decisions belong to P5.3 under a new governed research contract.

## P5.3 required architecture boundary

Target state vocabulary remains:

```text
NORMAL_BULL
BTC_LEADERSHIP_MATURING
LATE_BULL_ROTATION
EXHAUSTION_WATCH
DE_RISK_1
DE_RISK_2
FLAT
```

P5.3 must use multi-family state evidence and preserve these constraints:

- BRRK-0011 continues to decide relative asset ranking;
- cycle layer controls total directional risk, not BRRK ranking;
- ETH/BTC/alt leadership is not automatically bearish;
- no single RSI/volatility/relative-strength switch;
- no threshold hand-tuning to the sole 2021 terminal event;
- no fabricated dominance/OI/funding/basis/liquidation proxies;
- P5.1 windows and P5.2 immutable evidence remain unchanged;
- no production authorization.

## Roadmap audit status

All historical deviations identified by the 2026-08-07 program-wide audit have recorded CLOSED dispositions. Current canonical product/strategy/production drift: **DRIFT_0**.

## Frozen product boundaries

- directional core: BRRK-0011;
- target/tradable assets: BTC / ETH / SOL / BNB;
- XRP feature-only;
- primary venue: Hyperliquid;
- daily decision boundary: 00:00 UTC;
- FLAT = zero directional exposure;
- FLAT -> LONG / SHORT and MONITOR_ONLY -> ACTIVE require explicit human approval;
- first short of a new bear phase requires explicit human approval;
- intraday automation may reduce but not autonomously add directional exposure;
- master key, automated withdrawals and external transfers remain outside scope;
- P4.1 defensive scale stays `[0,1]`;
- production gross remains `1.0`.

## Exact next action

```text
CLOSE AND MERGE P5.2 ONLY AFTER FRESH FINAL-HEAD CI/GOVERNANCE
VERIFY NEW MAIN
CREATE FRESH P5.3 STATE-MODEL RESEARCH BRANCH
PREREGISTER MULTI-STATE STRUCTURE BEFORE FITTING THRESHOLDS
USE P5.1 TAXONOMY + IMMUTABLE P5.2 EVIDENCE WITHOUT RETUNING THEM
KEEP LATE_BULL_ROTATION DISTINCT FROM DE-RISK STATES
DO NOT PRODUCTION-AUTHORIZE ANYTHING
```
