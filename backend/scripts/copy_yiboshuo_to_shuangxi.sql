-- 将yiboshuo schema中的表结构复制到shuangxi schema（不复制数据）
-- 文件名: copy_yiboshuo_to_shuangxi.sql

-- 设置搜索路径
SET search_path TO shuangxi, yiboshuo, public;

-- 先删除shuangxi schema的所有内容
DROP SCHEMA IF EXISTS shuangxi CASCADE;

-- 重新创建shuangxi schema
CREATE SCHEMA shuangxi;

-- 创建UUID扩展（如果不存在）
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 获取yiboshuo schema中的所有表并复制表结构到shuangxi schema
DO $$
DECLARE
    table_record RECORD;
    create_table_sql TEXT;
    index_sql TEXT;
    constraint_sql TEXT;
    trigger_sql TEXT;
BEGIN
    -- 遍历yiboshuo schema中的所有表
    FOR table_record IN 
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'yiboshuo'
        ORDER BY tablename
    LOOP
        RAISE NOTICE '正在复制表结构: %', table_record.tablename;
        
        -- 1. 创建表结构（只复制结构，不复制数据）
        SELECT format('CREATE TABLE shuangxi.%I (LIKE yiboshuo.%I INCLUDING ALL)', 
                      table_record.tablename, table_record.tablename)
        INTO create_table_sql;
        
        EXECUTE create_table_sql;
        
        -- 2. 复制索引（除了主键索引，因为LIKE INCLUDING ALL已经包含了）
        FOR index_sql IN
            SELECT format('CREATE INDEX IF NOT EXISTS %I ON shuangxi.%I (%s)', 
                         indexname, table_record.tablename, 
                         substring(indexdef from 'ON [^)]+\(([^)]+)\)'))
            FROM pg_indexes 
            WHERE schemaname = 'yiboshuo' 
              AND tablename = table_record.tablename
              AND indexname NOT LIKE '%_pkey'
        LOOP
            BEGIN
                EXECUTE index_sql;
            EXCEPTION WHEN OTHERS THEN
                RAISE NOTICE '创建索引失败: %', index_sql;
            END;
        END LOOP;
        
        -- 3. 复制外键约束
        FOR constraint_sql IN
            SELECT format('ALTER TABLE shuangxi.%I ADD CONSTRAINT %I %s', 
                         table_record.tablename, conname,
                         substring(pg_get_constraintdef(oid) from 'FOREIGN KEY.*'))
            FROM pg_constraint 
            WHERE conrelid = (table_record.tablename::regclass::oid)
              AND contype = 'f'
        LOOP
            BEGIN
                EXECUTE constraint_sql;
            EXCEPTION WHEN OTHERS THEN
                RAISE NOTICE '创建外键约束失败: %', constraint_sql;
            END;
        END LOOP;
        
        -- 4. 复制触发器
        FOR trigger_sql IN
            SELECT format('CREATE TRIGGER %I %s ON shuangxi.%I %s', 
                         tgname, tgtype, table_record.tablename, tgdeferrable)
            FROM pg_trigger 
            WHERE tgrelid = (table_record.tablename::regclass::oid)
              AND NOT tgisinternal
        LOOP
            BEGIN
                EXECUTE trigger_sql;
            EXCEPTION WHEN OTHERS THEN
                RAISE NOTICE '创建触发器失败: %', trigger_sql;
            END;
        END LOOP;
        
    END LOOP;
END $$;

-- 创建更新时间触发器函数（如果不存在）
CREATE OR REPLACE FUNCTION shuangxi.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为所有表添加更新时间触发器
DO $$
DECLARE
    table_name text;
BEGIN
    FOR table_name IN
        SELECT tablename FROM pg_tables WHERE schemaname = 'shuangxi'
    LOOP
        EXECUTE format('
            DROP TRIGGER IF EXISTS update_updated_at_trigger ON shuangxi.%I;
            CREATE TRIGGER update_updated_at_trigger
                BEFORE UPDATE ON shuangxi.%I
                FOR EACH ROW
                EXECUTE FUNCTION shuangxi.update_updated_at_column();
        ', table_name, table_name);
    END LOOP;
END $$;

-- 输出复制完成信息
SELECT 
    'yiboshuo schema表结构复制到shuangxi schema完成!' as message,
    COUNT(*) as table_count
FROM pg_tables 
WHERE schemaname = 'shuangxi'; 