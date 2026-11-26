# Player attribute access

This map records the current-build behavior of the numeric attribute accessor
used by player evaluation and ranking code. It documents a partial storage
view, not the full player-record layout.

## Recovered functions

| Address | Working name | Observed role |
|---|---|---|
| `0x700183e8e0` | `player_attribute_get_float` | Returns a selected stored or delegated player attribute as a float in `s0`. |
| `0x70018623d4` | `player_attribute_add_delta_and_refresh` | Adds a signed delta to an eligible direct slot and refreshes selected cached fields. |
| `0x7001862594` | `player_attribute_value_or_zero` | Reads direct signed-halfword values or a derived group, returning zero for unsupported IDs. |
| `0x70018625ec` | `nested_attribute_add_delta_or_derived` | Adds a signed delta at record `+0xa8+2*id`, or delegates derived IDs. |
| `0x7001862710` | `nested_attribute_value_or_zero` | Reads signed-halfword values at `+0xa8+2*id`, or delegates derived IDs. |
| `0x70006b8860` | `player_attribute_scalar_evaluate` | Combines several player attributes, local record bytes, and helper results into a scalar used by the ranked candidate path. Its precise baseball meaning is unresolved. |
| `0x7000658c4c` | `player_configured_metric_component_compute` | Reads configured attributes and combines remaps for the optional selector-0 ranking component. |
| `0x700183bb94` | `attribute_record_value_get` | Returns direct or derived integer values from a byte-oriented attribute record. |
| `0x700183c0c8` | `attribute_record_value_set` | Writes direct byte values or selected derived-field inputs into the same record family. |
| `0x700183bf50` | `attribute_record_validated_max_3c_41_get` | Returns the maximum present value in a six-byte candidate group. |
| `0x700183eafc` | `nested_attribute_provider_get_float` | Loads an optional attribute-block pointer from owner `+0x68`, then calls the nested block accessor. |
| `0x70018392f0` | `nested_attribute_block_get_float` | Reads a second numeric attribute domain with its own direct storage ranges and derived-ID handlers. |
| `0x70006b7f54` | `attribute_context_pointer_resolve` | Selects and returns a context pointer from a container's preferred or fallback slots. |
| `0x700066c46c` | `global_subject_pointer_membership_check` | Checks a nonnull subject pointer against a global object/list through the shared lookup helper; returns a boolean. |
| `0x7001824b74` | `attribute_context_status_value_get` | Maps a small selector through a global context record and returns a 16-bit or byte value; unsupported selectors return zero. |
| `0x7001825e40` | `attribute_context_mode_is_two` | Reads the global context mode byte at `+0x52`, masks its low bit, and returns true when the remaining value is `2`. |
| `0x700185bf80` | `attribute_context_category_in_range` | Returns true exactly for unsigned selector values `0x23..0x40`. |
| `0x700183e06c` | `player_attribute_group_54_63_compute` | Indexed derived-value handler for IDs `0x54..0x63`; formulas include guarded integer ratios and weighted/composite calculations. |
| `0x700183e290` | `player_attribute_group_64_75_compute` | Indexed derived-value handler for IDs `0x64..0x75`; formulas include guarded ratios, weighted calculations, and fixed-coefficient adjustments. |

## Direct mutation and derived reads

`player_attribute_adjust_or_get_group_54_63` (`0x700183e978`) takes a mutable
player-attribute block, an attribute ID, and a signed integer delta. A zero delta
returns `0.0f` before any record access. IDs `0x00..0x10` add the delta to the
signed halfword at `id*2`; IDs `0x11..0x53` add it to the byte at `id+0x11`.
Both paths store the truncated result and return the resulting value as a float.
For IDs `0x54..0x63`, it returns the value from
`player_attribute_group_54_63_compute` without mutating the record. IDs
`0x64..0xff` return `0.0f`. The name describes the observed behavior and is not
an original source symbol.

After direct updates, a selector table at `0x7001ddda96` refreshes several
dependent values for a small set of IDs. All other direct IDs return without a
dependent-field store. The refreshed values are still identified by offsets,
not baseball stat names:

| Updated ID(s) | Refreshed field(s) | Observed calculation |
|---|---|---|
| `0x00`, `0x3e`, `0x42..0x44` | `s16[+0x1a]` | `s16[+0x00] + u8[+0x4f] + u8[+0x53] + u8[+0x54] + u8[+0x55]` |
| `0x05` | `s16[+0x16]` | `s16[+0x0a] + u8[+0x31] + 2*u8[+0x35] + 3*u8[+0x39]` |
| `0x13`, `0x1b`, `0x21`, `0x25`, `0x2d` | `u8[+0x57]` | `u8[+0x2c] + u8[+0x32] + 2*u8[+0x36] + 3*u8[+0x3e]` (low byte stored) |
| `0x20`, `0x24`, `0x28` | `s16[+0x18]`, `s16[+0x16]` | `+0x18 = u8[+0x31]+u8[+0x35]+u8[+0x39]`; `+0x16 = u8[+0x31]+2*u8[+0x35]+s16[+0x0a]+3*u8[+0x39]` |

The caller at `0x70006b96a0` passes ID `0x49` and an integer delta, then ignores
the returned float. This confirms the update use case while leaving the source
class and attribute labels unresolved. Evidence is in `main_0170.c` at
`f_700183e978` and `main_0052.c` at its caller.


`player_attribute_adjust_or_get_group_54_63` (`0x700183e978`) takes a mutable
player-attribute block, an attribute ID, and a signed integer delta. A zero delta
returns `0.0f` before any record access. IDs `0x00..0x10` add the delta to the
signed halfword at `id*2`; IDs `0x11..0x53` add it to the byte at `id+0x11`.
Both paths store the truncated result and return the resulting value as a float.
For IDs `0x54..0x63`, it returns the value from
`player_attribute_group_54_63_compute` without mutating the record. IDs
`0x64..0xff` return `0.0f`. The name describes the observed behavior and is not
an original source symbol.

After direct updates, a selector table at `0x7001ddda96` refreshes several
dependent values for a small set of IDs. All other direct IDs return without a
dependent-field store. The refreshed values are still identified by offsets,
not baseball stat names:

| Updated ID(s) | Refreshed field(s) | Observed calculation |
|---|---|---|
| `0x00`, `0x3e`, `0x42..0x44` | `s16[+0x1a]` | `s16[+0x00] + u8[+0x4f] + u8[+0x53] + u8[+0x54] + u8[+0x55]` |
| `0x05` | `s16[+0x16]` | `s16[+0x0a] + u8[+0x31] + 2*u8[+0x35] + 3*u8[+0x39]` |
| `0x13`, `0x1b`, `0x21`, `0x25`, `0x2d` | `u8[+0x57]` | `u8[+0x2c] + u8[+0x32] + 2*u8[+0x36] + 3*u8[+0x3e]` (low byte stored) |
| `0x20`, `0x24`, `0x28` | `s16[+0x18]`, `s16[+0x16]` | `+0x18 = u8[+0x31]+u8[+0x35]+u8[+0x39]`; `+0x16 = u8[+0x31]+2*u8[+0x35]+s16[+0x0a]+3*u8[+0x39]` |

