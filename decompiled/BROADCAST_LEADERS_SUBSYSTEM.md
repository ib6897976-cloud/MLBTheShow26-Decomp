# Broadcast moments and league-leader refresh

This partial map follows the current-build functions described by the local
1.0.20 patch analysis in [`../tools/data/patches-1.0.20.txt`](../tools/data/patches-1.0.20.txt).
The current generated C confirms function boundaries, callers, and direct
callees. The patch analysis records the repeated build and the storage region
that the ranking builder repopulates.

## Current-build functions

| Address | Working name | Observed role |
|---|---|---|
| `0x7000e53620` | `moments_game_start_sequence` | Calls the moments setup, secondary state writer, leader builder, and a continuation routine. |
| `0x7000e53654` | `moments_game_start_setup` | Clears and initializes the moments object and invokes the leaderboard builder. It has two direct callers: the game-start sequence and the full refresh. |
| `0x7000e543a4` | `league_leader_lists_build` | Builds the leader lists; it is called from game start, full refresh, and another current-build path. |
| `0x7000e54c00` | `league_leader_top_ten_population` | Populates top-ten lists. Local patch analysis describes 23 statistics in four groups (92 lists), scanning up to 1,350 players per statistic, and reports `qsort_r`. Its direct sort edge remains unverified in generated C. |
| `0x7000673660` | `ranked_stat_entry_rows_secondary_refresh` | Builds two candidate arrays of up to 1,350 16-byte records and calls the main `qsort` import thunk with a metric comparator before writing ranked rows. |
| `0x70006b8860` | `player_attribute_scalar_evaluate` | Shared scalar evaluator used by ranked candidate collection; queries numeric player attributes and the ranked path keeps positive results. |
| `0x70017cee44` / `0x70017cee5c` | `ranked_row_copy_player_payload_a` / `_b` | Zero and conditionally copy 15 bytes into the two opaque fixed-width row payloads. |
| `0x70006753d0` | `top_n_stat_candidate_generation` | Shared helper reached for a selected statistic. The leader path passes a 10-row limit, player-source and scratch/output pointers, selectors, and two option values; it initializes a scratch loop bounded by `0x546` (1,350) and tail-calls result handlers. |
| `0x700181ad74` | `strided_record_table_lookup` | Bounds-checks an index and derives a record subobject from a table with `0x550`-byte stride. |
| `0x7000e5640c` | `moments_full_leader_refresh` | Full refresh path called from the inning-change event route; calls both setup and list building. |

The local analysis finds that both game start and the inning-change refresh
call `0x7000e53654`, which calls `0x7000e54c00`, then call
`0x7000e543a4` again. It reports no reads of the first-built list region
between those calls. The local patch removes only the redundant first
`0x7000e54c00` call in the inning-change setup; the later builder and the
other call paths remain. This explains that patch's behavior, but does not
prove every list consumer or the complete object lifecycle.

## Candidate list and entry layout

`0x7000e54c00` selects a statistic and calls `0x70006753d0` with a row limit
of 10 and a candidate source. Other callers reach the same helper, so its name
is kept generic. The local 1.0.20 analysis reports a `qsort_r` pass in the leader refresh.
Generated C now establishes a separate concrete sort path in
`ranked_stat_entry_rows_secondary_refresh` (`0x7000673660`): it calls
`0x7001c20160`, a trampoline that loads the function pointer from guest address
`0x70022ab350`. ELF relocation metadata identifies that slot as the main
module's `qsort` import. The SDK's exported `qsort` wrapper calls `qsort_r`, so
the trampoline-to-SDK sort path is established for this secondary refresh.
This does not prove that `0x7000e54c00` itself calls the import, nor that the
patch report's per-statistic `qsort_r` refers to the exact same operation.

The comparator passed by `0x7000673660` is `0x700181f9c0`. It reads an `f32`
at scratch-record offset `+8`, orders larger metrics before smaller metrics,
and uses pointer-address comparison when the floats compare equal. The exact
tie behavior is unusual and is recorded without normalizing it to a conventional
stable comparator. Its 16-byte records are modeled in
[`recovered/broadcast_moments_types.h`](recovered/broadcast_moments_types.h).

The candidate list region is exactly `0xac80` bytes: `92 lists × 10 entries ×
0x30 bytes`. The current builder has four outer groups of 23 statistics; each
list advances by `0x1e0` bytes, which equals ten `0x30`-byte entries. The shared `ranked_record_0x30_reset` helper (`0x70017e96a4`) is called at
`0x30`-byte intervals and writes seven reset values through offset `+0x2c`.
The function behavior index lists six other direct callers in addition to the
leader population path, so its prototype uses `void *` rather than claiming a
leader-entry source type. A second helper, `ranked_record_0x30_initialize`
(`0x70017e9680`), performs the same writes in a different order and is also
called in record-array paths. Both therefore support the observed 0x30-byte
record layout without proving a single shared source structure. This matches
the list stride and the region end at object `+0x25d38`.

`ranked_stat_entry_rows_refresh` (`0x7000673210`) provides another writer for
the same row shape. It selects a list through the pointer stored at absolute
`0x7002287228`, using `0x1e0` bytes per ten-row list, and copies source player
fields at `+0x130`, `+0xa2`, and `+0x70` into row offsets `+0x28`, `+0x2a`, and
`+0x2c`. It writes the metric at `+0x24` and boolean candidate-state results
at each row's `+0x00`. This confirms the row offsets are shared across more
than the `0x7000e54c00` path; the field meanings and state predicate remain
unknown.

