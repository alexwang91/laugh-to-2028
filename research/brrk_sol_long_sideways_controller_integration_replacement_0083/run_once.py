from __future__ import annotations

import argparse
import json
from pathlib import Path

from research.brrk_sol_long_sideways_controller_integration_0071 import run_once as base
from research.brrk_sol_long_sideways_controller_integration_replacement_0083 import engine
from research.brrk_sol_long_sideways_controller_integration_replacement_0083.preflight import run_preflight

RID = "BRRK-SOL-LONG-SIDEWAYS-CONTROLLER-INTEGRATION-REPLACEMENT-0083"
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
ATTEMPT = HERE / "RUN_ATTEMPT.marker"
RESULT = HERE / "PRIMARY_RESULT.json"
EVIDENCE = HERE / "EVIDENCE.json"
EXECUTION = HERE / "EXECUTION.json"
FINAL = HERE / "RUN_ONCE.marker"

# This replacement runner intentionally delegates the frozen numerical calculation
# to the already-qualified 0071 implementation while rebinding only replacement-ID
# paths/identities. It deliberately exposes no local-only start/run command: the
# durable attempt marker must be created and remotely verified on the unique 0083
# result branch before evaluate is allowed to touch controlled content.
PINNED_BLOBS = {
    "research/brrk_sol_long_sideways_controller_integration_replacement_0083/RUN_INTERFACE.json": "5bcfb659e4913c1547727ed9b53f2e308415a83a",
    "research/brrk_sol_long_sideways_controller_integration_replacement_0083/CONTROLLED_EXECUTION_BOUNDARY.json": "1c0414a7c090505489c021e41dc723d755934df1",
    "research/brrk_sol_long_sideways_controller_integration_replacement_0083/PREREGISTRATION.json": "0504d08376c4baa97f3e6519a4188c5aeb2e56b3",
    "research/brrk_sol_long_sideways_controller_integration_replacement_0083/ECONOMIC_ANALYSIS_CONTRACT.json": "17a41f09db1d00a565fa45f6e245ceacc2cdd043",
    "research/brrk_sol_long_sideways_controller_integration_replacement_0083/QUALIFICATION_PREREGISTRATION.json": "850dac44aae23c9ffd057a741d72ec07c1681d47",
    "research/brrk_sol_long_sideways_controller_integration_replacement_0083/RESULT_SCHEMA.json": "78f2f93db7626e995769e21450f33eef2bd9c404",
    "research/brrk_sol_long_sideways_controller_integration_replacement_0083/IMPLEMENTATION_CONTRACT.json": "2832ea35f5f26e5738ea6d1629a5a3d0122eff16",
    "research/brrk_sol_long_sideways_controller_integration_replacement_0083/engine.py": "3de386ff662e4175cad0b5dab84524894384f5bc",
    "research/brrk_sol_long_sideways_controller_integration_replacement_0083/QUALIFICATION_RESULT.json": "89b38689524ff44cc54cb71da0573043c30bfa7e",
    "research/brrk_btc_sol_path_event_early_warning_execution_assured_0069/PRIMARY_RESULT.json": "df00901c77d8d334d61c7c65a14b8d127e9ca8b6",
    "research/brrk_btc_sol_path_event_early_warning_execution_assured_0069/EVIDENCE.json": "6266e6a11205e21592766546342ca5bca1dd97f0",
    "research/brrk_sol_long_sideways_early_warning_episode_robustness_0070/PRIMARY_RESULT.json": "e5226963c6bebfae4341889da1b17025152eec51",
    "research/brrk_sol_long_sideways_early_warning_episode_robustness_0070/EVIDENCE.json": "47d5f2ac5704ae2f89773d8d0c29ccce9ee2da0c",
    "research/brrk_sol_long_sideways_early_warning_episode_robustness_0070/EXECUTION.json": "ff264f5ef1bf3d5096301f3e31a0f136c7e3b0f8",
    "research/brrk_btc_sol_path_event_early_warning_runtime_qualified_0067/engine.py": "482868d45ccdeaa5fbad8033f122a8fcfde79ca6",
    "research/brrk_btc_sol_path_event_early_warning_0066/engine.py": "79320c83d0ce89c2c952fd0a4f7a9b7452a8e0ae",
    "research/brrk_btc_sol_path_event_early_warning_0066/event_engine.py": "651ebb824b9dc1390ed0170a4eab07a3870786aa",
    "research/brrk_btc_sol_path_event_early_warning_0066/models.py": "6b255b887f2cd8f1741086a7bf27e6254288e836",
    "research/brrk_btc_risk_signal_atlas_0062/engine.py": "cac8e946998c836d10842b9388e1e3ef345a8c0b",
    "research/brrk_beta_handoff_0047/engine.py": "059b55961e279dab41ba29b5b017de0922e4f33c",
    "research/brrk_beta_handoff_0047/evidence/MARKET_EVIDENCE.json": "64ebf5c6deaf3f34dbeac715378f196ff0f4fafe",
    "research/brrk_idle_cash_passive_accrual_robustness_0064/engine.py": "4060a307be2204c11952cb52e2fc718a5343d8e1",
    "research/brrk_idle_cash_sweep_robustness_0063/DTB3_RAW.csv": "71d50e26f8a9afb6bcb88401d20b97d5fb0a891a",
}


def _configure_base() -> None:
    base.RID = RID
    base.HERE = HERE
    base.ATTEMPT = ATTEMPT
    base.RESULT = RESULT
    base.EVIDENCE = EVIDENCE
    base.EXECUTION = EXECUTION
    base.FINAL = FINAL
    base.engine = engine
    base.PINNED_BLOBS = dict(PINNED_BLOBS)


def evaluate(boundary_sha: str) -> dict:
    _configure_base()
    return base.evaluate(boundary_sha)


def finalize(boundary_sha: str) -> dict:
    _configure_base()
    return base.finalize(boundary_sha)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("preflight", "evaluate", "finalize"))
    parser.add_argument("--boundary-sha", required=True)
    args = parser.parse_args()
    if args.command == "preflight":
        out = run_preflight(args.boundary_sha)
    elif args.command == "evaluate":
        out = evaluate(args.boundary_sha)
    else:
        out = finalize(args.boundary_sha)
    print(json.dumps(out, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
