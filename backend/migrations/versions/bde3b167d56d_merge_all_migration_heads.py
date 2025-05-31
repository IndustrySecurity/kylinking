"""Merge all migration heads

Revision ID: bde3b167d56d
Revises: 37d3eb7e9f6e, 6ae529a9934a, add_product_categories_table, add_quote_accessories_table, add_quote_inks_table, add_quote_materials_table, ddc393b778ab
Create Date: 2025-05-31 08:15:05.428620

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bde3b167d56d'
down_revision = ('37d3eb7e9f6e', '6ae529a9934a', 'add_product_categories_table', 'add_quote_accessories_table', 'add_quote_inks_table', 'add_quote_materials_table', 'ddc393b778ab')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
