# Copyable record and optional payload

This map describes a generic record-copy pattern recovered from call sites in
several parts of the main module. It does not establish the complete source
class or the semantic names of the copied fields.

| Address | Working name | Observed behavior |
|---|---|---|
| `0x700181fd80` | `decode_composite_record_descriptor_entries` | Walks 0x20-byte descriptors, validates paired halfwords against a word, and routes selector/value processing. |
| `0x700181ff40` | `make_typed_record_field_value_node` | Resolves one of ten selectors to a width-specific value at an observed composite-record offset. |
| `0x700183bfe4` | `record_copy_assign_with_optional_payload` | Copies bytes `+0x00..+0x4d` from source to destination, including one overlapping unaligned qword, then copies or resets an optional payload reached through `+0x50`. Returns the original destination pointer in `x0`. |
| `0x70017f4954` | `nested_payload_default_reset` | Writes the observed default byte/word values to the first 30 bytes of a nested payload. |
| `0x70017f4f00` | `record_default_zero_initialize_fields` | Clears selected qword regions and sets a 32-bit all-ones sentinel at `+0x48` and a 16-bit all-ones value at `+0x4c`. |
| `0x70017f4f24` | `record_seed_nonzero_default_fields` | Writes the state word at `+0x48`, a 16-bit value loaded from main rodata at `+0x4c`, seeds packed values at `+0x18..+0x27`, and clears selected qword regions. |
| `0x700183c070` | `record_initialize_empty_and_clear_payload` | Applies the zero/sentinel initializer, then clears the optional payload pointer at `+0x50`. |
| `0x700183c094` | `record_initialize_defaults_and_reset_payload` | Applies the nonzero-default initializer and, if `+0x50` is nonnull, resets the pointed-to payload. |
| `0x70017f4938` | `nested_payload_zero_state_initialize` | Sets payload `+0` and `+4` to all ones and clears the remaining observed 24 bytes. |
| `0x700183b4bc` | `nested_payload_zero_state_initialize_forwarder` | Tail-calls `nested_payload_zero_state_initialize`. |
| `0x70017db7ec` | `byte_default_table_zero_with_tail_sentinel` | Zeroes the first `0xf0` bytes of a table block and stores `0xff` at `+0xf0`. |
| `0x70017c64d0` | `byte_default_table_initialize_from_global_defaults` | Resets a `0xf1`-byte block, fills 160 entries at `+0x50..+0xef` from the low bytes of a global 16-bit table when enabled or with `0xff` otherwise, then writes marker bytes. |
| `0x7001820284` | `composite_record_initialize_zero_variant` | Initializes the record prefix, nested payload at `+0x58`, table block at `+0x78`, subobject at `+0x16c`, and observed trailing fields. |
| `0x70018202f0` | `composite_record_initialize_default_variant` | Initializes the seeded record prefix, points `+0x50` at inline payload `+0x58`, resets that payload, initializes the table at `+0x78`, and writes alternate trailing defaults. |
| `0x70017d4034` | `zero_56_byte_subobject` | Clears bytes `+0x00..+0x55` using overlapping qword stores. |
| `0x70017d4050` | `zero_56_byte_subobject` | Performs the same observed 0x56-byte clear as `0x70017d4034`. |
| `0x70018200f0` | `player_data_record_decode` | Looks up the `D_PLAYER_ATTS`, `D_PLAYER_APP`, and `D_PLAYER_ACC` sections and dispatches them to record offsets `+0`, `+0x78`, and `+0x16c`; accumulates the helper return values. |
| `0x700183c160` | `d_player_atts_section_decode` | Handles the D_PLAYER_ATTS section using the composite record and its nested payload pointer. |
| `0x700183c270` | `d_pitcher_atts_payload_merge_into_parent` | Merges nested payload bytes into the parent record and writes fixed defaults. |
| `0x700183c524` | `record_reset_sentinel_pair_at_48` | Stores an all-ones 32-bit word and halfword at `+0x48` and `+0x4c`. |
| `0x700183c534` | `record_write_indexed_byte_at_48` | Writes one byte at `+0x48+index` for indices 0 through 5. |
| `0x70017c3138` | `d_player_app_section_decode_dispatch` | Tail-calls a D_PLAYER_APP section wrapper. |
| `0x70017dddbc` | `d_player_app_section_decode_thunk` | Tail-calls `d_player_app_section_decode`. |
| `0x70017db3d0` | `d_player_app_section_decode` | Processes the D_PLAYER_APP section payload. |
| `0x70017c14dc` | `d_player_acc_section_decode_dispatch` | Tail-calls a D_PLAYER_ACC section wrapper. |
| `0x70017d7154` | `d_player_acc_section_decode_thunk` | Tail-calls `d_player_acc_section_decode`. |
| `0x70017d3d30` | `d_player_acc_section_decode` | Processes the D_PLAYER_ACC section payload. |
| `0x70017f4934` | `d_pitcher_atts_section_decode_thunk` | Tail-calls the D_PITCHER_ATTS payload decoder. |
| `0x70017f4680` | `d_pitcher_atts_section_decode` | Processes D_PITCHER_ATTS entries into the 30-byte nested payload and returns the accumulated 32-bit result. |