The caller at `0x70006b96a0` passes ID `0x49` and an integer delta, then ignores
the returned float. This confirms the update use case while leaving the source
class and attribute labels unresolved. Evidence is in `main_0170.c` at
`f_700183e978` and `main_0052.c` at its caller.

## Directly indexed storage

`player_attribute_get_float(record, id)` has two direct paths:

| Attribute IDs | Load | Address formula | Result conversion |
|---|---|---|---|
| `0x00..0x10` | signed 16-bit | `record + id*2` | signed integer to float |
| `0x11..0x53` | unsigned byte | `record + id + 0x11` | zero-extended integer to float |

The second range begins at `record+0x22` and ends at `record+0x64`. The first
range occupies `record+0x00..+0x21`. These accesses support the
`PlayerAttributeBlockCandidate` partial layout in
[`recovered/player_attributes_types.h`](recovered/player_attributes_types.h).
The recovered C candidate now gives each direct slot its numeric ID and exact storage type. Attribute names and units are not recovered for these IDs.

IDs above `0x53` do not follow either direct array path. Two exact membership
helpers partition the supported derived range: `0x7001859ac0` accepts
`0x54..0x63`, while `0x7001859ae0` accepts `0x64..0x75`. The getter dispatches
these ranges to `player_attribute_group_54_63_compute` (`0x700183e06c`) and
`player_attribute_group_64_75_compute` (`0x700183e290`), respectively. Each
uses an indexed case table to select a derived calculation. IDs above `0x75`
return `0.0f` without either group handler. The derived formulas do not carry
recovered baseball labels, but their arithmetic families are visible. The
`0x54..0x63` handler contains case paths that divide signed 16-bit values,
unsigned bytes, or sums of those values, with zero guards; other cases combine
multiple ratios or compute a ratio after adding stored counts. The
`0x64..0x75` handler has similar guarded ratios, plus weighted calculations
using fixed floating-point coefficients and adjustments based on signed words
and byte counters. The precise per-ID formulas require the embedded selector
tables and complete case mapping; stat names and units remain unresolved.

### Derived-ID to case map

I read the selector tables from the current main NSO at `0x7001ddda61`
(16 byte entries) and `0x7001ddda72` (18 little-endian 16-bit entries), then
matched each table value to the handler's branch target. This ties each ID to
the following case label and first-level data path. Offsets are relative to
the player record; `s16`, `u16`, and `u8` mean signed word, unsigned word, and
unsigned byte loads. `case` addresses are useful anchors in `main_0170.c`.

| ID | Case | Recovered calculation/path |
|---|---|---|
| `0x54` | `0x700183e094` | `s16[+0x0a] / s16[+0x00]`; zero inputs return zero. |
| `0x55` | `0x700183e0a0` | `s16[+0x0c] / s16[+0x02]`; zero inputs return zero. |
| `0x56` | `0x700183e0b4` | `s16[+0x0e] / s16[+0x04]`; zero inputs return zero. |
| `0x57` | `0x700183e0c8` | `u8[+0x29] / u8[+0x23]`; zero inputs return zero. |
| `0x58` | `0x700183e0dc` | `u8[+0x2a] / s16[+0x06]`; zero inputs return zero. |
| `0x59` | `0x700183e0f0` | `u8[+0x2b] / s16[+0x08]`; zero inputs return zero. |
| `0x5a` | `0x700183e114` | `u8[+0x2c] / u8[+0x24]`; zero inputs return zero. |
| `0x5b` | `0x700183e128` | `u8[+0x2d] / u8[+0x25]`; zero inputs return zero. |
| `0x5c` | `0x700183e13c` | `u8[+0x2e] / u8[+0x26]`; zero inputs return zero. |
| `0x5d` | `0x700183e150` | `u8[+0x2f] / u8[+0x27]`; zero inputs return zero. |
| `0x5e` | `0x700183e164` | `u8[+0x30] / u8[+0x28]`; zero inputs return zero. |
| `0x5f` | `0x700183e184` | `s16[+0x16] / s16[+0x00]`; zero inputs return zero. |
| `0x60` | `0x700183e1ac` | `(s16[+0x0a] + u8[+0x4f] + u8[+0x53]) / (s16[+0x00] + u8[+0x4f] + u8[+0x53] + u8[+0x54])`; zero numerator or denominator returns zero. |
| `0x61` | `0x700183e1dc` | Sum of `s16[+0x16] / s16[+0x00]` and `(s16[+0x0a] + u8[+0x4f] + u8[+0x53]) / (s16[+0x00] + u8[+0x4f] + u8[+0x53] + u8[+0x54])`; each component is independently zero-guarded. |
| `0x62` | `0x700183e240` | `(s16[+0x1e] + s16[+0x1c]) / (s16[+0x1e] + s16[+0x1c] + u8[+0x5d])`; zero numerator or denominator returns zero. |
| `0x63` | `0x700183e26c` | `u8[+0x60] / (u8[+0x60] + u8[+0x63])`; zero numerator or denominator returns zero. |
| `0x64` | `0x700183e2d0` | `((s16[+0x0a] + u8[+0x4f]) * s16[+0x16]) / (u16[+0x00] + u8[+0x4f])`; the `+0x00` word is zero-checked. |
| `0x65` | `0x700183e30c` | `s16[+0x16] / s16[+0x00]`, guarded by the `0x5f` supported-ID predicate and zero checks. |
| `0x66` | `0x700183e344` | `(s16[+0x16] + u8[+0x60] + u8[+0x4f] - s16[+0x0a] - u8[+0x63]) / s16[+0x00]`; zero denominator returns zero. |
| `0x67` | `0x700183e374` | `s16[+0x00] / u8[+0x39]`; zero denominator returns zero. |
| `0x68` | `0x700183e39c` | Returns `u8[+0x4f]` when `s16[+0x1a]` is nonzero; otherwise zero. |
| `0x69` | `0x700183e3a8` | Returns `u8[+0x4f]` when `s16[+0x14]` is nonzero; otherwise zero. |
| `0x6a` | `0x700183e3bc` | `(s16[+0x16] + u8[+0x4f] + u8[+0x53] + u8[+0x54] + u8[+0x55] + u8[+0x60]) / (s16[+0x00] - s16[+0x0a] + u8[+0x54] + u8[+0x55] + u8[+0x56] + u8[+0x63])`; returns zero if the divisor expression is zero. |
| `0x6b` | `0x700183e428` | Fused weighted sum: `0.47*(s16[+0x0a]-u8[+0x39]) + 0.78*u8[+0x31] + 1.09*u8[+0x35] + 1.4*u8[+0x39] + 0.33*(u8[+0x53]+u8[+0x4f]) + 0.33*(s16[+0x00]-s16[+0x0a]) - 0.25*(s16[+0x00]-s16[+0x0a])`. The final two terms use separate fused operations, in that order. |
| `0x6c` | `0x700183e4d8` | `(s16[+0x16] + u8[+0x4f] + u8[+0x53] + u8[+0x60]) / (s16[+0x00] - s16[+0x0a] + u8[+0x54] + u8[+0x55] + u8[+0x56] + u8[+0x63])`; returns zero if the divisor expression is zero. |
| `0x6d` | `0x700183e540` | Product of the ID `0x60` composite ratio and `s16[+0x16] / s16[+0x00]` (ID `0x5f`); both hard-coded range predicates pass. |
| `0x6e` | `0x700183e58c` | Duplicate product path: ID `0x60` composite ratio multiplied by ID `0x5f`'s `s16[+0x16] / s16[+0x00]` ratio; both hard-coded range predicates pass. |
| `0x6f` | `0x700183e5d8` | `(s16[+0x16] + s16[+0x12] + u8[+0x39]) / s16[+0x00]`; zero denominator returns zero. |
| `0x70` | `0x700183e5f8` | `s16[+0x10] + s16[+0x12] + s16[+0x16] + u8[+0x60] + 0.5*u8[+0x4f]`. |
| `0x71` | `0x700183e638` | `2 * u8[+0x39] * u8[+0x60] / (u8[+0x39] + u8[+0x60])`; zero sum returns zero. |
| `0x72` | `0x700183e670` | `s16[+0x16] / s16[+0x0a]`; zero denominator returns zero. |
| `0x73` | `0x700183e680` | `(s16[+0x0a] + u8[+0x39]) / s16[+0x00]`; zero denominator returns zero. |
| `0x74` | `0x700183e6b4` | `0.3*u8[+0x60] - 0.6*u8[+0x63]`. |
| `0x75` | `0x700183e6f4` | `27*(s16[+0x1c] + s16[+0x1e]) / s16[+0x20]`; returns zero if byte `+0x22` or the divisor is zero. |

