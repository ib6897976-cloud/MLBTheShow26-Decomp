/*
 * Generic owner offsets observed in allocation-backed decode paths.
 * This does not claim an original game-class identity.
 */
#pragma once

#include <stddef.h>
#include <stdint.h>

typedef struct GenericBufferOwnerCandidate {
    uint8_t unknown_000[0x20];
    void *pointer_020;                    /* +0x20; null gates value adjustment */
    uint8_t unknown_028[0x08];
    uint64_t value_030;                    /* +0x30; unit/meaning unknown */
} GenericBufferOwnerCandidate;

_Static_assert(offsetof(GenericBufferOwnerCandidate, pointer_020) == 0x20,
               "generic owner pointer offset");
_Static_assert(offsetof(GenericBufferOwnerCandidate, value_030) == 0x30,
               "generic owner value offset");
_Static_assert(sizeof(GenericBufferOwnerCandidate) == 0x38,
               "generic owner observed extent");
