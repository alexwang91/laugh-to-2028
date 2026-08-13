import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("run0060", HERE / "run_once.py")
R = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(R)


def args(tmp):
    return SimpleNamespace(
        expected_head_sha="HEAD0060",
        market=str(tmp/"market.json"),
        attempt=str(tmp/"RUN_ATTEMPT.marker"),
        result=str(tmp/"PRIMARY_RESULT.json"),
        execution=str(tmp/"EXECUTION.json"),
        marker=str(tmp/"RUN_ONCE.marker"),
    )


def frozen_interface():
    return {
        "frozen_market_evidence":{"dataset_slice_id":"BRRK-LEADERSHIP-ROTATION-0048-EXPOSED-HIST-V1","payload_sha256":R.scientific_engine.EXPECTED_PAYLOAD_SHA256,"git_blob_sha":"m"},
        "scientific_engine":{"git_blob_sha":"e"},
        "source_loader":{"git_blob_sha":"s"}
    }


def schema():
    return json.loads((HERE/"RESULT_SCHEMA.json").read_text())


def measurement(n=10):
    sc=schema(); targets=sc["target_keys"]
    rows=[]
    for i in range(n):
        row={k:0.1+i*0.001 for k in sc["origin_panel_fields"] if k not in ("origin_date","chronological_block_id")}
        row["origin_date"]=f"2020-01-{i+1:02d}"
        row["chronological_block_id"]=1 if i<3 else 2 if i<6 else 3 if i<8 else 4
        rows.append(row)
    rho={k:0.1 for k in targets}; lcb={k:0.01 for k in targets}
    return {
      "research_id":R.scientific_engine.RESEARCH_ID,
      "classification":R.scientific_engine.CLASS_SUPPORT,
      "gates":{"G0":True,"G1":False,"G2":False,"G3":False,"G4":False},
      "shared_origin_count":n,"shared_origin_start":rows[0]["origin_date"],"shared_origin_end":rows[-1]["origin_date"],
      "full_sample_rho_by_target":rho,
      "temporal_block_rho_by_target":{str(i):rho for i in range(1,5)},
      "temporal_positive_all_eight_blocks":4,
      "bootstrap_q95":0.09,"simultaneous_lcb_by_target":lcb,
      "axis_target_spearman":{"A1":rho,"A2":rho,"A3":rho},
      "axis_redundancy_matrix":[[1,0,0],[0,1,0],[0,0,1]],"axis_eigenvalues":[1,1,1],"axis_effective_rank":3.0,
      "terminal_positive_rate_by_horizon":{"20":0.5,"60":0.5,"120":0.5,"240":0.5},
      "actual_variants_evaluated":1,"data_budget":"DEVELOPMENT","independent_oos":False,
      "production_authorized":False,"signature_authorized":False,"order_submission_authorized":False,"origin_panel":rows
    }


def patch_static(monkeypatch, tmp):
    (tmp/"market.json").write_text(json.dumps({"payload_sha256":R.scientific_engine.EXPECTED_PAYLOAD_SHA256,"payload":{}}))
    monkeypatch.setattr(R,"verify_static",lambda expected,market:("HEAD0060",frozen_interface(),schema()))
    monkeypatch.setattr(R,"git",lambda *a:"blob")


def test_preflight_does_not_read_market(monkeypatch,tmp_path):
    a=args(tmp_path); patch_static(monkeypatch,tmp_path)
    monkeypatch.setattr(R,"load_json",lambda p: (_ for _ in ()).throw(AssertionError("content read")) if Path(p)==Path(a.market) else json.loads(Path(p).read_text()))
    R.preflight(a)
    assert not Path(a.attempt).exists()


def test_attempt_is_create_only(monkeypatch,tmp_path):
    a=args(tmp_path); patch_static(monkeypatch,tmp_path)
    R.start_attempt(a)
    assert Path(a.attempt).exists()
    with pytest.raises(R.ControlledRunError): R.start_attempt(a)


def test_evaluate_requires_attempt(monkeypatch,tmp_path):
    a=args(tmp_path); patch_static(monkeypatch,tmp_path)
    with pytest.raises(R.ControlledRunError): R.evaluate_after_attempt(a)


def test_exactly_one_loader_and_engine_call(monkeypatch,tmp_path):
    a=args(tmp_path); patch_static(monkeypatch,tmp_path); R.start_attempt(a)
    calls={"loader":0,"engine":0}
    def loader(e): calls["loader"]+=1; return {"BTC":"btc","ETH":"e","SOL":"s"}
    def engine(*x,**k): calls["engine"]+=1; return measurement()
    monkeypatch.setattr(R.source_engine,"frames_from_market_evidence",loader)
    monkeypatch.setattr(R.scientific_engine,"evaluate",engine)
    R.evaluate_after_attempt(a)
    assert calls=={"loader":1,"engine":1}
    assert Path(a.result).exists() and Path(a.execution).exists()
    with pytest.raises(R.ControlledRunError): R.evaluate_after_attempt(a)
    assert calls=={"loader":1,"engine":1}


def test_finalize_never_calls_loader_or_engine(monkeypatch,tmp_path):
    a=args(tmp_path); patch_static(monkeypatch,tmp_path); R.start_attempt(a)
    monkeypatch.setattr(R.source_engine,"frames_from_market_evidence",lambda e:{"BTC":"btc","ETH":"e","SOL":"s"})
    monkeypatch.setattr(R.scientific_engine,"evaluate",lambda *x,**k:measurement())
    R.evaluate_after_attempt(a)
    monkeypatch.setattr(R.source_engine,"frames_from_market_evidence",lambda e: (_ for _ in ()).throw(AssertionError("loader called")))
    monkeypatch.setattr(R.scientific_engine,"evaluate",lambda *x,**k: (_ for _ in ()).throw(AssertionError("engine called")))
    R.finalize(a)
    m=json.loads(Path(a.marker).read_text())
    assert m["market_content_read_during_finalize"] is False
    assert m["scientific_remeasurement_during_finalize"] is False


def test_tampered_result_blocks_finalize(monkeypatch,tmp_path):
    a=args(tmp_path); patch_static(monkeypatch,tmp_path); R.start_attempt(a)
    monkeypatch.setattr(R.source_engine,"frames_from_market_evidence",lambda e:{"BTC":"btc","ETH":"e","SOL":"s"})
    monkeypatch.setattr(R.scientific_engine,"evaluate",lambda *x,**k:measurement())
    R.evaluate_after_attempt(a)
    r=json.loads(Path(a.result).read_text()); r["bootstrap_q95"]=0.123; Path(a.result).write_text(json.dumps(r))
    with pytest.raises(R.ControlledRunError): R.finalize(a)


def test_result_schema_rejects_authority_or_wrong_classification():
    m=measurement(); m["production_authorized"]=True
    with pytest.raises(R.ControlledRunError): R.validate_result(m,schema())
    m=measurement(); m["classification"]=R.scientific_engine.CLASS_PASS
    with pytest.raises(R.ControlledRunError): R.validate_result(m,schema())


def test_runner_static_has_only_one_market_content_read_site():
    text=(HERE/"run_once.py").read_text()
    assert text.count("evidence = load_json(Path(args.market))") == 1
    assert "requests.get" not in text and "fetch_daily_frame" not in text
