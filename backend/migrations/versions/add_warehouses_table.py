"""添加仓库管理表

Revision ID: a7b8c9d0e1f2
Revises: bde3b167d56d
Create Date: 2024-01-10 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a7b8c9d0e1f2'
down_revision = 'bde3b167d56d'
branch_labels = None
depends_on = None


def upgrade():
    """添加仓库管理表"""
    # 创建仓库表
    op.create_table('warehouses',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('warehouse_code', sa.String(length=50), nullable=False),
        sa.Column('warehouse_name', sa.String(length=100), nullable=False),
        sa.Column('warehouse_type', sa.String(length=50), nullable=True),
        sa.Column('parent_warehouse_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('accounting_method', sa.String(length=50), nullable=True),
        sa.Column('enable_on_site_circulation', sa.Boolean(), nullable=True),
        sa.Column('circulation_type', sa.String(length=50), nullable=True),
        sa.Column('exclude_from_operations', sa.Boolean(), nullable=True),
        sa.Column('is_abnormal', sa.Boolean(), nullable=True),
        sa.Column('is_carryover_warehouse', sa.Boolean(), nullable=True),
        sa.Column('exclude_from_docking', sa.Boolean(), nullable=True),
        sa.Column('is_in_stocktaking', sa.Boolean(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=True),
        sa.Column('is_enabled', sa.Boolean(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['parent_warehouse_id'], ['warehouses.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('warehouse_code'),
        sa.CheckConstraint(
            "warehouse_type IN ('raw_material', 'finished_goods', 'semi_finished', 'defective_goods', 'virtual_warehouse', 'temporary_warehouse', 'return_warehouse', 'quality_warehouse', 'production_warehouse', 'external_warehouse')", 
            name='warehouses_type_check'
        ),
        sa.CheckConstraint(
            "accounting_method IN ('weighted_average', 'moving_average', 'fifo', 'lifo', 'standard_cost', 'individual_cost')", 
            name='warehouses_accounting_method_check'
        ),
        sa.CheckConstraint(
            "circulation_type IN ('normal_flow', 'fast_flow', 'slow_flow', 'special_flow', 'temporary_flow')", 
            name='warehouses_circulation_type_check'
        )
    )
    
    # 创建索引
    op.create_index(op.f('ix_warehouses_warehouse_code'), 'warehouses', ['warehouse_code'], unique=True)
    op.create_index(op.f('ix_warehouses_warehouse_name'), 'warehouses', ['warehouse_name'], unique=False)
    op.create_index(op.f('ix_warehouses_warehouse_type'), 'warehouses', ['warehouse_type'], unique=False)
    op.create_index(op.f('ix_warehouses_tenant_id'), 'warehouses', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_warehouses_is_enabled'), 'warehouses', ['is_enabled'], unique=False)
    op.create_index(op.f('ix_warehouses_created_at'), 'warehouses', ['created_at'], unique=False)


def downgrade():
    """删除仓库管理表"""
    # 删除索引
    op.drop_index(op.f('ix_warehouses_created_at'), table_name='warehouses')
    op.drop_index(op.f('ix_warehouses_is_enabled'), table_name='warehouses')
    op.drop_index(op.f('ix_warehouses_tenant_id'), table_name='warehouses')
    op.drop_index(op.f('ix_warehouses_warehouse_type'), table_name='warehouses')
    op.drop_index(op.f('ix_warehouses_warehouse_name'), table_name='warehouses')
    op.drop_index(op.f('ix_warehouses_warehouse_code'), table_name='warehouses')
    
    # 删除表
    op.drop_table('warehouses') 