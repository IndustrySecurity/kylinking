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
    Inventory, InventoryTransaction,
    MaterialCountPlan, MaterialCountRecord
)
from app.models.basic_data import Material, Employee, Department
from app.utils.database import get_current_tenant_id

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
        
        # 获取部门名称和员工名称
        try:
            department_name = order.department.dept_name if order.department else None
        except Exception as e:
            current_app.logger.warning(f"获取部门名称失败: {e}")
            department_name = None
            
        try:
            inbound_person_name = order.inbound_person.employee_name if order.inbound_person else None
        except Exception as e:
            current_app.logger.warning(f"获取员工名称失败: {e}")
            inbound_person_name = None
        
        # 为了避免SQLAlchemy懒加载问题，手动构建返回数据
        order_data = {
            'id': str(order.id),
            'order_number': order.order_number,
            'order_date': order.order_date.isoformat() if order.order_date else None,
            'order_type': order.order_type,
            'warehouse_id': str(order.warehouse_id) if order.warehouse_id else None,
            'warehouse_name': order.warehouse_name,
            'inbound_person_id': str(order.inbound_person_id) if order.inbound_person_id else None,
            'inbound_person': inbound_person_name,
            'department_id': str(order.department_id) if order.department_id else None,
            'department': department_name,
            'status': order.status,
            'approval_status': order.approval_status,
            'supplier_id': str(order.supplier_id) if order.supplier_id else None,
            'supplier_name': order.supplier_name,
            'notes': order.notes,
            'created_at': order.created_at.isoformat() if order.created_at else None,
            'updated_at': order.updated_at.isoformat() if order.updated_at else None
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
        
        # 验证必需字段 - 修复：使用新的外键字段名
        required_fields = ['warehouse_id', 'order_type']
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
        
        # 处理字段名映射 - 前端可能使用旧字段名
        if 'outbound_person' in data and 'outbound_person_id' not in data:
            data['outbound_person_id'] = data.pop('outbound_person')
        
        if 'department' in data and 'department_id' not in data:
            data['department_id'] = data.pop('department')
            
        if 'requisition_department' in data and 'requisition_department_id' not in data:
            data['requisition_department_id'] = data.pop('requisition_department')
            
        if 'requisition_person' in data and 'requisition_person_id' not in data:
            data['requisition_person_id'] = data.pop('requisition_person')
        
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

        # 处理字段名映射
        if 'outbound_person' in data and 'outbound_person_id' not in data:
            data['outbound_person_id'] = data.pop('outbound_person')
        
        if 'department' in data and 'department_id' not in data:
            data['department_id'] = data.pop('department')
            
        if 'requisition_department' in data and 'requisition_department_id' not in data:
            data['requisition_department_id'] = data.pop('requisition_department')
            
        if 'requisition_person' in data and 'requisition_person_id' not in data:
            data['requisition_person_id'] = data.pop('requisition_person')

        # 更新主表字段
        updateable_fields = [
            'order_date', 'order_type', 'warehouse_id', 'warehouse_name',
            'outbound_person_id', 'department_id', 'requisition_department_id', 
            'requisition_person_id', 'requisition_purpose', 'remark'
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
                # 提取必需的位置参数
                material_outbound_order_id = order_id
                outbound_quantity = detail_data.pop('outbound_quantity', 0)
                unit = detail_data.pop('unit', 'kg')
                created_by = current_user
                
                detail = MaterialOutboundOrderDetail(
                    material_outbound_order_id=material_outbound_order_id,
                    outbound_quantity=outbound_quantity,
                    unit=unit,
                    created_by=created_by,
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

# ==================== 材料盘点管理 ====================

@bp.route('/material-count-plans', methods=['GET'])
@jwt_required()
@tenant_required
def get_material_count_plans():
    """获取材料盘点计划列表"""
    try:
        from app.models.business.inventory import MaterialCountPlan
        from sqlalchemy.orm import joinedload
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        warehouse_id = request.args.get('warehouse_id')
        
        query = MaterialCountPlan.query.options(
            joinedload(MaterialCountPlan.count_person),
            joinedload(MaterialCountPlan.department)
        )
        
        if status:
            query = query.filter(MaterialCountPlan.status == status)
        if warehouse_id:
            query = query.filter(MaterialCountPlan.warehouse_id == warehouse_id)
            
        query = query.order_by(MaterialCountPlan.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        plans = [plan.to_dict() for plan in pagination.items]

        return jsonify({
            'success': True,
            'data': {
                'plans': plans,
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page
            }
        })

    except Exception as e:
        current_app.logger.error(f"获取盘点计划失败: {str(e)}")
        return jsonify({'success': False, 'error': '获取盘点计划失败'}), 500

@bp.route('/material-count-plans', methods=['POST'])
@jwt_required()
@tenant_required
def create_material_count_plan():
    """创建材料盘点计划"""
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        # 验证必需字段
        required_fields = ['warehouse_id', 'warehouse_name', 'count_person_id', 'count_date']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'缺少必需字段: {field}'}), 400
        
        # 验证员工ID存在性（可选）
        employee = db.session.query(Employee).filter_by(id=data['count_person_id']).first()
        if not employee:
            return jsonify({'message': '指定的员工不存在'}), 400
        
        # 验证部门ID存在性（如果提供了部门ID）
        if data.get('department_id'):
            department = db.session.query(Department).filter_by(id=data['department_id']).first()
            if not department:
                return jsonify({'message': '指定的部门不存在'}), 400
        
        # 创建盘点计划
        plan = MaterialCountPlan(
            warehouse_id=data['warehouse_id'],
            warehouse_name=data['warehouse_name'],
            count_person_id=data['count_person_id'],
            count_date=datetime.fromisoformat(data['count_date'].replace('Z', '+00:00')),
            created_by=current_user_id,
            warehouse_code=data.get('warehouse_code'),
            department_id=data.get('department_id'),
            notes=data.get('notes')
        )
        
        db.session.add(plan)
        db.session.flush()  # 先保存获得ID，但不提交事务
        
        # 获取该仓库的所有材料库存并创建盘点记录
        inventories = db.session.query(Inventory).filter(
            Inventory.warehouse_id == data['warehouse_id'],
            Inventory.material_id.isnot(None)
        ).all()
        
        if not inventories:
            db.session.rollback()
            return jsonify({'message': '该仓库没有材料库存，无法创建盘点计划'}), 400
        
        # 为每个库存记录创建盘点记录
        for inventory in inventories:
            # 获取材料信息
            material = db.session.query(Material).filter(Material.id == inventory.material_id).first()
            
            count_record = MaterialCountRecord(
                count_plan_id=plan.id,
                inventory_id=inventory.id,
                material_id=inventory.material_id,
                material_code=material.material_code if material else f'MAT_{inventory.material_id}',
                material_name=material.material_name if material else '未知材料',
                material_spec=material.specification_model if material else '',
                batch_number=inventory.batch_number,
                location_code=inventory.location_code,
                unit=inventory.unit,
                book_quantity=inventory.current_quantity,
                actual_quantity=None,  # 等待盘点输入
                variance_quantity=0,
                variance_rate=0,
                status='pending',
                created_by=current_user_id
            )
            db.session.add(count_record)
        
        db.session.commit()
        
        return jsonify({
            'message': '盘点计划创建成功',
            'data': plan.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'创建盘点计划失败: {str(e)}'}), 500

@bp.route('/material-count-plans/<plan_id>/records', methods=['GET'])
@jwt_required()
@tenant_required
def get_material_count_records(plan_id):
    """获取盘点记录"""
    try:
        from app.models.business.inventory import MaterialCountRecord
        
        records = MaterialCountRecord.query.filter(
            MaterialCountRecord.count_plan_id == plan_id
        ).order_by(MaterialCountRecord.material_code).all()
        
        records_data = [record.to_dict() for record in records]
        
        return jsonify({
            'success': True,
            'data': records_data
        })
        
    except Exception as e:
        current_app.logger.error(f"获取盘点记录失败: {str(e)}")
        return jsonify({'success': False, 'error': '获取盘点记录失败'}), 500

@bp.route('/material-count-plans/<plan_id>/records/<record_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_material_count_record(plan_id, record_id):
    """更新盘点记录"""
    try:
        from app.models.business.inventory import MaterialCountRecord
        from decimal import Decimal
        
        data = request.get_json()
        
        record = MaterialCountRecord.query.filter(
            MaterialCountRecord.id == record_id,
            MaterialCountRecord.count_plan_id == plan_id
        ).first()
        
        if not record:
            return jsonify({'success': False, 'error': '盘点记录不存在'}), 404
        
        # 更新实盘数量
        if 'actual_quantity' in data:
            try:
                actual_quantity = data['actual_quantity']
                if actual_quantity is not None:
                    # 确保转换为Decimal类型
                    record.actual_quantity = Decimal(str(actual_quantity))
                else:
                    record.actual_quantity = None
                    
                record.calculate_variance()  # 重新计算差异
                record.status = 'counted'
            except (ValueError, TypeError, Decimal.InvalidOperation) as e:
                return jsonify({'success': False, 'error': f'实盘数量格式错误: {str(e)}'}), 400
            
        # 更新其他字段
        if 'variance_reason' in data:
            record.variance_reason = data['variance_reason']
        if 'notes' in data:
            record.notes = data['notes']
            
        record.updated_by = get_jwt_identity()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': record.to_dict(),
            'message': '盘点记录更新成功'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"更新盘点记录失败: {str(e)}")
        return jsonify({'success': False, 'error': f'更新盘点记录失败: {str(e)}'}), 500

@bp.route('/material-count-plans/<plan_id>/start', methods=['POST'])
@jwt_required()
@tenant_required
def start_material_count_plan(plan_id):
    """开始盘点"""
    try:
        from app.models.business.inventory import MaterialCountPlan
        
        plan = MaterialCountPlan.query.get(plan_id)
        if not plan:
            return jsonify({'success': False, 'error': '盘点计划不存在'}), 404
            
        if plan.status != 'draft':
            return jsonify({'success': False, 'error': '只能开始草稿状态的盘点计划'}), 400
        
        plan.status = 'in_progress'
        plan.updated_by = get_jwt_identity()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': plan.to_dict(),
            'message': '盘点已开始'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"开始盘点失败: {str(e)}")
        return jsonify({'success': False, 'error': '开始盘点失败'}), 500

@bp.route('/material-count-plans/<plan_id>/complete', methods=['POST'])
@jwt_required()
@tenant_required
def complete_material_count_plan(plan_id):
    """完成盘点"""
    try:
        from app.models.business.inventory import MaterialCountPlan
        
        plan = MaterialCountPlan.query.get(plan_id)
        if not plan:
            return jsonify({'success': False, 'error': '盘点计划不存在'}), 404
            
        if plan.status != 'in_progress':
            return jsonify({'success': False, 'error': '只能完成进行中的盘点计划'}), 400
        
        plan.status = 'completed'
        plan.updated_by = get_jwt_identity()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': plan.to_dict(),
            'message': '盘点已完成'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"完成盘点失败: {str(e)}")
        return jsonify({'success': False, 'error': '完成盘点失败'}), 500

