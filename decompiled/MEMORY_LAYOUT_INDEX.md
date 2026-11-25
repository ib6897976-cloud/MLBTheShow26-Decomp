# Whole-program memory access index

`arg0_memory_fields.tsv` records every explicit constant-offset read or write
of the incoming `x0` value found in generated `main` and `sdk` functions. It
also includes callee-saved registers assigned exactly once from `x0`, marked
as candidate aliases. Each row records the base register, provenance,
function/offset, read/write counts, and access widths.
`arg0_offset_profile.tsv` aggregates observations by module, provenance, and
offset.

The current scan covers all 135,060 generated functions and produced 175,430
function/offset rows and 3,875 module/provenance/offset profiles. This is a navigation
aid for type recovery, not a structure database: `x0` has no single global
type, and this pass does not follow indexed addresses or pointers loaded from
fields. Alias recovery is deliberately conservative and only accepts a
callee-saved register assigned once from `x0`. High frequency alone is not
evidence that two functions share a structure.

Use a profile row to find candidates, then inspect the listed functions and
their callers together. Confirm the base pointer's role, access width, and
value behavior before assigning a field name or C type. Preserve an unknown
offset as reserved storage until there is independent evidence.

Regenerate after decomp changes with:

```powershell
python tools/analyze_arg0_layouts.py --root .
```
