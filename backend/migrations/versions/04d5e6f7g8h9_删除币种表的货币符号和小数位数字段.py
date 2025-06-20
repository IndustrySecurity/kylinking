"""删除币种表的货币符号和小数位数字段

Revision ID: 04d5e6f7g8h9
Revises: 03cee9bf8bac
Create Date: 2025-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '04d5e6f7g8h9'
down_revision = '03cee9bf8bac'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('currencies', schema=None) as batch_op:
        batch_op.drop_column('symbol')
        batch_op.drop_column('decimal_places')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('currencies', schema=None) as batch_op:
        batch_op.add_column(sa.Column('decimal_places', sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column('symbol', sa.VARCHAR(length=10), nullable=True))
    # ### end Alembic commands ### 