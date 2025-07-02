# -*- coding: utf-8 -*-
"""
供应商分类管理API
对应services/base_archive/base_category/supplier_category_service.py
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.tenant.routes import tenant_required
from app.services.base_archive.base_category.supplier_category_service import SupplierCategoryService

supplier_category_bp = Blueprint('supplier_category', __name__)

# 为统一导入方式提供别名
bp = supplier_category_bp


@supplier_category_bp.route('/', methods=['GET'])
@jwt_required()
@tenant_required
def get_supplier_categories():
    """获取供应商分类列表"""
    try:
        service = SupplierCategoryService()
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search')
        enabled_only = request.args.get('enabled_only', 'false').lower() == 'true'
        
        result = service.get_supplier_categories(
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


@supplier_category_bp.route('/<category_id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_supplier_category(category_id):
    """获取供应商分类详情"""
    try:
        service = SupplierCategoryService()
        category = service.get_supplier_category(category_id)
        
        return jsonify({
            'success': True,
            'data': category
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@supplier_category_bp.route('/', methods=['POST'])
@jwt_required()
@tenant_required
def create_supplier_category():
    """创建供应商分类"""
    try:
        service = SupplierCategoryService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        if not data.get('category_name'):
            return jsonify({'error': '供应商分类名称不能为空'}), 400
        
        category = service.create_supplier_category(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': category,
            'message': '供应商分类创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@supplier_category_bp.route('/<category_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_supplier_category(category_id):
    """更新供应商分类"""
    try:
        service = SupplierCategoryService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        category = service.update_supplier_category(category_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': category,
            'message': '供应商分类更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@supplier_category_bp.route('/<category_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_supplier_category(category_id):
    """删除供应商分类"""
    try:
        service = SupplierCategoryService()
        service.delete_supplier_category(category_id)
        
        return jsonify({
            'success': True,
            'message': '供应商分类删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@supplier_category_bp.route('/enabled', methods=['GET'])
@jwt_required()
@tenant_required
def get_enabled_supplier_categories():
    """获取启用的供应商分类列表"""
    try:
        service = SupplierCategoryService()
        categories = service.get_enabled_supplier_categories()
        
        return jsonify({
            'success': True,
            'data': categories
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 