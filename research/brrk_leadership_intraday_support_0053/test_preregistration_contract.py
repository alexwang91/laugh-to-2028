import hashlib,json
from pathlib import Path
import unittest
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]; SLICE="BRRK-LEADERSHIP-INTRADAY-SUPPORT-0053-BINANCE-4H-HIST-V1"
class Test0053Preregistration(unittest.TestCase):
 def test_frozen_prereg_unchanged(self):
  p=json.loads((HERE/"PREREGISTRATION.json").read_text()); self.assertEqual(p["objective_type"],"DATA_QUALITY"); self.assertEqual(p["actual_variants_evaluated"],0); self.assertEqual(p["development_dataset_refs"],[]); self.assertEqual(p["result_status"],"PREREGISTERED_DATA_NOT_CAPTURED")
 def test_capture_hash_and_registry(self):
  dec=json.loads((HERE/"DATASET_DECLARATION.json").read_text()); ev=json.loads((HERE/"MARKET_4H_EVIDENCE.json").read_text()); raw=(HERE/"MARKET_4H_PAYLOAD.json").read_bytes(); self.assertEqual(hashlib.sha256(raw).hexdigest(),dec["market_payload_sha256"]); self.assertEqual(dec["market_payload_sha256"],ev["raw_identity"]["sha256"]); self.assertFalse(dec["support_measurement_executed"]); self.assertFalse(dec["predictive_model_executed"]); reg=json.loads((ROOT/"config/dataset_exposure_registry.json").read_text()); self.assertEqual(len([x for x in reg["dataset_slices"] if x.get("dataset_slice_id")==SLICE]),1)
 def test_research_registry_capture_only(self):
  reg=json.loads((ROOT/"config/research_registry.json").read_text()); row=[x for x in reg["records"] if x.get("research_id")=="BRRK-LEADERSHIP-INTRADAY-SUPPORT-0053"][0]; self.assertEqual(row["development_dataset_refs"],[SLICE]); self.assertEqual(row["result_status"],"PREREGISTERED_DATA_CAPTURED_NOT_MEASURED"); self.assertEqual(row["actual_variants_evaluated"],0)
 def test_no_measurement_or_predictive_artifacts(self):
  for n in ["SUPPORT_RESULT.json","PRIMARY_RESULT.json","RESULT_SUMMARY.json","EXECUTION.json","RUN_ONCE.marker"]: self.assertFalse((HERE/n).exists(),n)
if __name__=="__main__": unittest.main()
