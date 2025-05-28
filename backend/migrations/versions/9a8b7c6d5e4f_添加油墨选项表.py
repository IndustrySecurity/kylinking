"""添加油墨选项表

Revision ID: 9a8b7c6d5e4f
Revises: 404f7c3661ce
Create Date: 2025-01-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '9a8b7c6d5e4f'
down_revision = '404f7c3661ce'
branch_labels = None
depends_on = None


def upgrade():
    """创建油墨选项表"""
    # 在每个租户schema中创建油墨选项表
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
                -- 在每个租户schema中创建油墨选项表
                EXECUTE format('
                    CREATE TABLE IF NOT EXISTS %I.ink_options (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        option_name VARCHAR(100) NOT NULL,
                        sort_order INTEGER DEFAULT 0,
                        is_enabled BOOLEAN DEFAULT TRUE,
                        description TEXT,
                        created_by UUID NOT NULL,
                        updated_by UUID,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                ', schema_name);
                
                EXECUTE format('
                    COMMENT ON TABLE %I.ink_options IS ''油墨选项表'';
                    COMMENT ON COLUMN %I.ink_options.option_name IS ''选项名称'';
                    COMMENT ON COLUMN %I.ink_options.sort_order IS ''显示排序'';
                    COMMENT ON COLUMN %I.ink_options.is_enabled IS ''是否启用'';
                    COMMENT ON COLUMN %I.ink_options.description IS ''描述'';
                    COMMENT ON COLUMN %I.ink_options.created_by IS ''创建人'';
                    COMMENT ON COLUMN %I.ink_options.updated_by IS ''修改人'';
                    COMMENT ON COLUMN %I.ink_options.created_at IS ''创建时间'';
                    COMMENT ON COLUMN %I.ink_options.updated_at IS ''修改时间'';
                ', schema_name, schema_name, schema_name, schema_name, schema_name, schema_name, schema_name, schema_name, schema_name, schema_name, schema_name, schema_name);
                
                EXECUTE format('
                    CREATE INDEX IF NOT EXISTS idx_ink_options_option_name ON %I.ink_options(option_name);
                    CREATE INDEX IF NOT EXISTS idx_ink_options_option_type ON %I.ink_options(option_type);
                    CREATE INDEX IF NOT EXISTS idx_ink_options_sort_order ON %I.ink_options(sort_order);
                    CREATE INDEX IF NOT EXISTS idx_ink_options_is_enabled ON %I.ink_options(is_enabled);
                    CREATE INDEX IF NOT EXISTS idx_ink_options_created_at ON %I.ink_options(created_at);
                ', schema_name, schema_name, schema_name, schema_name, schema_name);
                
                EXECUTE format('
                    CREATE OR REPLACE FUNCTION %I.update_ink_options_updated_at()
                    RETURNS TRIGGER AS $trigger$
                    BEGIN
                        NEW.updated_at = CURRENT_TIMESTAMP;
                        RETURN NEW;
                    END;
                    $trigger$ LANGUAGE plpgsql;
                ', schema_name);
                
                EXECUTE format('
                    DROP TRIGGER IF EXISTS trigger_update_ink_options_updated_at ON %I.ink_options;
                    CREATE TRIGGER trigger_update_ink_options_updated_at
                        BEFORE UPDATE ON %I.ink_options
                        FOR EACH ROW
                        EXECUTE FUNCTION %I.update_ink_options_updated_at();
                ', schema_name, schema_name, schema_name);
            END LOOP;
        END $$;
    """)


def downgrade():
    """删除油墨选项表"""
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
                -- 删除每个租户schema中的油墨选项表
                EXECUTE format('
                    DROP TRIGGER IF EXISTS trigger_update_ink_options_updated_at ON %I.ink_options;
                    DROP FUNCTION IF EXISTS %I.update_ink_options_updated_at();
                    DROP TABLE IF EXISTS %I.ink_options;
                ', schema_name, schema_name, schema_name);
            END LOOP;
        END $$;
    """) 