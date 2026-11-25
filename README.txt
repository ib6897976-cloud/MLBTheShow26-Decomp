Fastball 0.2.0+74a6525: MLB The Show 26 for PC

Start Fastball.exe. It builds the game on this PC from your own game files, into the MLBTS folder here (or a
folder you pick). Everything stays in this folder: delete it and the port is gone.

You need:
- MLB The Show 26 (NSP) and its 1.0.20 update (NSP; the 1.0.15 update works too), dumped from your own Nintendo
  Switch;
- prod.keys from your own Switch (the setup finds it in Ryujinx's or yuzu's folder by itself);
- about 40 GB free, Windows 10 or 11 (64-bit), a CPU with AVX2 and a graphics card with Vulkan 1.3.

No game files, keys or code of the game are in this download, and the setup never uploads anything. The game is
built on your PC, from your files, for your own use: do not share the installed folder.

After the install, Fastball.exe starts the game straight away. Hold Shift while starting it (or start it with
--menu) for its window: Play, Repair, Import Ryujinx save, and "Download and update" when GitHub has a new version
(it checks once a day; the update replaces this folder's files, and the game files are not needed again).
Settings: F1 in the game, or flags: Fastball.exe --fullscreen --fps-limit 120 (MLBTS\mlb.exe --help lists them
all, from a console window).

Source, issues and help: https://github.com/sam110411/fastball
