#ifndef MLBTS_ATTRIBUTE_DERIVED_RECORD_TYPES_H
#define MLBTS_ATTRIBUTE_DERIVED_RECORD_TYPES_H
#include <stdint.h>
/* Minimal output view; only pointer write at +0x08 is established. */
typedef struct AttributeDerivedRecordCandidate {
    uint8_t unknown_000_007[8];
    void *derived_record_pointer_008_candidate; /* +0x08 */
} AttributeDerivedRecordCandidate;
#endif
