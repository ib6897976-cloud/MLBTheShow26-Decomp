# Task context state processing

`process_task_context_state` (`0x700090efc0`) reads context/status flags, scans
an indexed global entry set, assembles temporary record state, reconciles packed
selectors, and performs additional state updates. Two caller paths are observed:
`f_7000902184` calls it after task/phase checks, while `f_700091a208` calls it
and returns success. Static metadata associates strings `EQUIPMENT_ATTRIBUTE_VALUE`
and `task[%d].reward_xp_amount` with this address, but the body does not directly
connect those strings to a specific field or branch. Keep its exact domain role
and structure names unresolved. Evidence: `main_0065.c:44552-45360`, callers
`main_0065.c:29581-29607` and `main_0066.c:4028-4038`.


`process_end_game_pitcher_state` (`0x7000f35764`) is tied by exact rodata to
`EndGamePitchers` and performs mode/status-gated context updates, including a
terminal branch that copies a table value and clears state bytes. The precise
statistical role and object layout remain unknown (`main_0109.c:20359-20487`).


`build_postgame_player_and_team_summary` (`0x7000f04ef0`) builds and copies a
player/team summary record using player status and attribute reads. Exact
strings include `EndGamePitchers`, `OPP_NAME`, and `league_games`; whether this
formats or persists the result is unclear (`main_0108.c:15224-16919`).

`record_league_game_attribute_metrics` (`0x7000c0c7a0`) processes a
league-game record with attribute metric and context helpers. The exact string
`league_games` is present, but the update/report role is unknown
(`main_0083.c:48453-48907`).
