#!/usr/bin/env python3
import json
from pathlib import Path
import sys


def count_complianceinfo(obj) -> int:
    """
    Recursively count items under any key named 'ComplianceInfo'.
    - If the value is a list, count its length.
    - If the value is a dict, count number of keys.
    - Otherwise, count as 1.
    """
    if isinstance(obj, dict):
        total = 0
        for key, value in obj.items():
            if key == "ComplianceInfo":
                if isinstance(value, list):
                    total += len(value)
                elif isinstance(value, dict):
                    total += len(value)
                else:
                    total += 1
            # recurse into nested structures
            total += count_complianceinfo(value)
        return total

    elif isinstance(obj, list):
        return sum(count_complianceinfo(item) for item in obj)

    # primitives: no nested structure
    return 0


def process_directory(dir_path: str):
    base = Path(dir_path)

    if not base.is_dir():
        print(f"Error: {dir_path} is not a directory")
        sys.exit(1)

    json_files = sorted(base.glob("*.json"))

    if not json_files:
        print(f"No JSON files found in {dir_path}")
        return

    for path in json_files:
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"{path.name}: invalid JSON ({e})")
            continue

        count = count_complianceinfo(data)
        print(f"{count}\t{path.name}")


if __name__ == "__main__":
    dir = "g_out_api"
    process_directory(dir)