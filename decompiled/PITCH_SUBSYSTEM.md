# Pitch flight subsystem: current-build findings

This map covers the traced pitch path in the current extracted `main` module.
Function labels are stored in `tools/data/function_annotations.tsv`; field
labels and type evidence are in `tools/data/field_annotations.tsv`. Generated
C remains address-based and is not edited.

## Call path

| Address | Working name | What the evidence supports |
|---|---|---|
| `0x7001656fa4` | `pitch_release_velocity_setup` | Converts the release speed with the current-build constant `0x3fbbbbbc` (~1.4667) and builds the initial velocity vector. |
| `0x7001657c10` | `pitch_flight_update_orchestrator` | Runs the per-flight update path, manages state selectors, and calls the force/state and paired-state helpers. |
| `0x7001658448` | `pitch_flight_force_state_update` | Selects indexed flight state and updates force/state values. A runtime trace observed eight calls during one tracked pitch, each from the orchestrator. |
| `0x7001658b78` | `pitch_state_pair_distance_update` | Reads two indexed records, subtracts 3D float vectors at offsets `0x60` and `0x68`, calculates their distance, and continues with state updates. |
| `0x70016671a0` | `pitch_movement_delta_xy_magnitude` | Subtracts the aim/reference vector from the destination vector and calculates the XY magnitude. Its result matched the live “Actual Pitch Movement” log. |

The context contains two candidate state records beginning at `+0x30`, each
`0x70` bytes long; together they end at `+0x110`. The 32-bit values at `+0x110`
and `+0x114` select records with that stride. The update flips both selectors
with XOR 1, consistent with two alternating state buffers. The helper at
`0x7001658b78` compares a three-float vector at record offset `+0x60` between
the selected records and computes its Euclidean distance. The vector's game
meaning is still unknown.

The partial C layout with explicit unknown byte ranges is in
[`recovered/pitch_types.h`](recovered/pitch_types.h). It is a reconstruction
artifact and is not compiled into the generated recomp.

## Newly mapped pitch helpers

| Address | Working name | Evidence and limit |
|---|---|---|
| `0x7001657420` | `pitch_flight_integrate_selected_state` | Reads `+0x114` as an index, uses the `0x70` record stride, reads flight flags at `+0x174`, and performs a large numeric update. The exact integrator and formula are not yet reconstructed. |
| `0x700165e274` | `pitch_flight_append_sample_record` | Checks a count/capacity pair, addresses the new item at `base + count*0x38`, initializes it from three input arguments, and increments the owning count at `+0x0c`. |
| `0x7001656cd8` | `pitch_flight_selected_state_transfer_and_adjust` | Uses the two `0x70`-stride selectors, transfers values between selected slots, builds a 12-float block, and writes four float results at context `+0x14..+0x20`; exact physical meanings remain unknown. |
| `0x7001656310` | `vector3_build_frame_from_direction` | Reads a 3-float direction, computes magnitude/normalized components under a scalar gate, and writes twelve f32 outputs. Its frame convention is unresolved. |

Both names are working labels for stripped internal functions, not original symbols. These annotations were added to `tools/data/function_annotations.tsv`; addresses remain searchable in `function_name_index.tsv`.

### State-slot field evidence

The indexed records start at `context + 0x30 + selector*0x70`. The force/state helper writes three single-precision values at slot offsets `+0x00/+0x04/+0x08`; it reads floats at `+0x0c` and `+0x14` during its magnitude/threshold path. The paired-state helper reads the existing 3-float vector at `+0x60..+0x68` from both selected slots and computes Euclidean distance. Their source-level meanings are still unknown, so the recovered header preserves neutral field names and the unobserved bytes. The selected-state helper also writes a 12-float block at slot `+0x30..+0x5f`, using a direction at `+0x18`; the helper's output is frame-like, but its axis convention is not established. Four additional f32 results are written to context `+0x14`, `+0x18`, `+0x1c`, and `+0x20`. These fields are typed in the partial header with neutral names.

## Recovered context fields

The field evidence is version-specific to this extracted build. `PitchFlightContext`
is a working label for the shared pointer passed into the traced routines, not
an original game type name.

| Offset | Recovered type/name | Evidence and limit |
|---|---|---|
| `+0x30` | `PitchFlightStateSlot[2]` | Two `0x70`-byte slots; their `0xe0`-byte span ends at `+0x110`. |
| `+0x110` | `uint32_t flight_state_index_a` | Used to select a `0x70`-stride record and flipped with XOR 1. |
| `+0x114` | `uint32_t flight_state_index_b` | A second selector, flipped with the first. Exact role distinction is unknown. |
| `+0x174` | `uint32_t flight_flags_174` | Branches test bits 13 and 15; meanings of those bits are unknown. |
| `+0x18c` | `float flight_scalar_18c` | Treated as a float and clamped nonnegative; units and gameplay meaning are unknown. |
| `+0x2c6` | `uint8_t flight_flag_2c6` | A zero/nonzero branch input; domain meaning is unknown. |
| `+0x311` | `uint8_t flight_state_flag_311_candidate` | Cleared and later assigned a boolean-like value; domain meaning is unknown. |
| `+0x410` | `float release_position[3]` | Live values matched the release position printed in the game log. |
| `+0x420` | `float pitch_destination[3]` | Live value confirmed as the final pitch destination. |
| `+0x42c` | `float aim_reference_position[3]` | Live value confirmed as the vector subtracted from the destination. |

The currently known vectors occupy 12 bytes each. No padding or neighboring
field assumptions should be inferred from them.

Additional context accesses in the same state path are now typed: bytes at `+0x2c0` and `+0x2c1`, and floats at `+0x2d8` and `+0x2e4`. The first byte is conditionally cleared, the second is a branch input, and the floats enter threshold/validation arithmetic. Their physics meanings and units are unresolved.

An independent Wave116 audit checked the base, offset, width, and C type for all
11 existing `PitchFlightContext` and `PitchFlightStateSlot` field rows. All were
confirmed, including the `0x70` slot stride and the non-overlapping vectors at
`+0x410`, `+0x420`, and `+0x42c`. The audit did not resolve the gameplay meanings
of the state-slot distance vector, `+0x18c`, or the flag fields; those labels
remain deliberately cautious. See the [first audit batch](../tools/data/staging/wave116_pitch_audit01.jsonl)
and [second audit batch](../tools/data/staging/wave116_pitch_audit02.jsonl).

## Physics findings and open questions

- The release path uses the full float `0x3fbbbbbc` (~1.4667) to scale pitch speed before constructing
  the initial velocity.
- The force path adds a spin/lift contribution scaled by about `71.85965` and
  applies `-32.0` vertically. The cross-product interpretation is consistent
  with the prior code-map evidence, but units and exact integration order have
  not been fully reconstructed.
- Drag and air-density terms are present in the flight path. The `0.31` drag
  value comes from an older-build map and still needs exact confirmation in
  this current build.
- The exact timestep, table meanings, flag meanings, record member layouts,
  and state-update ordering remain open. The current findings are not enough
  for a game-exact standalone flight simulator.

See [dynamic_pitch_trace.md](dynamic_pitch_trace.md) for the runtime evidence
and [pitch-logic-notes.md](../pitch-logic-notes.md) for the broader code-map
and trajectory-model notes.

`pitch_flight_step_and_state_update` (`0x7001676ba0`) coordinates a state
step across the two 0x70-stride records, then invokes the existing integration,
force, and paired-distance helpers. It uses the selector words at `+0x110` and
`+0x114`, tests bits in `+0x174`, and reads/writes a byte at `+0x311`; the
meaning of that byte and remaining vector fields are unresolved.
