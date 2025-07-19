# -*- coding: utf-8 -*-
"""
送货方式管理API路由
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services.base_archive.production_archive.delivery_method_service import DeliveryMethodService

bp = Blueprint('delivery_method', __name__)


@bp.route('/', methods=['GET'])
@jwt_required()
def get_delivery_methods():
    """获取送货方式列表"""
    try:
        delivery_method_service = DeliveryMethodService()
        # 获取查询参数
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search')
        enabled_only = request.args.get('enabled_only', 'false').lower() == 'true'
        
        # 获取送货方式列表
        result = delivery_method_service.get_delivery_methods(
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


@bp.route('/<delivery_method_id>', methods=['GET'])
@jwt_required()
def get_delivery_method(delivery_method_id):
    """获取送货方式详情"""
    try:
        delivery_method_service = DeliveryMethodService()
        delivery_method = delivery_method_service.get_delivery_method(delivery_method_id)
        
        return jsonify({
            'success': True,
            'data': delivery_method
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/', methods=['POST'])
@jwt_required()
def create_delivery_method():
    """创建送货方式"""
    try:
        delivery_method_service = DeliveryMethodService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        if not data.get('method_name'):
            return jsonify({'error': '送货方式名称不能为空'}), 400
        
        delivery_method = delivery_method_service.create_delivery_method(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': delivery_method,
            'message': '送货方式创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<delivery_method_id>', methods=['PUT'])
@jwt_required()
def update_delivery_method(delivery_method_id):
    """更新送货方式"""
    try:
        delivery_method_service = DeliveryMethodService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        delivery_method = delivery_method_service.update_delivery_method(delivery_method_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': delivery_method,
            'message': '送货方式更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<delivery_method_id>', methods=['DELETE'])
@jwt_required()
def delete_delivery_method(delivery_method_id):
    """删除送货方式"""
    try:
        delivery_method_service = DeliveryMethodService()
        delivery_method_service.delete_delivery_method(delivery_method_id)
        
        return jsonify({
            'success': True,
            'message': '送货方式删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/batch', methods=['PUT'])
@jwt_required()
def batch_update_delivery_methods():
    """批量更新送货方式"""
    try:
        delivery_method_service = DeliveryMethodService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'data' not in data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        results = delivery_method_service.batch_update_delivery_methods(data['data'], current_user_id)
        
        return jsonify({
            'success': True,
            'data': results,
            'message': '批量更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500 