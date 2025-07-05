# -*- coding: utf-8 -*-
"""
销售管理API模块
"""
from flask import Blueprint

from .sales_order import bp as sales_order_bp
from .delivery_notice import bp as delivery_notice_bp

# 创建销售主蓝图
sales_bp = Blueprint('sales', __name__)

# 注册子蓝图
sales_bp.register_blueprint(sales_order_bp)
sales_bp.register_blueprint(delivery_notice_bp)


__all__ = [
    'sales_bp',
] 