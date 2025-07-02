# -*- coding: utf-8 -*-
"""
业务管理API模块
"""

from flask import Blueprint, request, jsonify

# 创建业务管理蓝图
business_bp = Blueprint('business', __name__)

# 暂时注释掉有问题的导入，只保留基本功能
# from .sales import sales_bp
# from .production import production_bp
# business_bp.register_blueprint(sales_bp, url_prefix='/sales')  
# business_bp.register_blueprint(production_bp, url_prefix='/production')

# 创建库存管理API
@business_bp.route('/inventory/inventories', methods=['GET'])
def get_inventories():
    """获取库存列表 - 模拟数据"""
    try:
        page = int(request.args.get('page', 1))
        page_size = min(int(request.args.get('page_size', 20)), 100)
        
        # 模拟库存数据
        mock_inventories = [
            {
                'id': '1',
                'product_name': 'PP编织袋-50KG',
                'warehouse_name': '成品仓库B',
                'current_quantity': 1200.0,
                'available_quantity': 1000.0,
                'unit': '袋',
                'unit_cost': 2.5,
                'status': 'normal'
            },
            {
                'id': '2',
                'product_name': 'PE塑料袋-25KG',
                'warehouse_name': '成品仓库B',
                'current_quantity': 800.0,
                'available_quantity': 750.0,
                'unit': '袋',
                'unit_cost': 1.8,
                'status': 'low_stock'
            },
            {
                'id': '3',
                'product_name': '复合包装袋-30KG',
                'warehouse_name': '成品仓库B',
                'current_quantity': 600.0,
                'available_quantity': 580.0,
                'unit': '袋',
                'unit_cost': 3.2,
                'status': 'normal'
            }
        ]
        
        # 分页处理
        total = len(mock_inventories)
        start = (page - 1) * page_size
        end = start + page_size
        inventories = mock_inventories[start:end]
        
        return jsonify({
            'success': True,
            'data': {
                'inventories': inventories,
                'pagination': {
                    'current_page': page,
                    'page_size': page_size,
                    'total': total,
                    'pages': (total + page_size - 1) // page_size,
                    'has_prev': page > 1,
                    'has_next': page * page_size < total
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取库存列表失败: {str(e)}'
        }), 500

@business_bp.route('/health', methods=['GET'])  
def health_check():
    """业务模块健康检查"""
    return {
        'status': 'ok',
        'message': '业务模块API运行正常',
        'modules': ['inventory']
    } 