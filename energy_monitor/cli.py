from __future__ import annotations

def prompt_float(prompt: str, min_value: float | None = None, allow_zero: bool = False) -> float:
    while True:
        raw = input(prompt).strip()
        try:
            val = float(raw)
        except ValueError:
            print("Invalid number. Try again (example: 0.12).")
            continue

        if min_value is not None:
            if allow_zero:
                if val < min_value:
                    print(f"Value must be >= {min_value}.")
                    continue
            else:
                if val <= min_value:
                    print(f"Value must be > {min_value}.")
                    continue

        return val

def prompt_yes_no(prompt: str) -> bool:
    while True:
        raw = input(prompt + " (y/n): ").strip().lower()
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        print("Please enter y or n.")