## Player section entry dispatch

The `D_PLAYER_APP` loop in `d_player_app_section_decode` calls
`d_player_app_entry_value_dispatch` (`0x70017db590`) for each entry. It resolves
a 32-bit key through the 34-entry table at `0x7002286e80`, dispatches with
selector bytes at `0x7001ddd324`, extracts key-specific byte or signed-byte
values, and forwards them to generic decode helpers. The parallel
`d_player_acc_entry_value_dispatch` (`0x70017d3ef0`) uses a 15-entry table at
`0x7002286e70` and selector bytes at `0x7001ddd2e8`. The parent loops address
entries at `0x20`-byte stride; this is observed parser stride evidence, not a
complete source-level entry structure. Key meanings and helper prototypes remain
unresolved.

Both paths also call `buffer_owner_value_030_adjust` (`0x7000df1d00`). It checks
owner `+0x20`; if nonnull, it adds the signed 32-bit delta to the 64-bit value
at `+0x30`, stores it, and returns the delta. The generic candidate layout in
[`recovered/generic_buffer_owner_types.h`](recovered/generic_buffer_owner_types.h)
records only those observed offsets; the value's units and owner class are
unknown.

## Reusable state and byte accessors

`record_reset_sentinel_pair_at_48` stores a 32-bit all-ones value at base `+0x48` and a 16-bit all-ones value at `+0x4c`. `record_write_indexed_byte_at_48` accepts a base, index, and byte; it writes to `base + 0x48 + index` only when the low byte of the index is in the range 0 through 5. Multiple decode paths call the indexed writer with these six indices and parsed byte values. These helpers establish the access widths and bounds, but do not establish shared application-level field names for all callers.

## Copy routine

`record_copy_assign_with_optional_payload(destination, source)` copies qwords
at offsets `0`, `8`, `16`, `24`, `32`, `40`, `48`, `56`, and `64`, plus an
unaligned qword at decimal offset `70` (`0x46`). The final qword overlaps the
previous copy at bytes `+0x46..+0x47`; together these stores cover
`+0x00..+0x4d`. Bytes `+0x4e..+0x4f` are not written. It then reads the
existing nested-payload pointer from destination `+0x50`:

The initializer variants also provide type-width evidence for two fields
inside the copied prefix: a 32-bit state word at `+0x48` and a 16-bit state
value at `+0x4c`. The zero initializer sets both to all ones; the alternate
initializer writes `0xff060200` to the word and loads the halfword from
main-rodata address `0x7001ddd4c8`. Their application-level meanings remain
unknown. The copyable-record candidate layout preserves these as typed fields.

The alternate initializer also reads and rewrites a 64-bit packed value at
`+0x18`, preserving the top two bits of each 32-bit lane and setting the
remaining bits to the observed baseline pattern `0x2108421021084210`. It
preserves the top two bits of the 32-bit word at `+0x20` while setting its
lower bits to the observed baseline `0x01084210`, then writes `0x00002132` at
`+0x24`. These widths and bit operations are observed; the meanings of the
packed values are not recovered. The candidate layout records the widths
without assigning application-level names.

| Destination `+0x50` | Source `+0x50` | Action |
|---|---|---|
| null | any | Leave payload storage untouched. |
| nonnull | nonnull | Copy qwords from source payload offsets `0`, `8`, `16`, and `22` (decimal) into the destination payload. This covers bytes `0..29`; the final qword overlaps bytes `22..23` already covered by the qword at offset 16. |
| nonnull | null | Call `nested_payload_default_reset` on the destination payload. |

