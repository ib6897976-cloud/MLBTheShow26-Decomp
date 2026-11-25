/*
 * Evidence-backed partial context layout for the current-build hit outcome
 * calculation. This is a documentation model; generated recomp C does not
 * include it. Unresolved slots remain opaque.
 */
#pragma once

#include <stddef.h>
#include <stdint.h>

typedef struct HitCalculationAuxiliaryCandidate {
    uint8_t unknown_000[0x1c];
    float calculation_input_01c;     /* +0x1c */
    uint8_t unknown_020[0x2d];
    uint8_t dispatch_flag_04d;       /* +0x4d, selects the precomputed path */
    uint8_t dispatch_flag_04e;       /* +0x4e, secondary precomputed-path gate */
} HitCalculationAuxiliaryCandidate;

typedef struct HitCalculationB8Candidate {
    uint32_t unknown_word_000;
    uint32_t unknown_word_004;
    uint32_t unknown_word_008;
    uint8_t unknown_00c[0x28];
    uint8_t enabled_flag_034;
    uint8_t unknown_035[0x03];
} HitCalculationB8Candidate;

typedef struct HitHitterSettingsCandidate {
    uint8_t unknown_000[0xbc];
    uint16_t hitter_control_type_0bc; /* 9 selects the CPU hitter slider */
} HitHitterSettingsCandidate;

typedef struct HitCalculation78Candidate {
    uint8_t unknown_000[0x35];
    uint8_t condition_flag_035;
} HitCalculation78Candidate;

typedef struct HitCalculationC0Candidate {
    uint8_t unknown_000[0x69];
    uint8_t condition_flag_069;
    uint8_t unknown_06a;
    uint8_t condition_flag_06b;
} HitCalculationC0Candidate;

typedef struct HitCalculationF8Candidate {
    uint8_t unknown_000[0x04];
    uint8_t condition_flag_004;
    uint8_t unknown_005[0x02];
    uint8_t condition_flag_007;
} HitCalculationF8Candidate;

typedef struct HitCalculationContextCandidate {
    uint8_t unknown_000[0x18];
    void *unknown_object_018;       /* +0x18, used as a writable object */
    uint8_t unknown_020[0x18];
    uint64_t unknown_038;
    HitHitterSettingsCandidate *hitter_settings_040;
    uint64_t unknown_048;
    uint8_t unknown_050[0x08];
    uint64_t unknown_058;
    uint8_t unknown_060[0x18];
    HitCalculation78Candidate *nested_078;
    uint8_t unknown_080[0x28];
    uint64_t unknown_0a8;
    uint8_t unknown_0b0[0x08];
    HitCalculationB8Candidate *nested_0b8;
    HitCalculationC0Candidate *nested_0c0;
    uint8_t unknown_0c8[0x30];
    HitCalculationF8Candidate *nested_0f8;
    uint8_t unknown_100[0x20];
    uint64_t unknown_120;
    uint8_t unknown_128[0x10];
    uint64_t unknown_138;
    HitCalculationAuxiliaryCandidate *auxiliary_140; /* nested +0x1c and dispatch flags */
} HitCalculationContextCandidate;

_Static_assert(offsetof(HitCalculationAuxiliaryCandidate, calculation_input_01c) == 0x1c, "hit auxiliary float offset");
_Static_assert(offsetof(HitCalculationAuxiliaryCandidate, dispatch_flag_04d) == 0x4d, "hit dispatch flag D offset");
_Static_assert(offsetof(HitCalculationAuxiliaryCandidate, dispatch_flag_04e) == 0x4e, "hit dispatch flag E offset");
_Static_assert(sizeof(HitCalculationAuxiliaryCandidate) == 0x4f, "hit auxiliary observed extent");
_Static_assert(offsetof(HitCalculationB8Candidate, enabled_flag_034) == 0x34, "hit context B8 flag offset");
_Static_assert(sizeof(HitCalculationB8Candidate) == 0x38, "hit context B8 observed extent");
_Static_assert(offsetof(HitHitterSettingsCandidate, hitter_control_type_0bc) == 0xbc, "hitter settings selector offset");
_Static_assert(sizeof(HitHitterSettingsCandidate) == 0xbe, "hitter settings observed extent");
_Static_assert(offsetof(HitCalculation78Candidate, condition_flag_035) == 0x35, "hit context +0x78 nested flag offset");
_Static_assert(sizeof(HitCalculation78Candidate) == 0x36, "hit context +0x78 nested extent");
_Static_assert(offsetof(HitCalculationC0Candidate, condition_flag_069) == 0x69, "hit context +0xc0 first nested flag offset");
_Static_assert(offsetof(HitCalculationC0Candidate, condition_flag_06b) == 0x6b, "hit context +0xc0 second nested flag offset");
_Static_assert(sizeof(HitCalculationC0Candidate) == 0x6c, "hit context +0xc0 nested extent");
_Static_assert(offsetof(HitCalculationF8Candidate, condition_flag_004) == 0x04, "hit context +0xf8 first nested flag offset");
_Static_assert(offsetof(HitCalculationF8Candidate, condition_flag_007) == 0x07, "hit context +0xf8 second nested flag offset");
_Static_assert(sizeof(HitCalculationF8Candidate) == 0x08, "hit context +0xf8 nested extent");
_Static_assert(offsetof(HitCalculationContextCandidate, unknown_object_018) == 0x18, "hit context +0x18 offset");
_Static_assert(offsetof(HitCalculationContextCandidate, nested_078) == 0x78, "hit context +0x78 offset");
_Static_assert(offsetof(HitCalculationContextCandidate, nested_0c0) == 0xc0, "hit context +0xc0 offset");
_Static_assert(offsetof(HitCalculationContextCandidate, nested_0f8) == 0xf8, "hit context +0xf8 offset");
_Static_assert(offsetof(HitCalculationContextCandidate, nested_0b8) == 0xb8, "hit context +0xb8 offset");
_Static_assert(offsetof(HitCalculationContextCandidate, hitter_settings_040) == 0x40, "hit context settings pointer offset");
_Static_assert(offsetof(HitCalculationContextCandidate, unknown_120) == 0x120, "hit context +0x120 offset");
_Static_assert(offsetof(HitCalculationContextCandidate, unknown_138) == 0x138, "hit context +0x138 offset");
_Static_assert(offsetof(HitCalculationContextCandidate, auxiliary_140) == 0x140, "hit context +0x140 offset");
_Static_assert(sizeof(HitCalculationContextCandidate) == 0x148, "hit context observed extent");
