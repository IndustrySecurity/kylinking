#!/usr/bin/env python3
"""
全面修复yiboshuo schema与wanle schema的所有差异
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import logging
import json

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveSchemaFixer:
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
    
    def get_table_structure(self, schema_name, table_name):
        """获取表结构"""
        sql = """
        SELECT 
            c.column_name,
            c.data_type,
            c.is_nullable,
            c.column_default,
            c.character_maximum_length,
            c.numeric_precision,
            c.numeric_scale,
            c.udt_name
        FROM information_schema.columns c
        WHERE c.table_schema = %s AND c.table_name = %s
        ORDER BY c.ordinal_position
        """
        self.cursor.execute(sql, (schema_name, table_name))
        return self.cursor.fetchall()
    
    def get_table_constraints(self, schema_name, table_name):
        """获取表约束"""
        sql = """
        SELECT 
            tc.constraint_name,
            tc.constraint_type,
            kcu.column_name,
            ccu.table_schema AS foreign_table_schema,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name,
            rc.delete_rule,
            rc.update_rule
        FROM information_schema.table_constraints tc
        LEFT JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        LEFT JOIN information_schema.constraint_column_usage ccu
            ON ccu.constraint_name = tc.constraint_name
            AND ccu.table_schema = tc.table_schema
        LEFT JOIN information_schema.referential_constraints rc
            ON tc.constraint_name = rc.constraint_name
            AND tc.table_schema = rc.constraint_schema
        WHERE tc.table_schema = %s AND tc.table_name = %s
        ORDER BY tc.constraint_type, tc.constraint_name
        """
        self.cursor.execute(sql, (schema_name, table_name))
        return self.cursor.fetchall()
    
    def fix_timestamp_types(self, table_name):
        """修复时间戳类型差异"""
        logger.info(f"修复表 {table_name} 的时间戳类型...")
        
        # 获取wanle表结构
        wanle_columns = self.get_table_structure('wanle', table_name)
        yiboshuo_columns = self.get_table_structure('yiboshuo', table_name)
        
        # 创建字段映射
        wanle_col_map = {col['column_name']: col for col in wanle_columns}
        yiboshuo_col_map = {col['column_name']: col for col in yiboshuo_columns}
        
        fixed_count = 0
        for col_name, wanle_col in wanle_col_map.items():
            if col_name in yiboshuo_col_map:
                yiboshuo_col = yiboshuo_col_map[col_name]
                
                # 修复时间戳类型
                if wanle_col['data_type'] != yiboshuo_col['data_type']:
                    if 'timestamp' in wanle_col['data_type'].lower():
                        new_type = wanle_col['data_type']
                        if wanle_col['data_type'] == 'timestamp without time zone':
                            new_type = 'timestamp'
                        elif wanle_col['data_type'] == 'timestamp with time zone':
                            new_type = 'timestamptz'
                        
                        sql = f'ALTER TABLE yiboshuo.{table_name} ALTER COLUMN {col_name} TYPE {new_type}'
                        if self.execute_sql(sql):
                            logger.info(f"  修复字段 {col_name} 类型: {yiboshuo_col['data_type']} -> {wanle_col['data_type']}")
                            fixed_count += 1
                
                # 修复可空性
                if wanle_col['is_nullable'] != yiboshuo_col['is_nullable']:
                    if wanle_col['is_nullable'] == 'YES':
                        sql = f'ALTER TABLE yiboshuo.{table_name} ALTER COLUMN {col_name} DROP NOT NULL'
                    else:
                        sql = f'ALTER TABLE yiboshuo.{table_name} ALTER COLUMN {col_name} SET NOT NULL'
                    
                    if self.execute_sql(sql):
                        logger.info(f"  修复字段 {col_name} 可空性: {yiboshuo_col['is_nullable']} -> {wanle_col['is_nullable']}")
                        fixed_count += 1
                
                # 修复默认值
                if wanle_col['column_default'] != yiboshuo_col['column_default']:
                    wanle_default = wanle_col['column_default']
                    yiboshuo_default = yiboshuo_col['column_default']
                    
                    if wanle_default is None and yiboshuo_default is not None:
                        sql = f'ALTER TABLE yiboshuo.{table_name} ALTER COLUMN {col_name} DROP DEFAULT'
                        if self.execute_sql(sql):
                            logger.info(f"  删除字段 {col_name} 的默认值")
                            fixed_count += 1
                    elif wanle_default is not None:
                        # 处理常见的默认值格式
                        if wanle_default.startswith('nextval'):
                            # 序列默认值，跳过
                            continue
                        elif 'now()' in wanle_default.lower():
                            sql = f'ALTER TABLE yiboshuo.{table_name} ALTER COLUMN {col_name} SET DEFAULT now()'
                        elif 'current_timestamp' in wanle_default.lower():
                            sql = f'ALTER TABLE yiboshuo.{table_name} ALTER COLUMN {col_name} SET DEFAULT CURRENT_TIMESTAMP'
                        elif wanle_default.startswith("'") and wanle_default.endswith("'"):
                            sql = f'ALTER TABLE yiboshuo.{table_name} ALTER COLUMN {col_name} SET DEFAULT {wanle_default}'
                        else:
                            sql = f'ALTER TABLE yiboshuo.{table_name} ALTER COLUMN {col_name} SET DEFAULT {wanle_default}'
                        
                        if self.execute_sql(sql):
                            logger.info(f"  修复字段 {col_name} 默认值: {yiboshuo_default} -> {wanle_default}")
                            fixed_count += 1
                
                # 修复字段长度
                if (wanle_col['character_maximum_length'] != yiboshuo_col['character_maximum_length'] 
                    and wanle_col['character_maximum_length'] is not None):
                    new_length = wanle_col['character_maximum_length']
                    if wanle_col['data_type'] in ['character varying', 'varchar']:
                        sql = f'ALTER TABLE yiboshuo.{table_name} ALTER COLUMN {col_name} TYPE varchar({new_length})'
                        if self.execute_sql(sql):
                            logger.info(f"  修复字段 {col_name} 长度: {yiboshuo_col['character_maximum_length']} -> {new_length}")
                            fixed_count += 1
        
        if fixed_count > 0:
            logger.info(f"表 {table_name} 修复了 {fixed_count} 个字段差异")
        return fixed_count
    
    def fix_foreign_keys(self, table_name):
        """修复外键约束"""
        logger.info(f"修复表 {table_name} 的外键约束...")
        
        # 获取wanle的外键约束
        wanle_constraints = self.get_table_constraints('wanle', table_name)
        yiboshuo_constraints = self.get_table_constraints('yiboshuo', table_name)
        
        # 创建约束映射
        wanle_fk_map = {}
        yiboshuo_fk_map = {}
        
        for constraint in wanle_constraints:
            if constraint['constraint_type'] == 'FOREIGN KEY':
                key = (constraint['column_name'], constraint['foreign_table_name'], constraint['foreign_column_name'])
                wanle_fk_map[key] = constraint
        
        for constraint in yiboshuo_constraints:
            if constraint['constraint_type'] == 'FOREIGN KEY':
                key = (constraint['column_name'], constraint['foreign_table_name'], constraint['foreign_column_name'])
                yiboshuo_fk_map[key] = constraint
        
        # 添加缺失的外键
        fixed_count = 0
        for key, wanle_fk in wanle_fk_map.items():
            if key not in yiboshuo_fk_map:
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
                    logger.info(f"  添加外键: {col_name} -> {ref_table}.{ref_column}")
                    fixed_count += 1
        
        if fixed_count > 0:
            logger.info(f"表 {table_name} 添加了 {fixed_count} 个外键约束")
        return fixed_count
    
    def get_different_tables(self):
        """获取有差异的表列表"""
        # 重新运行一致性检查，获取差异表
        sql = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'wanle' 
        AND table_name IN (
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'yiboshuo'
        )
        ORDER BY table_name
        """
        self.cursor.execute(sql)
        common_tables = [row['table_name'] for row in self.cursor.fetchall()]
        
        # 检查每个表是否有差异
        different_tables = []
        for table_name in common_tables:
            wanle_structure = self.get_table_structure('wanle', table_name)
            yiboshuo_structure = self.get_table_structure('yiboshuo', table_name)
            
            if len(wanle_structure) != len(yiboshuo_structure):
                different_tables.append(table_name)
                continue
            
            # 检查字段差异
            wanle_map = {col['column_name']: col for col in wanle_structure}
            yiboshuo_map = {col['column_name']: col for col in yiboshuo_structure}
            
            has_difference = False
            for col_name, wanle_col in wanle_map.items():
                if col_name not in yiboshuo_map:
                    has_difference = True
                    break
                
                yiboshuo_col = yiboshuo_map[col_name]
                if (wanle_col['data_type'] != yiboshuo_col['data_type'] or
                    wanle_col['is_nullable'] != yiboshuo_col['is_nullable'] or
                    wanle_col['column_default'] != yiboshuo_col['column_default'] or
                    wanle_col['character_maximum_length'] != yiboshuo_col['character_maximum_length']):
                    has_difference = True
                    break
            
            if has_difference:
                different_tables.append(table_name)
        
        return different_tables
    
    def fix_all_differences(self):
        """修复所有表结构差异"""
        logger.info("开始全面修复schema差异...")
        
        different_tables = self.get_different_tables()
        logger.info(f"发现 {len(different_tables)} 个表存在差异")
        
        total_fixed = 0
        for table_name in different_tables:
            logger.info(f"\n处理表: {table_name}")
            
            # 修复字段差异
            field_fixes = self.fix_timestamp_types(table_name)
            total_fixed += field_fixes
            
            # 修复外键约束
            fk_fixes = self.fix_foreign_keys(table_name)
            total_fixed += fk_fixes
        
        logger.info(f"\n修复完成！总共修复了 {total_fixed} 个差异")
        return total_fixed

