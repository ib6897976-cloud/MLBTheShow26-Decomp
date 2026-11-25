#!/usr/bin/env python3
"""Stage exact no-op and immediate-return guest functions conservatively."""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEF = re.compile(r"^void f_([0-9a-fA-F]+)\(Cpu \*c\) \{$")
MARK = re.compile(r"^\s*FN_ENTER\(0x([0-9a-fA-F]+)ull\);\s*$")
CONST = re.compile(r"^x0 = \((uint32_t|uint64_t)\)\(0x([0-9a-fA-F]+)ull\);$")
STAGED_FILE = re.compile(r".+_wave\d+\.jsonl$")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def significant_body(body: list[tuple[int, str]], address: str) -> list[str] | None:
    markers = [m for _, line in body if (m := MARK.match(line))]
    if len(markers) != 1 or f"0x{int(markers[0].group(1), 16):x}" != address:
        return None
    statements = []
    for _, line in body:
        value = line.strip()
        if not value or value == "}" or value.startswith("//"):
            continue
        if value.startswith("/*") and value.endswith("*/"):
            continue
        if MARK.match(line):
            continue
        statements.append(value)
    return statements


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wave", type=int, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    decomp = ROOT / "decompiled"
    names = {r["address"].lower(): r for r in read_tsv(decomp / "function_name_index.tsv") if r["module"] == "main"}
    annotated = {r["address"].lower() for r in read_tsv(ROOT / "tools/data/function_annotations.tsv") if r["module"] == "main"}
    already_staged = set()
    staging = ROOT / "tools/data/staging"
    for path in staging.glob("*.jsonl"):
        if not STAGED_FILE.fullmatch(path.name):
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                if row.get("module") == "main" and row.get("address"):
                    already_staged.add(row["address"].lower())

    proposals = []
    for source in sorted((decomp / "main").glob("main_[0-9][0-9][0-9][0-9].c")):
        lines = source.read_text(encoding="utf-8").splitlines()
        address = None
        start = 0
        body: list[tuple[int, str]] = []

        def emit(end_line: int) -> None:
            if address is None:
                return
            if address in annotated or address in already_staged:
                return
            index = names.get(address, {})
            if index.get("raw_elf_name"):
                return
            statements = significant_body(body, address)
            if statements is None:
                return
            if statements == ["return;"]:
                semantic_name = "guest_state_noop_stub"
                behavior = "After FN_ENTER, the exact lifted body contains only return; it performs no guest-register, guest-memory, or control-flow operation. FN_ENTER is the profiling hook."
            elif (
                len(statements) == 3
                and statements[0] == "uint64_t x0 = c->x[0];"
                and (match := CONST.match(statements[1]))
                and statements[2] == "c->x[0] = x0; return;"
            ):
                width, literal = match.groups()
                value = int(literal, 16)
                semantic_name = f"return_immediate_0x{value:x}"
                behavior = f"After FN_ENTER, the exact lifted body overwrites guest x0 with the immediate 0x{value:x} using a {width} cast and returns; no other guest state is changed."
            else:
                return
            proposals.append({
                "module": "main",
                "address": address,
                "semantic_name": semantic_name,
                "confidence": "high",
                "evidence": f"{behavior} Exact function body: decompiled/main/{source.name}:{start}-{end_line}. This synthetic label describes the lifted behavior; it does not infer an original source symbol or prototype.",
            })

        for line_number, line in enumerate(lines, 1):
            definition = DEF.match(line)
            if definition:
                emit(line_number - 1)
                address = f"0x{int(definition.group(1), 16):x}"
                start = line_number
                body = []
            elif address is not None:
                body.append((line_number, line))
        emit(len(lines))

    if args.limit:
        proposals = proposals[: args.limit]
    output = args.output or staging / f"wave{args.wave:02d}_trivial_fastlane_wave{args.wave}.jsonl"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("".join(json.dumps(row, separators=(",", ":")) + "\n" for row in proposals), encoding="utf-8", newline="\n")
    print(f"Staged {len(proposals)} exact no-op/immediate-return functions to {output}")


if __name__ == "__main__":
    main()
