# BRRK Current State

Last updated: 2026-08-08  
Status: **authoritative current-state handoff**

## Executive state

```text
Phase 0-3                         COMPLETE / MERGED
Phase 4 leverage research         FAIL_STOP / no eligible >1 candidate
production gross cap              1.0
production_authorized_components = []
P5.1-P5.4                         COMPLETE / FROZEN
P5.5 validation                   COMPLETE / IMMUTABLE / NO_PROMOTION / FAIL_STOP
P5.6 cycle integration            BLOCKED / NO ELIGIBLE CANDIDATE
Phase 6 implementation/replay     PASS_SHADOW_ONLY_IMPLEMENTATION_REPLAY / MERGED #109
Phase 6 live elapsed evidence     MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT / CLOCK NOT ARMED
Phase 6 observation preactivation PREACTIVATION_BLOCKED_FAIL_CLOSED
Phase 6 durable evidence backend  FROZEN / ACTIONS_ARTIFACT_V4 / 90D / NO CREDIT / MERGED #133
Phase 6 valuation contract        PHASE6-LIVE-VALUATION-V1 / CANDIDATE #134 / STANDARD MODE ONLY
Phase 6 pre-arm dependencies      3 OF 4 FROZEN / ACCOUNT IDENTITY UNRESOLVED
Phase 7 readiness gate            IMPLEMENTED / MERGED #110 / LAUNCH BLOCKED
Phase 7 program state             MONITOR_ONLY
Phase 8 bear-short research       PREREGISTERED_TRIGGER_ABSENT_NOT_RUN / MERGED #111
Program epistemic governance v1   PG0-PG6 COMPLETE / CI-ENFORCED / NO-DRIFT
Stablecoin liquidity Stage-1      FAIL_NO_INCREMENTAL_INFORMATION / NO_PROMOTION / TERMINAL STOP
production authorization          NONE
first real short authorization    NONE
```

Current authoritative `main` before PR #134:

```text
af8ff7c6ce3bf16dd81ab9f510393d38fc790b63
```

That main includes PR #133, which froze the durable Phase-6 live-evidence backend without arming collection or creating elapsed credit.

## Frozen product / authority boundaries

- directional core: `BRRK-0011`;
- target/tradable long universe: `BTC / ETH / SOL / BNB`;
- XRP remains feature-only;
- primary venue: Hyperliquid;
- canonical daily decision boundary: `00:00 UTC`;
- P3.2 target engine remains `P3.2-BRRK0011-V1`;
- P3.3 control remains `P3.3-L1-BAND-V1`, aggregate L1 band `0.05`;
- production gross cap remains `1.0`;
- no P5 cycle overlay was promoted;
- no >1 production leverage was promoted;
- no production component is authorized;
- no automated withdrawal/external-transfer authority;
- credentials or `TRADING_MODE=trade` do not create production authority;
- first transition from zero exposure to risk-on remains human-gated;
- no first real short is authorized.

## Phase 4 / 5 immutable research closeout

`LEVERAGE-0040` and `LEVERAGE-0041` remain immutable `NO_PROMOTION`. No research cap, operating drawdown budget or prospective production leverage cap was selected.

`LEVERAGE-0040` immutable summary SHA256:

```text
3bb4dc46c61a5e9c7e049862575a89b2771830410ce4bc2bb25c83e469f52fc0
```

P5.5 immutable result:

```text
result commit   ae20890d87567c98e403e3558219d5de55daef67
summary SHA256  ccbdc067f9f7f1277e6eecaa2f74f31f84e3a1882ccef418e097b2ea66bf6e71
selection       NO_PROMOTION_FAIL_STOP
P5.6 eligible   false
```

No cycle-risk multiplier is carried into Phase 6 or Phase 7.

## STABLECOIN-LIQUIDITY-0001 — terminal

The prospectively governed Stage-1 mechanism test completed exactly once and is permanently closed:

```text
result_status                    FAIL_NO_INCREMENTAL_INFORMATION
failure_reason                   PRIMARY_MEAN_LOSS_DIFFERENTIAL_NONPOSITIVE
promotion_state                  NO_PROMOTION
valid_oos_prediction_count       933
mean_primary_loss_differential   -5430210.12771038
hac_max_lag                      19
hac_test_statistic               -1.2454264237630361
hac_one_sided_p_value            0.8935124773215692
primary_result_digest            d920d45397d45ae5636a2f3c682600778d4d087d97e035ba911844cca65821ff
stage1 merge commit              dd50ec35085eee2a2883dc1b29e3dd21ec52b043
stage1 workflow run              31264048473 / run_attempt=1 / SUCCESS
terminal closeout                MERGED #131
edge admission                   NONE
stage2 robustness eligibility    NONE
production_authorized            false
```

