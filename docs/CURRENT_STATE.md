# BRRK Current State

Last updated: 2026-08-25

Authoritative repository: `alexwang91/laugh-to-2028`.

## Immutable research anchors

- BRRK-EXHAUSTION-EVENT-STUDY-0043 — complete diagnostic; historical diagnostic state remains closed and unchanged.
  workflow run                         31381953131 / attempt 1
  7–14 day exhaustion-ranking signal appears feasible
  ID 0043 is closed against result-informed pruning, reweighting, threshold rescue
- 0064 = `PASS_PASSIVE_CASH_ACCRUAL_ROBUSTNESS / CLOSED TO SAME-ID RERUN`; merged closeout `ad8038af45bad2e25e8a7b88b569b1873635d9c2`.
- 0065 = `FAIL_NO_ROBUST_MULTI_ARCHITECTURE_IMPROVEMENT / CLOSED TO SAME-ID RERUN`; merged closeout `d1607277593a0c5c35bb0163e10e078f3dc85fc8`.
- 0066 = `INVALID_EXECUTION / CLOSED TO SAME-ID RERUN`; merged immutable timeout closeout `9a45bb5e778e21dfd30d7abc4ff7d9889542b495`.
- 0067 = `INVALID_EXECUTION / CLOSED TO SAME-ID RERUN`; attempt 1/1 consumed. Physical mismatch: validation 31,008/31,008, economic 5,808/11,904, P08 NNLS 20/40. No 0067 scientific result is admissible.
- 0068 = `PASS_EXECUTION_EQUIVALENCE / CLOSED`; immutable closeout `585308444719914028ac4410fba86948a5505a13`.
- 0069 = `PASS_EVENT_EARLY_WARNING_ONLY / CLOSED TO SAME-ID RERUN`; attempt 1/1 consumed; merged immutable historical result bundle `911b68225310ec7621e9937ff698e7dff84f9ae8`.
- 0070 = `PASS_LOCKED_EPISODE_ROBUSTNESS_REPLICATION / CLOSED TO SAME-ID RERUN`; attempt 1/1 consumed; merged immutable result bundle `174a30dc4950e7351f3a746edc8f581b8f12e6d3`; immutable closeout merge `d87607070cf03ccbbc318065f8c4c14ec6c6a50b`.
- Canonical BRRK-0011 = NO CHANGE.
- Phase 6 = NO CHANGE.

## Frozen 0067/0069 science and identities

0067 preregistration blob = `398e4a238229282582bbdbe4eed944d779c51ab3`.

Frozen semantics remain unchanged: BTC/SOL outcomes with BTC/ETH/SOL context; price-only DOWN/SIDEWAYS event construction; ANY_DOWN, MAJOR_DOWN, ANY_SIDEWAYS, LONG_SIDEWAYS targets; 1/3/5/10/20-session warning leads; 185 raw cells + 17 family scores; 8,080 atlas hypotheses; P01-P08 architectures and grids; 1,632 validation tuning configs; 64 final predictor tracks; 8 controllers; validation 2023, final event prediction 2024-01-01..2025-11-15, economic evaluation 2024-01-01..2026-08-02; 20-session refit cadence; t close may affect only t+1 return; no leverage/short/smoothing; 10 bps turnover cost; MBB L60 with 4,000 predictive + 4,000 economic replicates, seed 660066; PBO 8 slices / 70 splits where supported.

Frozen historical identities:
- Market evidence blob `64ebf5c6deaf3f34dbeac715378f196ff0f4fafe`, payload SHA256 `d1cd28bc76f2cd8ee0486287fc50b49e5451355a3e75132a2de5b30c15af3193`.
- 0062 feature engine blob `cac8e946998c836d10842b9388e1e3ef345a8c0b`.
- 0047 market loader blob `059b55961e279dab41ba29b5b017de0922e4f33c`.
- BRRK equity blob `82c87f8cb0ff01c728ffd3b717fff17cf5a364f2`.
- BRRK weights blob `2f6c8d3a8c25d3cafeaa0128f1c425dac248370b`.
- DTB3 blob `71d50e26f8a9afb6bcb88401d20b97d5fb0a891a`, payload SHA256 `4d8aee67dbd528ce38ff8482e9bb02dd5ccf2c6cd461f606fe90007151ab6879`.
- 0064 cash engine blob `4060a307be2204c11952cb52e2fc718a5343d8e1`.
- Network fetch, data replacement and post-result substitution are forbidden.
- History is researcher-exposed DEVELOPMENT history, not independent OOS.

0068 canonical graph builder blob = `56e910f787d96d572c570661359fc7005529925f`. Validation estimator fits are structurally 31,008; economic fit work and P08 NNLS are manifest-derived from realized frozen eligibility; every manifest unit receives exactly one terminal trace; inference remains blocked until exact accounting completes.

## 0069 immutable terminal result

Research ID = `BRRK-BTC-SOL-PATH-EVENT-EARLY-WARNING-EXECUTION-ASSURED-0069`.
State = `PASS_EVENT_EARLY_WARNING_ONLY / CLOSED TO SAME-ID RERUN`.

Lifecycle anchors:
- owner-first registry `dfd3f0a95e7245a4103637aaca1745bf3b2c8e03`;
- DESIGN `51d734bc510aed4ff5ba7c5eb9fbac686ddc2e13`;
- PREREGISTRATION `f9d1d95ec87ac9e86e2ed25a1340be3c725737f8`;
- IMPLEMENTATION `bd3952a47af80ee49dd2d99e501f23631be3ba67`, qualified head `c11101d8c454d71e918bed163fbd188934910670`;
- QUALIFICATION EVIDENCE `90e0aff461538d14cdf037bc57583ef6ac2b31ae`;
- qualification result blob `6a652faf66db4ef96edae4e3857e285816ca61da`;
- CONTROLLED-EXECUTION BOUNDARY `1665bda502cff9ac962b176ef0ed817a725f3134`;
- zero-result preflight workflow `31949044088` = PASS;
- unique historical workflow `31949133425`, job `95169748781` = PASS;
- immutable historical result bundle `911b68225310ec7621e9937ff698e7dff84f9ae8`.

Attempt 1/1 completed exactly once. `RUN_ATTEMPT.marker` preceded all historical reads. Persisted classification = `PASS_EVENT_EARLY_WARNING_ONLY`.

Predictive evidence: 8,080 atlas hypotheses, 149 Holm rejections, 64 final predictor tracks, 32 bootstrap-valid tracks, 4,000-replicate simultaneous predictive bootstrap, MBB L60, q95 `0.2668322318425197`. Winners are exactly P02, P03 and P08 for `SOL|T4_LONG_SIDEWAYS`.

Controller/economic evidence: 8 controllers, 0 winners; all persisted `COMPONENT_UNAVAILABLE` after frozen-path `KeyError ('BTC', 'T1_ANY_DOWN', 5)`; economic q95 null; PBO `NOT_EVALUATED`.

Execution assurance: `execution_valid=true`; validation 31,008/31,008; manifest-derived economic fits 5,808/5,808; P08 NNLS 20/20; manifest units and terminal traces 11,944/11,944; historical reads market/equity/weights/DTB3 1/1/1/1; loader calls 1; scientific-engine calls 1; network fetches 0. Same-ID rerun, retune, rescue and recomputation are forbidden. Production/signature/order authority remains zero.

## 0070 immutable terminal result

Research ID = `BRRK-SOL-LONG-SIDEWAYS-EARLY-WARNING-EPISODE-ROBUSTNESS-0070`.
State = `PASS_LOCKED_EPISODE_ROBUSTNESS_REPLICATION / CLOSED TO SAME-ID RERUN`.

