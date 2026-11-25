#ifndef MLBTS_RECOVERED_COPYABLE_RECORD_TYPES_H
#define MLBTS_RECOVERED_COPYABLE_RECORD_TYPES_H

#include <stddef.h>
#include <stdint.h>

/* Partial object layout inferred from f_700183bfe4 copy behavior. */
typedef struct CopyAssignableRecordCandidate {
    uint8_t unknown_prefix_000_017_candidate[0x18];
    uint64_t packed_value_018_candidate;
    uint32_t packed_value_020_candidate;
    uint32_t packed_default_024_candidate;
    uint8_t d_pitcher_atts_merged_bytes_028_041_candidate[0x1a];
    uint32_t d_pitcher_atts_default_word_042_candidate;
    uint16_t d_pitcher_atts_default_halfword_046_candidate;
    uint32_t reset_state_word_048_candidate;
    uint16_t reset_state_value_04c_candidate;
    uint8_t unknown_04e_04f_candidate[2];
    void *d_pitcher_atts_payload_050_candidate;
} CopyAssignableRecordCandidate;

_Static_assert(offsetof(CopyAssignableRecordCandidate, unknown_prefix_000_017_candidate) == 0x00,
               "unknown record prefix offset");
_Static_assert(offsetof(CopyAssignableRecordCandidate, packed_value_018_candidate) == 0x18,
               "packed 64-bit value offset");
_Static_assert(offsetof(CopyAssignableRecordCandidate, packed_value_020_candidate) == 0x20,
               "packed 32-bit value offset");
_Static_assert(offsetof(CopyAssignableRecordCandidate, packed_default_024_candidate) == 0x24,
               "packed default value offset");
_Static_assert(offsetof(CopyAssignableRecordCandidate, d_pitcher_atts_merged_bytes_028_041_candidate) == 0x28,
               "D_PITCHER_ATTS merged bytes offset");
_Static_assert(offsetof(CopyAssignableRecordCandidate, d_pitcher_atts_default_word_042_candidate) == 0x42,
               "D_PITCHER_ATTS default word offset");
_Static_assert(offsetof(CopyAssignableRecordCandidate, d_pitcher_atts_default_halfword_046_candidate) == 0x46,
               "D_PITCHER_ATTS default halfword offset");
_Static_assert(offsetof(CopyAssignableRecordCandidate, reset_state_word_048_candidate) == 0x48,
               "reset state word offset");
_Static_assert(offsetof(CopyAssignableRecordCandidate, reset_state_value_04c_candidate) == 0x4c,
               "reset state value offset");
_Static_assert(offsetof(CopyAssignableRecordCandidate, unknown_04e_04f_candidate) == 0x4e,
               "uncopied gap before payload pointer");
_Static_assert(offsetof(CopyAssignableRecordCandidate, d_pitcher_atts_payload_050_candidate) == 0x50,
               "D_PITCHER_ATTS payload pointer offset");
_Static_assert(sizeof(CopyAssignableRecordCandidate) == 0x58,
               "minimum copyable record extent");

/* 0xf1-byte table block initialized by f_70017c64d0. The byte-entry values
 * are selected from global defaults or set to 0xff; their game-level names
 * are not recovered. */
typedef struct __attribute__((packed)) ByteDefaultTableCandidate {
    uint8_t unknown_prefix_000_011_candidate[0x12];
    uint8_t marker_bytes_012_01c_candidate[0x0b];
    uint8_t unknown_region_01d_022_candidate[0x06];
    uint8_t marker_byte_023_candidate;
    uint8_t unknown_region_024_04f_candidate[0x2c];
    uint8_t value_bytes_050_0ef_candidate[0xa0];
    uint8_t tail_sentinel_0f0_candidate;
} ByteDefaultTableCandidate;

_Static_assert(offsetof(ByteDefaultTableCandidate, marker_bytes_012_01c_candidate) == 0x12,
               "table marker bytes offset");
_Static_assert(offsetof(ByteDefaultTableCandidate, marker_byte_023_candidate) == 0x23,
               "table marker byte offset");
_Static_assert(offsetof(ByteDefaultTableCandidate, value_bytes_050_0ef_candidate) == 0x50,
               "table entry byte array offset");
_Static_assert(sizeof(ByteDefaultTableCandidate) == 0xf1,
               "observed byte table extent");