@bp.route('/material-count-plans/<plan_id>/adjust', methods=['POST'])
@jwt_required()
@tenant_required
def adjust_material_count_inventory(plan_id):
    """调整库存"""
    try:
        from app.models.business.inventory import MaterialCountPlan, MaterialCountRecord, Inventory, InventoryTransaction
        
        plan = MaterialCountPlan.query.get(plan_id)
        if not plan:
            return jsonify({'success': False, 'error': '盘点计划不存在'}), 404
            
        if plan.status != 'completed':
            return jsonify({'success': False, 'error': '只能调整已完成的盘点计划'}), 400
        
        # 获取有差异的盘点记录
        records = MaterialCountRecord.query.filter(
            MaterialCountRecord.count_plan_id == plan_id,
            MaterialCountRecord.variance_quantity != 0,
            MaterialCountRecord.is_adjusted == False
        ).all()
        
        adjusted_count = 0
        
        for record in records:
            if record.variance_quantity == 0:
                continue
                
            # 更新库存
            inventory = Inventory.query.get(record.inventory_id)
            if inventory:
                old_quantity = inventory.current_quantity
                inventory.current_quantity = record.actual_quantity
                inventory.available_quantity = record.actual_quantity
                inventory.updated_by = get_jwt_identity()
                
                # 创建库存交易记录
                transaction_type = 'adjustment_in' if record.variance_quantity > 0 else 'adjustment_out'
                transaction = InventoryTransaction(
                    inventory_id=inventory.id,
                    warehouse_id=inventory.warehouse_id,
                    material_id=inventory.material_id,
                    transaction_type=transaction_type,
                    quantity_change=record.variance_quantity,
                    quantity_before=old_quantity,
                    quantity_after=record.actual_quantity,
                    unit=inventory.unit,
                    source_document_type='count_order',
                    source_document_number=plan.count_number,
                    reason=f'盘点调整: {record.variance_reason or "盘点差异调整"}',
                    created_by=get_jwt_identity()
                )
                db.session.add(transaction)
                
                # 标记记录为已调整
                record.is_adjusted = True
                record.status = 'adjusted'
                record.updated_by = get_jwt_identity()
                
                adjusted_count += 1
        
        # 更新盘点计划状态为已调整
        plan.status = 'adjusted'
        plan.updated_by = get_jwt_identity()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'成功调整了{adjusted_count}条库存记录'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"调整库存失败: {str(e)}")
        return jsonify({'success': False, 'error': '调整库存失败'}), 500

