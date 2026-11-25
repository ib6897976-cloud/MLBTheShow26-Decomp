# Nintendo SDK EXIF extractor

## Scope and confidence

This is a recovered SDK utility (`nn::image::ExifExtractor`), not a gameplay type. Method names and signatures are from exported Itanium symbols. The partial layout is backed by constructor and setter stores plus reads in `Analyze`; offsets inside the pointed-to EXIF/work-buffer data are not object members. See `recovered/exif_extractor_types.h` for an ABI-shaped candidate layout.

## Object layout

| Offset | Candidate type | Meaning | Evidence |
|---|---|---|---|
| `+0x00` | vtable pointer | `nn::image::ExifExtractor` virtual table | Constructor stores pointer loaded from SDK vtable region + `0xcb8`, adjusted by `+0x10` |
| `+0x08` | `uint32_t` | analyzed/ready flag | Constructor initializes 0; `SetExifData` sets 1; `Analyze` checks it |
| `+0x10` | `void*` | caller-provided work buffer | Constructor stores argument 1; `Analyze` loads this and initializes parser/work state |
| `+0x18` | `void const*` | EXIF input buffer | `SetExifData` stores argument 1; `Analyze` loads it |
| `+0x20` | `uint16_t` | EXIF input size (candidate) | Setter uses `ST16` from length argument; Analyze reads halfword |
| `+0x22..+0x27` | padding/unknown | not characterized | object extent only inferred from highest accessed field |

Caveat: on the target ABI, constructor `void*` and `unsigned long` arguments are passed in x1/x2. Setter stores x2 with a 16-bit write, so the exposed `unsigned long` length is narrowed.

## Behavior and function map

- `GetWorkBufferSize()` is a constant-return query (`0x7004c4ef54`); its caller is `ExifBuilder::Build`.
- Constructor (`0x7004c4ef5c`) initializes the flag, stores the work buffer, and installs the vtable.
- `SetExifData(data, size)` (`0x7004c4efa0`) stores data and 16-bit size, and marks the object ready for analysis.
- `Analyze()` (`0x7004c4efb4`, 0x260 bytes) consumes the work buffer and input range, initializes EXIF parser tables, validates/builds parser entries, and returns `-32` on the observed failure path. It also sets up tags including DateTime, Orientation, MakerNote, dimensions, and thumbnail-related entries. Fine-grained tag/value semantics still need additional tracing.
- Accessors return status and write outputs through their pointer arguments: `ExtractMaker`, `ExtractModel`, `ExtractOrientation`, `ExtractSoftware`, `ExtractDateTime`, `ExtractMakerNote`, `ExtractEffectiveDimension`, `ExtractUniqueId`, and `ExtractThumbnail` (addresses/symbols in `type_methods.tsv`).
- DateTime and UniqueId accessors validate byte sequences at offsets in parser-provided buffers. Those byte offsets are not fields of `ExifExtractor` itself.

## Evidence locations

Generated SDK body: `decompiled/sdk/sdk_0001.c`, functions `f_7004c4ef5c`, `f_7004c4efa0`, `f_7004c4efb4`, and `f_7004c4f220` through `f_7004c4f6ac`. Exported symbol inventory: `decompiled/type_methods.tsv`; field access heuristic inventory: `decompiled/type_class_field_candidates.tsv`.
