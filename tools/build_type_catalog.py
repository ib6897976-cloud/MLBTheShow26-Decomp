#!/usr/bin/env python3
"""Consolidate exported RTTI and vtable evidence into one row per type name."""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

PREFIXES = (
    ("RTTI type_info object", "typeinfo for "),
    ("RTTI type-name object", "typeinfo name for "),
    ("virtual-function table", "vtable for "),
    ("virtual-table table", "VTT for "),
    ("construction virtual table", "construction vtable for "),
)
ROLE_COLUMNS = {
    "RTTI type_info object": "has_rtti",
    "RTTI type-name object": "has_type_name",
    "virtual-function table": "has_vtable",
    "virtual-table table": "has_vtt",
    "construction virtual table": "has_construction_vtable",
}


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
    source = root / "decompiled" / "type_symbols.tsv"
    grouped = defaultdict(list)
    for row in read_tsv(source):
        role = row["symbol_role"]
        prefix = dict(PREFIXES).get(role)
        if not prefix:
            continue
        demangled = row["demangled_name"]
        entity = demangled[len(prefix):] if demangled.startswith(prefix) else demangled
        grouped[(row["module"], entity)].append(row)

    rows = []
    role_counts = defaultdict(int)
    for (module, entity), evidence in sorted(grouped.items()):
        present = {row["symbol_role"] for row in evidence}
        for role in present:
            role_counts[f"{module}:{role}"] += 1
        row = {
            "module": module,
            "type_name": entity,
            "has_rtti": str("RTTI type_info object" in present).lower(),
            "has_type_name": str("RTTI type-name object" in present).lower(),
            "has_vtable": str("virtual-function table" in present).lower(),
            "has_vtt": str("virtual-table table" in present).lower(),
            "has_construction_vtable": str("construction virtual table" in present).lower(),
            "evidence_count": len(evidence),
            "evidence_symbols": json.dumps([
                {"address": item["address"], "symbol": item["name"], "demangled": item["demangled_name"],
                 "role": item["symbol_role"], "size": item["elf_size"]}
                for item in sorted(evidence, key=lambda item: (item["symbol_role"], item["address"]))
            ], ensure_ascii=False, separators=(",", ":")),
        }
        rows.append(row)

    fields = ["module", "type_name", "has_rtti", "has_type_name", "has_vtable", "has_vtt",
              "has_construction_vtable", "evidence_count", "evidence_symbols"]
    output = root / "decompiled" / "type_catalog.tsv"
    write_tsv(output, fields, rows)

    # Associate exact exported C++ methods with RTTI/vtable class names when
    # the demangled spelling has an unambiguous class-name prefix.
    functions = read_tsv(root / "decompiled" / "function_name_index.tsv")
    types_by_module = defaultdict(list)
    for row in rows:
        types_by_module[row["module"]].append(row["type_name"])
    for module in types_by_module:
        types_by_module[module].sort(key=len, reverse=True)
    methods = []
    method_counts = defaultdict(int)
    for function in functions:
        raw = function["raw_elf_name"]
        if not raw.startswith("_Z"):
            continue
        readable = function["readable_name"]
        for type_name in types_by_module[function["module"]]:
            prefix = type_name + "::"
            if readable.startswith(prefix):
                method_name = readable[len(prefix):]
                first_call = method_name.find("(")
                nested_class = method_name.find("::")
                if nested_class >= 0 and (first_call < 0 or nested_class < first_call):
                    # A longer nested-class type may have no exported RTTI.
                    # Do not misattribute its methods to the outer class.
                    continue
                methods.append({
                    "module": function["module"], "type_name": type_name,
                    "method": method_name, "address": function["address"],
                    "generated_name": function["generated_name"], "raw_elf_name": raw,
                    "prototype_status": function["prototype_status"],
                })
                method_counts[(function["module"], type_name)] += 1
                break
    write_tsv(root / "decompiled" / "type_methods.tsv",
              ["module", "type_name", "method", "address", "generated_name", "raw_elf_name",
               "prototype_status"], methods)

    memory_by_function = defaultdict(list)
    memory_path = root / "decompiled" / "arg0_memory_fields.tsv"
    if memory_path.exists():
        for access in read_tsv(memory_path):
            memory_by_function[(access["module"], access["address"])].append(access)
    field_profiles = defaultdict(lambda: {"functions": set(), "methods": set(), "reads": 0, "writes": 0,
                                          "read_widths": set(), "write_widths": set()})
    for method in methods:
        for access in memory_by_function.get((method["module"], method["address"]), ()):
            key = (method["module"], method["type_name"], access["arg0_offset"])
            profile = field_profiles[key]
            profile["functions"].add(method["address"])
            profile["methods"].add(method["method"])
            profile["reads"] += int(access["reads"])
            profile["writes"] += int(access["writes"])
            if access["read_width_bytes"]:
                profile["read_widths"].update(map(int, access["read_width_bytes"].split(",")))
            if access["write_width_bytes"]:
                profile["write_widths"].update(map(int, access["write_width_bytes"].split(",")))
    field_rows = []
    for (module, type_name, offset), profile in sorted(field_profiles.items()):
        samples = sorted(profile["methods"])
        field_rows.append({
            "module": module, "type_name": type_name, "arg0_offset": offset,
            "method_count": len(profile["methods"]), "function_count": len(profile["functions"]),
            "loads": profile["reads"], "stores": profile["writes"],
            "read_width_bytes": ",".join(map(str, sorted(profile["read_widths"]))),
            "write_width_bytes": ",".join(map(str, sorted(profile["write_widths"]))),
            "sample_methods": json.dumps(samples[:12], ensure_ascii=False),
            "interpretation": "candidate first-argument field access in an exported class method; receiver status is unverified",
        })
    write_tsv(root / "decompiled" / "type_class_field_candidates.tsv",
              ["module", "type_name", "arg0_offset", "method_count", "function_count", "loads", "stores",
               "read_width_bytes", "write_width_bytes", "sample_methods", "interpretation"], field_rows)

    by_module = defaultdict(int)
    for row in rows:
        by_module[row["module"]] += 1
    manifest = {
        "schema_version": 1,
        "source": "decompiled/type_symbols.tsv",
        "unique_module_type_names": len(rows),
        "types_by_module": dict(sorted(by_module.items())),
        "types_by_module_and_role": dict(sorted(role_counts.items())),
        "class_method_associations": len(methods),
        "classes_with_named_methods": len(method_counts),
        "class_field_candidate_rows": len(field_rows),
        "type_layouts_recovered": 0,
        "note": "Names and RTTI/vtable evidence only; this catalog does not claim member layouts.",
    }
    (root / "decompiled" / "type_catalog.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} unique module/type names to {output}")
    print(f"Associated {len(methods)} exact C++ methods with {len(method_counts)} RTTI/vtable types")
    print("Types by module:", json.dumps(dict(sorted(by_module.items())), sort_keys=True))


if __name__ == "__main__":
    main()
