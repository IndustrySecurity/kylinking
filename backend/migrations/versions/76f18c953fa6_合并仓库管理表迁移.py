"""合并仓库管理表迁移

Revision ID: 76f18c953fa6
Revises: 4e79b51d9b6e, a7b8c9d0e1f2
Create Date: 2025-06-01 03:16:35.059334

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '76f18c953fa6'
down_revision = ('4e79b51d9b6e', 'a7b8c9d0e1f2')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
