# -*- coding: utf-8 -*-
"""
袋型管理API路由
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services.base_archive.production.production_archive.bag_type_service import BagTypeService
from app.api.tenant.routes import tenant_required

bp = Blueprint('bag_type', __name__)


@bp.route('/', methods=['GET'])
@jwt_required()
@tenant_required
def get_bag_types():
    """获取袋型列表"""
    try:
        bag_type_service = BagTypeService()
        # 获取查询参数
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search')
        is_enabled = request.args.get('is_enabled')
        if is_enabled is not None:
            is_enabled = is_enabled.lower() == 'true'
        
        # 获取袋型列表
        result = bag_type_service.get_bag_types(
            page=page,
            per_page=per_page,
            search=search,
            is_enabled=is_enabled
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<bag_type_id>', methods=['GET'])
@jwt_required()
def get_bag_type(bag_type_id):
    """获取袋型详情"""
    try:
        bag_type_service = BagTypeService()
        bag_type = bag_type_service.get_bag_type(bag_type_id)
        
        return jsonify({
            'success': True,
            'data': bag_type
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/', methods=['POST'])
@jwt_required()
def create_bag_type():
    """创建袋型"""
    try:
        bag_type_service = BagTypeService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        if not data.get('bag_type_name'):
            return jsonify({'error': '袋型名称不能为空'}), 400
        
        bag_type = bag_type_service.create_bag_type(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': bag_type,
            'message': '袋型创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<bag_type_id>', methods=['PUT'])
@jwt_required()
def update_bag_type(bag_type_id):
    """更新袋型"""
    try:
        bag_type_service = BagTypeService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        bag_type = bag_type_service.update_bag_type(bag_type_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': bag_type,
            'message': '袋型更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<bag_type_id>', methods=['DELETE'])
@jwt_required()
def delete_bag_type(bag_type_id):
    """删除袋型"""
    try:
        bag_type_service = BagTypeService()
        bag_type_service.delete_bag_type(bag_type_id)
        
        return jsonify({
            'success': True,
            'message': '袋型删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/batch', methods=['PUT'])
@jwt_required()
def batch_update_bag_types():
    """批量更新袋型"""
    try:
        bag_type_service = BagTypeService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'updates' not in data:
            return jsonify({'error': '请求数据格式错误'}), 400
        
        result = bag_type_service.batch_update_bag_types(data['updates'], current_user_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '批量更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/options', methods=['GET'])
@jwt_required()
@tenant_required
def get_bag_type_options():
    """获取袋型选项数据"""
    try:
        bag_type_service = BagTypeService()
        options = bag_type_service.get_bag_type_options()
        
        return jsonify({
            'success': True,
            'data': options
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/form-options', methods=['GET'])
@jwt_required()
@tenant_required
def get_bag_type_form_options():
    """获取袋型表单选项数据"""
    try:
        bag_type_service = BagTypeService()
        options = bag_type_service.get_form_options()
        
        return jsonify({
            'success': True,
            'data': options
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ================ 袋型结构管理 ================

@bp.route('/<bag_type_id>/structures', methods=['GET'])
@jwt_required()
def get_bag_type_structures(bag_type_id):
    """获取袋型结构列表"""
    try:
        bag_type_service = BagTypeService()
        result = bag_type_service.get_bag_type_structures(bag_type_id)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<bag_type_id>/structures', methods=['POST'])
@jwt_required()
def batch_save_bag_type_structures(bag_type_id):
    """批量保存袋型结构"""
    try:
        bag_type_service = BagTypeService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'structures' not in data:
            return jsonify({'error': '请求数据格式错误'}), 400
        
        result = bag_type_service.batch_update_bag_type_structures(
            bag_type_id, data['structures'], current_user_id
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 