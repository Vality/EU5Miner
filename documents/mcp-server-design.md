# MCP Server Design Report

## Purpose

This document outlines a practical design for an MCP (Model Context Protocol) server on top of EU5Miner and recommends where that server should live.

## Current Baseline

The library is now in a good position to support an MCP layer:

- representative-file coverage is in place across the implemented domain families
- grouped package entrypoints now exist for the major connected systems
- the curated `eu5miner.domains` surface already exposes the low-level adapters and higher-level helper layers
- the CLI now has install-backed system reports for the major connected systems, which is a useful rehearsal for the kinds of summaries an MCP tool surface should expose

The main remaining risk is not missing parser families. It is API churn while the integration and polish pass is still settling.

## Goals

The MCP server should make the parsed game data easy for an LLM to inspect without forcing the model to reason about filesystem details or raw Clausewitz syntax unless necessary.

The first version should optimize for:

- read-only install and content inspection
- narrow, composable tools
- stable, typed responses built directly on top of the library
- reuse of the same representative-file and integration validation already used by the core repo

## Proposed Tool Layers

### Phase 1: Read-Only Core Tools

These are the highest-value initial tools.

1. install inspection
2. representative file lookup
3. phase-aware file lookup
4. entity search by family and name
5. entity retrieval by family and identifier
6. system report retrieval for `economy`, `diplomacy`, `government`, `religion`, `interface`, and `map`

Examples:

- get install roots and available representative samples
- find all religions matching a substring
- retrieve one event, one government reform, or one holy site by name
- return the current economy or diplomacy report over representative files

### Phase 2: Cross-Reference Tools

Once the read-only basics are stable, add tools that take advantage of the existing helper layers.

1. diplomacy graph queries
2. religion helper queries
3. government helper queries
4. market helper queries
5. localization reference resolution queries
6. linked map-location queries

Examples:

- find peace treaties that reference a given casus belli
- list holy sites or religious schools for a religion
- list reforms or policies for a government type
- list market-targeted generic actions
- resolve missing localization references for one helper document

### Phase 3: Write-Planning Tools

Only after the read-only surface is stable.

1. plan mod update
2. summarize warnings and advisories
3. preview targeted outputs
4. optionally apply changes behind explicit user approval or a clearly separate write-capable mode

This phase should stay conservative. The first MCP release does not need write capability to be useful.

## Recommended Server Shape

The MCP server should be a thin adapter over the library, not a second implementation layer.

Recommended internal structure:

- transport or server bootstrap module
- tool modules grouped by concern: install, files, entities, systems, cross-links, mod planning
- shared serializers that convert dataclasses and helper reports into compact MCP-friendly payloads
- a narrow caching layer for install discovery and representative-file parsing within one server session

The server should call into existing library APIs such as:

- `GameInstall.discover`
- `VirtualFilesystem`
- `eu5miner.domains` curated exports
- grouped package entrypoints such as `eu5miner.domains.diplomacy`, `...economy`, `...government`, `...religion`, `...map`, and `...localization`
- `eu5miner.mods` for later write-planning tools

## Packaging Options

### Option A: Build It In This Repository And This Package

Pros:

- fastest to start
- easiest access to the evolving internal APIs
- simplest local development loop

Cons:

- increases dependency and packaging weight in the core library
- blurs the separation between reusable library code and one delivery surface

### Option B: Build It In This Repository As A Separate Package

Examples:

- `src/eu5miner_mcp/`
- or a sibling package directory such as `packages/eu5miner-mcp/`

Pros:

- keeps tight development coupling while the API is still settling
- preserves shared tests, fixtures, representative-file validation, and release coordination
- creates a cleaner extraction path later if the server needs its own release cadence
- keeps the core library leaner than embedding the server directly into `eu5miner`

Cons:

- slightly more packaging and workspace setup overhead than Option A

### Option C: Build It In A Separate Repository Now

Pros:

- strong separation of concerns from day one
- independent release cadence immediately available

Cons:

- duplicates integration effort while the core API is still changing
- makes representative-file validation and cross-repo change coordination slower
- raises the cost of early iteration before the tool surface is proven

## Recommendation

Recommendation: use Option B.

Build the first MCP server in this repository, but as a separate package rather than inside the main `eu5miner` package and not as a second repository yet.

This is the best fit for the repo's current maturity:

- the core library is now broad enough to support an MCP layer
- the integration pass is still recent, so close coupling to the core codebase is valuable
- shared representative-file and system-report validation should stay in one place during the first implementation cycle
- the roadmap already points toward eventual package modularization, so a same-repo separate package gives a clean upgrade path without paying cross-repo coordination costs too early

## Suggested Initial Layout

One reasonable starting layout is:

```text
src/
  eu5miner/
  eu5miner_mcp/
    __init__.py
    server.py
    serializers.py
    tools/
      install.py
      files.py
      entities.py
      systems.py
      cross_links.py
```

The MCP package should depend on `eu5miner` and expose only transport, tool wiring, and serialization logic.

## First Implementation Slice

The first milestone should stay intentionally small.

1. install inspection tool
2. representative key listing tool
3. entity search tool for a few high-value families
4. entity retrieval tool for a few high-value families
5. system report tool for the six current major systems

That is enough to prove the server model without committing to write-capable tooling too early.

## Extraction Trigger

If the MCP package reaches the point where it needs:

- independent releases
- non-library runtime dependencies that the core package should not carry
- deployment or hosting logic unrelated to core parsing

then it should be extracted into its own repository or at minimum promoted to a separately versioned package.

Until then, a same-repo separate package is the lowest-risk path.
