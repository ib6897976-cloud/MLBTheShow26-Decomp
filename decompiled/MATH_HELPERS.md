# Reusable math helpers

This page records small recovered primitives that are called from multiple gameplay paths. Names are evidence-backed working labels, not original source names.

## `linear_remap_clamped` — `0x70013f1050`

**Candidate source signature**: `float linear_remap_clamped(float value, float input_start, float input_end, float output_start, float output_end)`.

The generated routine reads five scalar float arguments in `s0` through `s4`. It computes `t = (value - input_start) / (input_end - input_start)`, clamps `t` to `[0, 1]`, and returns `output_start + t * (output_end - output_start)`. If the input endpoints are equal, it chooses `t = 0`, so the result is `output_start`. This is based on the current function's comparisons, divide, min/max clamp, and fused multiply-add; it does not infer a name from a symbol.

A gameplay call site is the swing PCI size adjustment in `f_70003560f0`: the returned scalar is written to the swing record's outer PCI size at `+0x64`, with the current inner size at `+0x60` as the other output endpoint. The input selector and mode-dependent endpoints are selected by preceding code. See [SWING_SUBSYSTEM.md](SWING_SUBSYSTEM.md).

Evidence: `decompiled/main/main_0144.c`, `f_70013f1050`; caller setup and output store in `decompiled/main/main_0027.c`, `f_70003560f0`.

## `float_linear_range_remap_clamped` — `0x700185a080`

**Candidate source signature**: `float float_linear_range_remap_clamped(float value, float input_low, float input_high, float output_low, float output_high)`.

For distinct input endpoints, this helper clamps `value` to the closed input interval, computes `(clamped_value-input_low)/(input_high-input_low)`, then returns `output_low + t*(output_high-output_low)` using a fused multiply-add. If the endpoints compare equal, the observed branch returns `2*output_low-output_high`, rather than a conventional endpoint choice. The argument order follows the scalar registers `s0` through `s4` at the call sites.

This helper is used by the ranked category metric and by several other gameplay functions. Do not substitute it for `linear_remap_clamped` without preserving the equal-endpoint behavior. Evidence: `decompiled/main/main_0170.c`, `f_700185a080`; ranked call chain in `decompiled/main/main_0056.c`, `f_700076dd54`.
