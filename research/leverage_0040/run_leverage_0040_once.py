from __future__ import annotations

"""One-time LEVERAGE-0040 historical study runner.

This file is inert unless explicitly executed by the dedicated run-once workflow.
All study semantics are frozen in LEVERAGE-0040-STUDY-IMPLEMENTATION-V1.json
before any cap>1 historical result is permitted.

The runner writes machine-readable result artifacts and intentionally avoids
printing candidate economic metrics to stdout.
"""

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Mapping

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RESEARCH = ROOT / "research"
CORE = RESEARCH / "core"
HYBRID = RESEARCH / "hybrid_meta"
LEVERAGE = RESEARCH / "leverage_0040"
RESULT_DIR = RESEARCH / "results" / "leverage_0040"
for p in (ROOT, RESEARCH, CORE, HYBRID, LEVERAGE):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import crypto_rotation_backtest as bt  # noqa: E402
from walkforward_v1_meta import build_benchmark_v1  # noqa: E402
from liquidation_model import evaluate_cross_margin_state, load_frozen_snapshot, uniform_long_down_liquidation_distance  # noqa: E402
from study_core import ASSETS, CAPS, BOOTSTRAP_BLOCKS, PathResult, broad_region_eligible, buy_and_hold_returns, construct_candidate_targets, path_metrics, paired_bootstrap_stats, recover_defensive_scale, select_operating_budget, simulate_legacy_path, simulate_p3_3_economic_path, stressed_log_returns, synthetic_gap_return  # noqa: E402

CONTRACT_PATH = LEVERAGE / "LEVERAGE-0040-STUDY-IMPLEMENTATION-V1.json"
PREREG_PATH = LEVERAGE / "LEVERAGE-0040.json"
ADDENDUM_PATH = LEVERAGE / "LEVERAGE-0040-PRE-RUN-ADDENDUM-V1.json"
WEIGHTS_PATH = RESEARCH / "results" / "pit_disp_0015" / "daily_weights.csv"
BASELINE_FREEZE_PATH = RESEARCH / "leverage_0039" / "P4_1_BASELINE_FREEZE.json"
FUNDING_PATH = RESEARCH / "results" / "funding_crossvenue_0002" / "paired_8h_blocks.csv"
REFERENCE_EQUITY = 2000.0
FULL_START = pd.Timestamp("2022-12-10")
FULL_END = pd.Timestamp("2026-08-02")
COMMON_FUNDING_START = pd.Timestamp("2023-06-18")
COMMON_FUNDING_END = pd.Timestamp("2026-07-31")
COST_GRID = (5.0, 10.0, 20.0, 50.0)
FUNDING_SPIKES = (1.0, 2.0, 3.0, 5.0)
VOL_MULTIPLIERS = (1.5, 2.0, 3.0)
START_DATES = ("2022-12-10", "2023-03-01", "2023-06-01", "2024-01-01")
GAP_SCENARIOS = {
    "UNIFORM_-10": {a: -0.10 for a in ASSETS}, "UNIFORM_-20": {a: -0.20 for a in ASSETS},
    "UNIFORM_-30": {a: -0.30 for a in ASSETS}, "UNIFORM_-40": {a: -0.40 for a in ASSETS},
    "UNIFORM_-50": {a: -0.50 for a in ASSETS},
    "ALT_CRASH": {"BTC": -0.25, "ETH": -0.35, "SOL": -0.50, "BNB": -0.40},
    "BTC_LED_CRASH": {"BTC": -0.40, "ETH": -0.25, "SOL": -0.30, "BNB": -0.25},
}
HISTORICAL_WINDOWS = {
    "2021_SPRING_CRASH_PROXY": ("2021-05-01", "2021-07-31", "PROXY"),
    "2021_BEAR_TRANSITION_PROXY": ("2021-11-01", "2022-03-31", "PROXY"),
    "2022_SEVERE_DRAWDOWN_PROXY": ("2022-05-01", "2022-12-31", "PROXY"),
    "2024_STRESS": ("2024-03-01", "2024-05-15", "FULL_BRRK"),
    "2025_FULL_YEAR": ("2025-01-01", "2025-12-31", "FULL_BRRK"),
    "2026_RECENT": ("2026-01-01", "2026-08-02", "FULL_BRRK"),
}


