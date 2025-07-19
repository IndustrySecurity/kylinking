# -*- coding: utf-8 -*-
"""
色卡管理API路由
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services.base_archive.production_archive.color_card_service import ColorCardService

bp = Blueprint('color_card', __name__)


@bp.route('/', methods=['GET'])
@jwt_required()
def get_color_cards():
    """获取色卡列表"""
    try:
        color_card_service = ColorCardService()
        # 获取查询参数
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search')
        enabled_only = request.args.get('enabled_only', 'false').lower() == 'true'
        
        # 获取色卡列表
        result = color_card_service.get_color_cards(
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


@bp.route('/<color_card_id>', methods=['GET'])
@jwt_required()
def get_color_card(color_card_id):
    """获取色卡详情"""
    try:
        color_card_service = ColorCardService()
        color_card = color_card_service.get_color_card(color_card_id)
        
        return jsonify({
            'success': True,
            'data': color_card
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/', methods=['POST'])
@jwt_required()
def create_color_card():
    """创建色卡"""
    try:
        color_card_service = ColorCardService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        if not data.get('color_name'):
            return jsonify({'error': '色卡名称不能为空'}), 400
        
        color_card = color_card_service.create_color_card(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': color_card,
            'message': '色卡创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<color_card_id>', methods=['PUT'])
@jwt_required()
def update_color_card(color_card_id):
    """更新色卡"""
    try:
        color_card_service = ColorCardService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        color_card = color_card_service.update_color_card(color_card_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': color_card,
            'message': '色卡更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<color_card_id>', methods=['DELETE'])
@jwt_required()
def delete_color_card(color_card_id):
    """删除色卡"""
    try:
        color_card_service = ColorCardService()
        color_card_service.delete_color_card(color_card_id)
        
        return jsonify({
            'success': True,
            'message': '色卡删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/batch', methods=['PUT'])
@jwt_required()
def batch_update_color_cards():
    """批量更新色卡"""
    try:
        color_card_service = ColorCardService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'data' not in data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        results = color_card_service.batch_update_color_cards(data['data'], current_user_id)
        
        return jsonify({
            'success': True,
            'data': results,
            'message': '批量更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500 