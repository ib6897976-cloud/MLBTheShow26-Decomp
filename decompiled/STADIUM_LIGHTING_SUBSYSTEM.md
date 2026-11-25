# Stadium lighting refresh and time-dependent props

This is a partial current-build reconstruction based on generated functions and
the local 1.0.20 patch analysis in [`../tools/data/patches-1.0.20.txt`](../tools/data/patches-1.0.20.txt).
The patch analysis records exact current guest addresses and instruction sites;
the generated C confirms those addresses are function boundaries and exposes
the current call graph. The notes describe a two-buffer lighting bake: an
incremental background bake fills the spare buffer, while a forced request can
finish the bake synchronously.

## Traced functions

| Address | Working name | Evidence and remaining limits |
|---|---|---|
| `0x70012d20a0` | `stadium_lighting_background_bake_scheduler` | Called by the lighting update path; the local patch analysis identifies its background bake flags as `0xec01`. The exact meaning of every flag is not recovered. |
| `0x700108b628` | `batter_up_lighting_request_handler` | Batter-up event handler contains the request site at main `+0x108bbb4`; the patch changes its `force` argument from 1 to 0 and marks the manager dirty. |
| `0x70012d0fcc` | `stadium_lighting_request_dispatch` | Called by the event handler and other lighting paths; dispatches into `0x70012d1e04`. |
| `0x70012d1e04` | `stadium_lighting_request_and_buffer_switch` | Handles a request, can switch to a matching spare buffer, or start a bake. The quick-switch block is at main `+0x12d1f30..+0x12d1f98`; its flags and counter behavior are documented in the patch analysis. |
| `0x70012e0150` | `stadium_lighting_bake_step_executor` | Runs bake steps. In the documented block, flag bit 9 makes it loop through all steps with GPU waits, while bit 8 requests a buffer switch at completion. The precise rendering work in every step is not mapped here. |
| `0x700128d2a0` | `indirect_lighting_probe_refresh` | Compares the global lighting-version counter with a cached 32-bit value at probe-state `+0x770`; on mismatch it marks probe state dirty. Other probe behavior is not fully described. |
| `0x70019fb800` | `stadium_time_prop_state_dispatch` | Called by the lighting request/update path with requested time and dispatches to the two prop-transition functions below. |
| `0x70019fb880` | `stadium_time_prop_transition_a` | One of the two mapped time-dependent prop transition paths. Which direction (enable or disable) it represents is not established by the local note. |
| `0x70019fbbb0` | `stadium_time_prop_transition_b` | The other mapped transition path. Its enable/disable direction is likewise unresolved. |

The local patch notes place the transition threshold at 19.5 hours, or 17.0
hours in months 0 and 12, for stadiums represented in the associated table.
The threshold and target functions are supported; per-prop identities and
which transition path corresponds to each state still need tracing.

## Candidate manager fields

[`recovered/stadium_lighting_types.h`](recovered/stadium_lighting_types.h)
records two observed lighting-manager fields and the separate probe-state
cache; unknown bytes remain reserved:

| Offset | Candidate field | Evidence |
|---|---|---|
| `+0xc2d` | dirty/request byte | The unforced request path sets this byte before calling the request dispatcher. |
| `+0xd38` | two-buffer selector (`uint32_t`, candidate) | Scheduler/request logic uses it to select one of two adjacent table values; the quick-switch path stores `1 - selector`. Which value means front/back remains unknown. |
| `+0xd3c` | bake flags (`uint32_t`) | The bake request and executor branch on this word; documented bits 8 and 9 control buffer switching and synchronous step execution. |
| probe state `+0x770` | cached lighting version (`uint32_t`) | Current `f_700128d2a0` compares it with the global lighting-version counter and marks probe state dirty when they differ. |

This is a minimum partial layout through `+0xd3f`, not the complete manager
size. See [`../tools/data/field_annotations.tsv`](../tools/data/field_annotations.tsv)
for evidence rows and confidence.

## Call path and open work

The current call chain is batter-up handler → request dispatcher → manager
request/buffer switch. The separate bake executor processes the rendering
steps, and the time-state dispatcher updates stadium props when the requested
time crosses the mapped threshold. The two buffers, all flag meanings, exact
GPU work, counter ownership, and prop records remain only partly reconstructed.
