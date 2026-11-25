#ifndef MLBTS_PLAYER_ATTRIBUTE_COMPONENT_OWNER_TYPES_H
#define MLBTS_PLAYER_ATTRIBUTE_COMPONENT_OWNER_TYPES_H

#include <stddef.h>
#include <stdint.h>

/* Minimal owner view shared by bulk attribute routines. Other regions remain
 * opaque; the collection at +0x50 is consumed by a helper, not decoded here. */
typedef struct __attribute__((packed)) PlayerAttributeComponentOwnerCandidate {
    uint8_t unknown_000_547_candidate[0x548];
    void *optional_component_setting_548_candidate;
} PlayerAttributeComponentOwnerCandidate;

_Static_assert(offsetof(PlayerAttributeComponentOwnerCandidate, optional_component_setting_548_candidate) == 0x548,
               "optional component setting pointer offset");
_Static_assert(sizeof(PlayerAttributeComponentOwnerCandidate) == 0x550,
               "minimum observed owner extent");

#endif
