# Ranked candidate and attribute evaluation

This map covers the main ranked-candidate path found by following calls into
already-mapped player-attribute helpers. Table selectors, candidate-ID semantics,
and source-level class names are still unknown.

## Rebuild and evaluation functions

| Address | Working name | Observed behavior |
|---|---|---|
| `0x7000723c10` | `ranked_attribute_candidates_rebuild` | Allocates/reinitializes candidate buffers, selects one of two global candidate-ID tables by status, filters entries, and writes status/score outputs. |
| `0x70007325c0` | `ranked_player_attribute_entries_rebuild` | Builds a pointer list after status and record-flag checks; entries use a 16-byte stride. |
| `0x70006b8abc` | `player_attribute_configured_metric_evaluate` | Computes configured primary or nested attribute metrics and returns a float. |
| `0x70006b8860` | `player_attribute_scalar_evaluate` | Existing related scalar evaluator; its selector and formulas are mapped in `PLAYER_ATTRIBUTES_SUBSYSTEM.md`. |

`ranked_attribute_candidates_rebuild` allocates/reinitializes storage at owner
`+0x318` with a requested size of `0x508`, resets status/sentinel bytes around
`+0x820..+0x836`, and selects between global candidate-ID tables at
`0x7001d89148` (0x60 entries) or `0x7001d891a8` (0x50 entries), based on a
status lookup. It queries candidate eligibility and configured metrics through
existing helpers. The raw table entries and output slots are not assigned
baseball meanings.

`ranked_player_attribute_entries_rebuild` is called from four wrapper paths in
`main_0055.c` and several in `main_0058.c`. It creates a list with capacity 0x0c,
sets sentinel values at owner `+0x360/+0x363`, filters candidate records using
status selector `0x13`, a flag at candidate `+0x132`, and context status/mode,
then stores selected pointers in 16-byte entries. These are observed list and
filter mechanics, not a recovered class layout.

`player_attribute_configured_metric_evaluate` takes a subject wrapper, a selector,
and an option word. Its primary path reads attribute IDs `0x6b`, `0x74`, `0x62`,
`0x10`, and `0x11`, obtains a divisor from a global/context helper, optionally
adds the configured metric component, and calls the category metric helper. Its
nested path reads IDs `0x5d` and `0x13` and calls the secondary metric helper.
These component formulas and their dependencies are documented in
`PLAYER_ATTRIBUTES_SUBSYSTEM.md`; the selector names and domain meanings remain
unknown.

Evidence: `main_0055.c` at `f_7000723c10` and `f_70007325c0`;
`main_0052.c` at `f_70006b8abc`; direct callers are listed in
`tools/data/function_annotations.tsv`.


## Ranked output rows

`ranked_player_stat_rows_refresh_and_sort` (`0x7000672ed0`) builds candidate rows,
copies 15-byte blocks from player-record offsets `+0x50` and `+0x60` to row
offsets `+0x01` and `+0x11`, writes a float at row `+0x24`, copies a halfword
from player-record `+0x130` to row `+0x28`, and copies bytes from `+0xa2` and
`+0x70` to row `+0x2a` and `+0x2c`. It then calls
`ranked_stat_entry_rows_refresh` and `ranked_stat_entry_rows_secondary_refresh`.
The observed row stride is `0x30`; the fields are laid out in
`recovered/ranked_stat_row_types.h` with unresolved names preserved.
