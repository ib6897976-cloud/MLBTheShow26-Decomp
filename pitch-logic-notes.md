
## Cross-check against ModTheShowManager's code map

The repository's `docs/CODE_MODS.md` gives a more useful semantic map for game version 1.0.15 than the isolated patch hook alone:

- `main + 0x1655ad4` launches a pitch. Input speed is in mph; at `+0x1655b18` it converts mph to feet/second using 1.4667, then aims the initial arc at the target.
- `main + 0x1665460` dispatches a pitch or throw. Pitches get speed from the ball record at `+0x454` or `+0x458`; throws use a different path.
- `main + 0x1656f78` is the forces-on-a-ball-in-flight routine. Spin crossed with velocity at `+0x16570b4`, multiplied by a lift value and by 71.86 at `+0x1657168`, produces the break force. Drag is 0.31 at `+0x165733c`; rolling friction depends on the surface at `+0x16573bc`.
- `main + 0x1665f68` logs `Actual Pitch Movement` as where the pitch ends (`ball + 0x420`) minus where it was aimed (`ball + 0x42c`). This gives a practical way to compare pitches in `MLBTS/logs/mlb.log`.
- The pitch speed mod is an experimental multiplier in this launch/flight code; its dial range in the mod table is 0.4–2.0, default 1.3. The pitch break dial range is 0–6, default 2.5. These are scale controls for internal quantities, not mph or inches of movement.

This corrects my earlier wording: the `pitch_break` hook is best understood as scaling the spin/lift contribution in the in-flight force calculation, not as scaling the final visible movement by a guaranteed 2.5x. The physics path also includes air density, drag and gravity, so the final displacement depends on the pitch's velocity, spin vector, flight time and environment.

## How the repo retains/uses generated code

The manager does not keep a source checkout of the original game. It supplies a patch table to the recomp builder: the builder translates game code into generated C, compiles it, and the manager installs the rebuilt `mlb.exe`, keeping the prior executable as `mlb.original.exe`. The code-mod guide says its own `mts_switches.c` adds switches, dials, counters and the in-game F4 page. A dial is injected into a spare instruction slot and the manager substitutes the live dial value after translation; if that substitution fails, it falls back to a fixed number in the build.

Your 18:27 setup log shows this same build path: `tools/build.py` wrote generated files under a temporary `temp/install-92866d8b/gen` directory and the setup later cleaned up. The current clean rebuilt executable has no `mts-code.cfg` or generated game C files, so the previous Arcade Code Mods/dials were not included in this build. To inspect readable output from a future build, preserve or copy the temporary `gen` directory before setup's cleanup. The repo's code map itself is currently the quickest way to follow pitch physics.

## Preserved generated code from the clean 1.0.20 rebuild

I ran the generator directly against `MLBTS/game/exefs` and preserved its output in `decompiled/` without compiling or replacing `MLBTS/mlb.exe`:

```powershell
python\python.exe -I -X utf8 recomp\gen.py --exefs MLBTS\game\exefs --out decompiled --modules main
```

It emitted 198 chunks and about 540 MB of C for `main` (94,991 functions). The persistent output is `decompiled/main/main_0000.c` through `main_0197.c`, plus `decompiled/layout.json` and support headers. This is the 1.0.20 `main` from the current extraction; ModTheShowManager's published pitch offsets are for 1.0.15, so verify signatures/offset shifts before applying those patch addresses to this generated version. The SDK module was deliberately not lifted because the pitch gameplay routines are in `main`.

### Full code generation completed

The recomp's installer passes `--modules main,sdk` to `recomp/gen.py`; `rtld` is not one of the modules it translates into generated C. I have now generated both modules from the current extracted ExeFS, without compiling or replacing the installed executable:

```powershell
python\python.exe -I -X utf8 recomp\gen.py --exefs MLBTS\game\exefs --out decompiled --modules main
python\python.exe -I -X utf8 recomp\gen.py --exefs MLBTS\game\exefs --out decompiled --modules sdk
```

