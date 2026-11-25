#ifndef MLBTS_MUTABLE_TEXT_BUFFER_TYPES_H
#define MLBTS_MUTABLE_TEXT_BUFFER_TYPES_H
#include <stdint.h>
/* Mutable {pointer,length} descriptor observed in one parser path. */
typedef struct MutableTextBufferDescriptorCandidate {
    char *buffer_pointer_000_candidate; /* +0x00 */
    uint32_t buffer_length_008_candidate; /* +0x08 */
    uint32_t unknown_00c;
} MutableTextBufferDescriptorCandidate;
#endif
