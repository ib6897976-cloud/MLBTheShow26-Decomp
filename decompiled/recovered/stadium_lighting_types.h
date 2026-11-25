#ifndef MLBTS_RECOVERED_STADIUM_LIGHTING_TYPES_H
#define MLBTS_RECOVERED_STADIUM_LIGHTING_TYPES_H

#include <stddef.h>
#include <stdint.h>

/* Partial current-build layout; offsets are observed on the lighting manager. */
typedef struct StadiumLightingManagerCandidate {
    uint8_t unknown_000_0c2c[0x0c2d];
    uint8_t lighting_dirty_flag_0c2d_candidate;
    uint8_t unknown_0c2e_0d37[0x010a];
    uint32_t lighting_buffer_selector_0d38_candidate;
    uint32_t bake_flags_0d3c_candidate;
} StadiumLightingManagerCandidate;

_Static_assert(offsetof(StadiumLightingManagerCandidate,
                        lighting_dirty_flag_0c2d_candidate) == 0x0c2d,
               "lighting dirty flag offset");
_Static_assert(offsetof(StadiumLightingManagerCandidate,
                        lighting_buffer_selector_0d38_candidate) == 0x0d38,
               "lighting buffer selector offset");
_Static_assert(offsetof(StadiumLightingManagerCandidate,
                        bake_flags_0d3c_candidate) == 0x0d3c,
               "lighting bake flags offset");
_Static_assert(sizeof(StadiumLightingManagerCandidate) == 0x0d40,
               "minimum observed lighting manager extent");

/* Separate probe-state object: +0x770 caches the lighting generation. */
typedef struct IndirectLightingProbeStateCandidate {
    uint8_t unknown_000_76f[0x0770];
    uint32_t cached_lighting_version_770_candidate;
} IndirectLightingProbeStateCandidate;

_Static_assert(offsetof(IndirectLightingProbeStateCandidate,
                        cached_lighting_version_770_candidate) == 0x0770,
               "cached lighting version offset");
_Static_assert(sizeof(IndirectLightingProbeStateCandidate) == 0x0774,
               "minimum observed probe-state extent");

#endif
