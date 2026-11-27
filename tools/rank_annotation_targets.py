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
    known_addresses = {r["address"].lower() for r in annotations}
    # Staging filenames have evolved beyond the original *_waveNN.jsonl form.
    # Exclude every target row in current JSONL/JSON staging files so reviewed,
    # sampled, and already-assigned functions do not keep resurfacing near the
    # top of the queue. Read only each row's top-level address for JSONL packet
    # files; their nested caller/callee addresses are not target assignments.
    staged_addresses: set[str] = set()
    if STAGING.exists():
        for path in STAGING.iterdir():
            if not path.is_file() or path.suffix.lower() not in {".jsonl", ".json"}:
                continue
            try:
                with path.open("r", encoding="utf-8-sig") as stream:
                    if path.suffix.lower() == ".jsonl":
                        for line in stream:
                            if not line.strip():
                                continue
                            try:
                                item = json.loads(line)
                            except json.JSONDecodeError:
                                # Preserve target exclusions even for malformed
                                # review scratch lines whose first field is address.
                                for match in re.finditer(r'"address"\s*:\s*"(0x[0-9a-fA-F]+)"', line):
                                    staged_addresses.add(match.group(1).lower())
                                continue
                            if isinstance(item, dict):
                                address = item.get("address")
                                if isinstance(address, str) and address.lower().startswith("0x"):
                                    staged_addresses.add(address.lower())
                    else:
                        try:
                            item = json.load(stream)
                        except json.JSONDecodeError:
                            continue
                        pending = [item]
                        while pending:
                            value = pending.pop()
                            if isinstance(value, dict):
                                address = value.get("address")
                                if isinstance(address, str) and address.lower().startswith("0x"):
                                    staged_addresses.add(address.lower())
                                pending.extend(value.values())
                            elif isinstance(value, list):
                                pending.extend(value)
            except (OSError, UnicodeError):
                continue
    known_addresses.update(staged_addresses)
    # Deterministic wrapper labels describe exact local behavior, but they are
    # not domain-semantic helpers. Counting them here would push callers of
    # thousands of no-op/delete stubs ahead of functions tied to game behavior.
    semantic_helpers = {
        r["semantic_name"] for r in annotations
        if r["semantic_name"] != "guest_state_noop_stub"
        and not r["semantic_name"].startswith("return_immediate_")
        and not r["semantic_name"].startswith("tailcall_forward_to_")
        and not r["semantic_name"].endswith("_import_thunk")
    }
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
        external_markers = ("openssl", "wws_gattaca", "external/", "external\\", "/ssl/", "\\ssl\\")
        useful_strings = [
            s for s in strings
            if not s.startswith("kParam_")
            and not any(marker in s.lower() for marker in external_markers)
        ]
        generic_helpers = {"linear_remap_clamped", "sampled_flight_segment_interpolate"}
        generic_only_penalty = (
            900 if callees and callees <= generic_helpers and not useful_strings else 0
        )
        external_string_penalty = 1600 if strings and not useful_strings else 0
        score = (
            len(callees) * 1000
            + min(loads + stores, 999)
            + min(caller_count, 99) * 25
            + min(len(useful_strings), 3) * 1800
            - generic_only_penalty
            - external_string_penalty
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
    print(
        f"Ranked {len(targets)} unannotated main functions after excluding "
        f"{len(staged_addresses)} staged targets; wrote top {len(selected)} to {args.output}"
    )


if __name__ == "__main__":
    main()
