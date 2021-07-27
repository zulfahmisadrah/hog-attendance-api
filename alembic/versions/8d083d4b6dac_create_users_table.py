"""create user table

Revision ID: 8d083d4b6dac
Revises: 
Create Date: 2021-07-27 17:11:36.847502

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8d083d4b6dac'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.BigInteger),
        sa.Column('username', sa.String(50), nullable=False),
        sa.Column('password', sa.String(100), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('email', sa.String(100)),
        sa.Column('phone_number', sa.String(15)),
        sa.Column('avatar', sa.String(255)),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('is_superuser', sa.Boolean, default=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table('users')