@bp.route('/warehouses/<warehouse_id>/material-inventory', methods=['GET'])
@jwt_required()
@tenant_required
def get_warehouse_material_inventory(warehouse_id):
    """获取仓库材料库存"""
    try:
        from app.models.business.inventory import Inventory
        
        # 查询该仓库的所有材料库存
        inventories = db.session.query(Inventory).filter(
            Inventory.warehouse_id == warehouse_id,
            Inventory.material_id.isnot(None)
        ).all()
        
        inventory_data = []
        for inventory in inventories:
            # 从材料表获取材料信息
            material = db.session.query(Material).filter(Material.id == inventory.material_id).first()
            
            inventory_dict = inventory.to_dict()
            if material:
                inventory_dict.update({
                    'material_code': material.material_code,
                    'material_name': material.material_name,
                    'material_spec': material.specification_model or ''
                })
            
            inventory_data.append(inventory_dict)
        
        return jsonify({
            'success': True,
            'data': inventory_data
        })
        
    except Exception as e:
        current_app.logger.error(f"获取仓库材料库存失败: {str(e)}")
        return jsonify({'success': False, 'error': '获取仓库材料库存失败'}), 500

# ==================== 材料调拨API ====================

@bp.route('/material-transfer-orders', methods=['GET'])
@jwt_required()
@tenant_required
def get_material_transfer_orders():
    """获取材料调拨单列表"""
    try:
        from app.models.business.inventory import MaterialTransferOrder
        
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
        query = MaterialTransferOrder.query
        
        if transfer_number:
            query = query.filter(MaterialTransferOrder.transfer_number.like(f'%{transfer_number}%'))
        if status:
            query = query.filter(MaterialTransferOrder.status == status)
        if transfer_type:
            query = query.filter(MaterialTransferOrder.transfer_type == transfer_type)
        if from_warehouse_id:
            query = query.filter(MaterialTransferOrder.from_warehouse_id == from_warehouse_id)
        if to_warehouse_id:
            query = query.filter(MaterialTransferOrder.to_warehouse_id == to_warehouse_id)
        if start_date:
            query = query.filter(MaterialTransferOrder.transfer_date >= start_date)
        if end_date:
            query = query.filter(MaterialTransferOrder.transfer_date <= end_date)
        
        # 分页查询
        pagination = query.order_by(MaterialTransferOrder.created_at.desc()).paginate(
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
        current_app.logger.error(f"获取材料调拨单列表失败: {str(e)}")
        return jsonify({'success': False, 'error': '获取调拨单列表失败'}), 500

@bp.route('/material-transfer-orders', methods=['POST'])
@jwt_required()
@tenant_required
def create_material_transfer_order():
    """创建材料调拨单"""
    try:
        from app.services.material_transfer_service import MaterialTransferService
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        required_fields = ['from_warehouse_id', 'to_warehouse_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'{field} 不能为空'}), 400
        
        # 创建调拨单
        transfer_order = MaterialTransferService.create_transfer_order(
            data, get_jwt_identity()
        )
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': transfer_order.to_dict(),
            'message': '调拨单创建成功'
        })
        
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"创建材料调拨单失败: {str(e)}")
        return jsonify({'success': False, 'error': '创建调拨单失败'}), 500

