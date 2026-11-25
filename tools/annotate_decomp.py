#!/usr/bin/env python3
"""Attach recoverable NSO symbols to generated recomp decomp output.

Run after recomp/gen.py:
  python tools/annotate_decomp.py --root .

The generated C stays address-based. Exact exported ELF function names are
inserted as comments above their wrappers, and TSV indexes cover every
decompiled function plus every named ELF symbol. The ELF symbol kind and size
are metadata, not recovered source-language prototypes or struct layouts.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path


def load_modules(root: Path):
    sys.path.insert(0, str(root / "recomp"))
    from nso import Nso  # pylint: disable=import-outside-toplevel

    exefs = root / "MLBTS" / "game" / "exefs"
    decomp = root / "decompiled"
    modules = {}
    for name in ("main", "sdk"):
        manifest = __import__("json").loads((decomp / name / "manifest.json").read_text(encoding="utf-8"))
        base = int(manifest["base"], 16)
        table = (decomp / name / f"{name}_table.c").read_text(encoding="utf-8")
        addrs = sorted({int(v, 16) for v in re.findall(r"\bf_([0-9a-fA-F]+)\b", table)})
        nso = Nso(str(exefs / name))
        exports = {}
        all_symbols = []
        for raw_name, info, shndx, value, size in nso.syms:
            if not raw_name:
                continue
            kind_id = info & 0xF
            kind = {0: "NOTYPE", 1: "OBJECT", 2: "FUNC", 3: "SECTION", 4: "FILE", 6: "TLS"}.get(
                kind_id, f"ELF_{kind_id}"
            )
            record = {
                "module": name,
                "address": base + value,
                "name": raw_name,
                "elf_kind": kind,
                "elf_size": size,
                "binding": {0: "LOCAL", 1: "GLOBAL", 2: "WEAK"}.get(info >> 4, f"ELF_{info >> 4}"),
                "defined": bool(shndx),
            }
            all_symbols.append(record)
            if shndx and kind_id == 2:
                exports.setdefault(base + value, []).append(record)
        modules[name] = {"base": base, "addrs": addrs, "exports": exports, "symbols": all_symbols, "decomp": decomp}
    return modules


def write_tsv(path: Path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def safe_comment(value: str) -> str:
    return value.replace("\r", " ").replace("\n", " ").replace("*/", "* /")


def annotate_c_files(module_name: str, module, dry_run: bool):
    name_by_addr = {}
    for addr, records in module["exports"].items():
        # Prefer a non-underscore public name if aliases share one address.
        record = sorted(records, key=lambda r: (r["name"].startswith("_"), r["name"]))[0]
        name_by_addr[addr] = record
    decomp_dir = module["decomp"] / module_name
    pat = re.compile(rb"(?m)^(void f_([0-9a-fA-F]+)\(Cpu \*c\) \{)$")
    changed, annotated = [], 0
    for source in sorted(decomp_dir.glob(f"{module_name}_[0-9][0-9][0-9][0-9].c")):
        data = source.read_bytes()
        def add_comment(match):
            nonlocal annotated
            addr = int(match.group(2), 16)
            record = name_by_addr.get(addr)
            if record is None:
                return match.group(0)
            annotated += 1
            previous_line_end = match.start() - 1
            previous_line_start = data.rfind(b"\n", 0, previous_line_end) + 1
            if b"// NSO symbol:" in data[previous_line_start:previous_line_end]:
                return match.group(0)
            line = (f"// NSO symbol: {safe_comment(record['name'])} | ELF FUNC | size 0x{record['elf_size']:x}\n").encode("utf-8")
            return line + match.group(0)
        updated = pat.sub(add_comment, data)
        if updated != data:
            changed.append(source.name)
            if not dry_run:
                source.write_bytes(updated)
    return annotated, changed


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1], help="recomp project root")
    ap.add_argument("--dry-run", action="store_true", help="write indexes but leave generated C unchanged")
    args = ap.parse_args()
    root = args.root.resolve()
    modules = load_modules(root)

    function_fields = ["module", "address", "generated_name", "recovered_name", "name_evidence", "function_type",
                       "elf_kind", "elf_symbol_size", "recomp_wrapper_signature", "original_prototype"]
    function_rows = []
    symbol_rows = []
    for name, module in modules.items():
        addrs = module["addrs"]
        for i, addr in enumerate(addrs):
            records = module["exports"].get(addr, [])
            symbol = sorted(records, key=lambda r: (r["name"].startswith("_"), r["name"]))[0] if records else None
            function_rows.append({
                "module": name,
                "address": f"0x{addr:x}",
                "generated_name": f"f_{addr:x}",
                "recovered_name": symbol["name"] if symbol else "",
                "name_evidence": "exact NSO exported ELF symbol" if symbol else "address-derived; no exact exported function symbol",
                "function_type": "AArch64 guest function; source return/parameter types unknown",
                "elf_kind": "FUNC" if symbol else "",
                "elf_symbol_size": f"0x{symbol['elf_size']:x}" if symbol else "",
                "recomp_wrapper_signature": f"void f_{addr:x}(Cpu *c)",
                "original_prototype": "unknown; Cpu* is the host recomp wrapper signature" if not symbol else "unknown; ELF exports do not encode C prototypes",
            })
        for symbol in module["symbols"]:
            symbol_rows.append({
                "module": name,
                "address": f"0x{symbol['address']:x}" if symbol["defined"] else "",
                "name": symbol["name"],
                "elf_kind": symbol["elf_kind"],
                "elf_size": f"0x{symbol['elf_size']:x}",
                "binding": symbol["binding"],
                "defined": str(symbol["defined"]).lower(),
            })

    decomp = root / "decompiled"
    write_tsv(decomp / "function_symbols.tsv", function_fields, function_rows)
    write_tsv(decomp / "elf_symbols.tsv", ["module", "address", "name", "elf_kind", "elf_size", "binding", "defined"], symbol_rows)

    totals = {}
    for name, module in modules.items():
        annotated, changed = annotate_c_files(name, module, args.dry_run)
        totals[name] = {"decompiled_functions": len(module["addrs"]), "exact_named_functions": annotated,
                        "changed_chunks": len(changed)}
    print(f"Wrote {len(function_rows)} function records and {len(symbol_rows)} ELF symbol records.")
    for name, counts in totals.items():
        print(f"{name}: {counts['exact_named_functions']} function definitions annotated in "
              f"{counts['changed_chunks']} C chunks ({counts['decompiled_functions']} total functions).")
    print("Types are ELF symbol kinds and recomp wrapper signatures; original source prototypes remain unknown.")


if __name__ == "__main__":
    main()
