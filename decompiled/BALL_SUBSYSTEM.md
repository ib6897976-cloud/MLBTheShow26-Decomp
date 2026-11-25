# Pitch launch, throw launch, and ball release records

This is a partial current-build map. Semantic field names were checked against generated code and the v1.0.15 comparison map; the current build has different addresses.

## Current functions

- `0x7001666930` (`pitch_or_throw_dispatch`, high confidence) checks the byte at ball record `+0x482`. The pitch branch reads `+0x454` and calls `pitch_release_velocity_setup`; the throw branch reads `+0x458` and calls `throw_velocity_mph_to_world_units`.
- `0x7001656fa4` (`pitch_release_velocity_setup`, high confidence) scales pitch speed by float bits `0x3fbbbbbc` (about 1.4667) and constructs an initial velocity/output state.
- `0x70016894d0` (`throw_velocity_mph_to_world_units`, high confidence) applies the same factor to a 3D throw velocity vector when its flag allows it.
- `0x700166b774` (`ball_release_state_update`, medium confidence) follows the ball's `+0x560` object pointer, copies object-state vectors into the ball record, sets a release-state byte, and continues with a vector helper.

- `0x700165c02c` (`air_density_from_environment`, medium confidence) reads an environment-table row and computes a scalar in `s0`; the flight-update caller passes that result into the next force update. The mapped v1.0.15 air-density multiply falls inside this current function.
- `0x7001659c70` (`ball_collision_contact_update`, medium confidence) contains the current contact-response block mapped from the v1.0.15 ball-collision site; the block calculates response values and writes a contact-state record.

Candidate source signature `float air_density_from_environment(uint32_t environment_slot)` is recorded as a medium-confidence ABI inference in [`../tools/data/function_prototype_candidates.tsv`](../tools/data/function_prototype_candidates.tsv). It is distinct from the `Cpu *` recomp wrapper type.

## Release snapshot fields

Tracing `0x700166b774` shows the `+0x560` pointer is a state-object pointer. When the byte at ball `+0x481` is zero, the routine copies the 16-float matrix from source offsets `+0xb0..+0xef` into ball offsets `+0x3e0..+0x41f`, then sets the guard byte to 1. The source object initializer writes `1.0f` at matrix offsets 0, 0x14, 0x28, and 0x3c (the diagonal), and a separate helper copies 64 bytes into this same matrix field. It also sets byte `+0x337` and writes a single-precision value at `+0x3ac`. The matrix values represent a transform; row/column convention and world/local meaning are not established. The partial ball layout in `recovered/ball_types.h` now extends through `+0x560`; the source-object model is in `recovered/ball_state_object_types.h`.

## Candidate record fields

The partial type is in [`recovered/ball_types.h`](recovered/ball_types.h); detailed evidence is in [`../tools/data/field_annotations.tsv`](../tools/data/field_annotations.tsv). Current generated code proves access widths and branch/callee behavior. Field labels are reinforced by the external code map. Unknown regions remain reserved.

## Version mapping

See [VERSION_CROSSWALK.md](VERSION_CROSSWALK.md) for the matched v1.0.15 offsets. The dispatch, release-state, throw-speed, pitch-launch, force, and hit entries currently match an exact local `+0x14d0` offset; this shift is not a global conversion rule.
