#!/usr/bin/env python3
"""
清理数据库中无效的图片记录
删除那些数据库中有记录但实际文件不存在的图片记录
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import create_app, db
from app.models.basic_data import ProductImage

def cleanup_invalid_images():
    """清理无效的图片记录"""
    app = create_app()
    
    with app.app_context():
        # 获取所有图片记录
        all_images = ProductImage.query.all()
        
        print(f"总共找到 {len(all_images)} 条图片记录")
        
        invalid_count = 0
        valid_count = 0
        
        for image in all_images:
            # 构建文件路径
            if image.image_url and image.image_url.startswith('/uploads/'):
                # 去掉开头的 /uploads/，构建相对路径
                relative_path = image.image_url[9:]  # 去掉 '/uploads/'
                file_path = os.path.join('uploads', relative_path)
                
                # 检查文件是否存在
                if os.path.exists(file_path):
                    valid_count += 1
                    print(f"✓ 有效: {image.image_url}")
                else:
                    invalid_count += 1
                    print(f"✗ 无效: {image.image_url} (文件不存在)")
                    
                    # 删除无效记录
                    try:
                        db.session.delete(image)
                        print(f"  已删除数据库记录")
                    except Exception as e:
                        print(f"  删除记录失败: {e}")
            else:
                print(f"? 跳过: {image.image_url} (URL格式不正确)")
        
        # 提交更改
        try:
            db.session.commit()
            print(f"\n清理完成:")
            print(f"  有效图片: {valid_count}")
            print(f"  无效图片: {invalid_count}")
            print(f"  已删除 {invalid_count} 条无效记录")
        except Exception as e:
            print(f"提交更改失败: {e}")
            db.session.rollback()

if __name__ == '__main__':
    cleanup_invalid_images() 