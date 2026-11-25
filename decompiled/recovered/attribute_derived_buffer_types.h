#ifndef MLBTS_ATTRIBUTE_DERIVED_BUFFER_TYPES_H
#define MLBTS_ATTRIBUTE_DERIVED_BUFFER_TYPES_H
#include <stdint.h>
/* Partial owner/holder views used by f_70010e22d0. */
typedef struct AttributeDerivedBufferOwnerCandidate {
    uint8_t unknown_000_027[0x28];
    void *attribute_source_holder_028_candidate; /* +0x28 */
} AttributeDerivedBufferOwnerCandidate;
typedef struct AttributeSourceHolderCandidate {
    uint8_t unknown_000_007[8];
    void *player_attribute_record_008_candidate; /* +0x08 */
} AttributeSourceHolderCandidate;
#endif
