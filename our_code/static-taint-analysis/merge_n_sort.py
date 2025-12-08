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
            "sdk_name": path.stem,  # use path.name if you want the .json suffix
            "findings": content
        })

    # Output file in the *current* working directory
    output_path = Path.cwd() / output_name

    # If all.json already exists, delete it first
    if output_path.exists():
        try:
            output_path.unlink()
            print(f"Deleted existing file: {output_path}")
        except OSError as e:
            print(f"Error deleting {output_path}: {e}")
            sys.exit(1)

    with output_path.open("w", encoding="utf-8") as out:
        json.dump(items, out, ensure_ascii=False, indent=2)

    print(f"Merged {len(items)} JSON files into {output_path}")


def sort_all_json_by_sdk_name(input_name: str = "all.json",
                              output_name: str = "all_sorted.json"):
    """
    Read input_name from the current directory, sort all items by 'sdk_name',
    and write the sorted content to output_name.
    """
    input_path = Path.cwd() / input_name

    if not input_path.is_file():
        print(f"Error: {input_path} does not exist. Run merge_json_in_dir first.")
        sys.exit(1)

    with input_path.open("r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error: {input_path} is not valid JSON ({e})")
            sys.exit(1)

    if not isinstance(data, list):
        print(f"Error: {input_path} does not contain a JSON array.")
        sys.exit(1)

    # Sort by sdk_name (missing keys get empty string to avoid KeyError)
    data_sorted = sorted(data, key=lambda item: item.get("sdk_name", ""))

    output_path = Path.cwd() / output_name

    # If all_sorted.json already exists, delete it first
    if output_path.exists():
        try:
            output_path.unlink()
            print(f"Deleted existing file: {output_path}")
        except OSError as e:
            print(f"Error deleting {output_path}: {e}")
            sys.exit(1)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(data_sorted, f, ensure_ascii=False, indent=2)

    print(f"Sorted {len(data_sorted)} items by 'sdk_name' into {output_path}")


if __name__ == "__main__":
    json_dir = "g_out_api"

    # 1) merge all JSON files in the given directory into all.json
    merge_json_in_dir(json_dir, "all.json")

    # 2) sort all.json by sdk_name into all_sorted.json
    sort_all_json_by_sdk_name("all.json", "all_sorted.json")