def _read_json(path): return json.loads(Path(path).read_text(encoding="utf-8"))
def _sha256_bytes(payload): return hashlib.sha256(payload).hexdigest()
def _dataframe_sha256(frame): return _sha256_bytes(frame.to_csv(index=True, float_format="%.12f", lineterminator="\n").encode())
def _json_safe(v):
    if isinstance(v, dict): return {str(k): _json_safe(x) for k,x in v.items()}
    if isinstance(v, (list, tuple)): return [_json_safe(x) for x in v]
    if isinstance(v, (pd.Timestamp, np.datetime64)): return pd.Timestamp(v).isoformat()
    if isinstance(v, (np.floating, float)):
        x=float(v); return None if math.isnan(x) or math.isinf(x) else x
    if isinstance(v, (np.integer, int)): return int(v)
    if isinstance(v, (np.bool_, bool)): return bool(v)
    return v


def _validate_pre_run_contract():
    contract, prereg, addendum = map(_read_json, (CONTRACT_PATH, PREREG_PATH, ADDENDUM_PATH))
    if contract.get("status") != "FROZEN_BEFORE_FIRST_ECONOMIC_RUN" or contract.get("result_observed_before_freeze") is not False:
        raise RuntimeError("study implementation contract is not a clean pre-result freeze")
    if addendum.get("production_authorized") is not False:
        raise RuntimeError("addendum unexpectedly authorizes production")
    if (RESULT_DIR / "summary.json").exists():
        raise RuntimeError("LEVERAGE-0040 result already exists; one-time run cannot repeat")
    return contract, prereg, addendum


def _fetch_prices():
    prices = pd.DataFrame({a: bt.fetch_daily(f"{a}USDT") for a in ASSETS}).dropna().sort_index()
    required = pd.date_range(prices.index.min(), FULL_END, freq="D")
    if not required.isin(prices.index).all():
        raise RuntimeError("price history is not contiguous through study end")
    return prices.loc[:FULL_END, list(ASSETS)]


def _load_frozen_targets():
    raw=pd.read_csv(WEIGHTS_PATH,parse_dates=["date"]).set_index("date").sort_index()
    v1=pd.DataFrame({a:raw[f"V1_BASELINE__{a}"].astype(float) for a in ASSETS},index=raw.index)
    brrk=pd.DataFrame({a:raw[f"BRRK0011_BASELINE__{a}"].astype(float) for a in ASSETS},index=raw.index)
    return v1,brrk,recover_defensive_scale(v1,brrk)


def _returns_metrics(ret):
    ret=ret.dropna().astype(float); nav=(1+ret).cumprod(); years=len(ret)/365.25; dd=nav/nav.cummax()-1; std=float(ret.std())
    cagr=float(nav.iloc[-1]**(1/years)-1); mdd=float(dd.min())
    return {"end_multiple":float(nav.iloc[-1]),"cagr":cagr,"max_drawdown":mdd,"sharpe":float(ret.mean()/std*math.sqrt(365)) if std>0 else float("nan"),"calmar":float(cagr/abs(mdd)) if mdd<0 else float("nan")}


def _costed_buy_hold(prices,weights,start,end,cost_bps):
    ret=buy_and_hold_returns(prices.loc[start:end],weights)
    if len(ret): ret.iloc[0]-=sum(abs(float(v)) for v in weights.values())*cost_bps/10000
    return _returns_metrics(ret)


def _legacy_preflight(prices,brrk):
    freeze=_read_json(BASELINE_FREEZE_PATH)["corrected_brrk0011_result"]
    path=simulate_legacy_path(brrk,prices,start=FULL_START,end=FULL_END,cost_bps=5.0); m=path_metrics(path)
    checks={"cagr":(m["cagr"],float(freeze["cagr"]),.005),"max_drawdown":(m["max_drawdown"],float(freeze["max_drawdown"]),.0005),"sharpe":(m["sharpe"],float(freeze["sharpe"]),.003),"avg_gross_exposure":(m["avg_gross_exposure"],float(freeze["average_gross_exposure"]),.003)}
    for name,(actual,expected,tol) in checks.items():
        if abs(actual-expected)>tol: raise RuntimeError(f"baseline preflight failed before candidate evaluation: {name} actual={actual} expected={expected} tolerance={tol}")
    return {"metrics":m,"checks":checks}


