from __future__ import annotations
from collections import defaultdict
from typing import Dict, List, Tuple

from .models import Device
from .calculations import (
    daily_kwh, monthly_kwh, daily_cost, weekly_cost, monthly_cost
)

def efficiency_suggestions(device: Device) -> List[str]:
    suggestions: List[str] = []

    # Example requirement: > 12 hours/day -> power saving mode suggestion
    if device.avg_hours_per_day > 12:
        suggestions.append("Consider using Power Saving Mode or reducing on-time (>12h/day).")

    # Simple heuristic ideas
    if device.wattage >= 1000:
        suggestions.append("High wattage device: run during off-peak hours if available.")
    if 0 < device.avg_hours_per_day <= 0.25:
        suggestions.append("Usage is very low; verify hours/day is correct (data sanity check).")

    return suggestions

def high_usage_alerts(devices: List[Device], monthly_kwh_threshold: float) -> List[str]:
    alerts = []
    for d in devices:
        mkwh = monthly_kwh(d.wattage, d.avg_hours_per_day)
        if mkwh > monthly_kwh_threshold:
            alerts.append(
                f"ALERT: {d.device_id} '{d.name}' in {d.room_location} uses ~{mkwh:.2f} kWh/month "
                f"(threshold {monthly_kwh_threshold:.2f})."
            )
    return alerts

def device_cost_rows(devices: List[Device], price_per_kwh: float) -> List[Dict[str, str]]:
    rows = []
    for d in devices:
        rows.append({
            "id": d.device_id,
            "name": d.name,
            "room": d.room_location,
            "wattage_w": f"{d.wattage:.0f}",
            "hours_day": f"{d.avg_hours_per_day:.2f}",
            "daily_kwh": f"{daily_kwh(d.wattage, d.avg_hours_per_day):.3f}",
            "daily_cost": f"{daily_cost(d.wattage, d.avg_hours_per_day, price_per_kwh):.2f}",
            "weekly_cost": f"{weekly_cost(d.wattage, d.avg_hours_per_day, price_per_kwh):.2f}",
            "monthly_cost": f"{monthly_cost(d.wattage, d.avg_hours_per_day, price_per_kwh):.2f}",
        })
    return rows

def totals(devices: List[Device], price_per_kwh: float) -> Dict[str, float]:
    total_daily = 0.0
    total_weekly = 0.0
    total_monthly = 0.0

    for d in devices:
        total_daily += daily_cost(d.wattage, d.avg_hours_per_day, price_per_kwh)
        total_weekly += weekly_cost(d.wattage, d.avg_hours_per_day, price_per_kwh)
        total_monthly += monthly_cost(d.wattage, d.avg_hours_per_day, price_per_kwh)

    return {"daily": total_daily, "weekly": total_weekly, "monthly": total_monthly}

def room_monthly_totals(devices: List[Device], price_per_kwh: float) -> Dict[str, float]:
    by_room = defaultdict(float)
    for d in devices:
        by_room[d.room_location] += monthly_cost(d.wattage, d.avg_hours_per_day, price_per_kwh)
    return dict(by_room)

def format_table(headers: List[str], rows: List[List[str]]) -> str:
    # simple fixed-width table
    widths = [len(h) for h in headers]
    for r in rows:
        for i, cell in enumerate(r):
            widths[i] = max(widths[i], len(cell))

    def fmt_row(r: List[str]) -> str:
        return " | ".join(r[i].ljust(widths[i]) for i in range(len(headers)))

    sep = "-+-".join("-" * w for w in widths)

    out = []
    out.append(fmt_row(headers))
    out.append(sep)
    for r in rows:
        out.append(fmt_row(r))
    return "\n".join(out)