The table resolves selector-to-case routing for all 34 primary derived IDs.
The formulas for IDs `0x6a..0x6e`, `0x70`, `0x71`, `0x74`, and `0x75` are now
normalized through their shared labels and literal range predicates. The
weighted cases use single-precision fused operations, so the written sums
describe their operands and order but not every intermediate rounding bit.
None of these offsets has a known source-level baseball stat name yet.

## Ranking use

`player_attribute_scalar_evaluate` (`0x70006b8860`) reads the player-record
byte at `+0xa2`, byte at `+0x72`, and word at `+0x70`. It calls the accessor
for IDs `0x6b`, `0x74`, `0x62`, `0x10`, and `0x11`, then combines results
with constants and other helpers. Its selector argument selects three paths:

| Selector | Behavior | Return value |
|---|---|---|
| `0` | Resolve an attribute context; read the five primary attributes above; compute a mode-dependent integer divisor with `global_mode_dependent_byte_or_0xa2_get`; optionally obtain `f_7000658c4c` when options bit 0 is set; then call `ranked_category_metric_compute` (`0x700076dd54`) using signed record byte `+0xa2` as category. | Category-specific metric described below. |
| `1` | Resolve the context; query nested IDs `0x5d` and `0x13`; select 0.35 when `(subject[+0x72] & 0xe0)==0`, otherwise 0.41; decode a signed 9-bit selector from subject word `+0x70`; if that selector resolves, select 3.7 when resolved-context byte `+0x47` is 1, otherwise 3.8; call `ranked_attribute_secondary_metric_compute` (`0x700076dd24`). | `(nested_13 / 9) * ((context_coefficient_3.7_or_3.8 - nested_5d) / 10 + 0.5 - subject_coefficient_0.35_or_0.41)`. |
| `2` | Recursively evaluate selectors 0 and 1, forwarding options bit 0 to selector 0 and clearing options for selector 1. | Sum of selector-0 and selector-1 results. |
| other | No scoring path. | `0.0f`. |

The selector-0 category helper `ranked_category_metric_compute` dispatches
category values 1 through 9 through a nine-entry table. It remaps primary ID
`0x62` from category-specific input ranges into `[-15, 30]`, giving
`R1`; it remaps primary ID `0x10` divided by 3 from `[0, 1250]` into
`[0, R1]`, giving `R2`. If options bit 0 is set, it also remaps the same
`ID 0x10 / 3` input from `[0, 1250]` into `[0, optional_helper_result]`,
giving `R3`, then replaces the composite with `0.25 + 0.75 * R3 * R2`.
Without the option bit, the composite is just `R2`. For categories 1 through 8, the category term
is 1 when primary ID `0x11` is nonpositive and 0 otherwise. Category 9 instead
uses `-17.375 * (primary_11 / divisor)`. The final returned metric is
`(primary_6b + primary_74 + remapped_composite + category_term) / 10`.
Categories outside 1..9 take a fallback path: category term 0, and the ID
`0x62` remap interval defaults to `[0.976, 1.000]` (the category-9 interval).
They do not enter the category-specific range cases. The range constants and
exact SIMD/FMA order are in `f_700076dd54` and its helper calls in
`main_0056.c`.

The category input intervals for remapping ID `0x62` are recoverable exactly:

| Category byte | Input low | Input high |
|---:|---:|---:|
| 1 | 0.989 | 1.000 |
| 2 | 0.977 | 0.999 |
| 3 | 0.965 | 0.994 |
| 4 | 0.954 | 0.995 |
| 5 | 0.963 | 0.997 |
| 6 | 0.958 | 1.000 |
| 7 | 0.920 | 1.000 |
| 8 | 0.968 | 1.000 |
| 9 | 0.976 | 1.000 |

These are the binary32 constants in the NSO, shown as decimal values. The
remap output interval is `[-15, 30]` for all nine categories.

`float_linear_range_remap_clamped` (`0x700185a080`) implements the remaps.
For distinct input endpoints it clamps the input value, computes its relative
position, and uses fused multiply-add to map between output endpoints. When
the input endpoints are equal, the observed special result is
`2 * output_low - output_high`; this differs from the separate helper
`linear_remap_clamped` (`0x70013f1050`), which returns `output_start` for
equal endpoints. `global_mode_dependent_byte_or_0xa2_get` (`0x70007697c4`)
returns `0xa2` unless the global attribute-context mode predicate is true;
then it returns the low byte produced by `f_70006ec414`.

