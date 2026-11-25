#!/usr/bin/env python3
"""Index direct x0-relative memory fields in generated guest functions.

The result is mechanical evidence for structure recovery, not an automatic
structure declaration: x0 may be a pointer, scalar, or different object in
each function. Only explicit `ea = x0 + constant` accesses are included.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

FN_MARK = re.compile(rb"FN_ENTER\(0x([0-9a-fA-F]+)ull\);")
EA_X0_BLOCK = re.compile(
    rb"\{\s*uint64_t ea = (x[0-9]+) \+\s*(0x[0-9a-fA-F]+|[0-9]+)(?:ull)?;([^{}]*?)\}", re.S
)
MEMORY_OP = re.compile(rb"\b(LD|ST)(8|16|32|64)\(\s*ea(?:\s*\+\s*(0x[0-9a-fA-F]+|[0-9]+)(?:ull)?)?")
ASSIGNMENT = re.compile(rb"(?m)\b(x(?:1[9]|2[0-8]))\s*=\s*([^;\n]+);")


def arg0_alias_registers(body: bytes):
    """Return callee-saved registers assigned once from the incoming x0."""
    assignments = defaultdict(list)
    for match in ASSIGNMENT.finditer(body):
        rhs = re.sub(rb"\s+", b"", match.group(2))
        if b"c->x[" in rhs:  # initial saved-register load is not a local reassignment
            continue
        assignments[match.group(1)].append(rhs)
    aliases = set()
    for register, sources in assignments.items():
        if len(sources) == 1 and sources[0] in (b"x0", b"(uint64_t)(0ull|x0)"):
            aliases.add(register)
    return aliases


def read_tsv(path: Path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def write_tsv(path: Path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    decomp = root / "decompiled"
    name_rows = read_tsv(decomp / "function_name_index.tsv")
    names = {(row["module"], int(row["address"], 16)): row["readable_name"] for row in name_rows}
    module_fields = defaultdict(lambda: defaultdict(dict))
    profile = defaultdict(lambda: {"functions": set(), "registers": set(), "reads": 0, "writes": 0,
                                   "read_widths": set(), "write_widths": set()})
    function_count = 0

    for module in ("main", "sdk"):
        manifest = json.loads((decomp / module / "manifest.json").read_text(encoding="utf-8"))
        for chunk in manifest["chunks"]:
            data = (decomp / module / chunk).read_bytes()
            markers = list(FN_MARK.finditer(data))
            for i, marker in enumerate(markers):
                address = int(marker.group(1), 16)
                end = markers[i + 1].start() if i + 1 < len(markers) else len(data)
                body = data[marker.end():end]
                aliases = arg0_alias_registers(body)
                by_base_offset = defaultdict(lambda: {"reads": 0, "writes": 0,
                                                      "read_widths": set(), "write_widths": set()})
                for block in EA_X0_BLOCK.finditer(body):
                    base_register = block.group(1)
                    if base_register != b"x0" and base_register not in aliases:
                        continue
                    provenance = "direct_x0" if base_register == b"x0" else "single_assignment_x0_alias"
                    base_offset = int(block.group(2), 0)
                    for access in MEMORY_OP.finditer(block.group(3)):
                        op = access.group(1).decode("ascii")
                        width = int(access.group(2)) // 8
                        inner = int(access.group(3), 0) if access.group(3) else 0
                        offset = base_offset + inner
                        key = (module, provenance, offset)
                        entry = by_base_offset[(base_register.decode("ascii"), provenance, offset)]
                        entry["writes" if op == "ST" else "reads"] += 1
                        entry["write_widths" if op == "ST" else "read_widths"].add(width)
                        total = profile[key]
                        total["functions"].add(address)
                        total["registers"].add(base_register.decode("ascii"))
                        total["writes" if op == "ST" else "reads"] += 1
                        total["write_widths" if op == "ST" else "read_widths"].add(width)
                for (base_register, provenance, offset), entry in by_base_offset.items():
                    module_fields[module][address][(base_register, provenance, offset)] = entry
                function_count += 1

    rows = []
    for module, functions in module_fields.items():
        for address, offsets in functions.items():
            for (base_register, provenance, offset), entry in sorted(offsets.items()):
                rows.append({
                    "module": module, "address": f"0x{address:x}",
                    "function_name": names.get((module, address), f"f_{address:x}"),
                    "base_register": base_register, "base_provenance": provenance,
                    "arg0_offset": f"0x{offset:x}", "reads": entry["reads"], "writes": entry["writes"],
                    "read_width_bytes": ",".join(map(str, sorted(entry["read_widths"]))),
                    "write_width_bytes": ",".join(map(str, sorted(entry["write_widths"]))),
                })
    field_path = decomp / "arg0_memory_fields.tsv"
    write_tsv(field_path, ["module", "address", "function_name", "base_register", "base_provenance",
                           "arg0_offset", "reads", "writes",
                           "read_width_bytes", "write_width_bytes"], rows)

    summary_rows = []
    for (module, provenance, offset), entry in sorted(profile.items()):
        summary_rows.append({
            "module": module, "base_provenance": provenance, "arg0_offset": f"0x{offset:x}",
            "functions": len(entry["functions"]), "loads": entry["reads"], "stores": entry["writes"],
            "base_registers": ",".join(sorted(entry["registers"])),
            "read_width_bytes": ",".join(map(str, sorted(entry["read_widths"]))),
            "write_width_bytes": ",".join(map(str, sorted(entry["write_widths"]))),
            "interpretation": "raw direct x0-relative access frequency; not a confirmed shared structure field",
        })
    profile_path = decomp / "arg0_offset_profile.tsv"
    write_tsv(profile_path, ["module", "base_provenance", "arg0_offset", "functions", "loads", "stores",
                             "base_registers", "read_width_bytes", "write_width_bytes", "interpretation"], summary_rows)

    manifest = {
        "schema_version": 1,
        "functions_scanned": function_count,
        "function_field_rows": len(rows),
        "unique_module_offsets": len(summary_rows),
        "scope": "explicit x0 + constant memory accesses and accesses through callee-saved registers assigned once from x0",
        "limitation": "x0 does not have one global type; alias recovery is conservative and frequencies are triage evidence, not proof of shared structure fields",
    }
    (decomp / "arg0_memory_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Scanned {function_count} functions; wrote {len(rows)} function-offset rows and "
          f"{len(summary_rows)} module-offset profiles.")
    print(f"Outputs: {field_path} and {profile_path}")


if __name__ == "__main__":
    main()
