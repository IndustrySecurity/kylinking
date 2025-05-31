"""add quote_inks table

Revision ID: add_quote_inks_table
Revises: add_machines_table
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_quote_inks_table'
down_revision = 'add_machines_table'
branch_labels = None
depends_on = None


def upgrade():
    """创建报价油墨表"""
    # 获取所有租户schema
    connection = op.get_bind()
    
    # 查询所有租户schema
    result = connection.execute(sa.text("""
        SELECT schema_name 
        FROM information_schema.schemata 
        WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast', 'public')
        AND schema_name NOT LIKE 'pg_%'
    """))
    
    schemas = [row[0] for row in result.fetchall()]
    
    # 为每个租户schema创建表
    for schema in schemas:
        # 设置search_path
        connection.execute(sa.text(f"SET search_path TO {schema}, public"))
        
        # 创建报价油墨表
        op.create_table('quote_inks',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('category_name', sa.String(length=100), nullable=False, comment='分类名称'),
            sa.Column('square_price', sa.Numeric(precision=10, scale=4), nullable=True, comment='平方价'),
            sa.Column('unit_price_formula', sa.String(length=200), nullable=True, comment='单价计算公式'),
            sa.Column('gram_weight', sa.Numeric(precision=10, scale=4), nullable=True, comment='克重'),
            sa.Column('is_ink', sa.Boolean(), nullable=True, comment='油墨'),
            sa.Column('is_solvent', sa.Boolean(), nullable=True, comment='溶剂'),
            sa.Column('sort_order', sa.Integer(), nullable=True, comment='排序'),
            sa.Column('description', sa.Text(), nullable=True, comment='描述'),
            sa.Column('is_enabled', sa.Boolean(), nullable=True, comment='是否启用'),
            sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False, comment='创建人'),
            sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True, comment='修改人'),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            schema=schema
        )
        
        # 创建索引
        op.create_index(f'ix_{schema}_quote_inks_category_name', 'quote_inks', ['category_name'], unique=False, schema=schema)
        op.create_index(f'ix_{schema}_quote_inks_is_enabled', 'quote_inks', ['is_enabled'], unique=False, schema=schema)
        op.create_index(f'ix_{schema}_quote_inks_sort_order', 'quote_inks', ['sort_order'], unique=False, schema=schema)
        
        # 添加表注释
        connection.execute(sa.text(f"COMMENT ON TABLE {schema}.quote_inks IS '报价油墨表'"))
    
    # 恢复默认search_path
    connection.execute(sa.text("SET search_path TO public"))


def downgrade():
    """删除报价油墨表"""
    # 获取所有租户schema
    connection = op.get_bind()
    
    # 查询所有租户schema
    result = connection.execute(sa.text("""
        SELECT schema_name 
        FROM information_schema.schemata 
        WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast', 'public')
        AND schema_name NOT LIKE 'pg_%'
    """))
    
    schemas = [row[0] for row in result.fetchall()]
    
    # 为每个租户schema删除表
    for schema in schemas:
        # 设置search_path
        connection.execute(sa.text(f"SET search_path TO {schema}, public"))
        
        # 删除索引
        op.drop_index(f'ix_{schema}_quote_inks_sort_order', table_name='quote_inks', schema=schema)
        op.drop_index(f'ix_{schema}_quote_inks_is_enabled', table_name='quote_inks', schema=schema)
        op.drop_index(f'ix_{schema}_quote_inks_category_name', table_name='quote_inks', schema=schema)
        
        # 删除表
        op.drop_table('quote_inks', schema=schema)
    
    # 恢复默认search_path
    connection.execute(sa.text("SET search_path TO public")) 