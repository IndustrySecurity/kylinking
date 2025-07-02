# -*- coding: utf-8 -*-
"""
报价损耗管理API
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.tenant.routes import tenant_required
from app.services.base_archive.production.production_config.quote_loss_service import get_quote_loss_service

bp = Blueprint('quote_loss', __name__)

@bp.route('/', methods=['GET'])
@jwt_required()
@tenant_required
def get_quote_losses():
    """获取报价损耗列表"""
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        search = request.args.get('search', '')
        
        service = get_quote_loss_service()
        result = service.get_quote_losses(page=page, per_page=page_size, search=search)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/', methods=['POST'])
@jwt_required()
@tenant_required
def create_quote_loss():
    """创建报价损耗"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        user_id = get_jwt_identity()
        service = get_quote_loss_service()
        result = service.create_quote_loss(data, user_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '报价损耗创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<loss_id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_quote_loss(loss_id):
    """获取报价损耗详情"""
    try:
        service = get_quote_loss_service()
        result = service.get_quote_loss(loss_id)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<loss_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_quote_loss(loss_id):
    """更新报价损耗"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        user_id = get_jwt_identity()
        service = get_quote_loss_service()
        result = service.update_quote_loss(loss_id, data, user_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '报价损耗更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<loss_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_quote_loss(loss_id):
    """删除报价损耗"""
    try:
        service = get_quote_loss_service()
        service.delete_quote_loss(loss_id)
        
        return jsonify({
            'success': True,
            'message': '报价损耗删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/enabled', methods=['GET'])
@jwt_required()
@tenant_required
def get_enabled_quote_losses():
    """获取启用的报价损耗列表"""
    try:
        service = get_quote_loss_service()
        result = service.get_enabled_quote_losses()
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/batch-update', methods=['POST'])
@jwt_required()
@tenant_required
def batch_update_quote_losses():
    """批量更新报价损耗"""
    try:
        data = request.get_json()
        if not data or not isinstance(data, list):
            return jsonify({'error': '请求数据必须是数组'}), 400
        
        user_id = get_jwt_identity()
        service = get_quote_loss_service()
        result = service.batch_update_quote_losses(data, user_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': f'成功更新{len(result)}个报价损耗'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500 