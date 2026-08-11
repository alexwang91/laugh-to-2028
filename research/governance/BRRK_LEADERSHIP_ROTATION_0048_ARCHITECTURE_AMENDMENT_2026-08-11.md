# BRRK-LEADERSHIP-ROTATION-0048 — Architecture Amendment

Date: 2026-08-11  
Research ID: `BRRK-LEADERSHIP-ROTATION-0048`  
Status: **ARCHITECTURE AMENDMENT FREEZES ON MERGE / NUMERICAL PREREG NOT YET FROZEN / NOT RUN**  
Base main SHA: `5d3e5b57c861b2a544db5da7456e78e17e818b12`

This amendment revises the economic architecture frozen in:

`research/governance/BRRK_LEADERSHIP_ROTATION_0048_ARCHITECTURE_FREEZE_2026-08-11.md`

before any 0048 dataset registration, numerical preregistration, implementation, model fitting or historical result release.

The amendment is required because subsequent owner review clarified that BTC does not occupy the same economic role as ETH and SOL. No prior research result is altered, reopened, rerun, rescued or reinterpreted.

---

## 1. Binding evidence and authority remain unchanged

The following remain binding and immutable:

- `BRRK-BETA-HANDOFF-EVENT-STUDY-0047` remains `FAIL_NO_RECURRENT_DURABLE_HANDOFF_STRUCTURE / CLOSED`; no same-ID rerun, retuning or rescue is permitted.
- `BRRK-EXHAUSTION-STATE-0044` remains continuous DEVELOPMENT exhaustion/risk information.
- failed 0045 and 0046 discrete translations remain negative evidence and are not rehabilitated by this amendment.
- `BRRK-WINNER-0001` and `BRRK-WINNER-ROBUSTNESS-0002` remain researcher-exposed DEVELOPMENT evidence only.
- canonical BRRK strategy remains unchanged.
- Phase 6 future-only observation remains unchanged and independent.
- production, signing and order-submission authority remain false.

This amendment creates no dataset, runner, model fit, historical measurement or portfolio result.

---

## 2. Superseded economic assumption

The original 0048 architecture treated:

```text
BTC / ETH / SOL
```

as symmetric competitors for the same leadership state:

```text
BTC_LEAD
ETH_LEAD
SOL_LEAD
NO_CLEAR_LEADER
```

That assumption is superseded.

BTC, ETH and SOL do not serve identical economic functions in the intended portfolio hierarchy.

---

## 3. Revised hierarchy of capital

The revised architecture distinguishes three risk tiers:

```text
Cash
  |
BTC defensive anchor inside crypto
  |
Beta risk
  |- ETH
  `- SOL
```

Conceptually:

\[
Cash < BTC < Beta
\]

where:

- **Cash** represents gross-risk reduction outside crypto.
- **BTC** is primarily the defensive anchor inside crypto.
- **ETH/SOL** constitute the present Beta-selection universe.

For 0048, the Beta universe is limited to:

\[
\{ETH,SOL\}
\]

UNI, AAVE, BNB and other assets are outside this research ID.

---

## 4. Revised meaning of BTC

BTC is not a third Beta winner candidate in 0048.

BTC has a distinct economic role:

> When Beta no longer offers sufficient continuation value, but the broader crypto regime does not yet justify moving to cash, BTC is the intermediate defensive anchor.

Therefore:

```text
SOL -> BTC
ETH -> BTC
```

are risk-tier changes and are not the same mechanism as:

```text
SOL <-> ETH
```

which is winner selection inside the Beta tier.

---

## 5. Revised 0048 scientific question

0048 now asks:

> **Within a causally identified crypto-uptrend environment, does current ETH/SOL relative state contain stable, recurrent and causally usable information about which Beta asset will produce the stronger subsequent relative wealth path?**

0048 therefore studies:

\[
ETH \leftrightarrow SOL
\]

only.

BTC does not receive a 0048 winner label.

---

## 6. Revised 0048 state space

The 0048 economic output space becomes:

```text
ETH_LEAD
SOL_LEAD
NO_CLEAR_BETA_LEADER
OUTSIDE_0048_BETA_UPTREND_SCOPE
```

`NO_CLEAR_BETA_LEADER` is mandatory at the architecture level. The later numerical design must not treat a tiny relative-score difference as authority for extreme winner concentration.

---

## 7. Market-state eligibility remains separate from leadership

0048 may use an already-established, causal BTC trend state only to define whether Beta leadership is economically relevant.

Architecture-level semantics:

```text
BTC trend supportive     -> ETH/SOL leadership may be evaluated
BTC trend not supportive -> outside 0048 Beta-leadership scope
```

BTC trend is an eligibility variable, not a winner selector and not a handoff clock.

It may not be interpreted as:

```text
BTC leads first -> Beta must follow after N days
```

and therefore does not rescue the failed 0047 BTC-positive episode-clock hypothesis.

The exact numerical eligibility construction must be frozen in numerical preregistration before any historical measurement.

---

## 8. Revised program decomposition

The research program is explicitly hierarchical.

### 0048 — ETH/SOL Beta Leadership Information

Question:

\[
ETH\ or\ SOL?
\]

0048 is an information/mechanism stage only. It performs no portfolio allocation economics.

### 0049 — Beta Winner Concentration

Question:

> Given reliable immutable 0048 leadership information, how much Beta risk budget should be concentrated in the winner?

The owner-approved economic hypothesis may later examine an aggressive 80%-100% winner region, but no allocation percentage is frozen here.

### 0050 — Beta -> BTC Continuation-Value Handoff

Question:

> **When does BTC have greater continuation value than remaining in the current Beta leader?**

This is a risk-tier downgrade / shelter decision, not an ETH-vs-SOL ranking decision.

Possible future information families may include Beta/BTC relative deterioration, deterioration velocity, broader Beta weakness, cross-sectional state and separately frozen CORE4-derived information. No rule or threshold is frozen here.

### 0051 — BTC -> Cash Gross Exit

Question:

> **When does cash have greater continuation value than remaining in BTC/crypto?**

BTC->Cash remains a separate gross-risk/cycle-exit problem.

### 0052 — Integrated Hierarchical Router

Later integration may combine:

```text
ETH/SOL Beta leader
       -> BTC defensive anchor
       -> Cash gross exit
