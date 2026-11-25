# Swing aim error and contact evaluation

This is a partial reconstruction for the current generated build. The evidence map is useful for navigation, not a claim that every swing field or decision rule is known. The external comparison map was written against MLB The Show v1.0.15; current generated code addresses differ, so external semantics are used only where current accesses corroborate them.

## Current-build function chain

- `0x70003560f0` (`swing_aim_error_and_pci_size_update`) consumes a swing record in `x19` and a pitch trajectory/state pointer in `x21`. It writes the PCI point at swing `+0x08/+0x0c`, subtracts pitch coordinates at `+0x148/+0x14c`, saves the two error components at swing `+0x10/+0x14`, and saves their Euclidean magnitude at `+0x118`. It also adjusts the outer PCI size at `+0x64` based on a selector and mode flag, as described below.
- `0x7000358764` (`swing_contact_chance_evaluation`, medium confidence) reads the error magnitude and values at swing `+0x60/+0x64`, then updates contact-related state/flags. In the external v1.0.15 map this corresponds to the contact-chance routine at offset `0x358744`; the current function begins at `0x358764`, a `+0x20` address difference.
- `0x7000358520` calls that evaluator and proceeds with additional contact-result work. Its broader role remains tentative.

The v1.0.15 map's outer-PCI adjustment at `0x356a18` maps into `f_70003560f0` at `0x7000356a38`. The current code selects remap parameters using a 16-bit value at `+0x48` of a context-owned object and a byte flag at `+0x2b` of another context-owned object. It passes the swing's `+0x64` and `+0x60` sizes as output endpoints to `linear_remap_clamped` (`0x70013f1050`), then stores the result back to `+0x64`. This supports the external description that the outer PCI is pulled toward the inner PCI; the meanings of the context objects, selector, flag, and exact tuning constants remain unresolved. The helper's instruction-level behavior is documented in [MATH_HELPERS.md](MATH_HELPERS.md).

`f_7000358520` calls the chance evaluator and writes additional swing-record outputs: single-precision values at `+0x34`, `+0x38`, and `+0x160`, plus boolean-like bytes at `+0x84` and `+0x87`. The evaluator also reads float inputs at `+0x11c` and `+0x120`. These fields are now represented with their observed widths in `recovered/swing_types.h`; their source-level labels and gameplay meanings remain unknown. The wrapper's working name is `swing_contact_result_update`.

## Candidate fields

See [`recovered/swing_types.h`](recovered/swing_types.h) and [`../tools/data/field_annotations.tsv`](../tools/data/field_annotations.tsv). Coordinates and error-vector math are high-confidence current-build observations. The inner/outer PCI labels and plate-crossing labels are medium confidence because their names come from a v1.0.15 map, while current-build code corroborates the corresponding fields and use. These structs intentionally reserve unknown bytes and do not claim full object extent.

## Contact chance curve (reference-build description)

The v1.0.15 code map describes the nominal `Hitchance` curve at `0x358744`: within the inner PCI size (`swing+0x60`), chance ranges from 1 to 2; between the inner and outer sizes (`+0x64`), it falls from 1 to 0. The current v1.0.20 routine at `0x7000358764` reads the aim-error length (`+0x118`) and these two float fields, which supports the field correspondence. The current routine also has numerous state, mode, and property gates, so the simple curve is a reference-build description of its nominal calculation, not a complete current-build behavioral specification. The game log records this diagnostic as `Hitchance` per the reference map.

## Evidence

Current generated implementation: `decompiled/main/main_0027.c`, functions `f_70003560f0`, `f_7000358764`, and `f_7000358520`. External comparison: [ModTheShowManager CODE_MODS.md](https://github.com/elripalda/ModTheShowManager/blob/main/docs/CODE_MODS.md), explicitly versioned for v1.0.15.
