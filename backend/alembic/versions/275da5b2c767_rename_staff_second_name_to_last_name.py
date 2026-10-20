"""rename staff second_name to last_name

Revision ID: 275da5b2c767
Revises: 0fd54b735936
Create Date: 2026-09-30 18:45:18.575509

"""

from collections.abc import Sequence

from alembic import op

revision: str = "275da5b2c767"
down_revision: str | None = "0fd54b735936"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column("staff", "second_name", new_column_name="last_name")


def downgrade() -> None:
    op.alter_column("staff", "last_name", new_column_name="second_name")
