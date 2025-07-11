"""
产品入库管理 API

提供产品入库的完整管理功能：
- 产品入库列表查询和创建
- 产品入库详情获取和更新
- 产品入库删除和状态管理
- 产品入库审核、执行、取消流程
- 产品入库明细管理
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.api.tenant.routes import tenant_required
from app.services.business.inventory.product_inbound_service import ProductInboundService
import logging

# 设置蓝图
bp = Blueprint('product_inbound', __name__)
logger = logging.getLogger(__name__)

# ==================== 产品入库管理 ====================

@bp.route('/product-inbound-orders', methods=['GET'])
@jwt_required()
@tenant_required
def get_product_inbound_orders():
    """获取产品入库单列表"""
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        page_size = min(int(request.args.get('page_size', 20)), 100)
        order_number = request.args.get('order_number')
        warehouse_id = request.args.get('warehouse_id')
        supplier_id = request.args.get('supplier_id')
        status = request.args.get('status')
        approval_status = request.args.get('approval_status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        
        # 获取产品入库单列表
        service = ProductInboundService()
        result = service.get_product_inbound_order_list(
            warehouse_id=warehouse_id,
            status=status,
            approval_status=approval_status,
            start_date=start_date,
            end_date=end_date,
            search=order_number,
            page=page,
            page_size=page_size
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"获取产品入库单列表失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


# 获取产品入库单详情
@bp.route('/product-inbound-orders/<order_id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_product_inbound_order(order_id):
    """获取产品入库单详情"""
    try:

        service = ProductInboundService()
        order = service.get_product_inbound_order_by_id(order_id)
        
        if not order:
            return jsonify({'error': '产品入库单不存在'}), 404
        
        return jsonify({
            'success': True,
            'data': order
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"获取产品入库单详情失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


# 创建产品入库单
@bp.route('/product-inbound-orders', methods=['POST'])
@jwt_required()
@tenant_required
def create_product_inbound_order():
    """创建产品入库单"""
    try:
        current_user_id = get_jwt_identity()

        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        if not data.get('warehouse_id'):
            return jsonify({'error': '仓库ID不能为空'}), 400
        
        service = ProductInboundService()
        order = service.create_product_inbound_order(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': order,
            'message': '产品入库单创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"创建产品入库单失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


# 更新产品入库单
@bp.route('/product-inbound-orders/<order_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_product_inbound_order(order_id):
    """更新产品入库单"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        service = ProductInboundService()
        result = service.update_product_inbound_order(order_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '产品入库单更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"更新产品入库单失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/product-inbound-orders/<order_id>/cancel', methods=['POST'])
