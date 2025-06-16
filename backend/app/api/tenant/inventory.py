# -*- coding: utf-8 -*-
"""
库存管理API路由
"""

from flask import Blueprint, request, jsonify, current_app, g
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from .routes import tenant_required
from app.services.inventory_service import InventoryService
from app.services.outbound_order_service import OutboundOrderService
from app.models.user import User
from app.extensions import db
from decimal import Decimal
from datetime import datetime
import uuid

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

