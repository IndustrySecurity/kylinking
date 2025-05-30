"""创建报价运费表

Revision ID: 5f3341bc0ea6
Revises: 9a8b7c6d5e4f
Create Date: 2025-05-28 06:44:15.966004

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5f3341bc0ea6'
down_revision = '9a8b7c6d5e4f'
branch_labels = None
depends_on = None


def upgrade():
    """在所有租户schema中创建报价运费表"""
    op.execute("""
        DO $$
        DECLARE
            schema_name text;
        BEGIN
            -- 获取所有租户schema
            FOR schema_name IN 
                SELECT nspname 
                FROM pg_namespace 
                WHERE nspname NOT IN ('information_schema', 'pg_catalog', 'pg_toast', 'public')
                AND nspname NOT LIKE 'pg_temp_%'
                AND nspname NOT LIKE 'pg_toast_temp_%'
            LOOP
                -- 在每个租户schema中创建报价运费表
                EXECUTE format('
                    CREATE TABLE IF NOT EXISTS %I.quote_freights (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        region VARCHAR(100) NOT NULL,
                        percentage NUMERIC(5, 2) NOT NULL DEFAULT 0,
                        sort_order INTEGER DEFAULT 0,
                        is_enabled BOOLEAN DEFAULT TRUE,
                        description TEXT,
                        created_by UUID NOT NULL,
                        updated_by UUID,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                ', schema_name);
                
                -- 添加注释
                EXECUTE format('
                    COMMENT ON TABLE %I.quote_freights IS ''报价运费表'';
                    COMMENT ON COLUMN %I.quote_freights.id IS ''主键ID'';
                    COMMENT ON COLUMN %I.quote_freights.region IS ''区域'';
                    COMMENT ON COLUMN %I.quote_freights.percentage IS ''百分比'';
                    COMMENT ON COLUMN %I.quote_freights.sort_order IS ''显示排序'';
                    COMMENT ON COLUMN %I.quote_freights.is_enabled IS ''是否启用'';
                    COMMENT ON COLUMN %I.quote_freights.description IS ''描述'';
                    COMMENT ON COLUMN %I.quote_freights.created_by IS ''创建人'';
                    COMMENT ON COLUMN %I.quote_freights.updated_by IS ''修改人'';
                    COMMENT ON COLUMN %I.quote_freights.created_at IS ''创建时间'';
                    COMMENT ON COLUMN %I.quote_freights.updated_at IS ''更新时间'';
                ', schema_name, schema_name, schema_name, schema_name, schema_name, schema_name, schema_name, schema_name, schema_name, schema_name, schema_name);
                
                -- 创建索引
                EXECUTE format('
                    CREATE INDEX IF NOT EXISTS idx_%I_quote_freights_region ON %I.quote_freights(region);
                    CREATE INDEX IF NOT EXISTS idx_%I_quote_freights_enabled ON %I.quote_freights(is_enabled);
                    CREATE INDEX IF NOT EXISTS idx_%I_quote_freights_sort ON %I.quote_freights(sort_order);
                ', schema_name, schema_name, schema_name, schema_name, schema_name, schema_name);
                
            END LOOP;
        END $$;
    """)


def downgrade():
    """删除所有租户schema中的报价运费表"""
    op.execute("""
        DO $$
        DECLARE
            schema_name text;
        BEGIN
            -- 获取所有租户schema
            FOR schema_name IN 
                SELECT nspname 
                FROM pg_namespace 
                WHERE nspname NOT IN ('information_schema', 'pg_catalog', 'pg_toast', 'public')
                AND nspname NOT LIKE 'pg_temp_%'
                AND nspname NOT LIKE 'pg_toast_temp_%'
            LOOP
                -- 删除每个租户schema中的报价运费表
                EXECUTE format('DROP TABLE IF EXISTS %I.quote_freights CASCADE;', schema_name);
            END LOOP;
        END $$;
    """)
