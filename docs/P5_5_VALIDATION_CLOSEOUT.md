# P5.5 Joint Profile/Behavior Validation — Research Closeout

Status: **COMPLETE / IMMUTABLE / NO_PROMOTION / FAIL_STOP**

This closeout records research evidence only. It does not authorize production, live trading, leverage changes, or automatic re-risk.

## Immutable result

- Contract: `P5.5-JOINT-PROFILE-MAP-VALIDATION-V1`
- Pre-result amendments: `R1` MaxDD sign semantics and `R2` common observable end
- Result commit: `ae20890d87567c98e403e3558219d5de55daef67`
- Summary SHA256: `ccbdc067f9f7f1277e6eecaa2f74f31f84e3a1882ccef418e097b2ea66bf6e71`
- Economic window: `2022-12-10 .. 2026-02-28`
- Candidates: 12
- Eligible candidates: 0

```text
selection_status              NO_PROMOTION_FAIL_STOP
profile_selected              NONE
behavior_map_selected         NONE
p5_6_integration_eligible     false
production_authorized         false
risk_permission_unlock        false
```

## Main finding

The frozen candidate family exhibits a structural trade-off rather than a robust sweet spot.

`HARD_ONLY` preserves the baseline economics exactly in the authoritative economic sample, but fails the frozen 2021 terminal-event partial-de-risk behavior gates and therefore is not an acceptable cycle overlay.

The gradual-de-risk maps generally improve drawdown magnitude, but the return sacrifice is too large under the frozen wealth-maximization-under-constraints objective. Representative 5-bps results:

```text
BRRK baseline CAGR                  0.797629
EARLY / GENTLE CAGR                 0.657242   (-0.140387)
BALANCED / GENTLE CAGR              0.721452   (-0.076177)

BRRK baseline MaxDD                -0.335292
EARLY / GENTLE MaxDD               -0.305992   (+0.029301 abs improvement)
BALANCED / GENTLE MaxDD            -0.315212   (+0.020080 abs improvement)
```

Thus the closest gradual policy still gives up roughly 7.6 percentage points of annualized CAGR for about 2.0 percentage points of absolute drawdown improvement. This is far outside the frozen 0.5–1.0 percentage-point CAGR tolerance gates.

More aggressive maps improve drawdown further but sacrifice still more terminal wealth/CAGR and often Calmar robustness. Start-date and event-held-out robustness also fail for the gradual policies.

## Gate structure

No candidate passes all of:

- terminal-event behavior;
- 2021/2025 second-wind preservation;
- known 2021 false-FLAT visibility/finite duration;
- 5/10/20/50-bps economic gates;
- minimum usefulness;
- start-date robustness;
- event-held-out robustness;
- adjacent-policy robustness.

The failure is not caused by a hidden 2021 BRRK backtest: 2021 is behavior diagnostics only. Authoritative BRRK economics begin `2022-12-10`. R2 stops at the immutable common cycle-state coverage end `2026-02-28`; no state forward-fill or fabricated extension was used.

## Disposition

```text
P5.3 V2 architecture      ACCEPTED AS RESEARCH ARCHITECTURE
P5.4 mapping mechanics    COMPLETE / NO SELECTION
P5.5 validation           COMPLETE / IMMUTABLE / NO_PROMOTION / FAIL_STOP
selected cycle profile    NONE
selected behavior map     NONE
P5.6 cycle integration    BLOCKED / NO ELIGIBLE CANDIDATE
production authorization  NONE
```

Do not retune P5.3 profile thresholds or P5.4 multiplier values against this result under the same experiment. Any future cycle-overlay attempt requires a new preregistered research hypothesis and new experiment identity.

## Roadmap continuation

P5.6 cannot honestly integrate a cycle overlay. Close P5.6 as blocked/no-candidate rather than selecting a loser. Continue Phase 6 against the currently authorized baseline architecture: frozen BRRK/P4.1 semantics, production gross cap `1.0`, no cycle-risk overlay, and zero trading/signing authority in shadow mode.

This preserves the roadmap while keeping failed research out of production.