The routine does not copy or replace the pointer at `+0x50`; it operates on
the destination's already-present nested object. `CopyAssignableRecordCandidate`
and `NestedPayloadPrefixCandidate` in
[`recovered/copyable_record_types.h`](recovered/copyable_record_types.h) model
only this observed extent. The fields at nested payload `+0` and `+4` are
typed from direct 32-bit and 16-bit stores; their application-level meanings
and the payload's source-level identity remain unknown.

## Nested payload merge into the parent record

After the D_PLAYER_ATTS parser path, `f_700183c270` reads the optional payload pointer at record `+0x50`. If present, it examines payload bytes `+0x06..+0x1d` and writes corresponding bytes to the parent at `+0x28..+0x41`; a zero payload byte leaves the existing parent byte in place. It then writes the fixed word `0x050f192d` at `+0x42` and halfword `0x0505` at `+0x46`. Finally it examines payload bytes `+0x00..+0x05` and writes qualifying nonnegative signed-byte values into parent `+0x48..+0x4d`. This establishes the byte/word widths and merge relationship; application meanings of the fields remain unknown. The candidate structure and field index split the formerly unknown `+0x28..+0x47` region according to these writes.

## Nested payload reset

`nested_payload_default_reset` stores the 32-bit constant `0xff060200` at
payload `+0`, clears an eight-byte region at `+6`, clears qwords at `+14` and
`+22`, and writes a 16-bit value loaded from main-rodata `0x7001ddd4c8` at
`+4`. `nested_payload_zero_state_initialize` instead writes `0xffffffff` at
`+0` and `+4`, then clears the same regions starting at `+6`. These writes
cover bytes `0..29`. The typed prefix widths are supported by the stores;
meanings of the two state values are not known.

One enclosing constructor, `f_70018202f0`, stores its own address plus `0x58`
into the record's pointer at `+0x50`, then initializes the payload at `+0x58`.
This proves the pointer can refer to an inline payload in that owner layout;
other callers and owners may supply a different payload address.

Within `D_PLAYER_ATTS`, `f_700183c160` looks up the exact NSO key
`D_PITCHER_ATTS` and decodes it through `f_70017f4934` to `f_70017f4680`,
using the payload pointer at `+0x50`. In the composite initializer variant,
that pointer is set to inline storage at `+0x58`, whose observed prefix is 30
bytes. The code therefore ties this pointer and inline storage to the nested
`D_PITCHER_ATTS` section in this player-record path.

Evidence: generated routines `f_700183bfe4` in `main_0170.c` and
`f_70017f4954` in `main_0168.c`; callers include `0x700043154c`,
`0x7000658524`, `0x70006682d4`, `0x7000781688`, and `0x7000ceb354`.

## Byte default table block

`byte_default_table_initialize_from_global_defaults` operates on a block of
at least `0xf1` bytes. It first calls `byte_default_table_zero_with_tail_sentinel`,
which clears bytes `+0x00..+0xef` and writes `0xff` at `+0xf0`. When the
global enable byte at `0x700464ab98` is set, it loads 160 halfwords beginning
at `0x700464ac9c`, stores each low byte at block `+0x50+i`, and discards each
high byte. When disabled, it fills those same 160 bytes with `0xff`. It then
sets bytes `+0x12..+0x1c` to `0x80` and byte `+0x23` to zero. The table entries'
source-level labels and meanings are unknown. `ByteDefaultTableCandidate`
records the observed extent and byte ranges.

The constructor `f_7001820284` calls this initializer on its object at
`+0x78`, after initializing the `+0x58` payload and before initializing a
separate subobject at `+0x16c`.

## Enclosing composite layout