When options bit 0 is set, selector 0 also calls
`player_configured_metric_component_compute` (`0x7000658c4c`). It returns
zero for a null input; otherwise it reads a series of configuration pointers
rooted at `0x7002286000`, makes eight numeric accessor calls with IDs
`0x17`, `0x3f`, `0x11`, `0x11`, `0x10`, `0x10`, `0x16`, and `0x0c`, and
combines several clamped remaps. Its result is the upper output bound of the
optional `R3` remap above. The configuration records and original names/units
of these inputs are still unresolved, so this helper is documented by its
call-site role and observed data flow rather than a guessed baseball label.

In
`ranked_stat_entry_rows_secondary_refresh` (`0x7000673660`), the selector
argument is derived from whether byte `+0xa2` is zero, and only positive
results become scratch records for sorting. That establishes the use of the
scalar as a ranking candidate metric, but not which statistic it represents.
In the primary accessor, IDs `0x10` and `0x11` take the direct 16-bit and byte
paths, respectively; `0x62` routes through the `0x54..0x63` derived handler,
and `0x6b`/`0x74` route through the `0x64..0x75` handler. The score routine
also queries IDs `0x13` and `0x5d` through the separate nested accessor below.
The complete meaning of the two scores and the names/units of their source
attributes are not yet recovered. In selector 1, the helper's `v0` and `v1`
inputs are nested ID `0x5d` and the subject-derived coefficient; `v2` is the
context-derived coefficient; and `v3` is nested ID `0x13`. This mapping is
established at the call site rather than inferred from the helper's stripped
name. The subject layout evidence is captured in `SubjectAttributeDataCandidate`:
a word at `+0x70` supplies the signed 9-bit selector, its overlapping byte at
`+0x72` supplies the coefficient flags, and the signed category byte is at
`+0xa2`. The rest of that subject record is unknown.

## Byte attribute record accessor

`attribute_record_value_get` (`0x700183bb94`) returns an integer value from
a byte-oriented record. IDs `0x00..0x17` load `record+id`; IDs `0x18..0x37`
load `record+id+0x10`, which maps them to bytes `+0x28..+0x47`. ID `0x38`
and IDs above `0x44` return zero. IDs `0x39` and `0x3a` compute selector-aware
maximums over candidate bytes `+0x36..+0x3b` and `+0x3c..+0x41`, respectively,
using the corresponding `pitch0_type`..`pitch5_type` bytes at `+0x48..+0x4d` as 0xff sentinels/category selectors and applying a `0x303` membership
mask to encoded categories 0..9 (accepted values are 0, 1, 8, and 9). It tracks
a filtered and an unfiltered maximum, returning the unfiltered maximum when the
filtered maximum is zero. This partial
layout is represented by `AttributeRecordCandidate` in the recovered header;
the recovered structure now names fields supported by exact NSO keys, while the remaining byte semantics and full source-level identity remain unresolved.

The byte-accessor record has an observed extent of `0x4e` bytes. Two rows previously grouped with it are accesses on a different subject-data pointer: the word at subject `+0x70` and signed category byte at subject `+0xa2` belong to `SubjectAttributeDataCandidate`. The category byte is explicitly sign-extended before selector arithmetic (`main_0052.c`, `f_70006ad360`, lines 24477–24485). The field table now keeps these layouts separate.

The fallback for the `0x3a` candidate group is independently implemented by
`attribute_record_validated_max_3c_41_get` (`0x700183bf50`): it returns the
maximum of unsigned bytes `+0x3c..+0x41` whose matching `+0x48..+0x4d` byte is
not `0xff`, or zero if all six are absent. The inlined accessor path adds its
filtered `0x303` selection before choosing that overall maximum as fallback.

IDs `0x3b..0x44` use a ten-entry selector table at main-rodata `0x7001ddd9e6`:

| ID | Recovered operation |
|---:|---|
| `0x3b` | `((30*u8[+0x03] + 70*u8[+0x04]) * 0x147b) >> 19`, using a fixed-point approximation to divide the weighted sum by 100. |
| `0x3c` | `((30*u8[+0x01] + 70*u8[+0x02]) * 0x147b) >> 19`, using the same fixed-point approximation to divide by 100. |
| `0x3d` | `(u8[+0x2a] + u8[+0x2b]) >> 1`. |
| `0x3e` | `(u8[+0x2d] + u8[+0x2e]) >> 1`. |
| `0x3f` | `(u8[+0x12] + u8[+0x13] + u8[+0x14] + u8[+0x15]) >> 2`. |
| `0x40` | `100 - int8[+0x24]`. |
| `0x41` | `int8[+0x24]`. |
| `0x42` | `int8[+0x25]`. |
| `0x43` | `100 - (int8[+0x25] + int8[+0x26])`. |
| `0x44` | `int8[+0x26]`. |

This accessor is one of the inputs to `player_configured_metric_component_compute`
(`0x7000658c4c`), which requests IDs `0x17`, `0x3f`, `0x11`, `0x11`,
`0x10`, `0x10`, `0x16`, and `0x0c`. Exact meanings for the underlying byte
fields and derived values remain unresolved.

## Byte attribute record setter

`attribute_record_value_set` (`0x700183c0c8`) uses the low byte of its ID
argument and truncates direct values to one byte. IDs `0x00..0x17` store at
`record+id`; IDs `0x18..0x37` store at `record+id+0x10`. IDs `0x38..0x3a`
do not write anything. IDs `0x40`, `0x41`, `0x42`, and `0x44` update the
signed derived-input triplet at `+0x24..+0x26`:

| ID | Store behavior |
|---:|---|
| `0x40` | `record[+0x24] = (uint8_t)(100 - value)` |
| `0x41` | `record[+0x24] = (uint8_t)value` |
| `0x42` | `record[+0x25] = (uint8_t)value` |
| `0x43` | Delegate to `f_7000574c40` with descriptor `0x7001d5535d`, ID, and value; no direct field write in this routine. |
| `0x44` | `record[+0x26] = (uint8_t)value` |

IDs `0x3b..0x3f` and IDs `0x45..0xff` also delegate to
`f_7000574c40` using descriptor `0x7001d5535d`; the descriptor's source-level
meaning and the delegate's update semantics are not recovered. The signed
field triplet is modeled in `AttributeRecordCandidate` and its field evidence
is in `../tools/data/field_annotations.tsv`.

## Nested attribute block

`nested_attribute_provider_get_float(owner, id)` reads a pointer from
`owner+0x68`; null returns `0.0f`, otherwise the same ID is forwarded to
`nested_attribute_block_get_float`. This supports the minimal
`NestedAttributeProviderCandidate` pointer field in
[`recovered/player_attributes_types.h`](recovered/player_attributes_types.h), but does not identify the
owner object's complete type.

