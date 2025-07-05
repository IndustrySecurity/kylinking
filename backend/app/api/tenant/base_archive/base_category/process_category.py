# -*- coding: utf-8 -*-
"""
工序分类管理API
对应services/base_archive/base_category/process_category_service.py
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.tenant.routes import tenant_required
from app.services.base_archive.base_category.process_category_service import ProcessCategoryService
from app.models.basic_data import ProcessCategory

process_category_bp = Blueprint('process_category', __name__)

# 为统一导入方式提供别名
bp = process_category_bp


@process_category_bp.route('/', methods=['GET'])
@jwt_required()
@tenant_required
def get_process_categories():
    """获取工序分类列表"""
    try:
        service = ProcessCategoryService()
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search')
        enabled_only = request.args.get('enabled_only', 'false').lower() == 'true'
        
        result = service.get_process_categories(
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


@process_category_bp.route('/<category_id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_process_category(category_id):
    """获取工序分类详情"""
    try:
        service = ProcessCategoryService()
        category = service.get_process_category(category_id)
        
        return jsonify({
            'success': True,
            'data': category
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@process_category_bp.route('/', methods=['POST'])
@jwt_required()
@tenant_required
def create_process_category():
    """创建工序分类"""
    try:
        service = ProcessCategoryService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        if not data.get('process_name'):
            return jsonify({'error': '工序分类名称不能为空'}), 400
        
        category = service.create_process_category(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': category,
            'message': '工序分类创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@process_category_bp.route('/<category_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_process_category(category_id):
    """更新工序分类"""
    try:
        service = ProcessCategoryService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        category = service.update_process_category(category_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': category,
            'message': '工序分类更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@process_category_bp.route('/<category_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_process_category(category_id):
    """删除工序分类"""
    try:
        service = ProcessCategoryService()
        service.delete_process_category(category_id)
        
        return jsonify({
            'success': True,
            'message': '工序分类删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@process_category_bp.route('/enabled', methods=['GET'])
@jwt_required()
@tenant_required
def get_enabled_process_categories():
    """获取启用的工序分类列表"""
    try:
        service = ProcessCategoryService()
        categories = service.get_enabled_process_categories()
        
        return jsonify({
            'success': True,
            'data': categories
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@process_category_bp.route('/options', methods=['GET'])
@jwt_required()
@tenant_required
def get_process_category_options():
    """获取工序分类选项（用于下拉框）"""
    try:
        service = ProcessCategoryService()
        categories = service.get_enabled_process_categories()
        
        # 转换为选项格式
        options = [
            {'value': str(cat['id']), 'label': cat['process_name']}
            for cat in categories
        ]
        
        return jsonify({
            'success': True,
            'data': options
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@process_category_bp.route('/batch-update', methods=['POST'])
@jwt_required()
@tenant_required
def batch_update_process_categories():
    """批量更新工序分类"""
    try:
        service = ProcessCategoryService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not isinstance(data, list):
            return jsonify({'error': '请求数据格式错误'}), 400
        
        results = service.batch_update_process_categories(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': results,
            'message': '批量更新完成'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 


@bp.route('/category-type-options', methods=['GET'])
@jwt_required()
@tenant_required
def get_category_type_options():
    """工序分类 类型选项"""
    options = [{'value': code, 'label': name}
               for code, name in ProcessCategory.CATEGORY_TYPES]
    return jsonify({'success': True, 'data': options})

@bp.route('/data-collection-mode-options', methods=['GET'])
@jwt_required()
@tenant_required
def get_data_collection_mode_options():
    """工序分类 数据采集模式选项"""
    options = [{'value': code, 'label': name}
               for code, name in ProcessCategory.DATA_COLLECTION_MODES]
    return jsonify({'success': True, 'data': options})