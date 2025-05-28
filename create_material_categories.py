#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建材料分类表的脚本
"""

import psycopg2
import uuid
from datetime import datetime

# 数据库连接配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'saas_platform',
    'user': 'postgres',
    'password': 'postgres123'  # 默认密码，可能需要调整
}

def create_material_categories_table():
    """在wanle schema中创建材料分类表"""
    conn = None
    cursor = None
    try:
        # 连接数据库
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 设置search_path
        cursor.execute("SET search_path TO wanle, public;")
        
        # 创建材料分类表
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS material_categories (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            
            -- 基本信息
            material_name VARCHAR(100) NOT NULL,
            material_type VARCHAR(20) NOT NULL CHECK (material_type IN ('主材', '辅材')),
            
            -- 单位信息
            base_unit_id UUID,
            auxiliary_unit_id UUID,
            sales_unit_id UUID,
            
            -- 物理属性
            density NUMERIC(10, 4),
            square_weight NUMERIC(10, 4),
            shelf_life INTEGER,
            
            -- 检验质量
            inspection_standard VARCHAR(200),
            quality_grade VARCHAR(100),
            
            -- 价格信息
            latest_purchase_price NUMERIC(15, 4),
            sales_price NUMERIC(15, 4),
            product_quote_price NUMERIC(15, 4),
            cost_price NUMERIC(15, 4),
            
            -- 业务配置
            show_on_kanban BOOLEAN DEFAULT FALSE,
            account_subject VARCHAR(100),
            code_prefix VARCHAR(10) DEFAULT 'M',
            warning_days INTEGER,
            
            -- 纸箱参数
            carton_param1 NUMERIC(10, 3),
            carton_param2 NUMERIC(10, 3),
            carton_param3 NUMERIC(10, 3),
            carton_param4 NUMERIC(10, 3),
            
            -- 材料属性标识
            enable_batch BOOLEAN DEFAULT FALSE,
            enable_barcode BOOLEAN DEFAULT FALSE,
            is_ink BOOLEAN DEFAULT FALSE,
            is_accessory BOOLEAN DEFAULT FALSE,
            is_consumable BOOLEAN DEFAULT FALSE,
            is_recyclable BOOLEAN DEFAULT FALSE,
            is_hazardous BOOLEAN DEFAULT FALSE,
            is_imported BOOLEAN DEFAULT FALSE,
            is_customized BOOLEAN DEFAULT FALSE,
            is_seasonal BOOLEAN DEFAULT FALSE,
            is_fragile BOOLEAN DEFAULT FALSE,
            is_perishable BOOLEAN DEFAULT FALSE,
            is_temperature_sensitive BOOLEAN DEFAULT FALSE,
            is_moisture_sensitive BOOLEAN DEFAULT FALSE,
            is_light_sensitive BOOLEAN DEFAULT FALSE,
            requires_special_storage BOOLEAN DEFAULT FALSE,
            requires_certification BOOLEAN DEFAULT FALSE,
            
            -- 通用字段
            display_order INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT TRUE,
            
            -- 审计字段
            created_by UUID NOT NULL,
            updated_by UUID,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        cursor.execute(create_table_sql)
        
        # 创建索引
        index_sqls = [
            "CREATE INDEX IF NOT EXISTS idx_material_categories_name ON material_categories(material_name);",
            "CREATE INDEX IF NOT EXISTS idx_material_categories_type ON material_categories(material_type);",
            "CREATE INDEX IF NOT EXISTS idx_material_categories_active ON material_categories(is_active);",
            "CREATE INDEX IF NOT EXISTS idx_material_categories_order ON material_categories(display_order);"
        ]
        
        for sql in index_sqls:
            cursor.execute(sql)
        
        # 获取admin用户ID (从system.users表)
        cursor.execute("SELECT id FROM system.users WHERE email LIKE '%admin%' LIMIT 1;")
        admin_user = cursor.fetchone()
        
        if admin_user:
            admin_id = admin_user[0]
            
            # 插入测试数据
            test_data = [
                ('BOPP薄膜', '主材', 1),
                ('PE薄膜', '主材', 2),
                ('油墨', '辅材', 3),
                ('胶水', '辅材', 4),
                ('PET薄膜', '主材', 5),
                ('纸箱', '辅材', 6)
            ]
            
            for name, type_, order in test_data:
                cursor.execute("""
                    INSERT INTO material_categories (material_name, material_type, display_order, is_active, created_by)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING;
                """, (name, type_, order, True, admin_id))
        
        # 提交事务
        conn.commit()
        print("✅ 材料分类表创建成功！")
        
        # 查询验证
        cursor.execute("SELECT COUNT(*) FROM material_categories;")
        count = cursor.fetchone()[0]
        print(f"📊 材料分类表中有 {count} 条记录")
        
        # 显示表结构
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_schema = 'wanle' AND table_name = 'material_categories'
            ORDER BY ordinal_position;
        """)
        columns = cursor.fetchall()
        print("\n📋 表结构:")
        for col in columns:
            print(f"  - {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
        
    except Exception as e:
        print(f"❌ 创建表失败: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    create_material_categories_table() 