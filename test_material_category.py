#!/usr/bin/env python3
"""
测试材料分类功能
"""

import sys
import os
sys.path.append('/app')

from app import create_app
from app.extensions import db
from app.models.basic_data import MaterialCategory
from sqlalchemy import text

def test_material_category():
    app = create_app()
    
    with app.app_context():
        # 设置schema
        db.session.execute(text('SET search_path TO wanle, public'))
        
        print("=== 测试材料分类功能 ===")
        
        # 1. 检查表结构
        print("\n1. 检查表结构:")
        result = db.session.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'wanle' 
            AND table_name = 'material_categories'
            ORDER BY ordinal_position
        """)).fetchall()
        
        for row in result:
            print(f"  {row[0]} - {row[1]}")
        
        # 2. 检查是否有material_code字段
        print("\n2. 检查material_code字段:")
        has_material_code = any(row[0] == 'material_code' for row in result)
        print(f"  material_code字段存在: {has_material_code}")
        
        # 3. 测试创建材料分类
        print("\n3. 测试创建材料分类:")
        try:
            # 删除可能存在的测试数据
            db.session.execute(text("DELETE FROM material_categories WHERE material_name = '测试材料分类'"))
            db.session.commit()
            
            # 创建新的材料分类
            category = MaterialCategory(
                material_name='测试材料分类',
                material_type='主材',
                display_order=1,
                is_active=True
            )
            
            db.session.add(category)
            db.session.commit()
            
            print(f"  ✓ 成功创建材料分类: {category.material_name}")
            print(f"  ID: {category.id}")
            
            # 4. 测试查询
            print("\n4. 测试查询:")
            categories = MaterialCategory.query.all()
            print(f"  总共有 {len(categories)} 个材料分类")
            
            for cat in categories:
                print(f"  - {cat.material_name} ({cat.material_type})")
            
            # 5. 测试to_dict方法
            print("\n5. 测试to_dict方法:")
            category_dict = category.to_dict()
            print(f"  字段数量: {len(category_dict)}")
            print(f"  包含material_code: {'material_code' in category_dict}")
            
            # 清理测试数据
            db.session.delete(category)
            db.session.commit()
            print("\n✓ 测试数据已清理")
            
        except Exception as e:
            print(f"  ✗ 错误: {e}")
            db.session.rollback()
        
        print("\n=== 测试完成 ===")

if __name__ == '__main__':
    test_material_category() 