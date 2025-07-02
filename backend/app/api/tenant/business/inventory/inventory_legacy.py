"""
库存管理相关API (Legacy版本 - 超大文件已拆分，此文件为占位符)

原inventory.py文件有3659行，已被拆分为以下模块：
- inventory.py - 库存查询和管理API
- material_inbound.py - 材料入库API
- material_outbound.py - 材料出库API  
- outbound_order.py - 出库订单API
- material_transfer.py - 材料调拨API
- product_count.py - 产品盘点API

注意：原inventory.py文件包含大量API，需要逐步迁移到对应的模块化API文件中。
这个legacy文件将在所有功能迁移完成后删除。
"""

from flask import Blueprint

inventory_legacy_bp = Blueprint('inventory_legacy', __name__)

# 这个文件将在原inventory.py中的所有API迁移到模块化结构后删除 