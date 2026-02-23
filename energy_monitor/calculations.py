from __future__ import annotations

DAYS_PER_WEEK = 7
DAYS_PER_MONTH = 30  # simple forecast month length

def validate_price_per_kwh(price: float) -> None:
    if price <= 0:
        raise ValueError("Price per kWh must be greater than 0.")

def validate_device_values(wattage: float, hours: float) -> None:
    if wattage <= 0:
        raise ValueError("Wattage must be greater than 0.")
    if hours < 0:
        raise ValueError("Average hours per day cannot be negative.")
    if hours > 24:
        raise ValueError("Average hours per day cannot exceed 24.")

def daily_kwh(wattage_w: float, hours_per_day: float) -> float:
    # kWh = (W * hours) / 1000
    return (wattage_w * hours_per_day) / 1000.0

def cost_for_kwh(kwh: float, price_per_kwh: float) -> float:
    return kwh * price_per_kwh

def daily_cost(wattage_w: float, hours_per_day: float, price_per_kwh: float) -> float:
    return cost_for_kwh(daily_kwh(wattage_w, hours_per_day), price_per_kwh)

def weekly_cost(wattage_w: float, hours_per_day: float, price_per_kwh: float) -> float:
    return daily_cost(wattage_w, hours_per_day, price_per_kwh) * DAYS_PER_WEEK

def monthly_cost(wattage_w: float, hours_per_day: float, price_per_kwh: float) -> float:
    return daily_cost(wattage_w, hours_per_day, price_per_kwh) * DAYS_PER_MONTH

def monthly_kwh(wattage_w: float, hours_per_day: float) -> float:
    return daily_kwh(wattage_w, hours_per_day) * DAYS_PER_MONTH