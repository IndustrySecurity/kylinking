# -*- coding: utf-8 -*-
"""
生产模块API
包含生产档案和生产配置两个子模块
"""

from flask import Blueprint

# 创建生产模块主蓝图
production_bp = Blueprint('production', __name__)

# ==================== 生产档案 ====================
from .production_archive import production_archive_bp

# ==================== 生产配置 ====================
from .production_config import production_config_bp

# 注册子模块蓝图
production_bp.register_blueprint(production_archive_bp, url_prefix='/production-archive')
production_bp.register_blueprint(production_config_bp, url_prefix='/production-config')

@production_bp.route('/health', methods=['GET'])
def health_check():
    """生产模块健康检查"""
    return {
        'status': 'ok',
        'message': '生产模块API运行正常',
        'modules': [
            'production_archive',  # 生产档案
            'production_config'    # 生产配置
        ]
    } 