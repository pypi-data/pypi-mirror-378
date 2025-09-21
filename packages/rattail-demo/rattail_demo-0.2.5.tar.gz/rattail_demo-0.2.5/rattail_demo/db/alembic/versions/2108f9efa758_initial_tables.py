# -*- coding: utf-8 -*-
"""initial tables

Revision ID: 2108f9efa758
Revises: efb7cd318947
Create Date: 2020-08-19 20:02:15.501843

"""

# revision identifiers, used by Alembic.
revision = '2108f9efa758'
down_revision = None
branch_labels = ('rattail_demo',)
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # demo_shopfoo_product
    op.create_table('demo_shopfoo_product',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('product_uuid', sa.String(length=32), nullable=True),
                    sa.Column('upc', sa.String(length=14), nullable=True),
                    sa.Column('description', sa.String(length=255), nullable=True),
                    sa.Column('price', sa.Numeric(precision=13, scale=2), nullable=True),
                    sa.Column('enabled', sa.Boolean(), nullable=True),
                    sa.ForeignKeyConstraint(['product_uuid'], ['product.uuid'], name='demo_shopfoo_product_fk_product'),
                    sa.PrimaryKeyConstraint('uuid')
    )
    op.create_table('demo_shopfoo_product_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('product_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('upc', sa.String(length=14), autoincrement=False, nullable=True),
                    sa.Column('description', sa.String(length=255), autoincrement=False, nullable=True),
                    sa.Column('price', sa.Numeric(precision=13, scale=2), autoincrement=False, nullable=True),
                    sa.Column('enabled', sa.Boolean(), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
    )
    op.create_index(op.f('ix_demo_shopfoo_product_version_end_transaction_id'), 'demo_shopfoo_product_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_demo_shopfoo_product_version_operation_type'), 'demo_shopfoo_product_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_demo_shopfoo_product_version_transaction_id'), 'demo_shopfoo_product_version', ['transaction_id'], unique=False)

    # demo_shopfoo_product_export
    op.create_table('demo_shopfoo_product_export',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('created', sa.DateTime(), nullable=False),
                    sa.Column('created_by_uuid', sa.String(length=32), nullable=False),
                    sa.Column('record_count', sa.Integer(), nullable=True),
                    sa.Column('filename', sa.String(length=255), nullable=True),
                    sa.Column('uploaded', sa.Boolean(), nullable=False),
                    sa.ForeignKeyConstraint(['created_by_uuid'], ['user.uuid'], name='demo_shopfoo_product_export_fk_created_by'),
                    sa.PrimaryKeyConstraint('uuid')
    )


def downgrade():

    # demo_shopfoo_product_export
    op.drop_table('demo_shopfoo_product_export')

    # demo_shopfoo_product
    op.drop_index(op.f('ix_demo_shopfoo_product_version_transaction_id'), table_name='demo_shopfoo_product_version')
    op.drop_index(op.f('ix_demo_shopfoo_product_version_operation_type'), table_name='demo_shopfoo_product_version')
    op.drop_index(op.f('ix_demo_shopfoo_product_version_end_transaction_id'), table_name='demo_shopfoo_product_version')
    op.drop_table('demo_shopfoo_product_version')
    op.drop_table('demo_shopfoo_product')