def _funding_block_maps():
    raw=pd.read_csv(FUNDING_PATH); raw["block"]=pd.to_datetime(raw["block"],utc=True).dt.tz_convert(None); native={}; proxy={}
    for block,g in raw.groupby("block",sort=True):
        day=pd.Timestamp(block).normalize(); nr={a:0.0 for a in ASSETS}; br={a:0.0 for a in ASSETS}
        for _,row in g.iterrows():
            a=str(row["asset"])
            if a in ASSETS: nr[a]=float(row["hyperliquid_additive"]); br[a]=float(row["binance_additive"])
        native.setdefault(day,[]).append(nr); proxy.setdefault(day,[]).append(br)
    return native,proxy


def _capacity_floor_by_route(artifact_dir):
    files=list(Path(artifact_dir).rglob("vwap_slippage.csv"))
    if len(files)!=1: raise RuntimeError(f"expected one vwap_slippage.csv, found {len(files)}")
    f=files[0]; frame=pd.read_csv(f); floor={}
    for asset,market in [("BTC","spot"),("BTC","perp"),("ETH","perp"),("SOL","perp"),("BNB","perp")]:
        sub=frame[(frame.target==asset)&(frame.market_type==market)]; good=[]
        for notional,g in sub.groupby("target_notional"):
            fill=g["fully_fillable_in_returned_book"].astype(str).str.lower().isin(["true","1"])
            if {"buy","sell"}.issubset(set(g.side.astype(str))) and bool(fill.all()): good.append(float(notional))
        if not good: raise RuntimeError(f"no two-sided fillable capacity evidence for {asset} {market}")
        floor[(asset,market)]=max(good)
    return floor,f,_sha256_bytes(f.read_bytes())


def _route_exposures(candidate,matched):
    spot=min(max(float(candidate["BTC"]),0),max(float(matched["BTC"]),0))
    return {("BTC","spot"):spot,("BTC","perp"):max(float(candidate["BTC"])-spot,0),("ETH","perp"):max(float(candidate["ETH"]),0),("SOL","perp"):max(float(candidate["SOL"]),0),("BNB","perp"):max(float(candidate["BNB"]),0)}


def _capacity_check(cand,matched,floors,depth):
    prev={k:0.0 for k in floors}; max_trade={k:0.0 for k in floors}; fail=[]
    for dt in cand.index.intersection(matched.index):
        routed=_route_exposures(cand.loc[dt],matched.loc[dt])
        for key,w in routed.items():
            trade=abs(float(w)-prev[key])*REFERENCE_EQUITY; max_trade[key]=max(max_trade[key],trade); cap=floors[key]*depth
            if trade>cap+1e-9: fail.append({"date":dt.strftime("%Y-%m-%d"),"route":f"{key[0]}:{key[1]}","trade_usd":trade,"capacity_usd":cap})
            prev[key]=float(w)
    return {"pass":not fail,"max_trade_usd_by_route":{f"{a}:{m}":v for (a,m),v in max_trade.items()},"capacity_usd_by_route":{f"{a}:{m}":v*depth for (a,m),v in floors.items()},"failures":fail[:25]}


