from runner_support_a_0041 import *

def _historical_stress(prices, path: core.Path0041, cap: float):
    out = {}
    for name, (start, end, role) in HISTORICAL_WINDOWS.items():
        s, e = pd.Timestamp(start), pd.Timestamp(end)
        if role == "FULL_BRRK":
            out[name] = {
                "role": role,
                "metrics": old._returns_metrics(path.returns.loc[s:e]),
            }
        else:
            proxy_targets = old._proxy_targets(prices.loc[:e], cap)
            proxy_path = old.simulate_p3_3_economic_path(
                proxy_targets,
                prices,
                start=s - pd.Timedelta(days=1),
                end=e,
                cost_bps=5.0,
            )
            metrics = old.path_metrics(proxy_path)
            out[name] = {
                "role": role,
                "metrics": metrics,
                "catastrophe_pass": bool(metrics["max_drawdown"] > -0.70),
            }
    return out


def _prices_from_returns(base_prices: pd.DataFrame, returns: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=base_prices.index, columns=core.ASSETS, dtype=float)
    out.iloc[0] = base_prices.iloc[0]
    for i in range(1, len(out)):
        out.iloc[i] = out.iloc[i - 1].to_numpy(float) * (
            1.0 + returns.iloc[i].to_numpy(float)
        )
    return out


def _vol_stress(prices, requested, base_targets, matched_path, native):
    asset_ret = prices.loc[:, list(core.ASSETS)].pct_change().fillna(0.0)
    blocks = old._worst_blocks(matched_path.returns)
    rows = {}
    for mult in VOL_MULTIPLIERS:
        scenarios = []
        for start, end in blocks:
            stressed = asset_ret.copy()
            mask = (stressed.index >= start) & (stressed.index <= end)
            stressed.loc[mask, list(core.ASSETS)] = old.stressed_log_returns(
                stressed.loc[mask, list(core.ASSETS)], mult
            )
            synthetic = _prices_from_returns(prices.loc[:, list(core.ASSETS)], stressed)
            p = core.simulate_path(
                requested,
                base_targets,
                synthetic,
                start=FULL_START,
                end=FULL_END,
                cost_bps=5.0,
                funding_blocks_by_session=native,
                apply_funding_reducer=True,
                charge_native_funding=True,
            )
            m = core.path_metrics(p)
            scenarios.append(
                {
                    "block_start": start.strftime("%Y-%m-%d"),
                    "block_end": end.strftime("%Y-%m-%d"),
                    "metrics": m,
                    "catastrophe_pass": bool(m["max_drawdown"] > -0.70),
                }
            )
        rows[str(mult)] = scenarios
    return {
        "selected_blocks": [
            [s.strftime("%Y-%m-%d"), e.strftime("%Y-%m-%d")] for s, e in blocks
        ],
        "scenarios": rows,
    }


def _robustness(candidate: core.Path0041, matched: core.Path0041, legacy):
    rows = {}
    passed = True
    for start in START_DATES:
        c = old._returns_metrics(candidate.returns.loc[start:])
        m = old._returns_metrics(matched.returns.loc[start:])
        l = old._returns_metrics(legacy.returns.loc[start:])
        dm = c["cagr"] - m["cagr"]
        dl = c["cagr"] - l["cagr"]
        ok = dm >= -0.02 and dl >= -0.02
        passed = passed and ok
        rows[start] = {
            "candidate": c,
            "matched_cap1": m,
            "legacy_brrk": l,
            "cagr_diff_vs_matched": dm,
            "cagr_diff_vs_legacy": dl,
            "pass": bool(ok),
        }
    return {"pass": bool(passed), "rows": rows}


def _bootstrap(candidate: core.Path0041, matched: core.Path0041, legacy):
    rows = {}
    passed = True
    for block in core.BOOTSTRAP_BLOCKS:
        cm = old.paired_bootstrap_stats(
            candidate.returns,
            matched.returns,
            block,
            resamples=core.BOOTSTRAP_RESAMPLES,
            base_seed=core.BOOTSTRAP_BASE_SEED,
        )
        cl = old.paired_bootstrap_stats(
            candidate.returns,
            legacy.returns,
            block,
            resamples=core.BOOTSTRAP_RESAMPLES,
            base_seed=core.BOOTSTRAP_BASE_SEED,
        )
        ok = (
            cm["terminal_outperformance_probability"] >= 0.80
            and cm["annualized_return_difference_p05"] >= -0.01
            and cl["terminal_outperformance_probability"] >= 0.80
            and cl["annualized_return_difference_p05"] >= -0.01
        )
        rows[str(block)] = {
            "vs_matched_cap1": cm,
            "vs_legacy_brrk": cl,
            "pass": bool(ok),
        }
        passed = passed and ok
    return {"pass": bool(passed), "rows": rows}


