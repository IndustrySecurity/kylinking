# -*- coding: utf-8 -*-
"""
员工管理API
对应services/base_archive/base_data/employee_service.py
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services.base_archive.base_data.employee_service import EmployeeService
from app.api.tenant.routes import tenant_required

employee_bp = Blueprint('employee', __name__)


@employee_bp.route('/', methods=['GET'])
@jwt_required()
@tenant_required
def get_employees():
    """获取员工列表"""
    try:
        employee_service = EmployeeService()
        # 获取查询参数
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search')
        department_id = request.args.get('department_id')
        position_id = request.args.get('position_id')
        employment_status = request.args.get('employment_status')
        
        # 获取员工列表
        result = employee_service.get_employees(
            page=page,
            per_page=per_page,
            search=search,
            department_id=department_id,
            position_id=position_id,
            employment_status=employment_status
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@employee_bp.route('/<employee_id>', methods=['GET'])
@jwt_required()
def get_employee(employee_id):
    """获取员工详情"""
    try:
        employee_service = EmployeeService()
        employee = employee_service.get_employee(employee_id)
        
        return jsonify({
            'success': True,
            'data': employee
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@employee_bp.route('/', methods=['POST'])
@jwt_required()
def create_employee():
    """创建员工"""
    try:
        employee_service = EmployeeService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 验证必填字段
        if not data.get('employee_name'):
            return jsonify({'error': '员工姓名不能为空'}), 400
        if not data.get('department_id'):
            return jsonify({'error': '部门不能为空'}), 400
        if not data.get('position_id'):
            return jsonify({'error': '职位不能为空'}), 400
        
        employee = employee_service.create_employee(data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': employee,
            'message': '员工创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@employee_bp.route('/<employee_id>', methods=['PUT'])
@jwt_required()
def update_employee(employee_id):
    """更新员工"""
    try:
        employee_service = EmployeeService()
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        employee = employee_service.update_employee(employee_id, data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': employee,
            'message': '员工更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@employee_bp.route('/<employee_id>', methods=['DELETE'])
@jwt_required()
def delete_employee(employee_id):
    """删除员工"""
    try:
        employee_service = EmployeeService()
        employee_service.delete_employee(employee_id)
        
        return jsonify({
            'success': True,
            'message': '员工删除成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ================ 选项数据API ================

@employee_bp.route('/employment-status-options', methods=['GET'])
@jwt_required()
def get_employment_status_options():
    """获取在职状态选项"""
    try:
        options = [
            {'value': 'active', 'label': '在职'},
            {'value': 'probation', 'label': '试用期'},
            {'value': 'resigned', 'label': '离职'},
            {'value': 'suspended', 'label': '停职'}
        ]
        
        return jsonify({
            'success': True,
            'data': options
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@employee_bp.route('/gender-options', methods=['GET'])
@jwt_required()
def get_gender_options():
    """获取性别选项"""
    try:
        options = [
            {'value': 'male', 'label': '男'},
            {'value': 'female', 'label': '女'}
        ]
        
        return jsonify({
            'success': True,
            'data': options
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@employee_bp.route('/business-type-options', methods=['GET'])
@jwt_required()
def get_business_type_options():
    """获取业务类型选项"""
    try:
        options = [
            {'value': 'production', 'label': '生产'},
            {'value': 'sales', 'label': '销售'},
            {'value': 'management', 'label': '管理'},
            {'value': 'support', 'label': '支持'}
        ]
        
        return jsonify({
            'success': True,
            'data': options
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@employee_bp.route('/evaluation-level-options', methods=['GET'])
@jwt_required()
def get_evaluation_level_options():
    """获取评量流程级别选项"""
    try:
        options = [
            {'value': 'finance', 'label': '财务'},
            {'value': 'technology', 'label': '工艺'},
            {'value': 'supply', 'label': '供应'},
            {'value': 'marketing', 'label': '营销'}
        ]
        
        return jsonify({
            'success': True,
            'data': options
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@employee_bp.route('/options', methods=['GET'])
@jwt_required()
def get_employee_options():
    """获取员工选项数据"""
    try:
        employee_service = EmployeeService()
        department_id = request.args.get('department_id')
        position_id = request.args.get('position_id')
        
        options = employee_service.get_employee_options(
            department_id=department_id,
            position_id=position_id
        )
        
        return jsonify({
            'success': True,
            'data': options
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@employee_bp.route('/form-options', methods=['GET'])
@jwt_required()
def get_employee_form_options():
    """获取员工表单选项数据"""
    try:
        employee_service = EmployeeService()
        options = employee_service.get_form_options()
        
        return jsonify({
            'success': True,
            'data': options
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@employee_bp.route('/init-data', methods=['POST'])
@jwt_required()
@tenant_required
def init_employee_data():
    """初始化员工测试数据"""
    try:
        service = EmployeeService()
        current_user_id = get_jwt_identity()
        
        # 检查是否已有员工数据
        existing_result = service.get_employees(page=1, per_page=5)
        if existing_result['total'] > 0:
            return jsonify({
                'success': True,
                'message': f'已存在 {existing_result["total"]} 个员工记录，无需初始化',
                'data': existing_result
            })
        
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'初始化员工数据失败: {str(e)}'
        }), 500

# 为统一导入方式提供别名
bp = employee_bp 