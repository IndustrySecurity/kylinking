# -*- coding: utf-8 -*-
"""
库存查询API路由
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.tenant.routes import tenant_required
from app.services import InventoryService
from decimal import Decimal
from datetime import datetime

bp = Blueprint('inventory_query', __name__)


@bp.route('/inventories', methods=['GET'])
@jwt_required()
@tenant_required
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
        
        # 创建服务实例
        service = InventoryService()
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
@tenant_required
def get_inventory(inventory_id):
    """获取库存详情"""
    try:
        service = InventoryService()
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
@tenant_required
def create_inventory():
    """创建库存记录"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        service = InventoryService()
        inventory = service.create_inventory(
            warehouse_id=data.get('warehouse_id'),
            unit=data.get('unit'),
            created_by=current_user_id,
            product_id=data.get('product_id'),
            material_id=data.get('material_id'),
            **{k: v for k, v in data.items() if k not in ['warehouse_id', 'unit', 'product_id', 'material_id']}
        )
        
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
@tenant_required
def update_inventory(inventory_id):
    """更新库存记录"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        service = InventoryService()
        inventory = service.update_inventory_quantity(
            inventory_id=inventory_id, 
            quantity_change=Decimal(data.get('quantity_change', 0)),
            transaction_type=data.get('transaction_type', 'adjustment'),
            updated_by=current_user_id,
            reason=data.get('reason'),
            **{k: v for k, v in data.items() if k not in ['quantity_change', 'transaction_type', 'reason']}
        )
        
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
@tenant_required
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
        
        service = InventoryService()
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
@tenant_required
def reserve_inventory():
    """预留库存"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        service = InventoryService()
        result = service.reserve_inventory(
            inventory_id=data.get('inventory_id'),
            quantity=Decimal(data.get('quantity', 0)),
            reserved_by=current_user_id,
            reason=data.get('reason'),
            reference_type=data.get('reference_type'),
            reference_id=data.get('reference_id')
        )
        
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
@tenant_required
def unreserve_inventory():
    """取消预留库存"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        service = InventoryService()
        result = service.release_reserved_inventory(
            inventory_id=data.get('inventory_id'),
            quantity=Decimal(data.get('quantity', 0)),
            released_by=current_user_id,
            reason=data.get('reason')
        )
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '库存预留取消成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/reports/low-stock', methods=['GET'])
@jwt_required()
@tenant_required
def get_low_stock_alerts():
    """获取低库存预警"""
    try:
        warehouse_id = request.args.get('warehouse_id')
        
        service = InventoryService()
        result = service.get_low_stock_alerts(warehouse_id=warehouse_id)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/reports/inventory-statistics', methods=['GET'])
@jwt_required()
@tenant_required
def get_inventory_statistics():
    """获取库存统计"""
    try:
        warehouse_id = request.args.get('warehouse_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 日期转换
        if start_date:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        service = InventoryService()
        result = service.get_inventory_statistics(
            warehouse_id=warehouse_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 