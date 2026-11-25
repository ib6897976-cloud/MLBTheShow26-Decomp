#ifndef MLBTS_RECORD_FIELD_DESCRIPTOR_TYPES_H
#define MLBTS_RECORD_FIELD_DESCRIPTOR_TYPES_H

#include <stddef.h>
#include <stdint.h>

typedef struct __attribute__((packed)) RecordFieldDescriptorCandidate {
    uint8_t unknown_000_013_candidate[0x14];
    uint16_t value_left_014_u16_candidate;
    uint16_t value_right_016_u16_candidate;
    uint32_t expected_product_018_u32_candidate;
    uint8_t unknown_01c_01f_candidate[4];
} RecordFieldDescriptorCandidate;

_Static_assert(offsetof(RecordFieldDescriptorCandidate, value_left_014_u16_candidate) == 0x14,
               "descriptor halfword offset");
_Static_assert(offsetof(RecordFieldDescriptorCandidate, value_right_016_u16_candidate) == 0x16,
               "descriptor halfword offset");
_Static_assert(offsetof(RecordFieldDescriptorCandidate, expected_product_018_u32_candidate) == 0x18,
               "descriptor word offset");
_Static_assert(sizeof(RecordFieldDescriptorCandidate) == 0x20,
               "observed descriptor stride");

#endif
