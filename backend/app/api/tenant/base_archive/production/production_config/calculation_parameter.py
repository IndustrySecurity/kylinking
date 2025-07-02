# -*- coding: utf-8 -*-
"""
计算参数管理API
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.tenant.routes import tenant_required
from app.services.base_archive.production.production_config.calculation_parameter_service import get_calculation_parameter_service

bp = Blueprint('calculation_parameter', __name__)

@bp.route('/', methods=['GET'])
@jwt_required()
@tenant_required
def get_calculation_parameters():
    """获取计算参数列表"""
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        search = request.args.get('search', '')
        
        service = get_calculation_parameter_service()
        result = service.get_calculation_parameters(page=page, per_page=page_size, search=search)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/', methods=['POST'])
@jwt_required()
@tenant_required
def create_calculation_parameter():
    """创建计算参数"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        user_id = get_jwt_identity()
        service = get_calculation_parameter_service()
        result = service.create_calculation_parameter(data, user_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '计算参数创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<parameter_id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_calculation_parameter(parameter_id):
    """获取计算参数详情"""
    try:
        service = get_calculation_parameter_service()
        result = service.get_calculation_parameter(parameter_id)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<parameter_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_calculation_parameter(parameter_id):
    """更新计算参数"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        user_id = get_jwt_identity()
        service = get_calculation_parameter_service()
        result = service.update_calculation_parameter(parameter_id, data, user_id)
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '计算参数更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<parameter_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_calculation_parameter(parameter_id):
    """删除计算参数"""
    try:
        service = get_calculation_parameter_service()
        service.delete_calculation_parameter(parameter_id)
        
        return jsonify({
            'success': True,
            'message': '计算参数删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/options', methods=['GET'])
@jwt_required()
@tenant_required
def get_calculation_parameter_options():
    """获取计算参数选项"""
    try:
        service = get_calculation_parameter_service()
        result = service.get_calculation_parameter_options()
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 