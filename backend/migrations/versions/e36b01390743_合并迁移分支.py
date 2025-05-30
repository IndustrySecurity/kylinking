"""合并迁移分支

Revision ID: e36b01390743
Revises: 2cb76157aa48, 5f3341bc0ea6
Create Date: 2025-05-30 10:45:47.203596

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e36b01390743'
down_revision = ('2cb76157aa48', '5f3341bc0ea6')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
