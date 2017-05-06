"""add_monitoring_models

Revision ID: e0598c814df5
Revises: a89b3c08edc2
Create Date: 2017-05-06 09:52:19.830284

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e0598c814df5'
down_revision = 'a89b3c08edc2'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('measurement',
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('value', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('name', 'date')
    )


def downgrade():
    op.drop_table('measurement')
