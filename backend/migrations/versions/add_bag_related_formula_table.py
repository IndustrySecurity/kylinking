"""添加袋型相关公式表

Revision ID: add_bag_related_formula
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'add_bag_related_formula'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 创建袋型相关公式表
    op.create_table(
        'bag_related_formulas',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('bag_type_id', UUID(as_uuid=True), sa.ForeignKey('bag_types.id'), nullable=False, comment='袋型ID'),
        sa.Column('meter_formula_id', UUID(as_uuid=True), comment='米数公式ID'),
        sa.Column('square_formula_id', UUID(as_uuid=True), comment='平方公式ID'),
        sa.Column('material_width_formula_id', UUID(as_uuid=True), comment='料宽公式ID'),
        sa.Column('per_piece_formula_id', UUID(as_uuid=True), comment='元/个公式ID'),
        sa.Column('dimension_description', sa.String(200), comment='尺寸维度'),
        sa.Column('sort_order', sa.Integer, default=0, comment='排序'),
        sa.Column('description', sa.Text, comment='描述'),
        sa.Column('is_enabled', sa.Boolean, default=True, comment='是否启用'),
        sa.Column('created_by', UUID(as_uuid=True), nullable=False, comment='创建人'),
        sa.Column('updated_by', UUID(as_uuid=True), comment='修改人'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now(), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now(), comment='更新时间'),
    )
    
    # 创建索引
    op.create_index('idx_bag_related_formulas_bag_type_id', 'bag_related_formulas', ['bag_type_id'])
    op.create_index('idx_bag_related_formulas_sort_order', 'bag_related_formulas', ['sort_order'])


def downgrade():
    # 删除索引
    op.drop_index('idx_bag_related_formulas_sort_order', 'bag_related_formulas')
    op.drop_index('idx_bag_related_formulas_bag_type_id', 'bag_related_formulas')
    
    # 删除表
    op.drop_table('bag_related_formulas') 