#ifndef MLBTS_RECOVERED_PLAYER_ATTRIBUTES_TYPES_H
#define MLBTS_RECOVERED_PLAYER_ATTRIBUTES_TYPES_H

#include <stddef.h>
#include <stdint.h>

/* Prefix storage consumed by player_attribute_get_float; not a full player struct. */
typedef struct PlayerAttributeBlockCandidate {
    int16_t attribute_id_00_s16_candidate;
    int16_t attribute_id_01_s16_candidate;
    int16_t attribute_id_02_s16_candidate;
    int16_t attribute_id_03_s16_candidate;
    int16_t attribute_id_04_s16_candidate;
    int16_t attribute_id_05_s16_candidate;
    int16_t attribute_id_06_s16_candidate;
    int16_t attribute_id_07_s16_candidate;
    int16_t attribute_id_08_s16_candidate;
    int16_t attribute_id_09_s16_candidate;
    int16_t attribute_id_0a_s16_candidate;
    int16_t attribute_id_0b_s16_candidate;
    int16_t attribute_id_0c_s16_candidate;
    int16_t attribute_id_0d_s16_candidate;
    int16_t attribute_id_0e_s16_candidate;
    int16_t attribute_id_0f_s16_candidate;
    int16_t attribute_id_10_s16_candidate;
    uint8_t attribute_id_11_u8_candidate;
    uint8_t attribute_id_12_u8_candidate;
    uint8_t attribute_id_13_u8_candidate;
    uint8_t attribute_id_14_u8_candidate;
    uint8_t attribute_id_15_u8_candidate;
    uint8_t attribute_id_16_u8_candidate;
    uint8_t attribute_id_17_u8_candidate;
    uint8_t attribute_id_18_u8_candidate;
    uint8_t attribute_id_19_u8_candidate;
    uint8_t attribute_id_1a_u8_candidate;
    uint8_t attribute_id_1b_u8_candidate;
    uint8_t attribute_id_1c_u8_candidate;
    uint8_t attribute_id_1d_u8_candidate;
    uint8_t attribute_id_1e_u8_candidate;
    uint8_t attribute_id_1f_u8_candidate;
    uint8_t attribute_id_20_u8_candidate;
    uint8_t attribute_id_21_u8_candidate;
    uint8_t attribute_id_22_u8_candidate;
    uint8_t attribute_id_23_u8_candidate;
    uint8_t attribute_id_24_u8_candidate;
    uint8_t attribute_id_25_u8_candidate;
    uint8_t attribute_id_26_u8_candidate;
    uint8_t attribute_id_27_u8_candidate;
    uint8_t attribute_id_28_u8_candidate;
    uint8_t attribute_id_29_u8_candidate;
    uint8_t attribute_id_2a_u8_candidate;
    uint8_t attribute_id_2b_u8_candidate;
    uint8_t attribute_id_2c_u8_candidate;
    uint8_t attribute_id_2d_u8_candidate;
    uint8_t attribute_id_2e_u8_candidate;
    uint8_t attribute_id_2f_u8_candidate;
    uint8_t attribute_id_30_u8_candidate;
    uint8_t attribute_id_31_u8_candidate;
    uint8_t attribute_id_32_u8_candidate;
    uint8_t attribute_id_33_u8_candidate;
    uint8_t attribute_id_34_u8_candidate;
    uint8_t attribute_id_35_u8_candidate;
    uint8_t attribute_id_36_u8_candidate;
    uint8_t attribute_id_37_u8_candidate;
    uint8_t attribute_id_38_u8_candidate;
    uint8_t attribute_id_39_u8_candidate;
    uint8_t attribute_id_3a_u8_candidate;
    uint8_t attribute_id_3b_u8_candidate;
    uint8_t attribute_id_3c_u8_candidate;
    uint8_t attribute_id_3d_u8_candidate;
    uint8_t attribute_id_3e_u8_candidate;
    uint8_t attribute_id_3f_u8_candidate;
    uint8_t attribute_id_40_u8_candidate;
    uint8_t attribute_id_41_u8_candidate;
    uint8_t attribute_id_42_u8_candidate;
    uint8_t attribute_id_43_u8_candidate;
    uint8_t attribute_id_44_u8_candidate;
    uint8_t attribute_id_45_u8_candidate;
    uint8_t attribute_id_46_u8_candidate;
    uint8_t attribute_id_47_u8_candidate;
    uint8_t attribute_id_48_u8_candidate;
    uint8_t attribute_id_49_u8_candidate;
    uint8_t attribute_id_4a_u8_candidate;
    uint8_t attribute_id_4b_u8_candidate;
    uint8_t attribute_id_4c_u8_candidate;
    uint8_t attribute_id_4d_u8_candidate;
    uint8_t attribute_id_4e_u8_candidate;
    uint8_t attribute_id_4f_u8_candidate;
    uint8_t attribute_id_50_u8_candidate;
    uint8_t attribute_id_51_u8_candidate;
    uint8_t attribute_id_52_u8_candidate;
    uint8_t attribute_id_53_u8_candidate;
} PlayerAttributeBlockCandidate;

