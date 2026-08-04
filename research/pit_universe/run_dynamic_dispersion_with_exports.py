"""Run frozen PIT-DISP-0015 and persist exact daily research outputs.

This wrapper does not alter the preregistered model. It captures the completed
`run_dynamic_dispersion.main` frame at return so the already-computed returns,
weights, universe and scale series can be written without performing a second
network/data/model pass.
"""

from __future__ import annotations

import html
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import run_dynamic_dispersion as experiment

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DOCS = ROOT / "docs"
CAPTURED: dict[str, object] = {}


def _local_trace(frame, event, arg):
    if event == "return":
        CAPTURED.update(frame.f_locals)
    return _local_trace


def _global_trace(frame, event, arg):
    if event == "call" and frame.f_code is experiment.main.__code__:
        return _local_trace
    return None


def _svg_path(values: np.ndarray, x0: float, y0: float, width: float, height: float, lo: float, hi: float) -> str:
    n = len(values)
    if n == 0:
        return ""
    span = max(hi - lo, 1e-12)
    coords = []
    for i, value in enumerate(values):
        x = x0 if n == 1 else x0 + width * i / (n - 1)
        y = y0 + height * (hi - float(value)) / span
        coords.append((x, y))
    return "M " + " L ".join(f"{x:.2f} {y:.2f}" for x, y in coords)


def write_equity_svg(equity: pd.DataFrame, destination: Path) -> None:
    selected = [
        "V1_BASELINE",
        "BRRK0011_BASELINE",
        "BRRK0011_PLUS_FIXED_PANEL_DISP0014",
        "BRRK0011_PLUS_DYNAMIC_UNIVERSE_DISP0015",
    ]
    selected = [name for name in selected if name in equity.columns]
    chart = equity[selected].dropna(how="all")
    if chart.empty:
        raise RuntimeError("Cannot draw PNL SVG: daily equity is empty")

    width, height = 1200, 660
    left, right, top, bottom = 105, 35, 75, 95
    plot_w, plot_h = width - left - right, height - top - bottom
    low = min(0.0, float(chart.min().min()) * 0.95)
    high = float(chart.max().max()) * 1.05
    colors = ["#111111", "#2457A7", "#777777", "#B13B2E"]
    dashes = ["", "", "8 5", ""]

    y_ticks = np.linspace(low, high, 6)
    years = sorted(set(chart.index.year))
    year_positions = []
    for year in years:
        candidates = chart.index[chart.index.year == year]
        if len(candidates):
            dt = candidates[0]
            pos = chart.index.get_loc(dt)
            year_positions.append((year, pos))

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#111}.grid{stroke:#dedede;stroke-width:1}.axis{stroke:#555;stroke-width:1.2}</style>',
        '<text x="105" y="30" font-size="22" font-weight="700">PIT-DISP-0015 exact daily NAV</text>',
        f'<text x="105" y="52" font-size="12">$10,000 start · {chart.index[0].date()} to {chart.index[-1].date()} · completed daily data · 5 bps cost · 0.05 L1 band</text>',
    ]

    for tick in y_ticks:
        y = top + plot_h * (high - float(tick)) / max(high - low, 1e-12)
        parts.append(f'<line class="grid" x1="{left}" y1="{y:.2f}" x2="{left + plot_w}" y2="{y:.2f}"/>')
        parts.append(f'<text x="{left - 12}" y="{y + 4:.2f}" font-size="11" text-anchor="end">${tick:,.0f}</text>')

    for year, pos in year_positions:
        x = left + plot_w * pos / max(len(chart) - 1, 1)
        parts.append(f'<line class="grid" x1="{x:.2f}" y1="{top}" x2="{x:.2f}" y2="{top + plot_h}"/>')
        parts.append(f'<text x="{x:.2f}" y="{top + plot_h + 24}" font-size="11" text-anchor="middle">{year}</text>')

    parts.extend([
        f'<line class="axis" x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_h}"/>',
        f'<line class="axis" x1="{left}" y1="{top + plot_h}" x2="{left + plot_w}" y2="{top + plot_h}"/>',
    ])

    for i, name in enumerate(selected):
        values = chart[name].ffill().to_numpy(float)
        path = _svg_path(values, left, top, plot_w, plot_h, low, high)
        dash = f' stroke-dasharray="{dashes[i]}"' if dashes[i] else ""
        parts.append(f'<path d="{path}" fill="none" stroke="{colors[i]}" stroke-width="2.5"{dash}/>')
        final = float(values[-1])
        legend_y = height - 58 + (i % 2) * 22
        legend_x = left + (i // 2) * 500
        parts.append(f'<line x1="{legend_x}" y1="{legend_y - 4}" x2="{legend_x + 30}" y2="{legend_y - 4}" stroke="{colors[i]}" stroke-width="3"{dash}/>')
        parts.append(f'<text x="{legend_x + 40}" y="{legend_y}" font-size="12">{html.escape(name)} — ${final:,.0f}</text>')

    parts.append('</svg>')
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(parts), encoding="utf-8")


