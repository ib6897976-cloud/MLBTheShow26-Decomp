#!/usr/bin/env python3
"""Validate and apply independent review verdicts to staged function proposals."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGING = ROOT / "tools" / "data" / "staging"
IDENTIFIER = re.compile(r"^[a-z][a-z0-9_]*$")
VERDICTS = {"confirmed", "corrected", "reject_name", "needs_more_evidence"}


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{path.name}:{line_number}: invalid JSON: {exc}") from exc
        if not isinstance(row, dict):
            raise SystemExit(f"{path.name}:{line_number}: expected a JSON object")
        rows.append(row)
    return rows


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proposals", nargs="+", required=True, help="producer JSONL file names in staging")
    parser.add_argument("--review", required=True, help="independent review JSONL file name in staging")
    parser.add_argument("--apply", action="store_true", help="rewrite producer files after validation")
    args = parser.parse_args()

    paths = [STAGING / name for name in args.proposals]
    review_path = STAGING / args.review
    if any(path.parent.resolve() != STAGING.resolve() for path in paths) or review_path.parent.resolve() != STAGING.resolve():
        raise SystemExit("All input files must be direct children of tools/data/staging")
    if any(not path.is_file() for path in [*paths, review_path]):
        raise SystemExit("A proposal or review file does not exist")

    proposals: list[tuple[Path, dict]] = []
    proposal_by_address: dict[str, tuple[Path, dict]] = {}
    for path in paths:
        for row in read_jsonl(path):
            address = str(row.get("address", "")).lower()
            if not address.startswith("0x") or address in proposal_by_address:
                raise SystemExit(f"Invalid or duplicate proposal address: {address!r}")
            proposals.append((path, row))
            proposal_by_address[address] = (path, row)

    reviews = {}
    for row in read_jsonl(review_path):
        address = str(row.get("address", "")).lower()
        if not address.startswith("0x") or address in reviews:
            raise SystemExit(f"Invalid or duplicate review address: {address!r}")
        if row.get("verdict") not in VERDICTS:
            raise SystemExit(f"{address}: invalid review verdict {row.get('verdict')!r}")
        if not str(row.get("notes", "")).strip() or not row.get("source_lines"):
            raise SystemExit(f"{address}: review must include notes and source_lines")
        reviews[address] = row

    missing = sorted(set(proposal_by_address) - set(reviews))
    extra = sorted(set(reviews) - set(proposal_by_address))
    if missing or extra:
        raise SystemExit(f"Review/proposal address mismatch; missing={missing}, extra={extra}")

    grouped: dict[Path, list[dict]] = {path: [] for path in paths}
    changed = corrected = cleared = 0
    for path, row in proposals:
        address = str(row["address"]).lower()
        review = reviews[address]
        if review.get("source_file") != path.name:
            raise SystemExit(f"{address}: review source_file {review.get('source_file')!r} != {path.name!r}")
        verdict = review["verdict"]
        proposed_name = str(row.get("semantic_name", "")).strip()
        reviewed_name = str(review.get("reviewed_name", "") or "").strip()
        rationale = str(review["notes"]).strip()

        if reviewed_name and not IDENTIFIER.fullmatch(reviewed_name):
            raise SystemExit(
                f"{address}: reviewed_name must be a concise snake_case identifier; got {reviewed_name[:100]!r}"
            )
        if verdict == "confirmed":
            if reviewed_name and reviewed_name != proposed_name:
                raise SystemExit(f"{address}: confirmed name differs from the producer proposal")
        elif verdict == "corrected":
            if not reviewed_name:
                raise SystemExit(f"{address}: corrected verdict requires a reviewed_name")
            if proposed_name != reviewed_name:
                row["semantic_name"] = reviewed_name
                changed += 1
        elif verdict in {"reject_name", "needs_more_evidence"}:
            if proposed_name:
                row["semantic_name"] = ""
                cleared += 1

        if row.get("fields") and "field" in rationale.lower() and "reject" in rationale.lower():
            raise SystemExit(f"{address}: review notes reject field claims; remove those rows before applying")
        grouped[path].append(row)

    if args.apply:
        for path, rows in grouped.items():
            write_jsonl(path, rows)
    accepted = sum(bool(row.get("semantic_name")) for _, row in proposals)
    print(
        f"Validated {len(proposals)} proposals and {len(reviews)} verdicts: "
        f"{accepted} names remain, {changed} corrected, {cleared} cleared; "
        f"{'applied' if args.apply else 'dry run'}."
    )


if __name__ == "__main__":
    main()