_Static_assert(offsetof(PlayerAttributeBlockCandidate, attribute_id_00_s16_candidate) == 0x00,
               "primary attribute ID 0x00 offset");
_Static_assert(offsetof(PlayerAttributeBlockCandidate, attribute_id_10_s16_candidate) == 0x20,
               "primary attribute ID 0x10 offset");
_Static_assert(offsetof(PlayerAttributeBlockCandidate, attribute_id_11_u8_candidate) == 0x22,
               "primary attribute ID 0x11 offset");
_Static_assert(offsetof(PlayerAttributeBlockCandidate, attribute_id_53_u8_candidate) == 0x64,
               "primary attribute ID 0x53 offset");
_Static_assert(sizeof(PlayerAttributeBlockCandidate) == 0x65,
               "minimum observed player attribute block extent");

/* Secondary attribute storage reached through a provider's +0x68 pointer. */
typedef struct NestedAttributeProviderCandidate {
    uint8_t unknown_000_067_candidate[0x68];
    void *nested_attribute_block_068_candidate;
} NestedAttributeProviderCandidate;

_Static_assert(offsetof(NestedAttributeProviderCandidate, nested_attribute_block_068_candidate) == 0x68,
               "nested attribute block pointer offset");
_Static_assert(sizeof(NestedAttributeProviderCandidate) == 0x70,
               "minimum observed nested attribute provider extent");

