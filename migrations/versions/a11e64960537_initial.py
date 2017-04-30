"""initial

Revision ID: a11e64960537
Revises: 
Create Date: 2017-04-30 21:48:06.463599

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a11e64960537'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('name',
        sa.Column('hash', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('hash')
    )
    op.create_table('object',
        sa.Column('hash', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('hash')
    )
    op.create_table('availability',
        sa.Column('object_hash', sa.String(), nullable=False),
        sa.Column('time', sa.DateTime(), nullable=False),
        sa.Column('available', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['object_hash'], ['object.hash'], ),
        sa.PrimaryKeyConstraint('object_hash', 'time')
    )
    op.create_table('link',
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('parent_object_hash', sa.String(), nullable=False),
        sa.Column('child_object_hash', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['child_object_hash'], ['object.hash'], ),
        sa.ForeignKeyConstraint(['parent_object_hash'], ['object.hash'], ),
        sa.PrimaryKeyConstraint('type', 'parent_object_hash', 'child_object_hash', 'name')
    )
    op.create_table('name_reference',
        sa.Column('object_hash', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('name_hash', sa.String(), nullable=False),
        sa.Column('label', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['name_hash'], ['name.hash'], ),
        sa.ForeignKeyConstraint(['object_hash'], ['object.hash'], ),
        sa.PrimaryKeyConstraint('object_hash', 'type', 'name_hash', 'label')
    )
    op.create_table('property',
        sa.Column('object_hash', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('value', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['object_hash'], ['object.hash'], ),
        sa.PrimaryKeyConstraint('object_hash', 'name')
    )
    op.create_table('resolution',
        sa.Column('time', sa.DateTime(), nullable=False),
        sa.Column('name_hash', sa.String(), nullable=False),
        sa.Column('object_hash', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['name_hash'], ['name.hash'], ),
        sa.ForeignKeyConstraint(['object_hash'], ['object.hash'], ),
        sa.PrimaryKeyConstraint('time', 'name_hash')
    )


def downgrade():
    op.drop_table('resolution')
    op.drop_table('property')
    op.drop_table('name_reference')
    op.drop_table('link')
    op.drop_table('availability')
    op.drop_table('object')
    op.drop_table('name')
