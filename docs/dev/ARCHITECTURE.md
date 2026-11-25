# Architecture and repository map

## Main layers

| Path | Role |
|---|---|
| `decompiled/main`, `decompiled/sdk` | Generated instruction-level C wrappers and module tables. |
| `decompiled/function_*.tsv` | Function names, behavior summaries, symbols, call relationships, and related indexes. |
| `tools/data` | Candidate annotations, prototypes, field observations, target queues, and progress history. |
| `tools/data/staging` | Per-worker annotation proposals, assignments, review records, and batch timings. |
| `recovered` | Partial recovered layouts and typed structure definitions. |
| `runtime` | Host runtime and platform, graphics, UI, and game integration code. |
| `tools` | Extraction, indexing, analysis, dashboard, build, and publishing scripts. |
| `docs/dev` | Workspace setup, architecture, and evidence conventions. |

## Generated wrappers

The C under `decompiled/` preserves guest instruction behavior in mechanically
generated functions. A wrapper's `f_<address>` symbol is an address identity,
not a source-level function name. Semantic labels in the TSV indexes are
separate analysis annotations and should be accepted only when the available
body, callers, callback registration, symbols, or runtime evidence supports
them.

## Evidence and derived data

Staged proposals are reviewed before they enter shared annotation tables.
Refresh scripts then rebuild readable indexes and the progress dashboard
inputs. Partial subsystem maps in `decompiled/*_SUBSYSTEM.md` connect
functions, observed behavior, and tentative layouts; each map has its own
evidence and confidence limits.

## Dashboard publishing

The local Python server exposes live data from the workspace. The Pages
repository is deliberately separate and contains a static export of the
dashboard UI and its JSON snapshot. This keeps the private analysis workspace
out of the public website repository.
