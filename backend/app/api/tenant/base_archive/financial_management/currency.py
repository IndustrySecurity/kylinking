# -*- coding: utf-8 -*-
"""
币别管理API路由
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.api.tenant.routes import tenant_required
from app.services.base_archive.financial_management.currency_service import get_currency_service

bp = Blueprint('currency', __name__)


@bp.route('/', methods=['GET'])
@jwt_required()
@tenant_required
def get_currencies():
    """获取币别列表"""
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search', '')
        
        # 获取币别列表
        service = get_currency_service()
        result = service.get_currencies(
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
def get_enabled_currencies():
    """获取启用的币别列表"""
    try:
        service = get_currency_service()
        currencies = service.get_enabled_currencies()
        
        return jsonify({
            'success': True,
            'data': {
                'currencies': currencies
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/<currency_id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_currency(currency_id):
    """获取币别详情"""
    try:
        service = get_currency_service()
        currency = service.get_currency(currency_id)
        
        return jsonify({
            'success': True,
            'data': currency
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
def create_currency():
    """创建币别"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        service = get_currency_service()
        currency = service.create_currency(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': currency,
            'message': '币别创建成功'
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


@bp.route('/<currency_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_currency(currency_id):
    """更新币别"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        service = get_currency_service()
        currency = service.update_currency(currency_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': currency,
            'message': '币别更新成功'
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


@bp.route('/<currency_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_currency(currency_id):
    """删除币别"""
    try:
        service = get_currency_service()
        service.delete_currency(currency_id)
        
        return jsonify({
            'success': True,
            'message': '币别删除成功'
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


@bp.route('/<currency_id>/set-base', methods=['POST'])
@jwt_required()
@tenant_required
def set_base_currency(currency_id):
    """设置基础币别"""
    try:
        current_user_id = get_jwt_identity()
        
        service = get_currency_service()
        currency = service.set_base_currency(currency_id, current_user_id)
        
        return jsonify({
            'success': True,
            'data': currency,
            'message': '基础币别设置成功'
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


@bp.route('/batch', methods=['PUT'])
@jwt_required()
@tenant_required
def batch_update_currencies():
    """批量更新币别"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not isinstance(data, list):
            return jsonify({
                'success': False,
                'message': '请求数据格式错误'
            }), 400
        
        service = get_currency_service()
        results = service.batch_update_currencies(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': results,
            'message': '批量更新成功'
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