# -*- coding: utf-8 -*-
"""
仓库管理API路由
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services.base_archive.production.production_archive.warehouse_service import WarehouseService
from app.api.tenant.routes import tenant_required

bp = Blueprint('warehouse', __name__)


@bp.route('/', methods=['GET'])
@jwt_required()
@tenant_required
def get_warehouses():
    """获取仓库列表"""
    try:
        warehouse_service = WarehouseService()
        # 获取查询参数
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search')
        warehouse_type = request.args.get('warehouse_type')
        
        # 获取仓库列表
        result = warehouse_service.get_warehouses(
            page=page,
            per_page=per_page,
            search=search,
            warehouse_type=warehouse_type
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<warehouse_id>', methods=['GET'])
@jwt_required()
def get_warehouse(warehouse_id):
    """获取仓库详情"""
    try:
        warehouse_service = WarehouseService()
        warehouse = warehouse_service.get_warehouse(warehouse_id)
        
        return jsonify({
            'success': True,
            'data': warehouse
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/', methods=['POST'])
@jwt_required()
def create_warehouse():
    """创建仓库"""
    try:
        warehouse_service = WarehouseService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        if not data.get('warehouse_name'):
            return jsonify({'error': '仓库名称不能为空'}), 400
        
        warehouse = warehouse_service.create_warehouse(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': warehouse,
            'message': '仓库创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<warehouse_id>', methods=['PUT'])
@jwt_required()
def update_warehouse(warehouse_id):
    """更新仓库"""
    try:
        warehouse_service = WarehouseService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        warehouse = warehouse_service.update_warehouse(warehouse_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': warehouse,
            'message': '仓库更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<warehouse_id>', methods=['DELETE'])
@jwt_required()
def delete_warehouse(warehouse_id):
    """删除仓库"""
    try:
        warehouse_service = WarehouseService()
        warehouse_service.delete_warehouse(warehouse_id)
        
        return jsonify({
            'success': True,
            'message': '仓库删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/options', methods=['GET'])
@jwt_required()
@tenant_required
def get_warehouse_options():
    """获取仓库选项"""
    try:
        warehouse_service = WarehouseService()
        
        # 获取仓库列表
        warehouse_type = request.args.get('warehouse_type')
        warehouses = warehouse_service.get_warehouses(page=1, per_page=20, warehouse_type=warehouse_type)
        
        # 转换为选项格式
        options = []
        if warehouses and 'warehouses' in warehouses:
            for warehouse in warehouses['warehouses']:
                options.append({
                    'value': str(warehouse['id']),
                    'label': warehouse['warehouse_name'],
                    'code': warehouse.get('warehouse_code', ''),
                    'type': warehouse.get('warehouse_type', ''),
                    'warehouse_type': warehouse.get('warehouse_type', ''),
                    'location': warehouse.get('location', ''),
                    'address': warehouse.get('address', ''),
                    'manager': warehouse.get('manager', ''),
                    'contact_phone': warehouse.get('contact_phone', ''),
                    'description': warehouse.get('description', '')
                })
        
        return jsonify({
            'success': True,
            'data': options
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 