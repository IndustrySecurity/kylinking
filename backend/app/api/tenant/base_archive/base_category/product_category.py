# -*- coding: utf-8 -*-
"""
产品分类管理API
对应services/base_archive/base_category/product_category_service.py
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.tenant.routes import tenant_required
from app.services.base_archive.base_category.product_category_service import ProductCategoryService

product_category_bp = Blueprint('product_category', __name__)

# 为统一导入方式提供别名
bp = product_category_bp


@product_category_bp.route('/', methods=['GET'])
@jwt_required()
@tenant_required
def get_product_categories():
    """获取产品分类列表"""
    try:
        service = ProductCategoryService()
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search')
        enabled_only = request.args.get('enabled_only', 'false').lower() == 'true'
        
        result = service.get_product_categories(
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


@product_category_bp.route('/<category_id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_product_category(category_id):
    """获取产品分类详情"""
    try:
        service = ProductCategoryService()
        category = service.get_product_category(category_id)
        
        return jsonify({
            'success': True,
            'data': category
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@product_category_bp.route('/', methods=['POST'])
@jwt_required()
@tenant_required
def create_product_category():
    """创建产品分类"""
    try:
        service = ProductCategoryService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        if not data.get('category_name'):
            return jsonify({'error': '产品分类名称不能为空'}), 400
        
        category = service.create_product_category(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': category,
            'message': '产品分类创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@product_category_bp.route('/<category_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_product_category(category_id):
    """更新产品分类"""
    try:
        service = ProductCategoryService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        category = service.update_product_category(category_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': category,
            'message': '产品分类更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@product_category_bp.route('/<category_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_product_category(category_id):
    """删除产品分类"""
    try:
        service = ProductCategoryService()
        service.delete_product_category(category_id)
        
        return jsonify({
            'success': True,
            'message': '产品分类删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@product_category_bp.route('/enabled', methods=['GET'])
@jwt_required()
@tenant_required
def get_enabled_product_categories():
    """获取启用的产品分类列表"""
    try:
        service = ProductCategoryService()
        categories = service.get_enabled_product_categories()
        
        return jsonify({
            'success': True,
            'data': categories
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@product_category_bp.route('/batch', methods=['PUT'])
@jwt_required()
@tenant_required
def batch_update_product_categories():
    """批量更新产品分类"""
    try:
        service = ProductCategoryService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data.get('updates'):
            return jsonify({'error': '请求数据不能为空'}), 400
        
        result = service.batch_update_product_categories(data['updates'], current_user_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '批量更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500 