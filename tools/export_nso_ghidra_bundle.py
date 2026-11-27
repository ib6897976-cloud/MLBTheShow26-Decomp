#!/usr/bin/env python3
"""Export a local Switch NSO as a raw Ghidra image plus symbols/unwind seeds.

The NSO/game binary and generated bundle are local artifacts; this script only
exports files into the requested output directory. Load image.bin in Ghidra as
AArch64 little-endian raw binary at the printed image base, then run the
included apply_symbols.py script against that program.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "recomp"))
from nso import Nso  # noqa: E402
from module import Module  # noqa: E402

DEFAULT_BASE = 0x7000000000


def clean_name(name: str, fallback: str) -> str:
    value = re.sub(r"[^A-Za-z0-9_$?@.]", "_", name).strip("_")
    if not value or value[0].isdigit():
        value = "sym_" + value
    return value[:240] or fallback


def load_annotation_names(path: Path) -> dict[str, tuple[str, str]]:
    result = {}
    if not path.is_file():
        return result
    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            if row.get("module") != "main":
                continue
            name = (row.get("semantic_name") or "").strip()
            if name:
                result[row["address"].lower()] = (name, row.get("semantic_confidence", ""))
    return result


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--nso", type=Path, default=ROOT / "MLBTS/game/exefs/main")
    ap.add_argument("--output", type=Path, default=ROOT / "temp/ghidra_main_bundle")
    ap.add_argument("--base", type=lambda x: int(x, 0), default=DEFAULT_BASE)
    args = ap.parse_args()

    nso = Nso(str(args.nso))
    mod = Module("main", str(args.nso), args.base)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "image.bin").write_bytes(nso.image)

    # Keep source symbol names where present, and add accepted semantic labels.
    labels: dict[int, dict] = {}
    annotations = load_annotation_names(ROOT / "tools/data/function_annotations.tsv")
    for name, info, shndx, value, size in nso.syms:
        if not name or not shndx:
            continue
        address = args.base + value
        labels[address] = {
            "address": address, "name": name,
            "kind": "function" if (info & 0xF) == 2 else "object",
            "size": size, "confidence": "elf",
        }
    for address_text, (name, confidence) in annotations.items():
        address = int(address_text, 16)
        if args.base + nso.text[0] <= address < args.base + nso.text[0] + nso.text[1]:
            labels[address] = {
                "address": address, "name": name, "kind": "semantic_function",
                "size": 0, "confidence": confidence,
            }

    for address in mod.eh_frame_functions():
        if args.base + nso.text[0] <= address < args.base + nso.text[0] + nso.text[1]:
            labels.setdefault(address, {
                "address": address, "name": f"unwind_{address:x}",
                "kind": "unwind_function_start", "size": 0, "confidence": "eh_frame_hdr",
            })

    symbols_path = args.output / "symbols.tsv"
    with symbols_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerow(["address", "name", "kind", "size_bytes", "confidence"])
        for item in sorted(labels.values(), key=lambda x: x["address"]):
            writer.writerow([
                f"0x{item['address']:x}", clean_name(item["name"], f"sym_{item['address']:x}"),
                item["kind"], item["size"], item["confidence"],
            ])

    metadata = {
        "input": str(args.nso), "build_id": nso.build_id,
        "image_base": f"0x{args.base:x}", "image_size": f"0x{nso.size:x}",
        "segments": {
            "text": {"offset": f"0x{nso.text[0]:x}", "size": f"0x{nso.text[1]:x}"},
            "rodata": {"offset": f"0x{nso.rodata[0]:x}", "size": f"0x{nso.rodata[1]:x}"},
            "data": {"offset": f"0x{nso.data[0]:x}", "size": f"0x{nso.data[1]:x}"},
            "bss_size": f"0x{nso.bss_size:x}",
        },
        "eh_frame": {"start": f"0x{nso.eh_start:x}", "end": f"0x{nso.eh_end:x}"},
        "nso_dynamic_symbols": len(nso.syms), "exports": len(nso.exports()),
        "imports": len(nso.imports()), "unwind_function_starts": len(mod.eh_frame_functions()),
        "labels_exported": len(labels), "architecture": "AArch64 little-endian",
        "relocations_applied": False,
        "image_note": "NSO segments are decompressed into a zero-filled image; dynamic relocations are not applied.",
        "load_instructions": "Import image.bin as raw AArch64:LE at image_base; run apply_symbols.py in that program.",
    }
    (args.output / "manifest.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    (args.output / "apply_symbols.py").write_text(GHIDRA_SCRIPT, encoding="utf-8")
    print(json.dumps(metadata, indent=2))
    print(f"Bundle: {args.output}")


GHIDRA_SCRIPT = r'''# Ghidra Jython script; open the raw image.bin program first.
import csv
from ghidra.program.model.symbol import SourceType

path = askFile("Select symbols.tsv from the exported NSO bundle", "Open")
count = 0
created = 0
with open(path.getAbsolutePath(), "r") as stream:
    rows = csv.DictReader(stream, delimiter="\t")
    for row in rows:
        address = toAddr(int(row["address"], 16))
        name = row["name"]
        kind = row["kind"]
        try:
            current = getSymbolAt(address)
            if current is None or current.getSource() == SourceType.DEFAULT:
                createLabel(address, name, True)
            if kind in ("function", "semantic_function", "unwind_function_start"):
                if getFunctionAt(address) is None:
                    disassemble(address)
                    createFunction(address, name)
                    created += 1
            count += 1
        except Exception as exc:
            print("Skipped %s %s: %s" % (row["address"], name, exc))
print("Applied %d labels; created %d functions" % (count, created))
'''


if __name__ == "__main__":
    main()
