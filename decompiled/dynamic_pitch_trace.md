# Dynamic pitch flight trace

## Capture 1

- Target: `main+0x1658448` (`f_7001658448`), the current-build flight/force update routine.
- Runtime reported one watched function, with the exact-address filter (`range 0-0`).
- The log recorded 8 calls, call numbers 1 through 8.
- Every recorded call came from return address `main+0x1657e54`, inside `f_7001657c10`.
- `x0` was `0x1a5c10650` on all 8 calls, so the same record/context pointer was passed throughout this capture.
- The current decomp reads the input record's `+0x110` index and `+0x2c6` flag, and updates `+0x18c`; later calculations use record substructures selected from that index.

This confirms the dynamic hook is firing on the intended code path. This capture had no memory peeks, so it does not establish the numeric trajectory, endpoint, or speed values yet.

## Capture 2

- The game log reports the same trace target and exact-address filter.
- During one pitch, `f_7001658448` was called 8 times. Every call came from
  `main+0x1657e54` and passed `x0=0x1a5c10650`, matching capture 1.
- The adjacent game log entries report `ACTUAL RELEASE MAT -2.515789 6.225129
  7.869708` and `Actual Pitch Movement: -0.790, .0.783, (1.113 ft)`. The
  release-matrix values are explicitly logged as release data; the movement
  values are not proven to be the final plate-crossing position.
- No values at `x0+0x420..0x42c` were logged. `Trace Pitch Flight.bat` sets
  `MLB_FNTRACE_PEEK`, but the installed Fastball runtime emits only the target,
  caller, and `x0` in its `fntrace` lines; repository search found no
  implementation of that environment variable. The earlier claim that the
  runtime reads and prints those offsets was incorrect. The batch file's peek
  setting is inert and should not be used as evidence.

## Current conclusion

Dynamic tracing confirms the function and stable context pointer, but does not
yet reveal a ball endpoint. The decomp at `main/main_0158.c` shows this routine
using `x0+0x110` as a record index (stride `0x70`), `x0+0x2c6` as a byte flag,
and updating fields such as `x0+0x18c`; it does not establish that `+0x420`
contains the endpoint. The next step is a runtime method that can sample the
process memory at the observed `x0` pointer, or trace the specific writes to
the ball-state fields. Do not interpret the current trace as validating the
overlay endpoint pointer.

## Offset dumper

`C:\Users\Gabri\Desktop\the show\pitch_offset_dumper.py` now follows two
read-only bases: the overlay's pitch actor pointer chain, and each `x0` value
parsed from the live `fntrace` log. This matters because the captured function
context can differ from the actor pointer across separate runs because heap
addresses vary. In the latest capture both resolved to `0x1a5c14f50`. The
dumper records all 32-bit words in the first `0x570` bytes for each base, then
appends only changed words to `pitch_offset_dump.tsv`, with raw hex, unsigned
integer, and float views.

`Trace Pitch Flight.bat` now opens the dumper in a second console before
launching the game. The dumper samples memory; the runtime trace still supplies
the x0 addresses. This is a candidate-field discovery tool: changing float
values need correlation against a pitch and the decomp before naming them as
position, speed, or endpoint fields.

## Capture 3: endpoint confirmed

The live dumper captured the same `x0`/actor pointer as the function trace,
`0x1a5c14f50`. On the first call, the 3-float vector at `+0x410` was
`(-2.512840, 6.225129, 7.877664)`, matching the adjacent
`ACTUAL RELEASE MAT` log exactly. The 3-float vector at `+0x420` was
`(-0.304906, 0.938438, 62.931267)`, and the vector at `+0x42c` was
`(-1.437442, 2.978786, 62.988464)`.

The decomp in `f_70016671a0` (`main_0158.c`, around line 29140) subtracts
`+0x42c/+0x430` from `+0x420/+0x424` and computes the XY magnitude. The
captured difference is `(+1.132536, -2.040347, -0.057197)`; its XY magnitude
is `2.334` units. The corresponding runtime log says
`Actual Pitch Movement: 1.133, .-2.040, (2.334 ft)`. This numerical match and
the decomp establish `+0x420..+0x428` as the pitch's final destination vector
and `+0x42c..+0x434` as its aim/reference vector. Therefore the endpoint offset
the overlay was seeking is confirmed. The separate live ball position remains
the ball-object chain `actor+0x560 -> object+0xE0` (mirrored at `actor+0x410`).
