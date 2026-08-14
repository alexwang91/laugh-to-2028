from __future__ import annotations
import hashlib,json,subprocess
from pathlib import Path
RID='BRRK-IDLE-CASH-PASSIVE-ACCRUAL-ROBUSTNESS-0064'
BASE_SHA='38b5740cb89ae16b4bc005f3d5bcb4f8e0a0181f'
BASE_BLOB='843be78545f0fa890853897a4b9b4fd91b2741f7'
PREFIX='research/brrk_idle_cash_passive_accrual_robustness_0064/'
DESIGN='research/governance/BRRK_IDLE_CASH_PASSIVE_ACCRUAL_ROBUSTNESS_0064_DESIGN_FREEZE_2026-08-14.md'
REG=Path('config/research_registry.json'); OUT=Path('/tmp/0064-owner-artifact')
def canon(x): return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def h(x): return hashlib.sha256(canon(x)).hexdigest()
def owner():
 return {
 'research_id':RID,'research_family_id':'IDLE_CASH_CARRY','research_domain':'RISK_CONTROL','research_governance_version':1,'governance_mode':'PROGRAM_GOVERNED_V1','objective_type':'MECHANISM_TEST','created_at':'2026-08-14T01:15:00Z','created_before_result':True,
 'question':'Does passive continuously interest-bearing residual cash improve unchanged BRRK-0011 full-cycle net wealth/CAGR after frozen yield haircut and annual cash-account spread/fee stresses without worsening drawdown?',
 'hypothesis':'The frozen 50% DTB3-realization / 100-bps annual-fee primary cell will beat unchanged BRRK-0011 terminal wealth/CAGR, preserve MDD, recur temporally, pass dependence-aware LCB, and survive the frozen core 9-cell neighborhood.',
 'hypothesis_origin':'RESULT_INFORMED_DEVELOPMENT_NEW_ID_FROM_0063_ZERO_SWEEP_DIAGNOSTIC_NOT_INDEPENDENT_OOS',
 'economic_mechanism':'Residual cash already created by unchanged BRRK-0011 risk-asset trades remains continuously interest-bearing; no extra sweep trade is introduced. Costs are yield realization haircut plus continuous annual spread/fee on idle cash principal.',
 'primary_target':'FULL_CYCLE_NET_TERMINAL_WEALTH_AND_CALENDAR_SPAN_CAGR_VERSUS_UNCHANGED_BRRK_0011','primary_metric':'PRIMARY_50_PERCENT_DTB3_REALIZATION_100_BPS_ANNUAL_FEE_PAIRED_RELATIVE_LOG_GROWTH_WITH_G0_G6_GATES',
 'secondary_metrics':['max_drawdown','chronological_block_relative_log_growth','moving_block_bootstrap_lcb','stress_grid_relative_terminal_wealth'],'feature_families':['IDLE_CASH_FRACTION','FRED_DTB3_SHORT_RATE','CONTINUOUS_ANNUAL_CASH_FEE'],'horizon':'FULL_COMMITTED_BRRK0011_WINDOW','universe':['BTC','ETH','SOL','BNB','CASH'],
 'development_dataset_refs':['BRRK-WINNER-0001-CANONICAL-HIST-V1'],'validation_dataset_refs':[],'sealed_dataset_refs':[],'declared_variant_budget':20,'actual_variants_evaluated':0,'parameter_candidate_count':20,
 'stopping_rule':'Exactly one governed historical attempt after preregistration, implementation and boundary merges; all 20 frozen stress cells inside one engine call; no same-ID rerun/retune/rescue.',
 'success_criteria':'Primary passes G0-G5 and all 9 core stress cells pass G6.','failure_criteria':'Ordered preregistered failure taxonomy binds at first failed gate; identity/support failure is inconclusive, not economic failure.',
 'allowed_followup':'PASS may motivate NEW-ID future-only confirmation/integration; FAIL requires distinct NEW-ID mechanism.','forbidden_followup':'No same-ID grid/primary/fee formula/DTB3/baseline/gate change, favorable-cell selection, rerun, recomputation, retune or rescue after outcome access.',
 'researcher_decisions':'Passive-accrual mechanism, 4x5 stress grid, primary 50%/100bps and core 9-cell neighborhood were frozen at DESIGN before 0064 candidate economics.',
 'research_process_complexity':{'declared_parameter_candidates':20,'actual_parameter_candidates_evaluated':0,'universes_evaluated':1,'horizons_evaluated':1,'rebalance_variants':0,'feature_representations':3,'special_cases_introduced':1,'validation_exposure_event_refs':[],'related_family_trials':1},
 'lineage_edges':[],'result_status':'PREREGISTERED_NOT_RUN','failure_reason':None,'promotion_state':'NONE','evidence_refs':[],'decision_refs':[DESIGN,PREFIX+'PREREGISTRATION.json',PREFIX+'DATASET_DECLARATION.json','docs/CURRENT_STATE.md'],
 'production_relevance':'DEVELOPMENT passive-cash accrual robustness only; no canonical/Phase6/production/signer/order authority.','production_authorized':False,'provenance_status':'FACT','governed_path_prefixes':[PREFIX],
 'notes':['0063 zero-sweep cells are exposed DEVELOPMENT motivation only and cannot satisfy 0064 gates.','0064 changes no BRRK-0011 risk-asset signal, target, weight or gross path.','All 20 cells are reported; only prospectively frozen primary can promote.']}
def main():
 assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==BASE_SHA
 base=json.loads(REG.read_text()); assert not any(r.get('research_id')==RID for r in base['records'])
 before=[h(r) for r in base['records']]; clean=owner(); assert not {'evidence_scorecard','confidence_level','confidence_components','derived_confidence'}.intersection(clean)
 patched=json.loads(json.dumps(base)); patched['records'].append(clean); assert before==[h(r) for r in patched['records'][:-1]]
 OUT.mkdir(parents=True,exist_ok=True); REG.write_text(json.dumps(patched,indent=2,ensure_ascii=False,allow_nan=False)+'\n'); subprocess.run(['python','-m','research.governance.validate'],check=True)
 blob=subprocess.check_output(['git','hash-object',str(REG)],text=True).strip(); report={'research_id':RID,'base_commit_sha':BASE_SHA,'base_registry_blob_sha':BASE_BLOB,'base_record_count':len(base['records']),'output_record_count':len(patched['records']),'preexisting_records_unchanged':True,'new_owner_has_evidence_scorecard':False,'output_registry_git_blob_sha':blob,'result_status':'PREREGISTERED_NOT_RUN','promotion_state':'NONE','actual_variants_evaluated':0,'production_authorized':False}
 (OUT/'research_registry.json').write_bytes(REG.read_bytes()); (OUT/'OWNER.json').write_text(json.dumps(clean,indent=2,ensure_ascii=False)+'\n'); (OUT/'BUILD_REPORT.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n'); print(json.dumps(report,sort_keys=True))
if __name__=='__main__': main()
