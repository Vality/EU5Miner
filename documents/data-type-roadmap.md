# Data Type Roadmap

This file is superseded by the newer planning layout.

Use:

- `ROADMAP.md` for the current order of work
- `documents/specs/library-integration-pass.md` for the current core-library execution slice
- `documents/specs/validation-expansion.md` for the current validation slice

The old domain-by-domain rollout plan was useful while the parser surface was still being established, but it is no longer the main planning surface for the project.
- filesystem materialization helpers
- public mod update facade
- dry-run and reporting helpers for the public mod workflow
- CLI mod workflow commands for plan/apply, advisories, warnings, and explicit file or content-root inputs

Next recommended work areas:

1. library integration pass and API polish
2. broader validation sweep expansion
3. first feature-facing consumer of the stable APIs

Recommendation:

- start with the library integration pass and API polish
- follow it immediately with a broader validation sweep expansion
- then choose one feature-facing surface, with MCP tooling likely giving faster leverage than a full desktop GUI

This sequence fits the current state of the codebase: the adapter families are effectively in place, so the highest-value next step is to stabilize and harden the integrated library surface before building larger downstream products on top of it.
