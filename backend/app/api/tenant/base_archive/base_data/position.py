# -*- coding: utf-8 -*-
"""
职位管理API路由
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services.base_archive.base_data.position_service import PositionService
from app.api.tenant.routes import tenant_required

position_bp = Blueprint('position', __name__)

# 为统一导入方式提供别名
bp = position_bp


@position_bp.route('/', methods=['GET'])
@jwt_required()
@tenant_required
def get_positions():
    """获取职位列表"""
    try:
        position_service = PositionService()
        # 获取查询参数
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search')
        department_id = request.args.get('department_id')
        
        # 获取当前用户和租户信息
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        if not tenant_id:
            return jsonify({'error': '租户信息缺失'}), 400
        
        # 获取职位列表
        result = position_service.get_positions(
            page=page,
            per_page=per_page,
            search=search,
            department_id=department_id
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<position_id>', methods=['GET'])
@jwt_required()
def get_position(position_id):
    """获取职位详情"""
    try:
        position_service = PositionService()
        position = position_service.get_position(position_id)
        
        return jsonify({
            'success': True,
            'data': position
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/', methods=['POST'])
@jwt_required()
def create_position():
    """创建职位"""
    try:
        position_service = PositionService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        if not data.get('position_name'):
            return jsonify({'error': '职位名称不能为空'}), 400
        if not data.get('department_id'):
            return jsonify({'error': '部门不能为空'}), 400
        
        position = position_service.create_position(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': position,
            'message': '职位创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<position_id>', methods=['PUT'])
@jwt_required()
def update_position(position_id):
    """更新职位"""
    try:
        position_service = PositionService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        position = position_service.update_position(position_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': position,
            'message': '职位更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<position_id>', methods=['DELETE'])
@jwt_required()
def delete_position(position_id):
    """删除职位"""
    try:
        position_service = PositionService()
        position_service.delete_position(position_id)
        
        return jsonify({
            'success': True,
            'message': '职位删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/options', methods=['GET'])
@jwt_required()
@tenant_required
def get_position_options():
    """获取职位选项数据"""
    try:
        position_service = PositionService()
        department_id = request.args.get('department_id')
        options = position_service.get_position_options(department_id)
        
        return jsonify({
            'success': True,
            'data': {
                'positions': options
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/form-options', methods=['GET'])
@jwt_required()
@tenant_required
def get_position_form_options():
    """获取职位表单选项数据"""
    try:
        position_service = PositionService()
        options = position_service.get_form_options()
        
        return jsonify({
            'success': True,
            'data': options
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/parent-options', methods=['GET'])
@jwt_required()
@tenant_required
def get_parent_position_options():
    """获取上级职位选项"""
    try:
        position_service = PositionService()
        department_id = request.args.get('department_id')
        current_position_id = request.args.get('current_position_id')  # 排除当前职位
        
        options = position_service.get_parent_position_options(department_id, current_position_id)
        
        return jsonify({
            'success': True,
            'data': options
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500 