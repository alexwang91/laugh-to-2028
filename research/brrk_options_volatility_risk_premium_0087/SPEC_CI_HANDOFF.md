# 0087 SPEC CI handoff

This handoff records the mechanical registry validation repair after the first PR exact-head governance check.

- Research ID: `BRRK-OPTIONS-VOLATILITY-RISK-PREMIUM-0087`
- Frozen science: unchanged from `SPEC_FREEZE.md`.
- Owner-first registry commit: `3686aec8a5a82d3a146828e464da090f0aea9a70`.
- First SPEC exact head: `f482cfc496279d86bb9f865bc01b1f5b0f807af1`.
- Failed workflow: Research governance core run `32895657848`, governance-core job `97957637643`.
- Failure: registry validator rejected the non-canonical research-domain token `VOLATILITY_RELATIVE_VALUE`.
- Canonical governance enum: `OPTIONS_VOLATILITY`.
- Repair commit: `38bcfe560f472596523e8a767b2b89e568b917c1`.
- Repair changes only the registry domain enum. It does not change venue, underlyings, maturity, selection, timing, volatility definition, hedging rule, costs, inference, support, trial budget, stopping rule, or terminal gates.
- Controlled attempt remains `0/1`; controlled reads remain `0`; scientific engine remains `0/1`; scientific values remain unexposed.

## What did not change

- 0076 remains sealed at its pre-marker read-boundary incident.
- Phase6 remains immutable PASS closeout.
- 0085 remains immutable `INVALID_EXECUTION`, attempt 1/1 consumed, with no admissible Trend result.
- 0086 remains ARM-complete at attempt 0/1 and requires separate irreversible authorization before RUN.
- 0072/0073 remain paused; 0083 remains immutable FAIL.
- `workflow run                         31381953131 / attempt 1` remains immutable.
- CAPTURE-0001 remains sealed/no-retry.
- CAPTURE-0002 remains permanently claimed/no-refetch.
- Production/signature/order/withdrawal/transfer authority remains false.
