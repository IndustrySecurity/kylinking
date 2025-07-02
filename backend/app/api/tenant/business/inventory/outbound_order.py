"""
出库订单管理 API

提供出库订单的完整管理功能：
- 出库订单列表查询和创建
- 出库订单详情获取和更新
- 出库订单删除和状态管理
- 出库订单审核、执行、取消流程
- 出库订单明细管理
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.api.tenant.routes import tenant_required
import logging

# 设置蓝图
bp = Blueprint('outbound_order', __name__)
logger = logging.getLogger(__name__)

# ==================== 出库订单管理 ====================

@bp.route('/outbound-orders', methods=['GET'])
@jwt_required()
@tenant_required
def get_outbound_orders():
    """获取出库单列表"""
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        page_size = min(int(request.args.get('page_size', 20)), 100)
        order_number = request.args.get('order_number')
        warehouse_id = request.args.get('warehouse_id')
        customer_id = request.args.get('customer_id')
        status = request.args.get('status')
        approval_status = request.args.get('approval_status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 获取当前用户和租户信息
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        if not tenant_id:
            return jsonify({'error': '租户信息缺失'}), 400
        
        # 获取出库单列表
        from app.services.business.inventory.outbound_order_service import OutboundOrderService
        service = OutboundOrderService()
        result = service.get_outbound_order_list(
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
        logger.error(f"获取出库单列表失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/outbound-orders/<order_id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_outbound_order(order_id):
    """获取出库单详情"""
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        from app.services.business.inventory.outbound_order_service import OutboundOrderService
        service = OutboundOrderService()
        order = service.get_outbound_order_by_id(order_id)
        
        return jsonify({
            'success': True,
            'data': order
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"获取出库单详情失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/outbound-orders', methods=['POST'])
@jwt_required()
@tenant_required
def create_outbound_order():
    """创建出库单"""
    try:
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        if not data.get('warehouse_id'):
            return jsonify({'error': '仓库ID不能为空'}), 400
        
        from app.services.business.inventory.outbound_order_service import OutboundOrderService
        service = OutboundOrderService()
        order = service.create_outbound_order(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': order,
            'message': '出库单创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"创建出库单失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/outbound-orders/<order_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_outbound_order(order_id):
    """更新出库单"""
    try:
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        from app.services.business.inventory.outbound_order_service import OutboundOrderService
        service = OutboundOrderService()
        order = service.update_outbound_order(order_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': order,
            'message': '出库单更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"更新出库单失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/outbound-orders/<order_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_outbound_order(order_id):
    """删除出库单"""
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        from app.services.business.inventory.outbound_order_service import OutboundOrderService
        service = OutboundOrderService()
        service.delete_outbound_order(order_id)
        
        return jsonify({
            'success': True,
            'message': '出库单删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"删除出库单失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/outbound-orders/<order_id>/approve', methods=['POST'])
@jwt_required()
@tenant_required
def approve_outbound_order(order_id):
    """审核出库单"""
    try:
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        from app.services.business.inventory.outbound_order_service import OutboundOrderService
        service = OutboundOrderService()
        order = service.approve_outbound_order(order_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': order,
            'message': '出库单审核成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"审核出库单失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/outbound-orders/<order_id>/execute', methods=['POST'])
@jwt_required()
@tenant_required
def execute_outbound_order(order_id):
    """执行出库单"""
    try:
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        from app.services.business.inventory.outbound_order_service import OutboundOrderService
        service = OutboundOrderService()
        order = service.execute_outbound_order(order_id, current_user_id)
        
        return jsonify({
            'success': True,
            'data': order,
            'message': '出库单执行成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"执行出库单失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/outbound-orders/<order_id>/cancel', methods=['POST'])
@jwt_required()
@tenant_required
def cancel_outbound_order(order_id):
    """取消出库单"""
    try:
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        data = request.get_json() or {}
        
        from app.services.business.inventory.outbound_order_service import OutboundOrderService
        service = OutboundOrderService()
        order = service.cancel_outbound_order(order_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': order,
            'message': '出库单取消成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"取消出库单失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ==================== 出库订单明细管理 ====================

@bp.route('/outbound-orders/<order_id>/details', methods=['GET'])
@jwt_required()
@tenant_required
def get_outbound_order_details(order_id):
    """获取出库单明细列表"""
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        from app.services.business.inventory.outbound_order_service import OutboundOrderService
        service = OutboundOrderService()
        details = service.get_outbound_order_details(order_id)
        
        return jsonify({
            'success': True,
            'data': details
        })
        
    except Exception as e:
        logger.error(f"获取出库单明细失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/outbound-orders/<order_id>/details', methods=['POST'])
@jwt_required()
@tenant_required
def create_outbound_order_detail(order_id):
    """创建出库单明细"""
    try:
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        from app.services.business.inventory.outbound_order_service import OutboundOrderService
        service = OutboundOrderService()
        detail = service.create_outbound_order_detail(order_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': detail,
            'message': '出库单明细创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"创建出库单明细失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/outbound-orders/<order_id>/details/<detail_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_outbound_order_detail(order_id, detail_id):
    """更新出库单明细"""
    try:
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        from app.services.business.inventory.outbound_order_service import OutboundOrderService
        service = OutboundOrderService()
        detail = service.update_outbound_order_detail(order_id, detail_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': detail,
            'message': '出库单明细更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"更新出库单明细失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/outbound-orders/<order_id>/details/<detail_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_outbound_order_detail(order_id, detail_id):
    """删除出库单明细"""
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        from app.services.business.inventory.outbound_order_service import OutboundOrderService
        service = OutboundOrderService()
        service.delete_outbound_order_detail(order_id, detail_id)
        
        return jsonify({
            'success': True,
            'message': '出库单明细删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"删除出库单明细失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/outbound-orders/<order_id>/details/batch', methods=['POST'])
@jwt_required()
@tenant_required
def batch_create_outbound_order_details(order_id):
    """批量创建出库单明细"""
    try:
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        data = request.get_json()
        
        if not data or not isinstance(data, list):
            return jsonify({'error': '请求数据必须是数组'}), 400
        
        from app.services.business.inventory.outbound_order_service import OutboundOrderService
        service = OutboundOrderService()
        
        details = []
        for detail_data in data:
            detail = service.create_outbound_order_detail(order_id, detail_data, current_user_id)
            details.append(detail)
        
        return jsonify({
            'success': True,
            'data': details,
            'message': '出库单明细批量创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"批量创建出库单明细失败: {str(e)}")
        return jsonify({'error': str(e)}), 500 