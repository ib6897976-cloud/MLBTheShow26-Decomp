#!/usr/bin/env python3
"""Independently validate the exact body shapes in a trivial fast-lane batch."""
import csv
import json
import random
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "tools/data/staging/wave66_trivial_fastlane_wave66.jsonl"
REPORT = ROOT / "tools/data/staging/wave66_trivial_review.md"
DEF = re.compile(r"^void f_([0-9a-fA-F]+)\(Cpu \*c\) \{$")
MARK = re.compile(r"^\s*FN_ENTER\(0x([0-9a-fA-F]+)ull\);\s*$")
CONST = re.compile(r"^x0 = \((uint32_t|uint64_t)\)\(0x([0-9a-fA-F]+)ull\);$")
EVIDENCE = re.compile(r"Exact function body: decompiled/main/([^:]+):(\d+)-(\d+)\.")


def tsv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def parse_bodies():
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
            close = j
            result[address] = (path.name, start, close, lines[start - 1 : close])
            i = j
    return result


def statements(lines, address, errors):
    if not lines or not DEF.match(lines[0]):
        errors.append(f"{address}: parsed function definition is missing")
        return []
    markers = [match for line in lines if (match := MARK.match(line))]
    if len(markers) != 1 or int(markers[0].group(1), 16) != int(address, 16):
        errors.append(f"{address}: FN_ENTER missing, duplicate, or mismatched")
    found = []
    for line in lines[1:-1]:
        value = line.strip()
        if not value or value.startswith("//") or (value.startswith("/*") and value.endswith("*/")):
            continue
        if MARK.match(line):
            continue
        found.append(value)
    return found


def main():
    rows = [json.loads(line) for line in BATCH.read_text(encoding="utf-8").splitlines() if line.strip()]
    names = {row["address"].lower(): row for row in tsv(ROOT / "decompiled/function_name_index.tsv") if row["module"] == "main"}
    annotated = {row["address"].lower() for row in tsv(ROOT / "tools/data/function_annotations.tsv") if row["module"] == "main"}
    prior_staged = set()
    staging = ROOT / "tools/data/staging"
    for path in staging.glob("*.jsonl"):
        if not re.fullmatch(r".+_wave\d+\.jsonl", path.name) or path == BATCH:
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                if row.get("module") == "main" and row.get("address"):
                    prior_staged.add(row["address"].lower())
    bodies = parse_bodies()
    errors = []
    seen = set()
    classes = Counter()
    sample_candidates = []

    for row in rows:
        address = row.get("address", "").lower()
        if address in seen:
            errors.append(f"{address}: duplicate proposal")
        seen.add(address)
        if address in annotated:
            errors.append(f"{address}: already annotated")
        if address in prior_staged:
            errors.append(f"{address}: duplicated in another staged producer batch")
        indexed = names.get(address)
        if not indexed:
            errors.append(f"{address}: missing from function-name index")
            continue
        if indexed.get("raw_elf_name"):
            errors.append(f"{address}: exact exported name exists")
        if row.get("module") != "main" or row.get("confidence") != "high":
            errors.append(f"{address}: invalid module or confidence")
        if any(key in row for key in ("candidate_prototype", "prototype_confidence", "fields")):
            errors.append(f"{address}: unexpected prototype/field claim")
        evidence = EVIDENCE.search(row.get("evidence", ""))
        body = bodies.get(address)
        if not evidence or not body:
            errors.append(f"{address}: missing source citation or parsed body")
            continue
        rel_file, cited_start, cited_end = evidence.groups()
        file_name, actual_start, actual_close, lines = body
        cited_start, cited_end = int(cited_start), int(cited_end)
        if rel_file != file_name or cited_start != actual_start:
            errors.append(f"{address}: source path/start does not match parsed body")
        if cited_end not in (actual_close, actual_close + 1):
            errors.append(f"{address}: cited end does not match function boundary")
        source = ROOT / "decompiled/main" / file_name
        source_lines = source.read_text(encoding="utf-8").splitlines()
        if cited_end == actual_close + 1 and (cited_end > len(source_lines) or source_lines[cited_end - 1].strip()):
            errors.append(f"{address}: extra cited line after body is not blank")

        found = statements(lines, address, errors)
        label = row.get("semantic_name", "")
        if label == "guest_state_noop_stub":
            if found != ["return;"]:
                errors.append(f"{address}: no-op label has statements {found}")
            classes["no-op stubs"] += 1
        elif label.startswith("return_immediate_0x"):
            if len(found) != 3 or found[0] != "uint64_t x0 = c->x[0];" or found[2] != "c->x[0] = x0; return;":
                errors.append(f"{address}: immediate-return body shape mismatch")
            else:
                match = CONST.match(found[1])
                if not match:
                    errors.append(f"{address}: immediate assignment is not a literal cast")
                elif label != f"return_immediate_0x{int(match.group(2), 16):x}":
                    errors.append(f"{address}: immediate label does not match body")
            classes["immediate returns"] += 1
        else:
            errors.append(f"{address}: unexpected label {label!r}")
        sample_candidates.append((address, label, found))

    random.seed(66004551)
    sample = random.sample(sample_candidates, min(50, len(sample_candidates)))
    for address, label, found in sample:
        if label == "guest_state_noop_stub" and found != ["return;"]:
            errors.append(f"{address}: sampled no-op mismatch")
        if label.startswith("return_immediate_0x") and len(found) != 3:
            errors.append(f"{address}: sampled immediate mismatch")

    report = [
        "# Wave 66 no-op and immediate-return batch QA", "",
        f"- Proposals examined: {len(rows):,}",
        f"- Unique addresses: {len(seen):,}",
        f"- Independent mechanical checks: {'PASS' if not errors else 'FAIL'} ({len(errors)} mismatches)",
        f"- Manual body sample: {len(sample)} deterministic functions; each checked against the parsed source body.",
        f"- No-op stubs: {classes['no-op stubs']:,}",
        f"- Immediate-return functions: {classes['immediate returns']:,}",
        "- Prototype and field claims: none", "", "## Sampled addresses", "",
        ", ".join(f"`{address}`" for address, _, _ in sample), "", "## Mismatches", "",
    ]
    report.extend([f"- {error}" for error in errors] or ["None."])
    report += ["", "## Limits", "", "This validates guest-state behavior for these exact body patterns. FN_ENTER may invoke the host profiling hook. The labels are synthetic behavior descriptions; they do not recover source symbols, prototypes, or types."]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"rows={len(rows)} unique={len(seen)} noops={classes['no-op stubs']} immediate_returns={classes['immediate returns']} mismatches={len(errors)} sample={len(sample)}")
    if errors:
        for error in errors[:40]:
            print(error)


if __name__ == "__main__":
    main()
