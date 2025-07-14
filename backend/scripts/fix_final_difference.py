#!/usr/bin/env python3
"""
修复最后一个schema差异：在yiboshuo的customers表中添加缺失的外键约束
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import logging

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinalDifferenceFixer:
    def __init__(self, db_config):
        self.db_config = db_config
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """连接数据库"""
        try:
            self.conn = psycopg2.connect(
                host=self.db_config['host'],
                database=self.db_config['database'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                port=self.db_config['port']
            )
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            logger.info("数据库连接成功")
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            raise
    
    def disconnect(self):
        """断开数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            
    def execute_sql(self, sql, params=None):
        """执行SQL语句"""
        try:
            self.cursor.execute(sql, params)
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"SQL执行失败: {sql}")
            logger.error(f"错误: {e}")
            self.conn.rollback()
            return False
    
    def check_table_exists(self, schema_name, table_name):
        """检查表是否存在"""
        sql = "SELECT 1 FROM information_schema.tables WHERE table_schema = %s AND table_name = %s"
        self.cursor.execute(sql, (schema_name, table_name))
        return self.cursor.fetchone() is not None
    
    def check_column_exists(self, schema_name, table_name, column_name):
        """检查列是否存在"""
        sql = "SELECT 1 FROM information_schema.columns WHERE table_schema = %s AND table_name = %s AND column_name = %s"
        self.cursor.execute(sql, (schema_name, table_name, column_name))
        return self.cursor.fetchone() is not None
    
    def check_foreign_key_exists(self, schema_name, table_name, column_name, ref_table, ref_column):
        """检查外键是否存在"""
        sql = """
        SELECT 1 FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage ccu
            ON ccu.constraint_name = tc.constraint_name
            AND ccu.table_schema = tc.table_schema
        WHERE tc.table_schema = %s 
        AND tc.table_name = %s
        AND tc.constraint_type = 'FOREIGN KEY'
        AND kcu.column_name = %s
        AND ccu.table_name = %s
        AND ccu.column_name = %s
        """
        self.cursor.execute(sql, (schema_name, table_name, column_name, ref_table, ref_column))
        return self.cursor.fetchone() is not None
    
    def fix_customers_foreign_key(self):
        """修复customers表的外键约束"""
        logger.info("修复customers表的外键约束...")
        
        # 检查yiboshuo.customers表是否存在
        if not self.check_table_exists('yiboshuo', 'customers'):
            logger.error("yiboshuo.customers表不存在")
            return False
        
        # 检查category_id列是否存在
        if not self.check_column_exists('yiboshuo', 'customers', 'category_id'):
            logger.error("yiboshuo.customers表中不存在category_id列")
            return False
        
        # 检查引用表是否存在
        if not self.check_table_exists('yiboshuo', 'customer_category_management'):
            logger.error("yiboshuo.customer_category_management表不存在")
            return False
        
        # 检查引用列是否存在
        if not self.check_column_exists('yiboshuo', 'customer_category_management', 'id'):
            logger.error("yiboshuo.customer_category_management表中不存在id列")
            return False
        
        # 检查外键是否已存在
        if self.check_foreign_key_exists('yiboshuo', 'customers', 'category_id', 'customer_category_management', 'id'):
            logger.info("外键约束已存在，无需添加")
            return True
        
        # 添加外键约束
        constraint_name = "fk_customers_category_id_customer_category_management_id"
        sql = f"""
        ALTER TABLE yiboshuo.customers 
        ADD CONSTRAINT {constraint_name} 
        FOREIGN KEY (category_id) 
        REFERENCES yiboshuo.customer_category_management(id) 
        ON DELETE NO ACTION 
        ON UPDATE NO ACTION
        """
        
        if self.execute_sql(sql):
            logger.info("✅ 成功添加外键约束: customers.category_id -> customer_category_management.id")
            return True
        else:
            logger.error("❌ 添加外键约束失败")
            return False
    
    def fix_final_difference(self):
        """修复最后一个差异"""
        logger.info("开始修复最后一个schema差异...")
        
        success = self.fix_customers_foreign_key()
        
        if success:
            logger.info("✅ 最后一个差异修复完成！")
            logger.info("🎉 yiboshuo schema现在与wanle schema完全一致！")
        else:
            logger.error("❌ 修复失败")
        
        return success

def main():
    # 数据库配置
    db_config = {
        'host': os.getenv('DATABASE_HOST', 'postgres'),
        'database': os.getenv('DATABASE_NAME', 'saas_platform'),
        'user': os.getenv('DATABASE_USER', 'postgres'),
        'password': os.getenv('DATABASE_PASSWORD', 'postgres'),
        'port': os.getenv('DATABASE_PORT', '5432')
    }
    
    fixer = FinalDifferenceFixer(db_config)
    
    try:
        fixer.connect()
        success = fixer.fix_final_difference()
        
        if success:
            logger.info("\n🎉 恭喜！所有schema差异都已修复完成！")
            logger.info("现在可以正常使用API功能了")
        else:
            logger.error("\n❌ 修复失败，请检查错误信息")
            return 1
        
    except Exception as e:
        logger.error(f"修复过程中发生错误: {e}")
        return 1
    finally:
        fixer.disconnect()
    
    return 0

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='修复最后一个schema差异')
    parser.add_argument('--force', action='store_true', help='强制执行修复')
    args = parser.parse_args()
    
    if not args.force:
        print("⚠️  这个操作会在yiboshuo.customers表中添加外键约束")
        print("⚠️  请确保已经备份了数据库")
        confirm = input("确定要继续吗？(y/N): ")
        if confirm.lower() != 'y':
            print("操作已取消")
            sys.exit(0)
    
    sys.exit(main()) 