typedef struct NestedAttributeBlockCandidate {
    int16_t attribute_id_00_s16_candidate;
    int16_t attribute_id_01_s16_candidate;
    int16_t attribute_id_02_s16_candidate;
    int16_t attribute_id_03_s16_candidate;
    int16_t attribute_id_04_s16_candidate;
    int16_t attribute_id_05_s16_candidate;
    int16_t attribute_id_06_s16_candidate;
    int16_t attribute_id_07_s16_candidate;
    int16_t attribute_id_08_s16_candidate;
    int16_t attribute_id_09_s16_candidate;
    int16_t attribute_id_0a_s16_candidate;
    int16_t attribute_id_0b_s16_candidate;
    int16_t attribute_id_0c_s16_candidate;
    int16_t attribute_id_0d_s16_candidate;
    int16_t attribute_id_0e_s16_candidate;
    int16_t attribute_id_0f_s16_candidate;
    int16_t attribute_id_10_s16_candidate;
    int16_t attribute_id_11_s16_candidate;
    int16_t attribute_id_12_s16_candidate;
    int16_t attribute_id_13_s16_candidate;
    int16_t attribute_id_14_s16_candidate;
    int16_t attribute_id_15_s16_candidate;
    uint8_t attribute_id_2c_u8_candidate;
    uint8_t attribute_id_2d_u8_candidate;
    uint8_t attribute_id_2e_u8_candidate;
    uint8_t attribute_id_2f_u8_candidate;
    uint8_t attribute_id_30_u8_candidate;
    uint8_t attribute_id_31_u8_candidate;
    uint8_t attribute_id_32_u8_candidate;
    uint8_t attribute_id_33_u8_candidate;
    uint8_t attribute_id_34_u8_candidate;
    uint8_t attribute_id_35_u8_candidate;
    uint8_t attribute_id_36_u8_candidate;
    uint8_t attribute_id_37_u8_candidate;
    uint8_t attribute_id_38_u8_candidate;
    uint8_t attribute_id_39_u8_candidate;
    uint8_t attribute_id_3a_u8_candidate;
    uint8_t attribute_id_3b_u8_candidate;
    uint8_t attribute_id_3c_u8_candidate;
    uint8_t attribute_id_3d_u8_candidate;
    uint8_t attribute_id_3e_u8_candidate;
    uint8_t attribute_id_3f_u8_candidate;
    uint8_t attribute_id_40_u8_candidate;
    uint8_t attribute_id_41_u8_candidate;
    uint8_t attribute_id_42_u8_candidate;
    uint8_t attribute_id_43_u8_candidate;
    uint8_t attribute_id_44_u8_candidate;
    uint8_t attribute_id_45_u8_candidate;
    uint8_t attribute_id_46_u8_candidate;
    uint8_t attribute_id_47_u8_candidate;
    uint8_t attribute_id_48_u8_candidate;
    uint8_t attribute_id_49_u8_candidate;
    uint8_t attribute_id_4a_u8_candidate;
    uint8_t attribute_id_4b_u8_candidate;
    uint8_t attribute_id_4c_u8_candidate;
    uint8_t attribute_id_4d_u8_candidate;
    uint8_t attribute_id_4e_u8_candidate;
    uint8_t attribute_id_4f_u8_candidate;
    uint8_t unknown_byte_050_candidate;
    uint8_t derived_id_inputs_051_candidate;
    uint8_t unknown_bytes_052_053_candidate[2];
    uint8_t derived_id_inputs_054_candidate;
    uint8_t unknown_bytes_055_059_candidate[5];
    uint8_t derived_id_inputs_05a_candidate;
    uint8_t derived_id_inputs_05b_candidate;
    uint8_t derived_id_inputs_05c_candidate;
    uint8_t unknown_byte_05d_candidate;
    uint8_t derived_id_inputs_05e_candidate;
    uint8_t unknown_region_05f_115_candidate[0xb7];
    uint8_t attribute_id_16_u8_secondary_candidate;
    uint8_t attribute_id_17_u8_secondary_candidate;
    uint8_t attribute_id_18_u8_secondary_candidate;
    uint8_t attribute_id_19_u8_secondary_candidate;
    uint8_t attribute_id_1a_u8_secondary_candidate;
    uint8_t attribute_id_1b_u8_secondary_candidate;
    uint8_t attribute_id_1c_u8_secondary_candidate;
    uint8_t attribute_id_1d_u8_secondary_candidate;
    uint8_t attribute_id_1e_u8_secondary_candidate;
    uint8_t attribute_id_1f_u8_secondary_candidate;
    uint8_t attribute_id_20_u8_secondary_candidate;
    uint8_t attribute_id_21_u8_secondary_candidate;
    uint8_t attribute_id_22_u8_secondary_candidate;
    uint8_t attribute_id_23_u8_secondary_candidate;
    uint8_t attribute_id_24_u8_secondary_candidate;
    uint8_t attribute_id_25_u8_secondary_candidate;
    uint8_t attribute_id_26_u8_secondary_candidate;
    uint8_t attribute_id_27_u8_secondary_candidate;
    uint8_t attribute_id_28_u8_secondary_candidate;
    uint8_t attribute_id_29_u8_secondary_candidate;
    uint8_t attribute_id_2a_u8_secondary_candidate;
    uint8_t attribute_id_2b_u8_secondary_candidate;
} NestedAttributeBlockCandidate;