def _pareto_not_dominated(candidate, comparator):
    return not (
        comparator["end_multiple"] >= candidate["end_multiple"]
        and comparator["max_drawdown"] >= candidate["max_drawdown"]
        and (
            comparator["end_multiple"] > candidate["end_multiple"]
            or comparator["max_drawdown"] > candidate["max_drawdown"]
        )
    )


def _funding_panel(prices, requested, base_targets, matched_requested, native, proxy):
    rows = {}
    for spike in FUNDING_SPIKES:
        matched = core.simulate_path(
            matched_requested,
            base_targets,
            prices,
            start=COMMON_FUNDING_START,
            end=COMMON_FUNDING_END,
            cost_bps=5.0,
            funding_blocks_by_session=native,
            apply_funding_reducer=True,
            charge_native_funding=True,
            adverse_funding_spike_multiplier=spike,
        )
        candidate = core.simulate_path(
            requested,
            base_targets,
            prices,
            start=COMMON_FUNDING_START,
            end=COMMON_FUNDING_END,
            cost_bps=5.0,
            funding_blocks_by_session=native,
            apply_funding_reducer=True,
            charge_native_funding=True,
            adverse_funding_spike_multiplier=spike,
        )
        cm, mm = core.path_metrics(candidate), core.path_metrics(matched)
        complete = bool(
            candidate.funding_data_complete.all()
            and matched.funding_data_complete.all()
        )
        rows[str(spike)] = {
            "candidate": cm,
            "matched_cap1": mm,
            "native_evidence_complete": complete,
            "pass": bool(
                complete
                and cm["end_multiple"] >= mm["end_multiple"]
                and cm["max_drawdown"] > -0.70
            ),
        }

    proxy_matched = core.simulate_path(
        matched_requested,
        base_targets,
        prices,
        start=COMMON_FUNDING_START,
        end=COMMON_FUNDING_END,
        cost_bps=5.0,
        funding_blocks_by_session=proxy,
        apply_funding_reducer=True,
        charge_native_funding=True,
    )
    proxy_candidate = core.simulate_path(
        requested,
        base_targets,
        prices,
        start=COMMON_FUNDING_START,
        end=COMMON_FUNDING_END,
        cost_bps=5.0,
        funding_blocks_by_session=proxy,
        apply_funding_reducer=True,
        charge_native_funding=True,
    )
    return {
        "native_hyperliquid": rows,
        "binance_proxy_report_only": {
            "role": "REPORT_ONLY_BINANCE_PROXY_NOT_HYPERLIQUID_LEVEL",
            "candidate": core.path_metrics(proxy_candidate),
            "matched_cap1": core.path_metrics(proxy_matched),
        },
        "pass": bool(all(row["pass"] for row in rows.values())),
    }


def _degraded(prices, requested, base_targets, matched_requested, native, floors):
    out = {}
    scenarios = (
        ("DEPTH_50_SLIP_1_5", 0.50, 1.5, 1.0),
        ("DEPTH_25_SLIP_2_0", 0.25, 2.0, 1.0),
        ("PARTIAL_FILL_50", 1.00, 1.0, 0.5),
    )
    for name, depth, cost_mult, fill in scenarios:
        matched = core.simulate_path(
            matched_requested,
            base_targets,
            prices,
            start=FULL_START,
            end=FULL_END,
            cost_bps=5.0,
            funding_blocks_by_session=native,
            fill_fraction=fill,
            transaction_cost_multiplier=cost_mult,
        )
        candidate = core.simulate_path(
            requested,
            base_targets,
            prices,
            start=FULL_START,
            end=FULL_END,
            cost_bps=5.0,
            funding_blocks_by_session=native,
            fill_fraction=fill,
            transaction_cost_multiplier=cost_mult,
        )
        cm, mm = core.path_metrics(candidate), core.path_metrics(matched)
        capacity = _capacity_check(candidate, floors, depth)
        ok = (
            cm["end_multiple"] >= mm["end_multiple"]
            and cm["max_drawdown"] > -0.70
            and capacity["pass"]
        )
        out[name] = {
            "candidate": cm,
            "matched_cap1": mm,
            "capacity": capacity,
            "pass": bool(ok),
        }
    return {"pass": bool(all(x["pass"] for x in out.values())), "scenarios": out}