The paired initializers `f_7001820284` and `f_70018202f0` establish a minimum
observed object extent of `0x1fb` bytes. Both use the same leading record
prefix, initialize a payload at `+0x58`, initialize the byte table at `+0x78`,
and clear a `0x56`-byte subobject at `+0x16c`. They leave the two-byte gaps
`+0x76..+0x77`, `+0x169..+0x16b`, and `+0x1c2..+0x1c3` untouched by these
helpers. Their trailing initialization differs: the zero variant clears
`+0x1c4..+0x1d3`, writes `0xffff0000` at `+0x1d4`, and clears through `+0x1fa`
with an overlapping final dword; the default variant writes `0xffff000000000000`
at `+0x1d0`, clears `+0x1d8..+0x1ef`, and clears `+0x1f0..+0x1fa`. This
evidence supports the byte ranges and subobject offsets in
`CompositeRecordCandidate`, but not the complete source class or meanings of
the trailing state bytes.

The copy routine `f_700181fadc` adds evidence for an assignment path: it resolves
pointer-like source fields at `+0x40` and `+0x48`, copies a `0xf1`-byte table
into destination `+0x78`, delegates the optional nested payload copy, and copies
16-byte blocks from source `+0x50`/`+0x60` to destination `+0x1d8`/`+0x1e8`.
Those trailing blocks are typed as qword arrays for the observed copy width only;
their meanings remain unknown.

The original main NSO's read-only strings provide section names for three
subobjects: `f_70018200f0` uses key `D_PLAYER_ATTS` with the record base and
dispatches through `f_700183c160`; it uses `D_PLAYER_APP` with the block at
`+0x78` and `D_PLAYER_ACC` with the block at `+0x16c`. The candidate field
names now preserve these exact serialized keys. They identify the sections,
but do not prove the full source class name or every field's game-level
meaning. `player_data_record_decode` first calls `f_700181fd80`, then adds the
three section-handler results and returns that 32-bit sum.

The D_PLAYER_APP chain passes through `f_70017c3138` and `f_70017dddbc` to
`f_70017db3d0`; the D_PLAYER_ACC chain passes through `f_70017c14dc` and
`f_70017d7154` to `f_70017d3d30`. Both leaf routines return 32-bit accumulated
results from their entry-processing loops. Generic argument types beyond the
destination, source, and observed count/option registers remain unresolved.


## Composite descriptor records

`decode_composite_record_descriptor_entries` (`0x700181fd80`) is called from
`player_data_record_decode`. In its validation path it walks 0x20-byte descriptors,
reads halfwords at entry `+0x14` and `+0x16`, and compares their product with the
word at `+0x18`. `make_typed_record_field_value_node` (`0x700181ff40`) resolves
a selector through a ten-entry table and reads the corresponding typed value
from the trailing composite record. Selector-to-game-field meanings are unknown.
The field widths and offsets are captured in `CompositeRecordCandidate`; the
descriptor entry view is in `record_field_descriptor_types.h`. Evidence is in
`main_0169.c` at both functions and the caller near `f_70018200f0`.

`build_record_attribute_value_summary` (`0x7000497690`) initializes temporary
record subobjects from a shared default, transfers 59 indexed byte-valued
entries from the input, validates the temporary aggregate, and returns a
32-bit conversion derived from a float helper. Its temporary offsets and
domain meaning remain unresolved; they do not establish a persistent record
layout. Evidence is in `main_0034.c:45348-45470` and its caller at `:45479-45496`.

`validate_tagged_attribute_value` (`0x700049ac08`) handles one tag branch of a
tagged attribute-value parser. It gates signed direct/nested selectors using
known ID-group and attribute predicates, delegates accepted values to parsing
helpers, and clears or terminates the caller's mutable text buffer. The code
supports raw widths at offsets `+0x00`, `+0x02`, `+0x03`, `+0x1c..+0x20` but
does not establish source field names or exact output formatting. Evidence is
in `main_0034.c:48900-48955,49287-49469`.

`rebuild_composite_record_from_tagged_value` (`0x70007c3840`) handles tagged
kind `0x3d`, reads a composite object pointer from the tagged value, prepares
a temporary composite, copy-assigns it into the source object, and writes a
16-bit result at `+0x1d6`. Those offsets overlap already-observed typed members;
no new member meaning is inferred. Evidence: `main_0058.c:29703-29793`.

`calculate_attribute_record_derived_value` (`0x7000497450`) builds a temporary
aggregate from a default record and 59 indexed input values, then returns a
32-bit conversion of a float evaluator result. Two callers store this result at
`+0xd8` and `+0x2d0`, with companion results at `+0xdc` and `+0x2d4`; the
owner types and metric labels are unknown. Evidence: `main_0034.c:45177-45267`,
callers in `main_0082.c:17501-17519,20990-21008`.

