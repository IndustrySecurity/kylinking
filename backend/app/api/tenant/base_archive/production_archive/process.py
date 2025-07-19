# -*- coding: utf-8 -*-
"""
工序管理API
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.api.tenant.routes import tenant_required
from app.services.base_archive.production_archive.process_service import get_process_service

bp = Blueprint('process', __name__)


@bp.route('/', methods=['GET'])
@jwt_required()
@tenant_required
def get_processes():
    """获取工序列表"""
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search', '')
        
        # 获取工序列表
        service = get_process_service()
        result = service.get_processes(
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
def get_enabled_processes():
    """获取启用的工序列表"""
    try:
        service = get_process_service()
        processes = service.get_enabled_processes()
        
        return jsonify({
            'success': True,
            'data': processes
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/<process_id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_process(process_id):
    """获取工序详情"""
    try:
        service = get_process_service()
        process = service.get_process(process_id)
        
        return jsonify({
            'success': True,
            'data': process
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
def create_process():
    """创建工序"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        service = get_process_service()
        process = service.create_process(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': process,
            'message': '工序创建成功'
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


@bp.route('/<process_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_process(process_id):
    """更新工序"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        service = get_process_service()
        process = service.update_process(process_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': process,
            'message': '工序更新成功'
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


@bp.route('/<process_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_process(process_id):
    """删除工序"""
    try:
        service = get_process_service()
        service.delete_process(process_id)
        
        return jsonify({
            'success': True,
            'message': '工序删除成功'
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