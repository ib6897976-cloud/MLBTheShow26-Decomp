#ifndef MLBTS_ATTRIBUTE_ADJUSTMENT_DESCRIPTOR_TYPES_H
#define MLBTS_ATTRIBUTE_ADJUSTMENT_DESCRIPTOR_TYPES_H
#include <stdint.h>
/* Raw 32-bit values passed by the descriptor caller; semantics unknown. */
typedef struct AttributeAdjustmentDescriptorCandidate {
    uint8_t unknown_000_00b[0x0c];
    uint32_t raw_value_0c_candidate; /* +0x0c */
    uint8_t unknown_010_013[4];
    uint32_t raw_value_14_candidate; /* +0x14 */
    uint32_t raw_value_18_candidate; /* +0x18 */
    uint32_t raw_value_1c_candidate; /* +0x1c */
    uint32_t raw_value_20_candidate; /* +0x20 */
    uint32_t raw_value_24_candidate; /* +0x24 */
    uint32_t raw_value_28_candidate; /* +0x28 */
    uint32_t raw_value_2c_candidate; /* +0x2c */
    uint32_t raw_value_30_candidate; /* +0x30 */
    uint32_t raw_value_34_candidate; /* +0x34 */
    uint32_t raw_value_38_candidate; /* +0x38 */
} AttributeAdjustmentDescriptorCandidate;
#endif
