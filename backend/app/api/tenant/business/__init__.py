# -*- coding: utf-8 -*-
"""
业务管理API模块
"""

from flask import Blueprint

# 创建业务管理蓝图
business_bp = Blueprint('business', __name__)

# 导入库存模块的所有蓝图
try:
    from .inventory import (
        inventory_bp,
        material_inbound_bp,
        material_outbound_bp,
        material_transfer_bp,
        product_count_bp
    )
    
    # 注册基础库存相关蓝图
    business_bp.register_blueprint(inventory_bp, url_prefix='/inventory')
    business_bp.register_blueprint(material_inbound_bp, url_prefix='/inventory/material-inbound')
    business_bp.register_blueprint(material_outbound_bp, url_prefix='/inventory/material-outbound')
    business_bp.register_blueprint(material_transfer_bp, url_prefix='/inventory/material-transfer')
    business_bp.register_blueprint(product_count_bp, url_prefix='/inventory/product-count')
    
    # 尝试注册新的库存API蓝图
    try:
        from .inventory import product_outbound_bp
        business_bp.register_blueprint(product_outbound_bp, url_prefix='/inventory/product-outbound')
        print("✅ Product outbound API registered successfully")
    except ImportError:
        print("⚠️  Warning: Could not import product_outbound_bp")
    
    try:
        from .inventory import product_inbound_bp
        business_bp.register_blueprint(product_inbound_bp, url_prefix='/inventory/product-inbound')
        print("✅ Product inbound API registered successfully")
    except ImportError:
        print("⚠️  Warning: Could not import product_inbound_bp")
    
    try:
        from .inventory import material_count_bp
        business_bp.register_blueprint(material_count_bp, url_prefix='/inventory/material-count')
        print("✅ Material count API registered successfully")
    except ImportError:
        print("⚠️  Warning: Could not import material_count_bp")
    
    try:
        from .inventory import product_transfer_bp
        business_bp.register_blueprint(product_transfer_bp, url_prefix='/inventory/product-transfer')
        print("✅ Product transfer API registered successfully")
    except ImportError:
        print("⚠️  Warning: Could not import product_transfer_bp")
    
except ImportError as e:
    print(f"Warning: Could not import inventory modules: {e}")

# 导入销售模块的所有蓝图
try:
    from .sales import (
        sales_order_bp,
        delivery_notice_bp
    )
    
    # 注册销售相关蓝图 - 修复路径匹配问题
    # 前端请求: /tenant/business/sales/sales-orders
    # 后端注册: /tenant/business + /sales + /sales-orders
    business_bp.register_blueprint(sales_order_bp, url_prefix='/sales')
    business_bp.register_blueprint(delivery_notice_bp, url_prefix='/sales')
    
    print("✅ Sales API registered successfully")
    
except ImportError as e:
    print(f"Warning: Could not import sales modules: {e}")

@business_bp.route('/health', methods=['GET'])  
def health_check():
    """业务模块健康检查"""
    return {
        'status': 'ok',
        'message': '业务模块API运行正常',
        'modules': ['inventory', 'sales']
    } 