`RUN_ONCE_STAGE1.marker` is permanent. The same research ID may not be rerun or rescued through lag, alpha, horizon, representation or secondary-metric changes. The Edge Registry remains empty for Stablecoin.

## Program-Level Epistemic Governance v1

Frozen prospective boundary:

```text
legacy_boundary_commit      = 896cbd123b7a0c38943815dd802f0f9dcd12e1c2
research_governance_version = 1
```

Canonical authority planes remain separate:

- `config/decision_registry.json` — product/decision/production authority;
- `config/research_registry.json` — experiments, lineage, variant accounting and research debt;
- `config/dataset_exposure_registry.json` — prospective dataset/exposure events;
- `config/edge_registry.json` — admitted incremental-information edges only;
- `config/phase6_shadow_contract.json` — Phase-6 acceptance and zero-authority boundary;
- `config/phase7_launch_readiness.json` — Phase-7 launch gate;
- `research/bear_short_0001/BEAR-SHORT-0001.json` — Phase-8 trigger-gated research state.

Future result-bearing research must be preregistered prospectively under exactly one `PROGRAM_GOVERNED_V1` record. Historical unknowns remain explicit governance debt rather than fabricated facts.

## Phase 6 — implementation vs elapsed evidence

Merged Phase-6 canonical shadow implementation/replay remains:

```text
status                       PASS_SHADOW_ONLY_IMPLEMENTATION_REPLAY
production_authorized        false
signature_authorized         false
order_submission_authorized  false
```

Real elapsed evidence remains:

```text
status                       MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT
minimum elapsed days         14
minimum scheduled decisions  10
minimum emergency drills     1
critical reconciliation      0 required
unexplained target drift     0 required
schedule failures            0 required
```

CI replay, historical replay, workflow rerun and duplicate decision timestamps cannot backfill elapsed credit.

### Phase-6 preactivation gate

Machine authority:

- `research/governance/phase6_live_observation_gate.json`
- `research/governance/phase6_live_observation_gate.py`

Current candidate gate state in PR #134:

```text
status                                      PREACTIVATION_BLOCKED_FAIL_CLOSED
collector_armed                             false
schedule_configured                         false
elapsed_evidence_credit_authorized          false
observation_account_identity_frozen         false
current_position_equity_valuation_frozen    true
durable_create_only_evidence_backend_frozen true
schedule_and_duplicate_credit_rule_frozen   true
dependencies_ready                          false
production_authorized                       false
signature_authorized                        false
order_submission_authorized                 false
```

### Durable evidence backend — frozen / merged #133

Machine authority:

- `research/governance/phase6_live_evidence_contract.json`
- `research/governance/phase6_live_evidence.py`

Frozen semantics:

- GitHub Actions Artifact v4;
- retention 90 days;
- `overwrite=false`;
- empty uploads hard fail;
- immutable artifact ID / URL / digest required;
- evidence bundle must be uploaded before a separately uploaded hash-bound receipt;
- runner files, logs and step summaries alone are not elapsed evidence;
- the backend contract itself creates zero decision/time credit.

### Current-position / account-equity valuation — PR #134 candidate

Machine authority:

- `research/governance/phase6_live_valuation_contract.json`
- `research/governance/phase6_live_valuation.py`

`PHASE6-LIVE-VALUATION-V1` is operational measurement semantics only. It does not change P3.2 targets, P3.3 economics, routing economics or production authority.

V1 accepts only explicit Hyperliquid Standard mode:

```text
userAbstraction = disabled
```

Unified Account, Portfolio Margin, `default`, DEX abstraction and unsupported account surfaces fail closed and receive zero Phase-6 elapsed credit.

For canonical economic assets:

```text
perp component = sign(szi) * abs(positionValue)
spot component = balances[].total * verified spot markPx
P3.3 current_positions_notional_usd = spot component + perp component by economic asset
```

Verified spot identities are inherited from the canonical instrument registry:

```text
BTC -> UBTC
ETH -> UETH
SOL -> USOL
BNB -> spot forbidden / PERP_ONLY_DEFAULT
```

Standard-mode account equity is frozen as:

```text
first-perp-dex marginSummary.accountValue
+ spot USDC total
+ allowed canonical spot base mark-to-market value
```

Unknown nonzero spot/perp assets, duplicate identities, invalid marks, nonpositive equity or unsupported abstraction modes hard fail. External exchange/wallet balances are not silently aggregated.

