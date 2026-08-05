from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from .product_config import load_product_config


TRUE_VALUES = {"1", "true", "yes", "on"}


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in TRUE_VALUES


def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    return float(value)


@dataclass(frozen=True)
class Settings:
    network: str
    trading_mode: str
    coin: str
    master_address: Optional[str]
    vault_address: Optional[str]
    api_private_key: Optional[str]
    external_spot_btc_qty: float
    external_cash_usd: float
    rebalance_band: float
    min_trade_usd: float
    normal_beta_cap: float
    hard_beta_cap: float
    allow_strong_beta: bool
    max_platform_leverage: int
    max_slippage_bps: float
    request_timeout_seconds: float
    candle_lookback_days: int
    cron_secret: Optional[str]
    live_trading_confirmation: Optional[str]
    telegram_bot_token: Optional[str]
    telegram_chat_id: Optional[str]

    @property
    def api_url(self) -> str:
        if self.network == "mainnet":
            return "https://api.hyperliquid.xyz"
        return "https://api.hyperliquid-testnet.xyz"

    @property
    def account_address(self) -> Optional[str]:
        return self.vault_address or self.master_address

    @property
    def can_trade(self) -> bool:
        return self.trading_mode == "trade"

    @classmethod
    def from_env(cls) -> "Settings":
        product = load_product_config()
        settings = cls(
            network=os.getenv("HL_NETWORK", "testnet").strip().lower(),
            trading_mode=os.getenv("TRADING_MODE", "shadow").strip().lower(),
            coin=os.getenv("COIN", product.long_universe[0]).strip().upper(),
            master_address=(os.getenv("HL_MASTER_ADDRESS") or "").strip() or None,
            vault_address=(os.getenv("HL_VAULT_ADDRESS") or "").strip() or None,
            api_private_key=(os.getenv("HL_API_PRIVATE_KEY") or "").strip() or None,
            external_spot_btc_qty=_env_float("EXTERNAL_SPOT_BTC_QTY", 0.0),
            external_cash_usd=_env_float("EXTERNAL_CASH_USD", 0.0),
            rebalance_band=_env_float("REBALANCE_BAND", 0.05),
            min_trade_usd=_env_float("MIN_TRADE_USD", 100.0),
            normal_beta_cap=_env_float("NORMAL_BETA_CAP", 1.30),
            hard_beta_cap=_env_float("HARD_BETA_CAP", 1.50),
            allow_strong_beta=_env_bool("ALLOW_STRONG_BETA", False),
            max_platform_leverage=int(_env_float("MAX_PLATFORM_LEVERAGE", 2.0)),
            max_slippage_bps=_env_float("MAX_SLIPPAGE_BPS", 15.0),
            request_timeout_seconds=_env_float("REQUEST_TIMEOUT_SECONDS", 15.0),
            candle_lookback_days=int(_env_float("CANDLE_LOOKBACK_DAYS", 450.0)),
            cron_secret=(os.getenv("CRON_SECRET") or "").strip() or None,
            live_trading_confirmation=(os.getenv("LIVE_TRADING_CONFIRMATION") or "").strip() or None,
            telegram_bot_token=(os.getenv("TELEGRAM_BOT_TOKEN") or "").strip() or None,
            telegram_chat_id=(os.getenv("TELEGRAM_CHAT_ID") or "").strip() or None,
        )
        settings.validate()
        return settings

    def validate(self) -> None:
        product = load_product_config()
        if product.primary_venue != "hyperliquid":
            raise ValueError("This execution service requires the canonical Hyperliquid venue")
        if self.network not in {"testnet", "mainnet"}:
            raise ValueError("HL_NETWORK must be testnet or mainnet")
        if self.trading_mode not in {"shadow", "trade"}:
            raise ValueError("TRADING_MODE must be shadow or trade")
        if self.coin not in product.long_universe:
            raise ValueError("COIN is outside the canonical BRRK long universe")
        if self.coin != "BTC":
            raise ValueError(
                "The current execution implementation is BTC-only even though the canonical product universe is BTC/ETH/SOL/BNB"
            )
        if not 0.0 < self.rebalance_band <= 0.5:
            raise ValueError("REBALANCE_BAND must be in (0, 0.5]")
        if not 0.0 < self.normal_beta_cap <= self.hard_beta_cap:
            raise ValueError("Beta caps are inconsistent")
        if self.hard_beta_cap > 1.5:
            raise ValueError("HARD_BETA_CAP cannot exceed the validated legacy 1.5 research limit")
        if self.max_platform_leverage > 2:
            raise ValueError("MAX_PLATFORM_LEVERAGE cannot exceed 2 in this version")
        if self.external_spot_btc_qty < 0 or self.external_cash_usd < 0:
            raise ValueError("External asset values cannot be negative")
        if self.can_trade:
            if not self.master_address:
                raise ValueError("HL_MASTER_ADDRESS is required in trade mode")
            if not self.api_private_key:
                raise ValueError("HL_API_PRIVATE_KEY is required in trade mode")
            if self.network == "mainnet" and self.live_trading_confirmation != "ENABLE_MAINNET_LIVE_TRADING":
                raise ValueError(
                    "Mainnet trade mode requires LIVE_TRADING_CONFIRMATION=ENABLE_MAINNET_LIVE_TRADING"
                )