Lifecycle anchors:
- owner-first registry commit `28be2794f8471e400fe70196460eed744cce694c`;
- DESIGN merge `828e90fa4b48ecb2ddc297d3b798e918601af2e9`;
- PREREGISTRATION merge `b00dd5e50401fd0b35c57d962d0625fa5790792f`;
- IMPLEMENTATION merge `378c0a0098d9a508c20a0e0bb891a503e2357f2e`;
- qualification evidence merge `709903bf5443cbb3b1fbd9d2c588db94b5566c6a`;
- qualification result blob `8ad8cc764407f954da7c82e06ad5fa0cb3b97ca1`;
- CONTROLLED BOUNDARY merge `0c5a6affc2243a0fdaf621f7801e1870657f1254`;
- exact merged-boundary zero-result preflight = PASS;
- unique controlled workflow `32040286477` = PASS;
- finalized scientific result branch head before governance-only documentation `a62ffbe3557530beb6aae24c94975ac1f1041fe3`;
- immutable result bundle merge `174a30dc4950e7351f3a746edc8f581b8f12e6d3`;
- immutable closeout merge `d87607070cf03ccbbc318065f8c4c14ec6c6a50b`;
- immutable closeout file `research/brrk_sol_long_sideways_early_warning_episode_robustness_0070/CLOSEOUT.md`.

Attempt 1/1 completed exactly once. `RUN_ATTEMPT.marker` was durably persisted before controlled source reads and `RUN_ONCE.marker` seals the attempt. Same-ID rerun, retune, rescue and recomputation are forbidden.

Frozen primary signal:
- `P02_RAW_ELASTIC_NET_LOGIT|SOL|T4_LONG_SIDEWAYS`;
- warning lead exactly 10 sessions;
- frozen 0069 PR-AUC `0.7974030713822858`, prevalence `0.45544554455445546`, PR-AUC lift `0.34195752682783037`, ROC-AUC `0.7913043478260869`;
- exactly seven final unique onsets.

Persisted scientific result:
- classification `PASS_LOCKED_EPISODE_ROBUSTNESS_REPLICATION`;
- `execution_valid=true`;
- exact full-window reproduction PASS at absolute tolerance `1e-12`;
- exactly `7/7` preregistered onset folds defined;
- P02 positive PR-AUC lift and ROC-AUC >0.50 in every fold;
- P02 median PR-lift retention `0.9823275624`;
- P02 retention >=0.50 in `7/7` folds;
- P03/P08 remain one dependent corroborative cluster and the frozen corroborative-cluster gate PASSes.

Execution assurance:
- controlled source reads: 0069 PRIMARY_RESULT `1`, 0069 EVIDENCE `1`, MARKET_EVIDENCE `1`;
- market loader calls `1`;
- frozen prediction reconstruction calls `1`;
- validation tuning calls `0`;
- model reselection calls `0`;
- LOEO retraining calls `0`;
- network fetches `0`;
- marker-only finalization controlled-source rereads `0`.

Evidence scope: researcher-exposed DEVELOPMENT-history episode robustness only; not independent OOS; no controller/economic inference. Production/signature/order authority remains zero.

## Governed multi-strategy research program

Roadmap merge = `169d9adf6531dc099a43541df413fef079322adf`.
Roadmap = `research/governance/CRYPTO_MULTI_STRATEGY_RESEARCH_PROGRAM_0071_0082.md`.

The merged roadmap serializes prospective IDs 0071–0082 and requires every eligible ID to independently traverse the same ten formal lifecycle stages used by 0069/0070. It defines point-in-time and anti-lookahead rules, ordered economic accounting, realistic/stressed cost treatment, trial counting, DSR/PBO/bootstrap requirements where applicable, concentration/capacity/stress tests, explicit stop/gating rules, and zero production authority.

The roadmap does not relax any per-ID lifecycle or evidence gate. Governance amendment PR #350 merged at `5b8153476aa63eb0c30d870a73e3bf14b4239ac8` and prospectively supersedes only the 0073 launch prerequisite after immutable 0072 closeout; it does not change or reinterpret 0072 science and grants no 0073 lifecycle credit by itself.

## 0071 controller integration

Research ID = `BRRK-SOL-LONG-SIDEWAYS-CONTROLLER-INTEGRATION-0071`.
State = `OWNER-FIRST + DESIGN + PREREGISTRATION + IMPLEMENTATION + NONHISTORICAL QUALIFICATION + CONTROLLED BOUNDARY MERGED / ZERO-RESULT PREFLIGHT BLOCKED_PRE_ATTEMPT_CONTROLLED_CONTENT_CONTAMINATION / CONTROLLED ATTEMPT 0/1`.

Lifecycle anchors:
- roadmap merge `169d9adf6531dc099a43541df413fef079322adf`;
- OWNER-FIRST merge `4b8762f8046000c1bd414fb60b9232917251e579`;
- DESIGN merge `0f86341d40516e0ed90d09baaa17e149c64671f6`;
- PREREGISTRATION merge `34ccffa6ecedffb5076b88cf86222c2fb142560c`;
- IMPLEMENTATION merge `cf203236348de692d8d92f30aedf35db7d2fe0c2`;
- NONHISTORICAL QUALIFICATION merge `693ddde4898ef923e3f55b09b138d9354d8da4c9`;
- qualification result blob `9a782797b32430e36fd20316f5aa3030fa04e72d`;
- CONTROLLED BOUNDARY merge `0cad34af6ea5919f974a593b3a0f9427a5c1c5fd`;
- governance incident Issue #295;
- governance resolution PR #296 merge `b58960ee3bc9e5cc5976d889cc28026614525686`.

Frozen preregistration fixes before any controlled read:
- common causal support and minimum 252 rows;
- exact six controller formulas and two nonselectable matched controls;
- t-close information first applies to t->t+1 return;
- C0/C1/C2 one-way turnover costs = 0/10/30 bps;
- frozen 0064 cash rule and exact cash/DTB3 identities;
- turnover, NAV, CAGR/vol/Sharpe/Sortino/MDD/Calmar/tail/exposure/cost/concentration formulas;
- 20-session synchronized MBB, 4,000 reps, seed 710071;
- DSR with exactly six trials and 0.95 gate;
- PBO CSCV 8 slices/70 splits as diagnostic only where supported;
- cost break-even, best-month concentration stress and matched-overlay attribution gates;
- exact candidate G0-G10 gates, Pareto tie-break and terminal classification meanings;
- controlled read/call budgets, create-only result chain and one-attempt rules.

Implementation encodes only the frozen contract in `engine.py`, `qualification.py` and `IMPLEMENTATION_CONTRACT.json`. NONHISTORICAL QUALIFICATION = PASS: all 13 preregistered classification regimes and mechanical checks passed with controlled historical/evidence reads `0`, market/DTB3 reads `0`, network fetches `0` and attempt consumed `0/1`.

CONTROLLED BOUNDARY is merged. During subsequent ZERO-RESULT PREFLIGHT, 0069 PRIMARY_RESULT content was opened before any durable 0071 `RUN_ATTEMPT.marker`. Stage 7 therefore cannot be declared PASS. No retroactive marker is permitted, no additional 0071 controlled payload may be read, no Stage 8 execution may occur under 0071, and no 0071 RESULT/CLOSEOUT stage may be fabricated. Attempt remains `0/1` unconsumed. Production/signature/order authority remains zero.

Governance resolution PR #296 permanently keeps 0071 blocked at 6/10, forbids same-ID continuation or retroactive marker creation, and authorizes a new full-lifecycle replacement ID `BRRK-SOL-LONG-SIDEWAYS-CONTROLLER-INTEGRATION-REPLACEMENT-0083`. No formal 0071 lifecycle stage transfers to 0083.

## 0083 replacement controller integration

Research ID = `BRRK-SOL-LONG-SIDEWAYS-CONTROLLER-INTEGRATION-REPLACEMENT-0083`.
State = `10/10 COMPLETE / FAIL_NO_ROBUST_LOCKED_P02_ECONOMIC_CONTROLLER_VALUE / CLOSED TO SAME-ID RERUN / CONTROLLED ATTEMPT 1/1`.

