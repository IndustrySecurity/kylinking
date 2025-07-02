# -*- coding: utf-8 -*-
"""
账户管理API路由
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.api.tenant.routes import tenant_required
from app.services.base_archive.financial_management.account_service import get_account_service

bp = Blueprint('account_management', __name__)


@bp.route('/', methods=['GET'])
@jwt_required()
@tenant_required
def get_accounts():
    """获取账户列表"""
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search', '')
        account_type = request.args.get('account_type', '')
        
        # 获取账户列表
        service = get_account_service()
        result = service.get_accounts(
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


@bp.route('/enabled', methods=['GET'])
@jwt_required()
@tenant_required
def get_enabled_accounts():
    """获取启用的账户列表"""
    try:
        service = get_account_service()
        accounts = service.get_enabled_accounts()
        
        return jsonify({
            'success': True,
            'data': accounts
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/<account_id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_account(account_id):
    """获取账户详情"""
    try:
        service = get_account_service()
        account = service.get_account(account_id)
        
        return jsonify({
            'success': True,
            'data': account
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/', methods=['POST'])
@jwt_required()
@tenant_required
def create_account():
    """创建账户"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        service = get_account_service()
        account = service.create_account(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': account,
            'message': '账户创建成功'
        }), 201
        
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


@bp.route('/<account_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_account(account_id):
    """更新账户"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        service = get_account_service()
        account = service.update_account(account_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': account,
            'message': '账户更新成功'
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


@bp.route('/<account_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_account(account_id):
    """删除账户"""
    try:
        service = get_account_service()
        service.delete_account(account_id)
        
        return jsonify({
            'success': True,
            'message': '账户删除成功'
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


@bp.route('/form-options', methods=['GET'])
@jwt_required()
@tenant_required
def get_account_form_options():
    """获取账户表单选项"""
    try:
        service = get_account_service()
        options = service.get_form_options()
        
        return jsonify({
            'success': True,
            'data': options
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500 