# BRRK-FACTOR-LS-0088 Closeout

## Terminal classification

`FAIL_FACTOR_LS_GATES / CLOSED TO SAME-ID RERUN`

The unique authorized controlled attempt completed through `CONTROLLED_RESEARCH_RUNNER_V1` with execution classification `EXECUTION_VALID` and `scientific_result_admissible=true`. The scientific engine returned `FAIL_FACTOR_LS_GATES`.

## Immutable execution evidence

- GitHub Actions workflow run: `33028536813`, attempt 1.
- Controlled attempt: `1/1` consumed.
- Controlled source reads: `30,336` exactly once through the frozen manifest.
- Scientific engine invocations: `1/1`.
- Durable create-only attempt marker exists on `research/0088-factor-ls-attempt-marker-v1` before controlled reads.
- `PRIMARY_RESULT.json` and `RUN_ONCE.marker` were created on `research/0088-factor-ls-result-v1`.
- Frozen source identity: artifact `9495175701`, digest `sha256:8040282ff412b2d3fd360173e4745ebfd048796eb9e9c2ad49fa0901e5cedf56`.
- Frozen manifest identity: `sha256:c33b575cc436db795086458a25ca38fe1527f649809e549caba00e9754422e58#0088-usdm-kline-funding-30336`.

## Scientific result

The single frozen three-factor long/short sleeve did not satisfy the preregistered gate family.

- Annualized Sharpe: `0.09891513515488597`.
- Mean C0: `0.0027521631674629413`.
- Mean C1: `0.0017770658911983495`.
- Mean C2: `0.0008019686149337581`.
- Max drawdown: `-0.7439030735108538`.
- Positive-week fraction: `0.556420233463035`.
- Observations: `257`.
- Max capacity utilization: `0.005400960411088462`.
- Max absolute target weight: `0.1`.

Gate outcomes:

- G0 execution: PASS
- G1 support: PASS
- G2 net return: FAIL
- G3 Sharpe: FAIL
- G4 drawdown: FAIL
- G5 hit rate: PASS
- G6 chronology: FAIL
- G7 calendar: PASS
- G8 state and leave-one-year-out: FAIL
- G9 implementation: FAIL

The result is admissible scientific evidence of failure. It is not an infrastructure invalidation.

## Closure

Same-ID rerun, retune, rescue, factor reselection, sign reinterpretation, threshold relaxation, source substitution, or recomputation are forbidden. The 0086 Atlas factor signs remain immutable historical inputs; this 0088 failure does not rewrite 0086.

Production, signing, order-submission, withdrawal, transfer, and release authority remain false.
