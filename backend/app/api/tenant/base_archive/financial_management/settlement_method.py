# -*- coding: utf-8 -*-
"""
结算方式管理API路由
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services.base_archive.financial_management.settlement_method_service import SettlementMethodService

bp = Blueprint('settlement_method', __name__)


@bp.route('/', methods=['GET'])
@jwt_required()
def get_settlement_methods():
    """获取结算方式列表"""
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search')
        
        # 获取结算方式列表
        service = SettlementMethodService()
        result = service.get_settlement_methods(
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
def get_enabled_settlement_methods():
    """获取启用的结算方式列表"""
    try:
        service = SettlementMethodService()
        settlement_methods = service.get_enabled_settlement_methods()
        
        return jsonify({
            'success': True,
            'data': settlement_methods
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<settlement_method_id>', methods=['GET'])
@jwt_required()
def get_settlement_method(settlement_method_id):
    """获取结算方式详情"""
    try:
        service = SettlementMethodService()
        settlement_method = service.get_settlement_method(settlement_method_id)
        
        return jsonify({
            'success': True,
            'data': settlement_method
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/', methods=['POST'])
@jwt_required()
def create_settlement_method():
    """创建结算方式"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        if not data.get('settlement_name'):
            return jsonify({'error': '结算方式名称不能为空'}), 400
        
        service = SettlementMethodService()
        settlement_method = service.create_settlement_method(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': settlement_method,
            'message': '结算方式创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<settlement_method_id>', methods=['PUT'])
@jwt_required()
def update_settlement_method(settlement_method_id):
    """更新结算方式"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        service = SettlementMethodService()
        settlement_method = service.update_settlement_method(settlement_method_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': settlement_method,
            'message': '结算方式更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<settlement_method_id>', methods=['DELETE'])
@jwt_required()
def delete_settlement_method(settlement_method_id):
    """删除结算方式"""
    try:
        service = SettlementMethodService()
        service.delete_settlement_method(settlement_method_id)
        
        return jsonify({
            'success': True,
            'message': '结算方式删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/batch', methods=['PUT'])
@jwt_required()
def batch_update_settlement_methods():
    """批量更新结算方式"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'data' not in data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        service = SettlementMethodService()
        results = service.batch_update_settlement_methods(data['data'], current_user_id)
        
        return jsonify({
            'success': True,
            'data': results,
            'message': '批量更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500 