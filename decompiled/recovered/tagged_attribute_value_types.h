#ifndef MLBTS_TAGGED_ATTRIBUTE_VALUE_TYPES_H
#define MLBTS_TAGGED_ATTRIBUTE_VALUE_TYPES_H
#include <stdint.h>
/* Raw tag-dispatched view; field meanings and total extent are unresolved. */
typedef struct TaggedAttributeValueCandidate {
    uint16_t value_kind_000_candidate; /* +0x00 */
    uint8_t tag_002_candidate; /* +0x02 */
    uint8_t flag_003_candidate; /* +0x03 */
    uint8_t unknown_004_01b[0x18];
    int8_t attribute_selector_01c_candidate; /* +0x1c */
    int8_t nested_attribute_selector_01d_candidate; /* +0x1d */
    uint8_t attribute_option_01e_candidate; /* +0x1e */
    uint8_t unknown_01f;
    uint32_t attribute_numeric_payload_020_candidate; /* +0x20 */
} TaggedAttributeValueCandidate;
#endif
