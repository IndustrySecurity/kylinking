# -*- coding: utf-8 -*-
"""
班组管理API
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.tenant.routes import tenant_required
from app.services.base_archive.base_data.team_group_service import TeamGroupService
from app.models.user import User
from app.extensions import db
import uuid

bp = Blueprint('team_group', __name__)

@bp.route('/', methods=['GET'])
@jwt_required()
@tenant_required
def get_team_groups():
    """获取班组列表"""
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        search = request.args.get('search', '').strip()
        is_enabled = request.args.get('is_enabled')
        
        # 转换启用状态参数
        if is_enabled is not None:
            is_enabled = is_enabled.lower() == 'true'
        
        # 获取当前用户信息
        current_user_id = get_jwt_identity()
        user = db.session.query(User).get(uuid.UUID(current_user_id))
        
        if not user or not user.tenant_id:
            return jsonify({'error': '用户未关联租户'}), 400
        
        # 创建服务实例
        service = TeamGroupService()    
        
        # 获取班组列表
        result = service.get_team_groups(
            page=page,
            per_page=per_page,
            search=search,
            is_enabled=is_enabled
        )
        
        return jsonify({
            'success': True,
            'data': result.get('team_groups', []),
            'pagination': {
                'page': result.get('page', 1),
                'total': result.get('total', 0),
                'per_page': result.get('per_page', 10),
                'pages': result.get('pages', 1)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"获取班组列表失败: {str(e)}"
        }), 500

@bp.route('/<team_group_id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_team_group(team_group_id):
    """获取班组详情"""
    try:
        # 获取当前用户信息
        current_user_id = get_jwt_identity()
        user = db.session.query(User).get(uuid.UUID(current_user_id))
        
        if not user or not user.tenant_id:
            return jsonify({'error': '用户未关联租户'}), 400
        
        # 创建服务实例
        service = TeamGroupService()
        
        # 获取班组详情
        team_group = service.get_team_group(team_group_id)

        return jsonify({
            'success': True,
            'data': team_group
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"获取班组详情失败: {str(e)}"
        }), 500

@bp.route('/', methods=['POST'])
@jwt_required()
@tenant_required
def create_team_group():
    """创建班组"""
    try:
        # 获取请求数据
        data = request.get_json()
        
        # 获取当前用户ID
        current_user_id = get_jwt_identity()
        user = db.session.query(User).get(uuid.UUID(current_user_id))
        
        if not user or not user.tenant_id:
            return jsonify({'error': '用户未关联租户'}), 400
        
        # 创建服务实例
        service = TeamGroupService()
        
        # 创建班组
        team_group = service.create_team_group(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': team_group,
            'message': '班组创建成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"创建班组失败: {str(e)}"
        }), 500

@bp.route('/<team_group_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_team_group(team_group_id):
    """更新班组"""
    try:
        # 获取请求数据
        data = request.get_json()
        
        # 获取当前用户ID
        current_user_id = get_jwt_identity()
        user = db.session.query(User).get(uuid.UUID(current_user_id))
        
        if not user or not user.tenant_id:
            return jsonify({'error': '用户未关联租户'}), 400
        
        # 创建服务实例
        service = TeamGroupService()
        
        # 更新班组
        team_group = service.update_team_group(team_group_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': team_group,
            'message': '班组更新成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"更新班组失败: {str(e)}"
        }), 500

@bp.route('/<team_group_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_team_group(team_group_id):
    """删除班组"""
    try:
        # 获取当前用户ID
        current_user_id = get_jwt_identity()
        user = db.session.query(User).get(uuid.UUID(current_user_id))
        
        if not user or not user.tenant_id:
            return jsonify({'error': '用户未关联租户'}), 400
        
        # 创建服务实例
        service = TeamGroupService()
        
        # 删除班组
        service.delete_team_group(team_group_id)
        
        return jsonify({
            'success': True,
            'message': '班组删除成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"删除班组失败: {str(e)}"
        }), 500

@bp.route('/form-options', methods=['GET'])
@jwt_required()
@tenant_required
def get_form_options():
    """获取表单选项数据"""
    try:
        # 获取当前用户信息
        current_user_id = get_jwt_identity()
        user = db.session.query(User).get(uuid.UUID(current_user_id))
        
        if not user or not user.tenant_id:
            return jsonify({'error': '用户未关联租户'}), 400
        
        # 创建服务实例
        service = TeamGroupService()
        
        # 获取表单选项
        options = service.get_form_options()
        
        return jsonify({
            'success': True,
            'data': options
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"获取表单选项失败: {str(e)}"
        }), 500 