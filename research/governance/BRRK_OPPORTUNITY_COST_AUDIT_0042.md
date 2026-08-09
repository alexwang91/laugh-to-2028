# BRRK Opportunity-Cost Audit 0042

Status: **DIAGNOSTIC ONLY / NO PROMOTION AUTHORITY**

This audit is a deterministic read-only diagnosis of already committed canonical historical artifacts. It is not a new strategy candidate, not a production decision, and not validation evidence for Phase 7.

## Question

Which mechanically observable parts of the frozen BRRK portfolio construction are associated with the user's concern that the strategy is slow, conservative, and under-captures dominant winners?

## Frozen inputs

- `research/results/pit_disp_0015/daily_weights.csv`
- `research/results/pit_disp_0015/daily_equity.csv`

No external data, parameter sweep, new signal, new target engine, leverage, shorting, or execution simulation is introduced.

## Measurements fixed before CI result review

1. Validate whether normalized BRRK target mixes equal normalized V1 target mixes on overlap days. Only if this passes may V1 → BRRK be described as observable gross defensive scaling.
2. Measure BRRK versus V1 CAGR and maximum-drawdown differences from the frozen equity curves.
3. Measure observable defensive-scale distribution from BRRK gross / V1 gross on valid overlap days.
4. Measure BTC share of gross on V1 alt-active days.
5. Measure structural cap signatures at ETH 50%, SOL 35%, BNB 25% of gross.
6. Measure adjacent target-vector change frequency and gap days.
7. Measure BRRK capture of V1's top-20 daily log-growth days and relative exposure on V1's bottom-20 days.

## Explicitly unavailable in this audit

- causal signal-speed attribution, because historical daily P3.2 signal/feature snapshots are not persisted;
- historical P3.3 5% account-gap return attribution, because current account position weights, `l1_target_gap`, controller plans and executed turnover are not persisted;
- winner-cap return counterfactuals, because changing caps would be a separate strategy experiment and must be separately preregistered before any result is viewed.

## Follow-up rule

The output may identify which mechanism deserves a separately preregistered experiment. It may not change BRRK-0011, Phase 6, production authority, or create an automatic promotion decision.
