#!/usr/bin/env python3
"""
调试产品详情API返回的数据
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import create_app
from app.services.base_archive.base_data.product_management_service import get_product_management_service

def debug_product_detail():
    """调试产品详情API返回的数据"""
    app = create_app()
    
    with app.app_context():
        # 设置租户上下文
        from app.utils.tenant_context import TenantContext
        tenant_context = TenantContext()
        tenant_context.set_schema('wanle')  # 使用万乐包装的租户
        
        service = get_product_management_service(tenant_id='wanle', schema_name='wanle')
        
        # 获取所有产品
        products = service.get_products(page=1, per_page=10)
        
        if products and 'products' in products and products['products']:
            # 获取第一个产品的详情
            first_product = products['products'][0]
            product_id = first_product['id']
            
            print(f"调试产品详情 - 产品ID: {product_id}")
            print(f"产品名称: {first_product['product_name']}")
            
            # 获取产品详情
            product_detail = service.get_product_detail(product_id)
            
            print(f"\n产品详情数据:")
            print(f"产品ID: {product_detail.get('id')}")
            print(f"产品名称: {product_detail.get('product_name')}")
            
            # 检查图片数据
            product_images = product_detail.get('product_images', [])
            print(f"\n图片数据:")
            print(f"图片数量: {len(product_images)}")
            
            for i, image in enumerate(product_images, 1):
                print(f"图片 {i}:")
                print(f"  ID: {image.get('id')}")
                print(f"  名称: {image.get('image_name')}")
                print(f"  URL: {image.get('image_url')}")
                print(f"  类型: {image.get('image_type')}")
                print(f"  大小: {image.get('file_size')}")
                print()
        else:
            print("没有找到产品数据")

if __name__ == '__main__':
    debug_product_detail() 