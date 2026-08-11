# BRRK-BETA-HANDOFF-EVENT-STUDY-0047 — Immutable Result

Status: **FAIL_NO_RECURRENT_DURABLE_HANDOFF_STRUCTURE / CLOSED**

Evidence class: **RESEARCHER_EXPOSED_DEVELOPMENT_HISTORY / NOT INDEPENDENT OOS**

## Bottom line

The exact preregistered durable BTC→Beta handoff structure did **not** recur often enough to pass the Stage-1 gate.

```text
target-eligible BTC-positive episodes     27
primary durable handoff episodes          12
episode-level prevalence                  12/27 = 44.4444%
frozen prevalence gate                    >=50%
ETH primary cause episodes                3
SOL primary cause episodes                9
result                                    FAIL_NO_RECURRENT_DURABLE_HANDOFF_STRUCTURE
```

Four of five hard gates passed. The **only** failed hard gate was `episode_level_prevalence_ge_0_50`.

This is a narrow negative result. It does **not** prove that BTC→Beta rotation is absent, non-predictable, or economically useless. It means the exact frozen definition — canonical BTC-positive episode plus the same unique ETH/SOL winner over BTC and the competing Beta at both +20 and +60 sessions while BTC itself is positive at both horizons — was present in 44.44% of eligible episodes rather than the preregistered majority threshold.

## Immutable execution identity

Unique scientific evaluation:

```text
GitHub Actions run                    31444910921
job                                  93636897419
attempt                              1
controlled head                      7c79f62e657c492afcb98be6c637905b2156f244
market payload SHA256                d1cd28bc76f2cd8ee0486287fc50b49e5451355a3e75132a2de5b30c15af3193
PRIMARY_RESULT pre-serialization SHA 961ac99bd5a2d3d6556262b17411333bfbeead921616dccf120190ee1dd67c2a
EXECUTION pre-serialization SHA      a87e37ae41e20d71e61dd52fb0b20009a5a6c6ffeeb6d0eb3d6faab568604665
```

The evaluation step completed successfully. A later post-result persistence assertion failed because JSON serialization converted integer `episode_intercepts` dictionary keys to strings. That changed the canonical hash after `json.loads()` but did not change the scientific object, market data, classification or gates. The failure therefore did **not** authorize a second scientific run.

Hash-locked evidence recovery:

```text
GitHub Actions run                    31445193701
job                                  93638056435
recovery commit                      8b813d7e25130ff47585e928e67c2c11a13205f2
recovery type                        EVIDENCE_RECOVERY_NOT_NEW_RESEARCH_EXECUTION
recovered object matched original    true
actual variants before / after       1 / 1
```

Official recovery artifact:

```text
artifact id                           9084248250
name                                  brrk-beta-handoff-0047-recovered-unique-result
digest                                sha256:b1992fa56b78a1a5807a156c8a483c0f035290669ff0e04095481d11000cde66
size                                  487959 bytes
```

### PRIMARY_RESULT hash semantics

Three hashes intentionally have different meanings and must not be conflated:

```text
original pre-serialization object    961ac99bd5a2d3d6556262b17411333bfbeead921616dccf120190ee1dd67c2a
recovered raw JSON file              6c354c2b29244a6a5389c49b4a315953132709c1b563d513f30bf6cd29e1d087
reparsed canonical JSON object       35f0c3dedbfb2a10ec20380d799006828358537928629431b51dbe05ff30bdaf
```

The original Actions log binds the first hash. The official recovery artifact preserves the latter two identities as durable serialization evidence.

## Dependence-aware uncertainty

The frozen complete-episode bootstrap used 10,000 resamples with seed `470047`.

For episode-level durable-handoff prevalence:

```text
2.5%       25.9259%
median     44.4444%
97.5%      62.9630%
```

This uncertainty is descriptive. The preregistered decision rule is the observed point prevalence gate, not a post-result confidence-interval rescue.

## Primary handoff anatomy

There were 12 mechanically labeled durable handoff episodes:

```text
ETH causes   3
SOL causes   9
```

Handoff state age:

```text
n           12
min          1
q25          1
median       1
q75          1.75
max         66
age == 1     8 / 12
```