@jwt_required()
@tenant_required
def cancel_product_inbound_order(order_id):
    """取消产品入库单"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        # 正确传递参数：order_id, cancel_data, cancelled_by
        service = ProductInboundService()
        result = service.cancel_product_inbound_order(order_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '产品入库单取消成功'
        })
            
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"取消产品入库单失败: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/product-inbound-orders/<order_id>/delete', methods=['POST'])
@jwt_required()
@tenant_required
def delete_product_inbound_order(order_id):
    """删除产品入库单"""
    try:
        current_user_id = get_jwt_identity()

        service = ProductInboundService()
        success = service.delete_product_inbound_order(order_id)
        
        return jsonify({
            'success': True,
            'message': '产品入库单删除成功'
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"删除产品入库单失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/product-inbound-orders/<order_id>/approve', methods=['POST'])
@jwt_required()
@tenant_required
def approve_product_inbound_order(order_id):
    """审核产品入库单"""
    try:
        current_user_id = get_jwt_identity()

        data = request.get_json()
        approval_status = data.get('approval_status', 'approved')
        
        service = ProductInboundService()
        result = service.approve_product_inbound_order(order_id, approval_status, current_user_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '产品入库单审核成功'
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"审核产品入库单失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ==================== 产品入库单明细管理 ====================

@bp.route('/product-inbound-orders/<order_id>/details', methods=['GET'])
@jwt_required()
@tenant_required
def get_product_inbound_order_details(order_id):
    """获取产品入库单明细列表"""
    try:
        service = ProductInboundService()
        details = service.get_product_inbound_order_details(order_id)
        
        return jsonify({
            'success': True,
            'data': details
        })
        
    except Exception as e:
        logger.error(f"获取产品入库单明细失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/product-inbound-orders/<order_id>/details', methods=['POST'])
@jwt_required()
@tenant_required
def create_product_inbound_order_detail(order_id):
    """创建产品入库单明细"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        service = ProductInboundService()
        detail = service.create_product_inbound_order_detail(order_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': detail,
            'message': '产品入库单明细创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"创建产品入库单明细失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/product-inbound-orders/<order_id>/details/<detail_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_product_inbound_order_detail(order_id, detail_id):
    """更新产品入库单明细"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        service = ProductInboundService()
        detail = service.update_product_inbound_order_detail(order_id, detail_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': detail,
            'message': '产品入库单明细更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"更新产品入库单明细失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/product-inbound-orders/<order_id>/details/<detail_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_product_inbound_order_detail(order_id, detail_id):
    """删除产品入库单明细"""
    try:
        service = ProductInboundService()
        success = service.delete_product_inbound_order_detail(order_id, detail_id)
        
        if not success:
            return jsonify({'error': '明细记录不存在或无法删除'}), 404

        return jsonify({
            'success': True,
            'message': '产品入库单明细删除成功'
        })

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"删除产品入库单明细失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/product-inbound-orders/<order_id>/execute', methods=['POST'])
@jwt_required()
@tenant_required
def execute_product_inbound_order(order_id):
    """执行产品入库单"""
    try:
        current_user_id = get_jwt_identity()

        service = ProductInboundService()
        result = service.execute_product_inbound_order(order_id, current_user_id)

        return jsonify({
            'success': True,
            'data': result,
            'message': '产品入库单执行成功'
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"执行产品入库单失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ==================== 批量操作 ====================
@bp.route('/product-inbound-orders/<order_id>/details/batch', methods=['POST'])
@jwt_required()
@tenant_required
def batch_create_product_inbound_order_details(order_id):
    """批量创建产品入库单明细"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data.get('details'):
            return jsonify({'error': '明细数据不能为空'}), 400
        
        service = ProductInboundService()
        details = service.batch_create_product_inbound_order_details(
            order_id, data['details'], current_user_id
        )
        
        return jsonify({
            'success': True,
            'data': details,
            'message': f'成功创建 {len(details)} 条产品入库单明细'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"批量创建产品入库单明细失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/product-inbound-orders/<order_id>/details/batch', methods=['PUT'])
@jwt_required()
@tenant_required
def batch_update_product_inbound_order_details(order_id):
    """批量更新产品入库单明细"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data.get('details'):
            return jsonify({'error': '明细数据不能为空'}), 400
        
        service = ProductInboundService()
        details = service.batch_update_product_inbound_order_details(
            order_id, data['details'], current_user_id
        )
        
        return jsonify({
            'success': True,
            'data': details,
            'message': f'成功更新 {len(details)} 条产品入库单明细'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"批量更新产品入库单明细失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/product-inbound-orders/<order_id>/details/batch', methods=['DELETE'])
@jwt_required()
@tenant_required
def batch_delete_product_inbound_order_details(order_id):
    """批量删除产品入库单明细"""
    try:
        data = request.get_json()
        
        if not data or not data.get('detail_ids'):
            return jsonify({'error': '明细ID列表不能为空'}), 400
        
        service = ProductInboundService()
        deleted_count = service.batch_delete_product_inbound_order_details(
            order_id, data['detail_ids']
        )
        
        return jsonify({
            'success': True,
            'message': f'成功删除 {deleted_count} 条产品入库单明细'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"批量删除产品入库单明细失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ==================== 报表和导出功能 ====================

@bp.route('/reports/inbound-statistics', methods=['GET'])
@jwt_required()
@tenant_required
def get_inbound_statistics():
    """获取入库统计报表"""
    try:
        # 获取查询参数
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        warehouse_id = request.args.get('warehouse_id')
        product_id = request.args.get('product_id')
        
        # 这里实现统计逻辑，暂时返回模拟数据
        statistics = {
            'total_orders': 100,
            'total_quantity': 5000,
            'total_amount': 250000,
            'by_warehouse': [
                {'warehouse_id': '1', 'warehouse_name': '成品仓库A', 'orders': 50, 'quantity': 2500},
                {'warehouse_id': '2', 'warehouse_name': '成品仓库B', 'orders': 50, 'quantity': 2500}
            ],
            'by_product': [
                {'product_id': '1', 'product_name': '产品A', 'quantity': 2000},
                {'product_id': '2', 'product_name': '产品B', 'quantity': 3000}
            ]
        }
        
        return jsonify({
            'success': True,
            'data': statistics
        })
        
    except Exception as e:
        logger.error(f"获取入库统计失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/product-inbound-orders/<order_id>/export', methods=['GET'])
@jwt_required()
@tenant_required
def export_product_inbound_order(order_id):
    """导出产品入库单"""
    try:
        service = ProductInboundService()
        order = service.get_product_inbound_order_by_id(order_id)
        
        if not order:
            return jsonify({'error': '产品入库单不存在'}), 404
        
        # 这里实现导出逻辑，暂时返回成功消息
        # 实际应用中应该生成Excel/PDF文件并返回
        
        return jsonify({
            'success': True,
            'message': '导出成功',
            'download_url': f'/api/downloads/inbound-order-{order_id}.xlsx'
        })
        
    except Exception as e:
        logger.error(f"导出产品入库单失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/export', methods=['GET'])
@jwt_required()
@tenant_required
def export_product_inbound_order_list():
    """导出产品入库单列表"""
    try:
        # 获取查询参数（与列表查询相同）
        warehouse_id = request.args.get('warehouse_id')
        status = request.args.get('status')
        approval_status = request.args.get('approval_status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 这里实现导出逻辑，暂时返回成功消息
        # 实际应用中应该生成Excel/PDF文件并返回
        
        return jsonify({
            'success': True,
            'message': '导出成功',
            'download_url': '/api/downloads/inbound-orders.xlsx'
        })
        
    except Exception as e:
        logger.error(f"导出产品入库单列表失败: {str(e)}")
        return jsonify({'error': str(e)}), 500