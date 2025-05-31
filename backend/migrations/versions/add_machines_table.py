"""添加机台表

Revision ID: add_machines_table
Revises: accc08d20e83
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_machines_table'
down_revision = 'accc08d20e83'
branch_labels = None
depends_on = None


def upgrade():
    """添加机台表到所有租户schema"""
    
    # 获取所有租户schema
    connection = op.get_bind()
    result = connection.execute(sa.text("""
        SELECT schema_name 
        FROM information_schema.schemata 
        WHERE schema_name LIKE 'tenant_%'
    """))
    
    tenant_schemas = [row[0] for row in result]
    
    # 为每个租户schema创建机台表
    for schema in tenant_schemas:
        # 设置search_path
        connection.execute(sa.text(f"SET search_path TO {schema}, public"))
        
        # 创建机台表
        op.create_table('machines',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('machine_code', sa.String(length=50), nullable=False, comment='机台编号(自动生成)'),
            sa.Column('machine_name', sa.String(length=100), nullable=False, comment='机台名称'),
            sa.Column('model', sa.String(length=100), nullable=True, comment='型号'),
            sa.Column('min_width', sa.Numeric(precision=10, scale=2), nullable=True, comment='最小上机门幅(mm)'),
            sa.Column('max_width', sa.Numeric(precision=10, scale=2), nullable=True, comment='最大上机门幅(mm)'),
            sa.Column('production_speed', sa.Numeric(precision=10, scale=2), nullable=True, comment='生产均速(m/h)'),
            sa.Column('preparation_time', sa.Numeric(precision=8, scale=2), nullable=True, comment='准备时间(h)'),
            sa.Column('difficulty_factor', sa.Numeric(precision=8, scale=4), nullable=True, comment='难易系数'),
            sa.Column('circulation_card_id', sa.String(length=100), nullable=True, comment='流转卡标识'),
            sa.Column('max_colors', sa.Integer(), nullable=True, comment='最大印色'),
            sa.Column('kanban_display', sa.String(length=200), nullable=True, comment='看板显示'),
            sa.Column('capacity_formula', sa.String(length=200), nullable=True, comment='产能公式'),
            sa.Column('gas_unit_price', sa.Numeric(precision=10, scale=4), nullable=True, comment='燃气单价'),
            sa.Column('power_consumption', sa.Numeric(precision=10, scale=2), nullable=True, comment='功耗(kw)'),
            sa.Column('electricity_cost_per_hour', sa.Numeric(precision=10, scale=4), nullable=True, comment='电费(/h)'),
            sa.Column('output_conversion_factor', sa.Numeric(precision=8, scale=4), nullable=True, comment='产量换算倍数'),
            sa.Column('plate_change_time', sa.Numeric(precision=8, scale=2), nullable=True, comment='换版时间'),
            sa.Column('mes_barcode_prefix', sa.String(length=20), nullable=True, comment='MES条码前缀'),
            sa.Column('is_curing_room', sa.Boolean(), nullable=True, default=False, comment='是否熟化室'),
            sa.Column('material_name', sa.String(length=200), nullable=True, comment='材料名称'),
            sa.Column('remarks', sa.Text(), nullable=True, comment='备注'),
            sa.Column('sort_order', sa.Integer(), nullable=True, default=0, comment='显示排序'),
            sa.Column('is_enabled', sa.Boolean(), nullable=True, default=True, comment='是否启用'),
            sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False, comment='创建人'),
            sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True, comment='修改人'),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('machine_code'),
            schema=schema
        )
        
        # 添加索引
        op.create_index(f'ix_{schema}_machines_machine_name', 'machines', ['machine_name'], unique=False, schema=schema)
        op.create_index(f'ix_{schema}_machines_is_enabled', 'machines', ['is_enabled'], unique=False, schema=schema)
        op.create_index(f'ix_{schema}_machines_sort_order', 'machines', ['sort_order'], unique=False, schema=schema)
        
        # 添加表注释
        connection.execute(sa.text(f"COMMENT ON TABLE {schema}.machines IS '机台管理表'"))
    
    # 重置search_path
    connection.execute(sa.text("SET search_path TO public"))


def downgrade():
    """删除机台表"""
    
    # 获取所有租户schema
    connection = op.get_bind()
    result = connection.execute(sa.text("""
        SELECT schema_name 
        FROM information_schema.schemata 
        WHERE schema_name LIKE 'tenant_%'
    """))
    
    tenant_schemas = [row[0] for row in result]
    
    # 为每个租户schema删除机台表
    for schema in tenant_schemas:
        # 设置search_path
        connection.execute(sa.text(f"SET search_path TO {schema}, public"))
        
        # 删除表
        op.drop_table('machines', schema=schema)
    
    # 重置search_path
    connection.execute(sa.text("SET search_path TO public")) 