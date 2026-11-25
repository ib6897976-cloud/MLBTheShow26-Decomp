# MLB The Show recomp progress

A public, static dashboard for aggregate analysis progress in the independent
MLB The Show recompilation and reverse-engineering project.

[![Function coverage map](progress.svg)](https://ib6897976-cloud.github.io/mlb-the-show-progress/)

## Status

The dashboard reports indexed function coverage, evidence-backed semantic
labels, candidate prototypes and fields, and recent work history. Values are
snapshots exported from the private analysis workspace and update when a
reviewed annotation batch is published.

## Contents

This repository contains the dashboard page and aggregate JSON snapshots only.
It does not contain generated decomp source, game files, proprietary assets, or
the private analysis workspace.

## Publishing

The private workspace exports this site with
`tools/publish_progress_pages.ps1`. GitHub Pages serves the resulting static
files; the Python live server runs separately in the workspace.

## Disclaimer

This is an independent research project and is not affiliated with or endorsed
by Sony Interactive Entertainment, San Diego Studio, or Major League Baseball.
