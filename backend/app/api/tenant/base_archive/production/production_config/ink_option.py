# -*- coding: utf-8 -*-
"""
油墨选项管理API
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.tenant.routes import tenant_required
from app.services.base_archive.production.production_config.ink_option_service import get_ink_option_service

bp = Blueprint('ink_option', __name__)

@bp.route('/', methods=['GET'])
@jwt_required()
@tenant_required
def get_ink_options():
    """获取油墨选项列表"""
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        search = request.args.get('search', '')
        
        service = get_ink_option_service()
        result = service.get_ink_options(page=page, per_page=page_size, search=search)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/', methods=['POST'])
@jwt_required()
@tenant_required
def create_ink_option():
    """创建油墨选项"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        user_id = get_jwt_identity()
        service = get_ink_option_service()
        result = service.create_ink_option(data, user_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '油墨选项创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<option_id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_ink_option(option_id):
    """获取油墨选项详情"""
    try:
        service = get_ink_option_service()
        result = service.get_ink_option(option_id)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<option_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_ink_option(option_id):
    """更新油墨选项"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        user_id = get_jwt_identity()
        service = get_ink_option_service()
        result = service.update_ink_option(option_id, data, user_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '油墨选项更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<option_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_ink_option(option_id):
    """删除油墨选项"""
    try:
        service = get_ink_option_service()
        service.delete_ink_option(option_id)
        
        return jsonify({
            'success': True,
            'message': '油墨选项删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/enabled', methods=['GET'])
@jwt_required()
@tenant_required
def get_enabled_ink_options():
    """获取启用的油墨选项列表"""
    try:
        service = get_ink_option_service()
        result = service.get_enabled_ink_options()
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/batch-update', methods=['POST'])
@jwt_required()
@tenant_required
def batch_update_ink_options():
    """批量更新油墨选项"""
    try:
        data = request.get_json()
        if not data or not isinstance(data, list):
            return jsonify({'error': '请求数据必须是数组'}), 400
        
        user_id = get_jwt_identity()
        service = get_ink_option_service()
        result = service.batch_update_ink_options(data, user_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': f'成功更新{len(result)}个油墨选项'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500 