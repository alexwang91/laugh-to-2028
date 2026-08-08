# Phase 0–8 Full Drift Audit — 2026-08-08

Status: **PASS_FINAL_HEAD_VERIFIED / PENDING EXACT-HEAD MERGE**  
Drift classification: **DRIFT_2**  
Economic retuning: **NONE**  
Production authorization: **NONE**

Machine contract: `config/phase0_8_drift_audit.json`.

## Purpose

This audit checks whether the repository still enforces the frozen product/research boundaries after completing the currently executable Phase 0–8 roadmap work. It is not a new strategy experiment and does not reinterpret failed research.

Audit success means only that the checked repository state is internally consistent and fail-closed. It does not mean live evidence or human launch gates have passed.

## Phase-by-phase conclusion

| Phase | Audited invariant | Conclusion |
| --- | --- | --- |
| 0 | governance/source-of-truth remains explicit | PASS after handoff alignment |
| 1 | ledger/reconciliation/emergency controls do not imply production authority | PASS with legacy-authority remediation |
| 2 | routing/instrument implementation records remain implementation-only | PASS |
| 3 | BRRK-0011 target authority and P3.2/P3.3 chain remain canonical | PASS / unchanged |
| 4 | no >1 leverage promotion; production gross remains 1.0 | PASS / immutable |
| 5 | P5.5 NO_PROMOTION preserved; no cycle overlay integrated | PASS / immutable |
| 6 | replay implementation passed but signer/submit remain impossible; elapsed evidence not backfilled | PASS with time-dependent criterion still open |
| 7 | readiness only; MONITOR_ONLY; launch blocked; human transitions preserved | PASS / launch not authorized |
| 8 | BEAR-SHORT-0001 preregistered; confirmed-bear trigger absent; no short result/authority | PASS / trigger-dependent study not run |

## Material findings and remediation

### AUDIT-P08-001 — legacy execution authority bypass

The older BTC-only service used `Settings.can_trade` / `TRADING_MODE=trade` as sufficient entry into normal execution plumbing. That created a path in which a clean account could reach `execute_target_position` without consuming the canonical Phase 7 launch authority.

Remediation:

- added `beta_bot.production_authority` as an explicit current authority boundary;
- legacy normal-service new-risk authority is frozen `False`;
- risk-increasing normal execution is blocked before order submission;
- same-direction reductions remain executable;
- emergency/kill-switch paths remain independent and available.

This fix changes authority plumbing, not strategy economics.

### AUDIT-P08-002 — production-facing cap drift

Legacy environment examples, validation and execution documentation still exposed `NORMAL_BETA_CAP=1.30`, while canonical production gross has remained `1.0` after Phase 4 NO_PROMOTION.

Remediation:

- default `NORMAL_BETA_CAP=1.0`;
- validation rejects values above `1.0`;
- execution README and `.env.example` state that >1 production leverage is unauthorized.

### AUDIT-P08-003 — authoritative handoff drift

Top-level README and roadmap handoff files lagged already-merged Phase 6/7/8 work. Because README is source-of-truth #1, stale text was an operational hazard even though contracts/code were newer.

Remediation:

- README records merged Phase 6/7/8 state;
- `docs/CURRENT_STATE.md` points to the audit closeout as the completed repository task;
- `docs/NEXT_STEPS.md` points to real Phase 6 elapsed evidence as the next dependency.

## Machine-enforced invariants

The dedicated audit test asserts at least:

```text
production_authorized_components = []
production gross cap             = 1.0
legacy new-risk authority        = false
LEVERAGE-0040 immutable digest   = unchanged
Phase 6 sign orders              = false
Phase 6 submit orders            = false
Phase 6 live evidence            = MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT
Phase 7 mode                     = MONITOR_ONLY
Phase 7 production authorization = false
Phase 8 trigger present          = false
Phase 8 short_ready              = false
Phase 8 production authorization = false
```

Behavioral tests additionally prove that closing legacy normal new-risk authority does not remove same-direction risk reduction.

## Deliberately unchanged

The audit does not modify:

- BRRK-0011 target economics;
- P3.2 target formula or P3.3 rebalance semantics;
- LEVERAGE-0040/0041 research results;
- P5 immutable result artifacts;
- Phase 6 elapsed-observation evidence;
- Phase 7 owner approval state;
- Phase 8 trigger state or candidate economics.

## Verification evidence

Pre-closeout verification head:

```text
aa94f4c03c7897c4b6420f151f679c7f8da1b283
```

All applicable workflows on that head passed, including:

- Phase 0 baseline contract;
- P3.2 target research-live parity and committed golden vectors;
- P4.3 cap1 parity and LEVERAGE-0040/0041 compatibility contracts;
- P5 frozen preregistration/implementation compatibility workflows;
- Phase 6 integrated shadow safety / zero-signer / zero-submit checks;
- Phase 7 limited-live readiness gate;
- Phase 8 bear-short research contract;
- PR handoff governance;
- dedicated Phase 0–8 drift audit and legacy authority behavior tests.

The closeout status commit must receive the same final-head CI confirmation before exact-head merge. No semantic change is permitted between that confirmation and merge.

## Remaining external/time/human boundaries

After this audit merges, the next dependency is **not another implementation phase**. It is real Phase 6 observation time under the frozen contract.

No repository merge may convert these conditions into a pass by assertion:

1. Phase 6 must accumulate the required real elapsed shadow evidence.
2. Phase 7 launch requires the complete checklist and explicit owner approval.
3. BEAR-SHORT-0001 economics requires the frozen confirmed-bear transition artifact.
4. The first real short remains a separate human approval boundary.

## Closeout rule

Exact-head merge is permitted only if the closeout head passes the dedicated audit gate plus all applicable repository CI/governance. That merge does not grant production authority.