_Static_assert(offsetof(NestedAttributeBlockCandidate, attribute_id_00_s16_candidate) == 0x00,
               "nested attribute ID 0x00 signed halfword offset");
_Static_assert(offsetof(NestedAttributeBlockCandidate, attribute_id_15_s16_candidate) == 0x2a,
               "nested attribute ID 0x15 signed halfword offset");
_Static_assert(offsetof(NestedAttributeBlockCandidate, attribute_id_2c_u8_candidate) == 0x2c,
               "nested attribute ID 0x2c byte offset");
_Static_assert(offsetof(NestedAttributeBlockCandidate, attribute_id_4f_u8_candidate) == 0x4f,
               "nested attribute ID 0x4f byte offset");
_Static_assert(offsetof(NestedAttributeBlockCandidate, derived_id_inputs_051_candidate) == 0x51,
               "nested derived input byte +0x51");
_Static_assert(offsetof(NestedAttributeBlockCandidate, derived_id_inputs_054_candidate) == 0x54,
               "nested derived input byte +0x54");
_Static_assert(offsetof(NestedAttributeBlockCandidate, derived_id_inputs_05a_candidate) == 0x5a,
               "nested derived input byte +0x5a");
_Static_assert(offsetof(NestedAttributeBlockCandidate, derived_id_inputs_05b_candidate) == 0x5b,
               "nested derived input byte +0x5b");
_Static_assert(offsetof(NestedAttributeBlockCandidate, derived_id_inputs_05c_candidate) == 0x5c,
               "nested derived input byte +0x5c");
_Static_assert(offsetof(NestedAttributeBlockCandidate, derived_id_inputs_05e_candidate) == 0x5e,
               "nested derived input byte +0x5e");
_Static_assert(offsetof(NestedAttributeBlockCandidate, attribute_id_16_u8_secondary_candidate) == 0x116,
               "nested attribute ID 0x16 secondary byte offset");
_Static_assert(offsetof(NestedAttributeBlockCandidate, attribute_id_2b_u8_secondary_candidate) == 0x12b,
               "nested attribute ID 0x2b secondary byte offset");
_Static_assert(sizeof(NestedAttributeBlockCandidate) == 0x12c,
               "minimum observed nested attribute block extent");

_Static_assert(offsetof(AttributeContextContainerCandidate, preferred_context_candidate) == 0x08,
               "preferred attribute context pointer offset");
_Static_assert(offsetof(AttributeContextContainerCandidate, fallback_context_a_candidate) == 0x20,
               "first fallback context pointer offset");
_Static_assert(offsetof(AttributeContextContainerCandidate, fallback_context_b_candidate) == 0x28,
               "second fallback context pointer offset");
_Static_assert(sizeof(AttributeContextContainerCandidate) == 0x30,
               "minimum observed attribute context container extent");

/* Subject data referenced at container+0; only ranking/context fields are known. */
typedef struct SubjectAttributeDataCandidate {
    uint8_t unknown_000_06f_candidate[0x70];
    uint32_t selector_and_flags_070_candidate;
    uint8_t unknown_074_0a1_candidate[0x2e];
    int8_t category_a2_candidate;
} SubjectAttributeDataCandidate;

_Static_assert(offsetof(SubjectAttributeDataCandidate, selector_and_flags_070_candidate) == 0x70,
               "subject selector/flags word offset");
_Static_assert(offsetof(SubjectAttributeDataCandidate, category_a2_candidate) == 0xa2,
               "signed category byte offset");
_Static_assert(sizeof(SubjectAttributeDataCandidate) >= 0xa3,
               "minimum observed subject data extent");

