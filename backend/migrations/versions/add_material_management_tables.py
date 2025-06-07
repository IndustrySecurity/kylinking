"""添加材料管理相关表

Revision ID: add_material_management_tables
Revises: bde3b167d56d
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_material_management_tables'
down_revision = 'bde3b167d56d'
branch_labels = None
depends_on = None


def upgrade():
    # 创建材料管理主表
    op.execute("SET search_path TO mytenant")
    
    op.create_table('material_management',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        
        # 基本信息字段
        sa.Column('material_code', sa.String(length=50), nullable=True, comment='材料编号'),
        sa.Column('material_name', sa.String(length=255), nullable=False, comment='材料名称'),
        sa.Column('material_category_id', postgresql.UUID(as_uuid=True), nullable=True, comment='材料分类ID'),
        sa.Column('material_attribute', sa.String(length=50), nullable=True, comment='材料属性'),
        sa.Column('unit_id', postgresql.UUID(as_uuid=True), nullable=True, comment='单位ID'),
        sa.Column('auxiliary_unit_id', postgresql.UUID(as_uuid=True), nullable=True, comment='辅助单位ID'),
        
        # 布尔字段
        sa.Column('is_blown_film', sa.Boolean(), nullable=True, default=False, comment='是否吹膜'),
        sa.Column('unit_no_conversion', sa.Boolean(), nullable=True, default=False, comment='单位不换算'),
        
        # 尺寸字段
        sa.Column('width_mm', sa.Numeric(precision=10, scale=3), nullable=True, comment='宽mm'),
        sa.Column('thickness_um', sa.Numeric(precision=10, scale=3), nullable=True, comment='厚μm'),
        sa.Column('specification_model', sa.String(length=200), nullable=True, comment='规格型号'),
        sa.Column('density', sa.Numeric(precision=10, scale=4), nullable=True, comment='密度'),
        
        # 其他字段
        sa.Column('conversion_factor', sa.Numeric(precision=10, scale=4), nullable=True, default=1, comment='换算系数'),
        sa.Column('sales_unit_id', postgresql.UUID(as_uuid=True), nullable=True, comment='销售单位ID'),
        sa.Column('inspection_type', sa.String(length=20), nullable=True, default='spot_check', comment='检验类型'),
        sa.Column('is_paper', sa.Boolean(), nullable=True, default=False, comment='是否卷纸'),
        sa.Column('is_surface_printing_ink', sa.Boolean(), nullable=True, default=False, comment='表印油墨'),
        sa.Column('length_mm', sa.Numeric(precision=10, scale=3), nullable=True, comment='长mm'),
        sa.Column('height_mm', sa.Numeric(precision=10, scale=3), nullable=True, comment='高mm'),
        
        # 库存管理字段
        sa.Column('min_stock_start', sa.Numeric(precision=15, scale=3), nullable=True, comment='最小库存(起)'),
        sa.Column('min_stock_end', sa.Numeric(precision=15, scale=3), nullable=True, comment='最小库存(止)'),
        sa.Column('max_stock', sa.Numeric(precision=15, scale=3), nullable=True, comment='最大库存'),
        sa.Column('shelf_life_days', sa.Integer(), nullable=True, comment='保质期/天'),
        sa.Column('warning_days', sa.Integer(), nullable=True, default=0, comment='预警天数'),
        sa.Column('standard_m_per_roll', sa.Numeric(precision=10, scale=3), nullable=True, default=0, comment='标准m/卷'),
        
        # 更多属性字段
        sa.Column('is_carton', sa.Boolean(), nullable=True, default=False, comment='是否纸箱'),
        sa.Column('is_uv_ink', sa.Boolean(), nullable=True, default=False, comment='UV油墨'),
        sa.Column('wind_tolerance_mm', sa.Numeric(precision=10, scale=3), nullable=True, default=0, comment='风差mm'),
        sa.Column('tongue_mm', sa.Numeric(precision=10, scale=3), nullable=True, default=0, comment='舌头mm'),
        
        # 价格字段
        sa.Column('purchase_price', sa.Numeric(precision=15, scale=4), nullable=True, default=0, comment='采购价'),
        sa.Column('latest_purchase_price', sa.Numeric(precision=15, scale=4), nullable=True, default=0, comment='最近采购价'),
        sa.Column('latest_tax_included_price', sa.Numeric(precision=15, scale=4), nullable=True, comment='最近含税单价'),
        
        # 选择字段
        sa.Column('material_formula_id', postgresql.UUID(as_uuid=True), nullable=True, comment='用料公式ID'),
        sa.Column('is_paper_core', sa.Boolean(), nullable=True, default=False, comment='是否纸芯'),
        sa.Column('is_tube_film', sa.Boolean(), nullable=True, default=False, comment='是否筒膜'),
        
        # 损耗字段
        sa.Column('loss_1', sa.Numeric(precision=10, scale=4), nullable=True, comment='损耗1'),
        sa.Column('loss_2', sa.Numeric(precision=10, scale=4), nullable=True, comment='损耗2'),
        sa.Column('forward_formula', sa.String(length=200), nullable=True, comment='正算公式'),
        sa.Column('reverse_formula', sa.String(length=200), nullable=True, comment='反算公式'),
        sa.Column('sales_price', sa.Numeric(precision=15, scale=4), nullable=True, comment='销售价'),
        sa.Column('subject_id', postgresql.UUID(as_uuid=True), nullable=True, comment='科目ID'),
        sa.Column('uf_code', sa.String(length=100), nullable=True, comment='用友编码'),
        
        # 更多布尔字段
        sa.Column('material_formula_reverse', sa.Boolean(), nullable=True, default=False, comment='用料公式反算'),
        sa.Column('is_hot_stamping', sa.Boolean(), nullable=True, default=False, comment='是否烫金'),
        sa.Column('material_position', sa.String(length=200), nullable=True, comment='材料位置'),
        sa.Column('carton_spec_volume', sa.Numeric(precision=15, scale=6), nullable=True, comment='纸箱规格体积'),
        sa.Column('security_code', sa.String(length=100), nullable=True, comment='保密编码'),
        sa.Column('substitute_material_category_id', postgresql.UUID(as_uuid=True), nullable=True, comment='替代材料分类ID'),
        sa.Column('scan_batch', sa.String(length=100), nullable=True, comment='扫码批次'),
        
        # 最后的布尔字段
        sa.Column('is_woven_bag', sa.Boolean(), nullable=True, default=False, comment='是否编织袋'),
        sa.Column('is_zipper', sa.Boolean(), nullable=True, default=False, comment='是否拉链'),
        sa.Column('remarks', sa.Text(), nullable=True, comment='备注'),
        sa.Column('is_self_made', sa.Boolean(), nullable=True, default=False, comment='是否自制'),
        sa.Column('no_interface', sa.Boolean(), nullable=True, default=False, comment='不对接'),
        sa.Column('cost_object_required', sa.Boolean(), nullable=True, default=False, comment='成本对象必填'),
        
        # 标准字段
        sa.Column('sort_order', sa.Integer(), nullable=True, default=0, comment='显示排序'),
        sa.Column('is_enabled', sa.Boolean(), nullable=True, default=True, comment='是否启用'),
        
        # 审计字段
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False, comment='创建人'),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True, comment='修改人'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        schema='mytenant'
    )

    # 创建材料属性子表
    op.create_table('material_management_properties',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('material_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('property_name', sa.String(length=100), nullable=True, comment='属性名称'),
        sa.Column('property_value', sa.String(length=255), nullable=True, comment='属性值'),
        sa.Column('property_unit', sa.String(length=50), nullable=True, comment='属性单位'),
        sa.Column('sort_order', sa.Integer(), nullable=True, default=0, comment='排序'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['material_id'], ['mytenant.material_management.id']),
        sa.PrimaryKeyConstraint('id'),
        schema='mytenant'
    )

    # 创建材料供应商子表
    op.create_table('material_management_suppliers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('material_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('supplier_id', postgresql.UUID(as_uuid=True), nullable=True, comment='供应商ID'),
        sa.Column('supplier_material_code', sa.String(length=100), nullable=True, comment='供应商材料编码'),
        sa.Column('supplier_price', sa.Numeric(precision=15, scale=4), nullable=True, comment='供应商价格'),
        sa.Column('is_primary', sa.Boolean(), nullable=True, default=False, comment='是否主供应商'),
        sa.Column('delivery_days', sa.Integer(), nullable=True, comment='交货天数'),
        sa.Column('sort_order', sa.Integer(), nullable=True, default=0, comment='排序'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['material_id'], ['mytenant.material_management.id']),
        sa.PrimaryKeyConstraint('id'),
        schema='mytenant'
    )

    # 创建索引
    op.create_index('idx_material_management_code', 'material_management', ['material_code'], unique=False, schema='mytenant')
    op.create_index('idx_material_management_name', 'material_management', ['material_name'], unique=False, schema='mytenant')
    op.create_index('idx_material_management_category', 'material_management', ['material_category_id'], unique=False, schema='mytenant')
    op.create_index('idx_material_management_enabled', 'material_management', ['is_enabled'], unique=False, schema='mytenant')
    

def downgrade():
    op.execute("SET search_path TO mytenant")
    
    # 删除索引
    op.drop_index('idx_material_management_enabled', table_name='material_management', schema='mytenant')
    op.drop_index('idx_material_management_category', table_name='material_management', schema='mytenant')
    op.drop_index('idx_material_management_name', table_name='material_management', schema='mytenant')
    op.drop_index('idx_material_management_code', table_name='material_management', schema='mytenant')
    
    # 删除表
    op.drop_table('material_management_suppliers', schema='mytenant')
    op.drop_table('material_management_properties', schema='mytenant')
    op.drop_table('material_management', schema='mytenant') 