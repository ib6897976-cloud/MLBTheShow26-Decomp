# Ghidra symbol and function-start export

`export_nso_ghidra_bundle.py` exports the locally supplied Switch `main` NSO
to an ignored local folder at `temp/ghidra_main_bundle` by default. It writes:

- `image.bin`: decompressed, zero-filled NSO memory image;
- `symbols.tsv`: dynamic symbols, accepted semantic names, and `.eh_frame_hdr`
  function starts;
- `manifest.json`: build ID, image layout, and export counts;
- `apply_symbols.py`: a Ghidra Jython helper to add names and function starts.

Run from any directory with the project's Python environment:

```powershell
python tools/export_nso_ghidra_bundle.py
```

In Ghidra, import `image.bin` as a raw **AArch64 little-endian** binary with
image base `0x7000000000`. Then run `apply_symbols.py` from the Script Manager
and select the generated `symbols.tsv`. The script derives labels from the
accepted annotation table, so unreviewed candidates are not exported as
semantic names.

The image contains decompressed segments and zero-filled gaps/BSS. Dynamic
runtime relocations are **not applied**. Code and unwind function-start hints
are useful for static analysis, but pointer-valued data and cross-references
that rely on absolute relocated pointers may be incomplete. The Ghidra script
is prepared but has not been executed here because Ghidra is not installed in
the environment. No game binary or generated bundle should be committed; the
default output is under the ignored `temp/` directory.
