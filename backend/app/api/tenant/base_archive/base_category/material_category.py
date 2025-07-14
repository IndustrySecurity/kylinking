# -*- coding: utf-8 -*-
"""
材料分类管理API
对应services/base_archive/base_category/material_category_service.py
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.tenant.routes import tenant_required
from app.services.base_archive.base_category.material_category_service import MaterialCategoryService

material_category_bp = Blueprint('material_category', __name__)

# 为统一导入方式提供别名
bp = material_category_bp


@material_category_bp.route('/', methods=['GET'])
@jwt_required()
@tenant_required
def get_material_categories():
    """获取材料分类列表"""
    try:
        service = MaterialCategoryService()
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search')
        material_type = request.args.get('material_type')
        is_enabled = request.args.get('is_enabled')
        
        # 处理布尔值参数
        if is_enabled is not None:
            is_enabled = is_enabled.lower() == 'true'
        
        result = service.get_material_categories(
            page=page,
            per_page=per_page,
            search=search,
            material_type=material_type,
            is_enabled=is_enabled
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@material_category_bp.route('/<category_id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_material_category(category_id):
    """获取材料分类详情"""
    try:
        service = MaterialCategoryService()
        category = service.get_material_category_by_id(category_id)
        
        if not category:
            return jsonify({'error': '材料分类不存在'}), 404
        
        return jsonify({
            'success': True,
            'data': category
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@material_category_bp.route('/', methods=['POST'])
@jwt_required()
@tenant_required
def create_material_category():
    """创建材料分类"""
    try:
        service = MaterialCategoryService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        if not data.get('material_name'):
            return jsonify({'error': '材料分类名称不能为空'}), 400
        
        category = service.create_material_category(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': category,
            'message': '材料分类创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@material_category_bp.route('/<category_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_material_category(category_id):
    """更新材料分类"""
    try:
        service = MaterialCategoryService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        category = service.update_material_category(category_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': category,
            'message': '材料分类更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@material_category_bp.route('/<category_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_material_category(category_id):
    """删除材料分类"""
    try:
        service = MaterialCategoryService()
        service.delete_material_category(category_id)
        
        return jsonify({
            'success': True,
            'message': '材料分类删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@material_category_bp.route('/enabled', methods=['GET'])
@jwt_required()
@tenant_required
def get_enabled_material_categories():
    """获取启用的材料分类列表"""
    try:
        service = MaterialCategoryService()
        result = service.get_material_categories(
            page=1,
            per_page=1000,
            is_enabled=True
        )
        
        return jsonify({
            'success': True,
            'data': result['material_categories']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@material_category_bp.route('/options', methods=['GET'])
@jwt_required()
@tenant_required
def get_material_category_options():
    """获取材料分类选项"""
    try:
        service = MaterialCategoryService()
        result = service.get_material_categories(
            page=1,
            per_page=1000,
            is_enabled=True
        )
        
        return jsonify({
            'success': True,
            'data': result['material_categories']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@material_category_bp.route('/form-options', methods=['GET'])
@jwt_required()
@tenant_required
def get_material_category_form_options():
    """获取材料分类表单选项"""
    try:
        service = MaterialCategoryService()
        
        # 获取材料类型选项
        material_types = service.get_material_types()
        
        # 获取单位选项
        units = service.get_units()
        
        return jsonify({
            'success': True,
            'data': {
                'material_types': material_types,
                'units': units
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@material_category_bp.route('/batch', methods=['PUT'])
@jwt_required()
@tenant_required
def batch_update_material_categories():
    """批量更新材料分类"""
    try:
        service = MaterialCategoryService()
        data = request.get_json()
        
        if not data or not data.get('updates'):
            return jsonify({'error': '请求数据不能为空'}), 400
        
        result = service.batch_update_material_categories(data['updates'])
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '批量更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500 