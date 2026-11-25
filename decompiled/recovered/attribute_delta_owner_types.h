#ifndef MLBTS_ATTRIBUTE_DELTA_OWNER_TYPES_H
#define MLBTS_ATTRIBUTE_DELTA_OWNER_TYPES_H
#include <stdint.h>
/* Partial owner view used by f_7000447240; full type unknown. */
typedef struct AttributeDeltaOwnerCandidate {
    void *attribute_context_pointer_000_candidate; /* +0x00 */
    uint8_t unknown_008_02f[0x28];
    void *attribute_provider_pointer_030_candidate; /* +0x30 */
    uint8_t unknown_038_06f[0x38];
    uint32_t packed_selector_070_candidate; /* +0x70 */
} AttributeDeltaOwnerCandidate;
#endif