Lifecycle anchors:
- governance resolution merge `b58960ee3bc9e5cc5976d889cc28026614525686`;
- guarded registry writer merge `be519797af338a2529910e27dfcd8f908f9cd8a3`;
- full-history writer repair merge `4d7ac96fc5b6f19e35405afa9d42633d33058738`;
- OWNER-FIRST merge `dd9f3f28aabfdf6c05dcb9ca5a3dd13ca36a2467`;
- DESIGN merge `440b474a1908a4ec4196efa635d8154409a3c3de`;
- PREREGISTRATION merge `7e8a4e1d296dc9cb095f6b4ba66ab604d2723ff2`;
- IMPLEMENTATION merge `87bbed308fc54496b74d7d12c17c7cb15845f231`;
- NONHISTORICAL QUALIFICATION merge `b61ca07338a7eda7eaed459fda89272f4e22fdc1`;
- qualification result blob `89b38689524ff44cc54cb71da0573043c30bfa7e`;
- CONTROLLED BOUNDARY merge `7a98d39ce5e686731f0528ae0adb7816fed30a67`;
- exact merged-boundary ZERO-RESULT PREFLIGHT = `PREFLIGHT_PASS_ZERO_RESULT_GIT_IDENTITY_ONLY`;
- unique controlled workflow `32113475556`, job `95637765942` = SUCCESS;
- durable attempt marker commit `049cd7cc92c76832c487a66a1f2a20752d6a8934`;
- immutable result bundle commit `b4fe7f97892bb710ac4ff3ce91704ff25170999d`;
- finalized scientific result branch head before governance-only documentation `1c3d2d8796eed226aee2f6bcc9abcf067cd75ead`;
- RESULT merge `867544e097de129355d336adbb52662b30a5f1c7`;
- IMMUTABLE CLOSEOUT merge `f4abfcabe68fa09f27900aac59228420f8721403`;
- immutable closeout file `research/brrk_sol_long_sideways_controller_integration_replacement_0083/CLOSEOUT.md`;
- PRIMARY_RESULT blob `173b738d30bd26a21a9a0041037fa53d1de33156`, payload SHA256 `1540060a0e768ce4154b4ffd06904f7362e4c73ebc34e70b183b05acafa074b1`;
- EVIDENCE blob `898ed00b90953bc1fc39721b588a9fafe2b67fb7`, payload SHA256 `6fe0b86aba6dd5b673b3c21a464accdd76ab798285a050b1a8b7d4aa02eab270`;
- EXECUTION blob `0d2758ae0c5384bab19eb8215864adbf0659950a`, payload SHA256 `6758cded3bd60ba71f13378a06e80f09003798e68bae11722855d15873ac365c`;
- RUN_ONCE blob `e3a20ed54e93aa9452a69772acd2a277bb1dbd11`.

The unique Stage 8 attempt was consumed exactly once after a strict identity-only preflight PASS and durable remote attempt marker. Same-ID rerun, retune, rescue and recomputation are permanently forbidden.

Persisted scientific classification = `FAIL_NO_ROBUST_LOCKED_P02_ECONOMIC_CONTROLLER_VALUE`. `execution_valid=true`; common support = 685 rows; full-window locked P02 reproduction PASSed at absolute tolerance `1e-12`. Candidate accounting is exact: six selectable candidates, two matched controls and one benchmark. Passing candidates = `0/6`; representative candidate = `null`; every selectable candidate has DSR `0.0` and cost break-even `0.0` bps. Under the frozen attribution and robustness gates, the locked warning does not establish robust controller economic value.

Execution assurance: controlled reads 0069 PRIMARY_RESULT/EVIDENCE, MARKET_EVIDENCE, DTB3 = `1/1/1/1`; 0070 result content = `0`; market loader / frozen P02 reconstruction / cash engine calls = `1/1/1`; validation tuning/model reselection/P02 retraining = `0/0/0`; network fetches = `0`; finalization controlled-source rereads = `0`. Evidence tier remains `RESEARCHER_EXPOSED_DEVELOPMENT_NOT_INDEPENDENT_OOS`. Production/signature/order authority remains zero.

The immutable closeout records the FAIL without rescue or reinterpretation. Governance resolution #296 sets the post-resolution 0072 hard prerequisite to `0083_IMMUTABLE_CLOSEOUT`; it does not require 0083 PASS. That prerequisite is now satisfied by closeout merge `f4abfcabe68fa09f27900aac59228420f8721403`.

## 0072 carry atlas

Research ID = `BRRK-CRYPTO-CARRY-ATLAS-0072`.
State = `10/10 COMPLETE / INCONCLUSIVE_INSUFFICIENT_SUPPORT / CLOSED TO SAME-ID RERUN / CONTROLLED ATTEMPT 1/1 CONSUMED / CONTROLLED READS 6 / SCIENTIFIC ENGINE 1/1 / SOURCE NETWORK FETCHES 0`.

