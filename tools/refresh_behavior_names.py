#!/usr/bin/env python3
"""Refresh readable callee names from cached guest-address call edges."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BEHAVIOR = ROOT / "decompiled" / "function_behavior.tsv"
NAMES = ROOT / "decompiled" / "function_name_index.tsv"


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        return list(reader.fieldnames or []), list(reader)


def main() -> None:
    fields, rows = read_tsv(BEHAVIOR)
    if "direct_callee_addresses" not in fields or "dispatch_target_addresses" not in fields:
        raise SystemExit("Call-edge address cache missing; run tools/analyze_functions.py once first.")

    name_fields, name_rows = read_tsv(NAMES)
    if "readable_name" not in name_fields:
        raise SystemExit("Readable function-name index missing; run tools/demangle_symbols.py first.")
    names = {
        (row["module"], row["address"].lower()): (
            row.get("semantic_name") or row.get("readable_name") or row.get("generated_name") or row["address"]
        )
        for row in name_rows
    }

    for row in rows:
        module = row["module"]
        direct = [a for a in row.get("direct_callee_addresses", "").split(";") if a]
        dispatch = [a for a in row.get("dispatch_target_addresses", "").split(";") if a]
        row["direct_callees"] = ";".join(names.get((module, a.lower()), a) for a in direct)
        row["dispatch_targets"] = ";".join(names.get((module, a.lower()), a) for a in dispatch)
        row["name"] = names.get((module, row["address"].lower()), row.get("name", ""))

    with BEHAVIOR.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Refreshed readable names for {len(rows)} cached function behavior rows.")


if __name__ == "__main__":
    main()
