from __future__ import annotations

from energy_monitor.storage import (
    load_devices, ensure_output_dir, write_text, DataFileError
)
from energy_monitor.calculations import validate_price_per_kwh
from energy_monitor.reporting import (
    build_cost_report_text, build_monthly_forecast_text, build_predictions_text,
    high_usage_alerts
)
from energy_monitor.cli import prompt_float, prompt_yes_no

APPLIANCES_FILE = "appliances.txt"
OUTPUT_DIR = "output"

def main() -> None:
    print("Smart Home Energy Monitor (CLI)")
    print("Loading devices from appliances.txt ...")

    try:
        devices = load_devices(APPLIANCES_FILE)
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        print("Fix: Ensure appliances.txt exists in the project folder.")
        return
    except DataFileError as e:
        print(f"ERROR in appliances.txt: {e}")
        print("Fix: Correct the file format: device_id|name|wattage|avg_hours_per_day|room_location")
        return
    except ValueError as e:
        # catches validate_device_values failures
        print(f"ERROR: Invalid device values: {e}")
        return
    except Exception as e:
        print(f"Unexpected error while loading devices: {e}")
        return

    print(f"Loaded {len(devices)} devices.\n")

    price_per_kwh = prompt_float("Enter price per kWh (example 0.12): ", min_value=0.0, allow_zero=False)
    try:
        validate_price_per_kwh(price_per_kwh)
    except ValueError as e:
        print(f"ERROR: {e}")
        return

    extra_daily_cost = prompt_float(
        "Enter additional fixed daily cost (service charge). If none, enter 0: ",
        min_value=0.0,
        allow_zero=True
    )

    # Threshold alerts
    threshold_kwh = prompt_float(
        "Enter monthly kWh threshold for alerts (example 50). If none, enter 0: ",
        min_value=0.0,
        allow_zero=True
    )

    out_dir = ensure_output_dir(OUTPUT_DIR)

    cost_report = build_cost_report_text(devices, price_per_kwh, extra_daily_cost)
    forecast_report = build_monthly_forecast_text(devices, price_per_kwh, extra_daily_cost)
    predictions_report = build_predictions_text(devices, price_per_kwh)

    # Alerts (only if threshold > 0)
    if threshold_kwh > 0:
        alerts = high_usage_alerts(devices, monthly_kwh_threshold=threshold_kwh)
    else:
        alerts = []

    # Print to terminal
    print("\n" + "=" * 70)
    print(cost_report)
    if alerts:
        print("\nALERTS:")
        for a in alerts:
            print(" - " + a)
            if prompt_yes_no("Do you want a reduction warning message for this device?"):
                print("   REDUCE USAGE: Try lowering hours/day or using eco mode / timers.\n")
    print("=" * 70)
    print("\n" + forecast_report)
    print("\n" + predictions_report)

    # Save outputs
    try:
        write_text(str(out_dir / "costs_report.txt"), cost_report + ("\n\nALERTS:\n" + "\n".join(alerts) if alerts else ""))
        write_text(str(out_dir / "monthly_forecast.txt"), forecast_report)
        write_text(str(out_dir / "predictions.txt"), predictions_report)
    except PermissionError:
        print("ERROR: Cannot write output files (permission denied). Try running in a writable folder.")
        return
    except OSError as e:
        print(f"ERROR: File write failed: {e}")
        return

    print("\nSaved reports to:")
    print(f" - {out_dir / 'costs_report.txt'}")
    print(f" - {out_dir / 'monthly_forecast.txt'}")
    print(f" - {out_dir / 'predictions.txt'}")
    print("\nDone.")

if __name__ == "__main__":
    main()