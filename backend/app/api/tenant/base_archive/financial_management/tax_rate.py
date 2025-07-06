# -*- coding: utf-8 -*-
"""
税率管理API路由
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.utils.decorators import tenant_required
from app.utils.tenant_context import tenant_context_required
from app.services.base_archive.financial_management.tax_rate_service import get_tax_rate_service

bp = Blueprint('tax_rate', __name__)


@bp.route('/', methods=['GET'])
@bp.route('', methods=['GET'])
@jwt_required()
@tenant_required
@tenant_context_required
def get_tax_rates():
    """获取税率列表"""
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search', '')
        
        # 获取税率服务
        service = get_tax_rate_service()
        result = service.get_tax_rates(
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
@tenant_context_required
def get_enabled_tax_rates():
    """获取启用的税率列表"""
    try:
        service = get_tax_rate_service()
        tax_rates = service.get_enabled_tax_rates()
        
        return jsonify({
            'success': True,
            'data': tax_rates
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/<tax_rate_id>', methods=['GET'])
@jwt_required()
@tenant_required
@tenant_context_required
def get_tax_rate(tax_rate_id):
    """获取税率详情"""
    try:
        service = get_tax_rate_service()
        tax_rate = service.get_tax_rate(tax_rate_id)
        
        return jsonify({
            'success': True,
            'data': tax_rate
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/', methods=['POST'])
@bp.route('', methods=['POST'])
@jwt_required()
@tenant_required
@tenant_context_required
def create_tax_rate():
    """创建税率"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        service = get_tax_rate_service()
        tax_rate = service.create_tax_rate(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': tax_rate,
            'message': '税率创建成功'
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


@bp.route('/<tax_rate_id>', methods=['PUT'])
@jwt_required()
@tenant_required
@tenant_context_required
def update_tax_rate(tax_rate_id):
    """更新税率"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        service = get_tax_rate_service()
        tax_rate = service.update_tax_rate(tax_rate_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': tax_rate,
            'message': '税率更新成功'
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


@bp.route('/<tax_rate_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
@tenant_context_required
def delete_tax_rate(tax_rate_id):
    """删除税率"""
    try:
        service = get_tax_rate_service()
        service.delete_tax_rate(tax_rate_id)
        
        return jsonify({
            'success': True,
            'message': '税率删除成功'
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


@bp.route('/options', methods=['GET'])
@jwt_required()
@tenant_required
@tenant_context_required
def get_tax_rate_options():
    """获取税率选项"""
    try:
        service = get_tax_rate_service()
        
        # 获取启用的税率列表
        tax_rates = service.get_enabled_tax_rates()
        
        # 转换为选项格式
        options = []
        if tax_rates:
            for tax_rate in tax_rates:
                rate_value = tax_rate.get('tax_rate', 0)
                options.append({
                    'value': str(tax_rate['id']),
                    'label': f"{tax_rate['tax_name']} ({rate_value}%)",
                    'tax_name': tax_rate['tax_name'],
                    'rate': float(rate_value),
                    'tax_rate': float(rate_value),
                    'description': tax_rate.get('description', ''),
                    'tax_code': tax_rate.get('tax_code', '')
                })
        
        # 如果没有数据，返回默认税率
        if not options:
            options = [
                {'value': '1', 'label': 'mock增值税13%', 'rate': 0.13},
                {'value': '2', 'label': 'mock增值税9%', 'rate': 0.09},
                {'value': '3', 'label': 'mock增值税6%', 'rate': 0.06},
                {'value': '4', 'label': 'mock增值税3%', 'rate': 0.03},
                {'value': '5', 'label': 'mock免税0%', 'rate': 0.00}
            ]
        
        return jsonify({
            'success': True,
            'data': options
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 