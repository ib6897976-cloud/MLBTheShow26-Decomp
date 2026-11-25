# Wave 65 exact tail-call batch QA

- Proposals examined: 4,152
- Unique addresses: 4,152
- Mechanical checks: PASS (0 mismatches)
- Independent manual spot sample: 50 functions; all inspected bodies have FN_ENTER followed only by one musttail forwarding statement.
- Generated C chunks represented: 115
- Name targets represented: 14
- No shared TSVs were modified by this QA.

## Forwarding target counts

- `operator delete(void*)`: 4,139
- `initialize_subsystem_if_needed`: 1
- `parse_game_command_line_arguments`: 1
- `initialize_owner_embedded_components`: 1
- `initialize_draft_view_pool`: 1
- `zero_56_byte_subobject`: 1
- `d_player_acc_entry_value_dispatch`: 1
- `decode_player_record_sections`: 1
- `d_player_app_entry_value_dispatch`: 1
- `decode_player_acc_and_app_sections`: 1
- `composite_record_initialize_default_variant`: 1
- `decode_player_profile_sections`: 1
- `player_attribute_delta_apply`: 1
- `player_attribute_delta_remove`: 1

## Spot-sampled addresses

`0x70000c5574`, `0x70017f82dc`, `0x70018053e8`, `0x70017e75dc`, `0x7000c2dfd4`, `0x70017f18ac`, `0x70017e78a4`, `0x70017f19f0`, `0x70017efcd8`, `0x7001847060`, `0x7001205338`, `0x7000c4fd18`, `0x700180b1ec`, `0x70017f1b20`, `0x7000b01758`, `0x7000004838`, `0x70017de3d8`, `0x7000cdbd68`, `0x7001856eac`, `0x7001807970`, `0x70017fa5f0`, `0x70017fb500`, `0x7001217f14`, `0x7000f46878`, `0x7001838488`, `0x7000af32e0`, `0x700133d29c`, `0x7001299ac8`, `0x7001816ffc`, `0x700178b2a0`, `0x70017dfcb4`, `0x70017e8bb4`, `0x7000c39634`, `0x70017d930c`, `0x70017f9150`, `0x70017d71ac`, `0x70018181ec`, `0x700033e6f4`, `0x700181831c`, `0x7001846b40`, `0x70018062a8`, `0x7001805c48`, `0x700189e5b8`, `0x70017e166c`, `0x700143a8a8`, `0x70017f7818`, `0x700180aad8`, `0x70017e1a3c`, `0x70017de7ac`, `0x7001804460`

## Mismatches

None.

## Limits

This verifies the exact lifted forwarding body and the target name evidence, not original source prototypes or object types. The generated labels describe the forwarding wrapper; they are not reconstructed original symbols. The 50-function manual sample supplements the independent full-batch mechanical scan.
