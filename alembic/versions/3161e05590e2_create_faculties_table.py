"""create faculty table

Revision ID: 3161e05590e2
Revises: 8d083d4b6dac
Create Date: 2021-07-27 17:11:53.784922

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3161e05590e2'
down_revision = '8d083d4b6dac'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'faculties',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(50), nullable=False),
    )


def downgrade():
    op.drop_table('faculties')

