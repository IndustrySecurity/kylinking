# -*- coding: utf-8 -*-
"""
租户API模块
包含所有租户相关的API端点
"""

from flask import Blueprint

# 创建租户主蓝图
tenant_bp = Blueprint('tenant', __name__)

@tenant_bp.route('/health', methods=['GET'])
def tenant_health():
    """租户API健康检查"""
    return {
        'status': 'ok',
        'message': '租户API模块运行正常',
        'modules': ['base_archive', 'business']
    }

# 直接在这里注册子蓝图
try:
    from .base_archive import base_archive_bp
    from .business import business_bp
    from .routes import production_bp
    
    # 注册子蓝图
    tenant_bp.register_blueprint(base_archive_bp, url_prefix='/base-archive')
    tenant_bp.register_blueprint(business_bp, url_prefix='/business')
    tenant_bp.register_blueprint(production_bp, url_prefix='/production')
    
    # 兼容路径 - 为前端错误的API路径创建别名
    from .base_archive.base_data import base_data_bp
    tenant_bp.register_blueprint(base_data_bp, url_prefix='/basic-data', name='basic_data_alias')
    
    print("✅ 租户子蓝图注册成功")
    
except Exception as e:
    print(f"❌ 租户子蓝图注册失败: {e}")

# 为统一导入方式提供别名
bp = tenant_bp
