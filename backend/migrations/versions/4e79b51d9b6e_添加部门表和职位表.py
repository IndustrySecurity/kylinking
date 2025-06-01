"""添加部门表和职位表

Revision ID: 4e79b51d9b6e
Revises: bde3b167d56d
Create Date: 2025-06-01 09:54:22.092339

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '4e79b51d9b6e'
down_revision = 'bde3b167d56d'
branch_labels = None
depends_on = None


def upgrade():
    """添加部门表和职位表到所有租户schema"""
    
    # 获取所有租户schema
    connection = op.get_bind()
    result = connection.execute(sa.text("""
        SELECT schema_name 
        FROM system.tenants 
        WHERE schema_name != 'public'
    """))
    
    tenant_schemas = [row[0] for row in result]
    
    # 为每个租户schema创建部门表和职位表
    for schema in tenant_schemas:
        # 设置search_path
        connection.execute(sa.text(f"SET search_path TO {schema}, public"))
        
        # 创建部门表
        op.create_table('departments',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('dept_code', sa.String(length=50), nullable=False),
            sa.Column('dept_name', sa.String(length=100), nullable=False),
            sa.Column('parent_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('is_blown_film', sa.Boolean(), nullable=True, default=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('sort_order', sa.Integer(), nullable=True, default=0),
            sa.Column('is_enabled', sa.Boolean(), nullable=True, default=True),
            sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['parent_id'], [f'{schema}.departments.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('dept_code'),
            schema=schema
        )
        
        # 创建职位表
        op.create_table('positions',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('position_name', sa.String(length=100), nullable=False),
            sa.Column('department_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('parent_position_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('hourly_wage', sa.Numeric(precision=10, scale=2), nullable=True),
            sa.Column('standard_pass_rate', sa.Numeric(precision=5, scale=2), nullable=True),
            sa.Column('is_supervisor', sa.Boolean(), nullable=True, default=False),
            sa.Column('is_machine_operator', sa.Boolean(), nullable=True, default=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('sort_order', sa.Integer(), nullable=True, default=0),
            sa.Column('is_enabled', sa.Boolean(), nullable=True, default=True),
            sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['department_id'], [f'{schema}.departments.id'], ),
            sa.ForeignKeyConstraint(['parent_position_id'], [f'{schema}.positions.id'], ),
            sa.PrimaryKeyConstraint('id'),
            schema=schema
        )
    
    # 恢复search_path
    connection.execute(sa.text("SET search_path TO public"))


def downgrade():
    """删除部门表和职位表"""
    
    # 获取所有租户schema
    connection = op.get_bind()
    result = connection.execute(sa.text("""
        SELECT schema_name 
        FROM system.tenants 
        WHERE schema_name != 'public'
    """))
    
    tenant_schemas = [row[0] for row in result]
    
    # 为每个租户schema删除表
    for schema in tenant_schemas:
        # 设置search_path
        connection.execute(sa.text(f"SET search_path TO {schema}, public"))
        
        # 删除职位表（先删除，因为有外键依赖）
        op.drop_table('positions', schema=schema)
        
        # 删除部门表
        op.drop_table('departments', schema=schema)
    
    # 恢复search_path
    connection.execute(sa.text("SET search_path TO public"))
