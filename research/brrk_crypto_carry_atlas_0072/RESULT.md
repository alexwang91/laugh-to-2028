# BRRK-CRYPTO-CARRY-ATLAS-0072 — Stage 9 RESULT

## Lifecycle status

Formal Stage 9 RESULT records the immutable Stage 8 controlled-attempt outcome for `BRRK-CRYPTO-CARRY-ATLAS-0072`.

- Stage 8 result bundle merge: `947475dc058c6204f20e1d26f719a1fea845876a`
- Controlled attempt: `1/1`, permanently consumed
- Scientific engine calls: `1/1`
- Controlled scientific-object reads: exactly `6`
- Raw artifact downloads: exactly `1`
- Source-network fetches during Stage 8: `0`
- Execution valid: `true`
- Evidence tier: `RESEARCHER_UNEXPOSED_CAPTURED_DEVELOPMENT_HISTORY_NOT_INDEPENDENT_OOS`
- Terminal scientific classification: `INCONCLUSIVE_INSUFFICIENT_SUPPORT`

This RESULT performs no scientific recomputation and introduces no new read, model, threshold, hypothesis, family, source, seed, replicate count, strategy, portfolio, production, signature, or order authority.

## Frozen support outcome

The immutable Stage 8 result contains 63 eligible state rows: BTC `21`, ETH `21`, SOL `21`.

Frozen support counts:

- extreme-carry rows: `0`
- nonextreme rows: `63`
- crash-positive rows: `0`
- support sufficient: `false`

Therefore gate `G1_SUPPORT_SUFFICIENT` fails. H06 `EXTREME_CARRY_CRASH_ASSOCIATION` is undefined under the preregistered contract. No same-ID rescue, threshold relaxation, family substitution, additional history, or recomputation is legal.

## Frozen hypothesis results

The immutable observed effects and preregistered permutation p-values are:

| Hypothesis | Effect | Permutation p-value |
| --- | ---: | ---: |
| H01 BASIS_PERSISTENCE | `-0.0038961038961038952` | `0.48262586870656465` |
| H02 BASIS_MEAN_REVERSION | `-0.6896103896103895` | `0.00004999750012499375` |
| H03 BASIS_VOLATILITY_ASSOCIATION | `-0.05454545454545454` | `0.6493675316234189` |
| H04 BASIS_VOLUME_ASSOCIATION | `-0.003032930081537899` | `0.5005249737513124` |
| H05 BASIS_TREND_ASSOCIATION | `0.17402597402597397` | `0.12924353782310885` |
| H06 EXTREME_CARRY_CRASH_ASSOCIATION | undefined | undefined |

All persisted BH-adjusted q-values are null under the frozen result because the required family is incomplete once H06 is undefined. H02's small unadjusted one-sided permutation p-value does not override the failed support gate and cannot justify a same-ID rescue or reinterpretation.

## Leave-one-asset robustness record

The immutable H02 mean-reversion effect remains negative in every leave-one-asset calculation:

- leave BTC out: `-0.6519480519480518`
- leave ETH out: `-0.6909090909090909`
- leave SOL out: `-0.7259740259740258`

This is descriptive evidence inside the same researcher-unexposed captured DEVELOPMENT-history attempt. It does not convert the terminal classification to PASS and is not independent OOS evidence.

## Economic metrics

No strategy translation or portfolio PnL was preregistered for 0072 Stage 8. The frozen RESULT schema therefore does not define CAGR, annualized return, Sharpe, Sortino, MDD, Calmar, terminal wealth, turnover, cost drag, exposure, concentration, DSR, PBO, cost break-even, stress, or capacity metrics for this ID. No such values may be fabricated or inferred from the carry-atlas association statistics.

## Governance interpretation

`INCONCLUSIVE_INSUFFICIENT_SUPPORT` means the authorized one-shot history did not contain enough frozen support to evaluate the full six-hypothesis family. It is neither a scientific PASS nor a scientific FAIL of the carry-atlas thesis. The attempt nevertheless remains permanently consumed because execution was valid and the exactly-once boundary was honored.

Same-ID rerun, retune, rescue, recompute, threshold modification, additional-source substitution, family substitution, or post-result window extension are forbidden. Production/signature/order authority remains `false/false/false`.

## Exact next step

After this Stage 9 RESULT and mandatory CURRENT_STATE handoff merge with all standing CI SUCCESS, create Stage 10 immutable `CLOSEOUT.md` that records `INCONCLUSIVE_INSUFFICIENT_SUPPORT / CLOSED TO SAME-ID RERUN` without rereading controlled scientific content or recomputing any result. Only after 0072 reaches 10/10 may the roadmap advance owner-first to 0073.