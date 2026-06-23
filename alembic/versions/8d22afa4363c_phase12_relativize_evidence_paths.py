"""phase12 relativize evidence paths

Revision ID: 8d22afa4363c
Revises: 183123584310
Create Date: 2026-06-23 15:15:34.212450

Data-only migration. Existing EvidenceFile rows store absolute host paths
like ``/Users/<user>/.../outputs/...``; from Phase 12 onward the application
persists paths relative to PROJECT_ROOT so they resolve both on the dev
machine and inside the Docker container (where PROJECT_ROOT is ``/app``).

This migration rewrites any path that falls under the current PROJECT_ROOT
into its repo-relative form. Paths outside PROJECT_ROOT are left as-is.
"""
from pathlib import Path
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '8d22afa4363c'
down_revision: Union[str, Sequence[str], None] = '183123584310'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# alembic/versions/<file>.py -> repo root is parents[2]
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def upgrade() -> None:
    bind = op.get_bind()
    rows = bind.execute(sa.text("SELECT id, path FROM evidence_files")).fetchall()
    updated = 0
    for row in rows:
        p = Path(row.path)
        if not p.is_absolute():
            continue
        try:
            rel = p.resolve().relative_to(PROJECT_ROOT)
        except ValueError:
            continue
        bind.execute(
            sa.text("UPDATE evidence_files SET path = :p WHERE id = :id"),
            {"p": str(rel), "id": row.id},
        )
        updated += 1
    print(f"[migration 8d22afa4363c] relativized {updated}/{len(rows)} evidence paths")


def downgrade() -> None:
    bind = op.get_bind()
    rows = bind.execute(sa.text("SELECT id, path FROM evidence_files")).fetchall()
    restored = 0
    for row in rows:
        p = Path(row.path)
        if p.is_absolute():
            continue
        bind.execute(
            sa.text("UPDATE evidence_files SET path = :p WHERE id = :id"),
            {"p": str(PROJECT_ROOT / p), "id": row.id},
        )
        restored += 1
    print(f"[migration 8d22afa4363c] restored {restored}/{len(rows)} evidence paths to absolute")
