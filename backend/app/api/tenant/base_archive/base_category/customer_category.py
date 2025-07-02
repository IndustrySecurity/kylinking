# -*- coding: utf-8 -*-
"""
客户分类管理API路由
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services.base_archive.base_category.customer_category_service import CustomerCategoryService

bp = Blueprint('customer_category', __name__)


@bp.route('/', methods=['GET'])
@jwt_required()
def get_customer_categories():
    """获取客户分类列表"""
    try:
        customer_category_service = CustomerCategoryService()
        # 获取查询参数
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search')
        enabled_only = request.args.get('enabled_only', 'false').lower() == 'true'
        
        # 获取客户分类列表
        result = customer_category_service.get_customer_categories(
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


@bp.route('/<category_id>', methods=['GET'])
@jwt_required()
def get_customer_category(category_id):
    """获取客户分类详情"""
    try:
        customer_category_service = CustomerCategoryService()
        category = customer_category_service.get_customer_category(category_id)
        
        return jsonify({
            'success': True,
            'data': category
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/', methods=['POST'])
@jwt_required()
def create_customer_category():
    """创建客户分类"""
    try:
        customer_category_service = CustomerCategoryService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        if not data.get('category_name'):
            return jsonify({'error': '客户分类名称不能为空'}), 400
        
        category = customer_category_service.create_customer_category(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': category,
            'message': '客户分类创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<category_id>', methods=['PUT'])
@jwt_required()
def update_customer_category(category_id):
    """更新客户分类"""
    try:
        customer_category_service = CustomerCategoryService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        category = customer_category_service.update_customer_category(category_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': category,
            'message': '客户分类更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<category_id>', methods=['DELETE'])
@jwt_required()
def delete_customer_category(category_id):
    """删除客户分类"""
    try:
        customer_category_service = CustomerCategoryService()
        customer_category_service.delete_customer_category(category_id)
        
        return jsonify({
            'success': True,
            'message': '客户分类删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/enabled', methods=['GET'])
@jwt_required()
def get_enabled_customer_categories():
    """获取启用的客户分类列表"""
    try:
        customer_category_service = CustomerCategoryService()
        categories = customer_category_service.get_categories(include_inactive=False)
        
        return jsonify({
            'success': True,
            'data': categories
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/options', methods=['GET'])
@jwt_required()
def get_customer_category_options():
    """获取客户分类选项（用于下拉框）"""
    try:
        customer_category_service = CustomerCategoryService()
        options = customer_category_service.get_category_options()
        
        return jsonify({
            'success': True,
            'data': options
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/batch-update', methods=['POST'])
@jwt_required()
def batch_update_customer_categories():
    """批量更新客户分类"""
    try:
        customer_category_service = CustomerCategoryService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not isinstance(data, list):
            return jsonify({'error': '请求数据格式错误'}), 400
        
        results = []
        for item in data:
            if item.get('id'):
                try:
                    result = customer_category_service.update_customer_category(
                        item['id'], item, current_user_id
                    )
                    results.append(result)
                except Exception as e:
                    results.append({'error': str(e), 'id': item.get('id')})
        
        return jsonify({
            'success': True,
            'data': results,
            'message': '批量更新完成'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 