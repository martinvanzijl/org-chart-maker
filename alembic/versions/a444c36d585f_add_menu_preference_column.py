"""add menu preference column

Revision ID: a444c36d585f
Revises:
Create Date: 2023-04-27 05:03:46.289527

"""
from alembic import op
from sqlalchemy import Column, INTEGER
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a444c36d585f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("user", Column("top_menu_type", INTEGER, server_default="0"))


def downgrade() -> None:
    # Causes error.
    # op.drop_column("user", "top_menu_type")

    # Hack to fix.
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('top_menu_type')