@bp.route('/material-transfer-orders/<order_id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_material_transfer_order(order_id):
    """获取材料调拨单详情"""
    try:
        from app.models.business.inventory import MaterialTransferOrder
        
        order = MaterialTransferOrder.query.get(order_id)
        if not order:
            return jsonify({'success': False, 'error': '调拨单不存在'}), 404
        
        return jsonify({
            'success': True,
            'data': order.to_dict()
        })
        
    except Exception as e:
        current_app.logger.error(f"获取材料调拨单详情失败: {str(e)}")
        return jsonify({'success': False, 'error': '获取调拨单详情失败'}), 500

@bp.route('/material-transfer-orders/<order_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_material_transfer_order(order_id):
    """更新材料调拨单"""
    try:
        from app.models.business.inventory import MaterialTransferOrder
        
        order = MaterialTransferOrder.query.get(order_id)
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
        current_app.logger.error(f"更新材料调拨单失败: {str(e)}")
        return jsonify({'success': False, 'error': '更新调拨单失败'}), 500

@bp.route('/material-transfer-orders/<order_id>/details', methods=['GET'])
@jwt_required()
@tenant_required
def get_material_transfer_order_details(order_id):
    """获取材料调拨单明细"""
    try:
        from app.models.business.inventory import MaterialTransferOrderDetail
        
        details = MaterialTransferOrderDetail.query.filter(
            MaterialTransferOrderDetail.transfer_order_id == order_id
        ).order_by(MaterialTransferOrderDetail.line_number).all()
        
        details_data = [detail.to_dict() for detail in details]
        
        return jsonify({
            'success': True,
            'data': details_data
        })
        
    except Exception as e:
        current_app.logger.error(f"获取材料调拨单明细失败: {str(e)}")
        return jsonify({'success': False, 'error': '获取调拨单明细失败'}), 500

@bp.route('/material-transfer-orders/<order_id>/details', methods=['POST'])
@jwt_required()
@tenant_required
def add_material_transfer_order_detail(order_id):
    """添加材料调拨单明细"""
    try:
        from app.services.material_transfer_service import MaterialTransferService
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        required_fields = ['material_id', 'transfer_quantity']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'{field} 不能为空'}), 400
        
        # 添加明细
        detail = MaterialTransferService.add_transfer_detail(
            order_id, data, get_jwt_identity()
        )
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': detail.to_dict(),
            'message': '明细添加成功'
        })
        
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"添加材料调拨单明细失败: {str(e)}")
        return jsonify({'success': False, 'error': '添加明细失败'}), 500

@bp.route('/material-transfer-orders/<order_id>/details/<detail_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_material_transfer_order_detail(order_id, detail_id):
    """更新材料调拨单明细"""
    try:
        from app.models.business.inventory import MaterialTransferOrder, MaterialTransferOrderDetail
        
        # 检查调拨单状态
        order = MaterialTransferOrder.query.get(order_id)
        if not order:
            return jsonify({'success': False, 'error': '调拨单不存在'}), 404
        
        if order.status not in ['draft']:
            return jsonify({'success': False, 'error': '只能修改草稿状态的调拨单明细'}), 400
        
        detail = MaterialTransferOrderDetail.query.get(detail_id)
        if not detail or detail.transfer_order_id != uuid.UUID(order_id):
            return jsonify({'success': False, 'error': '明细不存在'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '请求数据不能为空'}), 400
        
        # 更新字段
        if 'transfer_quantity' in data:
            transfer_quantity = Decimal(str(data['transfer_quantity']))
            if transfer_quantity <= 0:
                return jsonify({'success': False, 'error': '调拨数量必须大于0'}), 400
            
            # 检查库存
            from app.models.business.inventory import Inventory
            inventory = Inventory.query.get(detail.from_inventory_id)
            if inventory and inventory.available_quantity < transfer_quantity:
                return jsonify({'success': False, 'error': '库存不足'}), 400
            
            detail.transfer_quantity = transfer_quantity
            detail.calculate_total_amount()
        
        updateable_fields = ['unit_price', 'batch_number', 'notes']
        for field in updateable_fields:
            if field in data:
                setattr(detail, field, data[field])
        
        detail.updated_by = uuid.UUID(get_jwt_identity())
        
        # 更新调拨单统计信息
        order.calculate_totals()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': detail.to_dict(),
            'message': '明细更新成功'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"更新材料调拨单明细失败: {str(e)}")
        return jsonify({'success': False, 'error': '更新明细失败'}), 500

