from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
p = ROOT / "docs/CURRENT_STATE.md"
text = p.read_text(encoding="utf-8")
repl = {
    "Handoff PR: **#158**": "Handoff PR: **#159**",
    "Handoff branch: `research/brrk-exhaustion-trigger-0045-prereg`": "Handoff branch: `research/brrk-exhaustion-trigger-0045-runonce`",
    "Authoritative baseline main at branch creation: `23fd7a050cf8c543470fc48a2286cc75ff9fdafc`": "Authoritative baseline main at branch creation: `c48577bb95c9fc78e5d0d78b86f30905b3636503`",
    "Latest merged research PR at branch creation: **#157**": "Latest merged research PR at branch creation: **#158**",
    "BRRK exhaustion trigger 0045     PREREGISTERED / NOT RUN / NO GROSS AUTHORITY": "BRRK exhaustion trigger 0045     IMPLEMENTED / NOT RUN / CONTRACT VALIDATION PENDING",
}
for old,new in repl.items():
    if old not in text: raise SystemExit(f"missing anchor {old}")
    text = text.replace(old,new,1)
old_head = "## BRRK-EXHAUSTION-TRIGGER-0045 — preregistered, not run\n"
if old_head not in text: raise SystemExit("0045 heading missing")
text = text.replace(old_head, "## BRRK-EXHAUSTION-TRIGGER-0045 — implemented, still not run\n",1)
old_intro = "PR #158 freezes exactly one result-informed causal state machine before any 0045 result exists. It reuses immutable 0044 CORE4, uses S2 trend disagreement only as confirmation, and S3 price structure only for slow recovery confirmation. S5 volume/OBV is excluded because 0044 preserved negative evidence."
new_intro = "PR #158 froze exactly one result-informed causal state machine before any 0045 result existed. PR #159 now implements that frozen state machine, event/episode diagnostics, parent-result guards, run interface and permanent contract tests. No 0045 result has been executed or viewed; `PRIMARY_RESULT.json` and `RUN_ONCE.marker` do not exist. It reuses immutable 0044 CORE4, uses S2 trend disagreement only as confirmation, and S3 price structure only for slow recovery confirmation. S5 volume/OBV remains excluded."
if old_intro not in text: raise SystemExit("0045 intro missing")
text = text.replace(old_intro,new_intro,1)
if "## Current drift assessment\n" not in text: raise SystemExit("drift missing")
prefix = text.split("## Current drift assessment\n",1)[0]
tail = """## Current drift assessment

`DRIFT_0`.

PR #159 is pre-result governed trigger implementation only. No 0045 result, gross mapping, portfolio economics, canonical BRRK mathematics, Phase-6 observation, leverage/shorting or production/security authority changes occur.

## Exact next task

1. Keep PR #159 result-free until the frozen runner/interface/contract tests and final governance/no-drift/P3.2/Phase-6/handoff CI are green.
2. Only after that fully green pre-result baseline may one temporary one-shot workflow execute 0045 exactly once.
3. Preserve the first valid PASS or FAIL without threshold/persistence/state-machine rescue or rerun.
4. After a valid result, bind artifact/result hashes, create the permanent run-once marker, remove temporary workflows and rerun final CI.
5. Never map WATCH/RISK to portfolio gross under 0045. A dynamic-gross stage requires a new research ID and only becomes eligible after a full 0045 PASS. Phase 6 and all production/signing/order authority remain unchanged.
"""
text = prefix + tail
text = "\n".join(x.rstrip() for x in text.splitlines()) + "\n"
p.write_text(text, encoding="utf-8")