/* Byte-oriented record populated by player_attribute_property_decode and
 * accessed through attribute_record_value_get/set. This is not the full player. */
typedef struct AttributeRecordCandidate {
    uint8_t rank;
    uint8_t contact_left;
    uint8_t contact_right;
    uint8_t power_left;
    uint8_t power_right;
    uint8_t batting_clutch;
    uint8_t bunting_ability;
    uint8_t drag_bunting_ability;
    uint8_t plate_vision;
    uint8_t plate_discipline;
    uint8_t unknown_byte_00a_candidate;
    uint8_t durability;
    uint8_t speed;
    uint8_t base_stealing;
    uint8_t baserunning_ability;
    uint8_t arm_strength;
    uint8_t arm_accuracy;
    uint8_t fielding_ability;
    uint8_t reaction_time;
    uint8_t reaction_time_right;
    uint8_t reaction_time_forward;
    uint8_t reaction_time_back;
    uint8_t blocking;
    uint8_t pop_time;
    uint8_t unknown_region_018_023_candidate[0x0c];
    int8_t derived_signed_values_024_026_candidate[3];
    uint8_t unknown_byte_027_candidate;
    uint8_t stamina;
    uint8_t pitching_clutch;
    uint8_t hits_per_bf;
    uint8_t hits_per_bf_right;
    uint8_t hr_per_bf;
    uint8_t k_per_bf;
    uint8_t k_per_bf_right;
    uint8_t bb_per_bf;
    uint8_t unknown_region_030_035_candidate[6];
    uint8_t pitch_velocity;
    uint8_t pitch_1_velocity;
    uint8_t pitch_2_velocity;
    uint8_t pitch_3_velocity;
    uint8_t pitch_4_velocity;
    uint8_t pitch_5_velocity;
    uint8_t pitch_movement;
    uint8_t pitch_1_movement;
    uint8_t pitch_2_movement;
    uint8_t pitch_3_movement;
    uint8_t pitch_4_movement;
    uint8_t pitch_5_movement;
    uint8_t unknown_region_042_047_candidate[6];
    uint8_t pitch0_type;
    uint8_t pitch1_type;
    uint8_t pitch2_type;
    uint8_t pitch3_type;
    uint8_t pitch4_type;
    uint8_t pitch5_type;
} AttributeRecordCandidate;

_Static_assert(offsetof(AttributeRecordCandidate, rank) == 0x00, "rank offset");
_Static_assert(offsetof(AttributeRecordCandidate, contact_left) == 0x01, "contact_left offset");
_Static_assert(offsetof(AttributeRecordCandidate, derived_signed_values_024_026_candidate) == 0x24, "derived input triplet offset");
_Static_assert(offsetof(AttributeRecordCandidate, stamina) == 0x28, "stamina offset");
_Static_assert(offsetof(AttributeRecordCandidate, pitch_velocity) == 0x36, "pitch velocity offset");
_Static_assert(offsetof(AttributeRecordCandidate, pitch_movement) == 0x3c, "pitch movement offset");
_Static_assert(offsetof(AttributeRecordCandidate, pitch0_type) == 0x48, "pitch0_type offset");
_Static_assert(offsetof(AttributeRecordCandidate, pitch5_type) == 0x4d, "pitch5_type offset");
_Static_assert(sizeof(AttributeRecordCandidate) == 0x4e, "minimum observed attribute record extent");

/* Owner fragment read by attribute_record_pointer_or_default. */
typedef struct AttributeRecordProviderCandidate {
    uint8_t unknown_prefix_000_047_candidate[0x48];
    AttributeRecordCandidate *attribute_record_048_candidate;
} AttributeRecordProviderCandidate;

_Static_assert(offsetof(AttributeRecordProviderCandidate, attribute_record_048_candidate) == 0x48,
               "attribute record provider pointer offset");
_Static_assert(sizeof(AttributeRecordProviderCandidate) == 0x50,
               "minimum attribute record provider extent");

#endif
