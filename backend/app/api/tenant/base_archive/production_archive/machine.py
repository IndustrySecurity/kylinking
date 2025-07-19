# -*- coding: utf-8 -*-
"""
机台管理API
对应services/base_archive/production/production_archive/machine_service.py
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.tenant.routes import tenant_required
from app.services.base_archive.production_archive.machine_service import MachineService

machine_bp = Blueprint('machine', __name__)

# 设置别名以便注册路由时使用
bp = machine_bp


@machine_bp.route('/', methods=['GET'])
@jwt_required()
@tenant_required
def get_machines():
    """获取机台列表"""
    try:
        machine_service = MachineService()
        # 获取查询参数
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search')
        enabled_only = request.args.get('enabled_only', 'false').lower() == 'true'
        
        # 获取机台列表
        result = machine_service.get_machines(
            page=page,
            per_page=per_page,
            search=search,
            enabled_only=enabled_only
        )
        
        return jsonify({
            'success': True,
            'data': {
                'machines': result['items'],
                'total': result['total'],
                'current_page': result['current_page'],
                'per_page': result['per_page'],
                'has_next': result['has_next'],
                'has_prev': result['has_prev']
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@machine_bp.route('/<machine_id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_machine(machine_id):
    """获取机台详情"""
    try:
        machine_service = MachineService()
        machine = machine_service.get_machine(machine_id)
        
        if not machine:
            return jsonify({'error': '机台不存在'}), 404
        
        return jsonify({
            'success': True,
            'data': machine
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@machine_bp.route('/', methods=['POST'])
@jwt_required()
@tenant_required
def create_machine():
    """创建机台"""
    try:
        machine_service = MachineService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        if not data.get('machine_name'):
            return jsonify({'error': '机台名称不能为空'}), 400
        
        machine = machine_service.create_machine(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': machine,
            'message': '机台创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@machine_bp.route('/<machine_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_machine(machine_id):
    """更新机台"""
    try:
        machine_service = MachineService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        machine = machine_service.update_machine(machine_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': machine,
            'message': '机台更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@machine_bp.route('/<machine_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_machine(machine_id):
    """删除机台"""
    try:
        machine_service = MachineService()
        machine_service.delete_machine(machine_id)
        
        return jsonify({
            'success': True,
            'message': '机台删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@machine_bp.route('/batch', methods=['PUT'])
@jwt_required()
@tenant_required
def batch_update_machines():
    """批量更新机台"""
    try:
        machine_service = MachineService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not isinstance(data, list):
            return jsonify({'error': '请求数据格式错误'}), 400
        
        machines = machine_service.batch_update_machines(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': machines,
            'message': '批量更新成功'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@machine_bp.route('/enabled', methods=['GET'])
@jwt_required()
@tenant_required
def get_enabled_machines():
    """获取启用的机台列表"""
    try:
        machine_service = MachineService()
        machines = machine_service.get_enabled_machines()
        
        return jsonify({
            'success': True,
            'data': machines
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@machine_bp.route('/next-code', methods=['GET'])
@jwt_required()
@tenant_required
def get_next_machine_code():
    """获取下一个机台编号"""
    try:
        from app.models.basic_data import Machine
        next_code = Machine.generate_machine_code()
        
        return jsonify({
            'success': True,
            'data': {
                'next_code': next_code
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 