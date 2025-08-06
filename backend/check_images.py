#!/usr/bin/env python3
"""
检查数据库中的图片记录
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import create_app, db
from app.models.basic_data import ProductImage

def check_images():
    """检查数据库中的图片记录"""
    app = create_app()
    
    with app.app_context():
        # 获取所有图片记录
        all_images = ProductImage.query.all()
        
        print(f"数据库中总共有 {len(all_images)} 条图片记录")
        
        if all_images:
            print("\n图片记录详情:")
            for i, image in enumerate(all_images, 1):
                print(f"{i}. ID: {image.id}")
                print(f"   产品ID: {image.product_id}")
                print(f"   图片名称: {image.image_name}")
                print(f"   图片URL: {image.image_url}")
                print(f"   图片类型: {image.image_type}")
                print(f"   文件大小: {image.file_size}")
                print(f"   排序: {image.sort_order}")
                print(f"   创建时间: {image.created_at}")
                print()
        else:
            print("数据库中没有图片记录")

if __name__ == '__main__':
    check_images() 