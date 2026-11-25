"""Render a compact, one-box-per-function coverage graphic for GitHub."""
from __future__ import annotations

import csv
import html
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
FUNCTIONS = ROOT / "decompiled" / "function_name_index.tsv"
ANNOTATIONS = ROOT / "tools" / "data" / "function_annotations.tsv"
PROTOTYPES = ROOT / "tools" / "data" / "function_prototype_candidates.tsv"
FIELDS = ROOT / "tools" / "data" / "field_annotations.tsv"
OUTPUT = ROOT / "tools" / "progress_site" / "progress.svg"


def row_count(path: Path) -> int:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return sum(1 for _ in csv.DictReader(stream, delimiter="\t"))


def render() -> Path:
    annotation_counts: dict[tuple[str, str], int] = {}
    with ANNOTATIONS.open("r", encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            if row.get("semantic_name"):
                annotation_counts[(row["module"], row["address"])] = 1

    colors = {
        "semantic": "#2ea043",
        "exported": "#1f6feb",
        "address": "#30363d",
    }
    paths = {key: [] for key in colors}
    counts = {key: 0 for key in colors}
    columns, tile, stride = 320, 2, 3
    total = 0

    with FUNCTIONS.open("r", encoding="utf-8-sig", newline="") as stream:
        for index, row in enumerate(csv.DictReader(stream, delimiter="\t")):
            key = (row["module"], row["address"])
            category = (
                "semantic" if key in annotation_counts
                else "exported" if row.get("raw_elf_name")
                else "address"
            )
            x = (index % columns) * stride + 20
            y = (index // columns) * stride + 151
            paths[category].append(f"M{x} {y}h{tile}v{tile}h-{tile}z")
            counts[category] += 1
            total += 1

    semantic_total = counts["semantic"]
    prototype_total = row_count(PROTOTYPES)
    field_total = row_count(FIELDS)
    rows = math.ceil(total / columns)
    height = 151 + rows * stride + 36
    semantic_percent = semantic_total * 100 / total if total else 0
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 {height}" width="1000" height="{height}" role="img" aria-labelledby="title desc">',
        '<title id="title">MLB The Show recomp progress</title>',
        f'<desc id="desc">{total:,} indexed guest functions shown as boxes. {semantic_total:,} have evidence-backed semantic names, {counts["exported"]:,} have exact exported names only, and {counts["address"]:,} remain address-derived.</desc>',
        f'<rect width="1000" height="{height}" fill="#0d1117"/>',
        '<g font-family="Arial,Helvetica,sans-serif" fill="#f0f6fc">',
        '<text x="20" y="29" font-size="22" font-weight="600">MLB The Show recomp · progress</text>',
        f'<text x="20" y="51" font-size="13" fill="#8b949e">{total:,} guest functions indexed · one box per function · ordered by module and address</text>',
    ]

    cards = [
        (20, "SEMANTIC NAMES", f"{semantic_total:,}", f"{semantic_percent:.2f}% of indexed functions", colors["semantic"]),
        (347, "PROTOTYPE CANDIDATES", f"{prototype_total:,}", "candidate signatures", "#a371f7"),
        (674, "FIELD ANNOTATIONS", f"{field_total:,}", "candidate field/type rows", "#d29922"),
    ]
    for x, label, value, note, accent in cards:
        parts.extend([
            f'<rect x="{x}" y="65" width="306" height="48" rx="6" fill="#161b22" stroke="#30363d"/>',
            f'<rect x="{x}" y="65" width="4" height="48" rx="2" fill="{accent}"/>',
            f'<text x="{x + 14}" y="82" font-size="10" fill="#8b949e">{html.escape(label)}</text>',
            f'<text x="{x + 14}" y="103" font-size="18" font-weight="600">{html.escape(value)}</text>',
            f'<text x="{x + 112}" y="101" font-size="10" fill="#8b949e">{html.escape(note)}</text>',
        ])

    legend = [
        ("semantic", "Semantic name", counts["semantic"]),
        ("exported", "Exact ELF name only", counts["exported"]),
        ("address", "Address-derived", counts["address"]),
    ]
    lx = 20
    for category, label, count in legend:
        parts.extend([
            f'<rect x="{lx}" y="129" width="10" height="10" rx="1" fill="{colors[category]}"/>',
            f'<text x="{lx + 16}" y="138" font-size="11" fill="#c9d1d9">{html.escape(label)} · {count:,}</text>',
        ])
        lx += 245

    for category, label, count in legend:
        parts.append(f'<path fill="{colors[category]}" d="{"".join(paths[category])}"><title>{html.escape(label)}: {count:,} functions</title></path>')
    parts.extend(['</g>', '</svg>'])

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(parts) + "\n", encoding="utf-8")
    return OUTPUT


if __name__ == "__main__":
    print(f"Rendered progress graphic to {render()}")
