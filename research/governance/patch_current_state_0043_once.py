from pathlib import Path

p = Path('docs/CURRENT_STATE.md')
text = p.read_text(encoding='utf-8')
text = text.replace('Handoff PR: **#153**', 'Handoff PR: **#155**')
text = text.replace('Handoff branch: `research/brrk-winner-robustness-0002-runonce`', 'Handoff branch: `research/brrk-exhaustion-event-study-0043`')
text = text.replace('Authoritative baseline main at branch creation: `11c7967e4d22766b3abee33d382ab2912c16f5cb`', 'Authoritative baseline main at branch creation: `0db4f6e4ca6d8fe610e54fbb96c9240752229cfd`')
text = text.replace('Latest merged research PR at branch creation: **#152**', 'Latest merged research PR at branch creation: **#153**')
for line in (
    'Handoff PR: **#155**',
    'Handoff branch: `research/brrk-exhaustion-event-study-0043`',
    'Authoritative baseline main at branch creation: `0db4f6e4ca6d8fe610e54fbb96c9240752229cfd`',
    'Latest merged research PR at branch creation: **#153**',
):
    text = text.replace(line + '  \n', line + '\n')
old = 'BRRK-WINNER-ROBUSTNESS-0002       ONE-SHOT PASS / FUTURE-ONLY VALIDATION ELIGIBLE / CLOSED\n'
new = old + 'BRRK exhaustion event study 0043 COMPLETE DIAGNOSTIC / 7-14D SIGNAL FEASIBLE / TRIGGER NOT READY\n'
if 'BRRK exhaustion event study 0043 COMPLETE DIAGNOSTIC' not in text:
    if old not in text:
        raise SystemExit('executive-state insertion anchor missing')
    text = text.replace(old, new, 1)

marker = '## BRRK-EXHAUSTION-EVENT-STUDY-0043 — complete diagnostic\n'
if marker not in text:
    insert_before = '## Dashboard V5\n'
    if insert_before not in text:
        raise SystemExit('dashboard insertion anchor missing')
    section = '''## BRRK-EXHAUSTION-EVENT-STUDY-0043 — complete diagnostic

PR #155 is a read-only DEVELOPMENT diagnostic created after merged PR #153. It mechanically separates genuine local exhaustion tops from ordinary pullbacks / continuation false tops and measures causal 7–14 day deterioration signals. User-provided dates are sanity checks only and do not define labels, thresholds, or score weights.

Unique execution and evidence binding:

```text
workflow run                         31381953131 / attempt 1
artifact id                          9060216534
artifact digest                      sha256:6df40bbe0112082f045cd4da7b461753382c6980a348609a35bed9967f1520c4
full result SHA256                   1ca030e544d6e3391143c9ec47e202f9585ce8a846e0e46be583c31258958b43
source summary SHA256                82579688952e990809a01044378b40cd44ceba84142307686cfa8ae05158c278
historical sessions                  1332
mechanically detected peak candidates 16
portfolio economics executed         false
```

Primary `-15%` competing-barrier panel:

```text
TRUE_EXHAUSTION / CONTINUATION / AMBIGUOUS     9 / 6 / 1
PRE14_7 total EXHAUSTION_SCORE AUC             0.7333
PRE14_7 F7 BRRK disagreement AUC               0.7556
PRE14_7 F4 volatility/downside AUC             0.7111
PRE14_7 F1 momentum decay AUC                  0.6889
PRE14_7 F2 price structure AUC                 0.6889
PRE7_0 F4 volatility/downside AUC              0.8444
PRE7_0 F7 BRRK disagreement AUC                0.8222
```

Severe `-20%` panel strengthens the one-to-two-week signal:

```text
TRUE_EXHAUSTION / CONTINUATION / AMBIGUOUS     7 / 6 / 3
PRE14_7 total EXHAUSTION_SCORE AUC             0.8571
PRE14_7 F7 BRRK disagreement AUC               0.8000
PRE14_7 F2 price structure AUC                 0.7714
PRE14_7 F4 volatility/downside AUC             0.7714
```

Important negative evidence remains binding: the frozen equal-weight absolute threshold is too insensitive. The 80th-percentile / 3-day rule catches only `2/9` primary true events, although it produces `0/6` continuation false triggers; those two hits lead by 10 and 21 days. No threshold is selected or rescued under ID 0043.

The 48 oriented raw features collapse to about `7.2046` effective dimensions; 14 pairs have `|corr| >= 0.85`, including one exact duplicate between F1 and F7. Future work must deduplicate rather than count technical indicators as independent votes.

Anchor sanity checks remain result-neutral: 2023-12-25 and 2024-03-31 are mechanically TRUE_EXHAUSTION; the January-2025 region maps to 2025-01-18 TRUE_EXHAUSTION; the October-2025 region maps to the nearby higher 2025-10-08 TRUE_EXHAUSTION. The 2024-11-24 region maps to 2024-11-22 and is AMBIGUOUS under the primary `-15% / 60-session` rule (`-11.77%` minimum), but TRUE_EXHAUSTION in the frozen `-10%` panel. The taxonomy is not altered to force the anchor to pass.

Interpretation: a 7–14 day exhaustion-ranking signal appears feasible, especially for severe drawdowns, but the first equal-weight absolute trigger is not operationally ready. ID 0043 is closed against result-informed pruning, reweighting, threshold rescue, dynamic-gross mapping, or portfolio-economic counterfactual. Any continuation requires a new research ID with deduplicated state dimensions and episode/block-aware validation.

Canonical BRRK-0011, Phase 6 and all production/security authority remain unchanged.

'''
    text = text.replace(insert_before, section + insert_before, 1)

drift = '## Current drift assessment\n'
if drift not in text:
    raise SystemExit('current-drift anchor missing')
prefix = text.split(drift, 1)[0]
tail = '''## Current drift assessment

`DRIFT_0`.

PR #155 is read-only research/governance diagnostic work. The final intended diff contains the frozen diagnostic design, implementation, permanent contract test, execution binding, compact result/summary and handoff evidence only. The temporary one-shot workflow is removed. No `execution/**`, no `research/results/**`, no canonical BRRK mathematics, no Phase-6 collection and no production authority are changed.

## Exact next task

1. Merge PR #155 only after final governance/no-drift/Phase-6/handoff CI is green and the final diff contains no temporary workflow, no `execution/**`, and no historical `research/results/**` mutation.
2. Preserve `BRRK-EXHAUSTION-EVENT-STUDY-0043` as closed DEVELOPMENT diagnostic evidence; do not prune, reweight, retune thresholds or run dynamic-gross economics under this ID.
3. If continuing the exhaustion line, create a new result-informed research ID before defining a deduplicated low-dimensional state model or trigger. Validation must be episode/block-aware because the 16 detected peaks are not fully independent macro regimes.
4. Only after a separately frozen signal stage passes should a later research ID map exhaustion state to gross exposure and evaluate portfolio economics.
5. Continue Phase-6 future-only observation independently. Production, signing and order-submission authority remain false.
'''
p.write_text(prefix + tail, encoding='utf-8')