Lifecycle anchors:
- roadmap merge `169d9adf6531dc099a43541df413fef079322adf`;
- post-resolution prerequisite 0083 immutable closeout `f4abfcabe68fa09f27900aac59228420f8721403`;
- OWNER-FIRST merge `e1d61eadb8a4564cae2689a718e2eaaa859aa05e`;
- DESIGN merge `90a7b68718c5cb59002fe4b451d39d8979602161`;
- Stage 3 source-identity precondition merge `318adfe656ba1dfe4028ac3df388a96796e5ce60`;
- Stage 3 first metadata-only capture boundary merge `d8c9f3a262dadf1721103499f00fe9dcff4561ca`;
- documentation synchronization merge `f2912b86a5c3bcaf15580ebf7f210287ea741635`;
- Stage 3 offline first-capture wiring merge `d353fc89b92e75343a0b5e8228f27f9c50d8b4e4`;
- Stage 3 guarded execution-job contract merge `a2fb6612c8ec7e556585aafb9f759fa49834cfbb`;
- Stage 3 byte-preserving workflow patch-helper merge `25f6ec3d77055429c82a28c8631ff25b843592de`;
- Stage 3 first-capture workflow-wiring merge `884a21cb3b5d4e4342fa84efdf53e9a1250bef03`;
- Stage 3 execution-request merge / capture trigger `a5a71825756180f2f9eb079d7e8c3f17e1470e98`;
- first-capture workflow run `32194081362`, capture job `95894400892`;
- durable raw/failure artifact id `9345233553`, fixed artifact name `0072-first-capture-raw-BRRK-CRYPTO-CARRY-ATLAS-0072-CAPTURE-0001`;
- Stage 3 failed-capture reconciliation merge `6c9bc1e540d6ab7d497cc996fa8b1da4c4310066`;
- Stage 3 source-access requalification plan merge `a38dc764b5d075403c0827cacafc14a6a0d4230a`;
- Stage 3 access-probe execution-request merge `82163c1eaf51b25b09cf2c0119c60ba9e515668e`;
- Stage 3 access-probe workflow merge `cb1fafce46b3b17b9450ed58211408846530b272`;
- Stage 3 access-probe guard repair #327 merge `c17ed7b404456b0121c842eaed98a629c0929127`;
- Stage 3 runner-side request-id gate repair #328 merge `1e2dd25ee9de8ca19a4fbf31b482ba4076ad5d`;
- Stage 3 observable fail-closed gate repair #329 merge `c2e57537fe66f050e6aae4b70e343e37c197fa9d`;
- Stage 3 one-shot merge-trigger amendment #330 merge `788c59e1def18bd9cf9b38f8b832a326d8249f72`;
- Stage 3 source-identity amendment #332 merge `55b673f24155b4fe801e8adfdbb2f797b6f0ed0f`;
- Stage 3 CAPTURE-0002 request/object-plan #333 merge `2e86901d9fe49cb7a2f4944914caaee13e0c6b77`;
- Stage 3 CAPTURE-0002 implementation/execution-boundary #334 merge `be7aaf4640869d27a7efec974efa45d072ec9a7b`; boundary authorizes no network execution and earns no lifecycle credit.
- Stage 3 CAPTURE-0002 zero-artifact preflight evidence #336 merge `e095eca33f5dd4280b0f47e8acaf83e2d067c628`; preflight PASS records execution-claim/raw/support artifacts absent, result files absent, source-network requests 0, scientific payload reads 0, Stage-8 attempt 0 and controlled reads 0.
- Stage 3 CAPTURE-0002 one-shot execution request/trigger #337 merge `06ac1682b8a6de08ac75d53f0463f46727d60605`; unique workflow run `32428715027` attempt 1 = SUCCESS; durable execution-claim/raw/support artifacts `9428322109` / `9428326636` / `9428327167`; BTC/ETH/SOL x five frozen archive families = 15/15 support PASS; CAPTURE-0002 is permanently claimed and automatic refetch/second fetch is forbidden.
- Stage 3 CAPTURE-0002 success-evidence #339 merge `ad7d76af3fbfe489d9cf74f9de371db70ab1d8c7`; metadata/support evidence is canonical on main, no raw payload was added or read, no lifecycle credit was claimed.
- Stage 3 preregistration support-boundary prep #340 merge `d9eec67f490ce1aad0e34b6e2d2f8de27193420f`; it freezes only already-governed support facts, insufficient-family/no-substitution constraints, and earned no lifecycle credit.
- Stage 3 full preregistration #341 merge `8008b7450d7cc9d48667b832260fa2fb571e59b1`; preregistration blob `c1ba293d9623d8342b3611382fd26cbba269f048`; Stage 3 is formally complete at 3/10 with controlled reads 0 and Stage-8 attempt 0/1.
- Stage 4 implementation #342 merge `94a76ecb505a72314caaa00d39ad36faeb896b5f`; implementation encodes only the frozen preregistration in `engine.py`, synthetic-only `qualification.py`, `test_engine.py`, and `IMPLEMENTATION_CONTRACT.json`; Stage 4 is formally complete at 4/10 with controlled reads 0 and Stage-8 attempt 0/1.
- Stage 5 nonhistorical qualification #343 merge `46c43e9b628dd19eed3a5402360de4bb1ce0d8d6`; synthetic-only evidence blob `6275596a5db8c7d56e94db7b39394b95193a263b` records qualification PASS with controlled scientific-history reads 0, raw artifact reads 0, network fetches 0 and Stage-8 attempt consumed 0; Stage 5 is formally complete at 5/10.
- Stage 6 controlled-execution boundary #344 merge `62ea0971c8b8d47fde28f27c6b672d9cf5a61dcf`; boundary blob `cc43b63f63de0452d96078a29aeb3358b2d29515`; result-schema blob `b9e82e1f7cc1d14ad4d940d8793783df5e31fa68`; exact six scientific raw-object identities/read budgets, one raw-artifact download maximum, zero network/refetch, durable marker-before-read and create-only result persistence are frozen; Stage 6 is formally complete at 6/10 with controlled reads 0 and Stage-8 attempt 0/1.
- Stage 7 zero-result preflight evidence #345 merge `8736100e0d617d22b0580cfc1cdf5d52b330f4e8`; exact PR head `08f26f4493d192e4c043658231fc7fc6cb37dc01`; Stage 7 is formally complete at 7/10 with raw artifact downloads 0, controlled scientific-history reads 0, source-network fetches 0 and Stage-8 attempt 0/1.
- Stage 8 result branch `research/0072-result-v1`; durable `RUN_ATTEMPT.marker` preceded the first raw artifact download and controlled content read; raw artifact `9428326636` downloaded exactly once; exactly six authorized scientific objects read once each; source-network fetches 0; frozen scientific engine calls 1/1; create-only chain `RUN_ATTEMPT.marker` → `PRIMARY_RESULT.json` → `EVIDENCE.json` → `EXECUTION.json` → `RUN_ONCE.marker` is complete and sealed at head `bc35a226486efecdeb160f9c899d89b269651cde` before governance-only handoff updates.
- Stage 8 immutable result bundle merge `947475dc058c6204f20e1d26f719a1fea845876a`.
- Stage 8 persisted classification = `INCONCLUSIVE_INSUFFICIENT_SUPPORT`; execution valid; BTC/ETH/SOL state rows = 21/21/21, total 63; extreme-carry rows = 0; nonextreme rows = 63; crash-positive rows = 0; support sufficient = false; H06 is undefined. Same-ID attempt budget is consumed 1/1 and rerun/retune/rescue/recompute are permanently forbidden.
- Stage 9 RESULT PR #348 merge `1ce5bc4faffa1539cc56687f1c79f982efc1efe9`; Stage 9 is formally complete at 9/10 and performed governance-only interpretation with zero controlled-source rereads and zero recomputation.
- Stage 10 immutable CLOSEOUT PR #349 merge `e7571fd592c1a8074d487f27f8dbe9af6e33927f`; 0072 is formally complete at 10/10 with terminal state `INCONCLUSIVE_INSUFFICIENT_SUPPORT / CLOSED TO SAME-ID RERUN`.
- Prospective 0073 prerequisite governance PR #350 merge `5b8153476aa63eb0c30d870a73e3bf14b4239ac8` authorizes 0073 Stage 1 OWNER-FIRST under a prospective dependency amendment while preserving 0072 exactly as INCONCLUSIVE, not PASS.
- CAPTURE-0002 zero-existing-artifact diagnostic PR #335 was closed without merge after successful metadata-only preflight.
- CAPTURE-0002 zero-existing-artifact preflight workflow run `32422100836`, job `96596129550`: SUCCESS while checking out exact merged boundary main `be7aaf4640869d27a7efec974efa45d072ec9a7b`; contract validation = `CAPTURE_0002_CONTRACT_VALID_NO_NETWORK`; fixed raw/support artifact metadata rows = `0/0`; repository-wide nonexpired CAPTURE-0002 artifact count = `0`; repository CAPTURE-0002 result-file count = `0`; `scientific_payload_reads=0`; `source_network_requests=0`; `stage8_attempt_consumed=0`; `controlled_scientific_history_reads_to_researcher=0`.
- forward preflight evidence file `research/brrk_crypto_carry_atlas_0072/CAPTURE_0002_ZERO_ARTIFACT_PREFLIGHT_EVIDENCE.json` records only the above metadata/preflight facts and grants no lifecycle or execution authority.
- bounded access-probe dispatch run `32245507502`: contract validation PASS; execution job SKIPPED before any network probe; no artifact produced.
- bounded access-probe dispatch run `32245682524`: contract validation PASS; execution job SKIPPED before any network probe; no artifact produced.
- bounded access-probe dispatch run `32291738138`: exact main `c17ed7b404456b0121c842eaed98a629c0929127`; contract validation PASS; execution job still SKIPPED before any network probe; no artifact produced.
- unique one-shot access-probe push run `32412002636`, job `96564322145`: SUCCESS on exact main `788c59e1def18bd9cf9b38f8b832a326d8249f72`; artifact `9422472181` / `0072-access-probe-32412002636-1`; artifact ZIP SHA256 `b9f922ed17a855fe8f2a5292f3f198413ef6f0e190dba2f50ad7e2ab77e75576`; evidence payload SHA256 `9deda918c35f3a2a91a415ba0be8c703d2071f0844cb6c5d8cc6480840a45021`.
- frozen technical evidence: `data.binance.vision` checksum-object HEAD = HTTP 200 (`TECHNICALLY_REACHABLE_UNDER_FROZEN_PROBE`); `api.bybit.com` headers-only instrument-metadata request = HTTP 403 (`NOT_TECHNICALLY_USABLE_UNDER_FROZEN_PROBE`). Technical reachability is not source admission, PIT proof or scientific support.
- merged source-identity amendment fixes the next-capture boundary: no new source or family substitution; Binance archive only under already-enumerated archive families with exact object identities frozen before fetch; Binance fapi and Bybit API are ineligible under the current execution environment unless separately prospectively requalified.
- merged `CAPTURE-0002` request/plan freezes support month `2026-07`, cutoff `2026-08-20T20:33:00Z`, exactly BTC/ETH/SOL, exactly five already-enumerated `data.binance.vision` archive families, 15 ZIP objects plus 15 paired `.CHECKSUM` objects, zero retries and zero redirects. `premiumIndexKlines` is raw support only and is not perpetual funding.
- merged #334 implementation hardens CAPTURE-0002 before any fetch: canonical source-contract field is `contract_id`; frozen 2026-07 Binance SPOT archive timestamps are interpreted as microseconds while frozen USD-M archive-family timestamps are interpreted as milliseconds; unexpected unit ranges fail closed. The boundary keeps `network_execution_authorized_by_this_boundary=false` and `execution_trigger_in_this_boundary=false`.

`CAPTURE-0001` is sealed failed and permanently non-retriable after HTTP 451 on its first frozen request. No source payload object was persisted and no retry is legal.

The successful access probe read no scientific payload. Stage 7 read only identity/metadata. Stage 8 then consumed the unique authorized controlled attempt exactly once under the frozen marker-before-read boundary. Evidence tier remains DEVELOPMENT history and is not independent OOS. CAPTURE-0002 remains permanently claimed and no-refetch.

## Exact next step

