/* Partial current-build layout for the pitch-fatigue scalar path.
 * Field meanings are candidates; unknown bytes and pointer targets remain opaque.
 * Documentation model only, not included by generated recomp C. */
#pragma once
#include <stddef.h>
#include <stdint.h>
typedef struct PitchFatigueGateSourceCandidate {
    uint8_t unknown_000[0x08];
    uint32_t gate_value_008_candidate;            /* +0x08; tested against zero */
} PitchFatigueGateSourceCandidate;

typedef struct PitchFatigueFactorSourceCandidate {
    uint8_t unknown_000[0xe0];
    float divisor_scalar_e0_candidate;            /* +0xe0; read as float in final scaling */
} PitchFatigueFactorSourceCandidate;

typedef struct PitchFatigueProviderInterfaceCandidate {
    const void *vtable_candidate;                 /* +0x00; fatigue helper dispatches multiple virtual slots */
} PitchFatigueProviderInterfaceCandidate;

typedef struct PitchFatigueContextCandidate {
    uint8_t unknown_000[0x08];
    PitchFatigueGateSourceCandidate *gate_source_08_candidate; /* +0x08 */
    PitchFatigueFactorSourceCandidate *factor_source_10_candidate; /* +0x10 */
    struct PitchFatigueModifierCandidate *rate_modifier_object; /* +0x18 */
    PitchFatigueProviderInterfaceCandidate *provider_candidate; /* +0x20 */
} PitchFatigueContextCandidate;
typedef struct PitchFatigueModifierCandidate {
    uint8_t unknown_000[0x24];
    float per_pitch_rate_modifier_candidate;      /* +0x24 */
    uint8_t unknown_028[0x0d];
    uint8_t rate_modifier_enabled_flag;           /* +0x35 */
} PitchFatigueModifierCandidate;
_Static_assert(offsetof(PitchFatigueGateSourceCandidate, gate_value_008_candidate) == 0x08, "fatigue gate value offset");
_Static_assert(sizeof(PitchFatigueGateSourceCandidate) == 0x0c, "fatigue gate source extent");
_Static_assert(offsetof(PitchFatigueFactorSourceCandidate, divisor_scalar_e0_candidate) == 0xe0, "fatigue divisor scalar offset");
_Static_assert(sizeof(PitchFatigueFactorSourceCandidate) == 0xe4, "fatigue factor source extent");
_Static_assert(offsetof(PitchFatigueProviderInterfaceCandidate, vtable_candidate) == 0x00, "fatigue provider vtable offset");
_Static_assert(sizeof(PitchFatigueProviderInterfaceCandidate) == 0x08, "fatigue provider interface extent");
_Static_assert(offsetof(PitchFatigueContextCandidate, provider_candidate) == 0x20, "fatigue provider pointer offset");
_Static_assert(offsetof(PitchFatigueContextCandidate, gate_source_08_candidate) == 0x08, "fatigue gate source pointer offset");
_Static_assert(offsetof(PitchFatigueContextCandidate, factor_source_10_candidate) == 0x10, "fatigue factor source pointer offset");
_Static_assert(offsetof(PitchFatigueContextCandidate, rate_modifier_object) == 0x18, "fatigue config pointer offset");
_Static_assert(offsetof(PitchFatigueModifierCandidate, per_pitch_rate_modifier_candidate) == 0x24, "fatigue modifier offset");
_Static_assert(offsetof(PitchFatigueModifierCandidate, rate_modifier_enabled_flag) == 0x35, "fatigue modifier flag offset");
