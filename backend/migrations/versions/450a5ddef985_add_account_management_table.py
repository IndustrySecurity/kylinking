"""Add account management table

Revision ID: 450a5ddef985
Revises: b708d73eee9c
Create Date: 2025-05-27 13:14:35.141042

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '450a5ddef985'
down_revision = 'b708d73eee9c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('account_management',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('account_name', sa.String(length=200), nullable=False, comment='账户名称'),
    sa.Column('account_type', sa.String(length=50), nullable=False, comment='账户类型'),
    sa.Column('currency_id', sa.UUID(), nullable=True, comment='币别ID'),
    sa.Column('bank_name', sa.String(length=200), nullable=True, comment='开户银行'),
    sa.Column('bank_account', sa.String(length=100), nullable=True, comment='银行账户'),
    sa.Column('opening_date', sa.Date(), nullable=True, comment='开户日期'),
    sa.Column('opening_address', sa.String(length=500), nullable=True, comment='开户地址'),
    sa.Column('description', sa.Text(), nullable=True, comment='描述'),
    sa.Column('sort_order', sa.Integer(), nullable=True, comment='显示排序'),
    sa.Column('is_enabled', sa.Boolean(), nullable=True, comment='是否启用'),
    sa.Column('created_by', sa.UUID(), nullable=False, comment='创建人'),
    sa.Column('updated_by', sa.UUID(), nullable=True, comment='修改人'),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('settlement_methods',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('settlement_name', sa.String(length=100), nullable=False, comment='结算方式'),
    sa.Column('description', sa.Text(), nullable=True, comment='描述'),
    sa.Column('sort_order', sa.Integer(), nullable=True, comment='显示排序'),
    sa.Column('is_enabled', sa.Boolean(), nullable=True, comment='是否启用'),
    sa.Column('created_by', sa.UUID(), nullable=False, comment='创建人'),
    sa.Column('updated_by', sa.UUID(), nullable=True, comment='修改人'),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tax_rates',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tax_name', sa.String(length=100), nullable=False, comment='税收'),
    sa.Column('tax_rate', sa.Numeric(precision=5, scale=2), nullable=False, comment='税率%'),
    sa.Column('is_default', sa.Boolean(), nullable=True, comment='评审默认'),
    sa.Column('description', sa.Text(), nullable=True, comment='描述'),
    sa.Column('sort_order', sa.Integer(), nullable=True, comment='显示排序'),
    sa.Column('is_enabled', sa.Boolean(), nullable=True, comment='是否启用'),
    sa.Column('created_by', sa.UUID(), nullable=False, comment='创建人'),
    sa.Column('updated_by', sa.UUID(), nullable=True, comment='修改人'),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tax_rates')
    op.drop_table('settlement_methods')
    op.drop_table('account_management')
    # ### end Alembic commands ###