```

only after separate predecessor gates and preregistrations.

---

## 9. Revised program economic objective

The long-run portfolio objective is terminal compound wealth / net CAGR over a fixed common evaluation interval after realistic costs:

\[
\max W_T
\]

Intermediate maximum drawdown, Sharpe and Calmar are not the primary optimization objective.

A large spot-market drawdown does not by itself invalidate a strategy if terminal compound wealth is superior, provided no leverage/liquidation constraint is violated.

This architecture does not authorize leverage or shorting.

---

## 10. Consequence for 0048 target design

Because 0048 is a pure Beta-selection information study:

- future volatility is not embedded in the ETH/SOL winner target;
- future drawdown is not embedded in the winner target;
- BTC shelter utility is not embedded in the winner target;
- cash utility is not embedded in the winner target;
- portfolio CAGR is not measured in 0048.

0048 must isolate ETH/SOL relative leadership before later stages introduce risk-tier economics.

---

## 11. Consequence for feature architecture

The original three-asset symmetric leadership representation is superseded by:

> **A strictly antisymmetric ETH/SOL relative representation.**

Qualitatively, swapping ETH and SOL must reverse the sign of every primary dynamic feature and invert the predicted leadership probability.

No asset-name-specific fitted coefficient may create a permanent ETH or SOL preference.

A causal expanding historical prevalence prior may be represented separately from dynamic evidence if frozen prospectively in numerical preregistration.

Exact feature definitions and normalization belong to numerical preregistration.

---

## 12. Consequence for confidence

0048 must retain both:

1. winner direction; and
2. realized subsequent leadership magnitude.

The later numerical preregistration must define a causal confidence procedure and must permit an empirically unsupported concentration handoff to fail.

No numeric HIGH threshold is frozen by this amendment.

---

## 13. Revised adversarial null

The primary adversarial null becomes:

> **Apparent ETH/SOL rotation is explained by static historical prevalence, recent leader persistence or simple relative momentum rather than richer dynamic leadership information.**

Therefore 0048 must demonstrate incremental predictive information beyond strong, causal, preregistered simple baselines.

Beating random 50/50 alone is insufficient.

---

## 14. BTC Dominance is removed from primary 0048

BTC Dominance is removed from the primary 0048 architecture because:

1. it is primarily a market-diffusion variable rather than an ETH-vs-SOL winner selector;
2. it cannot by itself determine which Beta asset should lead;
3. no frozen reproducible BTC Dominance source presently exists in the repository; and
4. the revised 0048 scientific question can be tested without it.

No price-only proxy may be mislabeled as BTC market-cap dominance.

A future independent research ID may study BTC Dominance after prospectively freezing a reproducible source.

---

## 15. CORE4 is excluded from primary 0048

CORE4 is excluded from the 0048 primary leadership model.

Its natural future role is in the separate Beta->BTC continuation-value stage, where it may condition whether deterioration of the current Beta leader represents a broader risk-quality problem.

This preserves the distinction between:

```text
Who is the Beta leader?
```

and:

```text
Should the portfolio continue carrying Beta risk?
```

No CORE4 threshold is authorized here.

---

## 16. Broader cross-sectional state is reserved for later risk-tier work

Three-asset or broader crypto state variables such as:

- dispersion;
- average correlation;
- Beta breadth;
- rotation velocity; and
- broad participation

are not part of the primary 0048 winner selector.

They are reserved primarily for later Beta->BTC continuation-value research unless separately introduced by a new preregistered hypothesis.

This prevents 0048 from becoming an opaque all-purpose market-regime model.

---

## 17. No DeFi/universe expansion under 0048

0048 remains limited to:

```text
ETH
SOL
```

Specifically excluded from the primary universe are:

```text
UNI
AAVE
BNB
other DeFi tokens
other altcoins
```

Any future DeFi sleeve or universe expansion requires a new research ID and new preregistration.

---

## 18. Revised interpretation of success

A successful 0048 result would establish only:

> **ETH/SOL dynamic Beta-leadership information exists and is sufficiently stable to support a separately preregistered later allocation study.**

It would not establish:

- that 80%, 90% or 100% winner concentration is optimal;
- that BTC should be entered or exited at any particular point;
- that cash should be used;
- that MDD will improve;
- that portfolio CAGR will improve;
- that the historical result is independent OOS;
- that canonical BRRK should change; or
- that any production authority exists.

---

## 19. Revised interpretation of failure

Failure of the exact 0048 translation must not be broadened into a claim that all continuous ETH/SOL relative information is absent.

Immutable closeout must distinguish, where applicable:

- static prevalence explains the result;
- simple momentum explains the result;
- average dynamic information exists but is temporally unstable;
- winner direction is predictable but confidence does not map to larger realized leadership margins;
- only one direction is reliably identifiable;
- HIGH-confidence opportunities are too sparse; or
- no incremental dynamic leadership information is detected.

Negative and partial evidence must be preserved.

---

## 20. Explicitly superseded original 0048 clauses

The following concepts in the original 0048 architecture are superseded before any historical 0048 measurement:

```text
BTC / ETH / SOL as symmetric winner candidates
BTC_LEAD as a primary 0048 leadership state
three-asset symmetric leadership scoring
requirement that BTC occupy recurrent 0048 winning states
BTC Dominance as a possible primary 0048 feature family
0048 responsibility for winner -> BTC risk re-anchor
```

---

## 21. Preserved original 0048 principles

The following principles remain binding:

```text
leadership and broader risk are separate layers
NO_CLEAR state is mandatory
no fixed BTC-leading delay
no one-way BTC->ETH->SOL clock
no same-ID 0047 rescue
no historical threshold search
no portfolio allocation test in 0048
no 80/90/100 winner-allocation test in 0048
no CORE4 trigger search in 0048
no BTC->cash mapping in 0048
no canonical BRRK change
no Phase-6 change
no production/signing/order authority
dependence-aware validation is mandatory
static/simple alternatives must be adversarial controls
```

---

## 22. Numerical items remain unfrozen by this amendment

This architecture amendment does not itself freeze or release historical numerical results.

A subsequent numerical preregistration must freeze, before any result-bearing implementation:

1. exact forward ETH/SOL leadership target;
2. exact horizons and horizon weights;
3. exact antisymmetric feature construction;
4. exact market-state eligibility rule;
5. exact expanding/prequential training and label-maturity semantics;
6. exact probability model and calibration procedure;
7. exact causal baselines;
8. primary and secondary metrics;
9. dependence-aware bootstrap/subsampling rules;
10. confidence-strength and breakpoint method;
11. support, temporal and episode robustness gates;
12. exact result taxonomy;
13. exact dataset snapshot/provenance/hashes; and
14. one-candidate variant budget.

No result-bearing implementation may precede that preregistration.

---

## 23. Governance state created by merge

When this amendment is merged to `main`, the valid 0048 governance state becomes:

```text
REVISED ARCHITECTURE FROZEN
NUMERICAL PREREGISTRATION NOT YET FROZEN
NOT IMPLEMENTED
NOT RUN
```

The original architecture-freeze document remains preserved as historical governance evidence; this amendment supersedes only the clauses listed above.

No dataset, numerical result, canonical strategy change, Phase-6 change, production authorization, signing authorization or order-submission authorization is created.

---

## 24. Exact next permitted action after merge

After this amendment is merged, the only permitted next 0048 research action is:

> **Create and review a `PROGRAM_GOVERNED_V1` numerical preregistration consistent with the owner-approved Revised Architecture + Numerical Method Design v2.**

Implementation, model fitting and historical measurement remain prohibited until that numerical preregistration and dataset provenance are separately frozen.