@bp.route('/material-transfer-orders/<order_id>/details/<detail_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_material_transfer_order_detail(order_id, detail_id):
    """删除材料调拨单明细"""
    try:
        from app.models.business.inventory import MaterialTransferOrder, MaterialTransferOrderDetail
        
        # 检查调拨单状态
        order = MaterialTransferOrder.query.get(order_id)
        if not order:
            return jsonify({'success': False, 'error': '调拨单不存在'}), 404
        
        if order.status not in ['draft']:
            return jsonify({'success': False, 'error': '只能删除草稿状态的调拨单明细'}), 400
        
        detail = MaterialTransferOrderDetail.query.get(detail_id)
        if not detail or detail.transfer_order_id != uuid.UUID(order_id):
            return jsonify({'success': False, 'error': '明细不存在'}), 404
        
        db.session.delete(detail)
        
        # 更新调拨单统计信息
        order.calculate_totals()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '明细删除成功'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"删除材料调拨单明细失败: {str(e)}")
        return jsonify({'success': False, 'error': '删除明细失败'}), 500

@bp.route('/material-transfer-orders/<order_id>/confirm', methods=['POST'])
@jwt_required()
@tenant_required
def confirm_material_transfer_order(order_id):
    """确认材料调拨单"""
    try:
        from app.services.material_transfer_service import MaterialTransferService
        
        MaterialTransferService.confirm_transfer_order(order_id, get_jwt_identity())
        
        return jsonify({
            'success': True,
            'message': '调拨单确认成功'
        })
        
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"确认材料调拨单失败: {str(e)}")
        return jsonify({'success': False, 'error': '确认调拨单失败'}), 500

@bp.route('/material-transfer-orders/<order_id>/execute', methods=['POST'])
@jwt_required()
@tenant_required
def execute_material_transfer_order(order_id):
    """执行材料调拨单（出库）"""
    try:
        from app.services.material_transfer_service import MaterialTransferService
        
        MaterialTransferService.execute_transfer_order(order_id, get_jwt_identity())
        
        return jsonify({
            'success': True,
            'message': '调拨单执行成功，材料已出库'
        })
        
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"执行材料调拨单失败: {str(e)}")
        return jsonify({'success': False, 'error': '执行调拨单失败'}), 500

@bp.route('/material-transfer-orders/<order_id>/receive', methods=['POST'])
@jwt_required()
@tenant_required
def receive_material_transfer_order(order_id):
    """接收材料调拨单（入库）"""
    try:
        from app.services.material_transfer_service import MaterialTransferService
        
        MaterialTransferService.receive_transfer_order(order_id, get_jwt_identity())
        
        return jsonify({
            'success': True,
            'message': '调拨单接收成功，材料已入库'
        })
        
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"接收材料调拨单失败: {str(e)}")
        return jsonify({'success': False, 'error': '接收调拨单失败'}), 500

@bp.route('/material-transfer-orders/<order_id>/cancel', methods=['POST'])
@jwt_required()
@tenant_required
def cancel_material_transfer_order(order_id):
    """取消材料调拨单"""
    try:
        from app.services.material_transfer_service import MaterialTransferService
        
        data = request.get_json() or {}
        reason = data.get('reason', '')
        
        MaterialTransferService.cancel_transfer_order(order_id, get_jwt_identity(), reason)
        
        return jsonify({
            'success': True,
            'message': '调拨单取消成功'
        })
        
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"取消材料调拨单失败: {str(e)}")
        return jsonify({'success': False, 'error': '取消调拨单失败'}), 500

@bp.route('/warehouses/<warehouse_id>/transfer-materials', methods=['GET'])
@jwt_required()
@tenant_required
def get_warehouse_transfer_materials(warehouse_id):
    """获取仓库可调拨材料库存"""
    try:
        from app.services.material_transfer_service import MaterialTransferService
        
        materials = MaterialTransferService.get_warehouse_material_inventory(warehouse_id)
        
        return jsonify({
            'success': True,
            'data': materials
        })

    except Exception as e:
        current_app.logger.error(f"获取仓库可调拨材料失败: {str(e)}")
        return jsonify({'success': False, 'error': '获取可调拨材料失败'}), 500

# ==================== 成品盘点管理 ====================