### Four pre-arm dependencies

```text
1. observation account identity              UNRESOLVED
2. current-position/equity valuation         FROZEN IN #134 CANDIDATE
3. durable create-only evidence backend      FROZEN / MERGED #133
4. schedule + duplicate-credit rule          FROZEN / MERGED #132/#133
```

Therefore PR #134 advances Phase-6 preactivation from 2/4 to **3/4**, but does not arm anything.

The one remaining external dependency is one exact verified read-only Hyperliquid master/subaccount address compatible with `PHASE6-LIVE-VALUATION-V1`. The address must represent the actual observed account, not an agent-wallet identity. No address may be invented or derived from a private key merely to close the gate.

If the eventual account does not return `userAbstraction=disabled`, the collector remains blocked. V1 must not be broadened post-observation merely to make that account fit.

## Phase 7

Phase 7 remains:

```text
current_program_state = MONITOR_ONLY
production_authorized = false
launch                 = BLOCKED
```

Launch requires the complete readiness checklist, including genuine Phase-6 elapsed evidence and explicit owner approval. Human approval remains mandatory for `MONITOR_ONLY -> ACTIVE`, `FLAT -> LONG`, `FLAT -> SHORT` and the first short exposure of a new bear phase.

## Phase 8

`BEAR-SHORT-0001` remains:

```text
status                       PREREGISTERED_TRIGGER_ABSENT_NOT_RUN
trigger_present              false
selection_status             NONE_TRIGGER_ABSENT
short_ready                  false
production_authorized        false
first_real_short_authorized  false
```

No subjective market judgment substitutes for the missing `CONFIRMED_BEAR_TRANSITION_ARTIFACT`.

## Drift status at PR #134 candidate

The first #134 governance run validated the new valuation/gate logic and all canonical semantic invariants. The only first-pass no-drift failure was caused by two temporary new `docs/**` candidate paths outside the Governance-v1 allowlist. Those temporary files were removed; the allowlist was **not** broadened.

No canonical strategy/economic/production authority was changed:

```text
BRRK-0011                         unchanged
BTC/ETH/SOL/BNB long universe    unchanged
XRP feature-only                 unchanged
Hyperliquid primary venue        unchanged
00:00 UTC decision boundary      unchanged
P3.2 target engine               unchanged
P3.3 L1 band                     unchanged
production gross cap = 1.0       unchanged
production_authorized_components unchanged / []
Phase 7 MONITOR_ONLY             unchanged
Phase 8 short authority          none / unchanged
Stablecoin terminal FAIL         unchanged
```

The final #134 head must re-pass full governance/no-drift/parity/Phase-6 safety CI before merge. No historical failed workflow is relabeled as PASS.

## Exact next action

```text
1. COMPLETE FINAL #134 CI/GOVERNANCE ON THE AUTHORITATIVE HANDOFF HEAD
2. MERGE #134 ONLY WITH EXPECTED-HEAD PROTECTION AFTER ALL REQUIRED CHECKS ARE GREEN
3. VERIFY THE NEW MAIN SHA AND RECHECK CANONICAL NO-DRIFT INVARIANTS
4. FREEZE ONE EXACT PUBLIC READ-ONLY HYPERLIQUID MASTER/SUBACCOUNT ADDRESS
5. VERIFY THAT ADDRESS RETURNS userAbstraction=disabled AND FITS PHASE6-LIVE-VALUATION-V1
6. DO NOT USE OR DERIVE A PRIVATE KEY TO ESTABLISH THE OBSERVATION IDENTITY
7. ONLY AFTER ALL 4/4 PRE-ARM DEPENDENCIES ARE FROZEN, CREATE A SEPARATE PROSPECTIVE ARM CHANGE
8. FIRST ELIGIBLE SCHEDULED DECISION = FIRST 00:00 UTC STRICTLY AFTER THE ARM COMMIT TIMESTAMP
9. NEVER BACKFILL / REPLAY-CREDIT / RERUN-CREDIT / DUPLICATE-CREDIT PHASE-6 ELAPSED EVIDENCE
10. KEEP PHASE 7 MONITOR_ONLY AND ALL PRODUCTION/SIGNATURE/SUBMISSION AUTHORITY FALSE
```

After the Phase-6 collection path is genuinely operational, resume the infrastructure roadmap: formal research lifecycle/state-machine enforcement, then Research Queue / trial-overlap accounting. Do not start Stablecoin rescue, Holder Cost, new leverage, new allocation or bear-short economics as a substitute for closing the Phase-6 observation dependency.