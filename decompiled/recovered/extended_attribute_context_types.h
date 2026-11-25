#ifndef MLBTS_EXTENDED_ATTRIBUTE_CONTEXT_TYPES_H
#define MLBTS_EXTENDED_ATTRIBUTE_CONTEXT_TYPES_H

#include <stddef.h>
#include <stdint.h>

/* Sparse view of raw halfword operands used by two separate derived-metric
 * dispatchers. Signedness is applied by individual calculations, not baked
 * into this storage declaration. This is distinct from the compact primary
 * PlayerAttributeBlockCandidate. */
typedef struct __attribute__((packed)) ExtendedAttributeContextCandidate {
    uint16_t raw_halfword_000_candidate;
    uint16_t raw_halfword_002_candidate;
    uint16_t raw_halfword_004_candidate;
    uint16_t raw_halfword_006_candidate;
    uint16_t raw_halfword_008_candidate;
    uint16_t raw_halfword_00a_candidate;
    uint16_t raw_halfword_00c_candidate;
    uint16_t raw_halfword_00e_candidate;
    uint8_t unknown_010_015_candidate[0x6];
    uint16_t raw_halfword_016_candidate;
    uint8_t unknown_018_01b_candidate[0x4];
    uint16_t raw_halfword_01c_candidate;
    uint16_t raw_halfword_01e_candidate;
    uint8_t unknown_020_023_candidate[0x4];
    uint16_t raw_halfword_024_candidate;
    uint16_t raw_halfword_026_candidate;
    uint8_t unknown_028_02b_candidate[0x4];
    uint16_t raw_halfword_02c_candidate;
    uint16_t raw_halfword_02e_candidate;
    uint16_t raw_halfword_030_candidate;
    uint16_t raw_halfword_032_candidate;
    uint16_t raw_halfword_034_candidate;
    uint16_t raw_halfword_036_candidate;
    uint8_t unknown_038_03b_candidate[0x4];
    uint16_t raw_halfword_03c_candidate;
    uint16_t raw_halfword_03e_candidate;
    uint8_t unknown_040_07b_candidate[0x3c];
    uint16_t raw_halfword_07c_candidate;
    uint8_t unknown_07e_083_candidate[0x6];
    uint16_t raw_halfword_084_candidate;
    uint16_t raw_halfword_086_candidate;
    uint8_t unknown_088_097_candidate[0x10];
    uint16_t raw_halfword_098_candidate;
    uint8_t unknown_09a_09d_candidate[0x4];
    uint16_t raw_halfword_09e_candidate;
    uint8_t unknown_0a0_0a3_candidate[0x4];
    uint16_t raw_halfword_0a4_candidate;
    uint8_t unknown_0a6_0a7_candidate[0x2];
    uint16_t raw_halfword_0a8_candidate;
    uint16_t raw_halfword_0aa_candidate;
    uint16_t raw_halfword_0ac_candidate;
    uint16_t raw_halfword_0ae_candidate;
    uint16_t raw_halfword_0b0_candidate;
    uint16_t raw_halfword_0b2_candidate;
    uint16_t raw_halfword_0b4_candidate;
    uint16_t raw_halfword_0b6_candidate;
    uint8_t unknown_0b8_0b9_candidate[0x2];
    uint16_t raw_halfword_0ba_candidate;
    uint16_t raw_halfword_0bc_candidate;
    uint16_t raw_halfword_0be_candidate;
    uint8_t unknown_0c0_0cd_candidate[0xe];
    uint16_t raw_halfword_0ce_candidate;
    uint16_t raw_halfword_0d0_candidate;
    uint16_t raw_halfword_0d2_candidate;
    uint8_t unknown_0d4_0e5_candidate[0x12];
    uint16_t raw_halfword_0e6_candidate;
    uint8_t unknown_0e8_0f1_candidate[0xa];
    uint16_t raw_halfword_0f2_candidate;
    uint8_t unknown_0f4_117_candidate[0x24];
    uint16_t raw_halfword_118_candidate;
    uint16_t raw_halfword_11a_candidate;
    uint16_t raw_halfword_11c_candidate;
    uint8_t unknown_11e_123_candidate[0x6];
    uint16_t raw_halfword_124_candidate;
    uint8_t unknown_126_12f_candidate[0xa];
    uint16_t raw_halfword_130_candidate;
    uint16_t raw_halfword_132_candidate;
    uint16_t raw_halfword_134_candidate;
} ExtendedAttributeContextCandidate;

_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_000_candidate) == 0x0, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_002_candidate) == 0x2, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_004_candidate) == 0x4, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_006_candidate) == 0x6, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_008_candidate) == 0x8, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_00a_candidate) == 0xa, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_00c_candidate) == 0xc, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_00e_candidate) == 0xe, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_016_candidate) == 0x16, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_01c_candidate) == 0x1c, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_01e_candidate) == 0x1e, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_024_candidate) == 0x24, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_026_candidate) == 0x26, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_02c_candidate) == 0x2c, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_02e_candidate) == 0x2e, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_030_candidate) == 0x30, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_032_candidate) == 0x32, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_034_candidate) == 0x34, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_036_candidate) == 0x36, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_03c_candidate) == 0x3c, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_03e_candidate) == 0x3e, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_07c_candidate) == 0x7c, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_084_candidate) == 0x84, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_086_candidate) == 0x86, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_098_candidate) == 0x98, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_09e_candidate) == 0x9e, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_0a4_candidate) == 0xa4, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_0a8_candidate) == 0xa8, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_0aa_candidate) == 0xaa, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_0ac_candidate) == 0xac, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_0ae_candidate) == 0xae, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_0b0_candidate) == 0xb0, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_0b2_candidate) == 0xb2, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_0b4_candidate) == 0xb4, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_0b6_candidate) == 0xb6, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_0ba_candidate) == 0xba, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_0bc_candidate) == 0xbc, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_0be_candidate) == 0xbe, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_0ce_candidate) == 0xce, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_0d0_candidate) == 0xd0, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_0d2_candidate) == 0xd2, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_0e6_candidate) == 0xe6, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_0f2_candidate) == 0xf2, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_118_candidate) == 0x118, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_11a_candidate) == 0x11a, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_11c_candidate) == 0x11c, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_124_candidate) == 0x124, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_130_candidate) == 0x130, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_132_candidate) == 0x132, "observed raw halfword offset");
_Static_assert(offsetof(ExtendedAttributeContextCandidate, raw_halfword_134_candidate) == 0x134, "observed raw halfword offset");
_Static_assert(sizeof(ExtendedAttributeContextCandidate) == 0x136,
               "maximum observed derived operand extent");

#endif
