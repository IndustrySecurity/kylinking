# -*- coding: utf-8 -*-
"""
库存管理API路由
"""

from flask import Blueprint, request, jsonify, current_app, g
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from .routes import tenant_required
from app.services.inventory_service import InventoryService
from app.services.outbound_order_service import OutboundOrderService
from app.services.material_inbound_service import MaterialInboundService
from app.services.material_outbound_service import MaterialOutboundService
from app.models.user import User
from app.extensions import db
from decimal import Decimal
from datetime import datetime
import uuid
from app.models.business.inventory import (
    MaterialInboundOrder, MaterialInboundOrderDetail, 
    MaterialOutboundOrder, MaterialOutboundOrderDetail,
    Inventory, InventoryTransaction
)

bp = Blueprint('inventory', __name__)


@bp.route('/inventories', methods=['GET'])
@jwt_required()
def get_inventories():
    """获取库存列表"""
    try:
        # 获取查询参数
        warehouse_id = request.args.get('warehouse_id')
        inventory_status = request.args.get('inventory_status')
        quality_status = request.args.get('quality_status')
        below_safety_stock = request.args.get('below_safety_stock', 'false').lower() == 'true'
        expired_only = request.args.get('expired_only', 'false').lower() == 'true'
        page = int(request.args.get('page', 1))
        page_size = min(int(request.args.get('page_size', 20)), 100)
        
        # 获取当前用户信息
        current_user_id = get_jwt_identity()
        
        # 获取库存列表
        service = InventoryService(db.session)
        result = service.get_inventory_list(
            warehouse_id=warehouse_id,
            inventory_status=inventory_status,
            quality_status=quality_status,
            below_safety_stock=below_safety_stock,
            expired_only=expired_only,
            page=page,
            page_size=page_size
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/inventories/<inventory_id>', methods=['GET'])
@jwt_required()
def get_inventory(inventory_id):
    """获取库存详情"""
    try:
        service = InventoryService(db.session)
        inventory = service.get_inventory_by_id(inventory_id)
        
        if not inventory:
            return jsonify({'error': '库存记录不存在'}), 404
        
        return jsonify({
            'success': True,
            'data': inventory.to_dict() if hasattr(inventory, 'to_dict') else inventory
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/inventories', methods=['POST'])
@jwt_required()
def create_inventory():
    """创建库存记录"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        service = InventoryService(db.session)
        inventory = service.create_inventory(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': inventory.to_dict() if hasattr(inventory, 'to_dict') else inventory,
            'message': '库存记录创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/inventories/<inventory_id>', methods=['PUT'])
@jwt_required()
def update_inventory(inventory_id):
    """更新库存记录"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        service = InventoryService(db.session)
        inventory = service.update_inventory_quantity(inventory_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': inventory.to_dict() if hasattr(inventory, 'to_dict') else inventory,
            'message': '库存记录更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/inventory-transactions', methods=['GET'])
@jwt_required()
def get_inventory_transactions():
    """获取库存流水列表"""
    try:
        # 获取查询参数
        inventory_id = request.args.get('inventory_id')
        warehouse_id = request.args.get('warehouse_id')
        transaction_type = request.args.get('transaction_type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        page = int(request.args.get('page', 1))
        page_size = min(int(request.args.get('page_size', 20)), 100)
        
        # 日期转换
        if start_date:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        service = InventoryService(db.session)
        result = service.get_inventory_transactions(
            inventory_id=inventory_id,
            warehouse_id=warehouse_id,
            transaction_type=transaction_type,
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=page_size
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/inventories/reserve', methods=['POST'])
@jwt_required()
def reserve_inventory():
    """预留库存"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        inventory_id = data.get('inventory_id')
        quantity = data.get('quantity')
        reason = data.get('reason')
        
        if not inventory_id or not quantity:
            return jsonify({'error': '库存ID和数量不能为空'}), 400
        
        service = InventoryService(db.session)
        result = service.reserve_inventory(inventory_id, Decimal(str(quantity)), reason, current_user_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '库存预留成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/inventories/unreserve', methods=['POST'])
@jwt_required()
def unreserve_inventory():
    """取消预留库存"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        inventory_id = data.get('inventory_id')
        quantity = data.get('quantity')
        reason = data.get('reason')
        
        if not inventory_id or not quantity:
            return jsonify({'error': '库存ID和数量不能为空'}), 400
        
        service = InventoryService(db.session)
        result = service.release_reserved_inventory(inventory_id, Decimal(str(quantity)), reason, current_user_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '取消预留成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ================ 入库单相关API ================

@bp.route('/inbound-orders', methods=['GET'])
@jwt_required()
def get_inbound_orders():
    """获取入库单列表"""
    try:
        # 获取查询参数
        warehouse_id = request.args.get('warehouse_id')
        order_type = request.args.get('order_type')
        status = request.args.get('status')
        approval_status = request.args.get('approval_status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        search = request.args.get('search')
        page = int(request.args.get('page', 1))
        page_size = min(int(request.args.get('page_size', 20)), 100)
        
        # 日期转换
        if start_date:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        service = InventoryService(db.session)
        result = service.get_inbound_order_list(
            warehouse_id=warehouse_id,
            order_type=order_type,
            status=status,
            approval_status=approval_status,
            start_date=start_date,
            end_date=end_date,
            search=search,
            page=page,
            page_size=page_size
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/inbound-orders/<order_id>', methods=['GET'])
@jwt_required()
def get_inbound_order(order_id):
    """获取入库单详情"""
    try:
        service = InventoryService(db.session)
        order = service.get_inbound_order_by_id(order_id)
        
        if not order:
            return jsonify({'error': '入库单不存在'}), 404
        
        return jsonify({
            'success': True,
            'data': order.to_dict() if hasattr(order, 'to_dict') else order
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/inbound-orders', methods=['POST'])
@jwt_required()
def create_inbound_order():
    """创建入库单"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        if not data.get('warehouse_id'):
            return jsonify({'error': '仓库ID不能为空'}), 400
        
        service = InventoryService(db.session)
        order = service.create_inbound_order(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': order.to_dict() if hasattr(order, 'to_dict') else order,
            'message': '入库单创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/inbound-orders/<order_id>', methods=['PUT'])
@jwt_required()
def update_inbound_order(order_id):
    """更新入库单"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        service = InventoryService(db.session)
        # 修复参数顺序：order_id, updated_by, **update_data
        order = service.update_inbound_order(order_id, current_user_id, **data)
        
        return jsonify({
            'success': True,
            'data': order.to_dict() if hasattr(order, 'to_dict') else order,
            'message': '入库单更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/inbound-orders/<order_id>/details', methods=['GET'])
@jwt_required()
def get_inbound_order_details(order_id):
    """获取入库单明细列表"""
    try:
        service = InventoryService(db.session)
        
        # 首先检查入库单是否存在
        order = service.get_inbound_order_by_id(order_id)
        if not order:
            return jsonify({
                'success': False,
                'error': f'入库单不存在: {order_id}',
                'data': []
            }), 404
        
        # 获取明细
        details = service.get_inbound_order_details(order_id)
        
        return jsonify({
            'success': True,
            'data': details,
            'message': f'成功获取 {len(details)} 条明细记录'
        })
        
    except Exception as e:
        current_app.logger.error(f"获取入库单明细失败 - order_id: {order_id}, error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'获取入库单明细失败: {str(e)}',
            'data': []
        }), 500


@bp.route('/inbound-orders/<order_id>/details', methods=['POST'])
@jwt_required()
def add_inbound_order_detail(order_id):
    """添加入库单明细"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        if not data.get('inbound_quantity'):
            return jsonify({'error': '入库数量不能为空'}), 400
        
        service = InventoryService(db.session)
        detail = service.add_inbound_order_detail(
            order_id=order_id,
            inbound_quantity=Decimal(str(data['inbound_quantity'])),
            unit=data.get('unit', '个'),
            created_by=current_user_id,
            product_id=data.get('product_id'),
            product_name=data.get('product_name'),
            **{k: v for k, v in data.items() if k not in ['inbound_quantity', 'unit', 'product_id', 'product_name']}
        )
        
        return jsonify({
            'success': True,
            'data': detail.to_dict() if hasattr(detail, 'to_dict') else detail,
            'message': '明细添加成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/inbound-orders/<order_id>/details/<detail_id>', methods=['PUT'])
@jwt_required()
def update_inbound_order_detail(order_id, detail_id):
    """更新入库单明细"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        service = InventoryService(db.session)
        # 修复参数顺序：detail_id, updated_by, **update_data
        detail = service.update_inbound_order_detail(detail_id, current_user_id, **data)
        
        return jsonify({
            'success': True,
            'data': detail.to_dict() if hasattr(detail, 'to_dict') else detail,
            'message': '明细更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/inbound-orders/<order_id>/details/<detail_id>', methods=['DELETE'])
@jwt_required()
def delete_inbound_order_detail(order_id, detail_id):
    """删除入库单明细"""
    try:
        service = InventoryService(db.session)
        service.delete_inbound_order_detail(detail_id)
        
        return jsonify({
            'success': True,
            'message': '明细删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/inbound-orders/<order_id>/approve', methods=['POST'])
@jwt_required()
def approve_inbound_order(order_id):
    """审核入库单"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        approval_status = data.get('approval_status') if data else request.args.get('approval_status')
        approval_notes = data.get('approval_notes') if data else request.args.get('approval_notes')
        
        if not approval_status or approval_status not in ['approved', 'rejected']:
            return jsonify({'error': '审核状态必须是approved或rejected'}), 400
        
        service = InventoryService(db.session)
        # 修复参数顺序：order_id, approved_by, approval_status
        order = service.approve_inbound_order(order_id, current_user_id, approval_status)
        
        return jsonify({
            'success': True,
            'data': order.to_dict() if hasattr(order, 'to_dict') else order,
            'message': '审核成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/inbound-orders/<order_id>/execute', methods=['POST'])
@jwt_required()
def execute_inbound_order(order_id):
    """执行入库单"""
    try:
        current_user_id = get_jwt_identity()
        auto_create_inventory = request.args.get('auto_create_inventory', 'true').lower() == 'true'
        
        service = InventoryService(db.session)
        # 修复参数顺序：order_id, executed_by, auto_create_inventory
        transactions = service.execute_inbound_order(order_id, current_user_id, auto_create_inventory)
        
        return jsonify({
            'success': True,
            'data': {'transactions': len(transactions)},
            'message': '入库单执行成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/inbound-orders/<order_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_inbound_order(order_id):
    """取消入库单"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        cancel_reason = data.get('cancel_reason') if data else request.args.get('cancel_reason')
        
        service = InventoryService(db.session)
        # 修复参数顺序：order_id, cancelled_by, cancel_reason
        order = service.cancel_inbound_order(order_id, current_user_id, cancel_reason)
        
        return jsonify({
            'success': True,
            'data': order.to_dict() if hasattr(order, 'to_dict') else order,
            'message': '入库单已取消'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ================ 报表相关API ================

@bp.route('/reports/low-stock', methods=['GET'])
@jwt_required()
def get_low_stock_alerts():
    """低库存预警报表"""
    try:
        warehouse_id = request.args.get('warehouse_id')
        
        service = InventoryService(db.session)
        result = service.get_low_stock_alerts(warehouse_id)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/reports/inventory-statistics', methods=['GET'])
@jwt_required()
def get_inventory_statistics():
    """库存统计报表"""
    try:
        warehouse_id = request.args.get('warehouse_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 日期转换
        if start_date:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        service = InventoryService(db.session)
        result = service.get_inventory_statistics(warehouse_id, start_date, end_date)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 出库单相关API
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
        from app.services.outbound_order_service import get_outbound_order_service
        service = get_outbound_order_service()
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
        return jsonify({'error': str(e)}), 500


@bp.route('/outbound-orders/<order_id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_outbound_order(order_id):
    """获取出库单详情"""
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        from app.services.outbound_order_service import get_outbound_order_service
        service = get_outbound_order_service()
        order = service.get_outbound_order_by_id(order_id)
        
        return jsonify({
            'success': True,
            'data': order
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
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
        
        from app.services.outbound_order_service import get_outbound_order_service
        service = get_outbound_order_service()
        order = service.create_outbound_order(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': order,
            'message': '出库单创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
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
        
        from app.services.outbound_order_service import get_outbound_order_service
        service = get_outbound_order_service()
        order = service.update_outbound_order(order_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': order,
            'message': '出库单更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/outbound-orders/<order_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_outbound_order(order_id):
    """删除出库单"""
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        from app.services.outbound_order_service import get_outbound_order_service
        service = get_outbound_order_service()
        service.delete_outbound_order(order_id)
        
        return jsonify({
            'success': True,
            'message': '出库单删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
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
        
        from app.services.outbound_order_service import get_outbound_order_service
        service = get_outbound_order_service()
        order = service.approve_outbound_order(order_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': order,
            'message': '出库单审核成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
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
        
        from app.services.outbound_order_service import get_outbound_order_service
        service = get_outbound_order_service()
        order = service.execute_outbound_order(order_id, current_user_id)
        
        return jsonify({
            'success': True,
            'data': order,
            'message': '出库单执行成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
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
        
        from app.services.outbound_order_service import get_outbound_order_service
        service = get_outbound_order_service()
        order = service.cancel_outbound_order(order_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': order,
            'message': '出库单取消成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 出库单明细相关API
@bp.route('/outbound-orders/<order_id>/details', methods=['GET'])
@jwt_required()
@tenant_required
def get_outbound_order_details(order_id):
    """获取出库单明细列表"""
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        from app.services.outbound_order_service import get_outbound_order_service
        service = get_outbound_order_service()
        details = service.get_outbound_order_details(order_id)
        
        return jsonify({
            'success': True,
            'data': details
        })
        
    except Exception as e:
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
        
        from app.services.outbound_order_service import get_outbound_order_service
        service = get_outbound_order_service()  
        detail = service.create_outbound_order_detail(order_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': detail,
            'message': '出库单明细创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
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
        
        from app.services.outbound_order_service import get_outbound_order_service
        service = get_outbound_order_service()
        detail = service.update_outbound_order_detail(order_id, detail_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': detail,
            'message': '出库单明细更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/outbound-orders/<order_id>/details/<detail_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_outbound_order_detail(order_id, detail_id):
    """删除出库单明细"""
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        from app.services.outbound_order_service import get_outbound_order_service
        service = get_outbound_order_service()
        service.delete_outbound_order_detail(order_id, detail_id)
        
        return jsonify({
            'success': True,
            'message': '出库单明细删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
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
        
        from app.services.outbound_order_service import get_outbound_order_service
        service = get_outbound_order_service()
        
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
        return jsonify({'error': str(e)}), 500


# 材料入库单相关API
@bp.route('/material-inbound-orders', methods=['GET'])
@jwt_required()
def get_material_inbound_orders():
    """获取材料入库单列表"""
    try:
        # 获取查询参数
        warehouse_id = request.args.get('warehouse_id')
        order_type = request.args.get('order_type')
        status = request.args.get('status')
        approval_status = request.args.get('approval_status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        search = request.args.get('search')
        page = int(request.args.get('page', 1))
        page_size = min(int(request.args.get('page_size', 20)), 100)
        
        # 日期转换
        if start_date:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        # 使用MaterialInboundService
        service = MaterialInboundService(db.session)
        result = service.get_material_inbound_order_list(
            warehouse_id=warehouse_id,
            order_type=order_type,
            status=status,
            approval_status=approval_status,
            start_date=start_date,
            end_date=end_date,
            search=search,
            page=page,
            page_size=page_size
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/material-inbound-orders', methods=['POST'])
@jwt_required()
def create_material_inbound_order():
    """创建材料入库单"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        if not data.get('warehouse_id'):
            return jsonify({'error': '仓库ID不能为空'}), 400
        
        service = MaterialInboundService(db.session)
        order = service.create_material_inbound_order(data, current_user_id)
        
        # 查询部门名称（如果department是UUID）
        department_name = order.department
        if order.department:
            try:
                import uuid
                dept_uuid = uuid.UUID(order.department)
                from app.models.organization import Department
                dept = db.session.query(Department).filter(Department.id == dept_uuid).first()
                if dept:
                    department_name = dept.department_name
            except (ValueError, TypeError):
                # 如果不是UUID，保持原值
                pass
        
        # 为了避免SQLAlchemy懒加载问题，手动构建返回数据
        order_data = {
            'id': str(order.id),
            'order_number': order.order_number,
            'order_date': order.order_date.isoformat() if order.order_date else None,
            'order_type': order.order_type,
            'warehouse_id': str(order.warehouse_id) if order.warehouse_id else None,
            'warehouse_name': order.warehouse_name,
            'inbound_person': order.inbound_person,
            'department': department_name,
            'status': order.status,
            'approval_status': order.approval_status,
            'supplier_name': order.supplier_name,
            'notes': order.notes,
            'created_at': order.created_at.isoformat() if order.created_at else None
        }
        
        return jsonify({
            'success': True,
            'data': order_data,
            'message': '入库单创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/material-inbound-orders/<order_id>', methods=['GET'])
@jwt_required()
def get_material_inbound_order(order_id):
    """获取材料入库单详情"""
    try:
        service = MaterialInboundService(db.session)
        order = service.get_material_inbound_order_by_id(order_id)
        
        if not order:
            return jsonify({'error': '入库单不存在'}), 404
        
        return jsonify({
            'success': True,
            'data': order.to_dict() if hasattr(order, 'to_dict') else order
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/material-inbound-orders/<order_id>/details', methods=['GET'])
@jwt_required()
def get_material_inbound_order_details(order_id):
    """获取材料入库单明细列表"""
    try:
        service = MaterialInboundService(db.session)
        
        # 首先检查入库单是否存在
        order = service.get_material_inbound_order_by_id(order_id)
        if not order:
            return jsonify({
                'success': False,
                'error': f'入库单不存在: {order_id}',
                'data': []
            }), 404
        
        # 获取明细
        details = service.get_material_inbound_order_details(order_id)
        
        return jsonify({
            'success': True,
            'data': details,
            'message': f'成功获取 {len(details)} 条明细记录'
        })
        
    except Exception as e:
        current_app.logger.error(f"获取材料入库单明细失败 - order_id: {order_id}, error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'获取入库单明细失败: {str(e)}',
            'data': []
        }), 500


@bp.route('/material-inbound-orders/<order_id>/details', methods=['POST'])
@jwt_required()
def add_material_inbound_order_detail(order_id):
    """添加材料入库单明细"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        if not data.get('inbound_quantity'):
            return jsonify({'error': '入库数量不能为空'}), 400
        
        service = MaterialInboundService(db.session)
        detail = service.add_material_inbound_order_detail(
            order_id=order_id,
            inbound_quantity=Decimal(str(data['inbound_quantity'])),
            unit=data.get('unit', '个'),
            created_by=current_user_id,
            material_id=data.get('material_id'),
            material_name=data.get('material_name'),
            **{k: v for k, v in data.items() if k not in ['inbound_quantity', 'unit', 'material_id', 'material_name']}
        )
        
        return jsonify({
            'success': True,
            'data': detail.to_dict() if hasattr(detail, 'to_dict') else detail,
            'message': '明细添加成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/material-inbound-orders/<order_id>/details/<detail_id>', methods=['PUT'])
@jwt_required()
def update_material_inbound_order_detail(order_id, detail_id):
    """更新材料入库单明细"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        service = MaterialInboundService(db.session)
        detail = service.update_material_inbound_order_detail(
            detail_id=detail_id,
            updated_by=current_user_id,
            **data
        )
        
        if not detail:
            return jsonify({'error': '明细记录不存在'}), 404
        
        return jsonify({
            'success': True,
            'data': detail.to_dict() if hasattr(detail, 'to_dict') else detail,
            'message': '明细更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/material-inbound-orders/<order_id>/details/<detail_id>', methods=['DELETE'])
@jwt_required()
def delete_material_inbound_order_detail(order_id, detail_id):
    """删除材料入库单明细"""
    try:
        service = MaterialInboundService(db.session)
        success = service.delete_material_inbound_order_detail(detail_id)
        
        if not success:
            return jsonify({'error': '明细记录不存在'}), 404
        
        return jsonify({
            'success': True,
            'message': '明细删除成功'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/material-inbound-orders/<order_id>', methods=['PUT'])
@jwt_required()
def update_material_inbound_order(order_id):
    """更新材料入库单"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        service = MaterialInboundService(db.session)
        # 修复参数顺序：order_id, updated_by, **update_data
        order = service.update_material_inbound_order(order_id, current_user_id, **data)
        
        return jsonify({
            'success': True,
            'data': order.to_dict() if hasattr(order, 'to_dict') else order,
            'message': '入库单更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/material-inbound-orders/<order_id>', methods=['DELETE'])
@jwt_required()
def delete_material_inbound_order(order_id):
    """删除材料入库单"""
    try:
        service = MaterialInboundService(db.session)
        order = service.get_material_inbound_order_by_id(order_id)
        
        if not order:
            return jsonify({'error': '入库单不存在'}), 404
        
        if order.status not in ['draft', 'cancelled']:
            return jsonify({'error': '只能删除草稿或已取消状态的入库单'}), 400
        
        # 删除明细和主表
        # 这里应该在service中实现，暂时直接操作
        MaterialInboundOrderDetail.query.filter_by(material_inbound_order_id=order_id).delete()
        db.session.delete(order)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '入库单删除成功'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/material-inbound-orders/<order_id>/approve', methods=['POST'])
@jwt_required()
def approve_material_inbound_order(order_id):
    """审核材料入库单"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        approval_status = data.get('approval_status', 'approved')
        
        service = MaterialInboundService(db.session)
        order = service.approve_material_inbound_order(order_id, current_user_id, approval_status)
        
        return jsonify({
            'success': True,
            'data': order.to_dict() if hasattr(order, 'to_dict') else order,
            'message': '入库单审核成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/material-inbound-orders/<order_id>/execute', methods=['POST'])
@jwt_required()
def execute_material_inbound_order(order_id):
    """执行材料入库单"""
    try:
        current_user_id = get_jwt_identity()
        current_app.logger.info(f"开始执行材料入库单: {order_id}, 操作人: {current_user_id}")
        
        service = MaterialInboundService(db.session)
        transactions = service.execute_material_inbound_order(order_id, current_user_id)
        
        current_app.logger.info(f"执行完成，创建了 {len(transactions)} 个库存事务")
        
        return jsonify({
            'success': True,
            'data': {
                'transaction_count': len(transactions),
                'transactions': [t.to_dict() for t in transactions]
            },
            'message': '入库单执行成功'
        })
        
    except ValueError as e:
        current_app.logger.error(f"执行材料入库单失败 - ValueError: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"执行材料入库单失败 - Exception: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/material-inbound-orders/<order_id>/submit', methods=['POST'])
@jwt_required()
def submit_material_inbound_order(order_id):
    """提交材料入库单"""
    try:
        current_user_id = get_jwt_identity()
        
        service = MaterialInboundService(db.session)
        order = service.submit_material_inbound_order(order_id, current_user_id)
        
        return jsonify({
            'success': True,
            'data': order.to_dict() if hasattr(order, 'to_dict') else order,
            'message': '入库单提交成功'
        })
        
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/material-inbound-orders/<order_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_material_inbound_order(order_id):
    """取消材料入库单"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        cancel_reason = data.get('cancel_reason', '')
        
        service = MaterialInboundService(db.session)
        order = service.cancel_material_inbound_order(order_id, current_user_id, cancel_reason)
        
        return jsonify({
            'success': True,
            'data': order.to_dict() if hasattr(order, 'to_dict') else order,
            'message': '入库单取消成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 获取仓库列表（供下拉选择使用）
@bp.route('/warehouses', methods=['GET'])
@jwt_required()
def get_warehouses():
    """获取仓库列表"""
    try:
        # 获取查询参数
        warehouse_type = request.args.get('warehouse_type', '')
        
        # 使用仓库服务获取真实的仓库数据
        try:
            from app.services.basic_data_service import WarehouseService
            warehouses_data = WarehouseService.get_warehouse_options(warehouse_type)
            
            # 过滤材料仓库
            if warehouse_type == 'material' or not warehouse_type:
                # 如果没有指定类型，默认返回材料仓库
                warehouses = [w for w in warehouses_data if w.get('warehouse_type') == '材料仓库' or '材料' in w.get('label', '')]
            else:
                warehouses = warehouses_data
                
        except Exception as e:
            # 如果服务调用失败，使用模拟数据
            current_app.logger.warning(f"获取仓库数据失败，使用模拟数据: {e}")
            warehouses = [
                {'value': '1', 'label': '原材料一库', 'code': 'CL001', 'warehouse_type': '材料仓库'},
                {'value': '2', 'label': '原材料二库', 'code': 'CL002', 'warehouse_type': '材料仓库'},
                {'value': '3', 'label': '原材料三库', 'code': 'CL003', 'warehouse_type': '材料仓库'},
                {'value': '4', 'label': '材料仓', 'code': 'CL004', 'warehouse_type': '材料仓库'},
            ]

        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': warehouses
        })

    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取失败: {str(e)}'}), 500


# 获取材料列表（供下拉选择使用）
@bp.route('/materials', methods=['GET'])
@jwt_required()
def get_materials():
    """获取材料列表"""
    try:
        search = request.args.get('search', '')
        
        materials = [
            {
                'id': 1,
                'name': 'PE塑料颗粒',
                'code': 'MAT001',
                'specification': '规格A',
                'unit': '吨',
                'category': '塑料原料'
            },
            {
                'id': 2,
                'name': 'PP塑料颗粒',
                'code': 'MAT002',
                'specification': '规格B',
                'unit': '吨',
                'category': '塑料原料'
            },
            {
                'id': 3,
                'name': '聚乙烯薄膜',
                'code': 'MAT003',
                'specification': '0.05mm',
                'unit': '米',
                'category': '薄膜材料'
            },
            {
                'id': 4,
                'name': '包装袋',
                'code': 'MAT004',
                'specification': '50kg装',
                'unit': '个',
                'category': '包装材料'
            },
        ]

        # 简单的搜索过滤
        if search:
            materials = [m for m in materials if search.lower() in m['name'].lower() or search.lower() in m['code'].lower()]

        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': materials
        })

    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取失败: {str(e)}'}), 500


# 获取供应商列表（供下拉选择使用）
@bp.route('/suppliers', methods=['GET'])
@jwt_required()
def get_suppliers():
    """获取供应商列表"""
    try:
        suppliers = [
            {'id': 1, 'name': '供应商A', 'code': 'SUP001'},
            {'id': 2, 'name': '供应商B', 'code': 'SUP002'},
            {'id': 3, 'name': '供应商C', 'code': 'SUP003'},
        ]

        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': suppliers
        })

    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取失败: {str(e)}'}), 500


@bp.route('/departments/options', methods=['GET'])
@jwt_required()
def get_department_options():
    """获取部门选项"""
    try:
        from app.services.basic_data_service import DepartmentService
        options = DepartmentService.get_department_options()
        
        return jsonify({
            'success': True,
            'data': options
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== 材料出库单管理 ====================

@bp.route('/material-outbound-orders', methods=['GET'])
@jwt_required()
def get_material_outbound_orders():
    """获取材料出库单列表"""
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        page_size = min(int(request.args.get('page_size', 20)), 100)
        search = request.args.get('search', '')
        status = request.args.get('status', '')
        approval_status = request.args.get('approval_status', '')
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        warehouse_id = request.args.get('warehouse_id', '')

        # 日期转换
        start_date_obj = None
        end_date_obj = None
        if start_date:
            start_date_obj = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_date_obj = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        # 使用MaterialOutboundService
        service = MaterialOutboundService(db.session)
        result = service.get_material_outbound_order_list(
            warehouse_id=warehouse_id,
            order_type=request.args.get('order_type'),
            status=status,
            approval_status=approval_status,
            start_date=start_date_obj,
            end_date=end_date_obj,
            search=search,
            page=page,
            page_size=page_size
        )

        return jsonify({
            'success': True,
            'data': result
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/material-outbound-orders', methods=['POST'])
@jwt_required()
def create_material_outbound_order():
    """创建材料出库单"""
    try:
        data = request.get_json()
        
        # 验证必需字段 - 修复：warehouse_name不是必须的，可以从warehouse_id获取
        required_fields = ['warehouse_id', 'order_type', 'outbound_person', 'department']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'code': 400, 'message': f'缺少必需字段: {field}'}), 400

        current_user = get_jwt_identity()
        
        # 如果没有warehouse_name，根据warehouse_id获取
        if not data.get('warehouse_name') and data.get('warehouse_id'):
            try:
                # 从仓库API获取仓库名称
                warehouses_response = get_warehouses()
                if warehouses_response[1] == 200:  # 检查状态码
                    warehouses_data = warehouses_response[0].get_json()
                    if warehouses_data.get('code') == 200:
                        warehouses = warehouses_data.get('data', [])
                        warehouse = next((w for w in warehouses if str(w.get('id')) == str(data.get('warehouse_id'))), None)
                        if warehouse:
                            data['warehouse_name'] = warehouse.get('warehouse_name', f"仓库{data.get('warehouse_id')}")
            except Exception as e:
                current_app.logger.warning(f"获取仓库名称失败: {e}")
                data['warehouse_name'] = f"仓库{data.get('warehouse_id')}"
        
        # 处理部门名称映射
        department_id = data.get('department')
        department_name = None
        if department_id:
            try:
                # 尝试获取部门名称
                dept_response = get_department_options()
                if dept_response[1] == 200:
                    dept_data = dept_response[0].get_json()
                    if dept_data.get('success'):
                        departments = dept_data.get('data', [])
                        dept = next((d for d in departments if str(d.get('value')) == str(department_id)), None)
                        if dept:
                            department_name = dept.get('label', dept.get('name', department_id))
                        else:
                            department_name = department_id
                    else:
                        department_name = department_id
                else:
                    department_name = department_id
            except Exception as e:
                current_app.logger.warning(f"获取部门信息失败: {e}")
                # 如果获取失败，检查是否已经是部门名称
                department_name = department_id
        
        # 更新数据中的部门信息
        data['department'] = department_name or data.get('department')
        
        # 使用新的服务类创建出库单
        service = MaterialOutboundService(db.session)
        order = service.create_material_outbound_order(data, current_user)
        
        # 转换为前端期望的格式
        response_data = order.to_dict()
        response_data['audit_status'] = response_data.pop('approval_status', 'pending')
        response_data['remarks'] = response_data.pop('remark', '')

        return jsonify({
            'code': 200,
            'message': '创建成功',
            'data': response_data
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'创建失败: {str(e)}'}), 500


@bp.route('/material-outbound-orders/<order_id>', methods=['GET'])
@jwt_required()
def get_material_outbound_order(order_id):
    """获取材料出库单详情"""
    try:
        # 使用原生模型查询，不依赖service
        order = MaterialOutboundOrder.query.get(order_id)
        
        if not order:
            return jsonify({'code': 404, 'message': '出库单不存在'}), 404

        # 获取明细
        details = MaterialOutboundOrderDetail.query.filter_by(material_outbound_order_id=order_id).all()
        
        order_dict = order.to_dict()
        order_dict['details'] = [detail.to_dict() for detail in details]
        order_dict['audit_status'] = order_dict.pop('approval_status', 'pending')

        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': order_dict
        })

    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取失败: {str(e)}'}), 500


@bp.route('/material-outbound-orders/<order_id>', methods=['PUT'])
@jwt_required()
def update_material_outbound_order(order_id):
    """更新材料出库单"""
    try:
        data = request.get_json()
        current_user = get_jwt_identity()
        
        order = MaterialOutboundOrder.query.get(order_id)
        if not order:
            return jsonify({'code': 404, 'message': '出库单不存在'}), 404

        if order.status != 'draft':
            return jsonify({'code': 400, 'message': '只能修改草稿状态的出库单'}), 400

        # 更新主表字段
        updateable_fields = [
            'order_date', 'order_type', 'warehouse_id', 'warehouse_name',
            'outbound_person', 'department', 'requisition_department', 
            'requisition_person', 'use_purpose', 'remarks'
        ]
        
        for field in updateable_fields:
            if field in data:
                setattr(order, field, data[field])

        # 更新明细
        if 'details' in data:
            # 删除原有明细
            MaterialOutboundOrderDetail.query.filter_by(
                material_outbound_order_id=order_id
            ).delete()
            
            # 添加新明细
            for detail_data in data['details']:
                detail = MaterialOutboundOrderDetail(
                    material_outbound_order_id=order_id,
                    **detail_data
                )
                db.session.add(detail)

        order.updated_by = current_user
        order.updated_at = datetime.now()
        
        db.session.commit()
        
        # 转换为前端期望的格式
        response_data = order.to_dict()
        response_data['audit_status'] = response_data.pop('approval_status', 'pending')

        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': response_data
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'更新失败: {str(e)}'}), 500


@bp.route('/material-outbound-orders/<order_id>', methods=['DELETE'])
@jwt_required()
def delete_material_outbound_order(order_id):
    """删除材料出库单"""
    try:
        order = MaterialOutboundOrder.query.get(order_id)
        if not order:
            return jsonify({'code': 404, 'message': '出库单不存在'}), 404
        
        if order.status != 'draft':
            return jsonify({'code': 400, 'message': '只能删除草稿状态的出库单'}), 400
        
        # 删除明细
        MaterialOutboundOrderDetail.query.filter_by(material_outbound_order_id=order_id).delete()
        
        # 删除主单
        db.session.delete(order)
        db.session.commit()

        return jsonify({
            'code': 200,
            'message': '删除成功'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'删除失败: {str(e)}'}), 500


@bp.route('/material-outbound-orders/<order_id>/submit', methods=['POST'])
@jwt_required()
def submit_material_outbound_order(order_id):
    """提交材料出库单"""
    try:
        current_user = get_jwt_identity()
        
        order = MaterialOutboundOrder.query.get(order_id)
        if not order:
            return jsonify({'code': 404, 'message': '出库单不存在'}), 404
        
        if order.status != 'draft':
            return jsonify({'code': 400, 'message': '只能提交草稿状态的出库单'}), 400
        
        order.status = 'submitted'
        order.submitted_by = current_user
        order.submitted_at = datetime.now()
        order.approval_status = 'pending'
        
        db.session.commit()

        return jsonify({
            'code': 200,
            'message': '提交成功',
            'data': order.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'提交失败: {str(e)}'}), 500


@bp.route('/material-outbound-orders/<order_id>/approve', methods=['POST'])
@jwt_required()
def approve_material_outbound_order(order_id):
    """审核材料出库单"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        approval_status = data.get('approval_status', 'approved')
        approval_comments = data.get('approval_comments', '')
        
        order = MaterialOutboundOrder.query.get(order_id)
        if not order:
            return jsonify({'code': 404, 'message': '出库单不存在'}), 404
        
        if order.status != 'submitted':
            return jsonify({'code': 400, 'message': '只能审核已提交的出库单'}), 400
        
        order.approval_status = approval_status
        order.approved_by = current_user
        order.approved_at = datetime.now()
        order.approval_comments = approval_comments
        
        if approval_status == 'approved':
            order.status = 'approved'
        elif approval_status == 'rejected':
            order.status = 'rejected'
        
        db.session.commit()

        return jsonify({
            'code': 200,
            'message': '审核成功',
            'data': order.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'审核失败: {str(e)}'}), 500


@bp.route('/material-outbound-orders/<order_id>/execute', methods=['POST'])
@jwt_required()
def execute_material_outbound_order(order_id):
    """执行材料出库单"""
    try:
        from app.models.business.inventory import Inventory, InventoryTransaction, MaterialOutboundOrderDetail
        from decimal import Decimal
        
        current_user = get_jwt_identity()
        
        order = MaterialOutboundOrder.query.get(order_id)
        if not order:
            return jsonify({'code': 404, 'message': '出库单不存在'}), 404
        
        if order.status != 'approved':
            return jsonify({'code': 400, 'message': '只能执行已审核通过的出库单'}), 400
        
        # 获取出库单明细
        details = MaterialOutboundOrderDetail.query.filter_by(
            material_outbound_order_id=order_id
        ).all()
        
        if not details:
            return jsonify({'code': 400, 'message': '出库单没有明细数据'}), 400
        
        # 处理每个明细的库存更新
        for detail in details:
            if not detail.material_id:
                continue
                
            # 查找对应的库存记录
            inventory = Inventory.query.filter_by(
                warehouse_id=order.warehouse_id,
                material_id=detail.material_id,
                batch_number=detail.batch_number,
                is_active=True
            ).first()
            
            if not inventory:
                # 如果没有找到精确匹配的库存（包括批次），尝试找不指定批次的库存
                inventory = Inventory.query.filter_by(
                    warehouse_id=order.warehouse_id,
                    material_id=detail.material_id,
                    is_active=True
                ).first()
            
            if not inventory:
                return jsonify({
                    'code': 400, 
                    'message': f'材料 {detail.material_name} 在仓库中没有库存记录'
                }), 400
            
            outbound_qty = Decimal(str(detail.outbound_quantity))
            
            # 检查库存是否足够
            if inventory.available_quantity < outbound_qty:
                return jsonify({
                    'code': 400,
                    'message': f'材料 {detail.material_name} 库存不足，可用数量: {inventory.available_quantity}，需要出库: {outbound_qty}'
                }), 400
            
            # 记录出库前数量
            quantity_before = inventory.current_quantity
            
            # 更新库存数量
            inventory.current_quantity -= outbound_qty
            inventory.available_quantity -= outbound_qty
            inventory.updated_by = current_user
            inventory.updated_at = datetime.now()
            
            # 重新计算总成本
            inventory.calculate_total_cost()
            
            # 生成库存流水记录
            transaction = InventoryTransaction(
                inventory_id=inventory.id,
                warehouse_id=inventory.warehouse_id,
                material_id=inventory.material_id,
                transaction_number=InventoryTransaction.generate_transaction_number(),
                transaction_type='out',
                quantity_change=-outbound_qty,
                quantity_before=quantity_before,
                quantity_after=inventory.current_quantity,
                unit=detail.unit,
                unit_price=detail.unit_price,
                total_amount=detail.total_amount,
                source_document_type='material_outbound_order',
                source_document_id=order.id,
                source_document_number=order.order_number,
                batch_number=detail.batch_number,
                from_location=detail.location_code,
                reason=f'材料出库单 {order.order_number} 执行',
                approval_status='approved',
                approved_by=current_user,
                approved_at=datetime.now(),
                created_by=current_user
            )
            
            # 计算流水总金额
            transaction.calculate_total_amount()
            
            db.session.add(transaction)
        
        # 更新出库单状态
        order.status = 'executed'
        order.executed_by = current_user
        order.executed_at = datetime.now()
        
        db.session.commit()

        return jsonify({
            'code': 200,
            'message': '执行成功，库存已更新',
            'data': order.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'执行失败: {str(e)}'}), 500


@bp.route('/material-outbound-orders/<order_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_material_outbound_order(order_id):
    """取消材料出库单"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        cancel_reason = data.get('cancel_reason', '')
        
        order = MaterialOutboundOrder.query.get(order_id)
        if not order:
            return jsonify({'code': 404, 'message': '出库单不存在'}), 404
        
        if order.status in ['executed', 'cancelled']:
            return jsonify({'code': 400, 'message': '该订单不能取消'}), 400
        
        order.status = 'cancelled'
        order.cancelled_by = current_user
        order.cancelled_at = datetime.now()
        order.cancel_reason = cancel_reason
        
        db.session.commit()

        return jsonify({
            'code': 200,
            'message': '取消成功',
            'data': order.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'取消失败: {str(e)}'}), 500 

