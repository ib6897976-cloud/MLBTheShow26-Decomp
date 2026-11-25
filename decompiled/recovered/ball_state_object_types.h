/* Partial source object reached through BallRecordCandidate +0x560. */
#pragma once
#include <stddef.h>
#include <stdint.h>

typedef struct BallStateObjectCandidate {
    uint8_t unknown_000[0x10];
    uint8_t initialized_guard_candidate; /* +0x10, checked before default initialization */
    uint8_t unknown_011[0x9f];
    float transform_matrix_candidate[4][4]; /* +0xb0..+0xef */
} BallStateObjectCandidate;

_Static_assert(offsetof(BallStateObjectCandidate, initialized_guard_candidate) == 0x10,
               "ball state init guard offset");
_Static_assert(offsetof(BallStateObjectCandidate, transform_matrix_candidate) == 0xb0,
               "ball state transform matrix offset");
_Static_assert(sizeof(BallStateObjectCandidate) == 0xf0,
               "minimum observed ball state object extent");