`recompute_attribute_record_metrics` (`0x7000bc7fd8`) rebuilds a temporary
attribute record, calls `calculate_attribute_record_derived_value`, and stores
32-bit results at owner `+0x2d0` and `+0x2d4`. These offsets are typed by their
stores and helper return values; statistic meanings and the owner type are
unknown. Evidence: `main_0082.c:20962-21017`.

`recompute_attribute_record_summary_pair` (`0x7000bc50ec`) is a related
output-building path: it initializes a temporary 59-entry record and writes
results from the derived-value and summary helpers at output `+0xd8/+0xdc`. The
slots are 32-bit by the observed stores; their semantic labels and owner type
remain unknown. Evidence: `main_0082.c:17473-17521`.


`initialize_composite_record` (`0x7000a957c8`) initializes child regions at
`+0x1d8`, `+0x288`, `+0x2e0`, `+0x3d8`, and `+0x430`, then clears fields through
at least `+0x640`. The caller allocates `0x648` bytes. The subobject types and
domain meaning are still unresolved (`main_0075.c:36013-36094`; caller
`:37162-37172`).


## Additional opaque record initializers

The following functions initialize record-like bundles whose semantic types
are not recovered:

- `initialize_record_bundle_06922c8` (`0x70006922c8`) initializes nested
  regions and writes an interior link and sentinel values
  (`main_0050.c:42595-42699`).
- `initialize_record_bundle_a9aa38` (`0x7000a9aa38`) initializes nested
  regions and links in a 0x608-byte caller allocation
  (`main_0075.c:42113-42198`).
- `initialize_record_bundle_176941c` (`0x700176941c`) initializes nested
  regions and sets bit 0x48 in a halfword at +0x97c
  (`main_0165.c:8979-9064`).
- `initialize_record_bundle_176e418` (`0x700176e418`) initializes nested
  regions and sets observed byte, integer and float constants in a 0xbd8-byte
  caller allocation (`main_0165.c:14795-14883`).

`find_candidate_record_for_index` (`0x7000709e30`) looks up a strided table,
builds and sorts 16-byte pointer/score rows, applies attribute and packed-field
filters, then writes a matching pointer through an output argument. Its
candidate domain remains unknown (`main_0054.c:26176-26346`).


`initialize_record_bundle_0c0a5a8` (`0x7000c0a5a8`) initializes nested
regions and an indexed helper table inside a 0x5d0-byte caller allocation
(`main_0083.c:45924-46104`).

`construct_1776e78_owned_resource` (`0x7001776e78`) initializes child records,
constructs an owned 0x3230-byte subobject, and installs interior links. The
resource's type and role remain unknown (`main_0165.c:24892-24958`).

`initialize_repeated_record_17daff0` (`0x70017daff0`) initializes records
visited in a 0x340-byte-stride loop; the record's semantic type is unknown
(`main_0167.c:39083-39141`; caller `main_0169.c:44515-44535`).


`find_candidate_record_for_tag` (`0x700070a080`) looks up a strided table,
filters by a signed-byte tag and attribute score, sorts pointer/float rows, and
returns a matching pointer (`main_0054.c:26349-26530`).

`build_sorted_attribute_record_groups` (`0x7000673e70`) builds and sorts
pointer/float rows for five groups of up to 0x14 entries, then copies results
to global storage (`main_0050.c:7126-7660`).

`build_attribute_comparison_table` (`0x700072e860`) builds and sorts several
attribute-derived pointer/score rows and returns a success value. Its precise
comparison task is unresolved (`main_0055.c:15441-16461`).

`initialize_and_configure_17699f8_record` (`0x70017699f8`) initializes a
repeated 0x420-stride record, then updates shared count/handle state. The
record's domain remains unknown (`main_0165.c:9415-9530`).

`process_record_text_metadata` (`0x7000bfa2f0`) scans embedded metadata and
nested subrecords before sorting/copying results; the byte format is unresolved
(`main_0083.c:26853-27183`).

`collect_and_rank_attribute_matches` (`0x700079ed40`) scores selected
candidate pointers into 16-byte rows and sorts them (`main_0057.c:39934-40449`).
