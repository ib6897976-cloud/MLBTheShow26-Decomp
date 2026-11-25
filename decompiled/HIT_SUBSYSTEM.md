# Hit outcome and power calculation

This is a partial current-build reconstruction. The external comparison notes were written for v1.0.15, while this generated code is from a later build; the field meanings below are retained as candidates and cross-checked against accesses in current C.

## Function

`0x7001679cdc` (`hit_record_init_and_dispatch`, high confidence) initializes a hit result record and branches to the precomputed path at `0x7001679d18` or normal calculation at `0x700167bb7c`.

`0x7001679d18` (`precomputed_hit_processing`, medium confidence) handles the precomputed path. `0x700167bb7c` (`hit_outcome_and_power_calculation`, high confidence) receives the hit record in `x0` and keeps it in `x19`. It reads two float rating inputs at `+0x1c` and `+0x20`, conditionally stores 16-bit result values at `+0x4c` and `+0x4e`, and later reads the float at `+0x48`, multiplies it by approximately 1.4667, and updates hit vector values. The field sequence and role align with the v1.0.15 map's hit routine, with an exact `+0x14d0` entry shift from the documented v1.0.15 address.

The precomputed path calls `0x7001677f8c` (`precomputed_hit_result_setup`, medium confidence) with the output record, three float inputs, and a 0/1 control value. It stores hit type value 18 at `+0x08`, transformed inputs at `+0x40/+0x44/+0x48`, marker/control bytes at `+0x50/+0x51`, and a separate derived category value 7–10 at `+0x0c`. The `+0x0c` category is distinct from hit type. Separately, `0x7001679b2c` (`hit_vector_scaling_and_type_classification`, medium confidence) is called from the check-swing adjustment and the normal hit calculation. It reads `+0x48` as power, adjusts output vector values at `+0x28/+0x2c/+0x30`, then writes hit-type values 6–10 at `+0x08` from range checks. The v1.0.15 map identifies `+0x48` as power in mph; current normal-path code converts it by approximately 1.4667.

The v1.0.15 check-swing power multiplier site `0x16785f8` maps by `+0x14d0` to `0x7001679ac8`, inside current function `0x70016799f8`. That function derives a scalar and applies it to hit-record power at `+0x48` and float values at `+0x28/+0x2c/+0x30`, then may set byte `+0x54`. This supports naming the containing function `check_swing_hit_power_vector_adjustment` at medium confidence, but the exact scalar source and the meaning of the three scaled components are still unresolved. The correspondence is for an instruction site inside the function, not its entry address.

The partial `HitRecordCandidate` layout records `+0x28/+0x2c/+0x30` as three vector-like floats uniformly scaled by the check-swing factor applied to hit power at `+0x48`. The v1.0.15 reference map describes this region as direction then velocity, but current axis assignments are not established; the field therefore remains a candidate vector label. Byte `+0x54` is set to 1 on two paths and its flag meaning remains unknown.

The timing evaluator calls stripped helper `0x700167963c` (`hit_timing_quality_gate`). It rechecks the hit-record rating floats at `+0x1c/+0x20`, rejects when either condition byte at `+0x52/+0x53` is nonzero, and applies several context-derived floating remap/easing calculations before returning a boolean. This establishes its control-flow role but not the exact chance curve, external context fields, or gameplay labels for the two condition bytes. The label and a candidate bool prototype are recorded in the annotation/prototype tables.

The hit routine calls `0x70016794e0` (`perfect_timing_evaluation`) and stores its boolean result at `+0x4e`; the current helper checks timing/context conditions before returning 0 or 1.

