"""添加成品盘点表

Revision ID: add_product_count_tables
Revises: 
Create Date: 2025-01-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_product_count_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 成品盘点计划表
    op.create_table('product_count_plans',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('count_number', sa.String(length=100), nullable=False),
        sa.Column('warehouse_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('warehouse_name', sa.String(length=200), nullable=False),
        sa.Column('warehouse_code', sa.String(length=100), nullable=True),
        sa.Column('count_person_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('department_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('count_date', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['count_person_id'], ['employees.id'], ),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('count_number'),
        comment='成品盘点计划表'
    )
    op.create_index('idx_product_count_plans_warehouse', 'product_count_plans', ['warehouse_id'], unique=False)
    op.create_index('idx_product_count_plans_count_date', 'product_count_plans', ['count_date'], unique=False)
    op.create_index('idx_product_count_plans_status', 'product_count_plans', ['status'], unique=False)

    # 成品盘点记录表
    op.create_table('product_count_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('count_plan_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('inventory_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_code', sa.String(length=100), nullable=True),
        sa.Column('product_name', sa.String(length=200), nullable=False),
        sa.Column('product_spec', sa.String(length=200), nullable=True),
        sa.Column('base_unit', sa.String(length=20), nullable=False),
        sa.Column('book_quantity', sa.Numeric(precision=15, scale=3), nullable=False),
        sa.Column('actual_quantity', sa.Numeric(precision=15, scale=3), nullable=True),
        sa.Column('variance_quantity', sa.Numeric(precision=15, scale=3), nullable=True),
        sa.Column('variance_rate', sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column('batch_number', sa.String(length=100), nullable=True),
        sa.Column('production_date', sa.DateTime(), nullable=True),
        sa.Column('expiry_date', sa.DateTime(), nullable=True),
        sa.Column('location_code', sa.String(length=100), nullable=True),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('customer_name', sa.String(length=200), nullable=True),
        sa.Column('bag_type_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('bag_type_name', sa.String(length=100), nullable=True),
        sa.Column('package_unit', sa.String(length=20), nullable=True),
        sa.Column('package_quantity', sa.Numeric(precision=15, scale=3), nullable=True),
        sa.Column('net_weight', sa.Numeric(precision=10, scale=3), nullable=True),
        sa.Column('gross_weight', sa.Numeric(precision=10, scale=3), nullable=True),
        sa.Column('variance_reason', sa.String(length=500), nullable=True),
        sa.Column('is_adjusted', sa.Boolean(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['count_plan_id'], ['product_count_plans.id'], ),
        sa.PrimaryKeyConstraint('id'),
        comment='成品盘点记录表'
    )
    op.create_index('idx_product_count_records_count_plan', 'product_count_records', ['count_plan_id'], unique=False)
    op.create_index('idx_product_count_records_product', 'product_count_records', ['product_id'], unique=False)
    op.create_index('idx_product_count_records_status', 'product_count_records', ['status'], unique=False)


def downgrade():
    # 删除索引
    op.drop_index('idx_product_count_records_status', table_name='product_count_records')
    op.drop_index('idx_product_count_records_product', table_name='product_count_records')
    op.drop_index('idx_product_count_records_count_plan', table_name='product_count_records')
    op.drop_index('idx_product_count_plans_status', table_name='product_count_plans')
    op.drop_index('idx_product_count_plans_count_date', table_name='product_count_plans')
    op.drop_index('idx_product_count_plans_warehouse', table_name='product_count_plans')
    
    # 删除表
    op.drop_table('product_count_records')
    op.drop_table('product_count_plans') 