Persistent outputs are under `decompiled/main` (198 chunks, 94,991 functions, about 540 MB C) and `decompiled/sdk` (40 chunks, 40,069 functions, about 118 MB C). Together the translated modules contain roughly 658 MB of generated C. The source is the recomp's low-level translation of the game's executable code; textures, rosters and other RomFS data remain in `MLBTS/game/romfs` and are not C code.

## Current generated-code trace (from this folder's ExeFS)

I traced the live `MLBTS/game/exefs/main` into `decompiled/main`; the current code confirms the pitch hooks below are present at the documented module offsets. Useful code is in `decompiled/main/main_0158.c`:

### Initial speed and aim

- The flight setup uses the ball/pitch record in `x19`. At generated lines 28383–28393 it reads candidate pitch speeds from `ball + 0x454` and `ball + 0x458`, passes the aim point at `ball + 0x42c`, then calls `f_7001656fa4`.
- In `f_7001656fa4` (line 10404), the low halfword `0xbbbc` is combined with high halfword `0x3fbb0000`, forming float bits `0x3fbbbbbc` (~1.4667). The operation multiplies the input speed by that full value in the release path; `0x3fbb0000` by itself is not the full constant. The pitch-speed mod site at main offset `0x1656fe8` scales this speed calculation with its dial.
- The output is a 3D velocity aimed using the target point. Thus pitch speed affects travel time and consequently how long forces can act; it is not a direct movement/break slider.

### Spin break and forces

- `f_7001658448` (line 11906) handles the per-pitch trajectory/force state. The pitch record selects a subrecord by its `+0x110` index with a `0x70`-byte stride.
- At module offset `0x1658638` (around line 12040), the code loads `0x428fb824`, which is `71.85965`, and multiplies the three components of the computed vector by it before adding them to the stored 3D vector. The `pitch_break` code mod scales this coefficient by the dial (default 2.5). In the force path, the vector is the spin-cross-velocity/lift contribution documented by ModTheShowManager. This is force/acceleration input, not final plate displacement; therefore dial 2.5 does not mean 2.5x visible break in inches.
- At module offset `0x1658690`, the code supplies `-32.0` on the vertical axis and adds it to the vertical component: gravity.
- Air density/drag act elsewhere in the flight update. They can change the final trajectory along with speed, spin, and flight time.

### Practical model

A useful first-order description is:

```text
initial velocity = aim_direction * pitch_speed_mph * 1.4667 * pitch_speed_dial
spin/lift force  ~= (spin_vector x velocity_vector) * lift_coefficient * 71.85965 * pitch_break_dial
vertical force   includes -32.0 gravity
flight path      integrates those forces while drag/air-density act
```

The cross-product and integration labels follow the manager's code map; I verified the current generated code at the dial sites, initial-speed conversion and gravity site. Component units and the exact timestep still need a runtime log or deeper tracing of the integration step before treating the sketch as a fully quantified physics equation.

## Coverage audit (2026-11-21)

I rechecked the generated output against the current `MLBTS/game/exefs` modules. `decompiled/main/manifest.json` lists 94,991 generated function bodies across `main_0000.c` through `main_0197.c`; `decompiled/sdk/manifest.json` lists 40,069 across `sdk_0000.c` through `sdk_0039.c`. Both chunk sequences are contiguous, and the C function-definition counts match their manifests. The generated main+SDK C files total about 666 MB.

This is full generated C coverage of the `main` and `sdk` ExeFS code modules used by this recomp build, not recovered original source. Names, types, and intent have to be reconstructed from behavior. The ExeFS also contains `rtld` metadata, but the repo's generator is designed for `main` and `sdk`; game assets and data tables in RomFS are not decompiled C. Therefore this audit establishes code-generation coverage, not complete semantic understanding of every subsystem. The pitch endpoint record layout, plate-crossing condition, and camera projection remain to be traced before claiming ground-truth final-position offsets.