def export_outputs() -> None:
    required = {
        "candidates", "evaluated", "fixed_prices", "eval_start", "eval_idx",
        "universe_n", "dyn_d", "dyn_target", "dyn_raw_scale", "dyn_scale",
        "fixed_d", "fixed_raw_scale", "fixed_scale", "brrk_scale", "eligible", "status_map",
    }
    missing = sorted(required - CAPTURED.keys())
    if missing:
        raise RuntimeError(f"PIT-0015 completed but output capture is missing locals: {missing}")

    candidates = CAPTURED["candidates"]
    evaluated = CAPTURED["evaluated"]
    eval_idx = CAPTURED["eval_idx"]
    eligible = CAPTURED["eligible"]
    status_map = CAPTURED["status_map"]

    equity = pd.DataFrame({
        name: 10_000.0 * (1.0 + result["return"]).cumprod()
        for name, result in evaluated.items()
    }).reindex(eval_idx)
    equity.index.name = "date"
    equity.to_csv(HERE / "daily_equity.csv", float_format="%.10f")

    held_frames = []
    for name, raw_weights in candidates.items():
        banded = experiment.bt.apply_band(raw_weights, 0.05)
        held = banded.shift(1).fillna(0.0).reindex(eval_idx)
        held = held.rename(columns={asset: f"{name}__{asset}" for asset in held.columns})
        held_frames.append(held)
    daily_weights = pd.concat(held_frames, axis=1)
    daily_weights.index.name = "date"
    daily_weights.to_csv(HERE / "daily_weights.csv", float_format="%.10f")

    universe = pd.DataFrame({
        "eligible_count": CAPTURED["universe_n"],
        "dynamic_dispersion": CAPTURED["dyn_d"],
    }).reindex(eval_idx)
    universe.index.name = "date"
    universe.to_csv(HERE / "daily_dynamic_universe_count.csv", float_format="%.10f")

    scales = pd.DataFrame({
        "dynamic_dispersion": CAPTURED["dyn_d"],
        "dynamic_prior_median": CAPTURED["dyn_target"],
        "dynamic_raw_scale": CAPTURED["dyn_raw_scale"],
        "dynamic_smoothed_scale": CAPTURED["dyn_scale"],
        "fixed_panel_dispersion": CAPTURED["fixed_d"],
        "fixed_panel_raw_scale": CAPTURED["fixed_raw_scale"],
        "fixed_panel_smoothed_scale": CAPTURED["fixed_scale"],
        "brrk0011_scale": CAPTURED["brrk_scale"],
    }).reindex(eval_idx)
    scales.index.name = "date"
    scales.to_csv(HERE / "dispersion_scale.csv", float_format="%.10f")

    inactive_rows = []
    for symbol in eligible.columns:
        current_status = status_map.get(symbol, "MISSING")
        if current_status == "TRADING":
            continue
        dates = eligible.index[eligible[symbol].fillna(False)]
        if len(dates) == 0:
            continue
        inactive_rows.append({
            "symbol": symbol,
            "current_status": current_status,
            "eligible_days": int(len(dates)),
            "first_eligible_date": str(dates[0].date()),
            "last_eligible_date": str(dates[-1].date()),
        })
    inactive_audit = pd.DataFrame(inactive_rows)
    if not inactive_audit.empty:
        inactive_audit = inactive_audit.sort_values(["eligible_days", "symbol"], ascending=[False, True])
    inactive_audit.to_csv(HERE / "inactive_eligible_audit.csv", index=False)

    write_equity_svg(equity, HERE / "pnl_daily.svg")
    write_equity_svg(equity, DOCS / "pnl.svg")

    print("exact_outputs_written", {
        "equity_rows": len(equity),
        "weight_columns": len(daily_weights.columns),
        "inactive_symbols_ever_eligible": len(inactive_audit),
        "pnl_svg": str(DOCS / "pnl.svg"),
    }, flush=True)


def main() -> None:
    sys.settrace(_global_trace)
    try:
        experiment.main()
    finally:
        sys.settrace(None)
    export_outputs()


if __name__ == "__main__":
    main()
