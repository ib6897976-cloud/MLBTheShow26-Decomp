#ifndef MLBTS_RANKED_METRIC_CACHE_TYPES_H
#define MLBTS_RANKED_METRIC_CACHE_TYPES_H
#include <stdint.h>
/* Partial per-category record used by f_7000e9bfe0. */
typedef struct RankedMetricRecordCandidate {
    uint8_t unknown_000_003[4];
    uint32_t metric_kind_004_candidate; /* +0x04 */
    float metric_float_008_candidate; /* +0x08 */
    uint8_t unknown_00c_2f7[0x2ec];
    void *metric_cache_head_2f8_candidate; /* +0x2f8 */
    uint64_t metric_cache_count_300_candidate; /* +0x300 */
} RankedMetricRecordCandidate;
/* Allocated as 0x190 bytes; only list links/key are labeled. */
typedef struct RankedMetricCacheNodeCandidate {
    void *link_000_candidate; /* +0x00 */
    void *link_008_candidate; /* +0x08 */
    uint8_t unknown_010_01b[0x0c];
    uint16_t category_key_01c_candidate; /* +0x1c */
    uint8_t unknown_01e_18f[0x172];
} RankedMetricCacheNodeCandidate;
#endif
