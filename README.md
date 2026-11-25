# MLB The Show recomp

An independent recompilation and reverse-engineering project for MLB The Show.
The workspace combines generated native wrappers, analysis tools, a host runtime,
and evidence-based notes about game behavior.

The generated C files are instruction-level recomp wrappers for guest
functions. They are not recovered original source code. Names and structure
layouts in the analysis files are working conclusions backed by binary and
call-graph evidence, with confidence recorded where possible.

## Status

The current analysis covers 135,060 indexed guest functions. A subset has
readable names, candidate prototypes, or field annotations; the remaining
functions are still being investigated. See the
[public progress dashboard](https://ib6897976-cloud.github.io/mlb-the-show-progress/)
for current coverage and progress history.

Subsystem notes live in [decompiled](decompiled/), and recovered partial
layouts live in [recovered](recovered/). These are evolving maps, not complete
or authoritative descriptions of every game data structure.

## Compatibility

The workspace contains metadata for the supported game builds in
[`tools/data/expected-1.0.15.json`](tools/data/expected-1.0.15.json) and
[`tools/data/expected-1.0.20.json`](tools/data/expected-1.0.20.json). Addresses,
strings, and layouts are build-specific. Check the matching build before
reusing an observation.

## Build and analysis

- [Build and workspace setup](docs/dev/BUILD.md)
- [Architecture and generated-code map](docs/dev/ARCHITECTURE.md)
- [Analysis conventions](docs/dev/CONVENTIONS.md)
- [Contributing notes](CONTRIBUTING.md)

## Progress dashboard

Run `python tools/progress_server.py` to view the live local dashboard at
`http://127.0.0.1:8765`. To view it from another device on the same Wi-Fi,
use the host computer's LAN address and port 8765.

GitHub Pages serves a static exported snapshot because Pages cannot run the
Python server. After reviewed annotation updates, run
`tools/publish_progress_pages.ps1` to export and publish the latest snapshot.
The public Pages repository contains only the dashboard and progress data.

## Disclaimer

This is an independent interoperability and research project and is not
affiliated with or endorsed by Sony Interactive Entertainment, San Diego
Studio, or Major League Baseball. The repository excludes the locally installed
game and its proprietary assets. Users must supply their own legally obtained
game files and comply with applicable laws and platform terms.

## License

See [LICENSE](LICENSE) for this project's license and
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for notices about included
third-party components. Those notices and component licenses remain in force.
