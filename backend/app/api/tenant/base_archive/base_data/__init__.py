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

# ==================== 生产配置相关 ====================
from ..production.production_config.quote_accessory import bp as quote_accessory_bp

# ==================== 生产配置模块别名 ====================
# 为了兼容前端现有路径，添加生产配置模块的别名
from ..production.production_config.calculation_parameter import bp as calculation_parameter_bp
from ..production.production_config.calculation_scheme import bp as calculation_scheme_bp
from ..production.production_config.ink_option import bp as ink_option_bp
from ..production.production_config.quote_freight import bp as quote_freight_bp
from ..production.production_config.quote_ink import bp as quote_ink_bp
from ..production.production_config.quote_material import bp as quote_material_bp
from ..production.production_config.quote_loss import bp as quote_loss_bp
from ..production.production_config.bag_related_formula import bp as bag_related_formula_bp

# 注册各个API蓝图
base_data_bp.register_blueprint(customer_bp, url_prefix='/customers')
base_data_bp.register_blueprint(supplier_bp, url_prefix='/suppliers')
base_data_bp.register_blueprint(department_bp, url_prefix='/departments')
base_data_bp.register_blueprint(position_bp, url_prefix='/positions')
base_data_bp.register_blueprint(employee_bp, url_prefix='/employees')
base_data_bp.register_blueprint(product_management_bp, url_prefix='/product-management')
base_data_bp.register_blueprint(material_management_bp, url_prefix='/material-management')
base_data_bp.register_blueprint(quote_accessory_bp, url_prefix='/quote-accessories')

# 为了兼容现有前端路径，添加别名（使用不同的name避免重复）
base_data_bp.register_blueprint(customer_bp, url_prefix='/customer-management', name='customer_management_alias')
base_data_bp.register_blueprint(supplier_bp, url_prefix='/supplier-management', name='supplier_management_alias')
base_data_bp.register_blueprint(product_management_bp, url_prefix='/products', name='products_alias')
base_data_bp.register_blueprint(material_management_bp, url_prefix='/materials', name='materials_alias')

# ==================== 生产配置模块路由别名 ====================
# 为了兼容前端期望的路径，注册生产配置模块的别名
base_data_bp.register_blueprint(calculation_parameter_bp, url_prefix='/calculation-parameters', name='calculation_parameter_alias')
base_data_bp.register_blueprint(calculation_scheme_bp, url_prefix='/calculation-schemes', name='calculation_scheme_alias')
base_data_bp.register_blueprint(ink_option_bp, url_prefix='/ink-options', name='ink_option_alias')
base_data_bp.register_blueprint(quote_freight_bp, url_prefix='/quote-freights', name='quote_freight_alias')
base_data_bp.register_blueprint(quote_ink_bp, url_prefix='/quote-inks', name='quote_ink_alias')
base_data_bp.register_blueprint(quote_material_bp, url_prefix='/quote-materials', name='quote_material_alias')
base_data_bp.register_blueprint(quote_loss_bp, url_prefix='/quote-losses', name='quote_loss_alias')
base_data_bp.register_blueprint(bag_related_formula_bp, url_prefix='/bag-related-formulas', name='bag_related_formula_alias')

# 创建warehouses API
@base_data_bp.route('/warehouses/options', methods=['GET'])
def get_warehouse_options():
    """获取仓库选项 - 模拟数据"""
    try:
        warehouse_type = request.args.get('warehouse_type')
        
        # 模拟仓库数据
        warehouses = [
            {'value': '1', 'label': '原材料仓库A', 'code': 'WH001', 'warehouse_type': 'material'},
            {'value': '2', 'label': '成品仓库B', 'code': 'WH002', 'warehouse_type': 'finished_goods'},
            {'value': '3', 'label': '半成品仓库C', 'code': 'WH003', 'warehouse_type': 'semi_finished'}
        ]
        
        # 按类型过滤
        if warehouse_type:
            warehouses = [w for w in warehouses if w['warehouse_type'] == warehouse_type]
        
        return jsonify({
            'success': True,
            'data': warehouses
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取仓库选项失败: {str(e)}'
        }), 500

# 添加其他基础数据API
@base_data_bp.route('/employees/options', methods=['GET'])
def get_employee_options():
    """获取员工选项 - 模拟数据"""
    try:
        employees = [
            {'value': '1', 'label': '张三', 'code': 'EMP001', 'department_name': '生产部'},
            {'value': '2', 'label': '李四', 'code': 'EMP002', 'department_name': '质检部'},
            {'value': '3', 'label': '王五', 'code': 'EMP003', 'department_name': '仓储部'}
        ]
        
        return jsonify({
            'success': True,
            'data': employees
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取员工选项失败: {str(e)}'
        }), 500

@base_data_bp.route('/departments/options', methods=['GET'])
def get_department_options():
    """获取部门选项 - 模拟数据"""
    try:
        departments = [
            {'value': '1', 'label': '生产部', 'code': 'DEPT001'},
            {'value': '2', 'label': '质检部', 'code': 'DEPT002'},
            {'value': '3', 'label': '仓储部', 'code': 'DEPT003'}
        ]
        
        return jsonify({
            'success': True,
            'data': departments
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取部门选项失败: {str(e)}'
        }), 500

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
            'material_management',    # 材料管理
            'quote_accessories',      # 报价配件
            'calculation_parameters', # 计算参数（别名）
            'calculation_schemes',    # 计算方案（别名）
            'ink_options',           # 油墨选项（别名）
            'quote_freights',        # 报价运费（别名）
            'quote_inks',            # 报价油墨（别名）
            'quote_materials',       # 报价材料（别名）
            'quote_losses',          # 报价损耗（别名）
            'bag_related_formulas'   # 袋型相关公式（别名）
        ]
    } 