# Development Environment

## OneDrive and uv

This repository lives in a OneDrive-backed folder, which can interfere with `uv` when a project-local `.venv` contains many small files or when hardlink behavior is restricted.

The project-level workaround is to keep the environment outside OneDrive and point `uv` at that location.

## Recommended Path

Use this environment path for the workspace:

```text
%USERPROFILE%\.venvs\EU5Miner
```

## Workspace Support

The repository includes workspace settings in `.vscode/settings.json` that:

- set `UV_PROJECT_ENVIRONMENT` for integrated terminals
- point VS Code at `~/.venvs` when searching for interpreters
- default the interpreter path to `%USERPROFILE%\.venvs\EU5Miner\Scripts\python.exe`

## Bootstrap Command

Run:

```powershell
.\scripts\setup-centralized-uv.ps1
```

This script:

1. sets `UV_PROJECT_ENVIRONMENT` for the current session
2. creates or refreshes the centralized environment with `uv sync --extra dev`
3. reports the interpreter path to use

## Notes

- Existing `.venv` usage remains a fallback if needed.
- New terminals opened in this workspace should pick up the centralized environment setting automatically.
- If you work on another machine, the same workspace settings and script should be reused there.
