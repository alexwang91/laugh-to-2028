from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]; RESULT=ROOT/"research"/"results"/"leverage_0040"; LEVERAGE=ROOT/"research"/"leverage_0040"; SUMMARY=RESULT/"summary.json"; DIGEST=RESULT/"summary.sha256"; CONTRACT=LEVERAGE/"LEVERAGE-0040-STUDY-IMPLEMENTATION-V1.json"; PREREG=LEVERAGE/"LEVERAGE-0040.json"; ADDENDUM=LEVERAGE/"LEVERAGE-0040-PRE-RUN-ADDENDUM-V1.json"; CAPS=("1.00","1.10","1.20","1.30")
def sha256(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    if not SUMMARY.exists() or not DIGEST.exists(): raise SystemExit("LEVERAGE-0040 immutable result files are missing")
    expected=DIGEST.read_text().strip(); actual=sha256(SUMMARY)
    if expected!=actual: raise SystemExit("summary digest mismatch")
    data=json.loads(SUMMARY.read_text());
    if data.get("study_id")!="LEVERAGE-0040" or data.get("status")!="ONE_TIME_PREREGISTERED_STUDY_COMPLETE": raise SystemExit("result identity/status mismatch")
    if data.get("production_authorized") is not False or data.get("constraints",{}).get("production_authorized_components")!=[] or data.get("constraints",{}).get("post_result_retuning_allowed") is not False: raise SystemExit("production/retuning boundary violated")
    matrix=data.get("candidate_matrix");
    if not isinstance(matrix,dict) or tuple(sorted(matrix))!=CAPS: raise SystemExit("candidate matrix mismatch")
    ev=data.get("input_evidence",{})
    if ev.get("implementation_contract_sha256")!=sha256(CONTRACT) or ev.get("preregistration_sha256")!=sha256(PREREG) or ev.get("pre_run_addendum_sha256")!=sha256(ADDENDUM): raise SystemExit("frozen input digest mismatch")
    for cap in CAPS:
        row=matrix[cap]
        if float(row.get("cap"))!=float(cap): raise SystemExit(f"cap mismatch {cap}")
        if set(row.get("price_only_metrics_by_cost_bps",{}))!={"5.0","10.0","20.0","50.0"}: raise SystemExit(f"cost grid mismatch {cap}")
        if cap!="1.00" and not {"final_research_pass","broad_region_pass"}.issubset(row.get("gate",{})): raise SystemExit(f"gate bookkeeping missing {cap}")
    selection=data.get("selection",{}); status=selection.get("status")
    if status not in {"NO_PROMOTION","RESEARCH_PROMOTION_CANDIDATE_NOT_PRODUCTION_AUTHORIZED"} or selection.get("production_authorized") is not False: raise SystemExit("selection status invalid")
    if status=="NO_PROMOTION" and selection.get("selected_research_cap") is not None: raise SystemExit("NO_PROMOTION selected cap")
    if status!="NO_PROMOTION":
        selected=f"{float(selection['selected_research_cap']):.2f}"
        if selected not in {"1.10","1.20","1.30"} or matrix[selected]["gate"].get("final_research_pass") is not True: raise SystemExit("selected cap failed frozen gate")
    print(f"LEVERAGE-0040 immutable result validation PASS sha256={actual}")
if __name__=="__main__": main()
