# BRRK-WINNER-0001

Status: **ONE-SHOT PASS / ROBUSTNESS STAGE ELIGIBLE ONLY**

This governed research path contains the frozen preregistration and the completed exactly-once development evaluation for one BRRK portfolio-construction candidate. The one permitted candidate has been executed and the research ID is closed against same-ID retuning.

## Frozen candidate

Only the canonical single-eligible-alt branch changed composition:

```text
canonical: BTC 50% / sole eligible alt 50%
candidate: BTC 40% / sole eligible alt 60%
```

Everything else remained frozen:

- BRRK/V1 signal horizons and weights;
- eligibility rules;
- multi-alt branch allocation and caps;
- BRRK defensive gross scale;
- long-only BTC/ETH/SOL/BNB universe;
- gross <= 1.0;
- 5 bps / canonical P3.3 economic simulator semantics.

## Completed one-shot result

The candidate executed exactly once in GitHub Actions run `31364706555` after canonical matched-P3.3 baseline reproduction passed. No 45/55, 35/65, 30/70, or other rescue allocation was evaluated.

```text
canonical CAGR                         65.3057%
candidate CAGR                         69.6917%
CAGR delta                             +4.3860 pp
canonical max drawdown                 -33.5292%
candidate max drawdown                 -33.4499%
canonical Calmar                       1.9477
candidate Calmar                       2.0835
canonical-best-20 log-growth capture   103.5595%
turnover ratio                         1.1229x
all frozen hard gates                  PASS
result_status                          PASS_ROBUSTNESS_STAGE_ELIGIBLE
```

Machine-readable evidence:

- `PREREGISTRATION.json`: immutable pre-result contract;
- `RUN_INTERFACE.json`: exactly-once execution interface;
- `PRIMARY_RESULT.json`: committed frozen economics and hard-gate result;
- `EXECUTION.json`: workflow/artifact provenance, single-execution accounting, and explicit hash bindings.

The temporary trigger marker and temporary workflow are intentionally absent after the successful one-shot execution; `EXECUTION.json` is the permanent provenance record.

The development history is explicitly researcher-exposed. This PASS is not unbiased OOS confirmation and does not modify canonical BRRK-0011, Phase 6 observation, Phase 7 launch state, execution authority, signing, order submission, leverage, or shorting. It only makes a separately preregistered robustness research stage eligible.

Do not run `BRRK-WINNER-0001` again. Any further allocation variant, period, parameter, or mechanism requires a new research ID and preregistration before additional economics are evaluated.