@bp.route('/product-count-plans', methods=['GET'])
@jwt_required()
def get_product_count_plans():
    """获取成品盘点计划列表"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        
        # 筛选条件
        filters = {}
        if request.args.get('warehouse_id'):
            filters['warehouse_id'] = request.args.get('warehouse_id')
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        if request.args.get('count_person_id'):
            filters['count_person_id'] = request.args.get('count_person_id')
        if request.args.get('start_date'):
            filters['start_date'] = request.args.get('start_date')
        if request.args.get('end_date'):
            filters['end_date'] = request.args.get('end_date')
        if request.args.get('search'):
            filters['search'] = request.args.get('search')
        
        from app.services.product_count_service import ProductCountService
        result = ProductCountService.get_count_plans(page, page_size, **filters)
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        current_app.logger.error(f"获取成品盘点计划列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"获取盘点计划列表失败: {str(e)}"
        }), 500


@bp.route('/product-count-plans', methods=['POST'])
@jwt_required()
def create_product_count_plan():
    """创建成品盘点计划"""
    try:
        data = request.get_json()
        
        # 验证必需字段
        required_fields = ['warehouse_id', 'count_person_id', 'count_date']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'message': f'缺少必需字段: {field}'
                }), 400
        
        user_id = get_jwt_identity()
        from app.services.product_count_service import ProductCountService
        result = ProductCountService.create_count_plan(data, user_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '盘点计划创建成功'
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        current_app.logger.error(f"创建成品盘点计划失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"创建盘点计划失败: {str(e)}"
        }), 500


@bp.route('/product-count-plans/<plan_id>', methods=['GET'])
@jwt_required()
def get_product_count_plan(plan_id):
    """获取成品盘点计划详情"""
    try:
        from app.services.product_count_service import ProductCountService
        result = ProductCountService.get_count_plan(plan_id)
        return jsonify({
            'success': True,
            'data': result
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 404
    except Exception as e:
        current_app.logger.error(f"获取成品盘点计划详情失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"获取盘点计划详情失败: {str(e)}"
        }), 500


@bp.route('/product-count-plans/<plan_id>/records', methods=['GET'])
@jwt_required()
def get_product_count_records(plan_id):
    """获取成品盘点记录列表"""
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 50, type=int)
        
        from app.services.product_count_service import ProductCountService
        result = ProductCountService.get_count_records(plan_id, page, page_size)
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        current_app.logger.error(f"获取成品盘点记录失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"获取盘点记录失败: {str(e)}"
        }), 500


@bp.route('/product-count-plans/<plan_id>/records/<record_id>', methods=['PUT'])
@jwt_required()
def update_product_count_record(plan_id, record_id):
    """更新成品盘点记录"""
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        from app.services.product_count_service import ProductCountService
        result = ProductCountService.update_count_record(plan_id, record_id, data, user_id)
        return jsonify({
            'success': True,
            'data': result,
            'message': '盘点记录更新成功'
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        current_app.logger.error(f"更新成品盘点记录失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"更新盘点记录失败: {str(e)}"
        }), 500


@bp.route('/product-count-plans/<plan_id>/start', methods=['POST'])
@jwt_required()
def start_product_count_plan(plan_id):
    """开始成品盘点计划"""
    try:
        user_id = get_jwt_identity()
        from app.services.product_count_service import ProductCountService
        result = ProductCountService.start_count_plan(plan_id, user_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '盘点计划已开始'
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        current_app.logger.error(f"开始成品盘点计划失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"开始盘点计划失败: {str(e)}"
        }), 500


@bp.route('/product-count-plans/<plan_id>/complete', methods=['POST'])
@jwt_required()
def complete_product_count_plan(plan_id):
    """完成成品盘点计划"""
    try:
        user_id = get_jwt_identity()
        from app.services.product_count_service import ProductCountService
        result = ProductCountService.complete_count_plan(plan_id, user_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '盘点计划已完成'
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        current_app.logger.error(f"完成成品盘点计划失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"完成盘点计划失败: {str(e)}"
        }), 500


@bp.route('/product-count-plans/<plan_id>/adjust', methods=['POST'])
@jwt_required()
def adjust_product_inventory(plan_id):
    """根据成品盘点结果调整库存"""
    try:
        data = request.get_json() or {}
        record_ids = data.get('record_ids', [])
        
        user_id = get_jwt_identity()
        from app.services.product_count_service import ProductCountService
        result = ProductCountService.adjust_inventory(plan_id, record_ids, user_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': result.get('message', '库存调整成功')
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        current_app.logger.error(f"调整成品库存失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"调整库存失败: {str(e)}"
        }), 500


@bp.route('/product-count-plans/<plan_id>', methods=['DELETE'])
@jwt_required()
def delete_product_count_plan(plan_id):
    """删除成品盘点计划"""
    try:
        user_id = get_jwt_identity()
        from app.services.product_count_service import ProductCountService
        result = ProductCountService.delete_count_plan(plan_id, user_id)
        
        return jsonify({
            'success': True,
            'data': {"deleted": result},
            'message': '盘点计划删除成功'
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        current_app.logger.error(f"删除成品盘点计划失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"删除盘点计划失败: {str(e)}"
        }), 500


@bp.route('/product-count-plans/<plan_id>/statistics', methods=['GET'])
@jwt_required()
def get_product_count_statistics(plan_id):
    """获取成品盘点统计信息"""
    try:
        from app.services.product_count_service import ProductCountService
        result = ProductCountService.get_count_statistics(plan_id)
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        current_app.logger.error(f"获取成品盘点统计信息失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"获取统计信息失败: {str(e)}"
        }), 500


@bp.route('/warehouses/<warehouse_id>/product-inventory', methods=['GET'])
@jwt_required()
def get_warehouse_product_inventory(warehouse_id):
    """获取仓库成品库存"""
    try:
        from app.services.product_count_service import ProductCountService
        result = ProductCountService.get_warehouse_product_inventory(warehouse_id)
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        current_app.logger.error(f"获取仓库成品库存失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"获取成品库存失败: {str(e)}"
        }), 500

# ===== 成品调拨管理 =====

@bp.route('/product-transfer-orders', methods=['GET'])
@jwt_required()
@tenant_required
def get_product_transfer_orders():
    """获取成品调拨单列表"""
    try:
        from app.models.business.inventory import ProductTransferOrder
        from app.services.product_transfer_service import ProductTransferService
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        transfer_type = request.args.get('transfer_type')
        from_warehouse_id = request.args.get('from_warehouse_id')
        to_warehouse_id = request.args.get('to_warehouse_id')
        transfer_number = request.args.get('transfer_number')
        
        # 构建查询 - 移除tenant_id过滤
        query = db.session.query(ProductTransferOrder)
        
        # 添加过滤条件
        if status:
            query = query.filter(ProductTransferOrder.status == status)
        if transfer_type:
            query = query.filter(ProductTransferOrder.transfer_type == transfer_type)
        if from_warehouse_id:
            query = query.filter(ProductTransferOrder.from_warehouse_id == from_warehouse_id)
        if to_warehouse_id:
            query = query.filter(ProductTransferOrder.to_warehouse_id == to_warehouse_id)
        if transfer_number:
            query = query.filter(ProductTransferOrder.transfer_number.ilike(f'%{transfer_number}%'))
        
        # 排序
        query = query.order_by(ProductTransferOrder.created_at.desc())
        
        # 分页
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # 转换数据
        orders = []
        for order in pagination.items:
            order_dict = order.to_dict()
            orders.append(order_dict)
        
        return jsonify({
            'success': True,
            'data': {
                'orders': orders,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_prev': pagination.has_prev,
                    'has_next': pagination.has_next
                }
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"获取成品调拨单列表失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取失败: {str(e)}'}), 500


@bp.route('/product-transfer-orders', methods=['POST'])
@jwt_required()
@tenant_required
def create_product_transfer_order():
    """创建成品调拨单"""
    try:
        from app.services.product_transfer_service import ProductTransferService
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '请求数据不能为空'}), 400
        
        current_user_id = get_jwt_identity()
        result = ProductTransferService.create_transfer_order(data, current_user_id)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        current_app.logger.error(f"创建成品调拨单失败: {str(e)}")
        return jsonify({'success': False, 'message': f'创建失败: {str(e)}'}), 500


@bp.route('/product-transfer-orders/<order_id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_product_transfer_order(order_id):
    """获取成品调拨单详情"""
    try:
        from app.models.business.inventory import ProductTransferOrder
        
        order = db.session.query(ProductTransferOrder).filter_by(
            id=order_id
        ).first()
        
        if not order:
            return jsonify({'success': False, 'message': '调拨单不存在'}), 404
        
        return jsonify({
            'success': True,
            'data': order.to_dict()
        })
        
    except Exception as e:
        current_app.logger.error(f"获取成品调拨单详情失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取失败: {str(e)}'}), 500


@bp.route('/product-transfer-orders/<order_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_product_transfer_order(order_id):
    """更新成品调拨单"""
    try:
        from app.models.business.inventory import ProductTransferOrder
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '请求数据不能为空'}), 400
        
        order = db.session.query(ProductTransferOrder).filter_by(
            id=order_id
        ).first()
        
        if not order:
            return jsonify({'success': False, 'message': '调拨单不存在'}), 404
        
        if order.status != 'draft':
            return jsonify({'success': False, 'message': '只能修改草稿状态的调拨单'}), 400
        
        # 更新字段
        current_user_id = get_jwt_identity()
        updatable_fields = [
            'transfer_type', 'transfer_person_id', 'department_id',
            'transporter', 'transport_method', 'expected_arrival_date', 'notes'
        ]
        
        for field in updatable_fields:
            if field in data:
                if field == 'expected_arrival_date' and data[field]:
                    setattr(order, field, datetime.fromisoformat(data[field].replace('Z', '+00:00')))
                else:
                    setattr(order, field, data[field])
        
        order.updated_by = current_user_id
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '调拨单更新成功',
            'data': order.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"更新成品调拨单失败: {str(e)}")
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500


@bp.route('/product-transfer-orders/<order_id>/details', methods=['GET'])
@jwt_required()
@tenant_required
def get_product_transfer_order_details(order_id):
    """获取成品调拨单明细"""
    try:
        from app.models.business.inventory import ProductTransferOrderDetail
        
        details = db.session.query(ProductTransferOrderDetail).filter_by(
            transfer_order_id=order_id
        ).order_by(ProductTransferOrderDetail.line_number).all()
        
        detail_list = []
        for detail in details:
            detail_list.append(detail.to_dict())
        
        return jsonify({
            'success': True,
            'data': detail_list
        })
        
    except Exception as e:
        current_app.logger.error(f"获取成品调拨单明细失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取失败: {str(e)}'}), 500


@bp.route('/product-transfer-orders/<order_id>/details', methods=['POST'])
@jwt_required()
@tenant_required
def add_product_transfer_order_detail(order_id):
    """添加成品调拨单明细"""
    try:
        from app.services.product_transfer_service import ProductTransferService
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '请求数据不能为空'}), 400
        
        current_user_id = get_jwt_identity()
        result = ProductTransferService.add_transfer_detail(order_id, data, current_user_id)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        current_app.logger.error(f"添加成品调拨单明细失败: {str(e)}")
        return jsonify({'success': False, 'message': f'添加失败: {str(e)}'}), 500


@bp.route('/product-transfer-orders/<order_id>/details/<detail_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_product_transfer_order_detail(order_id, detail_id):
    """更新成品调拨单明细"""
    try:
        from app.models.business.inventory import ProductTransferOrderDetail, ProductTransferOrder
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '请求数据不能为空'}), 400
        
        # 验证调拨单状态
        order = db.session.query(ProductTransferOrder).filter_by(
            id=order_id
        ).first()
        
        if not order:
            return jsonify({'success': False, 'message': '调拨单不存在'}), 404
        
        if order.status != 'draft':
            return jsonify({'success': False, 'message': '只能修改草稿状态的调拨单明细'}), 400
        
        detail = db.session.query(ProductTransferOrderDetail).filter_by(
            id=detail_id,
            transfer_order_id=order_id
        ).first()
        
        if not detail:
            return jsonify({'success': False, 'message': '调拨明细不存在'}), 404
        
        # 更新明细
        current_user_id = get_jwt_identity()
        if 'transfer_quantity' in data:
            detail.transfer_quantity = data['transfer_quantity']
            detail.calculate_total_amount()
        
        if 'to_location_code' in data:
            detail.to_location_code = data['to_location_code']
        
        if 'notes' in data:
            detail.notes = data['notes']
        
        detail.updated_by = current_user_id
        
        # 更新调拨单统计信息
        order.calculate_totals()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '调拨明细更新成功',
            'data': detail.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"更新成品调拨单明细失败: {str(e)}")
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500


@bp.route('/product-transfer-orders/<order_id>/details/<detail_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_product_transfer_order_detail(order_id, detail_id):
    """删除成品调拨单明细"""
    try:
        from app.models.business.inventory import ProductTransferOrderDetail, ProductTransferOrder
        
        # 验证调拨单状态
        order = db.session.query(ProductTransferOrder).filter_by(
            id=order_id
        ).first()
        
        if not order:
            return jsonify({'success': False, 'message': '调拨单不存在'}), 404
        
        if order.status != 'draft':
            return jsonify({'success': False, 'message': '只能删除草稿状态的调拨单明细'}), 400
        
        detail = db.session.query(ProductTransferOrderDetail).filter_by(
            id=detail_id,
            transfer_order_id=order_id
        ).first()
        
        if not detail:
            return jsonify({'success': False, 'message': '调拨明细不存在'}), 404
        
        db.session.delete(detail)
        
        # 更新调拨单统计信息
        order.calculate_totals()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '调拨明细删除成功'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"删除成品调拨单明细失败: {str(e)}")
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500


@bp.route('/product-transfer-orders/<order_id>/confirm', methods=['POST'])
@jwt_required()
@tenant_required
def confirm_product_transfer_order(order_id):
    """确认成品调拨单"""
    try:
        from app.services.product_transfer_service import ProductTransferService
        
        current_user_id = get_jwt_identity()
        result = ProductTransferService.confirm_transfer_order(order_id, current_user_id)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        current_app.logger.error(f"确认成品调拨单失败: {str(e)}")
        return jsonify({'success': False, 'message': f'确认失败: {str(e)}'}), 500


@bp.route('/product-transfer-orders/<order_id>/execute', methods=['POST'])
@jwt_required()
@tenant_required
def execute_product_transfer_order(order_id):
    """执行成品调拨单"""
    try:
        from app.services.product_transfer_service import ProductTransferService
        
        current_user_id = get_jwt_identity()
        result = ProductTransferService.execute_transfer_order(order_id, current_user_id)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        current_app.logger.error(f"执行成品调拨单失败: {str(e)}")
        return jsonify({'success': False, 'message': f'执行失败: {str(e)}'}), 500


@bp.route('/product-transfer-orders/<order_id>/receive', methods=['POST'])
@jwt_required()
@tenant_required
def receive_product_transfer_order(order_id):
    """收货确认成品调拨单"""
    try:
        from app.services.product_transfer_service import ProductTransferService
        
        current_user_id = get_jwt_identity()
        result = ProductTransferService.receive_transfer_order(order_id, current_user_id)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        current_app.logger.error(f"收货确认成品调拨单失败: {str(e)}")
        return jsonify({'success': False, 'message': f'收货确认失败: {str(e)}'}), 500


@bp.route('/product-transfer-orders/<order_id>/cancel', methods=['POST'])
@jwt_required()
@tenant_required
def cancel_product_transfer_order(order_id):
    """取消成品调拨单"""
    try:
        from app.services.product_transfer_service import ProductTransferService
        
        data = request.get_json() or {}
        reason = data.get('reason', '用户取消')
        
        current_user_id = get_jwt_identity()
        result = ProductTransferService.cancel_transfer_order(order_id, current_user_id, reason)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        current_app.logger.error(f"取消成品调拨单失败: {str(e)}")
        return jsonify({'success': False, 'message': f'取消失败: {str(e)}'}), 500


@bp.route('/warehouses/<warehouse_id>/transfer-product-inventory', methods=['GET'])
@jwt_required()
@tenant_required
def get_warehouse_transfer_product_inventory(warehouse_id):
    """获取仓库成品库存（用于调拨）"""
    try:
        current_app.logger.info(f"获取仓库成品库存，仓库ID: {warehouse_id}")
        from app.services.product_transfer_service import ProductTransferService
        
        result = ProductTransferService.get_warehouse_product_inventory(warehouse_id)
        current_app.logger.info(f"服务返回结果: {result}")
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        current_app.logger.error(f"获取仓库成品库存失败: {str(e)}")
        return jsonify({'success': False, 'message': f'获取失败: {str(e)}'}), 500

