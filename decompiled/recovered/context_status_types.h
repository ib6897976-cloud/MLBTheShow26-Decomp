#ifndef MLBTS_CONTEXT_STATUS_TYPES_H
#define MLBTS_CONTEXT_STATUS_TYPES_H

#include <stddef.h>
#include <stdint.h>

typedef struct __attribute__((packed)) ContextStatusCandidate {
    uint8_t unknown_000_017_candidate[0x18];
    uint8_t flags_018_candidate;
} ContextStatusCandidate;

_Static_assert(offsetof(ContextStatusCandidate, flags_018_candidate) == 0x18,
               "observed flag byte offset");
_Static_assert(sizeof(ContextStatusCandidate) == 0x19,
               "minimum observed context extent");

#endif