def main():
    # 数据库配置
    db_config = {
        'host': os.getenv('DATABASE_HOST', 'postgres'),
        'database': os.getenv('DATABASE_NAME', 'saas_platform'),
        'user': os.getenv('DATABASE_USER', 'postgres'),
        'password': os.getenv('DATABASE_PASSWORD', 'postgres'),
        'port': os.getenv('DATABASE_PORT', '5432')
    }
    
    fixer = ComprehensiveSchemaFixer(db_config)
    
    try:
        fixer.connect()
        total_fixes = fixer.fix_all_differences()
        
        logger.info(f"\n✅ 全面修复完成！")
        logger.info(f"总共修复了 {total_fixes} 个差异")
        
    except Exception as e:
        logger.error(f"修复过程中发生错误: {e}")
        return 1
    finally:
        fixer.disconnect()
    
    return 0

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='全面修复schema差异')
    parser.add_argument('--force', action='store_true', help='强制执行修复')
    args = parser.parse_args()
    
    if not args.force:
        print("⚠️  这个操作会修改yiboshuo schema的结构")
        print("⚠️  请确保已经备份了数据库")
        confirm = input("确定要继续吗？(y/N): ")
        if confirm.lower() != 'y':
            print("操作已取消")
            sys.exit(0)
    
    sys.exit(main()) 