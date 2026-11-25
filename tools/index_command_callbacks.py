"""Index named main NSO callback records for source-level annotation review."""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMAND = re.compile(rb"[A-Za-z_][A-Za-z_0-9]*(?:\.[A-Za-z_0-9]+)+")
RECORD_SIZE = 24


def main() -> None:
    sys.path.insert(0, str(ROOT / "recomp"))
    from nso import Nso, R_AARCH64_RELATIVE

    module = ROOT / "decompiled/main"
    base = int(json.loads((module / "manifest.json").read_text(encoding="utf-8"))["base"], 16)
    with (ROOT / "decompiled/function_symbols.tsv").open(encoding="utf-8", newline="") as stream:
        function_offsets = {
            int(row["address"], 16) - base
            for row in csv.DictReader(stream, delimiter="\t")
            if row["module"] == "main"
        }

    nso = Nso(str(ROOT / "MLBTS/game/exefs/main"))
    ro_start, ro_size = nso.rodata
    ro_end = ro_start + ro_size
    relative = {
        slot: target
        for slot, kind, _, target in nso.relocs
        if kind == R_AARCH64_RELATIVE
    }
    relocation_slots = {slot for slot, _, _, _ in nso.relocs}
    records = {}
    for callback_slot, target in relative.items():
        name_offset = relative.get(callback_slot - 8, -1)
        terminator_slot = callback_slot + 8
        if target not in function_offsets or not ro_start <= name_offset < ro_end:
            continue
        if terminator_slot in relocation_slots or terminator_slot + 8 > len(nso.image):
            continue
        if nso.u64(terminator_slot):
            continue
        raw = bytes(nso.image[name_offset:min(ro_end, name_offset + 128)])
        name, terminator, _ = raw.partition(b"\0")
        if terminator and COMMAND.fullmatch(name):
            records[callback_slot] = (target, name_offset, name.decode("ascii"))

    path = ROOT / "decompiled/command_callback_candidates.tsv"
    temporary = path.with_suffix(".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(["address", "command", "callback_slot", "name_slot", "name_address", "adjacent_record"])
        for slot, (target, name_offset, command) in sorted(records.items()):
            adjacent = slot - RECORD_SIZE in records or slot + RECORD_SIZE in records
            writer.writerow([hex(base + target), command, hex(base + slot), hex(base + slot - 8),
                             hex(base + name_offset), int(adjacent)])
    temporary.replace(path)
    print(f"Indexed {len(records)} callback records for {len({row[0] for row in records.values()})} functions")


if __name__ == "__main__":
    main()
