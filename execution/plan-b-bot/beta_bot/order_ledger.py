from __future__ import annotations

import json
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable

from .order_identity import OrderIdentity


SCHEMA_VERSION = 1
KNOWN_EXCHANGE_STATUSES = {
    "filled",
    "open",
    "canceled",
    "triggered",
    "rejected",
    "marginCanceled",
}
TERMINAL_EXCHANGE_STATUSES = {"filled", "canceled", "rejected", "marginCanceled"}
FILL_LIMIT = 2000


class LedgerError(RuntimeError):
    """Persistent execution ledger could not be trusted."""


class LedgerUncertainState(LedgerError):
    """Exchange/local truth cannot be reconciled safely."""


def _now_ms() -> int:
    return int(time.time() * 1000)


def _json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def _as_float(value: Any, default: float | None = None) -> float | None:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise LedgerUncertainState(f"Invalid numeric exchange value: {value!r}") from exc


@dataclass(frozen=True)
class LedgerIntent:
    identity: OrderIdentity
    route_action: str
    submitted_quantity: float
    submitted_order_parameters: dict[str, Any]


class OrderLedger:
    """SQLite-backed execution truth keyed by deterministic Hyperliquid CLOID.

    The configured file is assumed to live on operator-provided durable storage.
    Settings validates that deployment precondition before trade mode is allowed.
    """

    def __init__(self, path: str):
        if not path or not path.strip():
            raise LedgerError("ORDER_LEDGER_PATH is required")
        self.path = path.strip()
        if self.path != ":memory:":
            try:
                Path(self.path).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                raise LedgerError(f"Cannot create ledger directory for {self.path}: {exc}") from exc
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        try:
            conn = sqlite3.connect(self.path, timeout=5.0)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA busy_timeout = 5000")
            conn.execute("PRAGMA synchronous = FULL")
            return conn
        except sqlite3.Error as exc:
            raise LedgerError(f"Cannot open order ledger {self.path}: {exc}") from exc

    def _initialize(self) -> None:
        try:
            with self._connect() as conn:
                # DELETE keeps committed truth in the configured database file rather
                # than depending on a long-lived WAL sidecar surviving separately.
                conn.execute("PRAGMA journal_mode = DELETE")
                check = conn.execute("PRAGMA quick_check").fetchone()
                if not check or check[0] != "ok":
                    raise LedgerError(f"SQLite quick_check failed: {check[0] if check else 'no result'}")
                conn.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS ledger_metadata (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL
                    );
                    INSERT OR IGNORE INTO ledger_metadata(key, value)
                    VALUES ('schema_version', '1');

                    CREATE TABLE IF NOT EXISTS orders (
                        cloid TEXT PRIMARY KEY,
                        identity_schema_version INTEGER NOT NULL,
                        strategy_release TEXT NOT NULL,
                        decision_timestamp_ms INTEGER NOT NULL,
                        asset TEXT NOT NULL,
                        side TEXT NOT NULL,
                        economic_intent TEXT NOT NULL,
                        target_revision TEXT NOT NULL,
                        route_action TEXT NOT NULL,
                        submitted_quantity REAL NOT NULL CHECK(submitted_quantity > 0),
                        submitted_order_parameters_json TEXT NOT NULL,
                        exchange_oid TEXT,
                        submission_attempt_timestamp_ms INTEGER,
                        submission_response_timestamp_ms INTEGER,
                        submission_response_status TEXT,
                        submission_response_json TEXT,
                        current_status TEXT NOT NULL,
                        last_exchange_status TEXT,
                        last_exchange_payload_json TEXT,
                        fill_quantity REAL NOT NULL DEFAULT 0,
                        average_fill_price REAL,
                        fees REAL NOT NULL DEFAULT 0,
                        remaining_quantity REAL NOT NULL,
                        cancel_reason TEXT,
                        reject_reason TEXT,
                        terminal_status TEXT,
                        last_reconciliation_timestamp_ms INTEGER,
                        created_at_ms INTEGER NOT NULL,
                        updated_at_ms INTEGER NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS status_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cloid TEXT NOT NULL REFERENCES orders(cloid),
                        event_timestamp_ms INTEGER NOT NULL,
                        source TEXT NOT NULL,
                        status TEXT NOT NULL,
                        detail_json TEXT NOT NULL
                    );
                    CREATE INDEX IF NOT EXISTS idx_status_history_cloid
                    ON status_history(cloid, id);

                    CREATE TABLE IF NOT EXISTS fill_events (
                        tid TEXT PRIMARY KEY,
                        cloid TEXT NOT NULL REFERENCES orders(cloid),
                        exchange_oid TEXT NOT NULL,
                        fill_timestamp_ms INTEGER NOT NULL,
                        price REAL NOT NULL,
                        quantity REAL NOT NULL CHECK(quantity > 0),
                        fee REAL NOT NULL,
                        fee_token TEXT,
                        side TEXT,
                        raw_json TEXT NOT NULL
                    );
                    CREATE INDEX IF NOT EXISTS idx_fill_events_cloid
                    ON fill_events(cloid, fill_timestamp_ms, tid);
                    """
                )
                row = conn.execute(
                    "SELECT value FROM ledger_metadata WHERE key='schema_version'"
                ).fetchone()
                if not row or int(row[0]) != SCHEMA_VERSION:
                    raise LedgerError(
                        f"Unsupported order-ledger schema version: {row[0] if row else None}"
                    )
        except LedgerError:
            raise
        except sqlite3.Error as exc:
            raise LedgerError(f"Order ledger initialization failed: {exc}") from exc

    @staticmethod
    def _history(
        conn: sqlite3.Connection,
        cloid: str,
        source: str,
        status: str,
        detail: Any,
        event_timestamp_ms: int | None = None,
    ) -> None:
        conn.execute(
            """INSERT INTO status_history
               (cloid, event_timestamp_ms, source, status, detail_json)
               VALUES (?, ?, ?, ?, ?)""",
            (cloid, event_timestamp_ms or _now_ms(), source, status, _json(detail)),
        )

    def get_order(self, cloid: str) -> dict[str, Any] | None:
        try:
            with self._connect() as conn:
                row = conn.execute("SELECT * FROM orders WHERE cloid=?", (cloid,)).fetchone()
                return dict(row) if row else None
        except sqlite3.Error as exc:
            raise LedgerError(f"Order ledger read failed: {exc}") from exc

    def list_status_history(self, cloid: str) -> list[dict[str, Any]]:
        try:
            with self._connect() as conn:
                rows = conn.execute(
                    "SELECT * FROM status_history WHERE cloid=? ORDER BY id", (cloid,)
                ).fetchall()
                return [dict(row) for row in rows]
        except sqlite3.Error as exc:
            raise LedgerError(f"Order status-history read failed: {exc}") from exc

    def list_fill_events(self, cloid: str) -> list[dict[str, Any]]:
        try:
            with self._connect() as conn:
                rows = conn.execute(
                    "SELECT * FROM fill_events WHERE cloid=? ORDER BY fill_timestamp_ms, tid", (cloid,)
                ).fetchall()
                return [dict(row) for row in rows]
        except sqlite3.Error as exc:
            raise LedgerError(f"Order fill-history read failed: {exc}") from exc

    def record_intent(self, intent: LedgerIntent) -> dict[str, Any]:
        identity = intent.identity
        quantity = float(intent.submitted_quantity)
        if quantity <= 0:
            raise LedgerError("submitted_quantity must be positive")
        params = _json(intent.submitted_order_parameters)
        now = _now_ms()
        try:
            with self._connect() as conn:
                existing = conn.execute(
                    "SELECT * FROM orders WHERE cloid=?", (identity.cloid,)
                ).fetchone()
                if existing is None:
                    conn.execute(
                        """INSERT INTO orders (
                            cloid, identity_schema_version, strategy_release,
                            decision_timestamp_ms, asset, side, economic_intent,
                            target_revision, route_action, submitted_quantity,
                            submitted_order_parameters_json, current_status,
                            remaining_quantity, created_at_ms, updated_at_ms
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'intent_recorded', ?, ?, ?)""",
                        (
                            identity.cloid,
                            identity.schema_version,
                            identity.release_id,
                            identity.decision_timestamp_ms,
                            identity.asset,
                            identity.side,
                            identity.intent,
                            identity.target_revision,
                            intent.route_action,
                            quantity,
                            params,
                            quantity,
                            now,
                            now,
                        ),
                    )
                    self._history(
                        conn,
                        identity.cloid,
                        "local",
                        "intent_recorded",
                        {
                            "route_action": intent.route_action,
                            "submitted_quantity": quantity,
                            "submitted_order_parameters": intent.submitted_order_parameters,
                        },
                        now,
                    )
                else:
                    expected = {
                        "identity_schema_version": identity.schema_version,
                        "strategy_release": identity.release_id,
                        "decision_timestamp_ms": identity.decision_timestamp_ms,
                        "asset": identity.asset,
                        "side": identity.side,
                        "economic_intent": identity.intent,
                        "target_revision": identity.target_revision,
                        "route_action": intent.route_action,
                        "submitted_quantity": quantity,
                        "submitted_order_parameters_json": params,
                    }
                    mismatches = {
                        key: {"existing": existing[key], "requested": value}
                        for key, value in expected.items()
                        if existing[key] != value
                    }
                    if mismatches:
                        self._history(
                            conn,
                            identity.cloid,
                            "local",
                            "cloid_uniqueness_conflict",
                            mismatches,
                            now,
                        )
                        conn.commit()
                        raise LedgerUncertainState(
                            f"CLOID {identity.cloid} already exists with different economic intent"
                        )
                row = conn.execute(
                    "SELECT * FROM orders WHERE cloid=?", (identity.cloid,)
                ).fetchone()
                return dict(row)
        except LedgerError:
            raise
        except sqlite3.Error as exc:
            raise LedgerError(f"Could not persist order intent: {exc}") from exc

    def record_submission_attempt(self, cloid: str, timestamp_ms: int | None = None) -> None:
        timestamp = timestamp_ms or _now_ms()
        try:
            with self._connect() as conn:
                row = conn.execute("SELECT * FROM orders WHERE cloid=?", (cloid,)).fetchone()
                if not row:
                    raise LedgerError(f"Cannot record submission attempt without intent: {cloid}")
                if row["submission_attempt_timestamp_ms"] is not None:
                    raise LedgerUncertainState(
                        f"CLOID {cloid} already has a prior submission attempt; blind retry is forbidden"
                    )
                conn.execute(
                    """UPDATE orders
                       SET submission_attempt_timestamp_ms=?,
                           current_status='submission_attempt_recorded', updated_at_ms=?
                       WHERE cloid=?""",
                    (timestamp, timestamp, cloid),
                )
                self._history(conn, cloid, "local", "submission_attempt_recorded", {}, timestamp)
        except LedgerError:
            raise
        except sqlite3.Error as exc:
            raise LedgerError(f"Could not persist submission attempt: {exc}") from exc

    def record_submission_unknown(self, cloid: str, error: BaseException | str) -> None:
        now = _now_ms()
        detail = {
            "error": str(error),
            "error_type": type(error).__name__ if not isinstance(error, str) else "str",
        }
        try:
            with self._connect() as conn:
                conn.execute(
                    "UPDATE orders SET current_status='submission_unknown', updated_at_ms=? WHERE cloid=?",
                    (now, cloid),
                )
                self._history(conn, cloid, "local", "submission_unknown", detail, now)
        except sqlite3.Error as exc:
            raise LedgerError(f"Could not persist unknown submission state: {exc}") from exc

    def record_submission_response(
        self,
        cloid: str,
        response: dict[str, Any],
        response_status: str,
        *,
        exchange_oid: Any = None,
        reject_reason: str | None = None,
    ) -> None:
        now = _now_ms()
        try:
            with self._connect() as conn:
                row = conn.execute("SELECT * FROM orders WHERE cloid=?", (cloid,)).fetchone()
                if not row or row["submission_attempt_timestamp_ms"] is None:
                    raise LedgerError(f"Submission response has no durable attempt record: {cloid}")
                terminal = "rejected" if response_status == "rejected" else None
                conn.execute(
                    """UPDATE orders SET
                        exchange_oid=COALESCE(?, exchange_oid),
                        submission_response_timestamp_ms=?, submission_response_status=?,
                        submission_response_json=?, current_status=?,
                        reject_reason=COALESCE(?, reject_reason),
                        terminal_status=COALESCE(?, terminal_status), updated_at_ms=?
                       WHERE cloid=?""",
                    (
                        str(exchange_oid) if exchange_oid is not None else None,
                        now,
                        response_status,
                        _json(response),
                        f"submission_response:{response_status}",
                        reject_reason,
                        terminal,
                        now,
                        cloid,
                    ),
                )
                self._history(
                    conn,
                    cloid,
                    "exchange_submission",
                    response_status,
                    {
                        "exchange_oid": exchange_oid,
                        "response": response,
                        "reject_reason": reject_reason,
                    },
                    now,
                )
        except LedgerError:
            raise
        except sqlite3.Error as exc:
            raise LedgerError(f"Could not persist submission response: {exc}") from exc

    def record_reconciliation_uncertainty(
        self, cloid: str, reason: str, detail: Any = None
    ) -> None:
        now = _now_ms()
        try:
            with self._connect() as conn:
                row = conn.execute("SELECT cloid FROM orders WHERE cloid=?", (cloid,)).fetchone()
                if not row:
                    raise LedgerError(f"Cannot audit uncertainty for missing CLOID: {cloid}")
                conn.execute(
                    """UPDATE orders SET current_status='reconciliation_uncertain',
                       last_reconciliation_timestamp_ms=?, updated_at_ms=? WHERE cloid=?""",
                    (now, now, cloid),
                )
                self._history(
                    conn,
                    cloid,
                    "reconciliation",
                    "reconciliation_uncertain",
                    {"reason": reason, "detail": detail},
                    now,
                )
        except LedgerError:
            raise
        except sqlite3.Error as exc:
            raise LedgerError(f"Could not persist reconciliation uncertainty: {exc}") from exc

    def record_exchange_discovery(self, cloid: str, response: dict[str, Any]) -> str:
        """Persist a known exchange order before full fill reconciliation."""
        if response.get("status") != "order":
            self.record_reconciliation_uncertainty(cloid, "non_order_exchange_discovery", response)
            raise LedgerUncertainState(f"Cannot record non-order discovery: {response}")
        envelope = response.get("order")
        if not isinstance(envelope, dict):
            self.record_reconciliation_uncertainty(cloid, "malformed_order_status_envelope", response)
            raise LedgerUncertainState(f"Malformed orderStatus envelope: {response}")
        order = envelope.get("order")
        status = envelope.get("status")
        if not isinstance(order, dict) or not isinstance(status, str) or order.get("oid") is None:
            self.record_reconciliation_uncertainty(cloid, "malformed_order_status_payload", response)
            raise LedgerUncertainState(f"Malformed orderStatus payload: {response}")
        if status not in KNOWN_EXCHANGE_STATUSES:
            self.record_reconciliation_uncertainty(
                cloid, "unknown_exchange_status", {"status": status, "response": response}
            )
            raise LedgerUncertainState(f"Unknown Hyperliquid order status: {status}")
        oid = str(order["oid"])
        try:
            remaining = _as_float(order.get("sz"))
        except LedgerUncertainState as exc:
            self.record_reconciliation_uncertainty(cloid, "invalid_remaining_quantity", str(exc))
            raise
        now = _now_ms()
        try:
            with self._connect() as conn:
                row = conn.execute("SELECT * FROM orders WHERE cloid=?", (cloid,)).fetchone()
                if not row:
                    raise LedgerError(f"Exchange discovery has no local intent record: {cloid}")
                existing_oid = row["exchange_oid"]
                if existing_oid is not None and str(existing_oid) != oid:
                    self._history(
                        conn,
                        cloid,
                        "reconciliation",
                        "exchange_oid_conflict",
                        {"local_oid": existing_oid, "exchange_oid": oid},
                        now,
                    )
                    conn.commit()
                    raise LedgerUncertainState(
                        f"CLOID {cloid} maps to conflicting exchange OIDs: {existing_oid} vs {oid}"
                    )
                conn.execute(
                    """UPDATE orders SET exchange_oid=?, current_status=?,
                       last_exchange_status=?, last_exchange_payload_json=?,
                       remaining_quantity=COALESCE(?, remaining_quantity),
                       last_reconciliation_timestamp_ms=?, updated_at_ms=? WHERE cloid=?""",
                    (
                        oid,
                        f"exchange_observed:{status}",
                        status,
                        _json(response),
                        remaining,
                        now,
                        now,
                        cloid,
                    ),
                )
                self._history(
                    conn,
                    cloid,
                    "exchange_lookup",
                    status,
                    {"exchange_oid": oid, "full_fill_reconciliation_pending": True},
                    now,
                )
                return status
        except LedgerError:
            raise
        except sqlite3.Error as exc:
            raise LedgerError(f"Could not persist exchange discovery: {exc}") from exc

    def unresolved_orders(self) -> list[dict[str, Any]]:
        try:
            with self._connect() as conn:
                rows = conn.execute(
                    "SELECT * FROM orders WHERE terminal_status IS NULL ORDER BY created_at_ms, cloid"
                ).fetchall()
                return [dict(row) for row in rows]
        except sqlite3.Error as exc:
            raise LedgerError(f"Could not enumerate unresolved orders: {exc}") from exc

    def blocking_unresolved_orders(
        self, *, excluding_cloid: str | None = None
    ) -> list[dict[str, Any]]:
        # A recovered exchange order is blocking even when this local database never
        # recorded its original submission attempt. Exchange existence is sufficient
        # evidence that another economic order must not be allowed through blindly.
        query = """SELECT * FROM orders
                   WHERE terminal_status IS NULL
                     AND (submission_attempt_timestamp_ms IS NOT NULL OR exchange_oid IS NOT NULL)"""
        params: list[Any] = []
        if excluding_cloid is not None:
            query += " AND cloid != ?"
            params.append(excluding_cloid)
        query += " ORDER BY created_at_ms, cloid"
        try:
            with self._connect() as conn:
                rows = conn.execute(query, params).fetchall()
                return [dict(row) for row in rows]
        except sqlite3.Error as exc:
            raise LedgerError(f"Could not enumerate blocking unresolved orders: {exc}") from exc

    def apply_exchange_truth(
        self,
        cloid: str,
        order_status_response: dict[str, Any],
        fills: Iterable[dict[str, Any]],
        *,
        reconciled_at_ms: int | None = None,
    ) -> dict[str, Any]:
        now = reconciled_at_ms or _now_ms()
        if order_status_response.get("status") != "order":
            raise LedgerUncertainState(
                f"Cannot apply non-order exchange response: {order_status_response}"
            )
        envelope = order_status_response.get("order")
        if not isinstance(envelope, dict):
            raise LedgerUncertainState(f"Malformed orderStatus envelope: {order_status_response}")
        order = envelope.get("order")
        status = envelope.get("status")
        status_timestamp = envelope.get("statusTimestamp")
        if not isinstance(order, dict) or not isinstance(status, str):
            raise LedgerUncertainState(f"Malformed orderStatus payload: {order_status_response}")
        if status not in KNOWN_EXCHANGE_STATUSES:
            raise LedgerUncertainState(f"Unknown Hyperliquid order status: {status}")
        oid = order.get("oid")
        if oid is None:
            raise LedgerUncertainState(f"orderStatus missing oid: {order_status_response}")
        exchange_oid = str(oid)
        remaining = _as_float(order.get("sz"))
        orig_sz = _as_float(order.get("origSz"))
        normalized_fills = [fill for fill in fills if str(fill.get("oid")) == exchange_oid]

        try:
            with self._connect() as conn:
                row = conn.execute("SELECT * FROM orders WHERE cloid=?", (cloid,)).fetchone()
                if not row:
                    raise LedgerError(f"Exchange truth has no local intent record: {cloid}")

                submission_status = row["submission_response_status"]
                previous_exchange_status = row["last_exchange_status"]
                if submission_status in TERMINAL_EXCHANGE_STATUSES and submission_status != status:
                    self._history(
                        conn,
                        cloid,
                        "reconciliation",
                        "exchange_state_conflict",
                        {"local_submission_status": submission_status, "exchange_status": status},
                        now,
                    )
                elif previous_exchange_status and previous_exchange_status != status:
                    self._history(
                        conn,
                        cloid,
                        "reconciliation",
                        "exchange_status_transition",
                        {"previous": previous_exchange_status, "exchange_status": status},
                        now,
                    )

                existing_oid = row["exchange_oid"]
                if existing_oid is not None and str(existing_oid) != exchange_oid:
                    self._history(
                        conn,
                        cloid,
                        "reconciliation",
                        "exchange_oid_conflict",
                        {"local_oid": existing_oid, "exchange_oid": exchange_oid},
                        now,
                    )
                    conn.commit()
                    raise LedgerUncertainState(
                        f"CLOID {cloid} maps to conflicting exchange OIDs: {existing_oid} vs {exchange_oid}"
                    )

                for fill in normalized_fills:
                    tid = fill.get("tid")
                    px = _as_float(fill.get("px"))
                    qty = _as_float(fill.get("sz"))
                    fee = _as_float(fill.get("fee"), 0.0)
                    fill_time = fill.get("time")
                    if tid is None or px is None or qty is None or qty <= 0 or fill_time is None:
                        raise LedgerUncertainState(
                            f"Malformed fill for oid {exchange_oid}: {fill}"
                        )
                    conn.execute(
                        """INSERT OR IGNORE INTO fill_events
                           (tid, cloid, exchange_oid, fill_timestamp_ms, price, quantity,
                            fee, fee_token, side, raw_json)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (
                            str(tid),
                            cloid,
                            exchange_oid,
                            int(fill_time),
                            px,
                            qty,
                            fee or 0.0,
                            fill.get("feeToken"),
                            fill.get("side"),
                            _json(fill),
                        ),
                    )

                aggregates = conn.execute(
                    """SELECT COALESCE(SUM(quantity),0) AS fill_qty,
                              CASE WHEN SUM(quantity) > 0
                                   THEN SUM(quantity * price) / SUM(quantity)
                                   ELSE NULL END AS avg_px,
                              COALESCE(SUM(fee),0) AS fees
                       FROM fill_events WHERE cloid=?""",
                    (cloid,),
                ).fetchone()
                fill_qty = float(aggregates["fill_qty"])
                avg_px = aggregates["avg_px"]
                fees = float(aggregates["fees"])
                submitted_qty = float(row["submitted_quantity"])
                authoritative_orig = orig_sz if orig_sz is not None else submitted_qty
                if abs(authoritative_orig - submitted_qty) > 1e-8:
                    self._history(
                        conn,
                        cloid,
                        "reconciliation",
                        "submitted_quantity_conflict",
                        {"local": submitted_qty, "exchange_origSz": authoritative_orig},
                        now,
                    )
                calculated_remaining = max(submitted_qty - fill_qty, 0.0)
                remaining_qty = remaining if remaining is not None else calculated_remaining

                complete = True
                uncertainty_reason = None
                if status == "filled" and fill_qty + 1e-8 < min(
                    submitted_qty, authoritative_orig
                ):
                    complete = False
                    uncertainty_reason = "exchange_reports_filled_but_fill_events_are_incomplete"

                terminal = status if status in TERMINAL_EXCHANGE_STATUSES and complete else None
                cancel_reason = None
                reject_reason = row["reject_reason"]
                if status in {"canceled", "marginCanceled"}:
                    cancel_reason = f"exchange_status:{status}"
                if status == "rejected" and not reject_reason:
                    reject_reason = "exchange_status:rejected"

                current_status = f"exchange:{status}" if complete else "reconciliation_uncertain"
                conn.execute(
                    """UPDATE orders SET
                        exchange_oid=?, current_status=?, last_exchange_status=?,
                        last_exchange_payload_json=?, fill_quantity=?, average_fill_price=?, fees=?,
                        remaining_quantity=?, cancel_reason=COALESCE(?, cancel_reason),
                        reject_reason=COALESCE(?, reject_reason), terminal_status=?,
                        last_reconciliation_timestamp_ms=?, updated_at_ms=?
                       WHERE cloid=?""",
                    (
                        exchange_oid,
                        current_status,
                        status,
                        _json(order_status_response),
                        fill_qty,
                        avg_px,
                        fees,
                        remaining_qty,
                        cancel_reason,
                        reject_reason,
                        terminal,
                        now,
                        now,
                        cloid,
                    ),
                )
                self._history(
                    conn,
                    cloid,
                    "exchange_reconciliation",
                    status,
                    {
                        "status_timestamp": status_timestamp,
                        "exchange_oid": exchange_oid,
                        "fill_quantity": fill_qty,
                        "average_fill_price": avg_px,
                        "fees": fees,
                        "remaining_quantity": remaining_qty,
                        "terminal_status": terminal,
                    },
                    int(status_timestamp) if status_timestamp else now,
                )
                if not complete:
                    self._history(
                        conn,
                        cloid,
                        "reconciliation",
                        "reconciliation_uncertain",
                        {"reason": uncertainty_reason},
                        now,
                    )
                    conn.commit()
                    raise LedgerUncertainState(
                        f"CLOID {cloid}: {uncertainty_reason}; new risk is blocked"
                    )
                result = conn.execute("SELECT * FROM orders WHERE cloid=?", (cloid,)).fetchone()
                return dict(result)
        except LedgerError:
            raise
        except sqlite3.Error as exc:
            raise LedgerError(f"Could not apply exchange truth: {exc}") from exc