The score routine obtains its context through `attribute_context_pointer_resolve`
(`0x70006b7f54`). It clears the caller's out pointer, rejects null output,
container, or subject-data pointers, then derives a signed 9-bit selector from
the subject's word at `+0x70`. Eligibility also depends on the result of
`global_subject_pointer_membership_check` (`0x700066c46c`) and context-status
values queried through `attribute_context_status_value_get` (`0x7001824b74`)
for selector `0x13`. A nonzero result selects the preferred path; the code
checks explicit values `3` and `4` before a general nonzero check, then also
uses `attribute_context_mode_is_two` (`0x7001825e40`) when the status is zero.
The earlier membership/range gates can also select the preferred path. It
prefers container `+0x08`. When that slot is null, it selects `+0x20` if the
signed selector falls in unsigned range `0x23..0x40` (`0x700185bf80`), otherwise
`+0x28`. The global mode helper checks whether byte `+0x52` masked with
`0xfe` equals two. The selected context is the owner passed to the
nested accessor. These observations establish control flow and storage, while
the original game meaning of the status values and context categories remains
unresolved. Candidate slots and widths are in
`AttributeContextContainerCandidate`.

| Attribute IDs | Load or handler | Address mapping |
|---|---|---|
| `0x00..0x15` | signed 16-bit | `block + id*2` |
| `0x16..0x4f` | unsigned byte | `block + (((id - 0x16 + 0xea) & 0xff) + 0x2c)` |
| `0x50..0x5b` | derived float | `nested_attribute_group_50_5b_compute` (`0x7001839114`) |
| `0x5c..0x5f` | derived float | `nested_attribute_group_5c_5f_compute` (`0x700183938c`) |
| above `0x5f` | zero | returns `0.0f` |

The recovered layout now gives each raw slot its numeric attribute ID and storage type (`int16_t` for IDs 0x00..0x15; `uint8_t` for IDs 0x16..0x4f). This names the data contract without inventing game-stat names for IDs whose meanings are still unknown.

The wrapped byte mapping splits physically: IDs `0x16..0x2b` read bytes at
`block+0x116..+0x12b`, while IDs `0x2c..0x4f` read `block+0x2c..+0x4f`.
This is modeled in `NestedAttributeBlockCandidate` in the recovered types
header. For the score routine, ID `0x13` reads signed 16-bit value at nested
block `+0x26`; ID `0x5d` reaches the `0x5c..0x5f` derived handler. The nested
derived handler entry points use embedded selector tables in the main NSO. I
decoded those tables and matched all 16 nested derived IDs to their cases:

| ID | Case | Recovered calculation/path |
|---|---|---|
| `0x50` | `0x700183913c` | `s16[+0x08] / s16[+0x00]`; zero inputs return zero. |
| `0x51` | `0x700183915c` | `s16[+0x0a] / s16[+0x02]`; zero inputs return zero. |
| `0x52` | `0x700183917c` | `s16[+0x0c] / s16[+0x04]`; zero inputs return zero. |
| `0x53` | `0x700183919c` | `s16[+0x0e] / s16[+0x06]`; zero inputs return zero. |
| `0x54` | `0x70018391bc` | `27 * s16[+0x12] / s16[+0x26]`, upper-capped at `999.99`; zero divisor with positive numerator returns the cap. |
| `0x55` | `0x70018391cc` | `27 * s16[+0x14] / s16[+0x28]`, upper-capped at `999.99`. |
| `0x56` | `0x70018391dc` | `27 * s16[+0x16] / s16[+0x2a]`, upper-capped at `999.99`. |
| `0x57` | `0x7001839218` | `27 * u8[+0x4e] / u8[+0x5a]`, upper-capped at `999.99`; zero divisor with positive numerator returns the cap. |
| `0x58` | `0x700183922c` | `27 * u8[+0x4f] / u8[+0x5b]`, upper-capped at `999.99`. |
| `0x59` | `0x7001839264` | `27 * u8[+0x50] / u8[+0x5c]`, upper-capped at `999.99`. |
| `0x5a` | `0x7001839274` | `u8[+0x35] / (u8[+0x35] + u8[+0x3b])`; zero sum returns zero. |
| `0x5b` | `0x7001839294` | `3 * (s16[+0x08] + u8[+0x54]) / s16[+0x26]`, upper-capped at `999.99`. |
| `0x5c` | `0x70018393b8` | Fixed-coefficient composite using signed words `+0x08/+0x24/+0x26` and bytes `+0x51/+0x54`; no explicit cap observed. |
| `0x5d` | `0x7001839460` | Fixed-coefficient composite using signed words `+0x18/+0x26` and bytes `+0x51/+0x54/+0x5e`; no explicit cap observed. |
| `0x5e` | `0x70018394b8` | `3 * (s16[+0x18] + u8[+0x54]) / s16[+0x26]`; no explicit cap observed. |
| `0x5f` | `0x70018394e0` | `27 * s16[+0x18] / s16[+0x26]`; no explicit cap observed. |

The capped cases use the exact single-precision constant `0x4479ff5c`
(`999.98999`).
The table bytes are at `0x7001ddd894` for IDs `0x50..0x5b` and
`0x7001ddd8a0` for IDs `0x5c..0x5f`. The layout candidate now identifies the
observed byte inputs at nested-block `+0x51`, `+0x54`, `+0x5a..+0x5c`, and
`+0x5e`; other bytes remain unknown. Game-specific stat names and units are
still unresolved.

See also the [broadcast leaders map](BROADCAST_LEADERS_SUBSYSTEM.md) and the
hand-reviewed function and field evidence in `../tools/data/`.
## Attribute-record provider and default singleton

`attribute_record_pointer_or_default(owner)` reads a pointer from owner `+0x48`; if nonnull it returns that `AttributeRecordCandidate`, otherwise it returns the process-wide default record at `0x700466e6b8`. `default_attribute_record_singleton_get` guards initialization with the byte at `0x700466e6b0`, initializes the singleton through `record_initialize_empty_and_clear_payload`, and then returns its address. The fallback is returned without being written into the owner. This validates the `AttributeRecordProviderCandidate` pointer field, while the provider's remaining layout is unknown.

## Shared keyed-value lookup

The property decoder calls `property_map_find_u32(map, key, out_value)` for each exact NSO attribute name. The helper hashes the NUL-terminated key, searches the map's entry structure, converts a matching value, writes a 32-bit result to the caller's output slot, and returns a boolean presence result. Missing or null keys return false. The player decoder then passes the low byte of selected results into the backing-object setters. This establishes the lookup output width; it does not establish the input file's source-level schema or the application range of each attribute.

