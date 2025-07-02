# -*- coding: utf-8 -*-
"""
袋型相关公式管理API
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.tenant.routes import tenant_required
from app.services.base_archive.production.production_config.bag_related_formula_service import get_bag_related_formula_service

bp = Blueprint('bag_related_formula', __name__)

@bp.route('/', methods=['GET'])
@jwt_required()
@tenant_required
def get_bag_related_formulas():
    """获取袋型相关公式列表"""
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        search = request.args.get('search', '')
        
        service = get_bag_related_formula_service()
        result = service.get_bag_related_formulas(page=page, per_page=page_size, search=search)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/', methods=['POST'])
@jwt_required()
@tenant_required
def create_bag_related_formula():
    """创建袋型相关公式"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        user_id = get_jwt_identity()
        service = get_bag_related_formula_service()
        result = service.create_bag_related_formula(data, user_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '袋型相关公式创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<formula_id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_bag_related_formula(formula_id):
    """获取袋型相关公式详情"""
    try:
        service = get_bag_related_formula_service()
        result = service.get_bag_related_formula(formula_id)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<formula_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_bag_related_formula(formula_id):
    """更新袋型相关公式"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        user_id = get_jwt_identity()
        service = get_bag_related_formula_service()
        result = service.update_bag_related_formula(formula_id, data, user_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '袋型相关公式更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<formula_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_bag_related_formula(formula_id):
    """删除袋型相关公式"""
    try:
        service = get_bag_related_formula_service()
        service.delete_bag_related_formula(formula_id)
        
        return jsonify({
            'success': True,
            'message': '袋型相关公式删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/enabled', methods=['GET'])
@jwt_required()
@tenant_required
def get_enabled_bag_related_formulas():
    """获取启用的袋型相关公式列表"""
    try:
        service = get_bag_related_formula_service()
        result = service.get_enabled_bag_related_formulas()
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/batch-update', methods=['POST'])
@jwt_required()
@tenant_required
def batch_update_bag_related_formulas():
    """批量更新袋型相关公式"""
    try:
        data = request.get_json()
        if not data or not isinstance(data, list):
            return jsonify({'error': '请求数据必须是数组'}), 400
        
        user_id = get_jwt_identity()
        service = get_bag_related_formula_service()
        result = service.batch_update_bag_related_formulas(data, user_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': f'成功更新{len(result)}个袋型相关公式'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/options', methods=['GET'])
@jwt_required()
@tenant_required
def get_bag_related_formula_options():
    """获取袋型相关公式选项"""
    try:
        service = get_bag_related_formula_service()
        result = service.get_bag_related_formula_options()
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 