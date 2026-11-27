# Reading names and types in this decomp

## What is complete

`main/` and `sdk/` contain generated C for all 135,060 guest functions in the
current extracted build: 94,991 in `main` and 40,069 in `sdk`. These are
instruction-level recomp translations. They are not recovered source code:
each `f_<address>(Cpu *c)` is a host wrapper that reads and writes guest CPU
state and dispatches guest addresses.

## Name indexes

- `function_name_index.tsv` has one row per generated function. It provides the
  address, generated name, best available readable name, name evidence, symbol
  size, wrapper signature, semantic annotation confidence/evidence, and any
  evidence-backed candidate source prototype. Unknown prototypes remain marked
  as unknown; the host `Cpu *` wrapper is not presented as the source type.
- `function_symbols.tsv` preserves the original exact exported symbol when
  present. An empty `recovered_name` means the function has no exact name in
  the NSO symbol table; `f_<address>` is then only a stable generated label.
- `symbol_demangle.tsv` maps exported Itanium C++ symbol spellings to the
  output of the bundled LLVM demangler. For most C++ functions, the encoding
  contains parameter types and the method/class name. C++ ABI names generally
  omit the return type, so a demangled spelling is not automatically a full C
  prototype.
- `function_behavior.tsv` is the static call and memory-operation index. Its
  direct callee lists now use readable names where exact exports exist and
  address names elsewhere. Calls through runtime dispatch may be incomplete.
  Static string candidates include adjacent page-plus-offset address formation.
  Confirm the resolved pointer and the consuming instruction before using a
  string to infer behavior.
- `command_callback_candidates.tsv` maps named main NSO callback records
  to generated function entry points. Each record pairs a relocated rodata
  command name with a relocated function pointer and a zero third word. It
  includes the two relocation sites and flags neighboring records of the same
  shape. Multiple callbacks can share a command and one callback can have
  multiple registrations.
- `tools/data/callback_target_queue.tsv` ranks unannotated handlers backed
  by adjacent command-name and function-pointer relocation records. It includes
  every registered command for an address plus indexed caller, callee, load,
  store, and string observations. Rebuild it as part of
  `refresh_annotation_indexes.py`.
- `tools/data/function_prototype_candidates.tsv` records ABI-level source prototype
  candidates, separately from recomp wrapper signatures.
- `tools/data/function_annotations.tsv` is the evidence-reviewed semantic layer.
  It currently contains 13470 named current-build routines and 177 candidate
  source prototypes across pitch/ball, stamina, swing/contact, hit/timing,
  stadium lighting, broadcast moments, player attributes, nested delta operations,
  composite record copying, ranked-candidate evaluation, record parsing, context predicates, ranked output rows, and math. Command callbacks now cover parts of league trade and lineup management, mission progress, and arena inventory and roster operations. Every
  annotation carries evidence and confidence; this is still a small sample of
  the 135,060-function program, not a full source recovery.
  `tailcall_forward_to_*`, `guest_state_noop_stub`, and
  `return_immediate_*` are synthetic labels from deterministic fast lanes.
  Tail-call labels cover exact lifted bodies that forward to an already named
  function or, with an `address_<guest-address>` suffix, to an unnamed target.
  The other labels cover wrappers that return without guest-state operations
  or set `x0` to one literal and return. The batches are mechanically checked
  row by row and manually spot-checked. These labels describe observed wrapper
  behavior, not recovered original symbols, and infer no parameter or field
  types.
  `tools/data/field_annotations.tsv` contains 885 typed candidate-field rows.
  Partial layouts are in `recovered/pitch_types.h`,
  `recovered/pitch_fatigue_types.h`, `recovered/swing_types.h`,
  `recovered/hit_types.h`, `recovered/stadium_lighting_types.h`,
  `recovered/broadcast_moments_types.h`, `recovered/player_attributes_types.h`,
  `recovered/copyable_record_types.h`, `recovered/generic_buffer_owner_types.h`,
  `recovered/stride18_record_types.h`, `recovered/context_status_types.h`,
  `recovered/category_candidate_types.h`,
  `recovered/extended_attribute_context_types.h`,
  `recovered/player_attribute_group_metric_types.h`, and
  `recovered/record_field_descriptor_types.h`, and `recovered/ranked_stat_row_types.h`, and `recovered/player_attribute_component_owner_types.h`, `recovered/attribute_slot_reference_types.h`, `recovered/tagged_attribute_value_types.h`, and `recovered/mutable_text_buffer_types.h`, `recovered/attribute_delta_owner_types.h`, and `recovered/attribute_derived_record_types.h`, and `recovered/attribute_metrics_owner_types.h`, and `recovered/ranked_metric_cache_types.h`, and `recovered/player_attribute_search_result_types.h`, and `recovered/attribute_record_summary_types.h`, `recovered/attribute_adjustment_descriptor_types.h`, and `recovered/contextual_attribute_rule_types.h`, `recovered/attribute_derived_buffer_types.h`, and `recovered/attribute_rule_descriptor_types.h`; unknown regions remain explicitly
  reserved. The generated C remains untouched.

