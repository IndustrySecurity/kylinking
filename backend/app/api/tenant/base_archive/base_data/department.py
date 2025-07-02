# -*- coding: utf-8 -*-
"""
部门管理API
对应services/base_archive/base_data/department_service.py
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services.base_archive.base_data.department_service import DepartmentService
from app.api.tenant.routes import tenant_required

department_bp = Blueprint('department', __name__)

# 为统一导入方式提供别名
bp = department_bp


@department_bp.route('/', methods=['GET'])
@jwt_required()
@tenant_required
def get_departments():
    """获取部门列表"""
    try:
        department_service = DepartmentService()
        # 获取查询参数
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search')
        
        # 获取当前用户和租户信息
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        if not tenant_id:
            return jsonify({'error': '租户信息缺失'}), 400
        
        # 获取部门列表
        result = department_service.get_departments(
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


@department_bp.route('/<department_id>', methods=['GET'])
@jwt_required()
def get_department(department_id):
    """获取部门详情"""
    try:
        department_service = DepartmentService()
        department = department_service.get_department(department_id)
        
        return jsonify({
            'success': True,
            'data': department
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@department_bp.route('/', methods=['POST'])
@jwt_required()
def create_department():
    """创建部门"""
    try:
        department_service = DepartmentService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        if not data.get('dept_name'):
            return jsonify({'error': '部门名称不能为空'}), 400
        
        department = department_service.create_department(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': department,
            'message': '部门创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@department_bp.route('/<department_id>', methods=['PUT'])
@jwt_required()
def update_department(department_id):
    """更新部门"""
    try:
        department_service = DepartmentService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        department = department_service.update_department(department_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': department,
            'message': '部门更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@department_bp.route('/<department_id>', methods=['DELETE'])
@jwt_required()
def delete_department(department_id):
    """删除部门"""
    try:
        department_service = DepartmentService()
        department_service.delete_department(department_id)
        
        return jsonify({
            'success': True,
            'message': '部门删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@department_bp.route('/options', methods=['GET'])
@jwt_required()
def get_department_options():
    """获取部门选项数据"""
    try:
        department_service = DepartmentService()
        options = department_service.get_department_options()
        
        return jsonify({
            'success': True,
            'data': options
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@department_bp.route('/tree', methods=['GET'])
@jwt_required()
def get_department_tree():
    """获取部门树形结构"""
    try:
        department_service = DepartmentService()
        tree = department_service.get_department_tree()
        
        return jsonify({
            'success': True,
            'data': tree
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 