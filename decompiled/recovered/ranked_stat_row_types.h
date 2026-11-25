#ifndef MLBTS_RANKED_STAT_ROW_TYPES_H
#define MLBTS_RANKED_STAT_ROW_TYPES_H

#include <stddef.h>
#include <stdint.h>

typedef struct __attribute__((packed)) RankedPlayerStatRowCandidate {
    uint8_t row_state_000_candidate;
    uint8_t payload_a_001_00f_candidate[0x0f];
    uint8_t payload_a_tail_010_candidate;
    uint8_t payload_b_011_01f_candidate[0x0f];
    uint8_t payload_b_tail_020_candidate;
    uint8_t unknown_021_023_candidate[3];
    float metric_024_candidate;
    uint16_t candidate_value_028_candidate;
    uint8_t candidate_byte_02a_candidate;
    uint8_t unknown_02b_candidate;
    uint8_t candidate_byte_02c_candidate;
    uint8_t unknown_02d_02f_candidate[3];
} RankedPlayerStatRowCandidate;

_Static_assert(offsetof(RankedPlayerStatRowCandidate, payload_a_001_00f_candidate) == 0x01,
               "first copied payload offset");
_Static_assert(offsetof(RankedPlayerStatRowCandidate, payload_b_011_01f_candidate) == 0x11,
               "second copied payload offset");
_Static_assert(offsetof(RankedPlayerStatRowCandidate, metric_024_candidate) == 0x24,
               "ranking metric offset");
_Static_assert(offsetof(RankedPlayerStatRowCandidate, candidate_value_028_candidate) == 0x28,
               "candidate halfword offset");
_Static_assert(sizeof(RankedPlayerStatRowCandidate) == 0x30,
               "observed ranked row stride");

#endif