typedef struct __attribute__((packed)) ZeroedSubobjectCandidate {
    uint8_t zeroed_bytes_000_055_candidate[0x56];
} ZeroedSubobjectCandidate;

_Static_assert(sizeof(ZeroedSubobjectCandidate) == 0x56,
               "observed zeroed subobject extent");

/* First 30-byte payload prefix copied by the record helper and initialized by
 * both the zero-state and seeded-default helpers. */
typedef struct __attribute__((packed)) NestedPayloadPrefixCandidate {
    uint32_t state_word_000_candidate;
    uint16_t state_value_004_candidate;
    uint8_t unknown_region_006_01d_candidate[0x18];
} NestedPayloadPrefixCandidate;

_Static_assert(offsetof(NestedPayloadPrefixCandidate, state_word_000_candidate) == 0x00,
               "nested payload state word offset");
_Static_assert(offsetof(NestedPayloadPrefixCandidate, state_value_004_candidate) == 0x04,
               "nested payload state value offset");
_Static_assert(offsetof(NestedPayloadPrefixCandidate, unknown_region_006_01d_candidate) == 0x06,
               "nested payload unknown region offset");
_Static_assert(sizeof(NestedPayloadPrefixCandidate) == 0x1e,
               "minimum nested payload prefix extent");

/* Enclosing layout observed through the two initializer variants at
 * f_7001820284 and f_70018202f0. Several subobject identities remain unknown. */
typedef struct __attribute__((packed)) CompositeRecordCandidate {
    CopyAssignableRecordCandidate d_player_atts_section_000_057_candidate;
    NestedPayloadPrefixCandidate d_pitcher_atts_payload_inline_058_candidate;
    uint8_t unknown_gap_076_077_candidate[2];
    ByteDefaultTableCandidate d_player_app_section_078_candidate;
    uint8_t unknown_gap_169_16b_candidate[3];
    ZeroedSubobjectCandidate d_player_acc_section_16c_1c1_candidate;
    uint8_t unknown_gap_1c2_1c3_candidate[2];
    uint32_t field_1c4_u32_candidate;
    uint8_t unknown_1c8_1cb_candidate[4];
    uint32_t field_1cc_u32_candidate;
    uint32_t field_1d0_u32_candidate;
    uint16_t field_1d4_u16_candidate;
    int16_t field_1d6_s16_candidate;
    uint64_t field_1d8_qword_candidate;
    uint64_t unknown_1e0_1e7_candidate;
    uint64_t field_1e8_qword_candidate;
    uint64_t unknown_1f0_1f7_candidate;
    uint8_t field_1f8_u8_candidate;
    uint8_t field_1f9_u8_candidate;
    uint8_t field_1fa_u8_candidate;
} CompositeRecordCandidate;

_Static_assert(offsetof(CompositeRecordCandidate, d_pitcher_atts_payload_inline_058_candidate) == 0x58,
               "inline nested payload offset");
_Static_assert(offsetof(CompositeRecordCandidate, d_player_app_section_078_candidate) == 0x78,
               "byte table subobject offset");
_Static_assert(offsetof(CompositeRecordCandidate, d_player_acc_section_16c_1c1_candidate) == 0x16c,
               "zeroed subobject offset");
_Static_assert(offsetof(CompositeRecordCandidate, field_1c4_u32_candidate) == 0x1c4,
               "selector-visible word offset");
_Static_assert(offsetof(CompositeRecordCandidate, field_1cc_u32_candidate) == 0x1cc,
               "selector-visible word offset");
_Static_assert(offsetof(CompositeRecordCandidate, field_1d0_u32_candidate) == 0x1d0,
               "selector-visible word offset");
_Static_assert(offsetof(CompositeRecordCandidate, field_1d6_s16_candidate) == 0x1d6,
               "selector-visible signed halfword offset");
_Static_assert(offsetof(CompositeRecordCandidate, field_1d8_qword_candidate) == 0x1d8,
               "copied and selector-visible qword offset");
_Static_assert(offsetof(CompositeRecordCandidate, field_1e8_qword_candidate) == 0x1e8,
               "copied and selector-visible qword offset");
_Static_assert(offsetof(CompositeRecordCandidate, field_1f8_u8_candidate) == 0x1f8,
               "selector-visible byte offset");
_Static_assert(sizeof(CompositeRecordCandidate) == 0x1fb,
               "minimum enclosing object extent from initializer stores");


#endif
