# -*- coding: utf-8 -*-
"""
付款方式管理API路由
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services.base_archive.financial_management.payment_method_service import PaymentMethodService

bp = Blueprint('payment_method', __name__)


@bp.route('/', methods=['GET'])
@jwt_required()
def get_payment_methods():
    """获取付款方式列表"""
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search')
        
        # 获取付款方式列表
        service = PaymentMethodService()
        result = service.get_payment_methods(
            page=page,
            per_page=per_page,
            search=search
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/enabled', methods=['GET'])
@jwt_required()
def get_enabled_payment_methods():
    """获取启用的付款方式列表"""
    try:
        service = PaymentMethodService()
        payment_methods = service.get_enabled_payment_methods()
        
        return jsonify({
            'success': True,
            'data': payment_methods
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<payment_method_id>', methods=['GET'])
@jwt_required()
def get_payment_method(payment_method_id):
    """获取付款方式详情"""
    try:
        service = PaymentMethodService()
        payment_method = service.get_payment_method(payment_method_id)
        
        return jsonify({
            'success': True,
            'data': payment_method
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/', methods=['POST'])
@jwt_required()
def create_payment_method():
    """创建付款方式"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        if not data.get('payment_name'):
            return jsonify({'error': '付款方式名称不能为空'}), 400
        
        service = PaymentMethodService()
        payment_method = service.create_payment_method(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': payment_method,
            'message': '付款方式创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<payment_method_id>', methods=['PUT'])
@jwt_required()
def update_payment_method(payment_method_id):
    """更新付款方式"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        service = PaymentMethodService()
        payment_method = service.update_payment_method(payment_method_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': payment_method,
            'message': '付款方式更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<payment_method_id>', methods=['DELETE'])
@jwt_required()
def delete_payment_method(payment_method_id):
    """删除付款方式"""
    try:
        service = PaymentMethodService()
        service.delete_payment_method(payment_method_id)
        
        return jsonify({
            'success': True,
            'message': '付款方式删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/batch', methods=['PUT'])
@jwt_required()
def batch_update_payment_methods():
    """批量更新付款方式"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'data' not in data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        service = PaymentMethodService()
        results = service.batch_update_payment_methods(data['data'], current_user_id)
        
        return jsonify({
            'success': True,
            'data': results,
            'message': '批量更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500 