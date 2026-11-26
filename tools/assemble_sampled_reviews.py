#!/usr/bin/env python3
"""Complete a name-only QA file with conservative verdicts for unsampled blanks.

Every proposed name must have an independent verdict. For blank proposals,
the partial review must include the requested number of sampled blanks;
remaining blank rows receive an explicit automatic needs_more_evidence verdict
and can never add a semantic name. Prototype/field claims are rejected because
they require full independent review.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGING = ROOT / "tools" / "data" / "staging"
SOURCE_LINE = re.compile(r"decompiled/[A-Za-z0-9_./-]+:\d+(?:-\d+)?")


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{path.name}:{number}: invalid JSON: {exc}") from exc
        if not isinstance(row, dict):
            raise SystemExit(f"{path.name}:{number}: expected a JSON object")
        rows.append(row)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proposals", required=True, help="producer JSONL basename in staging")
    parser.add_argument("--partial", required=True, help="reviewer JSONL basename containing inspected rows")
    parser.add_argument("--output", required=True, help="complete review JSONL basename to write in staging")
    parser.add_argument(
        "--minimum-blank-samples", type=int, default=1,
        help="minimum independently reviewed blank proposals (default: 1; use 2 when the producer proposed no names)",
    )
    args = parser.parse_args()

    if args.minimum_blank_samples < 0:
        raise SystemExit("--minimum-blank-samples must be nonnegative")

    paths = [STAGING / name for name in (args.proposals, args.partial, args.output)]
    if any(path.parent.resolve() != STAGING.resolve() for path in paths):
        raise SystemExit("All files must be direct children of tools/data/staging")
    proposal_path, partial_path, output_path = paths
    if not proposal_path.is_file() or not partial_path.is_file():
        raise SystemExit("Proposal or partial review file does not exist")

    proposals = read_jsonl(proposal_path)
    partial = read_jsonl(partial_path)
    by_address: dict[str, dict] = {}
    for row in proposals:
        address = str(row.get("address", "")).lower()
        if not address.startswith("0x") or address in by_address:
            raise SystemExit(f"Invalid or duplicate proposal address: {address!r}")
        if row.get("candidate_prototype") or row.get("fields"):
            raise SystemExit(f"{address}: prototype/field claims require full QA")
        by_address[address] = row

    reviewed: dict[str, dict] = {}
    for row in partial:
        address = str(row.get("address", "")).lower()
        if address not in by_address or address in reviewed:
            raise SystemExit(f"Invalid, duplicate, or unexpected partial review address: {address!r}")
        if row.get("source_file") != proposal_path.name:
            raise SystemExit(f"{address}: source_file must be {proposal_path.name!r}")
        if row.get("verdict") not in {"confirmed", "corrected", "reject_name", "needs_more_evidence"}:
            raise SystemExit(f"{address}: invalid verdict")
        if not str(row.get("notes", "")).strip() or not row.get("source_lines"):
            raise SystemExit(f"{address}: review needs notes and source_lines")
        reviewed[address] = row

    named = {address for address, row in by_address.items() if str(row.get("semantic_name", "")).strip()}
    missing_names = named - reviewed.keys()
    if missing_names:
        raise SystemExit(f"Every proposed name must be reviewed; missing={sorted(missing_names)}")
    blank_addresses = set(by_address) - named
    sampled_blanks = blank_addresses & reviewed.keys()
    required_samples = min(len(blank_addresses), args.minimum_blank_samples)
    if len(sampled_blanks) < required_samples:
        raise SystemExit(
            f"Need at least {required_samples} independently reviewed blank proposals; "
            f"found {len(sampled_blanks)}"
        )

    complete = []
    automatic = 0
    for address, proposal in by_address.items():
        if address in reviewed:
            complete.append(reviewed[address])
            continue
        lines = SOURCE_LINE.findall(str(proposal.get("evidence", "")))
        if not lines:
            raise SystemExit(f"{address}: cannot cite a source line for automatic blank carry-through")
        complete.append({
            "address": proposal["address"],
            "source_file": proposal_path.name,
            "verdict": "needs_more_evidence",
            "reviewed_name": "",
            "notes": (
                "Automatic conservative carry-through: producer proposed no semantic name, "
                "and this blank was outside the selected QA sample. It remains unnamed; "
                "no behavior claim was independently made or merged."
            ),
            "source_lines": [lines[0]],
        })
        automatic += 1

    output_path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in complete),
        encoding="utf-8",
        newline="\n",
    )
    print(
        f"complete={len(complete)} inspected={len(reviewed)} automatic_blank={automatic} "
        f"proposed_names={len(named)} sampled_blanks={len(sampled_blanks)}"
    )


if __name__ == "__main__":
    main()
