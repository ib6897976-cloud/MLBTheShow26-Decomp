# Contributing

Contributions that improve evidence, function naming, structure recovery,
analysis tooling, or documentation are welcome.

## Before proposing a semantic label

1. Confirm the target address and game build.
2. Read the full generated function body and inspect callers or callback
   registrations when available.
3. Treat strings and ranked queues as leads; trace how the function uses them.
4. Keep unsupported names blank and mark uncertain claims with lower
   confidence.
5. For field annotations, record the base, exact offset, access width, type,
   and evidence. Do not infer a complete structure from a few accesses.

For batch annotation work, follow
[`tools/data/staging/README.md`](tools/data/staging/README.md). Workers write
separate JSONL files; the shared TSV indexes are merged serially after review.

## Pull requests

Describe the target build, evidence examined, and files changed. Separate
confirmed observations from hypotheses, and note any limitations. Avoid
including game binaries, dumps, keys, proprietary assets, or locally generated
build outputs.

## Style and terminology

Follow [analysis conventions](docs/dev/CONVENTIONS.md). Preserve existing
third-party notices and licenses. Keep build-specific addresses and claims
explicitly tied to their source build.
