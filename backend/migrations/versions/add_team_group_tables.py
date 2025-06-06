"""Add team group tables

Revision ID: add_team_group_tables
Revises: 
Create Date: 2024-01-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_team_group_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 创建班组管理表
    op.create_table('team_groups',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('team_code', sa.String(length=50), nullable=False),
        sa.Column('team_name', sa.String(length=100), nullable=False),
        sa.Column('circulation_card_id', sa.String(length=50), nullable=True),
        sa.Column('day_shift_hours', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column('night_shift_hours', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column('rotating_shift_hours', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=True),
        sa.Column('is_enabled', sa.Boolean(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('team_code'),
        comment='班组管理表'
    )
    op.create_index('idx_team_groups_team_code', 'team_groups', ['team_code'])
    op.create_index('idx_team_groups_team_name', 'team_groups', ['team_name'])

    # 创建班组人员表
    op.create_table('team_group_members',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('team_group_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('piece_rate_percentage', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('saving_bonus_percentage', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['team_group_id'], ['team_groups.id'], ),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('team_group_id', 'employee_id', name='uq_team_group_employee'),
        comment='班组人员表'
    )
    op.create_index('idx_team_group_members_team_id', 'team_group_members', ['team_group_id'])
    op.create_index('idx_team_group_members_employee_id', 'team_group_members', ['employee_id'])

    # 创建班组机台表
    op.create_table('team_group_machines',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('team_group_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('machine_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['team_group_id'], ['team_groups.id'], ),
        sa.ForeignKeyConstraint(['machine_id'], ['machines.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('team_group_id', 'machine_id', name='uq_team_group_machine'),
        comment='班组机台表'
    )
    op.create_index('idx_team_group_machines_team_id', 'team_group_machines', ['team_group_id'])
    op.create_index('idx_team_group_machines_machine_id', 'team_group_machines', ['machine_id'])

    # 创建班组工序分类表
    op.create_table('team_group_processes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('team_group_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('process_category_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['team_group_id'], ['team_groups.id'], ),
        sa.ForeignKeyConstraint(['process_category_id'], ['process_categories.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('team_group_id', 'process_category_id', name='uq_team_group_process'),
        comment='班组工序分类表'
    )
    op.create_index('idx_team_group_processes_team_id', 'team_group_processes', ['team_group_id'])
    op.create_index('idx_team_group_processes_process_id', 'team_group_processes', ['process_category_id'])


def downgrade():
    # 删除表（按相反顺序）
    op.drop_table('team_group_processes')
    op.drop_table('team_group_machines')
    op.drop_table('team_group_members')
    op.drop_table('team_groups') 