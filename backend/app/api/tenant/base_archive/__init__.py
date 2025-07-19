# -*- coding: utf-8 -*-
"""
基础档案模块API
包含基础数据、财务管理、生产档案等功能的API
"""

from flask import Blueprint

# 创建基础档案模块主蓝图
base_archive_bp = Blueprint('base_archive', __name__)

# ==================== 基础数据模块 ====================
from .base_data import base_data_bp

# ==================== 财务管理模块 ====================
from .financial_management import financial_management_bp

# ==================== 生产档案模块 ====================
from .production_archive import production_archive_bp

# ==================== 生产配置模块 ====================
from .production_config import production_config_bp

# ==================== 基础分类模块 ====================
from .base_category import base_category_bp

# 注册子模块蓝图
base_archive_bp.register_blueprint(base_data_bp, url_prefix='/base-data')
base_archive_bp.register_blueprint(financial_management_bp, url_prefix='/financial-management')  
base_archive_bp.register_blueprint(production_archive_bp, url_prefix='/production-archive')
base_archive_bp.register_blueprint(production_config_bp, url_prefix='/production-config')
base_archive_bp.register_blueprint(base_category_bp, url_prefix='/base-category')

# 为了兼容前端现有路径，添加别名注册（使用不同的name避免重复）
# 财务管理API直接注册到根路径（兼容/currencies, /tax-rates等路径）
base_archive_bp.register_blueprint(financial_management_bp, url_prefix='', name='financial_management_alias')

@base_archive_bp.route('/health', methods=['GET'])
def health_check():
    """基础档案模块健康检查"""
    return {
        'status': 'ok',
        'message': '基础档案模块API运行正常',
        'modules': [
            'base_data',            # 基础数据
            'financial_management', # 财务管理
            'production_archive',   # 生产档案
            'production_config',    # 生产配置
            'base_category'         # 基础分类
        ]
    } 