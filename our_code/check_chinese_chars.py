#!/usr/bin/env python3
import sys
from pathlib import Path


def is_chinese_char(ch: str) -> bool:
    """Return True if char is a CJK (Chinese) character."""
    code = ord(ch)
    return (
        0x4E00 <= code <= 0x9FFF   or  # CJK Unified Ideographs
        0x3400 <= code <= 0x4DBF   or  # CJK Unified Ideographs Extension A
        0x20000 <= code <= 0x2A6DF or  # Extension B
        0x2A700 <= code <= 0x2B73F or  # Extension C
        0x2B740 <= code <= 0x2B81F or  # Extension D
        0x2B820 <= code <= 0x2CEAF or  # Extension E/F
        0xF900 <= code <= 0xFAFF   or  # CJK Compatibility Ideographs
        0x2F800 <= code <= 0x2FA1F     # CJK Compatibility Ideographs Supplement
    )


def find_chinese_in_file(path: str):
    p = Path(path)
    if not p.is_file():
        print(f"Error: {p} is not a file")
        sys.exit(1)

    text = p.read_text(encoding="utf-8", errors="replace")

    char_counts = {}

    for ch in text:
        if is_chinese_char(ch):
            char_counts[ch] = char_counts.get(ch, 0) + 1

    if not char_counts:
        print(f"No Chinese characters found in {p}")
        return

    print(f"Chinese characters found in {p}:")
    print(f"(unique: {len(char_counts)})\n")

    for ch, cnt in sorted(char_counts.items(), key=lambda x: x[0]):
        # Show char, its Unicode codepoint, and count
        print(f"'{ch}' (U+{ord(ch):04X})  count: {cnt}")


if __name__ == "__main__":
    filename = "../assessment_results_sanitized/scan_output_google.json"
    find_chinese_in_file(filename)