Handoff opportunity-spell length:

```text
n           12
min          1
q25          1
median       2.5
q75          4.25
max         47
```

The concentration of primary labels at `STATE_AGE=1` is important negative evidence for the proposed later duration-aware clock: the canonical `BTC_TREND_FAST >= 0` episode boundary often restarts when Beta leadership is already present, rather than cleanly beginning in a BTC-lead state and later observing a transition.

## Leader/follower transmission diagnostics — non-gating

Pooled episode-preserving daily return cross-correlation peaked contemporaneously:

```text
BTC / ETH peak lag          0
peak correlation            0.7689590617

BTC / SOL peak lag          0
peak correlation            0.5425798452
```

Lag convention is `corr(BTC_t, ALT_{t+lag})`; positive lag means BTC leads. The dominant peak at zero therefore does not support a simple fixed N-day BTC-leading delay.

The frozen pooled episode-preserving VAR(7) was estimable and stable:

```text
eligible VAR rows            1103
episodes contributing rows   13
spectral radius              0.7206946901
stable companion             true
```

All six directed Granger/Wald diagnostics were estimable under the frozen episode-cluster CR0 convention and showed statistically strong structure. The generalized BTC-shock impulse response was strongest contemporaneously and then decayed/oscillated rather than producing a clean persistent one-way delayed Beta response. These outputs are descriptive only and cannot rescue the failed recurrence gate.

## Hindsight one-switch opportunity bound — non-gating

The frozen one-switch oracle found positive uplift versus BTC-only in:

```text
17 / 27 episodes
```

Of those, **7 episodes had positive oracle uplift without a frozen durable-handoff label**.

This demonstrates that the dual-horizon durable target does not exhaust the descriptive economic opportunity set. It does **not** authorize changing the target under 0047 and does not establish causal tradability.

Examples include the 2021-04-08 to 2021-05-18 BTC-positive episode: the oracle preferred a BTC→SOL switch and produced approximately `1.1518` log-wealth uplift versus BTC-only, yet the frozen durable-handoff target did not label that episode. The larger 2021-07-26 to 2021-12-03 episode did contain a SOL durable handoff and the one-switch oracle uplift was approximately `1.7340` log wealth.

## Interpretation

The correct interpretation is:

1. **Durable handoffs exist.** Twelve episodes passed the strong dual-horizon label and both ETH and SOL appeared as causes.
2. **The exact frozen structure is not recurrent enough.** `44.44% < 50%` makes 0047 a valid FAIL.
3. **The current state clock is problematic for the planned hazard model.** Two thirds of handoffs occur on episode day 1, so a model framed as “start in BTC leadership and estimate later handoff hazard” is not justified by this exact episode segmentation.
4. **There is no simple fixed BTC lag.** Daily pooled XCF peaks at lag 0 and the VAR/IRF structure is richer and bidirectional.
5. **The frozen target is stricter than the descriptive economic opportunity set.** Oracle-positive episodes exist outside the durable label, but that is diagnostic evidence only.

Therefore the preregistered 0048-style duration-aware competing-risk model is **not stage-eligible from this lineage**. Any alternative episode definition, target architecture, state clock, model or portfolio mapping must use a new research ID and be preregistered before evaluation.

## What 0047 did not test

0047 did not fit a duration-aware hazard/semi-Markov model, did not run BOCPD, did not search a fixed switch delay, did not test BTC/winner 40/60, 20/80 or 0/100, and did not evaluate CAGR, Sharpe, Calmar, drawdown, turnover, cash credit or any portfolio economics.

Consequently this FAIL cannot be interpreted as evidence that aggressive Beta concentration cannot improve BRRK CAGR.

## Closure

```text
same-ID rerun allowed                 false
same-ID retuning allowed              false
same-ID rescue allowed                false
0048-style model stage eligible       false
portfolio allocation tested           false
portfolio economics executed          false
canonical BRRK changed                 false
Phase-6 changed                        false
production_authorized                  false
signature_authorized                   false
order_submission_authorized            false
```

0047 is permanently closed. Any result-informed continuation requires a new research ID.