def _minimum_liquidation_distance(cand,matched):
    snapshot=load_frozen_snapshot(); minimum=float("inf"); worst=None; any_perp=False
    for dt in cand.index.intersection(matched.index):
        routed=_route_exposures(cand.loc[dt],matched.loc[dt]); spot=routed[("BTC","spot")]; perp={"BTC":routed[("BTC","perp")],"ETH":routed[("ETH","perp")],"SOL":routed[("SOL","perp")],"BNB":routed[("BNB","perp")]}; notionals={a:w*REFERENCE_EQUITY for a,w in perp.items() if w>1e-15}
        if not notionals: continue
        any_perp=True; equity=REFERENCE_EQUITY*(1-spot)
        if equity<=0: return {"pass":False,"minimum_uniform_down_move":0.0,"worst_date":dt.strftime("%Y-%m-%d")}
        dist=uniform_long_down_liquidation_distance(current_cross_account_equity_usd=equity,current_long_perp_notionals_usd=notionals,snapshot=snapshot)
        d=float("inf") if not dist.liquidates_within_domain else float(dist.uniform_down_move_fraction)
        if d<minimum: minimum=d; worst=dt
    if not any_perp: return {"pass":True,"minimum_uniform_down_move":None,"worst_date":None}
    return {"pass":minimum>.50,"minimum_uniform_down_move":None if math.isinf(minimum) else minimum,"worst_date":None if worst is None else worst.strftime("%Y-%m-%d")}


def _gap_stress(cand,matched):
    snapshot=load_frozen_snapshot(); out={}
    for name,gaps in GAP_SCENARIOS.items():
        worst={"return":float("inf"),"date":None,"liquidatable":False}
        for dt in cand.index.intersection(matched.index):
            c=cand.loc[dt].to_dict(); m=matched.loc[dt].to_dict(); ret=synthetic_gap_return(c,gaps); routed=_route_exposures(c,m); spot=routed[("BTC","spot")]; notionals={"BTC":routed[("BTC","perp")]*REFERENCE_EQUITY,"ETH":routed[("ETH","perp")]*REFERENCE_EQUITY,"SOL":routed[("SOL","perp")]*REFERENCE_EQUITY,"BNB":routed[("BNB","perp")]*REFERENCE_EQUITY}; notionals={a:v for a,v in notionals.items() if v>1e-15}; liq=False
            if notionals:
                state=evaluate_cross_margin_state(current_cross_account_equity_usd=REFERENCE_EQUITY*(1-spot),current_long_perp_notionals_usd=notionals,relative_mark_returns={a:gaps[a] for a in notionals},snapshot=snapshot); liq=bool(state.liquidatable)
            if ret<worst["return"]: worst={"return":ret,"date":dt.strftime("%Y-%m-%d"),"liquidatable":liq}
            elif liq: worst["liquidatable"]=True
        worst.update({"catastrophe_pass":worst["return"]>-.70,"liquidation_pass":not worst["liquidatable"]}); worst["pass"]=worst["catastrophe_pass"] and worst["liquidation_pass"]; out[name]=worst
    return out


def _worst_blocks(ret,length=20,count=3):
    roll=(1+ret).rolling(length).apply(np.prod,raw=True)-1; ordered=sorted(((dt,float(v)) for dt,v in roll.dropna().items()),key=lambda x:(x[1],x[0])); chosen=[]
    for end,_ in ordered:
        start=pd.Timestamp(end)-pd.Timedelta(days=length-1)
        if any(not (end<s or start>e) for s,e in chosen): continue
        chosen.append((start,pd.Timestamp(end)))
        if len(chosen)==count: break
    return sorted(chosen)


def _prices_from_returns(base,ret):
    out=pd.DataFrame(index=base.index,columns=ASSETS,dtype=float); out.iloc[0]=base.iloc[0]
    for i in range(1,len(out)): out.iloc[i]=out.iloc[i-1].to_numpy(float)*(1+ret.iloc[i].to_numpy(float))
    return out


def _vol_stress(prices,candidate_targets,matched_path):
    asset_ret=prices.pct_change().fillna(0.0); blocks=_worst_blocks(matched_path.returns); rows={}
    for mult in VOL_MULTIPLIERS:
        rr=[]
        for start,end in blocks:
            stressed=asset_ret.copy(); mask=(stressed.index>=start)&(stressed.index<=end); stressed.loc[mask,list(ASSETS)]=stressed_log_returns(stressed.loc[mask,list(ASSETS)],mult); synthetic=_prices_from_returns(prices,stressed); p=simulate_p3_3_economic_path(candidate_targets,synthetic,start=FULL_START,end=FULL_END,cost_bps=5.0); m=path_metrics(p); rr.append({"block_start":start.strftime("%Y-%m-%d"),"block_end":end.strftime("%Y-%m-%d"),"metrics":m,"catastrophe_pass":m["max_drawdown"]>-.70})
        rows[str(mult)]=rr
    return {"selected_blocks":[[s.strftime("%Y-%m-%d"),e.strftime("%Y-%m-%d")] for s,e in blocks],"scenarios":rows}


