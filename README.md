# MLB The Show recomp workspace

This private repository tracks the generated native recomp wrappers, analysis
indexes, evidence-backed annotations, recovered type notes, and progress tools.
The generated C files are instruction-level recomp wrappers; they are not
recovered original source code.

The local MLBTS install, game assets, executables, and downloaded toolchains are
excluded. Do not add game binaries or assets to the repository.

## Progress dashboard

Run `python tools/progress_server.py` locally to serve the live dashboard on
your LAN at port 8765. GitHub Pages cannot run the Python server, so the Pages
workflow exports a static snapshot of the dashboard data whenever the tracked
progress indexes are pushed. To update the public dashboard, push the updated
indexes and timeline to `main`; the workflow publishes only `tools/progress_site`.

To generate the Pages data locally, run `python tools/export_progress_site.py`.
