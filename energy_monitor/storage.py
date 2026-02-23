from __future__ import annotations
from pathlib import Path
from typing import List, Tuple
from .models import Device
from .calculations import validate_device_values

class DataFileError(Exception):
    """Raised when appliance file content/format is invalid."""

def load_devices(file_path: str) -> List[Device]:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Appliance file not found: {file_path}")

    devices: List[Device] = []
    seen_ids = set()

    lines = path.read_text(encoding="utf-8").splitlines()
    for line_no, raw in enumerate(lines, start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        parts = [p.strip() for p in line.split("|")]
        if len(parts) != 5:
            raise DataFileError(
                f"Line {line_no}: expected 5 fields separated by '|', got {len(parts)}. "
                f"Bad line: {raw}"
            )

        device_id, name, wattage_s, hours_s, room = parts

        if not device_id:
            raise DataFileError(f"Line {line_no}: device_id cannot be empty.")
        if device_id in seen_ids:
            raise DataFileError(f"Line {line_no}: duplicate device_id '{device_id}'.")

        try:
            wattage = float(wattage_s)
            hours = float(hours_s)
        except ValueError:
            raise DataFileError(
                f"Line {line_no}: wattage and avg_hours_per_day must be numbers. "
                f"Got wattage='{wattage_s}', hours='{hours_s}'."
            )

        validate_device_values(wattage, hours)

        devices.append(Device(
            device_id=device_id,
            name=name or "Unknown",
            wattage=wattage,
            avg_hours_per_day=hours,
            room_location=room or "Unknown"
        ))
        seen_ids.add(device_id)

    if not devices:
        raise DataFileError("No valid devices found in appliances file.")

    return devices

def ensure_output_dir(output_dir: str) -> Path:
    p = Path(output_dir)
    p.mkdir(parents=True, exist_ok=True)
    return p

def write_text(output_path: str, content: str) -> None:
    Path(output_path).write_text(content, encoding="utf-8")