0074 remains immutable `10/10 COMPLETE / INVALID_EXECUTION / CLOSED TO SAME-ID RERUN`. Governance resolution #381 merged at `f50618f233aef5e8e9872695ab87b67ab294a3a4`; 0075 is permanently stopped at `7/10 BLOCKED_PRE_ATTEMPT_FROZEN_IMPLEMENTATION_INCOMPLETE`, attempt `0/1` unconsumed, reads `0`, engine `0/1`, Stage8 network `0`, values exposed `false`, no marker/result, and #379 is closed unmerged. Guarded 0084 OWNER-FIRST writer tooling merged at `896e307b83e5fa96553286b7752042b0e418cb22`; replacement 0084 Stage1 OWNER-FIRST merged at `a0b4c6b4943850e29ad5392d33be7ab1fb86c65d`; Stage2 DESIGN merged at `075d8b5b7de97836350314d517ad483d5de67219`; Stage3 PREREGISTRATION merged at `046e34b020a4f628967fb942947b06ca30c7289c`; Stage4 IMPLEMENTATION merged at `3574c33a199580637efa74b230564c7eb23d5725`; Stage5 NONHISTORICAL QUALIFICATION merged at `61b7e3a45c82604520ea9f76c6878a2707481fc2`; Stage6 CONTROLLED-EXECUTION BOUNDARY merged at `3e22ee336f82e14a8eea63d1d9afb07085699d07`; Stage7 ZERO-RESULT PREFLIGHT merged at `641ccf6bcd358c0255f65546bfcde1c06e861b51` with `PREFLIGHT_PASS_ZERO_RESULT`; Stage8 authorization gate merged at `d449475350a38df75c3a08bffc626beeff0ebc9d`; Stage8 controlled-attempt incident is merged at `eab63e048b051e96a03426ddc095f5c2a07d6a9f`; Stage9 RESULT is merged at `7775079deb51b6e6a522ee83e9c171a9c0adf998`; Stage10 CLOSEOUT merged at `4304456742c5bccea10433457e10fa3bb0e0af1e`. 0084 is immutable `10/10 COMPLETE / INVALID_EXECUTION / CLOSED TO SAME-ID RERUN`, reason `POST_MARKER_FROZEN_EXECUTION_INTERFACE_INCOMPLETE`; attempt `1/1` permanently consumed; controlled scientific-history reads `0`; scientific engine `0/1`; Stage8 scientific source-network fetches `0`; scientific values exposed `false`; no admissible scientific result bundle and no `RUN_ONCE.marker`. Prospective 0076 routing amendment #395 is merged at `5d773d9546e32b784381093ce5324001f7282e29`. 0076 Stage1 OWNER-FIRST merged at `4f9f4b3bf009af2b8affc41f29835c099b7fda70`; Stage2 DESIGN merged at `3d2a91558a1829314541f66304a5c463b164ef1c`; Stage3 PREREGISTRATION merged at `c0c587929af9fa71fab8ddb8a69d58ef03f36101`; Stage4 IMPLEMENTATION merged at `ffab381d8a47536835d461cc72f30ca14af04bb7`; Stage5 NONHISTORICAL QUALIFICATION merged at `0e453df9a1148919333a85d695bacfc9b35dbd39`; Stage6 CONTROLLED-EXECUTION BOUNDARY merged at `868187bae8f5e23dcf884b023c0783d19c96ed18`. Stage7 ZERO-RESULT PREFLIGHT on PR #404 / `research/0076-stage7-zero-result-preflight-v1` is `FAIL_CLOSED_PRE_MARKER_PAYLOAD_ENTRY_READ_BOUNDARY_VIOLATION`; formal completion remains 6/10; inherited validated factors 0; attempt 0/1 unconsumed; controlled authorized payload-file traversals 30336 occurred pre-marker; scientific engine 0/1; scientific source-network fetches 0; inner CSV rows parsed false; scientific row values exposed false; no Stage8 marker/result exists; same-ID Stage8/rerun/retune/rescue/recompute prohibited; zero production/signature/order authority.

## No-drift authority

production gross cap = 1.0
production_authorized_components = []
production_authorized = false
signature_authorized = false
order_submission_authorized = false
Canonical BRRK-0011 = NO CHANGE.
0064 = NO CHANGE.
0065 = NO CHANGE.
0066 = NO CHANGE.
0067 = NO CHANGE.
0068 = NO CHANGE.
0069 = NO CHANGE.
0070 = CLOSED / NO SAME-ID ACTION.
0071 = CONTROLLED BOUNDARY MERGED / ZERO-RESULT PREFLIGHT BLOCKED_PRE_ATTEMPT_CONTROLLED_CONTENT_CONTAMINATION / ATTEMPT 0/1.
0083 = 10/10 COMPLETE / `FAIL_NO_ROBUST_LOCKED_P02_ECONOMIC_CONTROLLER_VALUE` / CLOSED TO SAME-ID RERUN / ATTEMPT 1/1.
0072 = 10/10 COMPLETE / `INCONCLUSIVE_INSUFFICIENT_SUPPORT` / CLOSED TO SAME-ID RERUN / ATTEMPT 1/1 CONSUMED / CONTROLLED READS 6 / ENGINE 1/1 / SOURCE NETWORK FETCHES 0 / NO SAME-ID RERUN-RETUNE-RESCUE-RECOMPUTE.
0073 = 10/10 COMPLETE / `INCONCLUSIVE_INSUFFICIENT_SUPPORT` / CLOSED TO SAME-ID RERUN / ATTEMPT 1/1 CONSUMED / CONTROLLED READS 0 / SCIENTIFIC ENGINE 1/1 / SOURCE NETWORK FETCHES 0 / NO SAME-ID RERUN-RETUNE-RESCUE-RECOMPUTE / PRODUCTION-SIGNATURE-ORDER AUTHORITY FALSE.
0074 = 10/10 COMPLETE / `INVALID_EXECUTION` / CLOSED TO SAME-ID RERUN / STAGE-10 IMMUTABLE CLOSEOUT MERGED AT `92a1f24f5d5c439920f3cf7b3256343ee1c53f4c` / CONTROLLED ATTEMPT 1/1 CONSUMED / ACTUAL CONTROLLED READS 402 / SCIENTIFIC ENGINE 1/1 CONSUMED INADMISSIBLE NON-FROZEN HARNESS / SCIENTIFIC SOURCE NETWORK FETCHES 0 / SCIENTIFIC VALUES EXPOSED TRUE / NO ADMISSIBLE STRATEGY-PERFORMANCE RESULT / RUN_ONCE SEALED WITH INCIDENT SUPPLEMENT / NO SAME-ID RERUN-RETUNE-RESCUE-RECOMPUTE / PRODUCTION-SIGNATURE-ORDER AUTHORITY FALSE.
0075 = STAGE-1 THROUGH STAGE-7 MERGED / STAGE-7 MERGE `3af2a58cb7ff12be37f918f2c45f44369bd0900d` / `PREFLIGHT_PASS_ZERO_RESULT` / GOVERNANCE RESOLUTION #381 MERGED AT `f50618f233aef5e8e9872695ab87b67ab294a3a4` / PERMANENT `BLOCKED_PRE_ATTEMPT_FROZEN_IMPLEMENTATION_INCOMPLETE` AT 7/10 / STAGE-8 #379 CLOSED UNMERGED / ATTEMPT 0/1 UNCONSUMED / READS 0 / ENGINE 0/1 / NETWORK 0 / VALUES EXPOSED FALSE / NO MARKER / NO SCIENTIFIC RESULT / NO SAME-ID CONTINUATION / PRODUCTION-SIGNATURE-ORDER AUTHORITY FALSE.
0084 = 10/10 COMPLETE / `INVALID_EXECUTION / POST_MARKER_FROZEN_EXECUTION_INTERFACE_INCOMPLETE` / CLOSED TO SAME-ID RERUN / STAGE10 IMMUTABLE CLOSEOUT MERGED AT `4304456742c5bccea10433457e10fa3bb0e0af1e` / GOVERNANCE REPLACEMENT AUTHORITY `f50618f233aef5e8e9872695ab87b67ab294a3a4` / ATTEMPT 1/1 CONSUMED / CONTROLLED READS 0 / SCIENTIFIC ENGINE 0/1 / SCIENTIFIC SOURCE NETWORK FETCHES 0 / SCIENTIFIC VALUES EXPOSED FALSE / NO ADMISSIBLE SCIENTIFIC RESULT / NO RUN_ONCE.marker / NO SECOND MARKER-RERUN-RETUNE-RESCUE-RECOMPUTE / 0076 PASS PREREQUISITE UNSATISFIED / PRODUCTION-SIGNATURE-ORDER AUTHORITY FALSE.
0076 = STAGE-1 THROUGH STAGE-6 MERGED / STAGE6 MERGE `868187bae8f5e23dcf884b023c0783d19c96ed18` / STAGE7 `FAIL_CLOSED_PRE_MARKER_PAYLOAD_ENTRY_READ_BOUNDARY_VIOLATION` ON PR #404 / FORMAL COMPLETION REMAINS 6/10 / ATTEMPT 0/1 UNCONSUMED / CONTROLLED AUTHORIZED PAYLOAD-FILE TRAVERSALS 30336 PRE-MARKER / SCIENTIFIC ENGINE 0/1 / SCIENTIFIC SOURCE NETWORK FETCHES 0 / INNER CSV ROWS PARSED FALSE / SCIENTIFIC ROW VALUES EXPOSED FALSE / NO STAGE8 MARKER OR RESULT / NO SAME-ID STAGE8-RERUN-RETUNE-RESCUE-RECOMPUTE / PRODUCTION-SIGNATURE-ORDER AUTHORITY FALSE.
Phase 6 = NO CHANGE.

