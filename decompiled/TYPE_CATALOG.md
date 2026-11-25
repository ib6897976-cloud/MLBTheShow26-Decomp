# Exported C++ type catalog

`type_catalog.tsv` consolidates the exported RTTI and vtable symbols into
1,198 unique module/type names: 14 in `main` and 1,184 in `sdk`. The `main`
entries are standard-library stream classes and construction-vtable variants;
the game module does not expose a broad RTTI inventory for its own gameplay
classes. Most recovered names belong to Nintendo SDK and Android support code.

`type_methods.tsv` associates 2,124 exact exported C++ methods with 264 of
those type names (2,108 SDK methods and 16 main-module methods). The association
uses the longest exact demangled class-name prefix and skips nested-class
methods when their class has no RTTI entry; each row retains its original ELF
symbol and guest address.

`type_class_field_candidates.tsv` joins these methods to the whole-program
memory index and lists 1,269 observed argument-relative offsets across 207
types. These are candidate object fields: the ABI puts `this` in `x0` for
ordinary instance methods, but static methods also exist and the index does
not prove receiver status or field meaning. Access widths and repetition help
prioritize inspection; they do not establish a complete structure layout.

Use the type/method index to inspect one class at a time. Confirm each member
through the corresponding method behavior, vtable layout, or runtime evidence
before naming it. No member offsets are promoted automatically.

Regenerate the catalog after rebuilding the symbol and memory indexes with:

```powershell
python tools/build_type_catalog.py --root .
```
