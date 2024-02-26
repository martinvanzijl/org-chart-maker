"""Create password reset link table.

Revision ID: d0cd2ccf936d
Revises: d06722312ba1
Create Date: 2024-01-31 12:26:15.344505

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd0cd2ccf936d'
down_revision = 'd06722312ba1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'password_reset_link',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, nullable=False),
        sa.Column('link', sa.Text, nullable=False),
        sa.Column('created_date', sa.Date),
        sa.Column('expiry_date', sa.Date),
        sa.Column('status', sa.Text)
    )


def downgrade() -> None:
    op.drop_table('password_reset_link')