def _candidate_gate(paths, matched, legacy, historical, gaps, vol, funding, degraded, liq, robust, bootstrap):
    c5, c10, c20 = [core.path_metrics(paths[x]) for x in (5.0, 10.0, 20.0)]
    m5, m10, m20 = [core.path_metrics(matched[x]) for x in (5.0, 10.0, 20.0)]
    l5, l10, l20 = [old.path_metrics(legacy[x]) for x in (5.0, 10.0, 20.0)]
    budget = core.select_operating_budget(
        [
            c5["max_drawdown"],
            historical["2024_STRESS"]["metrics"]["max_drawdown"],
            historical["2025_FULL_YEAR"]["metrics"]["max_drawdown"],
            historical["2026_RECENT"]["metrics"]["max_drawdown"],
        ]
    )
    gates = {
        "after_cost_5bps": bool(
            c5["end_multiple"] > m5["end_multiple"]
            and c5["end_multiple"] > l5["end_multiple"]
        ),
        "after_cost_10bps": bool(
            c10["end_multiple"] > m10["end_multiple"]
            and c10["end_multiple"] > l10["end_multiple"]
        ),
        "not_dominated_20bps": bool(
            _pareto_not_dominated(c20, m20)
            and _pareto_not_dominated(c20, l20)
        ),
        "operating_budget_found": budget is not None,
        "catastrophe_full_history": bool(c5["max_drawdown"] > -0.70),
        "historical_proxy_catastrophe": bool(
            all(x.get("catastrophe_pass", True) for x in historical.values())
        ),
        "synthetic_gap": bool(all(x["pass"] for x in gaps.values())),
        "volatility_stress": bool(
            all(
                x["catastrophe_pass"]
                for block_rows in vol["scenarios"].values()
                for x in block_rows
            )
        ),
        "funding": bool(funding["pass"]),
        "degraded_execution": bool(degraded["pass"]),
        "liquidation_distance_gt_55pct": bool(liq["pass"]),
        "start_date_robustness": bool(robust["pass"]),
        "bootstrap": bool(bootstrap["pass"]),
    }
    return {
        "pass_pre_broad_region": bool(all(gates.values())),
        "gates": gates,
        "selected_operating_budget": budget,
    }


def _route_split_frame(path: core.Path0041, cap: float) -> pd.DataFrame:
    frame = pd.DataFrame(index=path.held_weights.index)
    frame["cap"] = float(cap)
    frame["overlay_scale"] = path.funding_overlay_scale
    frame["requested_gross"] = path.requested_gross
    frame["effective_target_gross"] = path.effective_target_gross
    frame["held_gross"] = path.gross_exposure
    frame["cash_reserve"] = path.cash_reserve_weight
    for asset in core.ASSETS:
        frame[f"{asset}_spot"] = path.routed_spot_weights[asset]
        frame[f"{asset}_base_perp"] = path.routed_base_perp_weights[asset]
        frame[f"{asset}_incremental_perp"] = path.routed_incremental_perp_weights[asset]
        frame[f"{asset}_total_perp"] = path.routed_perp_weights[asset]
    frame["spot_gross"] = path.routed_spot_weights.abs().sum(axis=1)
    frame["base_perp_gross"] = path.routed_base_perp_weights.abs().sum(axis=1)
    frame["incremental_perp_gross"] = path.routed_incremental_perp_weights.abs().sum(axis=1)
    frame["perp_gross"] = path.routed_perp_weights.abs().sum(axis=1)
    return frame


def _preflight(router_artifact_dir: Path):
    prereg, contract = _validate_pre_run_contract()
    prices, v1, brrk, defensive, cap1 = _load_authoritative_inputs()
    old._legacy_preflight(prices, brrk)
    floors, capacity_file, capacity_sha, classifications = _capacity_floor_by_route(
        router_artifact_dir
    )
    native, proxy = _funding_maps()
    snapshot = load_frozen_snapshot()
    test_state = evaluate_cross_margin_state(
        current_cross_account_equity_usd=core.CASH_RESERVE * core.REFERENCE_EQUITY,
        current_long_perp_notionals_usd={"BTC": 100.0},
        relative_mark_returns={"BTC": 0.0},
        snapshot=snapshot,
    )
    if test_state.liquidatable:
        raise RuntimeError("25% collateral reserve sanity state is liquidatable")
    return {
        "prereg": prereg,
        "contract": contract,
        "prices": prices,
        "v1": v1,
        "brrk": brrk,
        "defensive": defensive,
        "cap1": cap1,
        "floors": floors,
        "capacity_file": capacity_file,
        "capacity_sha": capacity_sha,
        "route_classifications": classifications,
        "native": native,
        "proxy": proxy,
    }

__all__ = [n for n in globals() if not n.startswith('__')]
