"""Initial tables creation

Revision ID: 001_initial_tables
Revises:
Create Date: 2024-03-17 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "001_initial_tables"
down_revision: Union[str, None] = None
branch_labels: Union[Sequence[str], None] = None
depends_on: Union[Sequence[str], None] = None


def upgrade() -> None:
    # Create datasets table
    op.create_table(
        'datasets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('fqn', sa.String(512), nullable=False),
        sa.Column('connection_name', sa.String(255), nullable=False),
        sa.Column('database_name', sa.String(255), nullable=False),
        sa.Column('schema_name', sa.String(255), nullable=False),
        sa.Column('table_name', sa.String(255), nullable=False),
        sa.Column('source_type', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('fqn', name='uq_dataset_fqn'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4'
    )
    op.create_index('idx_connection_db_schema_table', 'datasets',
                    ['connection_name', 'database_name', 'schema_name', 'table_name'])
    op.create_index('ix_datasets_fqn', 'datasets', ['fqn'])
    op.create_index('ix_datasets_connection_name', 'datasets', ['connection_name'])
    op.create_index('ix_datasets_database_name', 'datasets', ['database_name'])
    op.create_index('ix_datasets_schema_name', 'datasets', ['schema_name'])
    op.create_index('ix_datasets_table_name', 'datasets', ['table_name'])

    # Create columns table
    op.create_table(
        'columns',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('dataset_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('type', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['dataset_id'], ['datasets.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4'
    )
    op.create_index('idx_dataset_column_name', 'columns', ['dataset_id', 'name'])
    op.create_index('ix_columns_dataset_id', 'columns', ['dataset_id'])
    op.create_index('ix_columns_name', 'columns', ['name'])

    # Create lineage table
    op.create_table(
        'lineage',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('upstream_dataset_id', sa.Integer(), nullable=False),
        sa.Column('downstream_dataset_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['downstream_dataset_id'], ['datasets.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['upstream_dataset_id'], ['datasets.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('upstream_dataset_id', 'downstream_dataset_id', name='uq_lineage'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4'
    )
    op.create_index('idx_upstream_downstream', 'lineage',
                    ['upstream_dataset_id', 'downstream_dataset_id'])
    op.create_index('ix_lineage_upstream_dataset_id', 'lineage', ['upstream_dataset_id'])
    op.create_index('ix_lineage_downstream_dataset_id', 'lineage', ['downstream_dataset_id'])


def downgrade() -> None:
    op.drop_index('ix_lineage_downstream_dataset_id', table_name='lineage')
    op.drop_index('ix_lineage_upstream_dataset_id', table_name='lineage')
    op.drop_index('idx_upstream_downstream', table_name='lineage')
    op.drop_table('lineage')
    op.drop_index('ix_columns_name', table_name='columns')
    op.drop_index('ix_columns_dataset_id', table_name='columns')
    op.drop_index('idx_dataset_column_name', table_name='columns')
    op.drop_table('columns')
    op.drop_index('ix_datasets_table_name', table_name='datasets')
    op.drop_index('ix_datasets_schema_name', table_name='datasets')
    op.drop_index('ix_datasets_database_name', table_name='datasets')
    op.drop_index('ix_datasets_connection_name', table_name='datasets')
    op.drop_index('ix_datasets_fqn', table_name='datasets')
    op.drop_index('idx_connection_db_schema_table', table_name='datasets')
    op.drop_table('datasets')
