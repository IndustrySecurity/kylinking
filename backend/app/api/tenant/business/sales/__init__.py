# -*- coding: utf-8 -*-
"""
销售管理API模块
"""

from .sales_order import bp as sales_order_bp
from .delivery_notice import bp as delivery_notice_bp

__all__ = [
    'sales_order_bp',
    'delivery_notice_bp',
] 