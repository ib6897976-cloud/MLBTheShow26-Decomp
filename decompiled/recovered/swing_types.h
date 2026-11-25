/*
 * Partial, evidence-backed swing/pitch geometry layouts for the current build.
 * Documentation model only; generated recomp code does not include this file.
 * Unobserved bytes remain reserved, and these are not complete object sizes.
 */
#pragma once

#include <stddef.h>
#include <stdint.h>

typedef struct SwingRecordCandidate {
    uint8_t unknown_000[0x08];
    float pci_x;                         /* +0x08 */
    float pci_y;                         /* +0x0c */
    float aim_error_x;                   /* +0x10 */
    float aim_error_y;                   /* +0x14 */
    uint8_t unknown_018[0x1c];
    float unknown_f32_034_candidate;     /* +0x34, written during contact resolution */
    float unknown_f32_038_candidate;     /* +0x38, written during contact resolution */
    uint8_t unknown_03c[0x24];
    float pci_inner_size_candidate;      /* +0x60 */
    float pci_outer_size_candidate;      /* +0x64 */
    uint8_t unknown_068[0x1c];
    uint8_t contact_state_flag_084_candidate; /* +0x84 */
    uint8_t unknown_085[0x02];
    uint8_t contact_state_flag_087_candidate; /* +0x87 */
    uint8_t unknown_088[0x90];
    float aim_error_length;              /* +0x118 */
    float unknown_f32_11c_candidate;     /* +0x11c, contact evaluator input */
    float unknown_f32_120_candidate;     /* +0x120, contact evaluator input */
    uint8_t unknown_124[0x3c];
    float unknown_f32_160_candidate;     /* +0x160, clamped/compared in contact resolution */
} SwingRecordCandidate;

typedef struct PitchTrajectoryStateCandidate {
    uint8_t unknown_000[0x148];
    float plate_crossing_x_candidate;    /* +0x148 */
    float plate_crossing_y_candidate;    /* +0x14c */
} PitchTrajectoryStateCandidate;

_Static_assert(offsetof(SwingRecordCandidate, unknown_f32_034_candidate) == 0x34, "swing contact float 0x34 offset");
_Static_assert(offsetof(SwingRecordCandidate, unknown_f32_038_candidate) == 0x38, "swing contact float 0x38 offset");
_Static_assert(offsetof(SwingRecordCandidate, contact_state_flag_084_candidate) == 0x84, "swing contact flag 0x84 offset");
_Static_assert(offsetof(SwingRecordCandidate, contact_state_flag_087_candidate) == 0x87, "swing contact flag 0x87 offset");
_Static_assert(offsetof(SwingRecordCandidate, unknown_f32_11c_candidate) == 0x11c, "swing contact float 0x11c offset");
_Static_assert(offsetof(SwingRecordCandidate, unknown_f32_120_candidate) == 0x120, "swing contact float 0x120 offset");
_Static_assert(offsetof(SwingRecordCandidate, unknown_f32_160_candidate) == 0x160, "swing contact float 0x160 offset");
_Static_assert(offsetof(SwingRecordCandidate, pci_x) == 0x08, "swing PCI offset");
_Static_assert(offsetof(SwingRecordCandidate, pci_inner_size_candidate) == 0x60, "swing PCI size offset");
_Static_assert(offsetof(SwingRecordCandidate, aim_error_length) == 0x118, "swing error length offset");
_Static_assert(offsetof(PitchTrajectoryStateCandidate, plate_crossing_x_candidate) == 0x148, "pitch crossing offset");