def build_cost_report_text(devices: List[Device], price_per_kwh: float, extra_daily_cost: float) -> str:
    rows = device_cost_rows(devices, price_per_kwh)

    headers = ["ID", "Name", "Room", "W(W)", "Hrs/Day", "kWh/Day", "Daily", "Weekly", "Monthly"]
    table_rows = []
    for r in rows:
        table_rows.append([
            r["id"], r["name"], r["room"], r["wattage_w"], r["hours_day"],
            r["daily_kwh"], r["daily_cost"], r["weekly_cost"], r["monthly_cost"]
        ])

    t = totals(devices, price_per_kwh)
    # include user additional daily cost (e.g., fixed service charge)
    extra_weekly = extra_daily_cost * 7
    extra_monthly = extra_daily_cost * 30

    report = []
    report.append("SMART HOME ENERGY MONITOR - COST REPORT")
    report.append(f"Price per kWh: {price_per_kwh:.4f}")
    report.append("")
    report.append(format_table(headers, table_rows))
    report.append("")
    report.append("TOTALS (devices only):")
    report.append(f"  Daily:   {t['daily']:.2f}")
    report.append(f"  Weekly:  {t['weekly']:.2f}")
    report.append(f"  Monthly: {t['monthly']:.2f}")
    report.append("")
    report.append("ADDITIONAL COSTS (user provided):")
    report.append(f"  Extra daily cost:   {extra_daily_cost:.2f}")
    report.append(f"  Extra weekly cost:  {extra_weekly:.2f}")
    report.append(f"  Extra monthly cost: {extra_monthly:.2f}")
    report.append("")
    report.append("GRAND TOTALS (devices + extra):")
    report.append(f"  Daily:   {(t['daily'] + extra_daily_cost):.2f}")
    report.append(f"  Weekly:  {(t['weekly'] + extra_weekly):.2f}")
    report.append(f"  Monthly: {(t['monthly'] + extra_monthly):.2f}")
    report.append("")
    report.append("EFFICIENCY SUGGESTIONS:")
    for d in devices:
        sugg = efficiency_suggestions(d)
        if sugg:
            report.append(f"- {d.device_id} {d.name} ({d.room_location}):")
            for s in sugg:
                report.append(f"    * {s}")
    return "\n".join(report)

def build_monthly_forecast_text(devices: List[Device], price_per_kwh: float, extra_daily_cost: float) -> str:
    room_totals = room_monthly_totals(devices, price_per_kwh)
    extra_monthly = extra_daily_cost * 30

    headers = ["Room", "Expected Monthly Cost"]
    rows = [[room, f"{cost:.2f}"] for room, cost in sorted(room_totals.items(), key=lambda x: x[0].lower())]

    # Add a summary row
    device_monthly_total = sum(room_totals.values())
    grand_total = device_monthly_total + extra_monthly

    out = []
    out.append("MONTHLY FORECAST (BY ROOM)")
    out.append(f"Price per kWh: {price_per_kwh:.4f}")
    out.append("")
    out.append(format_table(headers, rows))
    out.append("")
    out.append(f"Devices monthly total: {device_monthly_total:.2f}")
    out.append(f"Extra monthly cost:    {extra_monthly:.2f}")
    out.append(f"Forecast grand total:  {grand_total:.2f}")
    return "\n".join(out)

def build_predictions_text(devices: List[Device], price_per_kwh: float) -> str:
    # "prediction" here is a simple projection:
    # - monthly kWh and monthly cost per device
    # - top 3 devices by monthly cost
    preds = []
    for d in devices:
        mkwh = monthly_kwh(d.wattage, d.avg_hours_per_day)
        mcost = mkwh * price_per_kwh
        preds.append((mcost, d, mkwh))

    preds.sort(reverse=True, key=lambda x: x[0])
    top3 = preds[:3]

    out = []
    out.append("PREDICTIONS / INSIGHTS")
    out.append("")
    out.append("Top devices by expected monthly cost:")
    for rank, (mcost, d, mkwh) in enumerate(top3, start=1):
        out.append(f"{rank}. {d.device_id} {d.name} ({d.room_location}) -> {mkwh:.2f} kWh/mo, {mcost:.2f}/mo")

    out.append("")
    out.append("Note: This is a simple projection based on average daily hours (no time-series learning).")
    return "\n".join(out)