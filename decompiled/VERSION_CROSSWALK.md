# Verified v1.0.15 to current-build code crosswalk

The public [ModTheShowManager code map](https://github.com/elripalda/ModTheShowManager/blob/main/docs/CODE_MODS.md) describes offsets in game v1.0.15. The local generated C is from the current extracted build (v1.0.20). Do not apply a single global address delta: confirmed examples show at least two local shifts. Each correspondence below is tied to behavior in the generated code.

| v1.0.15 main offset | Current generated entry | Shift | Cross-check |
|---|---:|---:|---|
| `0x1655ad4` pitch launch | `0x7001656fa4` | `+0x14d0` | Current code multiplies an input speed by the encoded `1.4667` factor and constructs the initial velocity/output state. |
| `0x1656f78` in-flight forces | `0x7001658448` | `+0x14d0` | Current pitch-flight path calls the force/state routine; its current-build role is also supported by the live trace and flight-state accesses. |
| `0x1665460` pitch-or-throw dispatcher | `0x7001666930` | `+0x14d0` | Current code branches on `+0x482`, selects pitch speed `+0x454` or throw speed `+0x458`, and calls the corresponding launch helper. |
| `0x166a2a4` ball release/update | `0x700166b774` | `+0x14d0` | Current code follows the ball's `+0x560` object pointer, copies motion state and sets a state byte. |
| `0x1688000` thrown-ball speed conversion | `0x70016894d0` | `+0x14d0` | Current code applies float `0x3fbbbbbc` (~1.4667) to a 3D velocity vector. |
| `0x1678010` perfect-timing check | `0x70016794e0` | `+0x14d0` | Current helper returns a boolean that the hit routine stores at hit-record `+0x4e`; current code checks timing/context gates. |
| `0x16767d0` bunt setup | `0x7001677ca0` | `+0x14d0` | Current code writes the bunt-specific bytes at `+0x50/+0x51`, writes power at `+0x48`, and applies the 130 mph cap. |
| `0x167880c` hit entry | `0x7001679cdc` | `+0x14d0` | Initializes the result record and dispatches to precomputed or normal hit calculation. |
| `0x1678848` precomputed hit path | `0x7001679d18` | `+0x14d0` | Current entry is the precomputed branch target selected by the hit-entry dispatcher. |
| `0x167a6ac` hit calculation | `0x700167bb7c` | `+0x14d0` | Current entry consumes the hit record, calculates rating outcomes, stores flags at `+0x4c/+0x4e`, and scales power at `+0x48` by `1.4667`. |
| `0x16785f8` check-swing power multiplier site | `0x7001679ac8` inside `f_70016799f8` | `+0x14d0` | The current containing function derives a scalar, scales hit-record power at `+0x48` and three float components at `+0x28/+0x2c/+0x30`, and conditionally sets byte `+0x54`. This is a site correspondence, not a function-entry match. |
| `0x3560d0` swing aim-error routine | `0x70003560f0` | `+0x20` | Current code calculates the PCI-to-pitch-crossing error and its magnitude. |
| `0x356a18` outer-PCI adjustment site | `0x7000356a38` inside `f_70003560f0` | `+0x20` | Current code remaps the swing-type value and writes the adjusted PCI outer size back to swing record `+0x64`; it also checks a mode flag. This is a site correspondence inside the swing setup function. |
| `0x358744` contact-chance routine | `0x7000358764` | `+0x20` | Current code reads the error magnitude and PCI dimensions and updates contact-related state. |

These are local code correspondences, not a general version-conversion formula. Code changes can alter function boundaries and shift different regions by different amounts. Other external offsets must be matched by instruction or behavior before being attributed to a current function.

Additional mapped code sites: v1.0.15 stamina sites `0x3c56fc` and `0x3c5710` correspond to the two 2.1-base branches in current function `0x70003c5680`; the current `0x70003c5680` function contains the corresponding 2.1 branches, but an exact site-by-site address delta has not been established.

Additional mapped code sites: v1.0.15 ball-contact site `0x1658dbc` maps by `+0x14d0` to block `0x700165a28c` inside current function `0x7001659c70`; the block computes collision response values and writes a contact-state record. The v1.0.15 final air-density multiply at `0x165ac78` maps by `+0x14d0` to `0x700165c148` inside current function `0x700165c02c`, which returns the scalar consumed by the force-update caller. These are code sites inside functions, not function entry addresses.

Additional mapped code sites: v1.0.15 swing offset `0x35acdc` maps by `+0x20` into current function `0x700035abec`, the broken-bat chance helper. The documented power-penalty sites `0x16808d4–0x1680c70` map by `+0x14d0` into current function `0x7001681314`; they are code locations inside that function, not entry addresses.
