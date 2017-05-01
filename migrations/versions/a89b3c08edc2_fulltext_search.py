"""fulltext_search

Revision ID: a89b3c08edc2
Revises: a11e64960537
Create Date: 2017-05-01 18:52:00.261001

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy_searchable import sync_trigger
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = 'a89b3c08edc2'
down_revision = 'a11e64960537'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()

    op.add_column('link', sa.Column('search_vector', sqlalchemy_utils.types.ts_vector.TSVectorType(), nullable=True))
    op.add_column('name_reference', sa.Column('search_vector', sqlalchemy_utils.types.ts_vector.TSVectorType(), nullable=True))
    op.add_column('property', sa.Column('search_vector', sqlalchemy_utils.types.ts_vector.TSVectorType(), nullable=True))

    op.create_index('ix_link_search_vector', 'link', ['search_vector'], unique=False, postgresql_using='gin')
    op.create_index('ix_name_reference_search_vector', 'name_reference', ['search_vector'], unique=False, postgresql_using='gin')
    op.create_index('ix_property_search_vector', 'property', ['search_vector'], unique=False, postgresql_using='gin')

    sync_trigger(conn, 'link', 'search_vector', ['name'])
    sync_trigger(conn, 'name_reference', 'search_vector', ['label'])
    sync_trigger(conn, 'property', 'search_vector', ['value'])


def downgrade():
    op.drop_index('ix_property_search_vector', table_name='property')
    op.drop_index('ix_name_reference_search_vector', table_name='name_reference')
    op.drop_index('ix_link_search_vector', table_name='link')

    op.drop_column('property', 'search_vector')
    op.drop_column('name_reference', 'search_vector')
    op.drop_column('link', 'search_vector')

