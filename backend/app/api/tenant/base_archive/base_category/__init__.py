# -*- coding: utf-8 -*-
"""
基础分类模块API
包含客户分类、供应商分类、产品分类、材料分类、工艺分类等功能的API
"""

from flask import Blueprint

# 创建基础分类模块主蓝图
base_category_bp = Blueprint('base_category', __name__)

# ==================== 分类管理 ====================
from .customer_category import bp as customer_category_bp
from .supplier_category import bp as supplier_category_bp
from .product_category import bp as product_category_bp
from .material_category import bp as material_category_bp
from .process_category import bp as process_category_bp

# 注册各个API蓝图
base_category_bp.register_blueprint(customer_category_bp, url_prefix='/customer-categories')
base_category_bp.register_blueprint(supplier_category_bp, url_prefix='/supplier-categories')
base_category_bp.register_blueprint(product_category_bp, url_prefix='/product-categories')
base_category_bp.register_blueprint(material_category_bp, url_prefix='/material-categories')
base_category_bp.register_blueprint(process_category_bp, url_prefix='/process-categories')

@base_category_bp.route('/health', methods=['GET'])
def health_check():
    """基础分类模块健康检查"""
    return {
        'status': 'ok',
        'message': '基础分类模块API运行正常',
        'modules': [
            'customer_categories',  # 客户分类
            'supplier_categories',  # 供应商分类
            'product_categories',   # 产品分类
            'material_categories',  # 材料分类
            'process_categories'    # 工艺分类
        ]
    }