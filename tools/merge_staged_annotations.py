"""Merge parallel worker JSONL proposals into the reviewed TSV indexes."""
from __future__ import annotations

import csv
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGING = ROOT / "tools" / "data" / "staging"
TIMING = STAGING / "batch_timing.jsonl"
CONFIDENCE = {"low", "medium-low", "medium", "medium-high", "high"}


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        return list(reader.fieldnames or []), list(reader)


def write_tsv(path: Path, headers: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream, fieldnames=headers, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def load_proposals(paths: list[Path] | None = None) -> list[dict]:
    proposals: list[dict] = []
    seen: set[str] = set()
    files = sorted(paths) if paths is not None else [
        path for path in sorted(STAGING.glob("*.jsonl"))
        if re.fullmatch(r".+_wave\d+\.jsonl", path.name)
    ]
    for path in files:
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path.name}:{line_number}: invalid JSON: {exc}") from exc
            address = str(item.get("address", "")).lower()
            if not address.startswith("0x") or item.get("module") not in {"main", "sdk"}:
                raise ValueError(f"{path.name}:{line_number}: invalid module/address")
            if item.get("module") == "sdk" and (
                item.get("candidate_prototype") or item.get("fields")
            ):
                raise ValueError(f"{path.name}:{line_number}: SDK prototype/field proposals require separate review")
            if address in seen:
                raise ValueError(f"Duplicate staged function address: {address}")
            seen.add(address)
            if item.get("confidence") not in CONFIDENCE:
                raise ValueError(f"{path.name}:{line_number}: invalid confidence")
            if not str(item.get("evidence", "")).strip():
                raise ValueError(f"{path.name}:{line_number}: missing function evidence")
            proposals.append(item)
    return proposals


def record_batch_finishes(paths: list[Path] | None) -> None:
    """Use staged file write times to close previously logged dispatches."""
    if paths is None or not TIMING.exists():
        return
    events = [json.loads(line) for line in TIMING.read_text(encoding="utf-8").splitlines() if line.strip()]
    started = {(e["wave"], e["agent"]): e for e in events if e.get("event") == "started"}
    finished = {(e["wave"], e["agent"]) for e in events if e.get("event") == "finished"}
    additions = []
    for path in paths:
        match = re.fullmatch(r"(.+)_wave(\d+)\.jsonl", path.name)
        if not match:
            continue
        key = (int(match.group(2)), match.group(1))
        start = started.get(key)
        if not start or key in finished:
            continue
        # On Windows, st_ctime is the file creation time, which survives a later
        # QA normalization of the staged JSONL. st_mtime would incorrectly count
        # reviewer/merge delay as producer work time.
        stat = path.stat()
        creation_time = getattr(stat, "st_birthtime", None) or stat.st_ctime
        end_dt = datetime.fromtimestamp(creation_time, timezone.utc)
        start_dt = datetime.fromisoformat(start["timestamp"].replace("Z", "+00:00"))
        elapsed = max(0.0, (end_dt - start_dt).total_seconds())
        count = int(start.get("target_count", 0))
        additions.append({
            "event": "finished", "wave": key[0], "agent": key[1],
            "timestamp": end_dt.isoformat().replace("+00:00", "Z"),
            "duration_seconds": round(elapsed, 2), "target_count": count,
            "seconds_per_function": round(elapsed / count, 2) if count else None,
            "staged_file": path.name,
            "timing_source": "staged_file_creation_time",
        })
    if additions:
        with TIMING.open("a", encoding="utf-8", newline="\n") as stream:
            for event in additions:
                stream.write(json.dumps(event, separators=(",", ":")) + "\n")


def merge(path: Path, headers: list[str], staged: list[dict], kind: str) -> int:
    actual_headers, rows = read_tsv(path)
    if actual_headers != headers:
        raise ValueError(f"Unexpected TSV schema in {path}")
    seen = {row["address"].lower() for row in rows} if "address" in headers else {
        (row["structure_name"], row["offset"]) for row in rows
    }
    added = 0
    for item in staged:
        values: list[dict[str, str]] = []
        if kind == "function":
            name = str(item.get("semantic_name", "")).strip()
            if name:
                values.append({
                    "module": item["module"], "address": item["address"],
                    "semantic_name": name, "confidence": item["confidence"],
                    "evidence": item["evidence"],
                })
        elif kind == "prototype":
            if item["module"] != "main":
                continue
            proto = str(item.get("candidate_prototype", "")).strip()
            evidence = str(item.get("prototype_evidence", "")).strip()
            confidence = item.get("prototype_confidence")
            if proto and evidence and confidence in CONFIDENCE:
                values.append({
                    "module": "main", "address": item["address"],
                    "candidate_prototype": proto, "confidence": confidence,
                    "evidence": evidence,
                })
        else:
            if item["module"] != "main":
                continue
            for field in item.get("fields", []):
                if not isinstance(field, dict):
                    raise ValueError(f"Invalid field proposal at {item['address']}")
                if field.get("confidence") not in CONFIDENCE or not str(field.get("evidence", "")).strip():
                    raise ValueError(f"Field evidence/confidence missing at {item['address']}")
                values.append({
                    "module": "main",
                    "structure_name": str(field["structure_name"]),
                    "structure_confidence": str(field.get("structure_confidence", "candidate")),
                    "base_description": str(field["base_description"]),
                    "offset": str(field["offset"]),
                    "size_bytes": str(field["size_bytes"]),
                    "field_name": str(field["field_name"]),
                    "ctype": str(field["ctype"]),
                    "semantic_description": str(field["semantic_description"]),
                    "confidence": field["confidence"],
                    "evidence": field["evidence"],
                })
        for row in values:
            key = row["address"].lower() if "address" in headers else (row["structure_name"], row["offset"])
            if key in seen:
                continue
            rows.append(row)
            seen.add(key)
            added += 1
    write_tsv(path, headers, rows)
    return added


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--files", nargs="*", help="specific staging JSONL files to merge")
    args = parser.parse_args()
    files = [STAGING / name for name in args.files] if args.files is not None else None
    if files and any(path.parent.resolve() != STAGING.resolve() for path in files):
        raise SystemExit("Staging files must be direct children of tools/data/staging")
    proposals = load_proposals(files)
    record_batch_finishes(files)
    counts = [
        merge(ROOT / "tools/data/function_annotations.tsv",
              ["module", "address", "semantic_name", "confidence", "evidence"],
              proposals, "function"),
        merge(ROOT / "tools/data/function_prototype_candidates.tsv",
              ["module", "address", "candidate_prototype", "confidence", "evidence"],
              proposals, "prototype"),
        merge(ROOT / "tools/data/field_annotations.tsv",
              ["module", "structure_name", "structure_confidence", "base_description",
               "offset", "size_bytes", "field_name", "ctype", "semantic_description",
               "confidence", "evidence"],
              proposals, "field"),
    ]
    print(f"Loaded {len(proposals)} staged function proposals")
    print(f"Added {counts[0]} names, {counts[1]} prototypes, and {counts[2]} fields")


if __name__ == "__main__":
    main()