`0x7001677ca0` (`bunt_hit_setup`, high confidence) builds the bunt case and writes hit type 18 at record `+0x08`, power at `+0x48`, and byte fields at `+0x50/+0x51`. The generic branch stores an incoming category at `+0x08`. Current `0x7001679b2c` classification writes numeric categories 6–10 to `+0x08`; the enum labels for these values (high fly, medium flyball, line drive, hard grounder, easy grounder) remain cross-version candidate meanings from the v1.0.15 map. `0x7001681314` (`hit_power_adjustments`, medium confidence) is called from the main hit calculation and updates power/result state. In the mapped current-build penalty range `0x7001681da4–0x7001682140`, it conditionally remaps factors using hit ratings at `+0x1c/+0x20`, checks hit type at `+0x08` and perfect timing at `+0x4e`, and reads the boolean-like conditions at `+0x52/+0x53` before modifying power at `+0x48`. The producing hit calculation `0x700167bb7c` sets both bytes from comparison results, but their specific gameplay meanings remain unresolved. This matches the reference map's power-penalty region, but the individual current factors cannot yet be assigned reliably to specific labels such as jammed or off-end. The swing path calls `0x700035abec` (`broken_bat_chance_evaluation`, medium confidence), whose code computes a bounded probability-like value from bat/context inputs.

Candidate source signature `bool perfect_timing_evaluation(HitRecordCandidate *hit, void *timing_context)` is recorded with medium confidence in [`../tools/data/function_prototype_candidates.tsv`](../tools/data/function_prototype_candidates.tsv); the timing-context pointee type remains unknown.

Candidate source signature `void hit_outcome_and_power_calculation(HitRecordCandidate *hit, void *hit_context)` is also recorded at medium confidence. The current dispatcher passes the hit record in `x0` and a context pointer in `x1`; the function writes into the record, and its known callers do not use a return value. The context pointee and the exact source return type remain inferred rather than symbol-confirmed.

The argument at `x1` now has a partial `HitCalculationContextCandidate` model in [`recovered/hit_context_types.h`](recovered/hit_context_types.h). Current accesses establish pointer slots at `+0x18`, `+0x40`, `+0x78`, `+0xb8`, `+0xc0`, `+0xf8`, and `+0x140`. The `+0x40` object has a 16-bit selector at `+0xbc`; current hit code compares it with 9 to choose between CPU and human hitter contact paths. This matches the v1.0.15 reference map's description of the settings block and its CPU-hitter value, so the semantic name remains a cross-version candidate. The `+0x78`, `+0xc0`, and `+0xf8` targets now have minimal nested layouts for the accessed bytes at `+0x35`, `+0x69/+0x6b`, and `+0x04/+0x07`; their gameplay meanings remain unknown. The `+0xb8` record contains sign-tested words at `+0/+4/+8` and a gating byte at `+0x34`. The `+0x140` object has a float at `+0x1c` and byte gates at `+0x4d/+0x4e`; either nonzero gate selects precomputed hit processing. Other opaque qwords occur at context `+0x38`, `+0x48`, `+0x58`, `+0xa8`, `+0x120`, and `+0x138`. The nested words' meanings and the auxiliary float's game meaning and units remain unknown. The modeled B8 record ends at `+0x37`, settings selector at `+0xbd`, auxiliary object at `+0x4e`, and context at `+0x147`; these observed extents do not establish allocation sizes. Reference: [CODE_MODS.md, hit routine notes](https://github.com/elripalda/ModTheShowManager/blob/main/docs/CODE_MODS.md#the-hit-function-at-167a6ac).

## Candidate structure

See [`recovered/hit_types.h`](recovered/hit_types.h) and [`../tools/data/field_annotations.tsv`](../tools/data/field_annotations.tsv). The current code proves access widths and arithmetic; the game-specific names are corroborated by the external map and therefore remain candidate labels. The struct is partial and does not imply the entire hit record is understood.

See [VERSION_CROSSWALK.md](VERSION_CROSSWALK.md) for the specific address correspondence and why the shift must not be generalized.

## Evidence

Current implementation: `decompiled/main/main_0159.c`, `f_700167bb7c`. External comparison: [ModTheShowManager CODE_MODS.md](https://github.com/elripalda/ModTheShowManager/blob/main/docs/CODE_MODS.md), v1.0.15.



