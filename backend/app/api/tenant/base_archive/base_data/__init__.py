# -*- coding: utf-8 -*-
"""
基础数据模块API
包含客户、供应商、产品、材料、部门、员工等基础数据管理功能
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

# 创建基础数据模块主蓝图
base_data_bp = Blueprint('base_data', __name__)

# ==================== 组织架构 ====================
from .customer import bp as customer_bp
from .supplier import bp as supplier_bp  
from .department import bp as department_bp
from .position import bp as position_bp
from .employee import bp as employee_bp

# ==================== 产品物料 ====================
from .product_management import bp as product_management_bp
from .material_management import bp as material_management_bp

# ==================== 生产管理 ====================
from .team_group import bp as team_group_bp

# 注册各个API蓝图
base_data_bp.register_blueprint(customer_bp, url_prefix='/customers')
base_data_bp.register_blueprint(supplier_bp, url_prefix='/suppliers')
base_data_bp.register_blueprint(department_bp, url_prefix='/departments')
base_data_bp.register_blueprint(position_bp, url_prefix='/positions')
base_data_bp.register_blueprint(employee_bp, url_prefix='/employees')
base_data_bp.register_blueprint(product_management_bp, url_prefix='/product-management')
base_data_bp.register_blueprint(material_management_bp, url_prefix='/material-management')
base_data_bp.register_blueprint(team_group_bp, url_prefix='/team-group')

# 为了兼容现有前端路径，添加别名（使用不同的name避免重复）
base_data_bp.register_blueprint(customer_bp, url_prefix='/customer-management', name='customer_management_alias')
base_data_bp.register_blueprint(supplier_bp, url_prefix='/supplier-management', name='supplier_management_alias')
# 恢复products别名路由，因为前端主要使用这个路径
base_data_bp.register_blueprint(product_management_bp, url_prefix='/products', name='products_alias')
base_data_bp.register_blueprint(material_management_bp, url_prefix='/materials', name='materials_alias')
base_data_bp.register_blueprint(team_group_bp, url_prefix='/team-groups', name='team_groups_alias')

# 添加设备管理API
@base_data_bp.route('/machines', methods=['GET'])
def get_machines():
    """获取设备列表 - 模拟数据"""
    try:
        # 模拟设备数据
        machines = [
            {
                'id': '1',
                'machine_code': 'M001',
                'machine_name': '注塑机A',
                'machine_type': '注塑机',
                'specification': '500T',
                'manufacturer': '海天',
                'purchase_date': '2023-01-15',
                'status': 'active',
                'department_id': '1',
                'location': '车间A-01',
                'description': '主要生产设备'
            },
            {
                'id': '2',
                'machine_code': 'M002',
                'machine_name': '注塑机B',
                'machine_type': '注塑机',
                'specification': '300T',
                'manufacturer': '海天',
                'purchase_date': '2023-02-20',
                'status': 'active',
                'department_id': '1',
                'location': '车间A-02',
                'description': '辅助生产设备'
            },
            {
                'id': '3',
                'machine_code': 'M003',
                'machine_name': '包装机',
                'machine_type': '包装机',
                'specification': '自动包装',
                'manufacturer': '星火',
                'purchase_date': '2023-03-10',
                'status': 'active',
                'department_id': '2',
                'location': '包装车间',
                'description': '产品包装设备'
            }
        ]
        
        return jsonify({
            'success': True,
            'data': machines
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@base_data_bp.route('/machines/options', methods=['GET'])
def get_machine_options():
    """获取设备选项 - 模拟数据"""
    try:
        # 模拟设备选项数据
        options = [
            {'value': '1', 'label': 'M001-注塑机A', 'data': {'machine_code': 'M001', 'machine_name': '注塑机A'}},
            {'value': '2', 'label': 'M002-注塑机B', 'data': {'machine_code': 'M002', 'machine_name': '注塑机B'}},
            {'value': '3', 'label': 'M003-包装机', 'data': {'machine_code': 'M003', 'machine_name': '包装机'}}
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

@base_data_bp.route('/health', methods=['GET'])
def health_check():
    """基础数据模块健康检查"""
    return {
        'status': 'ok',
        'message': '基础数据模块API运行正常',
        'modules': [
            'customers',              # 客户管理
            'suppliers',              # 供应商管理
            'departments',            # 部门管理
            'positions',              # 职位管理
            'employees',              # 员工管理
            'product_management',     # 产品管理
            'material_management'     # 材料管理
        ]
    } 