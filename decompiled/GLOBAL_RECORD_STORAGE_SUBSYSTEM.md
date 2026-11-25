# Global record storage initialization

`initialize_global_record_storage_block` (`0x7000665d70`) initializes a set of
repeated global regions through existing empty-record, payload, table, and
zero-fill helpers. The forwarding wrapper supplies base `0x7003a24420`. The
observed repeated views are:

| Owner-relative base | Stride | Count | Initialization behavior |
|---|---:|---:|---|
| `+0x30ac8` | `0x138` | 200 | record/payload initialization |
| `+0x39448` | `0xb0` | 200 | record initialization |
| `+0x3d908` | `0x58` | 200 | record initialization |
| `+0x497a8` | `0xf4` | 200 | two initializers per element |
| `+0x4fc68` | `0x58` | 200 | record initialization |
| `+0x503d8` | `0x1e` | 200 | compact record initialization |

These address ranges overlap when treated as linear arrays, so they are recorded
as initializer views rather than a disjoint parent-structure layout. Their
member names and higher-level owner type remain unknown. Evidence is in
`main_0049.c:44074-44233`; the forwarding call is at `:46240-46245`.


`initialize_global_3a7e000_subobjects` (`0x70006920d0`) initializes six fixed
global subobjects rooted at `0x7003a7e100`; their owner type remains unknown
(`main_0050.c:42429-42462`).

`ensure_global_attribute_registry_and_register_ids` (`0x7000692550`) lazily
creates a singleton with `initialize_record_bundle_06922c8`, publishes it, and
registers linked records for numeric codes. The meanings of those codes remain
unresolved (`main_0051.c:16-400`).
