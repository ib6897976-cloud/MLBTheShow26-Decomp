/*
 * Partial current-build ball record fields. Layout is incomplete.
 * The semantic labels are cross-checked against current code and the v1.0.15
 * external map; this file is documentation-only, not included by generated C.
 */
#pragma once

#include <stddef.h>
#include <stdint.h>

typedef struct BallRecordCandidate {
    uint8_t unknown_000[0x337];
    uint8_t release_state_marker_337_candidate; /* +0x337, set to 1 on release update */
    uint8_t unknown_338[0x74];
    float release_scalar_3ac_candidate;         /* +0x3ac, computed from release state */
    uint8_t unknown_3b0[0x30];
    float release_transform_matrix_candidate[4][4]; /* +0x3e0; copied from state object +0xb0 */
    uint8_t unknown_420[0x34];
    float pitch_speed_mph_candidate;      /* +0x454 */
    float throw_speed_mph_candidate;      /* +0x458 */
    uint8_t unknown_45c[0x25];
    uint8_t release_snapshot_valid_candidate; /* +0x481 */
    uint8_t pitch_mode_flag_candidate;    /* +0x482 */
    uint8_t unknown_483[0xdd];
    void *ball_state_object_candidate;    /* +0x560 */
} BallRecordCandidate;

_Static_assert(offsetof(BallRecordCandidate, release_state_marker_337_candidate) == 0x337, "ball release marker offset");
_Static_assert(offsetof(BallRecordCandidate, release_scalar_3ac_candidate) == 0x3ac, "ball release scalar offset");
_Static_assert(offsetof(BallRecordCandidate, release_transform_matrix_candidate) == 0x3e0, "ball release transform matrix offset");
_Static_assert(offsetof(BallRecordCandidate, ball_state_object_candidate) == 0x560, "ball state pointer offset");
_Static_assert(offsetof(BallRecordCandidate, pitch_speed_mph_candidate) == 0x454, "ball pitch speed offset");
_Static_assert(offsetof(BallRecordCandidate, throw_speed_mph_candidate) == 0x458, "ball throw speed offset");
_Static_assert(offsetof(BallRecordCandidate, release_snapshot_valid_candidate) == 0x481, "release snapshot guard offset");
_Static_assert(offsetof(BallRecordCandidate, pitch_mode_flag_candidate) == 0x482, "ball pitch flag offset");
