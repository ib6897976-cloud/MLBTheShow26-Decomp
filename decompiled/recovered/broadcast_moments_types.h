#ifndef MLBTS_RECOVERED_BROADCAST_MOMENTS_TYPES_H
#define MLBTS_RECOVERED_BROADCAST_MOMENTS_TYPES_H

#include <stddef.h>
#include <stdint.h>

/* Entry stride and field widths are confirmed; source player-field meanings remain candidates.
   The shared 0x30-byte reset helper also serves other record arrays. */
typedef struct LeagueLeaderEntryCandidate {
    uint8_t candidate_flag_000;
    uint8_t opaque_player_bytes_001_010_candidate[0x10];
    uint8_t opaque_player_bytes_011_020_candidate[0x10];
    uint8_t unknown_021_023_candidate[3];
    float leader_metric_024_candidate;
    uint16_t player_identifier_028_candidate;
    uint8_t player_source_byte_a2_02a_candidate;
    uint8_t unknown_02b_candidate;
    uint8_t player_source_byte_70_02c_candidate;
    uint8_t unknown_02d_02f_candidate[3];
} LeagueLeaderEntryCandidate;

_Static_assert(sizeof(LeagueLeaderEntryCandidate) == 0x30, "leader entry stride");
_Static_assert(offsetof(LeagueLeaderEntryCandidate, opaque_player_bytes_001_010_candidate) == 0x01,
               "first opaque player payload offset");
_Static_assert(offsetof(LeagueLeaderEntryCandidate, opaque_player_bytes_011_020_candidate) == 0x11,
               "second opaque player payload offset");
_Static_assert(offsetof(LeagueLeaderEntryCandidate, leader_metric_024_candidate) == 0x24,
               "leader metric offset");
_Static_assert(offsetof(LeagueLeaderEntryCandidate, player_identifier_028_candidate) == 0x28,
               "player identifier offset");
_Static_assert(offsetof(LeagueLeaderEntryCandidate, player_source_byte_a2_02a_candidate) == 0x2a,
               "player source byte offset");
_Static_assert(offsetof(LeagueLeaderEntryCandidate, player_source_byte_70_02c_candidate) == 0x2c,
               "leader player source byte offset");

/* Temporary sort elements from the secondary ranked-row refresh. */
typedef struct RankedScratchRecordCandidate {
    void *player_record_candidate;
    float sort_metric_candidate;
    uint8_t unknown_00c_candidate[4];
} RankedScratchRecordCandidate;

_Static_assert(sizeof(RankedScratchRecordCandidate) == 0x10, "ranked scratch record stride");
_Static_assert(offsetof(RankedScratchRecordCandidate, sort_metric_candidate) == 0x08,
               "ranked scratch metric offset");
_Static_assert(offsetof(RankedScratchRecordCandidate, unknown_00c_candidate) == 0x0c,
               "ranked scratch trailing bytes offset");

/* Header consumed by a shared bounds-checked lookup for 0x550-stride records. */
typedef struct StridedRecordTableHeaderCandidate {
    uint8_t unknown_000_007_candidate[8];
    void *records_base_candidate;
    uint8_t unknown_010_03b_candidate[0x2c];
    uint32_t record_count_candidate;
} StridedRecordTableHeaderCandidate;

_Static_assert(offsetof(StridedRecordTableHeaderCandidate, records_base_candidate) == 0x08,
               "strided record table base pointer offset");
_Static_assert(offsetof(StridedRecordTableHeaderCandidate, record_count_candidate) == 0x3c,
               "strided record table count offset");
_Static_assert(sizeof(StridedRecordTableHeaderCandidate) == 0x40,
               "minimum observed record table header extent");

/* Partial shell through the observed leader-list region; not the complete moments object. */
typedef struct BroadcastMomentsCandidate {
    uint8_t unknown_000_1b0b7_candidate[0x1b0b8];
    LeagueLeaderEntryCandidate league_leader_rows_candidate[4][23][10];
} BroadcastMomentsCandidate;

_Static_assert(offsetof(BroadcastMomentsCandidate, league_leader_rows_candidate) == 0x1b0b8,
               "leader list storage offset");
_Static_assert(sizeof(BroadcastMomentsCandidate) == 0x25d38,
               "minimum observed moments object extent");

#endif
