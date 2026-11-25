#!/usr/bin/env python3
"""Create a readable index of exported Itanium C++ symbols.

This uses the LLVM toolchain bundled with the project, so it needs no Python
packages or network access. It does not infer names for stripped functions.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import tempfile
from pathlib import Path


def read_tsv(path: Path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def parse_nm(text: str):
    rows = []
    for line in text.splitlines():
        parts = line.rsplit(None, 3)
        if len(parts) == 4 and parts[-3] == "U":
            rows.append(parts[0])
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    decomp = root / "decompiled"
    llvm_bin = root / "llvm" / "bin"
    clang = llvm_bin / "clang.exe"
    nm = llvm_bin / "llvm-nm.exe"
    if not clang.is_file() or not nm.is_file():
        raise SystemExit("Bundled clang.exe and llvm-nm.exe are required under llvm/bin")

    symbols = read_tsv(decomp / "elf_symbols.tsv")
    mangled = sorted({row["name"] for row in symbols if row["name"].startswith("_Z")})
    if not mangled:
        raise SystemExit("No Itanium-mangled symbols found in elf_symbols.tsv")

    # Assembler labels preserve the original symbol spelling. `llvm-nm` with
    # and without -C emits the same symbol-table order, giving an exact mapping
    # even when several ABI aliases demangle to identical display names.
    with tempfile.TemporaryDirectory(prefix="decomp-demangle-") as temp:
        temp_path = Path(temp)
        source = temp_path / "symbols.c"
        obj = temp_path / "symbols.o"
        with source.open("w", encoding="ascii", newline="\n") as stream:
            stream.write("/* generated; references only */\n")
            for i, name in enumerate(mangled):
                if not re.fullmatch(r"_[A-Za-z0-9_.$?@]+", name):
                    raise SystemExit(f"Unsupported character in symbol: {name!r}")
                stream.write(f'extern void s{i}(void) __asm__("{name}");\n')
                stream.write(f'void (* volatile ref_{i})(void) = s{i};\n')
        subprocess.run([str(clang), "-x", "c", "-c", str(source), "-o", str(obj)], check=True)
        raw = subprocess.run([str(nm), "--format=posix", "--no-sort", str(obj)],
                             check=True, capture_output=True, text=True, encoding="utf-8")
        pretty = subprocess.run([str(nm), "--demangle", "--format=posix", "--no-sort", str(obj)],
                                check=True, capture_output=True, text=True, encoding="utf-8")
        raw_names = parse_nm(raw.stdout)
        pretty_names = parse_nm(pretty.stdout)
        if raw_names != mangled:
            if set(raw_names) != set(mangled):
                raise SystemExit(f"Object symbol mismatch: {len(raw_names)} emitted for {len(mangled)} inputs")
            # Some object writers reorder symbol tables. Fall back to a mapping
            # by exact input order only when symbols remain unique.
            raise SystemExit("LLVM reordered symbols; refusing to write a mis-mapped index")
        if len(pretty_names) != len(mangled):
            raise SystemExit("LLVM demangler output did not match the raw symbol table")
        demangled = dict(zip(mangled, pretty_names))

    roles = (("_ZTI", "RTTI type_info object"), ("_ZTS", "RTTI type-name object"),
             ("_ZTV", "virtual-function table"), ("_ZTT", "virtual-table table"),
             ("_ZTC", "construction virtual table"), ("_ZTh", "virtual thunk"),
             ("_ZTv", "virtual thunk"), ("_ZTc", "covariant thunk"))
    out_rows = []
    for row in symbols:
        name = row["name"]
        if name not in demangled:
            continue
        role = next((label for prefix, label in roles if name.startswith(prefix)), "mangled C++ function or data symbol")
        out_rows.append({**row, "demangled_name": demangled[name], "symbol_role": role})

    output = decomp / "symbol_demangle.tsv"
    fields = ["module", "address", "name", "demangled_name", "symbol_role", "elf_kind",
              "elf_size", "binding", "defined"]
    with output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(out_rows)

    func_rows = read_tsv(decomp / "function_symbols.tsv")
    annotation_path = root / "tools" / "data" / "function_annotations.tsv"
    annotations = {}
    if annotation_path.exists():
        annotations = {(row["module"], int(row["address"], 16)): row
                       for row in read_tsv(annotation_path)}
    prototype_path = root / "tools" / "data" / "function_prototype_candidates.tsv"
    prototypes = {}
    if prototype_path.exists():
        prototypes = {(row["module"], int(row["address"], 16)): row
                      for row in read_tsv(prototype_path)}
    function_index = []
    for row in func_rows:
        raw_name = row["recovered_name"]
        annotation = annotations.get((row["module"], int(row["address"], 16)), {})
        prototype = prototypes.get((row["module"], int(row["address"], 16)), {})
        readable = (annotation.get("semantic_name") or
                    (demangled.get(raw_name, raw_name) if raw_name else row["generated_name"]))
        if prototype:
            prototype_status = f"candidate source prototype; confidence={prototype['confidence']}"
        elif not raw_name:
            prototype_status = "stripped internal function; prototype unknown"
        elif raw_name in demangled:
            prototype_status = "Itanium symbol encodes parameter types where present; return type may be omitted"
        else:
            prototype_status = "exact ELF function symbol; source prototype not encoded"
        function_index.append({
            "module": row["module"], "address": row["address"],
            "generated_name": row["generated_name"], "raw_elf_name": raw_name,
            "readable_name": readable, "name_evidence": row["name_evidence"],
            "elf_symbol_size": row["elf_symbol_size"],
            "recomp_wrapper_signature": row["recomp_wrapper_signature"],
            "prototype_status": prototype_status,
            "candidate_prototype": prototype.get("candidate_prototype", ""),
            "prototype_confidence": prototype.get("confidence", ""),
            "prototype_evidence": prototype.get("evidence", ""),
            "semantic_name": annotation.get("semantic_name", ""),
            "semantic_confidence": annotation.get("confidence", ""),
            "semantic_evidence": annotation.get("evidence", ""),
        })
    function_fields = ["module", "address", "generated_name", "raw_elf_name", "readable_name",
                       "name_evidence", "elf_symbol_size", "recomp_wrapper_signature", "prototype_status",
                       "candidate_prototype", "prototype_confidence", "prototype_evidence",
                       "semantic_name", "semantic_confidence", "semantic_evidence"]
    with (decomp / "function_name_index.tsv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=function_fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(function_index)

    type_roles = {"RTTI type_info object", "RTTI type-name object", "virtual-function table",
                  "virtual-table table", "construction virtual table"}
    type_rows = [row for row in out_rows if row["symbol_role"] in type_roles]
    with (decomp / "type_symbols.tsv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(type_rows)

    funcs_named = sum(bool(row["recovered_name"]) for row in func_rows)
    funcs_demangled = sum(bool(row["recovered_name"] in demangled) for row in func_rows)
    counts = {}
    for row in out_rows:
        counts[row["symbol_role"]] = counts.get(row["symbol_role"], 0) + 1
    manifest = {
        "schema_version": 1,
        "source": "decompiled/elf_symbols.tsv",
        "demangler": str(nm),
        "demangled_symbol_rows": len(out_rows),
        "functions_with_exact_exported_names": funcs_named,
        "functions_with_demangled_cpp_names": funcs_demangled,
        "symbol_role_counts": counts,
        "type_claim_limit": "RTTI/vtable names are exact symbol evidence; this does not recover object field layouts or stripped function prototypes.",
    }
    (decomp / "symbol_demangle.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(out_rows)} demangled symbol rows to {output}")
    print(f"Wrote {len(function_index)} function-name rows and {len(type_rows)} RTTI/vtable rows")
    print(f"Exact exported function names: {funcs_named}; demangled C++ function names: {funcs_demangled}")
    print("Symbol roles:", json.dumps(counts, sort_keys=True))


if __name__ == "__main__":
    main()
