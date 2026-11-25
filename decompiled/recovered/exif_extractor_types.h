#ifndef MLBTS_RECOVERED_EXIF_EXTRACTOR_TYPES_H
#define MLBTS_RECOVERED_EXIF_EXTRACTOR_TYPES_H

#include <stddef.h>
#include <stdint.h>

/* Partial layout from the SDK constructor, SetExifData, Analyze, and accessors. */
typedef struct ExifExtractorCandidate {
    const void *vtable_candidate;       /* +0x00; constructor writes SDK vtable */
    uint32_t analyzed_flag;             /* +0x08; ctor clears, SetExifData sets */
    uint32_t padding_00c;
    void *work_buffer;                  /* +0x10; constructor argument */
    const void *exif_data;              /* +0x18; SetExifData argument */
    uint16_t exif_data_size_candidate;  /* +0x20; SetExifData truncates length to 16 bits */
    uint8_t padding_022[6];
} ExifExtractorCandidate;

_Static_assert(offsetof(ExifExtractorCandidate, analyzed_flag) == 0x08, "analyzed flag offset");
_Static_assert(offsetof(ExifExtractorCandidate, work_buffer) == 0x10, "work buffer offset");
_Static_assert(offsetof(ExifExtractorCandidate, exif_data) == 0x18, "EXIF data offset");
_Static_assert(offsetof(ExifExtractorCandidate, exif_data_size_candidate) == 0x20, "EXIF size offset");
_Static_assert(sizeof(ExifExtractorCandidate) == 0x28, "observed object extent");

#endif