## Pitch-type property slots recovered from NSO keys

`f_70008de2fc` decodes a broad player-attribute property set. Its exact NSO keys `pitch0_type` through `pitch5_type` each feed `f_700183c534` with indices 0 through 5. The setter writes a byte at backing-object offset `+0x48+index`, yielding six `uint8_t` fields at `+0x48..+0x4d`. The backing base is the object returned by `f_7001843d80`. Its indexed getter and setter share the offsets of `AttributeRecordCandidate`, so these named fields are merged into that candidate in `recovered/player_attributes_types.h`; the full source-level class and enum domain remain unknown.

The initial rank keys share the first backing byte: `rank` writes offset `+0x00`; if `has_rank_change` is present and evaluates true, the decoder also looks up `new_rank` and writes that same byte. The `has_rank_change` key controls this branch and is not itself stored in the recovered backing byte range.

The wider key-to-store map also recovers these byte fields (offsets are relative to the `AttributeRecordCandidate` base):

| Offset | Field / exact key(s) |
|---:|---|
| `+0x01` | `contact_left` |
| `+0x02` | `contact_right` |
| `+0x03` | `power_left` |
| `+0x04` | `power_right` |
| `+0x05` | `batting_clutch` |
| `+0x06` | `bunting_ability` |
| `+0x07` | `drag_bunting_ability` |
| `+0x08` | `plate_vision` |
| `+0x09` | `plate_discipline` |
| `+0x0b` | `durability` |
| `+0x0c` | `speed` |
| `+0x0d` | `base_stealing` |
| `+0x0e` | `baserunning_ability` |
| `+0x0f` | `arm_strength` |
| `+0x10` | `arm_accuracy` |
| `+0x11` | `fielding_ability` |
| `+0x12` | `reaction_time` (`reaction_time`, `reaction_time_left`) |
| `+0x13` | `reaction_time_right` |
| `+0x14` | `reaction_time_forward` |
| `+0x15` | `reaction_time_back` |
| `+0x16` | `blocking` |
| `+0x17` | `pop_time` |
| `+0x28` | `stamina` |
| `+0x29` | `pitching_clutch` |
| `+0x2a` | `hits_per_bf` (`hits_per_bf`, `hits_per_bf_left`) |
| `+0x2b` | `hits_per_bf_right` |
| `+0x2c` | `hr_per_bf` |
| `+0x2d` | `k_per_bf` (`k_per_bf`, `k_per_bf_left`) |
| `+0x2e` | `k_per_bf_right` |
| `+0x2f` | `bb_per_bf` |
| `+0x36` | `pitch_velocity` (`pitch_velocity`, `pitch_0_velocity`) |
| `+0x37` | `pitch_1_velocity` |
| `+0x38` | `pitch_2_velocity` |
| `+0x39` | `pitch_3_velocity` |
| `+0x3a` | `pitch_4_velocity` |
| `+0x3b` | `pitch_5_velocity` |
| `+0x3c` | `pitch_movement` (`pitch_movement`, `pitch_0_movement`) |
| `+0x3d` | `pitch_1_movement` |
| `+0x3e` | `pitch_2_movement` |
| `+0x3f` | `pitch_3_movement` |
| `+0x40` | `pitch_4_movement` |
| `+0x41` | `pitch_5_movement` |
| `+0x48` | `pitch0_type` (`pitch0_type`) |
| `+0x49` | `pitch1_type` (`pitch1_type`) |
| `+0x4a` | `pitch2_type` (`pitch2_type`) |
| `+0x4b` | `pitch3_type` (`pitch3_type`) |
| `+0x4c` | `pitch4_type` (`pitch4_type`) |
| `+0x4d` | `pitch5_type` (`pitch5_type`) |

Several keys are aliases to one storage byte: `reaction_time`/`reaction_time_left`, `hits_per_bf`/`hits_per_bf_left`, `pitch_velocity`/`pitch_0_velocity`, and `pitch_movement`/`pitch_0_movement`. This is established from the dispatch labels targeting the same setter index, not inferred from naming similarity. Unmapped gaps remain unnamed.

## Additional direct and nested accessors

`player_attribute_value_or_zero` follows the direct ID ranges documented above: IDs
`0x00..0x53` load a signed halfword at `record+2*id` and convert it to float;
IDs `0x54..0x63` route to the derived calculator; other IDs return zero.
`player_attribute_add_delta_and_refresh` applies a signed delta to eligible direct
IDs and updates selected cached halfword/byte slots through an ID dispatch table.
The selector meanings are not yet mapped.

A separate helper pair receives an opaque record pointer and accesses a signed
halfword at `record+0xa8+2*id` for direct IDs `0x00..0x4f`. IDs `0x50..0x5b`
route to `nested_attribute_group_50_5b_compute`; larger IDs return zero. The
`+0xa8` base is verified, but the enclosing structure identity and the meaning
of this subrecord are not established, so the prototype keeps the pointer opaque.
Evidence: `main_0171.c` at `f_70018623d4`, `f_7001862594`,
`f_70018625ec`, and `f_7001862710`.

## Separate extended derived-calculation context

Two additional dispatchers consume a larger record view than the compact
`PlayerAttributeBlockCandidate`; keep these layouts separate.
`f_70018620c0` dispatches the 0x54..0x63 group through a separate table at
`0x7001dde178`. Case labels are recovered from code, but the table bytes needed
to associate each case with an ID are not in the current decomp artifact.
Observed cases include ratios `s16[+0x0a]/s16[+0x00]`,
`s16[+0x0c]/s16[+0x02]`, `s16[+0x0e]/s16[+0x04]`,
`s16[+0x30]/s16[+0x24]`, `s16[+0x32]/s16[+0x06]`,
`s16[+0x34]/s16[+0x08]`, `s16[+0x36]/s16[+0x26]`,
`s16[+0x3c]/s16[+0x2c]`, `s16[+0x3e]/s16[+0x2e]`, and
`s16[+0x16]/s16[+0x00]`, with zero guards. Composite cases combine
`u16` and `s16` operands at `+0x00..+0xa4`.

`f_7001862294` is a separate nested-group calculator using a selector table at
`0x7001dde188`; its ID mapping is likewise unresolved. Observed cases use
`(+0xb0/+0xa8)`, `(+0xb2/+0xaa)`, `(+0xb4/+0xac)`, `(+0xb6/+0xae)` ratios;
capped `27*n/d` formulas at pairs `(+0xba/+0xce)`, `(+0xbc/+0xd0)`,
`(+0xbe/+0xd2)`, `(+0x118/+0x130)`, `(+0x11a/+0x132)`,
`(+0x11c/+0x134)`; and composite formulas using `+0xe6`, `+0xf2`,
`+0xb0`, `+0x124`, and `+0xce`. The cap constant is 99.0 when the denominator
is zero and the numerator is nonzero. These calculations support the raw
halfword operand view in `recovered/extended_attribute_context_types.h`;
they do not establish baseball stat names or selector IDs. Evidence is in
`main_0171.c` at `f_70018620c0` and `f_7001862294`.

