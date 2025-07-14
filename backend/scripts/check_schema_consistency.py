#!/usr/bin/env python3
"""
检查多个schema之间的表结构一致性
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from collections import defaultdict
from typing import Dict, List, Tuple, Any
import json
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class SchemaConsistencyChecker:
    def __init__(self, db_config: Dict[str, str]):
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
            print(f"✓ 成功连接到数据库: {self.db_config['database']}")
        except Exception as e:
            print(f"✗ 数据库连接失败: {e}")
            sys.exit(1)
    
    def disconnect(self):
        """断开数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    def get_schema_tables(self, schema_name: str) -> List[str]:
        """获取指定schema中的所有表名"""
        query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = %s 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
        """
        self.cursor.execute(query, (schema_name,))
        return [row['table_name'] for row in self.cursor.fetchall()]
    
    def get_table_structure(self, schema_name: str, table_name: str) -> Dict[str, Any]:
        """获取表结构信息"""
        # 获取列信息
        columns_query = """
        SELECT 
            column_name,
            data_type,
            character_maximum_length,
            numeric_precision,
            numeric_scale,
            is_nullable,
            column_default,
            ordinal_position
        FROM information_schema.columns 
        WHERE table_schema = %s AND table_name = %s
        ORDER BY ordinal_position
        """
        self.cursor.execute(columns_query, (schema_name, table_name))
        columns = self.cursor.fetchall()
        
        # 获取主键信息
        pk_query = """
        SELECT kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu 
            ON tc.constraint_name = kcu.constraint_name
        WHERE tc.table_schema = %s 
            AND tc.table_name = %s 
            AND tc.constraint_type = 'PRIMARY KEY'
        ORDER BY kcu.ordinal_position
        """
        self.cursor.execute(pk_query, (schema_name, table_name))
        primary_keys = [row['column_name'] for row in self.cursor.fetchall()]
        
        # 获取外键信息
        fk_query = """
        SELECT 
            kcu.column_name,
            ccu.table_schema AS foreign_table_schema,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name,
            tc.constraint_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu 
            ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage ccu 
            ON ccu.constraint_name = tc.constraint_name
        WHERE tc.table_schema = %s 
            AND tc.table_name = %s 
            AND tc.constraint_type = 'FOREIGN KEY'
        """
        self.cursor.execute(fk_query, (schema_name, table_name))
        foreign_keys = self.cursor.fetchall()
        
        # 获取索引信息
        index_query = """
        SELECT 
            indexname,
            indexdef
        FROM pg_indexes 
        WHERE schemaname = %s AND tablename = %s
        """
        self.cursor.execute(index_query, (schema_name, table_name))
        indexes = self.cursor.fetchall()
        
        # 获取约束信息
        constraint_query = """
        SELECT 
            constraint_name,
            constraint_type
        FROM information_schema.table_constraints
        WHERE table_schema = %s AND table_name = %s
        """
        self.cursor.execute(constraint_query, (schema_name, table_name))
        constraints = self.cursor.fetchall()
        
        return {
            'columns': columns,
            'primary_keys': primary_keys,
            'foreign_keys': foreign_keys,
            'indexes': indexes,
            'constraints': constraints
        }
    
    def compare_columns(self, table_name: str, schema1_cols: List[Dict], schema2_cols: List[Dict]) -> List[str]:
        """比较两个表的列结构"""
        differences = []
        
        # 转换为字典便于比较
        schema1_dict = {col['column_name']: col for col in schema1_cols}
        schema2_dict = {col['column_name']: col for col in schema2_cols}
        
        all_columns = set(schema1_dict.keys()) | set(schema2_dict.keys())
        
        for col_name in sorted(all_columns):
            if col_name not in schema1_dict:
                differences.append(f"  列 '{col_name}' 只存在于 schema2 中")
            elif col_name not in schema2_dict:
                differences.append(f"  列 '{col_name}' 只存在于 schema1 中")
            else:
                col1, col2 = schema1_dict[col_name], schema2_dict[col_name]
                
                # 比较数据类型
                if col1['data_type'] != col2['data_type']:
                    differences.append(f"  列 '{col_name}' 数据类型不一致: {col1['data_type']} vs {col2['data_type']}")
                
                # 比较是否可为空
                if col1['is_nullable'] != col2['is_nullable']:
                    differences.append(f"  列 '{col_name}' 可空性不一致: {col1['is_nullable']} vs {col2['is_nullable']}")
                
                # 比较默认值
                if col1['column_default'] != col2['column_default']:
                    differences.append(f"  列 '{col_name}' 默认值不一致: {col1['column_default']} vs {col2['column_default']}")
                
                # 比较字符长度
                if col1['character_maximum_length'] != col2['character_maximum_length']:
                    differences.append(f"  列 '{col_name}' 字符长度不一致: {col1['character_maximum_length']} vs {col2['character_maximum_length']}")
        
        return differences
    
    def compare_primary_keys(self, table_name: str, schema1_pks: List[str], schema2_pks: List[str]) -> List[str]:
        """比较主键"""
        differences = []
        
        if set(schema1_pks) != set(schema2_pks):
            differences.append(f"  主键不一致: {schema1_pks} vs {schema2_pks}")
        
        return differences
    
    def compare_foreign_keys(self, table_name: str, schema1_fks: List[Dict], schema2_fks: List[Dict]) -> List[str]:
        """比较外键"""
        differences = []
        
        # 简化外键比较
        schema1_fk_set = {(fk['column_name'], fk['foreign_table_name'], fk['foreign_column_name']) for fk in schema1_fks}
        schema2_fk_set = {(fk['column_name'], fk['foreign_table_name'], fk['foreign_column_name']) for fk in schema2_fks}
        
        only_in_schema1 = schema1_fk_set - schema2_fk_set
        only_in_schema2 = schema2_fk_set - schema1_fk_set
        
        for fk in only_in_schema1:
            differences.append(f"  外键 '{fk[0]} -> {fk[1]}.{fk[2]}' 只存在于 schema1 中")
        
        for fk in only_in_schema2:
            differences.append(f"  外键 '{fk[0]} -> {fk[1]}.{fk[2]}' 只存在于 schema2 中")
        
        return differences
    
    def compare_schemas(self, schema1: str, schema2: str) -> Dict[str, Any]:
        """比较两个schema的结构"""
        print(f"\n🔍 开始比较 schema: {schema1} vs {schema2}")
        
        # 获取所有表
        schema1_tables = set(self.get_schema_tables(schema1))
        schema2_tables = set(self.get_schema_tables(schema2))
        
        print(f"  {schema1} 中的表数量: {len(schema1_tables)}")
        print(f"  {schema2} 中的表数量: {len(schema2_tables)}")
        
        # 表级别差异
        only_in_schema1 = schema1_tables - schema2_tables
        only_in_schema2 = schema2_tables - schema1_tables
        common_tables = schema1_tables & schema2_tables
        
        results = {
            'schema1': schema1,
            'schema2': schema2,
            'only_in_schema1': list(only_in_schema1),
            'only_in_schema2': list(only_in_schema2),
            'common_tables': list(common_tables),
            'table_differences': {}
        }
        
        # 比较公共表的结构
        for table_name in sorted(common_tables):
            print(f"  📋 检查表: {table_name}")
            
            schema1_structure = self.get_table_structure(schema1, table_name)
            schema2_structure = self.get_table_structure(schema2, table_name)
            
            table_diffs = []
            
            # 比较列
            col_diffs = self.compare_columns(table_name, schema1_structure['columns'], schema2_structure['columns'])
            table_diffs.extend(col_diffs)
            
            # 比较主键
            pk_diffs = self.compare_primary_keys(table_name, schema1_structure['primary_keys'], schema2_structure['primary_keys'])
            table_diffs.extend(pk_diffs)
            
            # 比较外键
            fk_diffs = self.compare_foreign_keys(table_name, schema1_structure['foreign_keys'], schema2_structure['foreign_keys'])
            table_diffs.extend(fk_diffs)
            
            if table_diffs:
                results['table_differences'][table_name] = table_diffs
        
        return results
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """生成差异报告"""
        report = []
        report.append("=" * 80)
        report.append(f"Schema 一致性检查报告")
        report.append(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"比较对象: {results['schema1']} vs {results['schema2']}")
        report.append("=" * 80)
        
        # 表级别差异
        if results['only_in_schema1']:
            report.append(f"\n❌ 只存在于 {results['schema1']} 中的表:")
            for table in sorted(results['only_in_schema1']):
                report.append(f"  - {table}")
        
        if results['only_in_schema2']:
            report.append(f"\n❌ 只存在于 {results['schema2']} 中的表:")
            for table in sorted(results['only_in_schema2']):
                report.append(f"  - {table}")
        
        # 结构差异
        if results['table_differences']:
            report.append(f"\n⚠️  表结构差异:")
            for table_name, differences in results['table_differences'].items():
                report.append(f"\n📋 表: {table_name}")
                for diff in differences:
                    report.append(diff)
        
        # 总结
        report.append(f"\n📊 总结:")
        report.append(f"  - 公共表数量: {len(results['common_tables'])}")
        report.append(f"  - 只在 {results['schema1']} 中的表: {len(results['only_in_schema1'])}")
        report.append(f"  - 只在 {results['schema2']} 中的表: {len(results['only_in_schema2'])}")
        report.append(f"  - 有结构差异的表: {len(results['table_differences'])}")
        
        if not results['only_in_schema1'] and not results['only_in_schema2'] and not results['table_differences']:
            report.append(f"\n✅ 恭喜！两个schema的表结构完全一致！")
        else:
            report.append(f"\n❌ 发现不一致的地方，请检查上述差异。")
        
        return "\n".join(report)

def main():
    # 数据库配置
    db_config = {
        'host': os.getenv('DATABASE_HOST', 'postgres'),  # 使用容器名
        'database': os.getenv('DATABASE_NAME', 'saas_platform'),
        'user': os.getenv('DATABASE_USER', 'postgres'),
        'password': os.getenv('DATABASE_PASSWORD', 'postgres'),
        'port': os.getenv('DATABASE_PORT', '5432')
    }
    
    # 要比较的schema
    schema1 = 'wanle'
    schema2 = 'yiboshuo'
    
    if len(sys.argv) > 1:
        schema1 = sys.argv[1]
    if len(sys.argv) > 2:
        schema2 = sys.argv[2]
    
    checker = SchemaConsistencyChecker(db_config)
    
    try:
        checker.connect()
        results = checker.compare_schemas(schema1, schema2)
        
        # 生成报告
        report = checker.generate_report(results)
        print(report)
        
        # 保存报告到文件
        report_file = f"schema_consistency_report_{schema1}_vs_{schema2}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n📄 报告已保存到: {report_file}")
        
        # 保存详细结果为JSON
        json_file = f"schema_consistency_data_{schema1}_vs_{schema2}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"📋 详细数据已保存到: {json_file}")
        
    except Exception as e:
        print(f"❌ 检查过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        checker.disconnect()

if __name__ == "__main__":
    main() 