from __future__ import annotations

from typing import Any

import pandas as pd

from run_tsmom_alpha_0029 import EPS, event_pnl_date


def _contiguous_spans(dates: list[pd.Timestamp]) -> list[dict[str, Any]]:
    if not dates:
        return []
    ordered = sorted(pd.Timestamp(date).normalize() for date in dates)
    spans: list[dict[str, Any]] = []
    start = prev = ordered[0]
    for current in ordered[1:]:
        if current == prev + pd.Timedelta(days=1):
            prev = current
            continue
        spans.append({
            "start": str(start.date()),
            "end": str(prev.date()),
            "days": int((prev - start).days + 1),
        })
        start = prev = current
    spans.append({
        "start": str(start.date()),
        "end": str(prev.date()),
        "days": int((prev - start).days + 1),
    })
    return spans


def funding_accounting_event_semantics(
    held: pd.DataFrame,
    funding: dict[str, pd.DataFrame],
    index: pd.DatetimeIndex,
) -> tuple[pd.Series, pd.DataFrame, dict[str, Any]]:
    """TSMOM-DATA-0029B funding-event accounting.

    Funding is an event cashflow. A symbol-day with an active held position but
    no official recorded settlement event contributes exactly no funding
    cashflow; it is retained explicitly as a coverage diagnostic. Missing
    symbol data is still a hard failure because load_funding_panel is required
    to return an entry for every active symbol.
    """
    events: list[dict[str, Any]] = []
    symbol_rows: list[dict[str, Any]] = []
    no_event_rows: list[dict[str, Any]] = []
    no_event_spans: list[dict[str, Any]] = []

    for symbol in held.columns:
        active = held.index[(held[symbol].abs() > EPS) & held.index.isin(index)]
        if len(active) == 0:
            continue
        if symbol not in funding:
            raise RuntimeError(f"{symbol}: active position but funding archive result is missing")
        frame = funding[symbol]

        covered_dates: set[pd.Timestamp] = set()
        long_contribution = 0.0
        short_contribution = 0.0
        event_count = 0

        if frame is not None and not frame.empty:
            for row in frame.itertuples(index=False):
                ts = pd.Timestamp(row.timestamp)
                pnl_date = event_pnl_date(ts)
                if pnl_date not in index or pnl_date not in held.index:
                    continue
                weight = float(held.at[pnl_date, symbol])
                if abs(weight) <= EPS:
                    continue
                rate = float(row.rate)
                contribution = -weight * rate
                covered_dates.add(pd.Timestamp(pnl_date))
                event_count += 1
                if weight > 0:
                    long_contribution += contribution
                else:
                    short_contribution += contribution
                events.append({
                    "timestamp": ts,
                    "pnl_date": pd.Timestamp(pnl_date),
                    "symbol": symbol,
                    "weight": weight,
                    "rate": rate,
                    "contribution": contribution,
                })

        missing_dates = [
            pd.Timestamp(date)
            for date in active
            if pd.Timestamp(date) not in covered_dates
        ]
        for date in missing_dates:
            weight = float(held.at[date, symbol])
            no_event_rows.append({
                "symbol": symbol,
                "date": pd.Timestamp(date),
                "weight": weight,
                "long_gross": max(weight, 0.0),
                "short_gross": max(-weight, 0.0),
            })
        for span in _contiguous_spans(missing_dates):
            no_event_spans.append({"symbol": symbol, **span})

        symbol_rows.append({
            "symbol": symbol,
            "active_days": int(len(active)),
            "active_days_with_funding_event": int(len(active) - len(missing_dates)),
            "active_days_without_funding_event": int(len(missing_dates)),
            "funding_event_count": int(event_count),
            "long_additive_contribution": float(long_contribution),
            "short_additive_contribution": float(short_contribution),
            "net_additive_contribution": float(long_contribution + short_contribution),
        })

    event_frame = pd.DataFrame(events)
    factor = pd.Series(1.0, index=index, dtype=float)
    if not event_frame.empty:
        grouped_event = event_frame.groupby(["pnl_date", "timestamp"], sort=True)["contribution"].sum()
        if (1.0 + grouped_event <= 0).any():
            raise RuntimeError("Funding event portfolio return <= -100%")
        daily = (1.0 + grouped_event).groupby(level=0).prod()
        common = daily.index.intersection(factor.index)
        factor.loc[common] = daily.loc[common].astype(float)

    symbol_summary = pd.DataFrame(symbol_rows)
    if not symbol_summary.empty:
        symbol_summary = symbol_summary.sort_values("symbol").reset_index(drop=True)

    active_symbol_days = int(symbol_summary["active_days"].sum()) if len(symbol_summary) else 0
    no_event_count = int(len(no_event_rows))
    covered_symbol_days = active_symbol_days - no_event_count
    coverage_ratio = float(covered_symbol_days / active_symbol_days) if active_symbol_days else None

    no_event = pd.DataFrame(no_event_rows)
    if no_event.empty:
        no_event_day_count = 0
        mean_long_gross = mean_short_gross = max_long_gross = max_short_gross = 0.0
        mean_abs_weight = 0.0
    else:
        by_day = no_event.groupby("date", sort=True).agg(
            long_gross=("long_gross", "sum"),
            short_gross=("short_gross", "sum"),
            missing_symbols=("symbol", "count"),
        )
        no_event_day_count = int(len(by_day))
        mean_long_gross = float(by_day["long_gross"].mean())
        mean_short_gross = float(by_day["short_gross"].mean())
        max_long_gross = float(by_day["long_gross"].max())
        max_short_gross = float(by_day["short_gross"].max())
        mean_abs_weight = float(no_event["weight"].abs().mean())

    spans_sorted = sorted(
        no_event_spans,
        key=lambda row: (-int(row["days"]), row["symbol"], row["start"]),
    )

    diag = {
        "semantics_audit_id": "TSMOM-DATA-0029B-FUNDING-EVENT-SEMANTICS",
        "event_rows_used": int(len(event_frame)),
        "active_symbol_days": active_symbol_days,
        "active_symbol_days_with_funding_event": int(covered_symbol_days),
        "active_symbol_days_without_funding_event": no_event_count,
        "active_symbol_day_event_coverage_ratio": coverage_ratio,
        "symbols_with_no_event_days": int(no_event["symbol"].nunique()) if not no_event.empty else 0,
        "calendar_days_with_at_least_one_active_symbol_missing_event": no_event_day_count,
        "mean_missing_subset_long_gross_on_affected_days": mean_long_gross,
        "mean_missing_subset_short_gross_on_affected_days": mean_short_gross,
        "max_missing_subset_long_gross_on_affected_days": max_long_gross,
        "max_missing_subset_short_gross_on_affected_days": max_short_gross,
        "mean_abs_weight_per_missing_symbol_day": mean_abs_weight,
        "long_additive_contribution": float(symbol_summary["long_additive_contribution"].sum()) if len(symbol_summary) else 0.0,
        "short_additive_contribution": float(symbol_summary["short_additive_contribution"].sum()) if len(symbol_summary) else 0.0,
        "net_additive_contribution": float(symbol_summary["net_additive_contribution"].sum()) if len(symbol_summary) else 0.0,
        "longest_no_event_spans": spans_sorted[:100],
        "accounting_rule": "only official recorded funding settlement events create cashflow; active symbol-days without a recorded event contribute zero cashflow and remain explicit coverage diagnostics",
    }
    return factor, symbol_summary, diag
