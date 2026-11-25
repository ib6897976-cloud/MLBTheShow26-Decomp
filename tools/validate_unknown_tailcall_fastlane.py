#!/usr/bin/env python3
"""Independently validate exact-address labels for stripped tail-call wrappers."""
from __future__ import annotations

import csv
import json
import random
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "tools/data/staging/wave68_auto_unknown_tailcalls_wave68.jsonl"
REPORT = ROOT / "tools/data/staging/wave68_unknown_tailcall_review.md"
DEF = re.compile(r"^void f_([0-9a-fA-F]+)\(Cpu \*c\) \{$")
MARK = re.compile(r"^\s*FN_ENTER\(0x([0-9a-fA-F]+)ull\);\s*$")
TAIL = re.compile(r"^\s*__attribute__\(\(musttail\)\) return f_([0-9a-fA-F]+)\(c\);\s*$")
EVIDENCE = re.compile(
    r"Exact lifted body in (decompiled/main/[^:]+):(\d+)-(\d+) contains FN_ENTER and only "
    r"the musttail return to (0x[0-9a-fA-F]+)\. The target label is '([^']+)' from "
    r"(accepted semantic annotation|exact exported ELF symbol demangling|"
    r"exact guest function address; no source symbol is inferred)\."
)


def tsv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def slug(value: str) -> str:
    value = value.strip()
    value = value.replace("operator delete", "operator_delete").replace("operator new", "operator_new")
    value = re.sub(r"\([^)]*\)", "", value)
    return re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").lower()


def body_index():
    out = {}
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
            depth = lines[i].count("{") - lines[i].count("}")
            j = i + 1
            while j < len(lines) and depth > 0:
                depth += lines[j].count("{") - lines[j].count("}")
                j += 1
            out[address] = (path.name, start, j, lines[start - 1:j])
            i = j
    return out


rows = [json.loads(line) for line in BATCH.read_text(encoding="utf-8").splitlines() if line.strip()]
names = {r["address"].lower(): r for r in tsv(ROOT / "decompiled/function_name_index.tsv") if r["module"] == "main"}
known = {r["address"].lower() for r in tsv(ROOT / "tools/data/function_annotations.tsv") if r["module"] == "main"}
behavior = {r["address"].lower(): r for r in tsv(ROOT / "decompiled/function_behavior.tsv") if r["module"] == "main"}
bodies = body_index()
seen: set[str] = set()
bad: list[str] = []
chunk_counts: Counter[str] = Counter()
targets: Counter[str] = Counter()

for row in rows:
    address = row.get("address", "").lower()
    if address in seen:
        bad.append(f"{address}: duplicate proposal")
    seen.add(address)
    if address in known:
        bad.append(f"{address}: already annotated")
    indexed = names.get(address)
    if not indexed:
        bad.append(f"{address}: absent from function-name index")
        continue
    if indexed.get("raw_elf_name"):
        bad.append(f"{address}: wrapper has an exact ELF symbol")
    evidence = EVIDENCE.search(row.get("evidence", ""))
    if not evidence:
        bad.append(f"{address}: evidence sentence/path not parseable")
        continue
    rel, start_s, end_s, callee_s, target_name, evidence_kind = evidence.groups()
    start, end = int(start_s), int(end_s)
    callee = f"0x{int(callee_s, 16):x}"
    if evidence_kind.startswith("exact guest function address") and target_name != f"address_{int(callee, 16):x}":
        bad.append(f"{address}: address-only target label differs from cited callee")
    if row.get("semantic_name") != f"tailcall_forward_to_{slug(target_name)}":
        bad.append(f"{address}: synthetic name does not encode exact target")
    if row.get("confidence") != "high":
        bad.append(f"{address}: expected high confidence for exact pattern")
    if row.get("candidate_prototype") or row.get("fields"):
        bad.append(f"{address}: unexpected prototype/field claim")
    body = bodies.get(address)
    if not body:
        bad.append(f"{address}: generated body missing")
        continue
    file_name, actual_start, actual_end, lines = body
    if rel.split("/")[-1] != file_name or start != actual_start or end not in (actual_end, actual_end + 1):
        bad.append(f"{address}: cited source range does not match parsed body")
    if len(lines) != 4 or not MARK.match(lines[1]) or not TAIL.match(lines[2]):
        bad.append(f"{address}: body is not exactly FN_ENTER plus one musttail statement")
        continue
    marker = MARK.match(lines[1])
    tail = TAIL.match(lines[2])
    if not marker or int(marker.group(1), 16) != int(address, 16):
        bad.append(f"{address}: FN_ENTER address mismatch")
    if not tail or f"0x{int(tail.group(1), 16):x}" != callee:
        bad.append(f"{address}: body target does not match cited callee")
    callees = {x.lower() for x in behavior.get(address, {}).get("direct_callee_addresses", "").split(";") if x}
    if callees != {callee}:
        bad.append(f"{address}: indexed direct callees differ from exact body target")
    if behavior.get(address, {}).get("dispatch_target_addresses"):
        bad.append(f"{address}: function has indexed dispatch targets")
    target_row = names.get(callee)
    if not target_row:
        bad.append(f"{address}: target address is absent from function index")
    elif evidence_kind == "accepted semantic annotation":
        if target_row.get("semantic_name") != target_name:
            bad.append(f"{address}: accepted target label does not match current annotation")
    elif evidence_kind == "exact exported ELF symbol demangling":
        if not target_row.get("raw_elf_name") or target_row.get("readable_name") != target_name:
            bad.append(f"{address}: exact exported target label does not match symbol index")
    elif evidence_kind.startswith("exact guest function address"):
        if target_row.get("semantic_name") or (
            target_row.get("raw_elf_name")
            and target_row.get("readable_name")
            and target_row.get("readable_name") != target_row.get("generated_name")
        ):
            bad.append(f"{address}: named target should not use an address-only label")
    chunk_counts[file_name] += 1
    targets[callee] += 1

sample = random.Random(68004152).sample(rows, min(50, len(rows)))
for row in sample:
    body = bodies.get(row["address"].lower())
    if not body or len(body[3]) != 4 or not MARK.match(body[3][1]) or not TAIL.match(body[3][2]):
        bad.append(f"{row['address']}: deterministic manual sample found unexpected body shape")

summary = [
    "# Wave 68 exact-address tail-call batch QA",
    "",
    f"- Proposals examined: {len(rows):,}",
    f"- Unique addresses: {len(seen):,}",
    f"- Mechanical checks: {'PASS' if not bad else 'FAIL'} ({len(bad)} mismatches)",
    f"- Deterministic manual sample: {len(sample):,} bodies; each is FN_ENTER plus one exact musttail call.",
    f"- Generated C chunks represented: {len(chunk_counts):,}",
    f"- Distinct target addresses represented: {len(targets):,}",
    "- No original source symbol, prototype, or field type is inferred for the wrapper.",
    "",
    "## Mismatches",
    "",
    *([f"- {item}" for item in bad] if bad else ["None."]),
    "",
    "These labels identify exact forwarding behavior and guest target addresses. They are synthetic and are not recovered original symbols.",
]
REPORT.write_text("\n".join(summary) + "\n", encoding="utf-8")
print(f"rows={len(rows)} unique={len(seen)} mismatches={len(bad)} sample={len(sample)} targets={len(targets)}")
if bad:
    print("\n".join(bad[:30]))
    raise SystemExit(1)
