#ifndef MLBTS_PLAYER_ATTRIBUTE_SEARCH_RESULT_TYPES_H
#define MLBTS_PLAYER_ATTRIBUTE_SEARCH_RESULT_TYPES_H
#include <stdint.h>
/* Partial output view; function writes/clears fields through at least +0x6a8c. */
typedef struct PlayerAttributeSearchMetricsResultCandidate {
    void *attribute_context_pointer_000_candidate; /* +0x00 */
    uint8_t unknown_008_6a8b[0x6a84];
} PlayerAttributeSearchMetricsResultCandidate;
#endif
