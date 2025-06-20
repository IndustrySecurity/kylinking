"""添加材料盘点功能相关表

Revision ID: add_material_count_functionality
Revises: 951ef0013fb6
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_material_count_functionality'
down_revision = '951ef0013fb6'
branch_labels = None
depends_on = None


def upgrade():
    """添加材料盘点相关表"""
    
    # 创建材料盘点计划表
    op.create_table('material_count_plans',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('count_number', sa.String(length=100), nullable=False),
        sa.Column('warehouse_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('warehouse_name', sa.String(length=200), nullable=False),
        sa.Column('warehouse_code', sa.String(length=100), nullable=True),
        
        # 使用外键关联到员工表和部门表
        sa.Column('count_person_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('department_id', postgresql.UUID(as_uuid=True), nullable=True),
        
        sa.Column('count_date', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        
        # 审计字段
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('count_number'),
        
        # 外键约束
        sa.ForeignKeyConstraint(['count_person_id'], ['employees.id'], ),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ),
        
        comment='材料盘点计划表'
    )
    
    # 创建索引
    op.create_index('ix_material_count_plan_number', 'material_count_plans', ['count_number'])
    op.create_index('ix_material_count_plan_warehouse', 'material_count_plans', ['warehouse_id'])
    op.create_index('ix_material_count_plan_person', 'material_count_plans', ['count_person_id'])
    op.create_index('ix_material_count_plan_department', 'material_count_plans', ['department_id'])
    op.create_index('ix_material_count_plan_date', 'material_count_plans', ['count_date'])
    op.create_index('ix_material_count_plan_status', 'material_count_plans', ['status'])
    
    # 创建材料盘点记录表
    op.create_table('material_count_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('count_plan_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('inventory_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('material_id', postgresql.UUID(as_uuid=True), nullable=False),
        
        # 材料信息
        sa.Column('material_code', sa.String(length=100), nullable=True),
        sa.Column('material_name', sa.String(length=200), nullable=False),
        sa.Column('material_spec', sa.String(length=200), nullable=True),
        sa.Column('unit', sa.String(length=20), nullable=False),
        
        # 盘点数据
        sa.Column('book_quantity', sa.Numeric(precision=15, scale=3), nullable=False),
        sa.Column('actual_quantity', sa.Numeric(precision=15, scale=3), nullable=True),
        sa.Column('variance_quantity', sa.Numeric(precision=15, scale=3), nullable=True),
        sa.Column('variance_rate', sa.Numeric(precision=8, scale=4), nullable=True),
        
        # 批次和位置信息
        sa.Column('batch_number', sa.String(length=100), nullable=True),
        sa.Column('location_code', sa.String(length=100), nullable=True),
        
        # 差异处理
        sa.Column('variance_reason', sa.String(length=500), nullable=True),
        sa.Column('is_adjusted', sa.Boolean(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        
        # 审计字段
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['count_plan_id'], ['material_count_plans.id'], ),
        
        comment='材料盘点记录表'
    )
    
    # 创建索引
    op.create_index('ix_material_count_records_plan_id', 'material_count_records', ['count_plan_id'])
    op.create_index('ix_material_count_records_material_id', 'material_count_records', ['material_id'])
    op.create_index('ix_material_count_records_material_code', 'material_count_records', ['material_code'])
    op.create_index('ix_material_count_records_status', 'material_count_records', ['status'])


def downgrade():
    """删除材料盘点相关表"""
    op.drop_table('material_count_records')
    op.drop_table('material_count_plans') 