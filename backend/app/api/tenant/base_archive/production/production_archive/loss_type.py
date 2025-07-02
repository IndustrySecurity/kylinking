# -*- coding: utf-8 -*-
"""
损耗类型管理API路由
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services.base_archive.production.production_archive.loss_type_service import LossTypeService

bp = Blueprint('loss_type', __name__)


@bp.route('/', methods=['GET'])
@jwt_required()
def get_loss_types():
    """获取损耗类型列表"""
    try:
        loss_type_service = LossTypeService()
        # 获取查询参数
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search')
        enabled_only = request.args.get('enabled_only', 'false').lower() == 'true'
        
        # 获取损耗类型列表
        result = loss_type_service.get_loss_types(
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


@bp.route('/enabled', methods=['GET'])
@jwt_required()
def get_enabled_loss_types():
    """获取启用的损耗类型列表"""
    try:
        loss_type_service = LossTypeService()
        result = loss_type_service.get_enabled_loss_types()
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<loss_type_id>', methods=['GET'])
@jwt_required()
def get_loss_type(loss_type_id):
    """获取损耗类型详情"""
    try:
        loss_type_service = LossTypeService()
        loss_type = loss_type_service.get_loss_type(loss_type_id)
        
        return jsonify({
            'success': True,
            'data': loss_type
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/', methods=['POST'])
@jwt_required()
def create_loss_type():
    """创建损耗类型"""
    try:
        loss_type_service = LossTypeService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        if not data.get('loss_type_name'):
            return jsonify({'error': '损耗类型名称不能为空'}), 400
        
        loss_type = loss_type_service.create_loss_type(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': loss_type,
            'message': '损耗类型创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<loss_type_id>', methods=['PUT'])
@jwt_required()
def update_loss_type(loss_type_id):
    """更新损耗类型"""
    try:
        loss_type_service = LossTypeService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        loss_type = loss_type_service.update_loss_type(loss_type_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': loss_type,
            'message': '损耗类型更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<loss_type_id>', methods=['DELETE'])
@jwt_required()
def delete_loss_type(loss_type_id):
    """删除损耗类型"""
    try:
        loss_type_service = LossTypeService()
        loss_type_service.delete_loss_type(loss_type_id)
        
        return jsonify({
            'success': True,
            'message': '损耗类型删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/batch', methods=['PUT'])
@jwt_required()
def batch_update_loss_types():
    """批量更新损耗类型"""
    try:
        loss_type_service = LossTypeService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'data' not in data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        results = loss_type_service.batch_update_loss_types(data['data'], current_user_id)
        
        return jsonify({
            'success': True,
            'data': results,
            'message': '批量更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500 