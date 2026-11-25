/*
 * Partial hit record reconstruction from current-build access patterns.
 * The external comparison map is v1.0.15; current meanings are cross-checked
 * against generated code but remain candidates. Unknown bytes stay reserved.
 * Documentation model only; generated recomp C does not include this file.
 */
#pragma once

#include <stddef.h>
#include <stdint.h>

/* Enum labels/order follow the v1.0.15 public code map. Current-build
 * f_7001679b2c writes categories 6-10 to record+0x08; f_7001677ca0 writes
 * BUNT (18). Thus these numeric values are current-build-confirmed, while
 * labels other than BUNT remain cross-version candidate meanings. */
typedef enum HitTypeCandidate {
    HIT_TYPE_MISSED_EARLY = 0,
    HIT_TYPE_MISSED_INSIDE = 1,
    HIT_TYPE_MISSED_BELOW = 2,
    HIT_TYPE_TIP_BACKSTOP = 3,
    HIT_TYPE_POPUP_BACKWARD = 4,
    HIT_TYPE_POPUP_FORWARD = 5,
    HIT_TYPE_HIGH_FLY = 6,
    HIT_TYPE_MEDIUM_FLYBALL = 7,
    HIT_TYPE_LINE_DRIVE = 8,
    HIT_TYPE_HARD_GROUNDER = 9,
    HIT_TYPE_EASY_GROUNDER = 10,
    HIT_TYPE_CHOPPER = 11,
    HIT_TYPE_DRIBBLER = 12,
    HIT_TYPE_TIP_CATCHER = 13,
    HIT_TYPE_MISSED_OVER = 14,
    HIT_TYPE_MISSED_OUTSIDE = 15,
    HIT_TYPE_MISSED_LATE = 16,
    HIT_TYPE_CORKSCREW = 17,
    HIT_TYPE_BUNT = 18
} HitTypeCandidate;
_Static_assert(sizeof(HitTypeCandidate) == 4, "hit type storage width");

typedef struct HitRecordCandidate {
    uint8_t unknown_000[0x08];
    HitTypeCandidate hit_type_candidate;            /* +0x08 */
    uint32_t precomputed_result_category_00c_candidate; /* +0x0c */
    uint8_t unknown_010[0x08];
    float unknown_f32_18;                           /* +0x18 */
    float contact_rating_late_inside_candidate;     /* +0x1c */
    float contact_rating_early_outside_candidate;  /* +0x20 */
    uint8_t unknown_024[0x04];
    float scaled_hit_vector_components_candidate[3]; /* +0x28/+0x2c/+0x30; axis meanings unresolved */
    uint8_t unknown_034[0x0c];
    float unknown_f32_40_candidate;                 /* +0x40, precomputed-path input */
    float unknown_f32_44_candidate;                 /* +0x44, precomputed-path input */
    float power_mph_candidate;                      /* +0x48 */
    uint16_t perfect_pci_flag_candidate;            /* +0x4c */
    uint16_t perfect_timing_flag_candidate;         /* +0x4e */
    uint8_t bunt_marker_flag_candidate;              /* +0x50 */
    uint8_t bunt_control_bit_candidate;              /* +0x51 */
    uint8_t power_adjustment_condition_52_candidate; /* +0x52; boolean-like */
    uint8_t power_adjustment_condition_53_candidate; /* +0x53; boolean-like */
    uint8_t unknown_flag_54_candidate;               /* +0x54 */
} HitRecordCandidate;

_Static_assert(offsetof(HitRecordCandidate, hit_type_candidate) == 0x08, "hit type offset");
_Static_assert(offsetof(HitRecordCandidate, contact_rating_late_inside_candidate) == 0x1c, "hit rating offset");
_Static_assert(offsetof(HitRecordCandidate, scaled_hit_vector_components_candidate) == 0x28, "hit vector components offset");
_Static_assert(offsetof(HitRecordCandidate, unknown_f32_40_candidate) == 0x40, "hit record +0x40 float offset");
_Static_assert(offsetof(HitRecordCandidate, unknown_f32_44_candidate) == 0x44, "hit record +0x44 float offset");
_Static_assert(offsetof(HitRecordCandidate, power_mph_candidate) == 0x48, "hit power offset");
_Static_assert(offsetof(HitRecordCandidate, perfect_pci_flag_candidate) == 0x4c, "hit PCI result offset");
_Static_assert(offsetof(HitRecordCandidate, bunt_marker_flag_candidate) == 0x50, "hit bunt marker offset");
_Static_assert(offsetof(HitRecordCandidate, power_adjustment_condition_52_candidate) == 0x52, "hit power condition 52 offset");
_Static_assert(offsetof(HitRecordCandidate, power_adjustment_condition_53_candidate) == 0x53, "hit power condition 53 offset");
_Static_assert(offsetof(HitRecordCandidate, unknown_flag_54_candidate) == 0x54, "hit unknown flag offset");
