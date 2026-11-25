#ifndef MLBTS_CATEGORY_CANDIDATE_TYPES_H
#define MLBTS_CATEGORY_CANDIDATE_TYPES_H

#include <stddef.h>
#include <stdint.h>

typedef struct __attribute__((packed)) CategoryCandidateEntryCandidate {
    uint64_t field_000_candidate;
    uint64_t field_008_candidate;
    uint8_t unknown_010_017_candidate[8];
} CategoryCandidateEntryCandidate;

_Static_assert(sizeof(CategoryCandidateEntryCandidate) == 0x18,
               "observed candidate entry stride");

/* Only the count and first inline entry are modeled; list capacity is unknown. */
typedef struct __attribute__((packed)) CategoryCandidateListCandidate {
    uint8_t unknown_000_097_candidate[0x98];
    uint32_t entry_count_098_candidate;
    uint8_t unknown_09c_0df_candidate[0x44];
    CategoryCandidateEntryCandidate first_entry_0e0_candidate;
} CategoryCandidateListCandidate;

_Static_assert(offsetof(CategoryCandidateListCandidate, entry_count_098_candidate) == 0x98,
               "candidate count offset");
_Static_assert(offsetof(CategoryCandidateListCandidate, first_entry_0e0_candidate) == 0xe0,
               "candidate array offset");
_Static_assert(sizeof(CategoryCandidateListCandidate) == 0xf8,
               "minimum observed candidate list extent");

#endif
