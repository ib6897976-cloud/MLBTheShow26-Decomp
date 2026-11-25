# MLB The Show recomp workspace

This private repository tracks the generated native recomp wrappers, analysis
indexes, evidence-backed annotations, recovered type notes, and progress tools.
The generated C files are instruction-level recomp wrappers; they are not
recovered original source code.

The local MLBTS install, game assets, executables, and downloaded toolchains are
excluded. Do not add game binaries or assets to the repository.

## Progress dashboard

Run `python tools/progress_server.py` locally to serve the live dashboard on
your LAN at port 8765. GitHub Pages cannot run the Python server, so the public
repository `ib6897976-cloud/mlb-the-show-progress` contains only the dashboard
UI and exported progress snapshots. After updating annotations, run
`tools/publish_progress_pages.ps1` to export and push the new snapshot to Pages.

To generate the Pages data locally, run `python tools/export_progress_site.py`.
