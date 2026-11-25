#!/usr/bin/env python3
"""Build compact, source-linked evidence packets for batches of guest functions."""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEF = re.compile(r"^void f_([0-9a-fA-F]+)\(Cpu \*c\) \{$")
MARK = re.compile(r"^\s*FN_ENTER\(0x([0-9a-fA-F]+)ull\);\s*$")
DIRECT = re.compile(r"\bf_([0-9a-fA-F]+)\(c\);")
ADDR_ASSIGN = re.compile(
    r"(?m)^    (?P<reg>(?:x[0-9]+|c->x\[[0-9]+\])) = \(uint64_t\)\(0x(?P<base>[0-9a-fA-F]+)ull\);"
    r"(?:\r?\n    (?:x[0-9]+|c->x\[[0-9]+\]) = \(uint64_t\)\((?P=reg) \+ 0x(?P<offset>[0-9a-fA-F]+)ull\);)?"
)
PRINTABLE = re.compile(rb"[\x20-\x7e]{4,}\x00")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def index_bodies() -> dict[str, dict]:
    result = {}
    for path in sorted((ROOT / "decompiled/main").glob("main_[0-9][0-9][0-9][0-9].c")):
        lines = path.read_text(encoding="utf-8").splitlines()
        i = 0
        while i < len(lines):
            match = DEF.match(lines[i])
            if not match:
                i += 1
                continue
            address = f"0x{int(match.group(1), 16):x}"
            start = i + 1
            depth = 1
            j = i + 1
            while j < len(lines) and depth:
                depth += lines[j].count("{") - lines[j].count("}")
                j += 1
            result[address] = {"file": path.name, "start": start, "end": j, "lines": lines[start - 1:j]}
            i = j
    return result


def load_strings() -> dict[int, str]:
    sys.path.insert(0, str(ROOT / "recomp"))
    from nso import Nso  # pylint: disable=import-outside-toplevel

    manifest = json.loads((ROOT / "decompiled/main/manifest.json").read_text(encoding="utf-8"))
    base = int(manifest["base"], 16)
    nso = Nso(str(ROOT / "MLBTS/game/exefs/main"))
    offset, size = nso.rodata
    rodata = nso.image[offset:offset + size]
    strings = {}
    for match in PRINTABLE.finditer(rodata):
        value = match.group(0)[:-1].decode("ascii", "replace").strip()
        if value:
            strings[base + offset + match.start()] = value
    return strings


def excerpt(body: dict, resolved: list[dict], max_lines: int) -> list[dict]:
    lines = body["lines"]
    if len(lines) <= max_lines:
        return [{"line": body["start"] + i, "text": line} for i, line in enumerate(lines)]
    keep = set(range(min(10, len(lines)))) | set(range(max(0, len(lines) - 8), len(lines)))
    for i, line in enumerate(lines):
        if DIRECT.search(line) or "rt_dispatch" in line or "LD" in line or "ST" in line:
            keep.update(range(max(0, i - 1), min(len(lines), i + 2)))
    for item in resolved:
        idx = item["body_line"] - body["start"]
        keep.update(range(max(0, idx - 1), min(len(lines), idx + 2)))
    if len(keep) > max_lines:
        prioritized = sorted(keep, key=lambda i: (0 if DIRECT.search(lines[i]) or "rt_dispatch" in lines[i] else 1, i))
        keep = set(prioritized[:max_lines])
    return [{"line": body["start"] + i, "text": lines[i]} for i in sorted(keep)]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--addresses", nargs="+", help="guest function addresses")
    group.add_argument("--assignments", type=Path, help="wave assignment JSON")
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--max-body-lines", type=int, default=140)
    args = ap.parse_args()

    if args.addresses:
        addresses = [f"0x{int(value, 16):x}" for value in args.addresses]
    else:
        data = json.loads(args.assignments.read_text(encoding="utf-8"))
        addresses = [target["address"] for worker in data["assignments"] for target in worker["targets"]]
    if len({address.lower() for address in addresses}) != len(addresses):
        raise SystemExit("Duplicate target address in packet request")

    names = {row["address"].lower(): row for row in read_tsv(ROOT / "decompiled/function_name_index.tsv")}
    behaviors = {row["address"].lower(): row for row in read_tsv(ROOT / "decompiled/function_behavior.tsv")}
    bodies = index_bodies()
    body_by_address = {address.lower(): body for address, body in bodies.items()}
    string_index = load_strings()
    packets = []
    for raw_address in addresses:
        address = raw_address.lower()
        body = body_by_address.get(address)
        if body is None:
            packets.append({"address": address, "error": "no generated body found"})
            continue
        raw = "\n".join(body["lines"])
        resolved = []
        for match in ADDR_ASSIGN.finditer(raw):
            value_address = int(match.group("base"), 16)
            offset = match.group("offset")
            if offset is not None:
                if value_address & 0xfff == 0 and int(offset, 16) >= 0x1000:
                    continue
                value_address += int(offset, 16)
            elif value_address & 0xfff == 0:
                continue
            value = string_index.get(value_address)
            if value:
                line_offset = raw[:match.start()].count("\n")
                resolved.append({"guest_address": f"0x{value_address:x}", "value": value, "body_line": body["start"] + line_offset})
        behavior = behaviors.get(address, {})
        callees = []
        for callee in [x.lower() for x in behavior.get("direct_callee_addresses", "").split(";") if x]:
            row = names.get(callee, {})
            callees.append({"address": callee, "name": row.get("semantic_name") or row.get("readable_name") or row.get("generated_name", callee), "name_evidence": row.get("name_evidence", "")})
        caller_packets = []
        for caller in [x.lower() for x in behavior.get("callers", "").split(";") if x and x != "..."]:
            caller_body = body_by_address.get(caller)
            if caller_body is None:
                continue
            target_pattern = re.compile(rf"\bf_{address[2:]}\(c\);")
            sites = []
            for idx, line in enumerate(caller_body["lines"]):
                if target_pattern.search(line):
                    lo, hi = max(0, idx - 3), min(len(caller_body["lines"]), idx + 2)
                    sites.append([{"line": caller_body["start"] + j, "text": caller_body["lines"][j]} for j in range(lo, hi)])
            caller_row = names.get(caller, {})
            caller_packets.append({"address": caller, "name": caller_row.get("semantic_name") or caller_row.get("readable_name") or caller, "call_sites": sites})
        name_row = names.get(address, {})
        packets.append({
            "module": "main", "address": address,
            "generated_name": name_row.get("generated_name", f"f_{address[2:]}"),
            "exact_symbol": name_row.get("raw_elf_name", ""),
            "current_semantic_name": name_row.get("semantic_name", ""),
            "existing_prototype_candidate": name_row.get("candidate_prototype", ""),
            "source": {"file": f"decompiled/main/{body['file']}", "start": body["start"], "end": body["end"], "line_count": len(body["lines"])},
            "body_excerpt": excerpt(body, resolved, args.max_body_lines),
            "indexed_callers": caller_packets,
            "known_direct_callees": callees,
            "resolved_exact_address_strings": resolved,
            "behavior_summary": behavior.get("evidence_summary", ""),
            "note": "Excerpt may omit body lines; source file and exact line range are included for focused follow-up. Resolved strings are exact guest-address matches.",
        })
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("".join(json.dumps(packet, separators=(",", ":")) + "\n" for packet in packets), encoding="utf-8", newline="\n")
    print(f"Wrote {len(packets)} evidence packets to {args.output}")


if __name__ == "__main__":
    main()
