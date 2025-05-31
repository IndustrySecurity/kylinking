"""Add product categories table

Revision ID: add_product_categories_table
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_product_categories_table'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Create product_categories table in tenant schemas"""
    
    # 这个迁移需要在租户schema中执行
    # 实际执行时需要根据具体的租户schema来运行
    
    op.create_table('product_categories',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('category_name', sa.String(length=255), nullable=False, comment='产品分类名称'),
        sa.Column('subject_name', sa.String(length=100), nullable=True, comment='科目名称'),
        sa.Column('is_blown_film', sa.Boolean(), nullable=True, default=False, comment='是否吹膜'),
        sa.Column('delivery_days', sa.Integer(), nullable=True, comment='交货天数'),
        sa.Column('description', sa.Text(), nullable=True, comment='描述'),
        sa.Column('sort_order', sa.Integer(), nullable=True, default=0, comment='显示排序'),
        sa.Column('is_enabled', sa.Boolean(), nullable=True, default=True, comment='是否启用'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False, comment='创建人'),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True, comment='修改人'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建索引
    op.create_index('idx_product_categories_enabled', 'product_categories', ['is_enabled'])
    op.create_index('idx_product_categories_sort_order', 'product_categories', ['sort_order'])


def downgrade():
    """Drop product_categories table"""
    op.drop_index('idx_product_categories_sort_order', table_name='product_categories')
    op.drop_index('idx_product_categories_enabled', table_name='product_categories')
    op.drop_table('product_categories') 