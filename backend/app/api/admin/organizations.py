# -*- coding: utf-8 -*-
"""
组织管理API路由
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.admin.routes import admin_required
from app.services.system.organization_service import get_organization_service
import uuid

bp = Blueprint('admin_organizations', __name__)


@bp.route('/tenants/<uuid:tenant_id>/organizations', methods=['GET'])
@admin_required
def get_tenant_organizations(tenant_id):
    """获取租户的组织列表"""
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search', '')
        
        # 获取组织服务
        service = get_organization_service()
        result = service.get_organizations(
            tenant_id=str(tenant_id),
            page=page,
            per_page=per_page,
            search=search
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/tenants/<uuid:tenant_id>/organizations/tree', methods=['GET'])
@admin_required
def get_tenant_organization_tree(tenant_id):
    """获取租户的组织树结构"""
    try:
        # 获取组织服务
        service = get_organization_service()
        tree_data = service.get_organization_tree(tenant_id=str(tenant_id))
        
        return jsonify({
            'success': True,
            'data': {
                'organizations': tree_data
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/tenants/<uuid:tenant_id>/organizations', methods=['POST'])
@admin_required
def create_tenant_organization(tenant_id):
    """创建租户组织"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['name', 'code']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'字段 {field} 是必填的'
                }), 400
        
        # 获取组织服务
        service = get_organization_service()
        result = service.create_organization(
            tenant_id=str(tenant_id),
            data=data,
            created_by=current_user_id
        )
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '组织创建成功'
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/tenants/<uuid:tenant_id>/organizations/<uuid:org_id>', methods=['PUT'])
@admin_required
def update_tenant_organization(tenant_id, org_id):
    """更新租户组织"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # 获取组织服务
        service = get_organization_service()
        result = service.update_organization(
            tenant_id=str(tenant_id),
            org_id=str(org_id),
            data=data,
            updated_by=current_user_id
        )
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '组织更新成功'
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/tenants/<uuid:tenant_id>/organizations/<uuid:org_id>', methods=['DELETE'])
@admin_required
def delete_tenant_organization(tenant_id, org_id):
    """删除租户组织"""
    try:
        # 获取组织服务
        service = get_organization_service()
        service.delete_organization(
            tenant_id=str(tenant_id),
            org_id=str(org_id)
        )
        
        return jsonify({
            'success': True,
            'message': '组织删除成功'
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/tenants/<uuid:tenant_id>/organizations/<uuid:org_id>/users', methods=['POST'])
@admin_required
def assign_users_to_organization(tenant_id, org_id):
    """分配用户到组织"""
    try:
        data = request.get_json()
        user_ids = data.get('user_ids', [])
        
        if not user_ids:
            return jsonify({
                'success': False,
                'message': '用户ID列表不能为空'
            }), 400
        
        # 获取组织服务
        service = get_organization_service()
        service.assign_users_to_organization(
            tenant_id=str(tenant_id),
            org_id=str(org_id),
            user_ids=user_ids
        )
        
        return jsonify({
            'success': True,
            'message': '用户分配成功'
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500 