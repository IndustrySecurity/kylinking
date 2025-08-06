#!/usr/bin/env python3
"""
批量schema更新脚本
用于对所有租户schema执行相同的数据库结构更新
"""

import os
import sys
import argparse
import logging
from sqlalchemy import create_engine, text

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BatchSchemaUpdater:
    """批量schema更新器"""
    
    def __init__(self, db_url=None):
        if db_url:
            self.db_url = db_url
        else:
            # 使用Flask配置获取数据库URL
            app = create_app()
            with app.app_context():
                self.db_url = app.config.get('SQLALCHEMY_DATABASE_URI')
        
        self.engine = create_engine(self.db_url)
    
    def get_all_tenant_schemas(self, exclude_schemas=None):
        """获取所有租户schema"""
        exclude_schemas = exclude_schemas or ['information_schema', 'pg_catalog', 'pg_toast', 'public']
        
        query = text("""
            SELECT DISTINCT schemaname
            FROM pg_tables 
            WHERE schemaname NOT IN :exclude_schemas
            ORDER BY schemaname
        """)
        
        with self.engine.connect() as conn:
            result = conn.execute(query, {"exclude_schemas": tuple(exclude_schemas)}).fetchall()
            return [row[0] for row in result]
    
    def execute_sql_on_schema(self, schema_name, sql_content, dry_run=False):
        """在指定schema上执行SQL"""
        try:
            if dry_run:
                logger.info(f"[DRY RUN] 将在schema {schema_name} 上执行SQL")
                return True
            
            with self.engine.connect() as conn:
                # 设置搜索路径
                conn.execute(text(f"SET search_path TO {schema_name}, public"))
                
                # 执行SQL
                conn.execute(text(sql_content))
                conn.commit()
                
                logger.info(f"Schema {schema_name} 更新成功")
                return True
                
        except Exception as e:
            logger.error(f"更新schema {schema_name} 失败: {e}")
            return False
    
    def batch_update(self, sql_file_path, exclude_schemas=None, dry_run=False):
        """批量更新所有租户schema"""
        if not os.path.exists(sql_file_path):
            logger.error(f"SQL文件不存在: {sql_file_path}")
            return False
        
        # 读取SQL文件
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 获取所有租户schema
        schemas = self.get_all_tenant_schemas(exclude_schemas)
        
        if not schemas:
            logger.warning("没有找到租户schema")
            return False
        
        logger.info(f"找到 {len(schemas)} 个租户schema: {', '.join(schemas)}")
        
        if dry_run:
            logger.info("DRY RUN模式 - 不会实际执行更新")
        
        # 批量执行
        success_count = 0
        failed_schemas = []
        
        for schema in schemas:
            success = self.execute_sql_on_schema(schema, sql_content, dry_run)
            if success:
                success_count += 1
            else:
                failed_schemas.append(schema)
        
        # 输出结果
        logger.info(f"批量更新完成:")
        logger.info(f"  成功: {success_count}/{len(schemas)}")
        if failed_schemas:
            logger.error(f"  失败: {', '.join(failed_schemas)}")
        
        return len(failed_schemas) == 0
    
    def preview_sql(self, sql_file_path):
        """预览SQL内容"""
        if not os.path.exists(sql_file_path):
            logger.error(f"SQL文件不存在: {sql_file_path}")
            return
        
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        print("\n" + "="*50)
        print("SQL文件内容预览:")
        print("="*50)
        print(sql_content)
        print("="*50)

def main():
    parser = argparse.ArgumentParser(description='批量schema更新工具')
    parser.add_argument('action', choices=['update', 'preview', 'list'], 
                       help='操作类型')
    parser.add_argument('--sql-file', help='SQL文件路径')
    parser.add_argument('--exclude', nargs='+', default=['public'], 
                       help='要排除的schema列表')
    parser.add_argument('--dry-run', action='store_true', 
                       help='试运行模式，不实际执行更新')
    
    args = parser.parse_args()
    
    app = create_app()
    
    with app.app_context():
        updater = BatchSchemaUpdater()
        
        if args.action == 'list':
            schemas = updater.get_all_tenant_schemas(args.exclude)
            print(f"\n当前租户schema列表 (排除: {', '.join(args.exclude)}):")
            print("-" * 50)
            for i, schema in enumerate(schemas, 1):
                print(f"{i:2d}. {schema}")
            print(f"\n总计: {len(schemas)} 个schema")
        
        elif args.action == 'preview':
            if not args.sql_file:
                logger.error("预览需要指定 --sql-file 参数")
                return
            updater.preview_sql(args.sql_file)
        
        elif args.action == 'update':
            if not args.sql_file:
                logger.error("更新需要指定 --sql-file 参数")
                return
            
            if args.dry_run:
                logger.info("DRY RUN模式 - 将显示将要执行的操作")
            
            success = updater.batch_update(args.sql_file, args.exclude, args.dry_run)
            if success:
                logger.info("批量更新操作完成")
            else:
                logger.error("批量更新操作失败")

if __name__ == '__main__':
    main() 