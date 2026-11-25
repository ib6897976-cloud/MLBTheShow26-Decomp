/*
 * Evidence-backed partial type reconstruction for the current MLBTS build.
 * This header is documentation/data modeling only; generated recomp C does
 * not include it. Unknown bytes stay explicitly reserved.
 */
#pragma once

#include <stddef.h>
#include <stdint.h>

typedef struct PitchFlightStateSlotCandidate {
    float unknown_vector_000_candidate[3];         /* +0x00; force update writes three components */
    float unknown_f32_00c_candidate;               /* +0x0c; read in state magnitude calculation */
    uint8_t unknown_010[0x04];
    float unknown_f32_014_candidate;               /* +0x14; read in state magnitude calculation */
    uint8_t unknown_018[0x18];
    /* Twelve f32 outputs built from the direction at +0x18; frame convention unknown. */
    float direction_frame_candidate[3][4];    /* +0x30 */
    /* Vector used in the paired-record distance calculation; meaning unknown. */
    float pair_distance_vector[3];                 /* +0x60 */
    uint8_t unknown_06c[0x04];
} PitchFlightStateSlotCandidate;

typedef struct PitchFlightContextCandidate {
    uint8_t unknown_000[0x14];
    float selected_state_result_014;              /* +0x14; units unknown */
    float selected_state_result_018;              /* +0x18; units unknown */
    float selected_state_result_01c;              /* +0x1c; units unknown */
    float selected_state_result_020;              /* +0x20; units unknown */
    uint8_t unknown_024[0x0c];
    PitchFlightStateSlotCandidate state_slots[2];   /* +0x30, stride 0x70 */
    uint32_t flight_state_index_a;                 /* +0x110, toggled with XOR 1 */
    uint32_t flight_state_index_b;                 /* +0x114, toggled with XOR 1 */
    uint8_t unknown_118[0x5c];
    uint32_t flight_flags_174;                     /* +0x174, bits 13/15 tested */
    uint8_t unknown_178[0x14];
    float flight_scalar_18c;                       /* +0x18c, clamped >= 0 */
    uint8_t unknown_190[0x130];
    uint8_t unknown_flag_2c0_candidate;            /* +0x2c0, read/set in force update */
    uint8_t unknown_flag_2c1_candidate;            /* +0x2c1, branch input */
    uint8_t unknown_2c2[0x04];
    uint8_t flight_flag_2c6;                       /* +0x2c6, meaning unknown */
    uint8_t unknown_2c7[0x11];
    float unknown_f32_2d8_candidate;               /* +0x2d8, used in float threshold path */
    uint8_t unknown_2dc[0x08];
    float unknown_f32_2e4_candidate;               /* +0x2e4, compared during state validation */
    uint8_t unknown_2e8_310[0x29];
    uint8_t flight_state_flag_311_candidate; /* +0x311; meaning unknown */
    uint8_t unknown_312_40f[0xfe];
    float release_position[3];                     /* +0x410, matches game log */
    uint8_t unknown_41c[0x04];
    float pitch_destination[3];                    /* +0x420, live-confirmed */
    float aim_reference_position[3];               /* +0x42c, live-confirmed */
} PitchFlightContextCandidate;

/* A 0x38-byte record appended by f_700165e274. Semantics are still unknown. */
typedef struct PitchFlightSampleRecordCandidate {
    uint8_t unknown_000[0x10];
    uint64_t copied_qword_010;      /* +0x10, copied from input object +0x30 */
    uint32_t copied_word_018;       /* +0x18, copied from input object +0x38 */
    uint8_t unknown_01c[0x08];
    float derived_float_024;        /* +0x24, calculated from count/ratio path */
    uint64_t copied_qword_028;      /* +0x28, copied from third input object +0 */
    uint32_t copied_word_030;       /* +0x30, copied from third input object +8 */
    float derived_float_034;        /* +0x34, numeric value from pitch setup */
} PitchFlightSampleRecordCandidate;

_Static_assert(sizeof(PitchFlightSampleRecordCandidate) == 0x38,
               "pitch sample append stride");
_Static_assert(offsetof(PitchFlightSampleRecordCandidate, copied_qword_010) == 0x10,
               "pitch sample copied qword offset");
_Static_assert(offsetof(PitchFlightSampleRecordCandidate, copied_qword_028) == 0x28,
               "pitch sample source object offset");

_Static_assert(offsetof(PitchFlightStateSlotCandidate, unknown_vector_000_candidate) == 0x00,
               "pitch state vector offset");
_Static_assert(offsetof(PitchFlightStateSlotCandidate, unknown_f32_00c_candidate) == 0x0c,
               "pitch state scalar 0x0c offset");
_Static_assert(offsetof(PitchFlightStateSlotCandidate, unknown_f32_014_candidate) == 0x14,
               "pitch state scalar 0x14 offset");
_Static_assert(offsetof(PitchFlightStateSlotCandidate, direction_frame_candidate) == 0x30,
               "pitch direction frame candidate offset");
_Static_assert(offsetof(PitchFlightContextCandidate, selected_state_result_014) == 0x14,
               "selected state result 0x14 offset");
_Static_assert(offsetof(PitchFlightContextCandidate, selected_state_result_020) == 0x20,
               "selected state result 0x20 offset");
_Static_assert(sizeof(PitchFlightStateSlotCandidate) == 0x70,
               "pitch state slot stride must remain 0x70");
_Static_assert(offsetof(PitchFlightContextCandidate, state_slots) == 0x30,
               "pitch state slot array offset changed");
_Static_assert(offsetof(PitchFlightContextCandidate, flight_state_index_a) == 0x110,
               "pitch state selector A offset changed");
_Static_assert(offsetof(PitchFlightContextCandidate, flight_state_index_b) == 0x114,
               "pitch state selector B offset changed");
_Static_assert(offsetof(PitchFlightContextCandidate, unknown_flag_2c0_candidate) == 0x2c0,
               "pitch state byte 0x2c0 offset");
_Static_assert(offsetof(PitchFlightContextCandidate, unknown_flag_2c1_candidate) == 0x2c1,
               "pitch state byte 0x2c1 offset");
_Static_assert(offsetof(PitchFlightContextCandidate, unknown_f32_2d8_candidate) == 0x2d8,
               "pitch state float 0x2d8 offset");
_Static_assert(offsetof(PitchFlightContextCandidate, unknown_f32_2e4_candidate) == 0x2e4,
               "pitch state float 0x2e4 offset");
_Static_assert(offsetof(PitchFlightContextCandidate, release_position) == 0x410,
               "release position offset changed");
_Static_assert(offsetof(PitchFlightContextCandidate, pitch_destination) == 0x420,
               "pitch destination offset changed");
_Static_assert(offsetof(PitchFlightContextCandidate, aim_reference_position) == 0x42c,
               "pitch aim reference offset changed");
