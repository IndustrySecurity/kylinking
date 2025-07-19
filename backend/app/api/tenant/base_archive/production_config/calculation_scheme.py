# -*- coding: utf-8 -*-
"""
计算方案管理API
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.tenant.routes import tenant_required
from app.services.base_archive.production_config.calculation_scheme_service import get_calculation_scheme_service

bp = Blueprint('calculation_scheme', __name__)

@bp.route('/', methods=['GET'])
@jwt_required()
@tenant_required
def get_calculation_schemes():
    """获取计算方案列表"""
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        search = request.args.get('search', '')
        category = request.args.get('category', '')
        
        service = get_calculation_scheme_service()
        result = service.get_calculation_schemes(
            page=page, 
            per_page=page_size, 
            search=search,
            category=category
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/', methods=['POST'])
@jwt_required()
@tenant_required
def create_calculation_scheme():
    """创建计算方案"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        user_id = get_jwt_identity()
        service = get_calculation_scheme_service()
        result = service.create_calculation_scheme(data, user_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '计算方案创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<scheme_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_calculation_scheme(scheme_id):
    """更新计算方案"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        user_id = get_jwt_identity()
        service = get_calculation_scheme_service()
        result = service.update_calculation_scheme(scheme_id, data, user_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '计算方案更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<scheme_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_calculation_scheme(scheme_id):
    """删除计算方案"""
    try:
        service = get_calculation_scheme_service()
        service.delete_calculation_scheme(scheme_id)
        
        return jsonify({
            'success': True,
            'message': '计算方案删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/options/by-category', methods=['GET'])
@jwt_required()
@tenant_required
def get_calculation_scheme_options_by_category():
    """获取按分类的计算方案选项"""
    try:
        service = get_calculation_scheme_service()
        category = request.args.get('category', '')
        if category:
            result = service.get_calculation_scheme_options_by_category(category)
        else:
            result = service.get_calculation_scheme_options()
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 

@bp.route('/categories', methods=['GET'])
@jwt_required()
@tenant_required
def get_calculation_scheme_categories():
    """获取计算方案分类"""
    try:
        service = get_calculation_scheme_service()
        result = service.get_scheme_categories()
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500