A second stage, `ranked_stat_entry_rows_secondary_refresh` (`0x7000673660`),
uses the same row payload offsets. It clears two auxiliary 20-row runs, scans
candidate data with a large temporary workspace, copies the same three player
record fields, clears row `+0x2b`, and writes a float metric at `+0x24`. This
independently confirms the widths and offsets of the candidate entry layout.
The selection and ordering algorithm is still unresolved.

The two ranking refreshes also populate byte payloads in each 0x30-byte row.
Helpers `ranked_row_copy_player_payload_a` (`0x70017cee44`) and `_b`
(`0x70017cee5c`) zero 16 bytes at row offsets `+0x01` and `+0x11`; when the
corresponding source pointer is nonnull, they copy 15 bytes from player-record
offsets `+0x50` and `+0x60`. The copy uses the three-argument import trampoline
`0x7001c1fbe0` (slot `0x70022ab090`). The main ELF import table contains both
`memcpy` and `memmove`, but the checked local metadata does not map this slot to
one exact symbol. These row regions are now modeled as fixed 16-byte opaque
payloads; their contents and meaning remain unidentified.

Candidate collection also uses `strided_record_table_lookup` (`0x700181ad74`).
The helper rejects a null output pointer, negative index, or index at/above the
32-bit count at table `+0x3c`; on success it returns
`records_base + index*0x550 + 0x50`, where `records_base` is loaded from `+0x08`.
The ranked refresh supplies the global table pointer at `0x700227e6c0`. This
supports a minimal 0x40-byte header candidate and a 0x550-byte record stride,
but does not yet identify the meaning of the returned record subobject or the
other header fields. See `StridedRecordTableHeaderCandidate` in the recovered
types header.

The ranked candidate loop calls `player_attribute_scalar_evaluate`
(`0x70006b8860`) with a record pointer, a selector derived from byte `+0xa2`,
and zero options. The routine reads that byte and byte `+0x72`, a 32-bit value
at `+0x70`, and several numeric player attributes (IDs observed include
`0x6b`, `0x74`, `0x62`, `0x10`, and `0x11`), then combines
them with constants and helper results. The refresh retains positive scalar
results for sorting. The exact formula inputs are partially traced, but the
statistic represented by the result and the units remain unknown.

Before filling its candidate scratch arrays, this function calls the trampoline
`0x7001c1fb70` twice with `(destination, 0, 0x5460)`, targeting stack ranges
`sp+0x5628` and `sp+0x1c8`. The trampoline tail-dispatches through guest slot
`0x70022ab058`. This call shape is consistent with zero-filling the two 0x5460-byte
buffers; the slot's imported symbol name is not present in the checked local
metadata, so the working name `zero_fill_import_thunk` remains a medium-confidence
behavioral label rather than a confirmed `memset` import.

The partial array and entry layout are in
[`recovered/broadcast_moments_types.h`](recovered/broadcast_moments_types.h).
The current population path writes a 32-bit float result at entry `+0x24`, a
16-bit value copied from the player record at `+0x130` to `+0x28`, a byte from
player `+0xa2` to entry `+0x2a`, and the low byte of player `+0x70` to entry
`+0x2c`. The semantic identity of those player fields is still unconfirmed.
The reset helper writes zero at `+0x00`, zeroes eight-byte spans beginning at
`+0x01`, `+0x09`, `+0x11`, and `+0x19`, writes
`0x00ffffff00000000` at `+0x24`, and clears `+0x2c`. In little-endian memory,
the qword at `+0x24` sets the metric to `0.0f` and seeds bytes `+0x28..+0x2b`
to `0xff`; the population path later overwrites some of those bytes, and the
builder explicitly clears `+0x2b`. The helper does not write `+0x21..+0x23`
or `+0x2d..+0x2f`.
The array shape is a candidate layout for the observed list region, not the
complete moments object.

## Shared global record reset routine

`global_record_array_storage_reset` (`0x7000675e20`) has no observed input or
output. It loads a pointer from absolute address `0x7002287240` and applies the
two 0x30-byte record initializers across `0x4b00` bytes, which is 400 entries.
It then initializes three explicit 20-entry runs at offsets `+0x48c`, `+0x84c`,
and `+0xc0c` from the base address `0x7003a78000`. This is 60 more entries;
those nonstandard starting offsets are preserved as observed instead of being
forced into a single contiguous array interpretation. The function therefore
touches 460 records across two global storage regions. Their semantic owners
and consumers remain unverified, so the name describes only the reset action.
See `decompiled/main/main_0050.c` at `f_7000675e20`.

The reset-only wrappers also separate those regions: `ranked_primary_20_record_rows_reset`
(`0x70006745d8`) clears 20 rows from `+0x48c`, while
`ranked_secondary_20_record_rows_reset` (`0x7000674694`) clears 20 rows from
each of `+0x84c` and `+0xc0c`. Both use the same 0x30-byte row reset helper.
These exact extents are clear from the generated loops/unrolled calls; the
meaning and owning type of the global table remain unresolved.

## Evidence and next recovery points

Generated implementation: `decompiled/main/main_0101.c` functions listed
above. Callers and callees are indexed in
[`function_behavior.tsv`](function_behavior.tsv). Detailed patch-site evidence
and the current-build event sequence are in
[`../tools/data/patches-1.0.20.txt`](../tools/data/patches-1.0.20.txt).
Next useful work is to trace the list comparator/key selection, identify the
meaning of the entry payload and sentinel, and find consumers of the moments
storage.