def _query_status_for_cloid(
    query_order_status: Callable[[str], dict[str, Any]], cloid: str
) -> dict[str, Any]:
    try:
        response = query_order_status(cloid)
    except Exception as exc:
        raise LedgerUncertainState(f"orderStatus lookup failed for {cloid}: {exc}") from exc
    if not isinstance(response, dict) or response.get("status") not in {"order", "unknownOid"}:
        raise LedgerUncertainState(f"Unexpected orderStatus response for {cloid}: {response}")
    return response


def _audit_known_orders(
    ledger: OrderLedger,
    orders: Iterable[dict[str, Any]],
    reason: str,
    detail: Any,
) -> None:
    for order in orders:
        ledger.record_reconciliation_uncertainty(order["cloid"], reason, detail)


def reconcile_unresolved_orders(
    ledger: OrderLedger,
    *,
    query_order_status: Callable[[str], dict[str, Any]],
    fetch_fills_by_time: Callable[[int, int], list[dict[str, Any]]],
    now_ms: int | None = None,
) -> dict[str, Any]:
    """Rebuild unresolved rows from Hyperliquid orderStatus + user fill truth.

    Any read ambiguity leaves a structured uncertainty event and raises. Exchange truth
    wins when known. A prior submission attempt that later returns unknownOid never
    triggers a blind resubmission.
    """
    now = now_ms or _now_ms()
    unresolved = ledger.unresolved_orders()
    if not unresolved:
        return {
            "unresolved_before": 0,
            "reconciled": 0,
            "unresolved_after": 0,
            "blocking_unresolved_after": 0,
        }

    known: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for local in unresolved:
        cloid = local["cloid"]
        try:
            response = _query_status_for_cloid(query_order_status, cloid)
        except LedgerUncertainState as exc:
            ledger.record_reconciliation_uncertainty(
                cloid, "order_status_lookup_failed", str(exc)
            )
            raise
        if response["status"] == "unknownOid":
            if local["submission_attempt_timestamp_ms"] is not None:
                ledger.record_reconciliation_uncertainty(
                    cloid,
                    "unknown_oid_after_durable_submission_attempt",
                    {"submission_attempt_timestamp_ms": local["submission_attempt_timestamp_ms"]},
                )
                raise LedgerUncertainState(
                    f"CLOID {cloid} is unknown at exchange after a durable submission attempt; blind retry is forbidden"
                )
            # The crash-safe ordering proves no network submit happened before the
            # durable attempt marker. Keep this intent for deterministic replay.
            continue
        known.append((local, response))

    fills: list[dict[str, Any]] = []
    if known:
        start_candidates = [
            int(local["submission_attempt_timestamp_ms"] or local["decision_timestamp_ms"])
            for local, _ in known
        ]
        start_ms = max(0, min(start_candidates) - 60_000)
        try:
            fills = fetch_fills_by_time(start_ms, now)
        except Exception as exc:
            _audit_known_orders(ledger, [local for local, _ in known], "fill_lookup_failed", str(exc))
            raise LedgerUncertainState(f"userFillsByTime lookup failed: {exc}") from exc
        if not isinstance(fills, list):
            _audit_known_orders(
                ledger,
                [local for local, _ in known],
                "malformed_fill_lookup_response",
                fills,
            )
            raise LedgerUncertainState(f"Malformed userFillsByTime response: {fills}")
        if len(fills) >= FILL_LIMIT:
            _audit_known_orders(
                ledger,
                [local for local, _ in known],
                "fill_response_may_be_truncated",
                {"count": len(fills)},
            )
            raise LedgerUncertainState(
                f"userFillsByTime returned {len(fills)} fills, reaching the API limit; pagination is required before truth is complete"
            )

    reconciled = 0
    for local, response in known:
        try:
            ledger.apply_exchange_truth(
                local["cloid"], response, fills, reconciled_at_ms=now
            )
        except LedgerUncertainState as exc:
            ledger.record_reconciliation_uncertainty(
                local["cloid"], "exchange_truth_apply_failed", str(exc)
            )
            raise
        reconciled += 1

    after = ledger.unresolved_orders()
    return {
        "unresolved_before": len(unresolved),
        "reconciled": reconciled,
        "unresolved_after": len(after),
        "blocking_unresolved_after": len(ledger.blocking_unresolved_orders()),
    }
