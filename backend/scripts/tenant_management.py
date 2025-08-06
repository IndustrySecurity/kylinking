#!/usr/bin/env python3
"""
租户数据库管理脚本
支持自动创建新租户、复制schema结构、批量更新等操作
"""

import os
import sys
import argparse
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TenantDatabaseManager:
    """租户数据库管理器"""
    
    def __init__(self, db_url=None):
        if db_url:
            self.db_url = db_url
        else:
            # 使用Flask配置获取数据库URL
            app = create_app()
            with app.app_context():
                self.db_url = app.config.get('SQLALCHEMY_DATABASE_URI')
        
        self.engine = create_engine(self.db_url)
        self.Session = sessionmaker(bind=self.engine)
        
    def create_new_tenant_schema(self, tenant_name, template_schema='yiboshuo'):
        """创建新租户的数据库schema"""
        try:
            with self.engine.connect() as conn:
                # 1. 创建新schema
                logger.info(f"正在创建schema: {tenant_name}")
                conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {tenant_name}"))
                
                # 2. 复制表结构（不复制数据）
                logger.info(f"正在从 {template_schema} 复制表结构到 {tenant_name}")
                self._copy_schema_structure(conn, template_schema, tenant_name)
                
                # 3. 创建更新时间触发器
                self._create_update_triggers(conn, tenant_name)
                
                logger.info(f"租户 {tenant_name} 的数据库结构创建完成")
                return True
                
        except Exception as e:
            logger.error(f"创建租户schema失败: {e}")
            return False
    
    def _copy_schema_structure(self, conn, source_schema, target_schema):
        """复制schema结构"""
        # 获取源schema中的所有表
        tables_query = text("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = :source_schema
            ORDER BY tablename
        """)
        
        tables = conn.execute(tables_query, {"source_schema": source_schema}).fetchall()
        
        for table in tables:
            table_name = table[0]
            logger.info(f"正在复制表: {table_name}")
            
            # 创建表结构（包含所有约束和索引）
            create_table_sql = text(f"""
                CREATE TABLE {target_schema}.{table_name} 
                (LIKE {source_schema}.{table_name} INCLUDING ALL)
            """)
            conn.execute(create_table_sql)
    
    def _create_update_triggers(self, conn, schema_name):
        """为schema中的所有表创建更新时间触发器"""
        # 创建触发器函数
        trigger_function = text(f"""
            CREATE OR REPLACE FUNCTION {schema_name}.update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ language 'plpgsql';
        """)
        conn.execute(trigger_function)
        
        # 为所有表添加触发器
        tables_query = text("""
            SELECT tablename FROM pg_tables WHERE schemaname = :schema_name
        """)
        
        tables = conn.execute(tables_query, {"schema_name": schema_name}).fetchall()
        
        for table in tables:
            self._create_update_trigger(conn, schema_name, table[0])
    
    def _create_update_trigger(self, conn, schema_name, table_name):
        """为单个表创建更新时间触发器"""
        trigger_sql = text(f"""
            DROP TRIGGER IF EXISTS update_updated_at_trigger ON {schema_name}.{table_name};
            CREATE TRIGGER update_updated_at_trigger
                BEFORE UPDATE ON {schema_name}.{table_name}
                FOR EACH ROW
                EXECUTE FUNCTION {schema_name}.update_updated_at_column();
        """)
        conn.execute(trigger_sql)
    
    def batch_update_schemas(self, schema_names, update_sql_file):
        """批量更新多个schema"""
        if not os.path.exists(update_sql_file):
            logger.error(f"SQL文件不存在: {update_sql_file}")
            return False
        
        with open(update_sql_file, 'r', encoding='utf-8') as f:
            update_sql = f.read()
        
        success_count = 0
        for schema_name in schema_names:
            try:
                logger.info(f"正在更新schema: {schema_name}")
                with self.engine.connect() as conn:
                    conn.execute(text(f"SET search_path TO {schema_name}, public"))
                    conn.execute(text(update_sql))
                    conn.commit()
                    success_count += 1
                    logger.info(f"Schema {schema_name} 更新成功")
            except Exception as e:
                logger.error(f"更新schema {schema_name} 失败: {e}")
        
        logger.info(f"批量更新完成，成功更新 {success_count}/{len(schema_names)} 个schema")
        return success_count == len(schema_names)
    
    def list_all_tenant_schemas(self):
        """列出所有租户schema"""
        query = text("""
            SELECT schemaname, COUNT(*) as table_count
            FROM pg_tables 
            WHERE schemaname NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
            GROUP BY schemaname
            ORDER BY schemaname
        """)
        
        with self.engine.connect() as conn:
            result = conn.execute(query).fetchall()
            return result

def main():
    parser = argparse.ArgumentParser(description='租户数据库管理工具')
    parser.add_argument('action', choices=['create', 'update', 'list'], 
                       help='操作类型')
    parser.add_argument('--tenant', help='租户名称')
    parser.add_argument('--template', default='yiboshuo', help='模板schema名称')
    parser.add_argument('--schemas', nargs='+', help='要操作的schema列表')
    parser.add_argument('--sql-file', help='SQL文件路径（用于批量更新）')
    
    args = parser.parse_args()
    
    app = create_app()
    
    with app.app_context():
        manager = TenantDatabaseManager()
        
        if args.action == 'create':
            if not args.tenant:
                logger.error("创建租户需要指定 --tenant 参数")
                return
            success = manager.create_new_tenant_schema(args.tenant, args.template)
            if success:
                logger.info(f"租户 {args.tenant} 创建成功")
            else:
                logger.error(f"租户 {args.tenant} 创建失败")
        
        elif args.action == 'update':
            if not args.sql_file or not args.schemas:
                logger.error("批量更新需要指定 --sql-file 和 --schemas 参数")
                return
            success = manager.batch_update_schemas(args.schemas, args.sql_file)
            if success:
                logger.info("批量更新成功")
            else:
                logger.error("批量更新失败")
        
        elif args.action == 'list':
            schemas = manager.list_all_tenant_schemas()
            print("\n当前所有租户schema:")
            print("Schema名称\t\t表数量")
            print("-" * 40)
            for schema in schemas:
                print(f"{schema[0]:<20}\t{schema[1]}")

if __name__ == '__main__':
    main() 
 