## Phase 6 live observation closeout — 2026-08-25

- Frozen Phase-6 live-observation thresholds were checked against live GitHub Actions evidence without replay/backfill: elapsed `15` days, `16` genuine schedule-origin decisions, and `1` separately evidenced zero-authority emergency drill.
- Every credited schedule decision is attempt-1 schedule-origin and has an already-persisted create-only evidence artifact plus separate hash-bound receipt; missing expected dates `[]`, duplicate decision timestamps `[]`.
- Observed critical reconciliation errors `0`, unexplained target drift `0`, schedule failures `0`; production/signature/order authority remains false.
- Emergency drill run `32822137245` is `workflow_dispatch`-origin and is not scheduled-decision credit.
- Closeout audit workflow run `32822011836`; audit artifact id `9553575209`, digest `sha256:2482e5f575b544ccc3168776d70b5ce0dfc3baef24dcf4de9fb7cb5caaf77096`.
- Persisted closeout inventory: `research/governance/PHASE6_OBSERVATION_CLOSEOUT_2026-08-25.json`. Repository recording creates no evidence or credit and does not alter the frozen Phase-6 contract.
- Phase 6 R1 evidence closeout = `PASS_FROZEN_LIVE_OBSERVATION_GATES`; this grants no production authority and does not authorize any paused/invalid historical research ID.
- 0076 remains sealed at Stage7 pre-marker read-boundary incident with no replacement, retroactive marker, same-ID Stage8, rerun, retune, rescue or recompute. 0072/0073 Carry remain paused; 0083 remains immutable FAIL.
- Next legal frontier: R2 public `CONTROLLED_RESEARCH_RUNNER_V1`, then prospective lifecycle-gate compression amendment only after runner qualification.

## R2 controlled research runner — 2026-08-25

- R1 Phase 6 evidence closeout is merged on main at `bac4b105e7576f8a00227c759b5cabdaaead7d9f` with `PASS_FROZEN_LIVE_OBSERVATION_GATES`; this grants no production authority.
- R2 PR #407 introduces prospective public `CONTROLLED_RESEARCH_RUNNER_V1`; it does not authorize or consume any scientific attempt.
- The runner enforces metadata-only pre-marker inspection, durable `RUN_ATTEMPT.marker` before payload reads, one verified physical payload-read pass, exactly one scientific engine invocation, create-only result persistence and `RUN_ONCE.marker` sealing.
- Pre-marker `ZipFile.testzip()`, payload `read/open`, decompression, extraction and CRC payload traversal are prohibited.
- Synthetic qualification covers corrupted ZIP/CRC, missing file, wrong hash, duplicate object, stale head, existing result, marker push failure, crash after marker, duplicate read, double engine invocation, NaN, missing timestamp, schema drift, writer failure, network attempt, wrong source manifest and wrong execution interface.
- Qualification also requires at least `20` consecutive synthetic full lifecycles with zero unexpected failure.
- Exact-head `Research governance core` on runner head `cbadff165afc78ae938e11da1f3e1f02bcfe22e3` passed; `PR handoff governance` failed only because this CURRENT_STATE handoff had not yet changed in PR #407. Final qualification remains pending a new exact-head terminal-green CI after this handoff.
- 0076 remains sealed at Stage7 pre-marker read-boundary incident; no replacement, retroactive marker, same-ID Stage8, rerun, retune, rescue or recompute. 0072/0073 Carry remain paused; 0083 remains immutable FAIL.
- No Trend, Factor or Options controlled scientific attempt may start until R2 runner qualification is durably PASS and the prospective R3 lifecycle amendment is separately merged.
- Production/signature/order/withdrawal/transfer authority remains false.

## R3 prospective five-gate lifecycle — 2026-08-25

- R2 `CONTROLLED_RESEARCH_RUNNER_V1` merged at `cfceb7f7eace6b3c08f3ec7cafb6cc09199163df` after exact-head terminal-green qualification; the runner remains prospective research infrastructure with zero production authority.
- R3 proposes `PROSPECTIVE_FIVE_GATE_LIFECYCLE_V1` for newly registered research IDs that explicitly adopt it after the amendment merges.
- The ten logical checkpoints remain unchanged and are grouped into five merge gates: `SPEC_FREEZE` = OWNER-FIRST + DESIGN + PREREGISTRATION; `BUILD` = IMPLEMENTATION + NONHISTORICAL QUALIFICATION; `ARM` = CONTROLLED BOUNDARY + ZERO-RESULT PREFLIGHT; `RUN` = UNIQUE CONTROLLED ATTEMPT; `SEAL` = RESULT + IMMUTABLE CLOSEOUT.
- The amendment cannot change, reopen, reinterpret, rescue, rerun, retune, recompute, or transfer lifecycle credit for any preexisting research ID.
- Future independent research tracks may run in parallel only when no declared scientific dependency exists. Factor L/S still requires qualifying factor evidence; portfolio studies still require their preregistered sleeve prerequisites.
- Every future controlled `RUN` gate must use a currently qualified common runner, preserve durable marker-before-read and exactly-once engine execution, and stop new science if the common runner causes a new `INVALID_EXECUTION`.
- 0076 remains sealed at 6/10 after its Stage7 pre-marker boundary incident; 0072/0073 Carry remain closed/paused; 0083 remains immutable FAIL; no historical authority changes.
- R3 is governance-only and grants no production/signature/order/withdrawal/transfer authority.
- Next legal frontier after R3 merge: register the first new Trend research under `SPEC_FREEZE`; Factor Atlas and Options/VRP may proceed independently under separate new IDs after their own SPEC_FREEZE gates.

## 0085 Trend SPEC_FREEZE — 2026-08-25

- Research ID `BRRK-MULTI-HORIZON-TREND-VOL-TARGET-0085` is the first new research ID explicitly adopting merged `PROSPECTIVE_FIVE_GATE_LIFECYCLE_V1`.
- `SPEC_FREEZE` contains OWNER-FIRST + DESIGN + PREREGISTRATION in preserved logical order; no controlled scientific payload value was read and attempt remains `0/1`.
- Exactly one candidate is frozen: BTC/ETH/SOL long/cash, 3-of-4 positive trailing log-return signs over 20/60/120/240 sessions, inverse 20-session realized-vol allocation, portfolio vol target 25% annualized, gross cap 1.0, daily decisions, t-close first affects t→t+1.
- One-way turnover cost panels are frozen at 10/20/30 bps. Primary economic gates include 10bps Sharpe >=0.80, Calmar >=1.00, MDD magnitude <=35%, 20bps Sharpe >=0.65, 30bps CAGR >0, >=3/4 positive chronological blocks, and frozen benchmark wealth/drawdown gates.
- Evidence tier is `RESEARCHER_EXPOSED_DEVELOPMENT_NOT_INDEPENDENT_OOS`; PASS can only qualify later forward validation/multi-sleeve consideration.
- 0074 remains immutable `INVALID_EXECUTION`; 0085 receives no lifecycle/result/attempt credit from it.
- Next 0085 gate after SPEC_FREEZE merge is `BUILD`: implementation + nonhistorical qualification only, with controlled payload reads 0 and attempt 0/1.
- Production/signature/order/withdrawal/transfer authority remains false.

