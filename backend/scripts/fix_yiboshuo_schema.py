#!/usr/bin/env python3
"""
修复yiboshuo schema结构，使其与wanle schema保持一致
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

class SchemaFixer:
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
            # 设置自动提交为False，手动控制事务
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
    
    def check_table_exists(self, schema_name, table_name):
        """检查表是否存在"""
        sql = """
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = %s AND table_name = %s
        )
        """
        self.cursor.execute(sql, (schema_name, table_name))
        return self.cursor.fetchone()['exists']
    
    def check_column_exists(self, schema_name, table_name, column_name):
        """检查列是否存在"""
        sql = """
        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_schema = %s AND table_name = %s AND column_name = %s
        )
        """
        self.cursor.execute(sql, (schema_name, table_name, column_name))
        return self.cursor.fetchone()['exists']
    
    def get_column_info(self, schema_name, table_name, column_name):
        """获取列信息"""
        sql = """
        SELECT data_type, character_maximum_length, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_schema = %s AND table_name = %s AND column_name = %s
        """
        self.cursor.execute(sql, (schema_name, table_name, column_name))
        return self.cursor.fetchone()
    
    def fix_missing_tables(self):
        """修复缺失的表"""
        logger.info("🔧 开始修复缺失的表...")
        
        # 从wanle复制缺失的表到yiboshuo
        missing_tables = [
            'customer_material_prices',
            'customers', 
            'quote_auxiliary_materials',
            'suppliers'
        ]
        
        for table_name in missing_tables:
            if not self.check_table_exists('yiboshuo', table_name):
                logger.info(f"  📋 复制表: {table_name}")
                
                # 获取表结构
                sql = f"""
                CREATE TABLE yiboshuo.{table_name} (LIKE wanle.{table_name} INCLUDING ALL);
                """
                if self.execute_sql(sql):
                    logger.info(f"  ✓ 表 {table_name} 创建成功")
                    
                    # 复制数据
                    copy_sql = f"""
                    INSERT INTO yiboshuo.{table_name} 
                    SELECT * FROM wanle.{table_name};
                    """
                    if self.execute_sql(copy_sql):
                        logger.info(f"  ✓ 表 {table_name} 数据复制成功")
    
    def fix_extra_tables(self):
        """处理多余的表"""
        logger.info("🔧 开始处理多余的表...")
        
        # yiboshuo中多余的表
        extra_tables = [
            'bag_related_formulas',
            'loss_types',
            'team_group_machines',
            'team_group_members', 
            'team_group_processes',
            'team_groups'
        ]
        
        for table_name in extra_tables:
            if self.check_table_exists('yiboshuo', table_name):
                logger.info(f"  ⚠️  发现多余的表: {table_name}")
                # 这里不删除，只是记录。如果需要删除，可以取消注释下面的代码
                # sql = f"DROP TABLE IF EXISTS yiboshuo.{table_name} CASCADE;"
                # self.execute_sql(sql)
    
    def fix_product_categories_table(self):
        """修复product_categories表结构"""
        logger.info("🔧 修复product_categories表...")
        
        # 检查并添加缺失的列
        missing_columns = {
            'category_name': 'VARCHAR(100)',
            'created_by': 'UUID',
            'delivery_days': 'INTEGER',
            'description': 'TEXT',
            'is_blown_film': 'BOOLEAN DEFAULT FALSE',
            'is_enabled': 'BOOLEAN DEFAULT TRUE',
            'sort_order': 'INTEGER DEFAULT 0',
            'subject_name': 'VARCHAR(100)',
            'updated_by': 'UUID'
        }
        
        for column_name, column_type in missing_columns.items():
            if not self.check_column_exists('yiboshuo', 'product_categories', column_name):
                sql = f"""
                ALTER TABLE yiboshuo.product_categories 
                ADD COLUMN {column_name} {column_type};
                """
                if self.execute_sql(sql):
                    logger.info(f"  ✓ 添加列 {column_name}")
        
        # 删除多余的列
        extra_columns = ['name', 'creator', 'is_blow', 'subject', 'updater']
        for column_name in extra_columns:
            if self.check_column_exists('yiboshuo', 'product_categories', column_name):
                sql = f"""
                ALTER TABLE yiboshuo.product_categories 
                DROP COLUMN IF EXISTS {column_name};
                """
                if self.execute_sql(sql):
                    logger.info(f"  ✓ 删除列 {column_name}")
        
        # 修复时间戳类型
        timestamp_fixes = [
            ("created_at", "TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP"),
            ("updated_at", "TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP")
        ]
        
        for column_name, new_type in timestamp_fixes:
            sql = f"""
            ALTER TABLE yiboshuo.product_categories 
            ALTER COLUMN {column_name} TYPE {new_type.split(' ')[0]} USING {column_name}::{new_type.split(' ')[0]};
            """
            if self.execute_sql(sql):
                logger.info(f"  ✓ 修复列类型 {column_name}")
        
        # 修复ID默认值
        sql = """
        ALTER TABLE yiboshuo.product_categories 
        ALTER COLUMN id SET DEFAULT gen_random_uuid();
        """
        self.execute_sql(sql)
    
    def fix_material_categories_table(self):
        """修复material_categories表结构"""
        logger.info("🔧 修复material_categories表...")
        
        # 修复字段默认值和约束
        fixes = [
            ("code_prefix", "ALTER COLUMN code_prefix DROP DEFAULT"),
            ("created_at", "ALTER COLUMN created_at SET NOT NULL"),
            ("created_by", "ALTER COLUMN created_by SET NOT NULL"),
            ("display_order", "ALTER COLUMN display_order SET NOT NULL"),
            ("enable_barcode", "ALTER COLUMN enable_barcode SET NOT NULL"),
            ("enable_batch", "ALTER COLUMN enable_batch SET NOT NULL"),
            ("is_accessory", "ALTER COLUMN is_accessory SET NOT NULL"),
            ("is_active", "ALTER COLUMN is_active SET NOT NULL"),
            ("is_consumable", "ALTER COLUMN is_consumable SET NOT NULL"),
            ("is_customized", "ALTER COLUMN is_customized SET NOT NULL"),
            ("is_fragile", "ALTER COLUMN is_fragile SET NOT NULL"),
            ("is_hazardous", "ALTER COLUMN is_hazardous SET NOT NULL"),
            ("is_imported", "ALTER COLUMN is_imported SET NOT NULL"),
            ("is_ink", "ALTER COLUMN is_ink SET NOT NULL"),
            ("is_light_sensitive", "ALTER COLUMN is_light_sensitive SET NOT NULL"),
            ("is_moisture_sensitive", "ALTER COLUMN is_moisture_sensitive SET NOT NULL"),
            ("is_perishable", "ALTER COLUMN is_perishable SET NOT NULL"),
            ("is_recyclable", "ALTER COLUMN is_recyclable SET NOT NULL"),
            ("is_seasonal", "ALTER COLUMN is_seasonal SET NOT NULL"),
            ("is_temperature_sensitive", "ALTER COLUMN is_temperature_sensitive SET NOT NULL"),
            ("requires_certification", "ALTER COLUMN requires_certification SET NOT NULL"),
            ("requires_special_storage", "ALTER COLUMN requires_special_storage SET NOT NULL"),
            ("show_on_kanban", "ALTER COLUMN show_on_kanban SET NOT NULL"),
            ("updated_at", "ALTER COLUMN updated_at SET NOT NULL")
        ]
        
        for column_name, alter_statement in fixes:
            sql = f"ALTER TABLE yiboshuo.material_categories {alter_statement};"
            self.execute_sql(sql, commit=False)
        
        # 修复字符长度
        length_fixes = [
            ("material_name", "ALTER COLUMN material_name TYPE VARCHAR(200)"),
            ("quality_grade", "ALTER COLUMN quality_grade TYPE VARCHAR(50)")
        ]
        
        for column_name, alter_statement in length_fixes:
            sql = f"ALTER TABLE yiboshuo.material_categories {alter_statement};"
            self.execute_sql(sql, commit=False)
        
        # 修复默认值
        default_fixes = [
            ("id", "ALTER COLUMN id SET DEFAULT uuid_generate_v4()"),
            ("material_type", "ALTER COLUMN material_type SET DEFAULT 'main'::character varying")
        ]
        
        for column_name, alter_statement in default_fixes:
            sql = f"ALTER TABLE yiboshuo.material_categories {alter_statement};"
            self.execute_sql(sql, commit=False)
        
        # 修复时间戳类型
        timestamp_fixes = [
            ("created_at", "TIMESTAMP WITH TIME ZONE"),
            ("updated_at", "TIMESTAMP WITH TIME ZONE")
        ]
        
        for column_name, new_type in timestamp_fixes:
            sql = f"""
            ALTER TABLE yiboshuo.material_categories 
            ALTER COLUMN {column_name} TYPE {new_type} USING {column_name}::{new_type};
            """
            self.execute_sql(sql, commit=False)
        
        self.conn.commit()
    
    def fix_timestamp_columns(self):
        """修复时间戳列的类型不一致"""
        logger.info("🔧 修复时间戳列类型...")
        
        # 需要修复的表和列
        timestamp_fixes = [
            ('departments', ['created_at', 'updated_at'], 'TIMESTAMP WITH TIME ZONE'),
            ('employees', ['created_at', 'updated_at'], 'TIMESTAMP WITH TIME ZONE'),
            ('positions', ['created_at', 'updated_at'], 'TIMESTAMP WITH TIME ZONE'),
            ('warehouses', ['created_at', 'updated_at'], 'TIMESTAMP WITH TIME ZONE'),
            ('ink_options', ['created_at', 'updated_at'], 'TIMESTAMP WITH TIME ZONE'),
            ('quote_freights', ['created_at', 'updated_at'], 'TIMESTAMP WITH TIME ZONE'),
            ('quote_losses', ['created_at', 'updated_at'], 'TIMESTAMP WITH TIME ZONE'),
        ]
        
        for table_name, columns, target_type in timestamp_fixes:
            for column_name in columns:
                sql = f"""
                ALTER TABLE yiboshuo.{table_name} 
                ALTER COLUMN {column_name} TYPE {target_type} 
                USING {column_name}::{target_type};
                """
                if self.execute_sql(sql, commit=False):
                    logger.info(f"  ✓ 修复 {table_name}.{column_name} 类型")
        
        self.conn.commit()
    
    def fix_nullable_columns(self):
        """修复列的可空性"""
        logger.info("🔧 修复列的可空性...")
        
        # 需要修复的列
        nullable_fixes = [
            ('account_management', 'created_at', 'SET NOT NULL'),
            ('account_management', 'updated_at', 'SET NOT NULL'),
            ('currencies', 'created_at', 'SET NOT NULL'),
            ('currencies', 'updated_at', 'SET NOT NULL'),
            ('payment_methods', 'created_at', 'SET NOT NULL'),
            ('payment_methods', 'updated_at', 'SET NOT NULL'),
            ('settlement_methods', 'created_at', 'SET NOT NULL'),
            ('settlement_methods', 'updated_at', 'SET NOT NULL'),
            ('tax_rates', 'created_at', 'SET NOT NULL'),
            ('tax_rates', 'updated_at', 'SET NOT NULL'),
            ('package_methods', 'created_at', 'SET NOT NULL'),
            ('package_methods', 'updated_at', 'SET NOT NULL'),
        ]
        
        for table_name, column_name, constraint in nullable_fixes:
            sql = f"""
            ALTER TABLE yiboshuo.{table_name} 
            ALTER COLUMN {column_name} {constraint};
            """
            if self.execute_sql(sql, commit=False):
                logger.info(f"  ✓ 修复 {table_name}.{column_name} 可空性")
        
        self.conn.commit()
    
    def fix_default_values(self):
        """修复默认值"""
        logger.info("🔧 修复默认值...")
        
        # 需要修复的默认值
        default_fixes = [
            ('color_cards', 'created_at', 'SET DEFAULT now()'),
            ('color_cards', 'updated_at', 'SET DEFAULT now()'),
            ('customer_category_management', 'created_at', 'SET DEFAULT now()'),
            ('customer_category_management', 'updated_at', 'SET DEFAULT now()'),
            ('delivery_methods', 'created_at', 'SET DEFAULT now()'),
            ('delivery_methods', 'updated_at', 'SET DEFAULT now()'),
            ('customer_management', 'created_by', 'SET DEFAULT gen_random_uuid()'),
            ('supplier_management', 'created_by', 'SET DEFAULT gen_random_uuid()'),
            ('package_methods', 'id', 'SET DEFAULT gen_random_uuid()'),
            ('package_methods', 'created_at', 'SET DEFAULT CURRENT_TIMESTAMP'),
            ('package_methods', 'updated_at', 'SET DEFAULT CURRENT_TIMESTAMP'),
        ]
        
        for table_name, column_name, default_clause in default_fixes:
            sql = f"""
            ALTER TABLE yiboshuo.{table_name} 
            ALTER COLUMN {column_name} {default_clause};
            """
            if self.execute_sql(sql, commit=False):
                logger.info(f"  ✓ 修复 {table_name}.{column_name} 默认值")
        
        self.conn.commit()
    
    def fix_foreign_keys(self):
        """修复外键约束"""
        logger.info("🔧 修复外键约束...")
        
        # 需要添加的外键
        foreign_keys = [
            ('materials', 'material_category_id', 'material_categories', 'id'),
            ('products', 'customer_id', 'customer_management', 'id'),
            ('sales_orders', 'customer_id', 'customer_management', 'id'),
            ('delivery_notices', 'customer_id', 'customer_management', 'id'),
            ('delivery_notices', 'sales_order_id', 'sales_orders', 'id'),
            ('delivery_notice_details', 'product_id', 'products', 'id'),
            ('sales_order_details', 'product_id', 'products', 'id'),
            ('sales_order_materials', 'material_id', 'materials', 'id'),
            ('sales_order_other_fees', 'product_id', 'products', 'id'),
            ('product_materials', 'material_id', 'materials', 'id'),
            ('material_suppliers', 'material_id', 'materials', 'id'),
            ('bag_types', 'production_unit_id', 'units', 'id'),
            ('bag_types', 'sales_unit_id', 'units', 'id'),
            ('bag_type_structures', 'bag_type_id', 'bag_types', 'id'),
            ('quote_accessories', 'calculation_scheme_id', 'calculation_schemes', 'id'),
            ('process_machines', 'machine_id', 'machines', 'id'),
            ('product_transfer_orders', 'department_id', 'departments', 'id'),
        ]
        
        for table_name, column_name, ref_table, ref_column in foreign_keys:
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
    
    def run_all_fixes(self):
        """运行所有修复"""
        logger.info("🚀 开始修复yiboshuo schema...")
        
        try:
            # 按顺序执行修复
            self.fix_missing_tables()
            self.fix_extra_tables()
            self.fix_product_categories_table()
            self.fix_material_categories_table()
            self.fix_timestamp_columns()
            self.fix_nullable_columns()
            self.fix_default_values()
            self.fix_foreign_keys()
            
            logger.info("✅ 所有修复完成！")
            
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
    
    fixer = SchemaFixer(db_config)
    
    try:
        fixer.connect()
        
        # 提示用户确认
        print("⚠️  警告：此操作将修改yiboshuo schema的结构，请确保已备份数据！")
        print("要继续吗？(y/N): ", end='')
        
        if len(sys.argv) > 1 and sys.argv[1] == '--force':
            confirm = 'y'
        else:
            confirm = input().lower()
        
        if confirm == 'y':
            fixer.run_all_fixes()
            print("\n🎉 Schema修复完成！")
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