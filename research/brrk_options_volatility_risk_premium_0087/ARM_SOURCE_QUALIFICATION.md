# BRRK Options Volatility Risk Premium 0087 — ARM source qualification

Research ID: `BRRK-OPTIONS-VOLATILITY-RISK-PREMIUM-0087`
Gate: `ARM source qualification`
Status: `BLOCKED_NO_QUALIFYING_CONTROLLED_SOURCE_METADATA`
Controlled attempt: `0/1`
Controlled value reads: `0`
Scientific engine calls: `0/1`
Scientific values exposed: `false`
Production/signature/order/withdrawal/transfer authority: `false`

## Qualification result

The live repository was searched from exact main `20f2a5290bfb37ee2c6e02f2f2e9e0bd57f1b782` after the 0087 BUILD merge. No existing Worker B ARM branch or open ARM PR exists. Repository code, issues and research paths contain no qualifying Deribit controlled source identity plus metadata/schema evidence sufficient to bind the merged 0087 SPEC and BUILD without opening historical payload values.

ARM requires pre-exposure evidence for all of the following:

- immutable Deribit artifact/run/object identities, declared digest and size;
- BTC and ETH option instrument identity, strike and expiration timestamps;
- point-in-time executable option bid and ask at the frozen Monday 08:00 UTC observation;
- contemporaneous source-native option IV used by frozen `ATM_IVAR30`;
- underlying index closes sufficient for the exact 30-return `RV30` window;
- source-native expiry/settlement convention and the common numeraire mapping used by the source-convention-neutral BUILD economic core;
- source-native option delta / hedge-target semantics at each frozen daily UTC hedge point;
- point-in-time executable underlying hedge bid and ask;
- source timestamps and schema fields that establish PIT ordering before scientific execution;
- deterministic source keys/read budget compatible with `ControlledResearchRunnerV1SourceQualified`.

The live repository search found no evidence set satisfying these requirements. In particular, no repository source/schema binding for Deribit `best_bid`/`best_ask`, contemporaneous IV, expiration/settlement, or delta/hedge-target fields could be established.

## Fail-closed consequence

0087 does not advance to ARMED and no controlled RUN may start. This is a pre-scientific engineering/data-qualification blocker, not `PASS_OPTIONS_VRP_STRUCTURE`, `FAIL_NO_ROBUST_OPTIONS_VRP`, `INCONCLUSIVE_INSUFFICIENT_OPTIONS_SUPPORT`, or `INVALID_EXECUTION`.

The project must not invent a source schema, substitute midpoint marks, use another venue, relax the frozen observation time/maturity, reconstruct historical bid/ask after exposure, choose a post-exposure delta model, or assume a Deribit settlement convention without pre-exposure source evidence.

A future reversible ARM continuation is legal only if a qualifying point-in-time Deribit source is independently staged and its metadata/schema can be verified before any controlled historical value exposure. That continuation does not consume the current attempt and does not create a replacement research ID.

## What did not change

- 0087 SPEC_FREEZE and BUILD science remain frozen exactly as merged.
- 0087 controlled attempt remains `0/1`; controlled reads remain `0`; scientific engine remains `0/1`; scientific values remain unexposed; no RUN marker exists.
- No scientific terminal classification is assigned to 0087 by this source-qualification blocker.
- 0086 remains ARM-complete at attempt `0/1` and requires a separate irreversible authorization before RUN. Factor L/S remains blocked unless 0086 returns a valid PASS.
- 0085 remains immutable `INVALID_EXECUTION`, attempt `1/1` consumed, with no admissible Trend result and no same-ID rerun/rescue/recompute.
- 0076 remains sealed at its pre-marker incident; 0072/0073 remain paused; 0083 remains immutable FAIL; 0070/0071/0074/0075/0084 remain immutable anchors.
- Phase6 remains immutable PASS closeout and is not evidence for a future final-candidate shadow.
- `CONTROLLED_RESEARCH_RUNNER_V1` source-qualified interface remains mandatory for every future 0086+ controlled RUN.
- `workflow run                         31381953131 / attempt 1` remains immutable.
- CAPTURE-0001 remains sealed/no-retry.
- CAPTURE-0002 remains permanently claimed/no-refetch.
- No production, signing, order, withdrawal, or transfer authority is granted.
