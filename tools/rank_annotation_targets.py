from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANNOTATIONS = ROOT / "tools" / "data" / "function_annotations.tsv"
BEHAVIOR = ROOT / "decompiled" / "function_behavior.tsv"
NAMES = ROOT / "decompiled" / "function_name_index.tsv"
DEFAULT_OUTPUT = ROOT / "tools" / "data" / "annotation_target_queue.tsv"
STAGING = ROOT / "tools" / "data" / "staging"


def read_tsv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def count_from_summary(summary: str, label: str) -> int:
    match = re.search(rf"(\d+) lifted {label}", summary)
    return int(match.group(1)) if match else 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Rank unannotated main functions that call already-understood semantic helpers."
    )
    parser.add_argument("--limit", type=int, default=500, help="maximum ranked targets to write")
    parser.add_argument("--minimum-hits", type=int, default=1, help="minimum distinct annotated callees")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    annotations = [r for r in read_tsv(ANNOTATIONS) if r["module"] == "main"]
    known_addresses = {r["address"] for r in annotations}
    # A reviewed function with inconclusive evidence should not be sent to workers
    # again just because it has no semantic rename. Staged rows are the audit log.
    if STAGING.exists():
        for path in STAGING.glob("*.jsonl"):
            if not re.fullmatch(r".+_wave\d+\.jsonl", path.name):
                continue
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    item = json.loads(line)
                    address = item.get("address")
                    if address:
                        known_addresses.add(address.lower())
    semantic_helpers = {r["semantic_name"] for r in annotations}
    names = {
        (r["module"], r["address"]): r["generated_name"]
        for r in read_tsv(NAMES)
    }

    targets = []
    for row in read_tsv(BEHAVIOR):
        if row["module"] != "main" or row["address"] in known_addresses:
            continue
        callees = {
            name for name in (row.get("direct_callees") or "").split(";")
            if name in semantic_helpers
        }
        if len(callees) < args.minimum_hits:
            continue
        summary = row.get("evidence_summary", "")
        loads = count_from_summary(summary, "loads")
        stores = count_from_summary(summary, "stores")
        caller_count = len([x for x in (row.get("callers") or "").split(";") if x and x != "..."])
        # Candidate strings and observed callers make reviewable evidence more likely;
        # helper overlap still determines whether the function belongs in this queue.
        strings = [s for s in (row.get("rodata_strings") or "").split(";") if s]
        useful_strings = [s for s in strings if not s.startswith("kParam_")]
        score = (
            len(callees) * 1000
            + min(loads + stores, 999)
            + min(caller_count, 99) * 25
            + min(len(useful_strings), 3) * 1800
        )
        targets.append({
            "score": score,
            "module": row["module"],
            "address": row["address"],
            "generated_name": names.get((row["module"], row["address"]), row.get("name", "")),
            "semantic_callee_count": len(callees),
            "semantic_callees": ";".join(sorted(callees)),
            "caller_count_observed": caller_count,
            "lifted_loads": loads,
            "lifted_stores": stores,
            "rodata_strings": row.get("rodata_strings", ""),
            "evidence_summary": summary,
        })

    targets.sort(key=lambda r: (-r["score"], r["address"]))
    selected = targets[:max(0, args.limit)]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    columns = [
        "rank", "score", "module", "address", "generated_name",
        "semantic_callee_count", "semantic_callees", "caller_count_observed",
        "lifted_loads", "lifted_stores", "rodata_strings", "evidence_summary",
    ]
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for rank, row in enumerate(selected, 1):
            writer.writerow({"rank": rank, **row})
    temporary.replace(args.output)
    print(f"Ranked {len(targets)} unannotated main functions; wrote top {len(selected)} to {args.output}")


if __name__ == "__main__":
    main()