## 0085 Trend RUN interface repair handoff — 2026-08-25

- `SPEC_FREEZE`, `BUILD`, and `ARM` are already merged on main for `BRRK-MULTI-HORIZON-TREND-VOL-TARGET-0085`.
- PR #414 is a mechanical pre-attempt RUN-interface repair only. It does not create `RUN_ATTEMPT.marker`, read controlled historical payloads, invoke the scientific engine, expose scientific values, or consume attempt 1/1.
- The user has explicitly authorized `0085 Trend RUN controlled attempt 1/1`; that authorization applies only after this repair merges and the frozen common runner confirms the exact merged ARM/RUN contract.
- Attempt state at this handoff: `0/1` unconsumed; controlled reads `0`; scientific engine calls `0/1`; scientific values exposed `false`; production/signature/order/withdrawal/transfer authority remains false.
- Exact next legal action after #414 terminal-green merge: execute the single authorized RUN through `CONTROLLED_RESEARCH_RUNNER_V1`, with durable marker-before-read and create-only result sealing. No manual marker fabrication or alternate execution path is permitted.

## R2.1 common-runner superset-container compatibility repair — 2026-08-25

- Live 0085 pre-attempt inspection found its frozen artifact is the 0074 Stage6 shared `stage/` artifact containing 402 payload objects, while the 0085 ARM filter authorizes exactly 201 perpetual-1d-kline objects.
- `CONTROLLED_RESEARCH_RUNNER_V1` previously required archive membership to equal the filtered manifest exactly, which would preflight-reject the frozen shared artifact before marker creation. No 0085 attempt, controlled read, engine invocation or scientific-value exposure occurred.
- This prospective infrastructure-only repair permits a frozen archive to be a superset container: metadata preflight requires every manifest member and validates only its declared central-directory size; unmanifested members are ignored and never opened. Post-marker reads remain exactly the manifest entries, each at most once, with unchanged SHA-256 verification and exactly-one engine invocation.
- The repair changes no 0085 universe, date range, signal, cost, threshold, benchmark, source identity or 201-object read budget. It changes no historical result or authority and grants no new attempt.
- The common runner must re-pass the complete existing synthetic fault matrix, the 20-consecutive full-lifecycle qualification, and the new superset-container test on the exact final PR head before 0085 RUN may execute.
- 0085 user authorization for controlled attempt 1/1 remains valid but unconsumed. Production/signature/order/withdrawal/transfer authority remains false.

## R2.2 durable Git create-only store qualification — 2026-08-25

- PR #416 prospectively qualifies `GitCreateOnlyStoreV1` as the durable Git-backed `CreateOnlyStore` backend for `CONTROLLED_RESEARCH_RUNNER_V1`; it maps governed keys to dedicated remote branches, rejects existing keys, never force-pushes, and remotely fetches/byte-verifies every successful write.
- Qualification uses only synthetic bytes and temporary local bare Git repositories. It creates no 0085 marker/result/RUN_ONCE object and reads no controlled historical payload.
- 0085 remains ARM-complete with the user's explicit RUN attempt 1/1 authorization valid and unconsumed. Attempt remains 0/1; controlled reads remain 0; scientific engine remains 0/1; scientific values exposed remain false.
- Frozen Trend science, ARM-bound 201-object manifest, parent artifact identity, immutable historical anchors, and production/signature/order/withdrawal/transfer authority remain unchanged.
- Exact next legal action after #416 terminal-green merge is the already-authorized single 0085 RUN through the requalified common runner using this durable backend.

## 0085 Trend unique controlled RUN orchestration — 2026-08-25

- Worker B rebased the RUN orchestration onto merged PR #416 and removed its duplicate store implementation. The RUN path now reuses the qualified `GitCreateOnlyStoreV1` backend from main.
- The unique orchestrator rebuilds the frozen 201-object SourceManifest from the ARM-bound parent manifest, verifies parent SHA-256/filter/read budgets, requires the frozen `ControlledArchiveTrendEngine`, and delegates marker-before-read, exactly-once engine, create-only result and RUN_ONCE ordering to `CONTROLLED_RESEARCH_RUNNER_V1`.
- The science workflow is scoped only to `research/0085-trend-run-v1` plus the exact `RUN_TRIGGER.json`. It verifies artifact id/name/size/digest before downloading the outer artifact container; no payload member is opened before the common runner persists and remotely verifies the attempt marker.
- `research/governance/no_drift.py` adds only the exact workflow path `.github/workflows/0085-unique-controlled-run.yml`; no broad workflow prefix or research-path exemption is introduced.
- The earlier workflow-definition failures occurred before GitHub created any job. They consumed no attempt, created no marker, downloaded no controlled artifact, performed no controlled read, and invoked no scientific engine.
- 0085 remains attempt `0/1`, controlled reads `0`, scientific engine `0/1`, scientific values exposed `false`. The user authorization for controlled RUN attempt 1/1 remains valid and unconsumed.
- Frozen science, source identity, 201-object read budget, immutable historical states, and production/signature/order/withdrawal/transfer authority remain unchanged.

## 0085 terminal seal and R2 source-interface requalification — 2026-08-25

- 0085 Trend completed its single authorized controlled RUN attempt `1/1` and is permanently sealed `INVALID_EXECUTION / CLOSED TO SAME-ID RERUN`.
- Durable `RUN_ATTEMPT.marker` preceded all controlled reads. The run consumed exactly `201` controlled reads and exactly `1/1` scientific engine invocation; source-network fetches remained `0`.
- The persisted terminal failure is `INVALID_EXECUTION:ENGINE_OR_RUNTIME_FAILURE:TrendExecutionError`, rooted in the runner exposing artifact member keys as `payloads/...` while the frozen 0085 adapter expected `stage/payloads/...`. No PASS/FAIL/INCONCLUSIVE scientific result is admissible.
- Durable result and `RUN_ONCE.marker` exist. 0085 cannot rerun, retune, rescue, recompute, substitute sources, reinterpret the terminal result, or receive same-ID continuation.
- PR #419 merged the immutable 0085 seal. PR #420 prospectively requalified the common execution interface with metadata-only source-key validation, the exact 0085 namespace regression, and 20 consecutive synthetic full lifecycles.
- Future controlled science remains forbidden from using the old callable-only runner path. PR #421 adds the prospective 0086+ guard requiring `ControlledResearchRunnerV1SourceQualified` for future numeric controlled RUN scripts.
- 0076 remains sealed at its Stage7 pre-marker boundary incident; 0072/0073 Carry remain paused/closed; 0083 remains immutable FAIL; all historical attempts/captures remain unchanged.
- `workflow run                         31381953131 / attempt 1`, CAPTURE-0001 sealed/no-retry, CAPTURE-0002 permanently claimed/no-refetch, and Phase6 closeout remain immutable.
- Production/signature/order/withdrawal/transfer authority remains false.

## 0086 independent cross-sectional Factor Atlas

Research ID = `BRRK-CROSS-SECTIONAL-FACTOR-ATLAS-0086`.
State = `SPEC_FREEZE_PROPOSED / CONTROLLED ATTEMPT 0/1 / CONTROLLED READS 0`.

0086 is independent from 0075/0076/0084/0085 and inherits zero lifecycle credit, attempt credit, factor-selection credit, or scientific result. The central owner record was durably committed before the governed 0086 research path was introduced.

Frozen SPEC tests exactly three predeclared factor representatives: momentum `MOM60_RAW`, volatility `RVOL20_RAW`, and liquidity `LIQ30_RAW`. Size/market-cap and carry/funding are excluded because no qualifying point-in-time source identity was frozen before SPEC_FREEZE. The exact multiplicity family is three tests with Holm FWER 0.05. Universe construction, Monday UTC-close decision timing, FWD5 outcome, raw rank transforms, MBB inference, support minima, 10/20 bps economic diagnostics, terminal rules, trial budget, and stop rules are frozen before any controlled value exposure.

Any future 0086 controlled RUN must use `ControlledResearchRunnerV1SourceQualified`, requires a separate irreversible user authorization, and permits at most one attempt. Pre-marker payload traversal/decompression/CRC remains forbidden. Factor L/S remains forbidden unless 0086 returns a valid PASS, and only passing factor families may become eligible for a separately governed future ID.

