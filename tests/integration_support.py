"""Internal re-export shim for the synthetic-install helpers.

The public home for these helpers is now ``eu5miner.testing``. This module
exists so existing internal tests can keep importing from
``tests.integration_support`` without churn. New code should import directly
from ``eu5miner.testing`` so the helpers can be reused from
``eu5miner-gui`` and ``eu5miner-mcp`` without path manipulation.
"""

from __future__ import annotations

from eu5miner.testing import (
    SyntheticCliSmokeSurface,
    SyntheticModWorkflowSurface,
    build_synthetic_cli_smoke_surface,
    build_synthetic_install,
    build_synthetic_mod_workflow_surface,
)

__all__ = [
    "SyntheticCliSmokeSurface",
    "SyntheticModWorkflowSurface",
    "build_synthetic_cli_smoke_surface",
    "build_synthetic_install",
    "build_synthetic_mod_workflow_surface",
]
