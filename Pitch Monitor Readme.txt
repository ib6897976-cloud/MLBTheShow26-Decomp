MLBTS PITCH SPEED VALUE SCANNER

1. Start the recomp and get into a game.
2. Double-click "Run Pitch Monitor.bat".
3. Enter the known pitch speed shown by the game. The initial scan finds that
   float across writable guest memory. When an address lines up with a pitch
   record's +0x454/+0x458 field, the console also shows its record context.
4. Throw a pitch with a different known speed, then enter that mph to filter
   the saved addresses. Repeat with more pitches until few addresses remain.
5. When one address remains, check its pitch-record context, then type w to
   watch it. The monitor reports break only while the inferred actor record is
   active and its position/aim fields are initialized.

The default matching tolerance is +/- 0.10 mph. You can change it at the
prompt. The initial scan reports progress every 64 MiB; later filters only
reread the saved addresses. Use different speeds to narrow the list. A raw
float match without an active actor flag is not a confirmed pitch pointer; keep
narrowing with another known speed. Break is current position (+0x420) minus
aimed position (+0x42c), in world units; it is measured movement, not the
internal force vector.

This read-only scanner targets the current extracted recomp and may need offset
updates after a game build change. The Windows "py" launcher must be on PATH.
