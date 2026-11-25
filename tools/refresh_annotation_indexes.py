#!/usr/bin/env python3
"""Refresh semantic name/call indexes after merging annotation proposals."""
from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def tsv_headers(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t").fieldnames or [])


def row_count(path: Path) -> int:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return max(0, sum(1 for _ in csv.reader(stream, delimiter="\t")) - 1)


def run(script: str, *args: str) -> None:
    subprocess.run([sys.executable, str(ROOT / "tools" / script), *args], cwd=ROOT, check=True)


def main() -> None:
    behavior = ROOT / "decompiled" / "function_behavior.tsv"
    headers = tsv_headers(behavior)
    if "direct_callee_addresses" not in headers or "dispatch_target_addresses" not in headers:
        # One-time bootstrap; later waves use the cached edge addresses.
        run("analyze_functions.py")

    run("demangle_symbols.py")
    run("refresh_behavior_names.py")
    run("index_command_callbacks.py")
    run("rank_annotation_targets.py", "--limit", "1000")
    run("rank_callback_targets.py")

    annotations = row_count(ROOT / "tools" / "data" / "function_annotations.tsv")
    prototypes = row_count(ROOT / "tools" / "data" / "function_prototype_candidates.tsv")
    fields = row_count(ROOT / "tools" / "data" / "field_annotations.tsv")
    doc = ROOT / "decompiled" / "SYMBOLS_AND_TYPES.md"
    text = doc.read_text(encoding="utf-8")
    import re
    text = re.sub(
        r"It currently contains \d+ named current-build routines and \d+ candidate",
        f"It currently contains {annotations} named current-build routines and {prototypes} candidate",
        text,
    )
    text = re.sub(r"contains \d+ typed candidate-field rows", f"contains {fields} typed candidate-field rows", text)
    doc.write_text(text, encoding="utf-8")
    print(f"Updated SYMBOLS_AND_TYPES.md counts: {annotations} names, {prototypes} prototypes, {fields} field rows.")


if __name__ == "__main__":
    main()
