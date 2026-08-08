from __future__ import annotations

"""Canonical production-authority boundary for legacy execution paths.

The legacy BTC-only service predates the Phase 6/7 canonical BRRK integration and
must never infer launch authority from TRADING_MODE alone.  Until a future
explicit production-integration change wires verified Phase-6 elapsed evidence,
Phase-7 checklist evidence and an owner approval record into the canonical
multi-asset service, normal risk-increasing transitions through the legacy
service are denied unconditionally.

Risk-reducing transitions remain classified separately by the execution service
so emergency/reduction capability is preserved.
"""

LEGACY_NORMAL_SERVICE_NEW_RISK_AUTHORIZED = False
PRODUCTION_GROSS_CAP = 1.0
PRODUCTION_AUTHORIZED_COMPONENTS: tuple[str, ...] = ()


def legacy_normal_service_new_risk_authorized() -> bool:
    """Return the frozen current authority state for the legacy normal service."""
    return LEGACY_NORMAL_SERVICE_NEW_RISK_AUTHORIZED
