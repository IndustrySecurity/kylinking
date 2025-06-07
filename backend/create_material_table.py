#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建材料管理表的脚本
"""

from app import create_app
from app.extensions import db
from sqlalchemy import text

def create_material_management_table():
    app = create_app()
    with app.app_context():
        try:
            # 检查并创建mytenant schema
            db.engine.execute(text("CREATE SCHEMA IF NOT EXISTS mytenant"))
            
            # 设置搜索路径
            db.engine.execute(text("SET search_path TO mytenant"))
            
            # 创建material_management表
            sql = text("""
            CREATE TABLE IF NOT EXISTS material_management (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                material_code VARCHAR(50),
                material_name VARCHAR(255) NOT NULL,
                material_category_id UUID,
                material_attribute VARCHAR(50),
                unit_id UUID,
                auxiliary_unit_id UUID,
                is_blown_film BOOLEAN DEFAULT FALSE,
                unit_no_conversion BOOLEAN DEFAULT FALSE,
                width_mm NUMERIC(10, 3),
                thickness_um NUMERIC(10, 3),
                specification_model VARCHAR(200),
                density NUMERIC(10, 4),
                conversion_factor NUMERIC(10, 4) DEFAULT 1,
                sales_unit_id UUID,
                inspection_type VARCHAR(20) DEFAULT 'spot_check',
                is_paper BOOLEAN DEFAULT FALSE,
                is_surface_printing_ink BOOLEAN DEFAULT FALSE,
                length_mm NUMERIC(10, 3),
                height_mm NUMERIC(10, 3),
                min_stock_start NUMERIC(15, 3),
                min_stock_end NUMERIC(15, 3),
                max_stock NUMERIC(15, 3),
                shelf_life_days INTEGER,
                warning_days INTEGER DEFAULT 0,
                standard_m_per_roll NUMERIC(10, 3) DEFAULT 0,
                is_carton BOOLEAN DEFAULT FALSE,
                is_uv_ink BOOLEAN DEFAULT FALSE,
                wind_tolerance_mm NUMERIC(10, 3) DEFAULT 0,
                tongue_mm NUMERIC(10, 3) DEFAULT 0,
                purchase_price NUMERIC(15, 4) DEFAULT 0,
                latest_purchase_price NUMERIC(15, 4) DEFAULT 0,
                latest_tax_included_price NUMERIC(15, 4),
                material_formula_id UUID,
                is_paper_core BOOLEAN DEFAULT FALSE,
                is_tube_film BOOLEAN DEFAULT FALSE,
                loss_1 NUMERIC(10, 4),
                loss_2 NUMERIC(10, 4),
                forward_formula VARCHAR(200),
                reverse_formula VARCHAR(200),
                sales_price NUMERIC(15, 4),
                subject_id UUID,
                uf_code VARCHAR(100),
                material_formula_reverse BOOLEAN DEFAULT FALSE,
                is_hot_stamping BOOLEAN DEFAULT FALSE,
                material_position VARCHAR(200),
                carton_spec_volume NUMERIC(15, 6),
                security_code VARCHAR(100),
                substitute_material_category_id UUID,
                scan_batch VARCHAR(100),
                is_woven_bag BOOLEAN DEFAULT FALSE,
                is_zipper BOOLEAN DEFAULT FALSE,
                remarks TEXT,
                is_self_made BOOLEAN DEFAULT FALSE,
                no_interface BOOLEAN DEFAULT FALSE,
                cost_object_required BOOLEAN DEFAULT FALSE,
                sort_order INTEGER DEFAULT 0,
                is_enabled BOOLEAN DEFAULT TRUE,
                created_by UUID NOT NULL DEFAULT gen_random_uuid(),
                updated_by UUID,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            db.engine.execute(sql)
            
            # 创建索引
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_material_management_code ON material_management (material_code)",
                "CREATE INDEX IF NOT EXISTS idx_material_management_name ON material_management (material_name)",
                "CREATE INDEX IF NOT EXISTS idx_material_management_category ON material_management (material_category_id)",
                "CREATE INDEX IF NOT EXISTS idx_material_management_enabled ON material_management (is_enabled)"
            ]
            
            for idx_sql in indexes:
                db.engine.execute(text(idx_sql))
            
            print("Material management table created successfully!")
            
        except Exception as e:
            print(f"Error creating table: {e}")
            
if __name__ == "__main__":
    create_material_management_table() 