0085 remains immutable `INVALID_EXECUTION` with attempt 1/1 consumed and no admissible Trend result. 0076 remains sealed; 0072/0073 remain paused; 0083 remains immutable FAIL; Phase6 PASS closeout remains unchanged. Production/signature/order/withdrawal/transfer authority remains zero.

## 0086 Factor Atlas BUILD — 2026-08-25

- `BRRK-CROSS-SECTIONAL-FACTOR-ATLAS-0086` SPEC_FREEZE is merged. BUILD implements exactly the frozen three-factor family `MOM60_RAW`, `RVOL20_RAW`, `LIQ30_RAW` with no controlled historical reads.
- BUILD freezes the exact PIT top-30 liquidity universe, Monday UTC-close/FWD5 timing, BTC state rule (`BTC_UP` iff BTCUSDT MOM60_RAW > 0), average-rank Spearman IC, tercile spread/turnover accounting, 10/20 bps costs, 8-week/10,000-replicate MBB seed 860086, exact three-test Holm correction, support minima, G0-G9 gates and terminal classifier.
- The source-qualified adapter validates filenames metadata-only before marker and accepts both known staging `stage/payloads/...` and GitHub artifact `payloads/...` namespaces while rejecting duplicate logical `(symbol, month)` objects. Inner ZIP/CSV parsing is post-marker execution only.
- Synthetic qualification covers factor formulas, both namespaces, duplicate/unknown keys, ZIP normalization, Holm, insufficient support, an adequate-support full synthetic Atlas and the source-qualified interface. Synthetic classifications carry zero scientific evidence.
- 0086 controlled attempt remains `0/1`; controlled reads remain `0`; scientific engine remains `0/1`. Factor L/S remains blocked pending a valid 0086 PASS.
- Next legal gate is ARM. ARM may bind exact artifact/object identities, declared hashes/sizes, source keys, schema/read budget/result-marker paths and engine-call budget using metadata only. Pre-marker decompression, `testzip()`, CRC traversal and payload parsing remain forbidden.
- 0085 remains immutable `INVALID_EXECUTION` with attempt 1/1 consumed and no admissible Trend result. 0076 remains sealed; 0072/0073 remain paused; 0083 remains immutable FAIL; Phase6 PASS closeout remains unchanged.
- No production/signature/order/withdrawal/transfer authority is granted.

## 0086 Factor Atlas ARM — 2026-08-25

- `BRRK-CROSS-SECTIONAL-FACTOR-ATLAS-0086` SPEC_FREEZE and BUILD are merged; ARM binds controlled identities only and opens no scientific payload value.
- ARM binds GitHub Actions run `32646565505`, artifact `9495175701` / `0075-stage6-authorized-payloads-v1`, size `174445627`, SHA-256 `8040282ff412b2d3fd360173e4745ebfd048796eb9e9c2ad49fa0901e5cedf56`.
- The immutable 0075 parent manifest SHA-256 remains `2f70384dd84a601b69528ef3d770e0fa9c714b3e0888bec009e93b5067ecebf8`; immutable 0076 zero-result submanifest SHA-256 remains `c33b575cc436db795086458a25ca38fe1527f649809e549caba00e9754422e58`.
- 0086 authorizes exactly the `15254` `USD_M_MONTHLY_1D_PERPETUAL_KLINE` identities from that submanifest and excludes all funding objects. Source substitution/refetch/renaming after ARM is forbidden.
- Future RUN must use `ControlledResearchRunnerV1SourceQualified` with `CrossSectionalFactorAtlas0086Engine`; pre-marker `testzip()`, payload open/read, decompression, inner-ZIP/CSV parsing and CRC payload traversal remain forbidden.
- Controlled attempt remains `0/1`; controlled reads remain `0`; scientific engine remains `0/1`; scientific values exposed remain `false`. No `RUN_ATTEMPT.marker` exists.
- A separate explicit irreversible user authorization is required before 0086 RUN attempt 1/1. Factor L/S remains blocked unless 0086 returns a valid PASS.
- 0085 remains immutable `INVALID_EXECUTION` attempt 1/1 consumed with no admissible Trend result. 0076 remains sealed; 0072/0073 remain paused; 0083 remains immutable FAIL; Phase6 PASS closeout remains unchanged.
- `workflow run                         31381953131 / attempt 1`, CAPTURE-0001 sealed/no-retry and CAPTURE-0002 permanently claimed/no-refetch remain immutable.
- Production/signature/order/withdrawal/transfer authority remains false.


## 0087 independent Options / VRP SPEC_FREEZE

Research ID = `BRRK-OPTIONS-VOLATILITY-RISK-PREMIUM-0087`.
State = `SPEC_FREEZE_PROPOSED / CONTROLLED ATTEMPT 0/1 / CONTROLLED READS 0`.

Owner-first registry commit `3686aec8a5a82d3a146828e464da090f0aea9a70` predates the governed 0087 path. 0087 freezes one independent Deribit BTC/ETH ATM 30D VRP family, Monday 08:00 UTC timing, nearest 25-35 DTE same-strike ATM call/put selection, source-IV VRP30 definition, daily delta-hedged short-straddle economics, C1/C2 cost panels, support minima, HAC/MBB inference and PASS/FAIL/INCONCLUSIVE/INVALID rules. No controlled scientific value has been exposed.

BUILD may use synthetic/nonhistorical fixtures only. ARM must bind qualifying point-in-time Deribit options, index and hedge identities using metadata only; inability to bind them stops 0087 before RUN without source substitution or scientific rescue. Any RUN requires separate irreversible user authorization and `ControlledResearchRunnerV1SourceQualified`.

0086 remains ARM-complete at attempt 0/1 pending separate authorization. 0085 remains immutable INVALID_EXECUTION attempt 1/1 consumed. 0076 remains sealed; 0072/0073 remain paused; 0083 remains immutable FAIL. `workflow run                         31381953131 / attempt 1`, CAPTURE-0001 sealed/no-retry and CAPTURE-0002 permanently claimed/no-refetch remain immutable. Production/signature/order/withdrawal/transfer authority remains false.
## 0087 Options / VRP BUILD — 2026-08-25

- `BRRK-OPTIONS-VOLATILITY-RISK-PREMIUM-0087` SPEC_FREEZE is merged. BUILD implements the frozen single BTC/ETH Deribit ATM 30D VRP candidate using synthetic/nonhistorical fixtures only; no controlled historical value was opened.
- BUILD freezes same-strike ATM selection, source-IV `ATM_IVAR30`, exact 30-return `RV30`, distinct-week support counting, HAC lag 8, 8-week/4,000-replicate MBB seed 870087, G1-G8 adjudication, and executable-side daily delta-hedged short-straddle economics with C1 5 bps / C2 15 bps hedge friction.
- Synthetic qualification covers selection/spread rejection, IVAR/RV30, weekly support, pure hedge accounting, stress-cost monotonicity, valid INCONCLUSIVE, adequate-support PASS/FAIL and duplicate-identity fail-closed behavior. Synthetic outcomes carry zero scientific evidence.
- 0087 controlled attempt remains `0/1`; controlled reads remain `0`; scientific engine remains `0/1`; scientific values remain unexposed. Next legal gate is ARM metadata/schema binding only.
- ARM must bind qualifying point-in-time Deribit option/index/hedge identities, executable bid/ask, source IV, source-native deltas, timestamps, hashes/sizes, source keys, read budget and `ControlledResearchRunnerV1SourceQualified` without payload traversal. If it cannot, 0087 stops before RUN without source substitution or rescue.
- 0086 remains ARM-complete at attempt `0/1` pending separate irreversible RUN authorization. Factor L/S remains blocked unless 0086 returns a valid PASS.
- 0085 remains immutable `INVALID_EXECUTION` attempt 1/1 consumed; 0076 remains sealed; 0072/0073 remain paused; 0083 remains immutable FAIL; Phase6 PASS closeout remains unchanged.
- `workflow run                         31381953131 / attempt 1`, CAPTURE-0001 sealed/no-retry and CAPTURE-0002 permanently claimed/no-refetch remain immutable.
- Production/signature/order/withdrawal/transfer authority remains false.
