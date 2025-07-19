# -*- coding: utf-8 -*-
"""
报价运费管理API
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.tenant.routes import tenant_required
from app.services.base_archive.production_config.quote_freight_service import get_quote_freight_service

bp = Blueprint('quote_freight', __name__)

@bp.route('/', methods=['GET'])
@jwt_required()
@tenant_required
def get_quote_freights():
    """获取报价运费列表"""
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        search = request.args.get('search', '')
        
        service = get_quote_freight_service()
        result = service.get_quote_freights(page=page, per_page=page_size, search=search)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/', methods=['POST'])
@jwt_required()
@tenant_required
def create_quote_freight():
    """创建报价运费"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        user_id = get_jwt_identity()
        service = get_quote_freight_service()
        result = service.create_quote_freight(data, user_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '报价运费创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<freight_id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_quote_freight(freight_id):
    """获取报价运费详情"""
    try:
        service = get_quote_freight_service()
        result = service.get_quote_freight(freight_id)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<freight_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_quote_freight(freight_id):
    """更新报价运费"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        user_id = get_jwt_identity()
        service = get_quote_freight_service()
        result = service.update_quote_freight(freight_id, data, user_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '报价运费更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<freight_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_quote_freight(freight_id):
    """删除报价运费"""
    try:
        service = get_quote_freight_service()
        service.delete_quote_freight(freight_id)
        
        return jsonify({
            'success': True,
            'message': '报价运费删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/enabled', methods=['GET'])
@jwt_required()
@tenant_required
def get_enabled_quote_freights():
    """获取启用的报价运费列表"""
    try:
        service = get_quote_freight_service()
        result = service.get_enabled_quote_freights()
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/batch-update', methods=['POST'])
@jwt_required()
@tenant_required
def batch_update_quote_freights():
    """批量更新报价运费"""
    try:
        data = request.get_json()
        if not data or not isinstance(data, list):
            return jsonify({'error': '请求数据必须是数组'}), 400
        
        user_id = get_jwt_identity()
        service = get_quote_freight_service()
        result = service.batch_update_quote_freights(data, user_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': f'成功更新{len(result)}个报价运费'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500 