def _proxy_targets(prices,cap): return build_benchmark_v1(prices).loc[:,list(ASSETS)]*float(cap)


def _historical_stress(prices,path,cap):
    out={}
    for name,(start,end,role) in HISTORICAL_WINDOWS.items():
        s,e=pd.Timestamp(start),pd.Timestamp(end)
        if role=="FULL_BRRK": out[name]={"role":role,"metrics":_returns_metrics(path.returns.loc[s:e])}
        else:
            p=simulate_p3_3_economic_path(_proxy_targets(prices.loc[:e],cap),prices,start=s,end=e,cost_bps=5.0); m=path_metrics(p); out[name]={"role":role,"metrics":m,"catastrophe_pass":m["max_drawdown"]>-.70}
    return out


def _robustness(candidate,matched,legacy):
    rows={}; passed=True
    for start in START_DATES:
        c,m,l=map(_returns_metrics,(candidate.returns.loc[start:],matched.returns.loc[start:],legacy.returns.loc[start:])); dm=c["cagr"]-m["cagr"]; dl=c["cagr"]-l["cagr"]; ok=dm>=-.02 and dl>=-.02; passed &= ok; rows[start]={"candidate":c,"matched_cap1":m,"legacy_brrk":l,"cagr_diff_vs_matched":dm,"cagr_diff_vs_legacy":dl,"pass":ok}
    return {"pass":bool(passed),"rows":rows}


def _bootstrap(candidate,matched,legacy):
    rows={}; passed=True
    for block in BOOTSTRAP_BLOCKS:
        cm=paired_bootstrap_stats(candidate.returns,matched.returns,block); cl=paired_bootstrap_stats(candidate.returns,legacy.returns,block); ok=cm["terminal_outperformance_probability"]>=.80 and cm["annualized_return_difference_p05"]>=-.01 and cl["terminal_outperformance_probability"]>=.80 and cl["annualized_return_difference_p05"]>=-.01; rows[str(block)]={"vs_matched_cap1":cm,"vs_legacy_brrk":cl,"pass":ok}; passed &= ok
    return {"pass":bool(passed),"rows":rows}


def _pareto_not_dominated(c,b): return not (b["end_multiple"]>=c["end_multiple"] and b["max_drawdown"]>=c["max_drawdown"] and (b["end_multiple"]>c["end_multiple"] or b["max_drawdown"]>c["max_drawdown"]))


def _funding_panel(prices,candidate_targets,matched_targets,legacy_ref,native,proxy):
    px=prices.loc[COMMON_FUNDING_START:COMMON_FUNDING_END]; ct=candidate_targets.reindex(px.index).ffill(); mt=matched_targets.reindex(px.index).ffill(); rows={}
    for spike in FUNDING_SPIKES:
        m=simulate_p3_3_economic_path(mt,px,start=COMMON_FUNDING_START,end=COMMON_FUNDING_END,cost_bps=5.0,funding_blocks_by_session=native,adverse_funding_spike_multiplier=spike,base_btc_fully_spot=True); c=simulate_p3_3_economic_path(ct,px,start=COMMON_FUNDING_START,end=COMMON_FUNDING_END,cost_bps=5.0,funding_blocks_by_session=native,adverse_funding_spike_multiplier=spike,matched_cap1_held=m.held_weights); cm,mm=path_metrics(c),path_metrics(m); rows[str(spike)]={"candidate":cm,"matched_cap1":mm,"pass":cm["end_multiple"]>=mm["end_multiple"] and cm["max_drawdown"]>-.70}
    ma=simulate_p3_3_economic_path(mt,px,start=COMMON_FUNDING_START,end=COMMON_FUNDING_END,cost_bps=5.0,funding_blocks_by_session=native,all_perp=True); ca=simulate_p3_3_economic_path(ct,px,start=COMMON_FUNDING_START,end=COMMON_FUNDING_END,cost_bps=5.0,funding_blocks_by_session=native,all_perp=True); allp={"candidate":path_metrics(ca),"matched_cap1":path_metrics(ma)}; allp["pass"]=allp["candidate"]["max_drawdown"]>-.70
    mp=simulate_p3_3_economic_path(mt,px,start=COMMON_FUNDING_START,end=COMMON_FUNDING_END,cost_bps=5.0,funding_blocks_by_session=proxy,base_btc_fully_spot=True); cp=simulate_p3_3_economic_path(ct,px,start=COMMON_FUNDING_START,end=COMMON_FUNDING_END,cost_bps=5.0,funding_blocks_by_session=proxy,matched_cap1_held=mp.held_weights); proxy_report={"role":"REPORT_ONLY_BINANCE_PROXY_NOT_HYPERLIQUID_LEVEL","candidate":path_metrics(cp),"matched_cap1":path_metrics(mp)}
    return {"native_hyperliquid":rows,"all_perp_stress":allp,"binance_proxy_report_only":proxy_report,"pass":all(x["pass"] for x in rows.values()) and allp["pass"],"legacy_reference":legacy_ref}


