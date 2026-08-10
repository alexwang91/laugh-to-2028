# BRRK-EXHAUSTION-TRIGGER-0045

Status: **PREREGISTERED / NOT RUN**
Governance: **PROGRAM_GOVERNED_V1**
Authority: **STATE-TRIGGER RESEARCH ONLY / NO GROSS MAP / NO PRODUCTION AUTHORITY**
Parent: `BRRK-EXHAUSTION-STATE-0044` — closed `PASS_TRIGGER_STAGE_ELIGIBLE`

## Purpose

0044 proved that a fixed low-dimensional exhaustion representation retains useful 7–14 day discrimination after macro-episode dependence control. It did not answer when the system should actually change state.

0045 freezes exactly one causal state machine before any trigger result is observed. The objective is to test whether the state can move from `HEALTHY` toward `WATCH` early enough, escalate severe events to `RISK` near the peak, avoid excessive continuation false alarms, and clear risk more slowly than it enters.

No portfolio weights or gross-risk values are defined under this ID.

## Frozen inputs

0045 reuses the exact 0044 mathematics:

- `CORE4`: equal-weight S1 momentum deceleration, S2 trend disagreement, S3 price structure, S4 volatility/downside;
- `S2`: the frozen trend-disagreement axis, used as an explicit confirmation input because 0044 found it strongest after result release;
- `S3`: the frozen price-structure axis, used only as part of recovery confirmation.

`S5` volume/OBV is excluded because 0044 preserved negative evidence: it reduced CORE4 discrimination and was approximately chance alone in the primary early-warning window. It cannot be reintroduced under 0045.

## Causal percentile normalization

For `CORE4`, `S2` and `S3`, the current value at session `t` is ranked only against the immediately preceding 252 available sessions, excluding `t`. At least 60 prior observations are required.

Percentile rank is the fraction of those prior observations less than or equal to the current value. No future or full-history percentile is permitted.

## Frozen state machine

### Entry conditions

`DECELERATION_RAW`:

```text
pct_CORE4 >= 0.60 OR pct_S2 >= 0.60
```

Enter `DECELERATION` when this holds on at least 2 of the latest 3 available sessions.

`WATCH_RAW`:

```text
pct_CORE4 >= 0.65 AND pct_S2 >= 0.65
```

Enter `WATCH` when this holds on at least 2 of the latest 3 sessions.

`RISK_RAW`:

```text
pct_CORE4 >= 0.75 AND pct_S2 >= 0.80
```

Enter `RISK` when this holds on at least 2 of the latest 3 sessions.

Entry is hierarchical: if multiple states qualify, enter the highest. `WATCH` may escalate to `RISK` whenever RISK qualifies.

### Clearing DECELERATION

A `DECELERATION` episode that never reached WATCH clears to `HEALTHY` only after `DECELERATION_RAW` is false for 3 consecutive sessions.

### WATCH/RISK hysteresis

Once `WATCH` or `RISK` has been entered, the machine cannot fall below WATCH until all of the following hold for 5 consecutive sessions:

```text
pct_CORE4 <= 0.45
pct_S2    <= 0.45
pct_S3    <= 0.50
```

Then the state becomes `RECOVERY`.

`RECOVERY` has a minimum 5-session hold. If WATCH or RISK qualifies during RECOVERY, the machine immediately escalates back to that higher state.

After the minimum hold, RECOVERY returns to HEALTHY only when all three repair conditions hold on at least 3 of the latest 5 sessions:

```text
pct_CORE4 <= 0.55
pct_S2    <= 0.55
pct_S3    <= 0.55
```

This is the preregistered `fast entry / slow recovery` asymmetry. No alternative persistence setting may be tested under 0045.

## Frozen event windows

Event labels and macro episodes reuse 0044 exactly.

```text
PRE14_7       sessions -14 through -7
PRE14_0       sessions -14 through 0 inclusive
PRE7_POST3    sessions -7 through +3 inclusive
PRE14_POST3   sessions -14 through +3 inclusive
PRE21_0       sessions -21 through 0 inclusive
```

A `WATCH-or-RISK hit` means at least one session in the window is WATCH or RISK. A `RISK confirmation` means at least one session is exactly RISK.

A transition onset is the first transition from below WATCH into WATCH/RISK in PRE21_0. Lead is measured in session distance to the peak.

## Premature-clear definition

For a primary TRUE_EXHAUSTION event that has a qualifying PRE21_0 WATCH/RISK onset and a frozen -15% downside-barrier date, a premature clear occurs if the state enters RECOVERY or HEALTHY after that onset but before the downside barrier is reached.

This directly tests whether hysteresis avoids the kind of early re-risking / whipsaw that motivated the study.

## Hard gates

A full PASS requires all frozen criteria, including:

- episode diversity >=4 usable episodes, TRUE >=2 episodes, CONTINUATION >=2;
- primary TRUE PRE14_7 WATCH/RISK hit rate >=0.50;
- continuation PRE14_0 WATCH/RISK false rate <=0.34;
- TRUE episode hit rate >=0.60;
- continuation episode false rate <=0.50;
- severe TRUE PRE14_7 WATCH/RISK hit rate >=0.57;
- severe TRUE PRE7_POST3 RISK confirmation >=0.57;
- continuation PRE14_POST3 RISK false rate <=0.17;
- at least four primary TRUE events have qualifying PRE21_0 onsets and median lead is 7–21 sessions inclusive;
- premature-clear rate before the -15% downside barrier <=0.25;
- no trigger-to-gross mapping and no canonical/Phase-6/authority change.

A failure closes 0045 with `FAIL_NO_DYNAMIC_GROSS_STAGE_ELIGIBILITY`. There is no same-ID rescue.

## Explicitly forbidden

- threshold or percentile grid search;
- persistence search;
- alternative WATCH/RISK/recovery candidate;
- S2-only rescue or CORE4 reweighting;
- volume/OBV, breadth or correlation reintroduction;
- classifier fitting;
- data after 2026-08-02;
- portfolio counterfactual, gross map, transaction-cost optimization;
- canonical BRRK or Phase 6 modification;
- leverage, shorts, signing, order submission or production authority.

Only a full 0045 PASS can make a separately preregistered dynamic-gross research stage eligible.
