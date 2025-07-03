# type: ignore
# pyright: reportGeneralTypeIssues=false
# pyright: reportAttributeAccessIssue=false
# pyright: reportOptionalMemberAccess=false
"""
成品调拨管理 API

提供成品调拨的完整管理功能：
- 成品调拨单列表查询和创建
- 成品调拨单详情获取和更新
- 成品调拨单明细管理
- 成品调拨单确认、执行、接收、取消流程
- 仓库可调拨成品查询
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.tenant.routes import tenant_required
from app.services.business.inventory.product_transfer_service import ProductTransferService
from app.models.business.inventory import (
    ProductTransferOrder, ProductTransferOrderDetail, Inventory
)
from datetime import datetime
from decimal import Decimal
from app import db
import uuid
import logging

# 设置蓝图
bp = Blueprint('product_transfer', __name__)
logger = logging.getLogger(__name__)

# ==================== 成品调拨单管理 ====================

@bp.route('/product-transfer-orders', methods=['GET'])
@jwt_required()
@tenant_required
def get_product_transfer_orders():
    """获取成品调拨单列表"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        transfer_number = request.args.get('transfer_number', '')
        status = request.args.get('status', '')
        transfer_type = request.args.get('transfer_type', '')
        from_warehouse_id = request.args.get('from_warehouse_id', '')
        to_warehouse_id = request.args.get('to_warehouse_id', '')
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        
        # 构建查询
        query = ProductTransferOrder.query
        
        if transfer_number:
            query = query.filter(ProductTransferOrder.transfer_number.like(f'%{transfer_number}%'))
        if status:
            query = query.filter(ProductTransferOrder.status == status)
        if transfer_type:
            query = query.filter(ProductTransferOrder.transfer_type == transfer_type)
        if from_warehouse_id:
            query = query.filter(ProductTransferOrder.from_warehouse_id == from_warehouse_id)
        if to_warehouse_id:
            query = query.filter(ProductTransferOrder.to_warehouse_id == to_warehouse_id)
        if start_date:
            query = query.filter(ProductTransferOrder.transfer_date >= start_date)
        if end_date:
            query = query.filter(ProductTransferOrder.transfer_date <= end_date)
        
        # 分页查询
        pagination = query.order_by(ProductTransferOrder.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        orders = []
        for order in pagination.items:
            order_data = order.to_dict()
            orders.append(order_data)
        
        return jsonify({
            'success': True,
            'data': {
                'orders': orders,
                'pagination': {
                    'page': pagination.page,
                    'pages': pagination.pages,
                    'per_page': pagination.per_page,
                    'total': pagination.total
                }
            }
        })
        
    except Exception as e:
        logger.error(f"获取成品调拨单列表失败: {str(e)}")
        return jsonify({'success': False, 'error': '获取调拨单列表失败'}), 500


@bp.route('/product-transfer-orders', methods=['POST'])
@jwt_required()
@tenant_required
def create_product_transfer_order():
    """创建成品调拨单"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        required_fields = ['from_warehouse_id', 'to_warehouse_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'{field} 不能为空'}), 400
        
        # 创建调拨单
        product_transfer_service = ProductTransferService()
        result = product_transfer_service.create_transfer_order(
            data, get_jwt_identity()
        )
        
        if result.get('success'):
            return jsonify(result), 201
        else:
            return jsonify(result), 400
        
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        logger.error(f"创建成品调拨单失败: {str(e)}")
        return jsonify({'success': False, 'error': '创建调拨单失败'}), 500


@bp.route('/product-transfer-orders/<order_id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_product_transfer_order(order_id):
    """获取成品调拨单详情"""
    try:
        order = ProductTransferOrder.query.get(order_id)
        if not order:
            return jsonify({'success': False, 'error': '调拨单不存在'}), 404
        
        return jsonify({
            'success': True,
            'data': order.to_dict()
        })
        
    except Exception as e:
        logger.error(f"获取成品调拨单详情失败: {str(e)}")
        return jsonify({'success': False, 'error': '获取调拨单详情失败'}), 500


@bp.route('/product-transfer-orders/<order_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_product_transfer_order(order_id):
    """更新成品调拨单"""
    try:
        order = ProductTransferOrder.query.get(order_id)
        if not order:
            return jsonify({'success': False, 'error': '调拨单不存在'}), 404
        
        if order.status not in ['draft']:
            return jsonify({'success': False, 'error': '只能修改草稿状态的调拨单'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '请求数据不能为空'}), 400
        
        # 更新字段
        updateable_fields = [
            'transfer_date', 'transfer_type', 'transfer_person_id', 'department_id',
            'transporter', 'transport_method', 'expected_arrival_date', 'notes'
        ]
        
        for field in updateable_fields:
            if field in data:
                if field.endswith('_id') and data[field]:
                    setattr(order, field, uuid.UUID(data[field]))
                elif field == 'transfer_date' and data[field]:
                    setattr(order, field, datetime.fromisoformat(data[field].replace('Z', '+00:00')))
                elif field == 'expected_arrival_date' and data[field]:
                    setattr(order, field, datetime.fromisoformat(data[field].replace('Z', '+00:00')))
                else:
                    setattr(order, field, data[field])
        
        order.updated_by = uuid.UUID(get_jwt_identity())
        
        db.session.commit()

        return jsonify({
            'success': True,
            'data': order.to_dict(),
            'message': '调拨单更新成功'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新成品调拨单失败: {str(e)}")
        return jsonify({'success': False, 'error': '更新调拨单失败'}), 500


@bp.route('/product-transfer-orders/<order_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_product_transfer_order(order_id):
    """删除成品调拨单"""
    try:
        order = ProductTransferOrder.query.get(order_id)
        if not order:
            return jsonify({'success': False, 'error': '调拨单不存在'}), 404
        
        if order.status not in ['draft']:
            return jsonify({'success': False, 'error': '只能删除草稿状态的调拨单'}), 400
        
        db.session.delete(order)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '调拨单删除成功'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"删除成品调拨单失败: {str(e)}")
        return jsonify({'success': False, 'error': '删除调拨单失败'}), 500


# ==================== 成品调拨单明细管理 ====================

@bp.route('/product-transfer-orders/<order_id>/details', methods=['GET'])
@jwt_required()
@tenant_required
def get_product_transfer_order_details(order_id):
    """获取成品调拨单明细列表"""
    try:
        order = ProductTransferOrder.query.get(order_id)
        if not order:
            return jsonify({'success': False, 'error': '调拨单不存在'}), 404
        
        details = ProductTransferOrderDetail.query.filter_by(transfer_order_id=order_id).all()
        
        details_data = []
        for detail in details:
            details_data.append(detail.to_dict())
        
        return jsonify({
            'success': True,
            'data': details_data
        })
        
    except Exception as e:
        logger.error(f"获取成品调拨单明细失败: {str(e)}")
        return jsonify({'success': False, 'error': '获取调拨明细失败'}), 500


@bp.route('/product-transfer-orders/<order_id>/details', methods=['POST'])
@jwt_required()
@tenant_required
def add_product_transfer_order_detail(order_id):
    """添加成品调拨单明细"""
    try:
        order = ProductTransferOrder.query.get(order_id)
        if not order:
            return jsonify({'success': False, 'error': '调拨单不存在'}), 404
        
        if order.status not in ['draft']:
            return jsonify({'success': False, 'error': '只能为草稿状态的调拨单添加明细'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        if not data.get('product_id'):
            return jsonify({'success': False, 'error': '产品ID不能为空'}), 400
        if not data.get('transfer_quantity'):
            return jsonify({'success': False, 'error': '调拨数量不能为空'}), 400
        
        # 使用服务添加明细
        product_transfer_service = ProductTransferService()
        result = product_transfer_service.add_transfer_order_detail(
            order_id, data, get_jwt_identity()
        )
        
        if result.get('success'):
            return jsonify(result), 201
        else:
            return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"添加成品调拨单明细失败: {str(e)}")
        return jsonify({'success': False, 'error': '添加调拨明细失败'}), 500


@bp.route('/product-transfer-orders/<order_id>/details/<detail_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_product_transfer_order_detail(order_id, detail_id):
    """更新成品调拨单明细"""
    try:
        detail = ProductTransferOrderDetail.query.get(detail_id)
        if not detail:
            return jsonify({'success': False, 'error': '调拨明细不存在'}), 404
        
        order = detail.transfer_order
        if order.status not in ['draft']:
            return jsonify({'success': False, 'error': '只能修改草稿状态的调拨单明细'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '请求数据不能为空'}), 400
        
        # 使用服务更新明细
        product_transfer_service = ProductTransferService()
        result = product_transfer_service.update_transfer_order_detail(
            detail_id, data, get_jwt_identity()
        )
        
        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"更新成品调拨单明细失败: {str(e)}")
        return jsonify({'success': False, 'error': '更新调拨明细失败'}), 500


@bp.route('/product-transfer-orders/<order_id>/details/<detail_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_product_transfer_order_detail(order_id, detail_id):
    """删除成品调拨单明细"""
    try:
        detail = ProductTransferOrderDetail.query.get(detail_id)
        if not detail:
            return jsonify({'success': False, 'error': '调拨明细不存在'}), 404
        
        order = detail.transfer_order
        if order.status not in ['draft']:
            return jsonify({'success': False, 'error': '只能删除草稿状态的调拨单明细'}), 400
        
        db.session.delete(detail)
        db.session.commit()
        
        # 重新计算调拨单统计信息
        order.calculate_totals()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '调拨明细删除成功'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"删除成品调拨单明细失败: {str(e)}")
        return jsonify({'success': False, 'error': '删除调拨明细失败'}), 500


# ==================== 成品调拨单流程管理 ====================

@bp.route('/product-transfer-orders/<order_id>/confirm', methods=['POST'])
@jwt_required()
@tenant_required
def confirm_product_transfer_order(order_id):
    """确认成品调拨单"""
    try:
        product_transfer_service = ProductTransferService()
        result = product_transfer_service.confirm_transfer_order(order_id, get_jwt_identity())
        
        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"确认成品调拨单失败: {str(e)}")
        return jsonify({'success': False, 'error': '确认调拨单失败'}), 500


@bp.route('/product-transfer-orders/<order_id>/execute', methods=['POST'])
@jwt_required()
@tenant_required
def execute_product_transfer_order(order_id):
    """执行成品调拨单（出库）"""
    try:
        product_transfer_service = ProductTransferService()
        result = product_transfer_service.execute_transfer_order(order_id, get_jwt_identity())
        
        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"执行成品调拨单失败: {str(e)}")
        return jsonify({'success': False, 'error': '执行调拨单失败'}), 500


@bp.route('/product-transfer-orders/<order_id>/receive', methods=['POST'])
@jwt_required()
@tenant_required
def receive_product_transfer_order(order_id):
    """接收成品调拨单（入库）"""
    try:
        product_transfer_service = ProductTransferService()
        result = product_transfer_service.receive_transfer_order(order_id, get_jwt_identity())
        
        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"接收成品调拨单失败: {str(e)}")
        return jsonify({'success': False, 'error': '接收调拨单失败'}), 500


@bp.route('/product-transfer-orders/<order_id>/cancel', methods=['POST'])
@jwt_required()
@tenant_required
def cancel_product_transfer_order(order_id):
    """取消成品调拨单"""
    try:
        data = request.get_json()
        cancel_reason = data.get('cancel_reason', '') if data else ''
        
        product_transfer_service = ProductTransferService()
        result = product_transfer_service.cancel_transfer_order(order_id, get_jwt_identity(), cancel_reason)
        
        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"取消成品调拨单失败: {str(e)}")
        return jsonify({'success': False, 'error': '取消调拨单失败'}), 500


# ==================== 辅助功能API ====================

@bp.route('/warehouses/<warehouse_id>/transfer-products', methods=['GET'])
@jwt_required()
@tenant_required
def get_warehouse_transfer_products(warehouse_id):
    """获取仓库可调拨成品库存"""
    try:
        product_transfer_service = ProductTransferService()
        products = product_transfer_service.get_warehouse_product_inventory(warehouse_id)
        
        return jsonify({
            'success': True,
            'data': products
        })

    except Exception as e:
        logger.error(f"获取仓库可调拨成品失败: {str(e)}")
        return jsonify({'success': False, 'error': '获取可调拨成品失败'}), 500 