See [PITCH_SUBSYSTEM.md](PITCH_SUBSYSTEM.md) and
[SWING_SUBSYSTEM.md](SWING_SUBSYSTEM.md), and
[HIT_SUBSYSTEM.md](HIT_SUBSYSTEM.md), [BALL_SUBSYSTEM.md](BALL_SUBSYSTEM.md), [STAMINA_SUBSYSTEM.md](STAMINA_SUBSYSTEM.md), [RANKING_SUBSYSTEM.md](RANKING_SUBSYSTEM.md),
and [MATH_HELPERS.md](MATH_HELPERS.md), [VERSION_CROSSWALK.md](VERSION_CROSSWALK.md) for current call paths, candidate
fields, version-matched addresses, and unresolved behavior.

See [MEMORY_LAYOUT_INDEX.md](MEMORY_LAYOUT_INDEX.md) for whole-program
first-argument field-access evidence and its limits.

See [STADIUM_LIGHTING_SUBSYSTEM.md](STADIUM_LIGHTING_SUBSYSTEM.md) and
[BROADCAST_LEADERS_SUBSYSTEM.md](BROADCAST_LEADERS_SUBSYSTEM.md) for the
current-build lighting refresh and broadcast leader-list paths.

See [TYPE_CATALOG.md](TYPE_CATALOG.md) for deduplicated RTTI/vtable names,
class-to-method associations, and candidate SDK field offsets.

## Type evidence

`type_symbols.tsv` indexes 2,814 exported RTTI and virtual-table symbols. These
provide exact class/type names for objects represented in the ELF symbol table;
they do not define member offsets, field types, inheritance layout, or the
types of stripped functions' locals and parameters. The current `main` module's
RTTI/vtable entries are C++ standard-library stream types. The larger Nintendo
SDK RTTI set is in `sdk` and mostly describes SDK interfaces and implementation
classes. There is no broad game-class RTTI database in `main` to recover the
game's actor and gameplay record layouts automatically.

The generated C wrapper type `Cpu *` is not a recovered game parameter type.
Where ELF has only an unmangled C export, its name does not establish a source
prototype. For address-only internal functions, neither name nor source
prototype is present in the symbol table.

## Current coverage snapshot

The current indexes contain 135,060 functions. Of those, 18,338 have exact
exported ELF function names; 14,640 of those names are readable C++ demanglings.
The remaining 116,722 functions lack exact exported names. The semantic layer
records reviewed names separately. The symbol index contains 19,579 demangled
ELF symbols, including RTTI and vtable entries.

## Rebuild the indexes

After regenerating `decompiled/` with `recomp/gen.py`, run:

```powershell
python tools/annotate_decomp.py --root .
python tools/demangle_symbols.py --root .
python tools/analyze_functions.py --root .
python tools/index_command_callbacks.py
python tools/analyze_arg0_layouts.py --root .
python tools/build_type_catalog.py --root .
```

## Iterating semantic annotation batches

Parallel workers stage one JSONL file each under `tools/data/staging/`, so they
do not write to the shared TSV indexes at the same time. Merge finished batches
and refresh the semantic name/call indexes with:

```powershell
python tools/merge_staged_annotations.py --files <reviewed-batch-filename>
python tools/refresh_annotation_indexes.py
```

The first full behavior scan stores raw callee addresses in
`function_behavior.tsv`. Later annotation waves refresh readable callee names
from those cached addresses and rerank the queue without rescanning all generated
functions. Already reviewed staged functions are skipped, including cases where
the evidence was too weak to justify a semantic rename.

The generated C files are not edited by these index tools. `demangle_symbols.py`
uses the bundled `llvm/bin/clang.exe` and `llvm/bin/llvm-nm.exe`; it maps exact
ELF spellings to demangled output and refuses to write if the mapping cannot be
verified.

## How to turn evidence into semantic names

For each subsystem, start from the call graph, callback registrations, and resolved strings, inspect the
generated guest instructions, then confirm candidate arguments and record
fields against runtime observations or known binary assets. Give each proposed
name a source and confidence level. Promote a field from `unknown_0xNNN` only
after a cross-check; do not treat a convenient offset or a matching constant
as proof of a full structure layout. This process must be repeated per build
version because addresses and layouts can change.
