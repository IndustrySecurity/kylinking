#!/usr/bin/env python3
"""
修复外键约束差异，使yiboshuo与wanle的外键约束保持一致
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

class ForeignKeyFixer:
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
    
    def get_foreign_keys(self, schema_name, table_name):
        """获取外键约束"""
        sql = """
        SELECT 
            tc.constraint_name,
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name,
            rc.delete_rule,
            rc.update_rule
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage ccu
            ON ccu.constraint_name = tc.constraint_name
            AND ccu.table_schema = tc.table_schema
        LEFT JOIN information_schema.referential_constraints rc
            ON tc.constraint_name = rc.constraint_name
            AND tc.table_schema = rc.constraint_schema
        WHERE tc.table_schema = %s 
        AND tc.table_name = %s
        AND tc.constraint_type = 'FOREIGN KEY'
        ORDER BY tc.constraint_name
        """
        self.cursor.execute(sql, (schema_name, table_name))
        return self.cursor.fetchall()
    
    def fix_table_foreign_keys(self, table_name):
        """修复单个表的外键约束"""
        logger.info(f"修复表 {table_name} 的外键约束...")
        
        # 获取两个schema的外键约束
        wanle_fks = self.get_foreign_keys('wanle', table_name)
        yiboshuo_fks = self.get_foreign_keys('yiboshuo', table_name)
        
        # 创建外键映射
        wanle_fk_map = {}
        for fk in wanle_fks:
            key = (fk['column_name'], fk['foreign_table_name'], fk['foreign_column_name'])
            wanle_fk_map[key] = fk
        
        yiboshuo_fk_map = {}
        for fk in yiboshuo_fks:
            key = (fk['column_name'], fk['foreign_table_name'], fk['foreign_column_name'])
            yiboshuo_fk_map[key] = fk
        
        # 删除yiboshuo中多余的外键约束
        dropped_count = 0
        for key, yiboshuo_fk in yiboshuo_fk_map.items():
            if key not in wanle_fk_map:
                # 这个外键在wanle中不存在，需要删除
                constraint_name = yiboshuo_fk['constraint_name']
                sql = f"ALTER TABLE yiboshuo.{table_name} DROP CONSTRAINT {constraint_name}"
                
                if self.execute_sql(sql):
                    logger.info(f"  删除外键约束: {constraint_name} ({yiboshuo_fk['column_name']} -> {yiboshuo_fk['foreign_table_name']}.{yiboshuo_fk['foreign_column_name']})")
                    dropped_count += 1
        
        # 添加wanle中存在但yiboshuo中缺失的外键约束
        added_count = 0
        for key, wanle_fk in wanle_fk_map.items():
            if key not in yiboshuo_fk_map:
                # 这个外键在yiboshuo中不存在，需要添加
                col_name, ref_table, ref_column = key
                
                # 检查引用表是否存在
                check_sql = "SELECT 1 FROM information_schema.tables WHERE table_schema = 'yiboshuo' AND table_name = %s"
                self.cursor.execute(check_sql, (ref_table,))
                if not self.cursor.fetchone():
                    logger.warning(f"  引用表 {ref_table} 不存在，跳过外键 {col_name}")
                    continue
                
                # 生成外键约束名
                fk_name = f"fk_{table_name}_{col_name}_{ref_table}_{ref_column}"
                
                # 添加外键约束
                delete_rule = wanle_fk['delete_rule'] or 'NO ACTION'
                update_rule = wanle_fk['update_rule'] or 'NO ACTION'
                
                sql = f"""
                ALTER TABLE yiboshuo.{table_name} 
                ADD CONSTRAINT {fk_name} 
                FOREIGN KEY ({col_name}) 
                REFERENCES yiboshuo.{ref_table}({ref_column}) 
                ON DELETE {delete_rule} 
                ON UPDATE {update_rule}
                """
                
                if self.execute_sql(sql):
                    logger.info(f"  添加外键约束: {col_name} -> {ref_table}.{ref_column}")
                    added_count += 1
        
        total_changes = dropped_count + added_count
        if total_changes > 0:
            logger.info(f"表 {table_name} 外键约束修复完成: 删除 {dropped_count} 个，添加 {added_count} 个")
        
        return total_changes
    
    def fix_all_foreign_keys(self):
        """修复所有表的外键约束差异"""
        logger.info("开始修复所有表的外键约束差异...")
        
        # 获取需要修复的表列表（基于之前的检查报告）
        tables_to_fix = [
            'bag_type_structures',
            'bag_types',
            'customers',
            'delivery_notice_details',
            'delivery_notices',
            'material_suppliers',
            'materials',
            'process_machines',
            'product_materials',
            'product_transfer_orders',
            'products',
            'quote_accessories',
            'sales_order_details',
            'sales_order_materials',
            'sales_order_other_fees',
            'sales_orders'
        ]
        
        total_changes = 0
        for table_name in tables_to_fix:
            logger.info(f"\n处理表: {table_name}")
            changes = self.fix_table_foreign_keys(table_name)
            total_changes += changes
        
        logger.info(f"\n外键约束修复完成！总共修复了 {total_changes} 个差异")
        return total_changes

def main():
    # 数据库配置
    db_config = {
        'host': os.getenv('DATABASE_HOST', 'postgres'),
        'database': os.getenv('DATABASE_NAME', 'saas_platform'),
        'user': os.getenv('DATABASE_USER', 'postgres'),
        'password': os.getenv('DATABASE_PASSWORD', 'postgres'),
        'port': os.getenv('DATABASE_PORT', '5432')
    }
    
    fixer = ForeignKeyFixer(db_config)
    
    try:
        fixer.connect()
        total_changes = fixer.fix_all_foreign_keys()
        
        logger.info(f"\n✅ 外键约束修复完成！")
        logger.info(f"总共修复了 {total_changes} 个差异")
        
    except Exception as e:
        logger.error(f"修复过程中发生错误: {e}")
        return 1
    finally:
        fixer.disconnect()
    
    return 0

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='修复外键约束差异')
    parser.add_argument('--force', action='store_true', help='强制执行修复')
    args = parser.parse_args()
    
    if not args.force:
        print("⚠️  这个操作会修改yiboshuo schema的外键约束")
        print("⚠️  请确保已经备份了数据库")
        confirm = input("确定要继续吗？(y/N): ")
        if confirm.lower() != 'y':
            print("操作已取消")
            sys.exit(0)
    
    sys.exit(main()) 