def _degraded(prices,candidate_targets,matched_targets,floors):
    out={}
    for name,depth,cost_mult,fill in [("DEPTH_50_SLIP_1_5",.5,1.5,1.0),("DEPTH_25_SLIP_2_0",.25,2.0,1.0),("PARTIAL_FILL_50",1.0,1.0,.5)]:
        m=simulate_p3_3_economic_path(matched_targets,prices,start=FULL_START,end=FULL_END,cost_bps=5.0,fill_fraction=fill,transaction_cost_multiplier=cost_mult); c=simulate_p3_3_economic_path(candidate_targets,prices,start=FULL_START,end=FULL_END,cost_bps=5.0,fill_fraction=fill,transaction_cost_multiplier=cost_mult); cm,mm=path_metrics(c),path_metrics(m); cap=_capacity_check(c.held_weights,m.held_weights,floors,depth); ok=cm["end_multiple"]>=mm["end_multiple"] and cm["max_drawdown"]>-.70 and cap["pass"]; out[name]={"candidate":cm,"matched_cap1":mm,"capacity":cap,"pass":ok}
    return {"pass":all(x["pass"] for x in out.values()),"scenarios":out}


def _candidate_gate(price_paths,matched,legacy,historical,gaps,vol,funding,degraded,liq,robust,bootstrap):
    c5,c10,c20=[path_metrics(price_paths[x]) for x in (5.0,10.0,20.0)]; m5,m10,m20=[path_metrics(matched[x]) for x in (5.0,10.0,20.0)]; l5,l10,l20=[path_metrics(legacy[x]) for x in (5.0,10.0,20.0)]; budget=select_operating_budget([c5["max_drawdown"],historical["2024_STRESS"]["metrics"]["max_drawdown"],historical["2025_FULL_YEAR"]["metrics"]["max_drawdown"],historical["2026_RECENT"]["metrics"]["max_drawdown"]]); gates={"after_cost_5bps":c5["end_multiple"]>m5["end_multiple"] and c5["end_multiple"]>l5["end_multiple"],"after_cost_10bps":c10["end_multiple"]>m10["end_multiple"] and c10["end_multiple"]>l10["end_multiple"],"not_dominated_20bps":_pareto_not_dominated(c20,m20) and _pareto_not_dominated(c20,l20),"operating_budget_found":budget is not None,"catastrophe_full_history":c5["max_drawdown"]>-.70,"historical_proxy_catastrophe":all(x.get("catastrophe_pass",True) for x in historical.values()),"synthetic_gap":all(x["pass"] for x in gaps.values()),"volatility_stress":all(x["catastrophe_pass"] for rows in vol["scenarios"].values() for x in rows),"funding":funding["pass"],"degraded_execution":degraded["pass"],"liquidation_distance":liq["pass"],"start_date_robustness":robust["pass"],"bootstrap":bootstrap["pass"]}; return {"pass_pre_broad_region":all(gates.values()),"gates":gates,"selected_operating_budget":budget}


