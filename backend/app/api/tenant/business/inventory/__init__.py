# -*- coding: utf-8 -*-
"""
库存业务模块 - API层

提供完整的库存管理API接口：
- 基础库存管理
- 材料入库管理  
- 材料出库管理
- 出库订单管理
- 材料调拨管理
- 产品盘点管理
"""

from .inventory import bp as inventory_bp
from .material_inbound import bp as material_inbound_bp
from .material_outbound import bp as material_outbound_bp
from .outbound_order import bp as outbound_order_bp
from .material_transfer import bp as material_transfer_bp
from .product_count import bp as product_count_bp

# 导出所有API蓝图
__all__ = [
    'inventory_bp',
    'material_inbound_bp', 
    'material_outbound_bp',
    'outbound_order_bp',
    'material_transfer_bp',
    'product_count_bp'
] 