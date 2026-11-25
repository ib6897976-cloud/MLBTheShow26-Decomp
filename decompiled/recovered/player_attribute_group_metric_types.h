#ifndef MLBTS_PLAYER_ATTRIBUTE_GROUP_METRIC_TYPES_H
#define MLBTS_PLAYER_ATTRIBUTE_GROUP_METRIC_TYPES_H

#include <stdint.h>

/*
 * Partial view read by f_700183d480. The enclosing source-level class and
 * total extent are unknown; reserved bytes only preserve observed offsets.
 */
typedef struct PlayerAttributeGroupMetricSubjectCandidate {
    int16_t metric_operand_000_candidate; /* +0x00 */
    uint8_t unknown_002_009[8];
    int16_t metric_operand_00a_candidate; /* +0x0a */
    uint8_t unknown_00c_015[10];
    int16_t metric_operand_016_candidate; /* +0x16 */
    uint8_t unknown_018_04e[0x37];
    uint8_t metric_operand_04f_candidate; /* +0x4f */
    uint8_t unknown_050_052[3];
    uint8_t metric_operand_053_candidate; /* +0x53 */
    uint8_t metric_operand_054_candidate; /* +0x54 */
    uint8_t unknown_055_067[0x13];
    void *nested_metric_context_068_candidate; /* +0x68 */
} PlayerAttributeGroupMetricSubjectCandidate;

#endif