See [RANKING_SUBSYSTEM.md](RANKING_SUBSYSTEM.md) for candidate rebuilding and the configured metric evaluator.

## Bulk component application

`player_attribute_component_values_apply` (`0x700185d380`) and
`player_attribute_component_values_apply_from_nested_context` (`0x700185d540`)
extract 14 component entries through the collection helper using owner `+0x50`.
They read values for direct IDs `0x00..0x53` and nested IDs `0x00..0x4f`, then
write through the direct and nested update helpers. Their child context pointers
differ (`entry+0x18` versus `entry+0x08`), so they remain separate paths. The
first path also reads an optional settings pointer at owner `+0x548`; when
non-null it reads configuration bytes, otherwise it uses a fixed default.

`player_attribute_context_adjust` (`0x700185d9d0`) applies negated provider
values across direct IDs and nested IDs `0x16..0x39`, writes selected
context-dependent values, and refreshes derived state at owner `+0x3b8`.
These operations establish the update behavior but not the meanings of the IDs
or the enclosing owner class. The observed `+0x548` pointer is represented in
`recovered/player_attribute_component_owner_types.h`.

`aggregate_attribute_candidate_values` (`0x7000cfa410`) is an adjacent
selector-driven routine that calls `build_attribute_candidate_views` and the
direct/nested getters, then copies or clears candidate records. Its output fields
remain unlabeled; see its address-level annotation for evidence.

`evaluate_attribute_context_metric` (`0x700073fc20`) selects indexed metric
paths using context mode and subject fields at `+0xa2` and `+0x70`, then
combines scalar, direct, and nested attribute results into a float. The caller
also passes a counter-like pointer that is incremented in indexed paths. The
specific metric labels and subject type are not recovered.

`player_attribute_summary_records_rebuild` (`0x7000e87960`) rebuilds 23 output
records with `0xcc`-byte stride. It uses status selector `0x13`, direct and
nested attribute getters, and a mode input to initialize flags and pack metric
results. Several record fields and the record's owning type remain unresolved;
do not infer baseball labels from the attribute IDs alone.

`collect_status_filtered_attribute_values` (`0x70007bd150`) scans a configured
12-byte entry table, filters through context status, and gathers nonzero direct
or nested attribute values. Its pointer/value scratch entries are local to the
function, so they are documented as scratch observations rather than a
persistent structure. The table's attribute group and status labels are not
known.

`player_attribute_group_metric_get_float` (`0x700183d480`) dispatches a
32-bit attribute ID to direct ratio formulas or nested-context metric lookups.
The partial subject view records three signed halfword operands at `+0x00`,
`+0x0a`, and `+0x16`, byte operands at `+0x4f`, `+0x53`, and `+0x54`, and the
nested-context pointer at `+0x68`. These fields are typed by access behavior;
their domain labels and enclosing object are unknown. The routine also reads a
live pointer from guest register `x8`; its high-level ABI role is unresolved.

`apply_context_attribute_deltas` (`0x70007701c0`) chooses context status 1 or
2 from its mode, reads and integer-converts direct IDs `0x00..0x53` and nested
IDs `0x00..0x4f`, then applies values through the state pointer at owner
`+0x3b8`. A wrapper calls it with modes 0 and 1. These ranges and modes are
observed behavior; their game-level labels remain unknown.

`apply_attribute_context_deltas` (`0x7000447240`) resolves a writable target
from a context selector, then adds integer-converted provider values for direct
IDs `0x00..0x53` and nested IDs `0x00..0x4f`. Its owner has an observed context
pointer at `+0x00`, provider pointer at `+0x30`, and packed selector at `+0x70`;
selector and owner semantics remain unknown.

`populate_attribute_derived_record` (`0x7000a0a630`) fills mode-selected output
records from player and nested attribute reads plus configuration lookups.
Callers populate adjacent slots with modes 1 and 0. A pointer write at output
`+0x08` is typed, while the other output fields and record purpose are
unresolved.

`build_ranked_attribute_metrics` (`0x7000e9bfe0`) combines fixed-constant float
calculations and attribute selectors `0x10/0x11`, then maintains an ordered
per-category cache. Its partial record view includes a clamped float at `+0x08`,
a cache head at `+0x2f8`, and counter at `+0x300`; cache nodes are allocated at
0x190 bytes with links at `+0/+8` and a 16-bit key at `+0x1c`. Metric labels,
record identity, and the second context type remain unresolved.

`populate_player_attribute_search_metrics` (`0x7000e8e82c`) fills a large
result object after status/context checks, with repeated direct and nested
attribute reads and derived scalar calculations. The result pointer at `+0x00`
is validated; writes span regions through at least `+0x6a8c`, but most output
fields and the business meaning remain unresolved. Player-search strings appear
in static metadata, without a proven call-site link.

`apply_equipment_attribute_property_updates` (`0x70008eafe8`) follows a
property/configuration path associated in static metadata with the exact key
`EQUIPMENT_ATTRIBUTE_VALUE`. It applies nested component values, resolves
additional property keys, and updates direct/nested attribute state. The
individual key-to-field mappings and the caller object type are not recovered.

`evaluate_contextual_attribute_condition` (`0x7001872670`) is a boolean
predicate selected by a 32-bit mode. It combines virtual-method checks, nested
attribute floats, direct attribute ID `0x18`, clamped remaps, and global status
selectors. Its mode-specific rule labels remain unknown.

`rebuild_attribute_derived_buffers` (`0x70010e22d0`) initializes a large
block and six 0x100-byte regions, then feeds parameter calculations from direct
and nested attribute reads. Only the owner+0x28 holder pointer and the holder
+0x08 attribute-record pointer are typed; region semantics remain unknown.

`apply_attribute_record_rule` (`0x700067b830`) dispatches a 16-byte descriptor
by its 32-bit kind at `+0x00`. The lifted switch has explicit cases for raw
kinds 1 through 5; other values take the no-op/default path. Raw kind 2 returns
the 32-bit operand at `+0x08` directly. Raw kind 1 queries and updates a record
value using the `+0x04` selector and `+0x08` operand. The remaining cases call
record and attribute helpers, including range checks against selectors. The
numeric values are established, but their domain names and the exact semantics
of kinds 3-5 are still unknown. The caller at `0x700067b7a0` walks 16-byte
entries in a nested table and invokes this routine for each entry.


