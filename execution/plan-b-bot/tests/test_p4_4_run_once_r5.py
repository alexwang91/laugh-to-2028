from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "research" / "leverage_0040"
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

MODULE = HERE / "run_leverage_0040_once_r5.py"
spec = importlib.util.spec_from_file_location("leverage_0040_r5", MODULE)
assert spec and spec.loader
r5 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = r5
spec.loader.exec_module(r5)


def test_r5_json_safe_preserves_native_boolean_types():
    out = r5._json_safe_r5(
        {
            "false": False,
            "true": True,
            "np_false": np.bool_(False),
            "np_true": np.bool_(True),
            "integer": 1,
        }
    )
    assert out["false"] is False
    assert out["true"] is True
    assert out["np_false"] is False
    assert out["np_true"] is True
    assert type(out["integer"]) is int
    encoded = json.loads(json.dumps(out))
    assert encoded["false"] is False
    assert encoded["true"] is True


def test_r5_record_is_post_compute_blinded_and_non_economic():
    data = json.loads(
        (HERE / "LEVERAGE-0040-POST-COMPUTE-CORRECTION-R5.json").read_text(
            encoding="utf-8"
        )
    )
    assert data["correction_id"] == "POST-COMPUTE-SERIALIZATION-VALIDATOR-006"
    assert data["observability"]["full_candidate_matrix_computed"] is True
    assert data["observability"]["candidate_metrics_emitted_to_stdout"] is False
    assert data["observability"]["candidate_metrics_committed"] is False
    assert data["correction"]["economic_logic_change"] is False
    assert data["correction"]["bootstrap_seed_changed"] is False
    assert data["correction"]["result_driven_retuning"] is False
