# CARRY-STACK-0033 — idle-capital BRRK stack

Decision: **rejected** under the preregistered qualification rule. No same-window rescue tuning is authorized.

## What was tested

The strict-router BRRK directional portfolio was left completely unchanged. On each day, only BRRK's unused fully-funded capital was allocated to the exact frozen CARRY-PNL-0031 sleeve:

`carry_scale_t = clip(1 - held_BRRK_gross_t, 0, 1)`

This was intentionally not an optimized 80/20 stack. Combined gross was required to remain <= 1, and changes in carry allocation paid an additional 5 bps per absolute scale change.

Before the stack was evaluated, the run reconstructed the full frozen 0031 carry path exactly. The persisted and reconstructed $10,000 final values both equaled **$11,719.8277666**, a $0.00 parity error, with 100% funding-event coverage and no required price gaps.

## Result

Common window: 2023-06-19 through 2026-07-30.

| Metric | Strict-router BRRK | BRRK + idle-capital carry |
| --- | ---: | ---: |
| Final $10k | $40,447.92 | $39,948.40 |
| CAGR | **56.66%** | **56.04%** |
| Max drawdown | **-34.95%** | **-35.08%** |
| Annualized vol | 44.16% | 44.16% |
| Sharpe | **1.235** | **1.226** |
| Calmar | **1.621** | **1.597** |

All performance gates failed; only the gross-discipline gate passed.

## Attribution

Average held BRRK gross was **0.7445**, so the mechanical rule allocated an average **0.2555** of NAV to carry and activated carry on **62.3%** of days. Combined gross was exactly 1.0 under the conservative capital model.

However, the carry sleeve's historical returns were poorly timed relative to the days BRRK happened to leave capital idle:

- scaled carry before allocation-change cost: **-0.20% cumulative**;
- allocation-scale turnover: **20.866x**;
- additive scale-change cost at 5 bps: **1.043%**;
- scaled carry after scale-change cost: **-1.236% cumulative**.

From 2025 onward, strict-router BRRK returned about **+1.00%** cumulatively over the common subwindow, while the combined portfolio returned only **+0.37%**; scaled carry net contribution was about **-0.63%**.

The worst drawdown date remained 2024-09-06. Carry scale on that day was effectively zero, so the carry sleeve did not protect the principal BRRK drawdown and slightly worsened the wider path through nearby allocation changes.

## Interpretation

CARRY-PNL-0031 remains valid as an independent low-vol funding-carry mechanism. What fails here is the specific assumption that BRRK's idle-capital dates are a good time to deploy that carry. They are not in this historical sample, and frequent switching further destroys the economics.

Do not rescue 0033 by choosing a fixed carry weight, adding a gross threshold, removing BNB, filtering funding, leveraging carry, or reducing BRRK exposure on this same sample. Any future carry overlay must be justified independently by collateral/margin efficiency or execution structure rather than by optimizing this failed stack.
