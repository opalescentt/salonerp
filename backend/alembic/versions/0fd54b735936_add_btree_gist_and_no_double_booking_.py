"""add btree_gist and no-double-booking constraint

Revision ID: 0fd54b735936
Revises: 99b772dbf8ba
Create Date: 2026-09-29 19:26:05.774893

"""

from collections.abc import Sequence

from alembic import op

revision: str = "0fd54b735936"
down_revision: str | None = "99b772dbf8ba"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:

    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")
    op.execute("""ALTER TABLE appointment
               ADD CONSTRAINT no_double_bookings
               EXCLUDE USING gist (tenant_id WITH =,
                                   staff_id WITH =,
                                   tstzrange(started_at, end_at, '[)') WITH &&)""")


def downgrade() -> None:

    op.execute("""ALTER TABLE appointment
               DROP CONSTRAINT no_double_bookings
               """)
    op.execute("DROP EXTENSION IF EXISTS btree_gist")
