#ifndef MLBTS_STRIDE18_RECORD_TYPES_H
#define MLBTS_STRIDE18_RECORD_TYPES_H

#include <stddef.h>
#include <stdint.h>

/* Element view inferred from repeated initializer stores. The bytes outside
 * these two words are not semantically identified. */
typedef struct __attribute__((packed)) Stride18RecordCandidate {
    uint8_t unknown_000_00b_candidate[0x0c];
    uint32_t word_00c_candidate;
    uint8_t unknown_010_013_candidate[4];
    uint32_t word_014_candidate;
} Stride18RecordCandidate;

_Static_assert(offsetof(Stride18RecordCandidate, word_00c_candidate) == 0x0c,
               "first repeated word offset");
_Static_assert(offsetof(Stride18RecordCandidate, word_014_candidate) == 0x14,
               "second repeated word offset");
_Static_assert(sizeof(Stride18RecordCandidate) == 0x18,
               "observed record stride");

#endif
