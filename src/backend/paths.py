"""Helpers to keep persisted evidence paths portable across hosts/containers.

We store paths as **relative to PROJECT_ROOT** when possible so the same DB
row resolves on a developer Mac and inside the Docker container (where the
host project root becomes ``/app``). Paths outside PROJECT_ROOT are stored
as absolute and remain absolute on the way out.
"""
from __future__ import annotations

from pathlib import Path

from src.backend.config import PROJECT_ROOT


def to_repo_relative(p: Path | str) -> str:
    """Convert a path to its repo-relative form (str). Falls back to absolute.

    If the path is not under the current PROJECT_ROOT (e.g. a host-side
    absolute path being ingested inside the container), look for an
    ``outputs/`` segment and use the suffix from there. This keeps cross-host
    JSONL ingestion portable.
    """
    path = Path(p).resolve()
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        parts = path.parts
        if "outputs" in parts:
            idx = parts.index("outputs")
            return str(Path(*parts[idx:]))
        return str(path)


def resolve_evidence_path(stored: str) -> Path:
    """Reverse of :func:`to_repo_relative` — resolve a stored path for I/O."""
    p = Path(stored)
    return p if p.is_absolute() else PROJECT_ROOT / p
