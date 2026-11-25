#!/usr/bin/env python3
"""Build a whole-decomp, evidence-only function behavior index.

Run after tools/annotate_decomp.py:
  python tools/analyze_functions.py --root .

The report records call edges, dispatch targets, memory operation families,
and candidate references to printable NSO rodata strings. It intentionally does
not turn these observations into unsupported semantic claims.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

FN_MARK = re.compile(rb"FN_ENTER\(0x([0-9a-fA-F]+)ull\);")
DIRECT_CALL = re.compile(rb"\bf_([0-9a-fA-F]+)\(c\);")
DISPATCH_LINE = re.compile(rb"(?m)^([^\n]*rt_dispatch\(c\);[^\n]*)$")
PC_CONST = re.compile(rb"c->pc\s*=\s*0x([0-9a-fA-F]+)ull")
GUEST_REGISTER = rb"(?:x[0-9]+|c->x\[[0-9]+\])"
ADDRESS_ASSIGN = re.compile(
    rb"(?m)^    (?P<reg>" + GUEST_REGISTER + rb") = \(uint64_t\)\(0x(?P<base>[0-9a-fA-F]+)ull\);"
    rb"(?:\r?\n    " + GUEST_REGISTER + rb" = \(uint64_t\)\((?P=reg) \+ 0x(?P<offset>[0-9a-fA-F]+)ull\);)?"
)
LOAD = re.compile(rb"\bLD(?:8|16|32|64)\(")
STORE = re.compile(rb"\bST(?:8|16|32|64)\(")
STRING = re.compile(rb"[\x20-\x7e]{4,}\x00")


def tsv_read(path):
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def write_tsv(path, rows):
    fields = ["module", "address", "name", "callers", "direct_callees", "dispatch_targets",
              "direct_callee_addresses", "dispatch_target_addresses",
              "loads", "stores", "dispatch_sites", "indirect_dispatch_sites", "rodata_strings", "evidence_summary"]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def clean_cell(s):
    return str(s).replace("\t", " ").replace("\r", " ").replace("\n", " ").replace(";", ",")


def rodata_candidates(body, strings):
    """Recognize direct addresses and adjacent lifted page-plus-offset pairs."""
    found = set()
    for assignment in ADDRESS_ASSIGN.finditer(body):
        address = int(assignment["base"], 16)
        offset = assignment["offset"]
        if address & 0xfff == 0:
            # A bare page base is ambiguous: ADRP alone does not identify a string.
            if offset is None or int(offset, 16) >= 0x1000:
                continue
            address += int(offset, 16)
        value = strings.get(address)
        if value:
            found.add(value)
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1], help="recomp project root")
    ap.add_argument("--limit", type=int, default=0, help="optional cap for exploratory runs")
    args = ap.parse_args()
    root = args.root.resolve()
    decomp = root / "decompiled"
    modules = {}
    by_addr = {}
    for mod in ("main", "sdk"):
        manifest = json.loads((decomp / mod / "manifest.json").read_text(encoding="utf-8"))
        base = int(manifest["base"], 16)
        modules[mod] = {"base": base, "manifest": manifest, "calls": defaultdict(set), "dispatch": defaultdict(set),
                        "loads": defaultdict(int), "stores": defaultdict(int), "dsites": defaultdict(int),
                        "indirect": defaultdict(int), "strings": defaultdict(set), "callers": defaultdict(set)}
    funcs = tsv_read(decomp / "function_symbols.tsv")
    names = {}
    readable_names = {}
    readable_index = decomp / "function_name_index.tsv"
    if readable_index.exists():
        for f in tsv_read(readable_index):
            readable_names[int(f["address"], 16)] = (
                f.get("semantic_name") or f["readable_name"]
            )
    for f in funcs:
        addr = int(f["address"], 16)
        names[addr] = readable_names.get(addr, f["recovered_name"] or f["generated_name"])
        by_addr[addr] = f["module"]

    # Recover printable strings and their absolute guest addresses from each NSO's rodata.
    sys.path.insert(0, str(root / "recomp"))
    from nso import Nso  # pylint: disable=import-outside-toplevel
    for mod, info in modules.items():
        nso = Nso(str(root / "MLBTS" / "game" / "exefs" / mod))
        ro_off, ro_size = nso.rodata
        ro = nso.image[ro_off:ro_off + ro_size]
        strings = {}
        for m in STRING.finditer(ro):
            value = m.group(0)[:-1].decode("ascii", "replace").strip()
            if value:
                strings[info["base"] + ro_off + m.start()] = value
        info["rodata_strings"] = strings

    # Every FN_ENTER marks one original guest function in the generated C.
    for mod, info in modules.items():
        for chunk in info["manifest"]["chunks"]:
            data = (decomp / mod / chunk).read_bytes()
            marks = list(FN_MARK.finditer(data))
            for i, mark in enumerate(marks):
                addr = int(mark.group(1), 16)
                end = marks[i + 1].start() if i + 1 < len(marks) else len(data)
                body = data[mark.end():end]
                direct = {int(m.group(1), 16) for m in DIRECT_CALL.finditer(body)}
                direct.discard(addr)
                info["calls"][addr].update(direct)
                for target in direct:
                    if target in by_addr:
                        modules[by_addr[target]]["callers"][target].add(addr)
                for line in DISPATCH_LINE.finditer(body):
                    targets = {int(m.group(1), 16) for m in PC_CONST.finditer(line.group(1))}
                    if targets:
                        info["dispatch"][addr].update(targets)
                    else:
                        info["indirect"][addr] += 1
                    info["dsites"][addr] += 1
                info["loads"][addr] += len(LOAD.findall(body))
                info["stores"][addr] += len(STORE.findall(body))
                references = rodata_candidates(body, info["rodata_strings"])
                if references:
                    info["strings"][addr].update(references)

    rows = []
    for f in funcs:
        addr = int(f["address"], 16)
        mod = f["module"]
        info = modules[mod]
        direct = sorted(info["calls"].get(addr, ()))
        dispatch = sorted(info["dispatch"].get(addr, ()))
        callers = sorted(info["callers"].get(addr, ()))
        strings = sorted(info["strings"].get(addr, ()))
        named_direct = [names.get(a, f"0x{a:x}") for a in direct[:24]]
        named_dispatch = [names.get(a, f"0x{a:x}") for a in dispatch[:24]]
        reads, writes = info["loads"].get(addr, 0), info["stores"].get(addr, 0)
        dispatch_sites = info["dsites"].get(addr, 0)
        indirect = info["indirect"].get(addr, 0)
        summary = (f"{len(direct)} direct callees; {len(dispatch)} static dispatch targets; "
                   f"{reads} lifted loads; {writes} lifted stores; {len(strings)} candidate rodata strings")
        rows.append({
            "module": mod,
            "address": f"0x{addr:x}",
            "name": clean_cell(names.get(addr, f["recovered_name"] or f["generated_name"])),
            "callers": ";".join(f"0x{x:x}" for x in callers[:24]) + (";..." if len(callers) > 24 else ""),
            "direct_callees": ";".join(clean_cell(x) for x in named_direct) + (";..." if len(direct) > 24 else ""),
            "dispatch_targets": ";".join(clean_cell(x) for x in named_dispatch) + (";..." if len(dispatch) > 24 else ""),
            "direct_callee_addresses": ";".join(f"0x{x:x}" for x in direct),
            "dispatch_target_addresses": ";".join(f"0x{x:x}" for x in dispatch),
            "loads": reads,
            "stores": writes,
            "dispatch_sites": dispatch_sites,
            "indirect_dispatch_sites": indirect,
            "rodata_strings": ";".join(clean_cell(s) for s in strings[:16]) + (";..." if len(strings) > 16 else ""),
            "evidence_summary": summary,
        })
        if args.limit and len(rows) >= args.limit:
            break
    out = decomp / "function_behavior.tsv"
    write_tsv(out, rows)
    print(f"Wrote behavior observations for {len(rows)} functions to {out}.")
    print("These are static evidence summaries; they do not claim recovered source-level intent.")


if __name__ == "__main__":
    main()
