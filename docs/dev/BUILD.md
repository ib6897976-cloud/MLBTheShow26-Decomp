# Build and workspace setup

## Workspace contents

This repository is the analysis and recompilation workspace. The locally
installed game files are intentionally not tracked. Toolchain folders,
generated artifacts, and build outputs are also excluded by `.gitignore`.

The project build entry point is `tools/build.py`. It consumes generated
module C from `recomp/gen.py` plus the host runtime sources. Its module
docstring lists the current command-line options and expected inputs. Build
outputs belong in an ignored work directory; do not commit generated game
executables or binary assets.

## Analysis tools

Common workflows include:

- `python tools/analyze_functions.py` for function and call-graph analysis.
- `python tools/refresh_annotation_indexes.py` after the shared annotation
  tables have been merged.
- `python tools/progress_server.py` to serve the live progress dashboard.
- `tools/publish_progress_pages.ps1` to export a static snapshot and publish
  it to the separate public dashboard repository.

The target game build and locally available extraction inputs vary by machine.
Keep those inputs outside version control and consult each tool's command-line
help or module documentation before running it.

## Reproducibility

Record the game version and evidence source when adding analysis. Do not
publish proprietary game data or assume that addresses from one build apply
to another. Generated indexes can be regenerated from their source TSV and
binary-analysis inputs.
