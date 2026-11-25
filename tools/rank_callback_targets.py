#!/usr/bin/env python3
"""Rank unannotated functions with named adjacent main-NSO callback records."""
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CALLBACKS = ROOT / "decompiled" / "command_callback_candidates.tsv"
BEHAVIOR = ROOT / "decompiled" / "function_behavior.tsv"
ANNOTATIONS = ROOT / "tools" / "data" / "function_annotations.tsv"
DEFAULT_OUTPUT = ROOT / "tools" / "data" / "callback_target_queue.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="	"))


def write_tsv(path: Path, columns: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, delimiter="	", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    known = {
        row["address"].lower()
        for row in read_tsv(ANNOTATIONS)
        if row["module"] == "main" and row["semantic_name"]
    }
    behavior = {
        row["address"].lower(): row
        for row in read_tsv(BEHAVIOR)
        if row["module"] == "main"
    }
    registrations: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in read_tsv(CALLBACKS):
        if row["adjacent_record"] == "1":
            registrations[row["address"].lower()].append(row)

    targets = []
    for address, records in registrations.items():
        if address in known or address not in behavior:
            continue
        observed = behavior[address]
        commands = sorted({row["command"] for row in records})
        caller_count = len([
            caller for caller in observed["callers"].split(";")
            if caller and caller != "..."
        ])
        score = (
            len(records) * 1000
            + min(caller_count, 99) * 25
            + min(int(observed["loads"]) + int(observed["stores"]), 999)
        )
        targets.append({
            "score": score,
            "module": "main",
            "address": address,
            "generated_name": observed["name"],
            "commands": ";".join(commands),
            "registration_count": len(records),
            "adjacent_record_count": len(records),
            "caller_count_observed": caller_count,
            "direct_callees": observed["direct_callees"],
            "lifted_loads": observed["loads"],
            "lifted_stores": observed["stores"],
            "resolved_rodata_strings": observed["rodata_strings"],
            "callback_slots": ";".join(sorted({row["callback_slot"] for row in records})),
            "name_slots": ";".join(sorted({row["name_slot"] for row in records})),
        })

    targets.sort(key=lambda row: (-int(row["score"]), str(row["address"])))
    output = [
        {"rank": rank, **row}
        for rank, row in enumerate(targets, 1)
    ]
    columns = [
        "rank", "score", "module", "address", "generated_name", "commands",
        "registration_count", "adjacent_record_count", "caller_count_observed",
        "direct_callees", "lifted_loads", "lifted_stores",
        "resolved_rodata_strings", "callback_slots", "name_slots",
    ]
    write_tsv(args.output, columns, output)
    print(f"Ranked {len(output)} unannotated registered callback functions into {args.output}")


if __name__ == "__main__":
    main()
