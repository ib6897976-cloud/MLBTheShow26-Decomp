# Staged annotation batches

Workers write one JSON object per line to their own batch file. Do not edit the shared annotation TSVs from parallel workers; the parent merges staged rows after checking evidence.

Each object uses this shape:

```json
{"module":"main","address":"0x...","semantic_name":"...","confidence":"low|medium|high","evidence":"Exact behavior and source file:line references.","candidate_prototype":"optional logical candidate","prototype_confidence":"optional confidence","prototype_evidence":"optional evidence","fields":[{"structure_name":"...","structure_confidence":"candidate","base_description":"...","offset":"0x...","size_bytes":4,"field_name":"...","ctype":"uint32_t","semantic_description":"...","confidence":"medium","evidence":"file:line evidence"}]}
```

Use generated names or an empty semantic name when evidence does not support a rename. Only include field rows when access widths and offsets are directly visible. The main TSV files are updated by a single sequential merge after all workers finish.

Cross-checkers write one review object per examined proposal to a separate
`*_review.jsonl` file. Use this shape:

```json
{"address":"0x...","source_file":"player_attributes_wave10.jsonl","verdict":"confirmed|corrected|reject_name|needs_more_evidence","reviewed_name":"optional corrected name","notes":"What was checked and what evidence supports the verdict.","source_lines":["decompiled/main/main_0000.c:123-145"]}
```

Review the function body and at least one caller where available. Check every
claimed offset/width against the actual loads/stores. Review files are advisory;
the parent applies corrections before merging the proposals.


Treat string matches in the ranked queue as leads. For a semantic claim,
resolve the full guest address against NSO rodata and trace how the body uses
it. Earlier queue versions could mistake an AArch64 page base for a string.
For indirect command callbacks, `decompiled/command_callback_candidates.tsv`
gives the name and callback relocation sites. Confirm that the record and body
support the proposed name. `callback_target_queue.tsv` puts functions with an
adjacent named command/function record first. Those exact registrations identify
the dispatch association. Read the body to confirm what the handler does,
especially where one command has multiple registered functions. Several older
labels were corrected after wave 22. Earlier rows that rely on cached string
evidence remain candidates for audit.

## Deterministic fast lanes

`tools/build_tailcall_fastlane.py` stages a narrow class of stripped functions
only when the entire lifted body is `FN_ENTER` plus one `musttail` return to an
single function. By default, the target must have an accepted semantic label or
readable exact ELF name. `--include-unknown-targets` also emits
`tailcall_forward_to_address_<guest-address>` when the destination has no
recovered name. All tail-call labels describe exact forwarding behavior, not
original source symbols, and make no source-prototype or field claims. Before
merge, run an independent all-row mechanical validator and manually inspect a
random sample; preserve the validator report with the batch. Do not broaden the
classifier to functions with any extra operations without a separate review.

Wave 68's address-inclusive batch is checked by
`tools/validate_unknown_tailcall_fastlane.py`; it verifies each body and target
and checks a 50-function sample. Its independent audit is stored beside the
batch in `wave68_independent_review.md`.

`tools/build_trivial_fastlane.py` similarly stages only exact no-op wrappers
(`FN_ENTER; return;`) and literal-return wrappers (`FN_ENTER`, set `x0` to one
immediate, store it, return). It emits `guest_state_noop_stub` or
`return_immediate_<literal>`, never a source prototype or field. Independently
validate every generated row and manually inspect a random sample before merge.
The profiling hook in `FN_ENTER` is host instrumentation, not guest-state
behavior.
