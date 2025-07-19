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

# 注册各个API蓝图
base_data_bp.register_blueprint(customer_bp, url_prefix='/customers')
base_data_bp.register_blueprint(supplier_bp, url_prefix='/suppliers')
base_data_bp.register_blueprint(department_bp, url_prefix='/departments')
base_data_bp.register_blueprint(position_bp, url_prefix='/positions')
base_data_bp.register_blueprint(employee_bp, url_prefix='/employees')
base_data_bp.register_blueprint(product_management_bp, url_prefix='/product-management')
base_data_bp.register_blueprint(material_management_bp, url_prefix='/material-management')

# 为了兼容现有前端路径，添加别名（使用不同的name避免重复）
base_data_bp.register_blueprint(customer_bp, url_prefix='/customer-management', name='customer_management_alias')
base_data_bp.register_blueprint(supplier_bp, url_prefix='/supplier-management', name='supplier_management_alias')
base_data_bp.register_blueprint(product_management_bp, url_prefix='/products', name='products_alias')
base_data_bp.register_blueprint(material_management_bp, url_prefix='/materials', name='materials_alias')

# 添加设备管理API
@base_data_bp.route('/machines', methods=['GET'])
def get_machines():
    """获取设备列表 - 模拟数据"""
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search', '')
        
        # 模拟设备数据
        mock_machines = [
            {
                'id': '1',
                'machine_code': 'MC001',
                'machine_name': '编织机A1',
                'machine_type': '编织设备',
                'status': 'running',
                'department': '生产部',
                'created_at': '2024-01-01T10:00:00'
            },
            {
                'id': '2',
                'machine_code': 'MC002', 
                'machine_name': '印刷机B1',
                'machine_type': '印刷设备',
                'status': 'idle',
                'department': '生产部',
                'created_at': '2024-01-02T10:00:00'
            },
            {
                'id': '3',
                'machine_code': 'MC003',
                'machine_name': '切割机C1', 
                'machine_type': '切割设备',
                'status': 'maintenance',
                'department': '生产部',
                'created_at': '2024-01-03T10:00:00'
            }
        ]
        
        # 搜索过滤
        filtered_machines = mock_machines
        if search:
            filtered_machines = [
                m for m in mock_machines
                if search.lower() in m['machine_name'].lower() or 
                   search.lower() in m['machine_code'].lower()
            ]
        
        # 分页
        total = len(filtered_machines)
        start = (page - 1) * per_page
        end = start + per_page
        machines = filtered_machines[start:end]
        
        return jsonify({
            'success': True,
            'data': {
                'machines': machines,
                'pagination': {
                    'current_page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page,
                    'has_prev': page > 1,
                    'has_next': page * per_page < total
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取设备列表失败: {str(e)}'
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