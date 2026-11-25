#ifndef MLBTS_ATTRIBUTE_RULE_DESCRIPTOR_TYPES_H
#define MLBTS_ATTRIBUTE_RULE_DESCRIPTOR_TYPES_H
#include <stdint.h>
/* Fixed 16-byte descriptor passed to apply_attribute_record_rule.
 * Observed raw kinds: 1..5 have explicit dispatch; kind 2 returns operand_008.
 * Semantic enum names for kinds 1 and 3..5 are not established yet.
 */
typedef struct AttributeRuleDescriptorCandidate {
    uint32_t rule_kind_000_candidate; /* +0x00; observed explicit cases 1..5 */
    uint32_t rule_selector_004_candidate; /* +0x04 */
    uint32_t rule_operand_008_candidate; /* +0x08; returned directly for kind 2 */
    uint32_t rule_selector_00c_candidate; /* +0x0c */
} AttributeRuleDescriptorCandidate;
#endif