## Candidate selection and record scans

`evaluate_player_attribute_candidates` (`0x7000438470`) and
`evaluate_nested_attribute_candidates` (`0x70004386b0`) are parallel routines
that read direct versus nested attribute values while examining candidate
records. They return a 32-bit result and write a byte through an output
pointer. Higher-level code invokes them for repeated attribute IDs and stores
the byte results in an output block. Their exact ranking rule and candidate
layout remain unknown (`main_0032.c:41619-41712,41834-41862`; caller
`main_0053.c:25368-25418`).

`process_attribute_candidate_set` (`0x7000716690`) inspects candidate records
and returns a signed halfword observed at candidate `+0x130`; it also reads a
signed byte at `+0xa2`. The selector/filter meaning is unresolved
(`main_0054.c:41135-41805`).

`find_matching_strided_record` (`0x70007092f0`) scans a strided table using an
index and mode, optionally stores the matching record pointer, and returns a
boolean. The shared table helper establishes records at base `+0x50` with a
`0x550` stride; matching conditions remain unresolved
(`main_0054.c:25363-25628`; table helper `main_0169.c:28850`).

`sort_and_filter_attribute_candidates` (`0x7000758a70`) creates 16-byte rows
with attribute-derived float values, sorts them, and filters candidates using
status/config and packed record fields. Its output contract and ordering rule
are still unknown (`main_0056.c:12269-12544`).

`select_attribute_record_candidate` (`0x7000670ea0`) builds and sorts
candidate rows, filters pointers using packed record fields, then selects a
candidate with an RNG-derived index. The candidate category and filter
meanings remain unresolved (`main_0050.c:3595-3816`).


`calculate_contextual_attribute_value` (`0x70007404f8`) combines direct and
nested attribute reads with status/mode checks and a clamped linear remap.
Context offsets `+0xa2` (signed byte) and `+0x70` (u32) are observed, but the
result's selector meaning is unknown (`main_0055.c:36200-36565`).

`initialize_player_attribute_state` (`0x70010bfa40`) mutates a record-like
object using status and attribute helpers; two observed u32 stores are at
`+0x1f74` and `+0x1fa0`. The complete record layout is unresolved
(`main_0123.c:5780-6047`).

`evaluate_object_attribute_condition` (`0x700186ee64`) dispatches mode-selected
virtual methods, checks status and direct/nested attributes, and returns a
boolean. Its condition labels and virtual method signatures remain unknown
(`main_0171.c:16290-16558`).


`resolve_context_attribute` (`0x700048ef70`) dispatches attribute IDs and
context categories into direct/nested accessors and branch-specific scalar or
vector packing paths. Its output layout changes by branch and is not yet
recovered (`main_0034.c:35665-36684`).

`collect_and_sort_attribute_records` (`0x70006b7560`) builds 16-byte
pointer/float-score rows, filters candidates, sorts them, and copies ordered
pointers to an output region. The comparator meaning and output capacity are
unknown (`main_0052.c:36115-36458`).

`aggregate_related_attribute_values` (`0x700185dcb0`) sums selected attribute
values accepted by the recovered ID-group predicates and stores an average or
related aggregate. The container and exact operation remain unresolved
(`main_0170.c:56001-56156`).

`update_global_attribute_records` (`0x70007b03a0`) walks a global collection,
checks status selector `0x13`, and retrieves or adjusts several attribute IDs.
The collection element layout and attribute meanings remain unknown
(`main_0058.c:6975-7079`).


`compute_and_set_attribute_10_from_context` (`0x7001843de8`) resolves an
owner-associated record, computes a clamped value, and writes attribute ID
`0x0a`. The owner fields used as inputs are not semantically named
(`main_0170.c:19081-19282`).

`evaluate_context_attribute_scalar` (`0x70006b8738`) classifies a context
selector/status and obtains direct or nested attribute values before converting
the result. The scalar's domain meaning remains unknown
(`main_0052.c:37473-37546`).

`add_to_context_attribute_clamped` (`0x70006c9230`) adds a supplied delta to a
selected value, clamps it to 0..99, and updates the record when changed
(`main_0053.c:4774-4827`). `set_attribute_record_value_clamped`
(`0x7000431d1c`) performs the related bound-remap/read/clamp/set sequence for
an explicit attribute ID (`main_0032.c:34090-34146`).

`apply_attribute_deltas_to_record` (`0x7001863640`) applies direct deltas via
the shared update helper and writes nested values to 80 u16 slots beginning at
record `+0xa8`. Source modifier semantics remain unknown
(`main_0171.c:2338-2372`).

`get_eligible_context_object` (`0x70006b7e60`) checks a normalized selector and
status, then writes one of the pointer candidates at context `+0x08`, `+0x20`,
or `+0x28` to its output slot (`main_0052.c:36762-36834`).

The output helpers `compute_scaled_direct_context_attribute`
(`0x70006c1a6c`), `compute_scaled_nested_context_attribute`
(`0x70006c1d18`), and `compute_scaled_group_context_attribute`
(`0x70006c1908`) each write a u32 result through an output pointer. The
formulas differ in their access paths; their metric and scale meanings remain
unknown (`main_0052.c:48951-49048,49250-49342`).


`rebuild_attribute_filter_flags` (`0x70007444f0`) walks candidate pointers and
writes a byte flag array while checking context/status conditions. Exact filter
meaning is unknown (`main_0055.c:40884-41007`).

`evaluate_contextual_attribute_scalar` (`0x7000420c0c`) reads several raw
metadata bytes and returns an f32 consumed by its caller; numeric selectors
remain unnamed (`main_0032.c:13105-13184,33184-33201`).

`refresh_nested_attribute_state` (`0x7000c0b8d0`) reads a nested pointer at
`+0x98`, writes two u32 values at `+0x1d8/+0x1dc`, and a byte at `+0x1e1`
(`main_0083.c:47431+`).

`populate_attribute_summary_slots` (`0x70007beee0`) traverses 11 slots and
copies a u16 from nested `+0x9a` to slot `+0x04`, then writes derived floats.
Slot meanings remain unknown (`main_0058.c:24176-24330`).

`find_matching_players` (`0x7000e3d830`) uses player attribute/context helpers
and references the exact empty-search message `No players found matching %s.`
The search record layout and criteria remain unknown (`main_0100.c:31021-31310`).

`refresh_global_attribute_condition_cache` (`0x7000432860`) refreshes global
flags through status and attribute checks. Its cache fields are not named
(`main_0032.c:34885-35000`).

`compute_contextual_attribute_value` (`0x70006b60b4`) uses selector bits at
context `+0x70` and a byte at `+0xa2`; its computed scalar's meaning remains
unknown (`main_0052.c:34569-34800`).
