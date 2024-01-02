"""add email field to user

Revision ID: d06722312ba1
Revises: 5702b6ae81ba
Create Date: 2024-01-01 13:05:39.047689

"""
from alembic import op
from sqlalchemy import Column, TEXT
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd06722312ba1'
down_revision = '5702b6ae81ba'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("user", Column("email", TEXT))


def downgrade() -> None:
    # Causes error.
    # op.drop_column("user", "email")

    # Hack to fix.
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('email')
