#ifndef MLBTS_ATTRIBUTE_SLOT_REFERENCE_TYPES_H
#define MLBTS_ATTRIBUTE_SLOT_REFERENCE_TYPES_H
#include <stdint.h>
/* Partial views rebuilt by f_7000759650; slot names are unknown. */
typedef struct AttributeSlotReferenceEntryCandidate {
    void *reference_000_candidate; /* +0x00 */
    uint32_t value_008_candidate; /* +0x08 */
    uint32_t unknown_00c; /* +0x0c */
} AttributeSlotReferenceEntryCandidate;
typedef struct AttributeSlotPackedRecordCandidate {
    uint8_t unknown_000_06f[0x70];
    uint32_t packed_selector_070_candidate; /* +0x70 */
    uint32_t packed_flags_074_candidate; /* +0x74 */
} AttributeSlotPackedRecordCandidate;
#endif
