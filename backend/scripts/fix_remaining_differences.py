#!/usr/bin/env python3
"""
修复yiboshuo schema与wanle schema的剩余差异
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

class RemainingDifferencesFixer:
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
            self.conn.autocommit = False
            logger.info(f"✓ 成功连接到数据库: {self.db_config['database']}")
        except Exception as e:
            logger.error(f"✗ 数据库连接失败: {e}")
            sys.exit(1)
    
    def disconnect(self):
        """断开数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    def execute_sql(self, sql, params=None, commit=True):
        """执行SQL语句"""
        try:
            logger.info(f"执行SQL: {sql}")
            self.cursor.execute(sql, params)
            if commit:
                self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"SQL执行失败: {e}")
            logger.error(f"SQL: {sql}")
            self.conn.rollback()
            return False
    
    def fix_timestamp_defaults(self):
        """修复时间戳默认值不一致（now() vs CURRENT_TIMESTAMP）"""
        logger.info("🔧 修复时间戳默认值...")
        
        # 需要统一为 now() 的表和字段
        timestamp_defaults = [
            # 基础档案相关
            ('material_inbound_order_details', ['created_at', 'updated_at']),
            ('material_inbound_orders', ['created_at', 'updated_at', 'order_date']),
            ('material_outbound_order_details', ['created_at', 'updated_at']),
            ('material_outbound_orders', ['created_at', 'updated_at', 'order_date']),
            ('outbound_order_details', ['created_at', 'updated_at']),
            ('outbound_orders', ['created_at', 'updated_at', 'order_date']),
            ('quote_materials', ['created_at', 'updated_at']),
            ('specifications', ['created_at', 'updated_at']),
            ('supplier_category_management', ['created_at', 'updated_at']),
            ('units', ['created_at', 'updated_at']),
            
            # 业务相关
            ('delivery_notice_details', ['created_at', 'updated_at']),
            ('delivery_notices', ['created_at', 'updated_at']),
            ('sales_order_details', ['created_at', 'updated_at']),
            ('sales_order_materials', ['created_at', 'updated_at']),
            ('sales_order_other_fees', ['created_at', 'updated_at']),
            ('sales_orders', ['created_at', 'updated_at', 'order_date']),
            
            # 材料相关（需要特殊处理时间戳类型）
            ('material_properties', ['created_at', 'updated_at']),
        ]
        
        for table_name, columns in timestamp_defaults:
            for column_name in columns:
                sql = f"""
                ALTER TABLE yiboshuo.{table_name} 
                ALTER COLUMN {column_name} SET DEFAULT now();
                """
                if self.execute_sql(sql, commit=False):
                    logger.info(f"  ✓ 修复 {table_name}.{column_name} 默认值")
        
        self.conn.commit()
    
    def fix_remaining_timestamp_types(self):
        """修复剩余的时间戳类型不一致"""
        logger.info("🔧 修复剩余时间戳类型...")
        
        # 需要修复为 timestamp with time zone 的表和字段
        timestamp_fixes = [
            # 库存相关表
            ('inbound_order_details', ['created_at', 'updated_at', 'expiry_date', 'production_date']),
            ('inbound_orders', ['created_at', 'updated_at', 'order_date', 'approved_at']),
            ('inventories', ['created_at', 'updated_at', 'expiry_date', 'last_count_date', 'production_date']),
            ('inventory_count_plans', ['created_at', 'updated_at', 'actual_end_date', 'actual_start_date', 'plan_end_date', 'plan_start_date']),
            ('inventory_count_records', ['created_at', 'updated_at', 'count_date', 'recount_date']),
            ('inventory_transactions', ['created_at', 'updated_at', 'approved_at', 'cancelled_at', 'transaction_date']),
            
            # 材料相关表
            ('material_count_plans', ['created_at', 'updated_at', 'count_date']),
            ('material_count_records', ['created_at', 'updated_at']),
            ('material_transfer_order_details', ['created_at', 'updated_at', 'expiry_date', 'production_date']),
            ('material_transfer_orders', ['created_at', 'updated_at', 'actual_arrival_date', 'approved_at', 'executed_at', 'expected_arrival_date', 'transfer_date']),
            ('material_suppliers', ['created_at', 'updated_at']),
            
            # 产品相关表
            ('product_count_plans', ['created_at', 'updated_at', 'count_date']),
            ('product_count_records', ['created_at', 'updated_at', 'expiry_date', 'production_date']),
            ('product_transfer_order_details', ['created_at', 'updated_at', 'expiry_date', 'production_date']),
            ('product_transfer_orders', ['created_at', 'updated_at', 'actual_arrival_date', 'approved_at', 'executed_at', 'expected_arrival_date', 'transfer_date']),
        ]
        
        for table_name, columns in timestamp_fixes:
            for column_name in columns:
                sql = f"""
                ALTER TABLE yiboshuo.{table_name} 
                ALTER COLUMN {column_name} TYPE TIMESTAMP WITH TIME ZONE 
                USING {column_name}::TIMESTAMP WITH TIME ZONE;
                """
                if self.execute_sql(sql, commit=False):
                    logger.info(f"  ✓ 修复 {table_name}.{column_name} 类型")
        
        self.conn.commit()
    
    def fix_nullable_constraints(self):
        """修复可空性约束"""
        logger.info("🔧 修复可空性约束...")
        
        # 需要设置为 NOT NULL 的字段
        nullable_fixes = [
            # 库存相关
            ('inbound_order_details', ['created_at', 'updated_at']),
            ('inbound_orders', ['created_at', 'updated_at']),
            ('inventories', ['created_at', 'updated_at']),
            ('inventory_count_plans', ['created_at', 'updated_at']),
            ('inventory_count_records', ['created_at', 'updated_at']),
            ('inventory_transactions', ['created_at', 'updated_at']),
            
            # 产品相关
            ('product_materials', ['material_id']),
            ('product_transfer_order_details', ['created_by', 'product_name', 'transfer_quantity', 'unit']),
            ('product_transfer_orders', ['created_by', 'from_warehouse_id', 'to_warehouse_id', 'transfer_date']),
        ]
        
        for table_name, columns in nullable_fixes:
            for column_name in columns:
                sql = f"""
                ALTER TABLE yiboshuo.{table_name} 
                ALTER COLUMN {column_name} SET NOT NULL;
                """
                if self.execute_sql(sql, commit=False):
                    logger.info(f"  ✓ 修复 {table_name}.{column_name} 可空性")
        
        self.conn.commit()
    
    def fix_default_values(self):
        """修复其他默认值"""
        logger.info("🔧 修复其他默认值...")
        
        # 特殊的默认值修复
        default_fixes = [
            # 材料供应商表
            ('material_suppliers', 'delivery_days', 'SET DEFAULT 0'),
            ('material_suppliers', 'supplier_price', 'SET DEFAULT 0'),
            ('material_suppliers', 'supplier_id', 'SET NOT NULL'),
            
            # 产品调拨表
            ('product_transfer_order_details', 'actual_transfer_quantity', 'SET DEFAULT 0'),
            ('product_transfer_order_details', 'received_quantity', 'SET DEFAULT 0'),
            
            # 报价油墨表
            ('quote_inks', 'created_at', 'SET DEFAULT CURRENT_TIMESTAMP'),
            ('quote_inks', 'updated_at', 'SET DEFAULT CURRENT_TIMESTAMP'),
            ('quote_inks', 'id', 'SET DEFAULT gen_random_uuid()'),
            ('quote_inks', 'is_enabled', 'SET DEFAULT true'),
            ('quote_inks', 'is_ink', 'SET DEFAULT false'),
            ('quote_inks', 'is_solvent', 'SET DEFAULT false'),
            ('quote_inks', 'sort_order', 'SET DEFAULT 0'),
            
            # 产品调拨订单
            ('product_transfer_orders', 'transfer_date', 'SET DEFAULT CURRENT_TIMESTAMP'),
        ]
        
        for table_name, column_name, default_clause in default_fixes:
            sql = f"""
            ALTER TABLE yiboshuo.{table_name} 
            ALTER COLUMN {column_name} {default_clause};
            """
            if self.execute_sql(sql, commit=False):
                logger.info(f"  ✓ 修复 {table_name}.{column_name} 默认值")
        
        self.conn.commit()
    
    def fix_column_lengths(self):
        """修复字段长度不一致"""
        logger.info("🔧 修复字段长度...")
        
        # 字段长度修复
        length_fixes = [
            ('product_transfer_orders', 'from_warehouse_name', 'VARCHAR(100)'),
            ('product_transfer_orders', 'to_warehouse_name', 'VARCHAR(100)'),
            ('product_transfer_orders', 'transfer_number', 'VARCHAR(50)'),
            ('product_transfer_orders', 'transport_method', 'VARCHAR(20)'),
            ('product_transfer_orders', 'transporter', 'VARCHAR(100)'),
            ('product_images', 'file_size', 'BIGINT'),
        ]
        
        for table_name, column_name, new_type in length_fixes:
            sql = f"""
            ALTER TABLE yiboshuo.{table_name} 
            ALTER COLUMN {column_name} TYPE {new_type} 
            USING {column_name}::{new_type};
            """
            if self.execute_sql(sql, commit=False):
                logger.info(f"  ✓ 修复 {table_name}.{column_name} 长度")
        
        self.conn.commit()
    
    def fix_missing_columns(self):
        """修复缺失的列"""
        logger.info("🔧 修复缺失的列...")
        
        # 需要添加的列
        missing_columns = [
            # 库存盘点计划表
            ('inventory_count_plans', 'custom_fields', 'JSONB'),
            ('inventory_count_plans', 'manager_id', 'UUID'),
            ('inventory_count_plans', 'manager_name', 'VARCHAR(100)'),
            
            # 产品调拨详情表
            ('product_transfer_order_details', 'transferred_quantity', 'DECIMAL(12,3) DEFAULT 0'),
            
            # 产品调拨订单表
            ('product_transfer_orders', 'business_type', 'VARCHAR(50)'),
            ('product_transfer_orders', 'department_name', 'VARCHAR(100)'),
            ('product_transfer_orders', 'execute_date', 'TIMESTAMP WITH TIME ZONE'),
            ('product_transfer_orders', 'executor_id', 'UUID'),
            ('product_transfer_orders', 'executor_name', 'VARCHAR(100)'),
            ('product_transfer_orders', 'priority', 'VARCHAR(20)'),
            ('product_transfer_orders', 'receive_date', 'TIMESTAMP WITH TIME ZONE'),
            ('product_transfer_orders', 'receiver_id', 'UUID'),
            ('product_transfer_orders', 'receiver_name', 'VARCHAR(100)'),
            ('product_transfer_orders', 'related_order_id', 'UUID'),
            ('product_transfer_orders', 'related_order_no', 'VARCHAR(50)'),
            ('product_transfer_orders', 'review_date', 'TIMESTAMP WITH TIME ZONE'),
            ('product_transfer_orders', 'review_notes', 'TEXT'),
            ('product_transfer_orders', 'reviewer_id', 'UUID'),
            ('product_transfer_orders', 'reviewer_name', 'VARCHAR(100)'),
            ('product_transfer_orders', 'total_cost', 'DECIMAL(12,2)'),
            ('product_transfer_orders', 'total_varieties', 'INTEGER'),
            ('product_transfer_orders', 'tracking_no', 'VARCHAR(50)'),
            ('product_transfer_orders', 'transfer_person_name', 'VARCHAR(100)'),
            ('product_transfer_orders', 'transport_cost', 'DECIMAL(12,2)'),
            ('product_transfer_orders', 'urgent_reason', 'TEXT'),
            
            # 工艺机台表
            ('process_machines', 'created_at', 'TIMESTAMP WITH TIME ZONE DEFAULT now()'),
            ('process_machines', 'created_by', 'UUID'),
            ('process_machines', 'updated_at', 'TIMESTAMP WITH TIME ZONE DEFAULT now()'),
            ('process_machines', 'updated_by', 'UUID'),
        ]
        
        for table_name, column_name, column_type in missing_columns:
            # 检查列是否已存在
            check_sql = """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'yiboshuo' AND table_name = %s AND column_name = %s
            )
            """
            self.cursor.execute(check_sql, (table_name, column_name))
            if not self.cursor.fetchone()['exists']:
                sql = f"""
                ALTER TABLE yiboshuo.{table_name} 
                ADD COLUMN {column_name} {column_type};
                """
                if self.execute_sql(sql, commit=False):
                    logger.info(f"  ✓ 添加列 {table_name}.{column_name}")
        
        self.conn.commit()
    
    def fix_extra_columns(self):
        """删除多余的列"""
        logger.info("🔧 删除多余的列...")
        
        # 需要删除的列
        extra_columns = [
            ('inventory_count_plans', 'count_team'),
            ('inventory_count_plans', 'material_categories'),
            ('inventory_count_plans', 'supervisor_id'),
        ]
        
        for table_name, column_name in extra_columns:
            # 检查列是否存在
            check_sql = """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'yiboshuo' AND table_name = %s AND column_name = %s
            )
            """
            self.cursor.execute(check_sql, (table_name, column_name))
            if self.cursor.fetchone()['exists']:
                sql = f"""
                ALTER TABLE yiboshuo.{table_name} 
                DROP COLUMN {column_name};
                """
                if self.execute_sql(sql, commit=False):
                    logger.info(f"  ✓ 删除列 {table_name}.{column_name}")
        
        self.conn.commit()
    
    def fix_remaining_foreign_keys(self):
        """修复剩余的外键约束"""
        logger.info("🔧 修复剩余外键约束...")
        
        # 需要添加的外键（这些在第一次修复时可能失败了）
        additional_foreign_keys = [
            # 员工相关外键
            ('inbound_orders', 'inbound_person_id', 'employees', 'id'),
            ('material_inbound_orders', 'inbound_person_id', 'employees', 'id'),
            ('material_outbound_orders', 'requisition_person_id', 'employees', 'id'),
            ('material_outbound_orders', 'outbound_person_id', 'employees', 'id'),
            ('outbound_orders', 'outbound_person_id', 'employees', 'id'),
            ('material_transfer_orders', 'transfer_person_id', 'employees', 'id'),
            ('material_count_plans', 'count_person_id', 'employees', 'id'),
            ('product_count_plans', 'count_person_id', 'employees', 'id'),
        ]
        
        for table_name, column_name, ref_table, ref_column in additional_foreign_keys:
            # 检查外键是否已存在
            check_sql = """
            SELECT COUNT(*) FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name
            WHERE tc.table_schema = 'yiboshuo' 
                AND tc.table_name = %s 
                AND kcu.column_name = %s
                AND tc.constraint_type = 'FOREIGN KEY'
            """
            self.cursor.execute(check_sql, (table_name, column_name))
            if self.cursor.fetchone()['count'] == 0:
                # 添加外键约束
                constraint_name = f"fk_{table_name}_{column_name}"
                sql = f"""
                ALTER TABLE yiboshuo.{table_name} 
                ADD CONSTRAINT {constraint_name} 
                FOREIGN KEY ({column_name}) 
                REFERENCES yiboshuo.{ref_table}({ref_column});
                """
                if self.execute_sql(sql, commit=False):
                    logger.info(f"  ✓ 添加外键 {table_name}.{column_name} -> {ref_table}.{ref_column}")
        
        self.conn.commit()
    
    def run_all_remaining_fixes(self):
        """运行所有剩余修复"""
        logger.info("🚀 开始修复剩余差异...")
        
        try:
            # 按顺序执行修复
            self.fix_timestamp_defaults()
            self.fix_remaining_timestamp_types()
            self.fix_nullable_constraints()
            self.fix_default_values()
            self.fix_column_lengths()
            self.fix_missing_columns()
            self.fix_extra_columns()
            self.fix_remaining_foreign_keys()
            
            logger.info("✅ 剩余差异修复完成！")
            
        except Exception as e:
            logger.error(f"❌ 修复过程中发生错误: {e}")
            self.conn.rollback()
            raise

def main():
    # 数据库配置
    db_config = {
        'host': os.getenv('DATABASE_HOST', 'postgres'),
        'database': os.getenv('DATABASE_NAME', 'saas_platform'),
        'user': os.getenv('DATABASE_USER', 'postgres'),
        'password': os.getenv('DATABASE_PASSWORD', 'postgres'),
        'port': os.getenv('DATABASE_PORT', '5432')
    }
    
    fixer = RemainingDifferencesFixer(db_config)
    
    try:
        fixer.connect()
        
        # 提示用户确认
        print("⚠️  警告：此操作将修复yiboshuo schema的剩余差异！")
        print("要继续吗？(y/N): ", end='')
        
        if len(sys.argv) > 1 and sys.argv[1] == '--force':
            confirm = 'y'
        else:
            confirm = input().lower()
        
        if confirm == 'y':
            fixer.run_all_remaining_fixes()
            print("\n🎉 剩余差异修复完成！")
        else:
            print("❌ 操作已取消")
            
    except Exception as e:
        logger.error(f"❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        fixer.disconnect()

if __name__ == "__main__":
    main() 