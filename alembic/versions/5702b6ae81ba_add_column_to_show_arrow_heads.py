"""Add column to show arrow heads.

Revision ID: 5702b6ae81ba
Revises: a444c36d585f
Create Date: 2023-07-20 14:44:43.644859

"""
from alembic import op
from sqlalchemy import Column, INTEGER
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5702b6ae81ba'
down_revision = 'a444c36d585f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("user", Column("show_arrow_heads", INTEGER, server_default="1"))


def downgrade() -> None:
    # Causes error.
    # op.drop_column("user", "top_menu_type")

    # Hack to fix.
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('show_arrow_heads')
