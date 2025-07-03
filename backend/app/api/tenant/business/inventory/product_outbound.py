# type: ignore
# pyright: reportGeneralTypeIssues=false
# pyright: reportAttributeAccessIssue=false
# pyright: reportOptionalMemberAccess=false
"""
产品出库管理 API

提供产品出库的完整管理功能：
- 产品出库列表查询和创建
- 产品出库详情获取和更新
- 产品出库删除和状态管理
- 产品出库审核、执行、取消流程
- 产品出库明细管理
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.api.tenant.routes import tenant_required
import logging

# 设置蓝图
bp = Blueprint('product_outbound', __name__)
logger = logging.getLogger(__name__)

# ==================== 产品出库管理 ====================

@bp.route('/product-outbound-orders', methods=['GET'])
@jwt_required()
@tenant_required
def get_outbound_orders():
    """获取产品出库单列表"""
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
        
        # 获取产品出库单列表
        from app.services.business.inventory.product_outbound_service import ProductOutboundService
        service = ProductOutboundService()
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
        logger.error(f"获取产品出库单列表失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/product-outbound-orders/<order_id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_outbound_order(order_id):
    """获取产品出库单详情"""
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        from app.services.business.inventory.product_outbound_service import ProductOutboundService
        service = ProductOutboundService()
        order = service.get_outbound_order_by_id(order_id)
        
        return jsonify({
            'success': True,
            'data': order
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"获取产品出库单详情失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/product-outbound-orders', methods=['POST'])
@jwt_required()
@tenant_required
def create_outbound_order():
    """创建产品出库单"""
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
        
        from app.services.business.inventory.product_outbound_service import ProductOutboundService
        service = ProductOutboundService()
        order = service.create_outbound_order(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': order,
            'message': '产品出库单创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"创建产品出库单失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/product-outbound-orders/<order_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_outbound_order(order_id):
    """更新产品出库单"""
    try:
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        from app.services.business.inventory.product_outbound_service import ProductOutboundService
        service = ProductOutboundService()
        order = service.update_outbound_order(order_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': order,
            'message': '产品出库单更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"更新产品出库单失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/product-outbound-orders/<order_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_outbound_order(order_id):
    """删除产品出库单"""
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        from app.services.business.inventory.product_outbound_service import ProductOutboundService
        service = ProductOutboundService()
        service.delete_outbound_order(order_id)
        
        return jsonify({
            'success': True,
            'message': '产品出库单删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"删除产品出库单失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/product-outbound-orders/<order_id>/approve', methods=['POST'])
@jwt_required()
@tenant_required
def approve_outbound_order(order_id):
    """审核产品出库单"""
    try:
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        from app.services.business.inventory.product_outbound_service import ProductOutboundService
        service = ProductOutboundService()
        order = service.approve_outbound_order(order_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': order,
            'message': '产品出库单审核成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"审核产品出库单失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/product-outbound-orders/<order_id>/execute', methods=['POST'])
@jwt_required()
@tenant_required
def execute_outbound_order(order_id):
    """执行产品出库单"""
    try:
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        from app.services.business.inventory.product_outbound_service import ProductOutboundService
        service = ProductOutboundService()
        order = service.execute_outbound_order(order_id, current_user_id)
        
        return jsonify({
            'success': True,
            'data': order,
            'message': '产品出库单执行成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"执行产品出库单失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/product-outbound-orders/<order_id>/cancel', methods=['POST'])
@jwt_required()
@tenant_required
def cancel_outbound_order(order_id):
    """取消产品出库单"""
    try:
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        data = request.get_json()
        
        from app.services.business.inventory.product_outbound_service import ProductOutboundService
        service = ProductOutboundService()
        order = service.cancel_outbound_order(order_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': order,
            'message': '产品出库单取消成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"取消产品出库单失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ==================== 产品出库单明细管理 ====================

@bp.route('/product-outbound-orders/<order_id>/details', methods=['GET'])
@jwt_required()
@tenant_required
def get_outbound_order_details(order_id):
    """获取产品出库单明细列表"""
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        from app.services.business.inventory.product_outbound_service import ProductOutboundService
        service = ProductOutboundService()
        details = service.get_outbound_order_details(order_id)
        
        return jsonify({
            'success': True,
            'data': details
        })
        
    except Exception as e:
        logger.error(f"获取产品出库单明细失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/product-outbound-orders/<order_id>/details', methods=['POST'])
@jwt_required()
@tenant_required
def create_outbound_order_detail(order_id):
    """创建产品出库单明细"""
    try:
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        from app.services.business.inventory.product_outbound_service import ProductOutboundService
        service = ProductOutboundService()
        detail = service.create_outbound_order_detail(order_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': detail,
            'message': '产品出库单明细创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"创建产品出库单明细失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/product-outbound-orders/<order_id>/details/<detail_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_outbound_order_detail(order_id, detail_id):
    """更新产品出库单明细"""
    try:
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        from app.services.business.inventory.product_outbound_service import ProductOutboundService
        service = ProductOutboundService()
        detail = service.update_outbound_order_detail(order_id, detail_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': detail,
            'message': '产品出库单明细更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"更新产品出库单明细失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/product-outbound-orders/<order_id>/details/<detail_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_outbound_order_detail(order_id, detail_id):
    """删除产品出库单明细"""
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        from app.services.business.inventory.product_outbound_service import ProductOutboundService
        service = ProductOutboundService()
        service.delete_outbound_order_detail(order_id, detail_id)
        
        return jsonify({
            'success': True,
            'message': '产品出库单明细删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"删除产品出库单明细失败: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/product-outbound-orders/<order_id>/details/batch', methods=['POST'])
@jwt_required()
@tenant_required
def batch_create_outbound_order_details(order_id):
    """批量创建产品出库单明细"""
    try:
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        data = request.get_json()
        
        if not data or not data.get('details'):
            return jsonify({'error': '明细数据不能为空'}), 400
        
        from app.services.business.inventory.product_outbound_service import ProductOutboundService
        service = ProductOutboundService()
        
        details = []
        for detail_data in data['details']:
            detail = service.create_outbound_order_detail(order_id, detail_data, current_user_id)
            details.append(detail)
        
        return jsonify({
            'success': True,
            'data': details,
            'message': f'成功创建 {len(details)} 条产品出库单明细'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"批量创建产品出库单明细失败: {str(e)}")
        return jsonify({'error': str(e)}), 500 