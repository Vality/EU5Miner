# Security Policy

## Supported Versions

The current supported line is `0.8.x` for the unified `eu5miner` distribution. The previous `0.7.x` and `0.6.x` lines remain supported for the core library and the former downstream packages.

Older preview builds may not receive fixes.

## Reporting a Vulnerability

Please avoid filing public issues for suspected security problems.

If GitHub private vulnerability reporting is enabled for this repository, use that channel first.

If private reporting is not available, contact the maintainer privately through GitHub and include:

- a short description of the issue
- affected version or commit, including which surface (`eu5miner` core, `eu5miner.mcp`, or `eu5miner.gui`) is implicated
- reproduction steps or a proof of concept
- any suggested remediation or impact details

Please do not publish exploit details until the issue has been reviewed and a fix or mitigation is available.

## Scope Notes

EU5Miner is a local, file-oriented library, an MCP server, and a desktop UI. The main security-sensitive areas for this project are expected to be file handling, path resolution, MCP write workflows that materialize or modify mod content on disk, and any GUI workflows that touch the local filesystem.
