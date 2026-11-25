"""Export the progress dashboard's dynamic API payloads as GitHub Pages files."""
from __future__ import annotations

import json
import time
from pathlib import Path

import progress_server
import render_progress_svg


DATA_DIR = progress_server.SITE / "data"


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    temporary.replace(path)


def main() -> None:
    # The timeline scanner intentionally waits for stable index files and for the
    # function-name and behavior indexes to have matching row counts.
    progress_server.refresh_timeline()
    time.sleep(1.6)
    progress_server.refresh_timeline()
    coverage = progress_server.snapshot()
    timeline = progress_server.read_timeline()
    render_progress_svg.render()
    write_json(DATA_DIR / "coverage-status.json", progress_server.coverage_status())
    write_json(DATA_DIR / "coverage.json", coverage)
    write_json(DATA_DIR / "timeline.json", timeline)
    print(f"Exported dashboard data to {DATA_DIR}")


if __name__ == "__main__":
    main()
