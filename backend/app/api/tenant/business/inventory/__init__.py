# -*- coding: utf-8 -*-
"""
库存业务模块 - API层

提供完整的库存管理API接口：
- 基础库存管理
- 材料入库管理  
- 材料出库管理
- 材料盘点管理
- 材料调拨管理
- 产品入库管理
- 产品出库管理
- 产品盘点管理
- 成品调拨管理
"""

from .inventory import bp as inventory_bp
from .material_inbound import bp as material_inbound_bp
from .material_outbound import bp as material_outbound_bp
from .material_transfer import bp as material_transfer_bp
from .product_count import bp as product_count_bp

# 尝试导入新的API模块
try:
    from .product_outbound import bp as product_outbound_bp
    _has_product_outbound = True
except ImportError:
    _has_product_outbound = False
    print("Warning: product_outbound module not found")

try:
    from .product_inbound import bp as product_inbound_bp
    _has_product_inbound = True
except ImportError:
    _has_product_inbound = False
    print("Warning: product_inbound module not found")

try:
    from .material_count import bp as material_count_bp
    _has_material_count = True
except ImportError:
    _has_material_count = False
    print("Warning: material_count module not found")

try:
    from .product_transfer import bp as product_transfer_bp
    _has_product_transfer = True
except ImportError:
    _has_product_transfer = False
    print("Warning: product_transfer module not found")

# 导出所有API蓝图
__all__ = [
    'inventory_bp',
    'material_inbound_bp', 
    'material_outbound_bp',
    'material_transfer_bp',
    'product_count_bp'
]

# 添加新的蓝图（如果存在）
if _has_product_outbound:
    __all__.append('product_outbound_bp')

if _has_product_inbound:
    __all__.append('product_inbound_bp')

if _has_material_count:
    __all__.append('material_count_bp')

if _has_product_transfer:
    __all__.append('product_transfer_bp') 