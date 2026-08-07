from runner_support_b_0041 import *

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--router-artifact-dir", required=True)
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args()

    inputs = _preflight(Path(args.router_artifact_dir))
    if args.preflight_only:
        print("LEVERAGE-0041 preflight-only PASS; no cap>1 candidate economics evaluated.")
        print(f"price_frame_sha256={_dataframe_sha256(inputs['prices'])}")
        print(f"router_vwap_slippage_sha256={inputs['capacity_sha']}")
        return

    prices = inputs["prices"]
    brrk = inputs["brrk"]
    cap1 = inputs["cap1"]
    native = inputs["native"]
    proxy = inputs["proxy"]
    floors = inputs["floors"]

    legacy = {
        cost: old.simulate_legacy_path(
            brrk, prices, start=FULL_START, end=FULL_END, cost_bps=cost
        )
        for cost in core.COST_GRID
    }
    matched = {
        cost: core.simulate_path(
            cap1,
            cap1,
            prices,
            start=FULL_START,
            end=FULL_END,
            cost_bps=cost,
            funding_blocks_by_session=native,
        )
        for cost in core.COST_GRID
    }

    old_summary = _read_json(OLD_SUMMARY)
    benchmarks = {}
    for cost in core.COST_GRID:
        benchmarks[str(cost)] = {
            "btc_buy_and_hold": old._costed_buy_hold(
                prices, {"BTC": 1.0}, FULL_START, FULL_END, cost
            ),
            "four_asset_equal_weight_buy_and_hold": old._costed_buy_hold(
                prices, {a: 0.25 for a in core.ASSETS}, FULL_START, FULL_END, cost
            ),
            "legacy_brrk": old.path_metrics(legacy[cost]),
            "leverage_0041_cap1_architecture": core.path_metrics(matched[cost]),
            "immutable_leverage_0040_cap1": old_summary["candidate_matrix"]["1.00"][
                "price_only_metrics_by_cost_bps"
            ][str(cost)],
        }

    matrix = {}
    pass_by_cap: dict[float, bool] = {1.0: True}
    route_frames = []
    liquidation_rows = []

    for cap in core.CAPS:
        requested = core.construct_requested_targets(brrk, cap)
        paths = {
            cost: core.simulate_path(
                requested,
                cap1,
                prices,
                start=FULL_START,
                end=FULL_END,
                cost_bps=cost,
                funding_blocks_by_session=native,
            )
            for cost in core.COST_GRID
        }
        p5 = paths[5.0]
        historical = _historical_stress(prices, p5, cap)
        gaps = _gap_stress(p5)
        vol = _vol_stress(prices, requested, cap1, matched[5.0], native)
        liq = _liquidation_distance(p5)
        robust = _robustness(p5, matched[5.0], legacy[5.0])
        boot = (
            {"pass": True, "role": "CAP1_COMPARATOR"}
            if cap == 1.0
            else _bootstrap(p5, matched[5.0], legacy[5.0])
        )
        if cap == 1.0:
            funding = {"role": "CAP1_COMPARATOR", "pass": True}
            degraded = {"role": "CAP1_COMPARATOR", "pass": True}
            gate = {
                "pass_pre_broad_region": True,
                "gates": {"identity_comparator": True},
                "selected_operating_budget": core.select_operating_budget(
                    [core.path_metrics(p5)["max_drawdown"]]
                ),
            }
        else:
            funding = _funding_panel(
                prices, requested, cap1, cap1, native, proxy
            )
            degraded = _degraded(
                prices, requested, cap1, cap1, native, floors
            )
            gate = _candidate_gate(
                paths,
                matched,
                legacy,
                historical,
                gaps,
                vol,
                funding,
                degraded,
                liq,
                robust,
                boot,
            )
            pass_by_cap[round(cap, 2)] = bool(gate["pass_pre_broad_region"])

        matrix[f"{cap:.2f}"] = {
            "cap": cap,
            "architecture_metrics_by_cost_bps": {
                str(cost): core.path_metrics(path)
                for cost, path in paths.items()
            },
            "historical_stress": historical,
            "synthetic_gap_stress": gaps,
            "volatility_stress": vol,
            "funding_stress": funding,
            "degraded_execution": degraded,
            "liquidation": liq,
            "start_date_robustness": robust,
            "bootstrap": boot,
            "gate": gate,
        }
        route_frames.append(_route_split_frame(p5, cap))
        liquidation_rows.append(
            {
                "cap": cap,
                "pass": liq["pass"],
                "minimum_uniform_down_move": liq["minimum_uniform_down_move"],
                "worst_date": liq["worst_date"],
                "cross_margin_equity_usd": liq["cross_margin_equity_usd"],
            }
        )

    region_map = core.qualifying_region_map(pass_by_cap)
    selection_rows: dict[float, dict[str, object]] = {}
    for cap in core.CAPS:
        key = f"{cap:.2f}"
        row = matrix[key]
        if cap == 1.0:
            row["gate"]["broad_region_pass"] = None
            row["gate"]["final_research_pass"] = None
            continue
        broad = bool(region_map.get(cap, False))
        final_pass = bool(row["gate"]["pass_pre_broad_region"] and broad)
        row["gate"]["broad_region_pass"] = broad
        row["gate"]["final_research_pass"] = final_pass
        metrics = row["architecture_metrics_by_cost_bps"]["5.0"]
        selection_rows[cap] = {
            "final_research_pass": final_pass,
            "cagr": metrics["cagr"],
            "calmar": metrics["calmar"],
            "sharpe": metrics["sharpe"],
            "max_drawdown": metrics["max_drawdown"],
        }

    selected_cap = core.choose_sweet_spot(selection_rows, pass_by_cap)
    if selected_cap is None:
        decision = {
            "status": "NO_PROMOTION",
            "selected_research_cap": None,
            "selected_operating_max_drawdown_budget": None,
            "prospective_live_cap_if_separately_authorized": None,
            "production_authorized": False,
        }
    else:
        selected_row = matrix[f"{selected_cap:.2f}"]
        decision = {
            "status": "RESEARCH_PROMOTION_CANDIDATE_NOT_PRODUCTION_AUTHORIZED",
            "selected_research_cap": selected_cap,
            "selected_operating_max_drawdown_budget": selected_row["gate"][
                "selected_operating_budget"
            ],
            "prospective_live_cap_if_separately_authorized": core.prospective_live_cap(
                selected_cap
            ),
            "production_authorized": False,
        }

    result = {
        "schema_version": 1,
        "study_id": "LEVERAGE-0041",
        "status": "ONE_TIME_PREREGISTERED_STUDY_COMPLETE",
        "production_authorized": False,
        "input_evidence": {
            "base_main": inputs["contract"]["base_main"],
            "preregistration_sha256": _sha256(PREREG_PATH),
            "implementation_contract_sha256": _sha256(CONTRACT_PATH),
            "immutable_leverage_0040_summary_sha256": OLD_DIGEST.read_text(
                encoding="utf-8"
            ).strip(),
            "price_frame_sha256": _dataframe_sha256(prices),
            "funding_blocks_sha256": _sha256(FUNDING_PATH),
            "router_vwap_slippage_sha256": inputs["capacity_sha"],
            "router_capacity_floor_usd": {
                f"{a}:{m}": v for (a, m), v in floors.items()
            },
            "router_classifications": inputs["route_classifications"],
            "margin_snapshot_sha256": _sha256(MARGIN_SNAPSHOT),
            "raw_target_authority": authority._target_authority_meta,
            "runner_entrypoint": "research/leverage_0041/run_leverage_0041_once.py",
            "owner_run_once_authorized_pre_result": True,
        },
        "benchmarks": benchmarks,
        "candidate_matrix": matrix,
        "broad_region_pre_gate_map": {
            f"{cap:.2f}": bool(pass_by_cap.get(cap, False))
            for cap in core.CAPS
        },
        "selection": decision,
        "constraints": {
            "production_authorized_components": [],
            "post_result_retuning_allowed": False,
            "search_caps": list(core.CAPS),
            "cash_collateral_reserve_fraction": core.CASH_RESERVE,
            "spot_financing_max_fraction": core.SPOT_BUDGET,
            "funding_lookback_sessions": core.FUNDING_LOOKBACK_SESSIONS,
            "funding_full_overlay_max_bps_day": core.FUNDING_FULL_OVERLAY_MAX_BPS_DAY,
            "funding_zero_overlay_min_bps_day": core.FUNDING_ZERO_OVERLAY_MIN_BPS_DAY,
            "liquidation_min_distance": core.LIQUIDATION_MIN_DISTANCE,
            "catastrophic_drawdown_boundary": 0.70,
            "bootstrap_base_seed": core.BOOTSTRAP_BASE_SEED,
        },
    }

    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    safe = _json_safe(result)
    summary = RESULT_DIR / "summary.json"
    summary.write_text(json.dumps(safe, indent=2, sort_keys=True), encoding="utf-8")

    rows = []
    for cap in core.CAPS:
        row = safe["candidate_matrix"][f"{cap:.2f}"]
        m = row["architecture_metrics_by_cost_bps"]["5.0"]
        g = row["gate"]
        rows.append(
            {
                "cap": cap,
                "cagr_5bps": m["cagr"],
                "max_drawdown_5bps": m["max_drawdown"],
                "sharpe_5bps": m["sharpe"],
                "calmar_5bps": m["calmar"],
                "turnover_5bps": m["turnover"],
                "avg_gross_5bps": m["avg_gross_exposure"],
                "avg_overlay_scale_5bps": m["avg_overlay_scale"],
                "pass_pre_broad_region": g.get("pass_pre_broad_region"),
                "broad_region_pass": g.get("broad_region_pass"),
                "final_research_pass": g.get("final_research_pass"),
                "operating_budget": g.get("selected_operating_budget"),
            }
        )
    pd.DataFrame(rows).to_csv(
        RESULT_DIR / "candidate_table.csv", index=False, float_format="%.12f"
    )

    route_frame = pd.concat(route_frames).reset_index().rename(columns={"index": "date"})
    route_frame.to_csv(
        RESULT_DIR / "route_split_daily.csv", index=False, float_format="%.12f"
    )
    pd.DataFrame(liquidation_rows).to_csv(
        RESULT_DIR / "liquidation_table.csv", index=False, float_format="%.12f"
    )
    (RESULT_DIR / "router_vwap_slippage.csv").write_bytes(
        inputs["capacity_file"].read_bytes()
    )
    digest = _sha256(summary)
    (RESULT_DIR / "summary.sha256").write_text(digest + "\n", encoding="utf-8")
    print("LEVERAGE-0041 one-time study completed; immutable result files written.")
    print(f"summary_sha256={digest}")


if __name__ == "__main__":
    main()