def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--router-artifact-dir",required=True); parser.add_argument("--preflight-only",action="store_true"); args=parser.parse_args()
    contract,prereg,addendum=_validate_pre_run_contract(); prices=_fetch_prices(); v1,brrk,defensive=_load_frozen_targets(); preflight=_legacy_preflight(prices,brrk); floors,capacity_file,capacity_sha=_capacity_floor_by_route(Path(args.router_artifact_dir)); native,proxy=_funding_block_maps(); matched_targets=construct_candidate_targets(brrk,defensive,1.0)
    if not np.allclose(matched_targets.to_numpy(),brrk.to_numpy(),rtol=0,atol=1e-12): raise RuntimeError("cap1 identity failed")
    if args.preflight_only:
        print("LEVERAGE-0040 preflight-only PASS: baseline/data/cap1/artifact inputs valid; cap>1 not evaluated."); print(f"price_frame_sha256={_dataframe_sha256(prices)}"); print(f"router_vwap_slippage_sha256={capacity_sha}"); return

    legacy={cost:simulate_legacy_path(brrk,prices,start=FULL_START,end=FULL_END,cost_bps=cost) for cost in COST_GRID}; matched={cost:simulate_p3_3_economic_path(matched_targets,prices,start=FULL_START,end=FULL_END,cost_bps=cost) for cost in COST_GRID}
    benchmarks={str(cost):{"btc_buy_and_hold":_costed_buy_hold(prices,{"BTC":1.0},FULL_START,FULL_END,cost),"four_asset_equal_weight_buy_and_hold":_costed_buy_hold(prices,{a:.25 for a in ASSETS},FULL_START,FULL_END,cost),"legacy_brrk":path_metrics(legacy[cost]),"matched_p3_3_cap1":path_metrics(matched[cost])} for cost in COST_GRID}
    matrix={}; pass_by_cap={}
    for cap in CAPS:
        targets=construct_candidate_targets(brrk,defensive,cap); paths={cost:simulate_p3_3_economic_path(targets,prices,start=FULL_START,end=FULL_END,cost_bps=cost) for cost in COST_GRID}; historical=_historical_stress(prices,paths[5.0],cap); gaps=_gap_stress(paths[5.0].held_weights,matched[5.0].held_weights); vol=_vol_stress(prices,targets,matched[5.0]); liq=_minimum_liquidation_distance(paths[5.0].held_weights,matched[5.0].held_weights); robust=_robustness(paths[5.0],matched[5.0],legacy[5.0]); boot=_bootstrap(paths[5.0],matched[5.0],legacy[5.0])
        if cap==1.0: funding={"role":"CAP1_COMPARATOR","pass":True}; degraded={"role":"CAP1_COMPARATOR","pass":True}; gate={"pass_pre_broad_region":True,"gates":{"identity_comparator":True},"selected_operating_budget":select_operating_budget([path_metrics(paths[5.0])["max_drawdown"]])}
        else:
            funding=_funding_panel(prices,targets,matched_targets,path_metrics(legacy[5.0]),native,proxy); degraded=_degraded(prices,targets,matched_targets,floors); gate=_candidate_gate(paths,matched,legacy,historical,gaps,vol,funding,degraded,liq,robust,boot); pass_by_cap[round(cap,2)]=gate["pass_pre_broad_region"]
        matrix[f"{cap:.2f}"]={"cap":cap,"price_only_metrics_by_cost_bps":{str(c):path_metrics(p) for c,p in paths.items()},"historical_stress":historical,"synthetic_gap_stress":gaps,"volatility_stress":vol,"funding_stress":funding,"degraded_execution":degraded,"liquidation":liq,"start_date_robustness":robust,"bootstrap":boot,"gate":gate}
    for cap in (1.1,1.2,1.3):
        row=matrix[f"{cap:.2f}"]; row["gate"]["broad_region_pass"]=broad_region_eligible(pass_by_cap,cap); row["gate"]["final_research_pass"]=row["gate"]["pass_pre_broad_region"] and row["gate"]["broad_region_pass"]
    passing=[matrix[f"{c:.2f}"] for c in (1.1,1.2,1.3) if matrix[f"{c:.2f}"]["gate"]["final_research_pass"]]; passing.sort(key=lambda r:(r["price_only_metrics_by_cost_bps"]["5.0"]["end_multiple"],r["price_only_metrics_by_cost_bps"]["5.0"]["calmar"],r["price_only_metrics_by_cost_bps"]["5.0"]["sharpe"],r["price_only_metrics_by_cost_bps"]["5.0"]["max_drawdown"],-r["price_only_metrics_by_cost_bps"]["5.0"]["turnover"],-r["cap"]),reverse=True)
    if passing:
        sel=passing[0]; sc=float(sel["cap"]); lower=[c for c in CAPS if 1<=c<sc]; decision={"status":"RESEARCH_PROMOTION_CANDIDATE_NOT_PRODUCTION_AUTHORIZED","selected_research_cap":sc,"selected_operating_max_drawdown_budget":sel["gate"]["selected_operating_budget"],"prospective_live_cap_if_separately_authorized":min(max(lower),1.20) if lower else 1.0,"production_authorized":False}
    else: decision={"status":"NO_PROMOTION","selected_research_cap":None,"selected_operating_max_drawdown_budget":None,"prospective_live_cap_if_separately_authorized":None,"production_authorized":False}
    result={"schema_version":1,"study_id":"LEVERAGE-0040","status":"ONE_TIME_PREREGISTERED_STUDY_COMPLETE","production_authorized":False,"input_evidence":{"implementation_contract_sha256":_sha256_bytes(CONTRACT_PATH.read_bytes()),"preregistration_sha256":_sha256_bytes(PREREG_PATH.read_bytes()),"pre_run_addendum_sha256":_sha256_bytes(ADDENDUM_PATH.read_bytes()),"published_weights_blob_sha":"2f6c8d3a8c25d3cafeaa0128f1c425dac248370b","price_frame_sha256":_dataframe_sha256(prices),"funding_blocks_sha256":_sha256_bytes(FUNDING_PATH.read_bytes()),"router_vwap_slippage_sha256":capacity_sha,"router_capacity_floor_usd":{f"{a}:{m}":v for (a,m),v in floors.items()}},"preflight":preflight,"benchmarks":benchmarks,"candidate_matrix":matrix,"selection":decision,"constraints":{"production_authorized_components":[],"post_result_retuning_allowed":False,"search_caps":[1.0,1.1,1.2,1.3],"catastrophic_drawdown_boundary":.70}}
    RESULT_DIR.mkdir(parents=True,exist_ok=True); safe=_json_safe(result); summary=RESULT_DIR/"summary.json"; summary.write_text(json.dumps(safe,indent=2,sort_keys=True),encoding="utf-8"); (RESULT_DIR/"router_data_0004_vwap_slippage.csv").write_bytes(capacity_file.read_bytes()); rows=[]
    for cap in CAPS:
        row=safe["candidate_matrix"][f"{cap:.2f}"]; m=row["price_only_metrics_by_cost_bps"]["5.0"]; g=row["gate"]; rows.append({"cap":cap,"cagr_5bps":m["cagr"],"max_drawdown_5bps":m["max_drawdown"],"sharpe_5bps":m["sharpe"],"calmar_5bps":m["calmar"],"turnover_5bps":m["turnover"],"pass_pre_broad_region":g.get("pass_pre_broad_region"),"broad_region_pass":g.get("broad_region_pass"),"final_research_pass":g.get("final_research_pass"),"operating_budget":g.get("selected_operating_budget")})
    pd.DataFrame(rows).to_csv(RESULT_DIR/"candidate_table.csv",index=False,float_format="%.12f"); digest=_sha256_bytes(summary.read_bytes()); (RESULT_DIR/"summary.sha256").write_text(digest+"\n",encoding="utf-8"); print("LEVERAGE-0040 one-time study completed; immutable result files written."); print(f"summary_sha256={digest}")


if __name__ == "__main__": main()
