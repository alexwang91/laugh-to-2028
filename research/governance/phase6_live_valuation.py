from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

from .validate import repo_root_from_module

CONTRACT_RELATIVE_PATH = Path("research/governance/phase6_live_valuation_contract.json")
INSTRUMENT_REGISTRY_RELATIVE_PATH = Path("config/instrument_registry.json")
CANONICAL_ASSETS = ("BTC", "ETH", "SOL", "BNB")
SPOT_TOKEN_TO_ASSET = {"UBTC": "BTC", "UETH": "ETH", "USOL": "SOL"}


class Phase6ValuationError(RuntimeError):
    pass


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise Phase6ValuationError(f"{path} must contain a JSON object")
    return value


def _finite(value: object, *, field: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise Phase6ValuationError(f"{field} must be numeric") from exc
    if not math.isfinite(number):
        raise Phase6ValuationError(f"{field} must be finite")
    return number


def validate_valuation_contract(
    contract: Mapping[str, Any], *, instrument_registry: Mapping[str, Any]
) -> dict[str, Any]:
    if contract.get("schema_version") != 1:
        raise Phase6ValuationError("unsupported valuation contract schema")
    if contract.get("contract_id") != "PHASE6-LIVE-VALUATION-V1":
        raise Phase6ValuationError("unexpected valuation contract id")
    if contract.get("status") != "FROZEN_STANDARD_MODE_ONLY_NO_ACCOUNT_BOUND":
        raise Phase6ValuationError("valuation contract status drift")
    for field in ("production_authorized", "signature_authorized", "order_submission_authorized"):
        if contract.get(field) is not False:
            raise Phase6ValuationError(f"{field} must remain false")

    mode = contract.get("supported_account_mode", {})
    if mode.get("required_value") != "disabled":
        raise Phase6ValuationError("V1 must support only explicit Standard/disabled abstraction")
    if set(mode.get("unsupported_values_fail_closed", [])) != {
        "unifiedAccount", "portfolioMargin", "default", "dexAbstraction"
    }:
        raise Phase6ValuationError("unsupported account-mode set drift")

    if tuple(contract.get("canonical_assets", [])) != CANONICAL_ASSETS:
        raise Phase6ValuationError("canonical valuation asset set drift")
    if contract.get("quote_asset") != "USDC":
        raise Phase6ValuationError("quote asset must remain USDC")

    assets = instrument_registry.get("assets", {})
    expected = {"BTC": "UBTC", "ETH": "UETH", "SOL": "USOL", "BNB": None}
    if contract.get("spot_identity", {}).get("identity_authority") != str(INSTRUMENT_REGISTRY_RELATIVE_PATH):
        raise Phase6ValuationError("spot identity authority drift")
    for asset, token in expected.items():
        if contract.get("spot_identity", {}).get(asset) != token:
            raise Phase6ValuationError(f"valuation spot identity drift for {asset}")
        row = assets.get(asset, {})
        if asset == "BNB":
            if row.get("route_policy") != "PERP_ONLY_DEFAULT":
                raise Phase6ValuationError("BNB must remain perp-only")
        else:
            if row.get("spot", {}).get("hypercore_token_candidate") != token:
                raise Phase6ValuationError(f"instrument registry spot identity drift for {asset}")

    p3 = contract.get("p3_3_binding", {})
    if p3.get("control_version") != "P3.3-L1-BAND-V1" or p3.get("economic_parameter_change") is not False:
        raise Phase6ValuationError("P3.3 binding drift")

    return {
        "contract_id": contract["contract_id"],
        "status": contract["status"],
        "supported_user_abstraction": "disabled",
        "canonical_assets": list(CANONICAL_ASSETS),
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
    }


def contract_snapshot(root: Path | None = None) -> dict[str, Any]:
    repo_root = Path(root or repo_root_from_module())
    return validate_valuation_contract(
        _load_json(repo_root / CONTRACT_RELATIVE_PATH),
        instrument_registry=_load_json(repo_root / INSTRUMENT_REGISTRY_RELATIVE_PATH),
    )


def derive_standard_account_valuation(
    *,
    user_abstraction: str,
    spot_state: Mapping[str, Any],
    perp_state: Mapping[str, Any],
    spot_mark_by_token: Mapping[str, float],
) -> dict[str, Any]:
    """Pure Standard-mode mapping from exact read-only states into canonical P3.3 inputs."""
    if user_abstraction != "disabled":
        raise Phase6ValuationError("only explicit Standard/disabled account abstraction is supported")

    if set(spot_mark_by_token) != set(SPOT_TOKEN_TO_ASSET):
        raise Phase6ValuationError("spot mark identity set must be exactly UBTC/UETH/USOL")
    marks = {
        token: _finite(value, field=f"spot_mark_by_token.{token}")
        for token, value in spot_mark_by_token.items()
    }
    if any(value <= 0 for value in marks.values()):
        raise Phase6ValuationError("spot marks must be strictly positive")

    current = {asset: 0.0 for asset in CANONICAL_ASSETS}
    seen_perp: set[str] = set()
    positions = perp_state.get("assetPositions", [])
    if not isinstance(positions, list):
        raise Phase6ValuationError("assetPositions must be a list")
    for item in positions:
        if not isinstance(item, Mapping) or not isinstance(item.get("position"), Mapping):
            raise Phase6ValuationError("malformed perp position")
        position = item["position"]
        coin = str(position.get("coin", "")).upper()
        szi = _finite(position.get("szi"), field=f"perp.{coin}.szi")
        position_value = _finite(position.get("positionValue"), field=f"perp.{coin}.positionValue")
        if position_value < 0:
            raise Phase6ValuationError("perp positionValue must be nonnegative")
        if coin not in CANONICAL_ASSETS:
            if szi != 0 or position_value != 0:
                raise Phase6ValuationError(f"noncanonical perp position is not allowed: {coin}")
            continue
        if coin in seen_perp:
            raise Phase6ValuationError(f"duplicate perp position identity: {coin}")
        seen_perp.add(coin)
        if szi == 0:
            if position_value != 0:
                raise Phase6ValuationError(f"zero-size perp has nonzero positionValue: {coin}")
            signed_notional = 0.0
        else:
            signed_notional = math.copysign(position_value, szi)
        current[coin] += signed_notional

    margin_summary = perp_state.get("marginSummary")
    if not isinstance(margin_summary, Mapping):
        raise Phase6ValuationError("perp marginSummary is required")
    perp_equity = _finite(margin_summary.get("accountValue"), field="marginSummary.accountValue")

    balances = spot_state.get("balances", [])
    if not isinstance(balances, list):
        raise Phase6ValuationError("spot balances must be a list")
    seen_spot: set[str] = set()
    spot_nav = 0.0
    for balance in balances:
        if not isinstance(balance, Mapping):
            raise Phase6ValuationError("malformed spot balance")
        coin = str(balance.get("coin", "")).upper()
        total = _finite(balance.get("total"), field=f"spot.{coin}.total")
        hold = _finite(balance.get("hold", 0.0), field=f"spot.{coin}.hold")
        if total < 0 or hold < 0 or hold > total:
            raise Phase6ValuationError(f"invalid spot total/hold for {coin}")
        if coin in seen_spot:
            raise Phase6ValuationError(f"duplicate spot balance identity: {coin}")
        seen_spot.add(coin)
        if coin == "USDC":
            spot_nav += total
            continue
        asset = SPOT_TOKEN_TO_ASSET.get(coin)
        if asset is None:
            if total != 0:
                raise Phase6ValuationError(f"noncanonical spot token is not allowed: {coin}")
            continue
        value = total * marks[coin]
        spot_nav += value
        current[asset] += value

    account_equity = perp_equity + spot_nav
    if not math.isfinite(account_equity) or account_equity <= 0:
        raise Phase6ValuationError("derived account_equity_usd must be finite and strictly positive")
    if any(not math.isfinite(value) for value in current.values()):
        raise Phase6ValuationError("derived current position notional is nonfinite")

    return {
        "account_equity_usd": account_equity,
        "current_positions_notional_usd": current,
        "perp_account_equity_usd": perp_equity,
        "spot_mark_to_market_usd": spot_nav,
        "user_abstraction": user_abstraction,
        "valuation_contract_id": "PHASE6-LIVE-VALUATION-V1",
    }


def main() -> int:
    print(json.dumps(contract_snapshot(), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
