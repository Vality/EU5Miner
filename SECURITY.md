# Security Policy

## Supported Versions

The current supported public release line is `0.6.x`.

Older preview builds may not receive fixes.

## Reporting a Vulnerability

Please avoid filing public issues for suspected security problems.

If GitHub private vulnerability reporting is enabled for this repository, use that channel first.

If private reporting is not available, contact the maintainer privately through GitHub and include:

- a short description of the issue
- affected version or commit
- reproduction steps or a proof of concept
- any suggested remediation or impact details

Please do not publish exploit details until the issue has been reviewed and a fix or mitigation is available.

## Scope Notes

EU5Miner is a local, file-oriented library and CLI. The main security-sensitive areas for this project are expected to be file handling, path resolution, and any future workflows that materialize or modify mod content on disk.
