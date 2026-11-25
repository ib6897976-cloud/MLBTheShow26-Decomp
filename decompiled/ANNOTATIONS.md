# Decompiled symbol annotations

The C files in `main/` and `sdk/` are generated AArch64 recomp wrappers. Their
`f_<address>(Cpu *c)` names and `Cpu *` signatures are host-side dispatch
wrappers, not recovered source function names or prototypes.

`function_symbols.tsv` indexes every discovered function. When an exact
exported `STT_FUNC` symbol exists at that address, `recovered_name` contains
the NSO symbol. Otherwise the function remains address-named and is marked as
unresolved. `elf_symbols.tsv` records the NSO dynamic symbols and their ELF
symbol kinds (`FUNC`, `OBJECT`, and so on); it does not claim C parameter or
structure types.

`function_name_index.tsv` joins every function to its best available readable
name and evidence. `symbol_demangle.tsv` preserves original Itanium C++ names
alongside LLVM-demangled spellings. `type_symbols.tsv` indexes exported RTTI
and vtable symbols; these identify classes but do not recover their fields.

`function_behavior.tsv` contains static evidence for every function: callers,
direct callees, statically visible dispatch targets, counts of lifted loads
and stores, and exact references to printable rodata strings. It is a
navigation and triage index, not a natural-language claim about a function's
purpose.

`arg0_memory_fields.tsv` and `arg0_offset_profile.tsv` index direct constant
offset memory accesses from guest register `x0` plus conservative
single-assignment aliases across both modules. These are triage observations
only; `x0` does not have one global structure type.

`type_catalog.tsv`, `type_methods.tsv`, and `type_class_field_candidates.tsv`
consolidate RTTI/vtable names, exact class method symbols, and candidate
argument-relative field offsets. They do not claim fully recovered layouts.

For each exact exported function, the generated C definition also has a
comment with its original ELF symbol name, kind, and recorded symbol size.
The generated C comments preserve the original spelling; the indexes also
include human-readable C++ demanglings. The decomp contains 135,060 functions;
18,338 unique function definitions have exact exported names available in the
NSO symbol tables. Other internal game functions have no exact names in those
tables.

After regenerating the C with `recomp/gen.py`, reapply the annotations with:

```powershell
python tools/annotate_decomp.py --root .
python tools/demangle_symbols.py --root .
python tools/analyze_functions.py --root .
python tools/analyze_arg0_layouts.py --root .
python tools/build_type_catalog.py --root .
```

ELF symbol kinds and sizes are the only recovered type metadata here. Recovering
original function prototypes, local variable types, and game-specific names for
stripped internal functions requires further analysis and cannot be inferred
reliably from the address alone.


Hand-reviewed semantic names and typed field candidates are maintained in `../tools/data/function_annotations.tsv` and `../tools/data/field_annotations.tsv`. Current subsystem maps: [pitch](PITCH_SUBSYSTEM.md), [swing/contact](SWING_SUBSYSTEM.md), [hit](HIT_SUBSYSTEM.md), [ball](BALL_SUBSYSTEM.md), [stamina](STAMINA_SUBSYSTEM.md), [player attributes](PLAYER_ATTRIBUTES_SUBSYSTEM.md), and [copyable records](RECORD_COPY_SUBSYSTEM.md). These are incremental evidence-backed reconstructions; they do not imply that every stripped function, prototype, or structure is understood.

Candidate source prototypes are maintained in `../tools/data/function_prototype_candidates.tsv` and are kept distinct from the generated `Cpu *` wrapper signature.

To prioritize the next manual pass, run `python tools/rank_annotation_targets.py`.
It ranks unannotated main functions that directly call already-annotated helpers
and writes `tools/data/annotation_target_queue.tsv`. The queue is a triage aid:
shared helper calls suggest useful neighborhoods, but do not prove a candidate
function's purpose or recover its source name.
