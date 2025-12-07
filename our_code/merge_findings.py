#!/usr/bin/env python3
import json
from pathlib import Path
import sys


def merge_json_in_dir(input_dir: str, output_name: str = "all.json"):
    input_path = Path(input_dir)

    if not input_path.is_dir():
        print(f"Error: {input_dir} is not a directory")
        sys.exit(1)

    # Collect all *.json files (non-recursive). Sort for deterministic order.
    json_files = sorted(input_path.glob("*.json"))

    if not json_files:
        print(f"No JSON files found in directory: {input_dir}")
        sys.exit(1)

    items = []

    for path in json_files:
        try:
            with path.open("r", encoding="utf-8") as f:
                content = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Skipping {path.name}: invalid JSON ({e})")
            continue

        items.append({
            "sdk_name": path.stem,  # or path.name if you want the .json suffix
            "findings": content
        })

    # Output file in the *current* working directory
    output_path = Path.cwd() / output_name
    with output_path.open("w", encoding="utf-8") as out:
        json.dump(items, out, ensure_ascii=False, indent=2)

    print(f"Merged {len(items)} JSON files into {output_path}")


if __name__ == "__main__":
    #if len(sys.argv) != 2:
    #    print(f"Usage: {Path(sys.argv[0]).name} <directory_with_json_files>")
    #    sys.exit(1)
    #merge_json_in_dir(sys.argv[1])

    json_dir = "sdk"

    merge_json_in_dir(json_dir)