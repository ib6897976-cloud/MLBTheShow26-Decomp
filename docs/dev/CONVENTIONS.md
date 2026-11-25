# Analysis conventions

## Confidence and names

- Keep the generated address-based function name when behavior is unclear.
- Prefer a narrow verb-and-object name that matches observed behavior.
- Use a confidence level consistent with the evidence and state the reason in
  the annotation evidence.
- A matching string is a clue. Confirm its use in the function body.
- For stripped callbacks, inspect the registration record and callback body;
  an absent direct caller is not evidence that the routine is unused.

## Structure fields

For each candidate field, record the containing base, byte offset, access
width, candidate type, meaning, and the code that supports the interpretation.
Keep raw storage facts distinct from semantic guesses. Do not silently combine
same-offset observations from different bases or builds.

## Build-specific evidence

Function addresses and data layouts belong to a particular game build. Note the
module and source file/line range, and use exact guest string addresses when
strings support the conclusion. Keep observations from older builds clearly
separated from current-build evidence.

## Shared annotation workflow

Follow [the staging workflow](../../tools/data/staging/README.md). Keep worker
outputs isolated, review proposals before merging, merge serially, and refresh
the derived indexes after accepted changes. Never use row counts from raw
physical TSV lines when quoted evidence may contain embedded newlines; parse
the TSV as CSV.
