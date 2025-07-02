# -*- coding: utf-8 -*-
"""
单位管理API路由
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services.base_archive.production.production_archive.unit_service import UnitService

bp = Blueprint('unit', __name__)


@bp.route('/', methods=['GET'])
@jwt_required()
def get_units():
    """获取单位列表"""
    try:
        unit_service = UnitService()
        # 获取查询参数
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search')
        enabled_only = request.args.get('enabled_only', 'false').lower() == 'true'
        
        # 获取单位列表
        result = unit_service.get_units(
            page=page,
            per_page=per_page,
            search=search,
            enabled_only=enabled_only
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<unit_id>', methods=['GET'])
@jwt_required()
def get_unit(unit_id):
    """获取单位详情"""
    try:
        unit_service = UnitService()
        unit = unit_service.get_unit(unit_id)
        
        return jsonify({
            'success': True,
            'data': unit
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/', methods=['POST'])
@jwt_required()
def create_unit():
    """创建单位"""
    try:
        unit_service = UnitService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        if not data.get('unit_name'):
            return jsonify({'error': '单位名称不能为空'}), 400
        
        unit = unit_service.create_unit(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': unit,
            'message': '单位创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<unit_id>', methods=['PUT'])
@jwt_required()
def update_unit(unit_id):
    """更新单位"""
    try:
        unit_service = UnitService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        unit = unit_service.update_unit(unit_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': unit,
            'message': '单位更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<unit_id>', methods=['DELETE'])
@jwt_required()
def delete_unit(unit_id):
    """删除单位"""
    try:
        unit_service = UnitService()
        unit_service.delete_unit(unit_id)
        
        return jsonify({
            'success': True,
            'message': '单位删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/batch', methods=['PUT'])
@jwt_required()
def batch_update_units():
    """批量更新单位"""
    try:
        unit_service = UnitService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'data' not in data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        results = unit_service.batch_update_units(data['data'], current_user_id)
        
        return jsonify({
            'success': True,
            'data': results,
            'message': '批量更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500 