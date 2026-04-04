# EU5MinerGUI Architecture

## Role

This repo owns the GUI application surface.

It should not become a second parser or a second domain-model implementation.

## Boundaries

- `eu5miner`: parsing, discovery, VFS, typed domain adapters, system reports, mod planning
- `eu5miner_gui`: presentation, app flow, view composition, and UI-specific state

## First Principle

Start with a read-only shell. The first useful version of this repo is a stable browser over existing library outputs.
