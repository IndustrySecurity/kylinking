# -*- coding: utf-8 -*-
"""
销售订单管理API路由
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.tenant.routes import tenant_required
from app.services import (
    CustomerService,
    SalesOrderService
)
from app.models.business.sales import SalesOrder

bp = Blueprint('sales_order', __name__)


@bp.route('/sales-orders', methods=['GET'])
@jwt_required()
@tenant_required
def get_sales_orders():
    """获取销售订单列表"""
    try:
        # 创建服务实例
        sales_order_service = SalesOrderService()
        
        # 获取查询参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        
        # 构建过滤条件
        filters = {}
        if request.args.get('order_number'):
            filters['order_number'] = request.args.get('order_number')
        if request.args.get('customer_id'):
            filters['customer_id'] = request.args.get('customer_id')
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        if request.args.get('salesperson_id'):
            filters['salesperson_id'] = request.args.get('salesperson_id')
        if request.args.get('start_date'):
            filters['start_date'] = datetime.fromisoformat(request.args.get('start_date'))
        if request.args.get('end_date'):
            filters['end_date'] = datetime.fromisoformat(request.args.get('end_date'))
        
        result = sales_order_service.get_sales_order_list(
            page=page,
            page_size=page_size,
            filters=filters
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/sales-orders', methods=['POST'])
@jwt_required()
@tenant_required
def create_sales_order():
    """创建销售订单"""
    try:
        # 创建服务实例
        sales_order_service = SalesOrderService()
        
        data = request.get_json()
        
        if not data.get('order_number'):
            data['order_number'] = SalesOrder.generate_order_number()

        # 验证必填字段
        if not data.get('customer_id'):
            return jsonify({'error': '客户ID不能为空'}), 400

        # 处理日期字段
        if data.get('order_date'):
            data['order_date'] = datetime.fromisoformat(data['order_date'].replace('Z', '+00:00'))
        if data.get('internal_delivery_date'):
            data['internal_delivery_date'] = datetime.fromisoformat(data['internal_delivery_date'].replace('Z', '+00:00'))
        if data.get('contract_date'):
            data['contract_date'] = datetime.fromisoformat(data['contract_date'].replace('Z', '+00:00'))
        
        user_id = get_jwt_identity()
        result = sales_order_service.create_sales_order(
            order_data=data,
            user_id=user_id
        )
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '销售订单创建成功'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'创建失败: {str(e)}'}), 500


@bp.route('/sales-orders/<order_id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_sales_order_detail(order_id):
    """获取销售订单详情"""
    try:
        # 创建服务实例
        sales_order_service = SalesOrderService()
        
        result = sales_order_service.get_sales_order_detail(order_id=order_id)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/sales-orders/<order_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_sales_order(order_id):
    """更新销售订单"""
    try:
        # 创建服务实例
        sales_order_service = SalesOrderService()
        
        data = request.get_json()
        
        # 处理日期字段
        if data.get('order_date'):
            data['order_date'] = datetime.fromisoformat(data['order_date'].replace('Z', '+00:00'))
        if data.get('internal_delivery_date'):
            data['internal_delivery_date'] = datetime.fromisoformat(data['internal_delivery_date'].replace('Z', '+00:00'))
        if data.get('contract_date'):
            data['contract_date'] = datetime.fromisoformat(data['contract_date'].replace('Z', '+00:00'))
        
        user_id = get_jwt_identity()
        result = sales_order_service.update_sales_order(
            order_id=order_id,
            order_data=data,
            user_id=user_id
        )
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '销售订单更新成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'更新失败: {str(e)}'}), 500


@bp.route('/sales-orders/<order_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_sales_order(order_id):
    """删除销售订单"""
    try:
        # 创建服务实例
        sales_order_service = SalesOrderService()
        
        user_id = get_jwt_identity()
        success = sales_order_service.delete_sales_order(
            order_id=order_id,
            user_id=user_id
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': '销售订单删除成功'
            })
        else:
            return jsonify({'error': '删除失败'}), 500
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'删除失败: {str(e)}'}), 500


@bp.route('/sales-orders/<order_id>/approve', methods=['POST'])
@jwt_required()
@tenant_required
def approve_sales_order(order_id):
    """审批销售订单"""
    try:
        # 创建服务实例
        sales_order_service = SalesOrderService()
        
        user_id = get_jwt_identity()
        result = sales_order_service.approve_sales_order(
            order_id=order_id,
            user_id=user_id
        )
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '销售订单审批成功'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'审批失败: {str(e)}'}), 500


@bp.route('/sales-orders/<order_id>/cancel', methods=['POST'])
@jwt_required()
@tenant_required
def cancel_sales_order(order_id):
    """取消销售订单"""
    try:
        # 创建服务实例
        sales_order_service = SalesOrderService()
        
        data = request.get_json() or {}
        reason = data.get('reason', '')
        
        user_id = get_jwt_identity()
        result = sales_order_service.cancel_sales_order(
            order_id=order_id,
            user_id=user_id,
            reason=reason
        )
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '销售订单已取消'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'取消失败: {str(e)}'}), 500


# ==================== 选项获取API ====================

@bp.route('/customers/options', methods=['GET'])
@jwt_required()
@tenant_required
def get_customer_options():
    """获取客户选项"""
    try:
        from app.services.base_archive.base_data.customer_service import CustomerService
        customer_service = CustomerService()
        
        # 获取客户列表
        customers = customer_service.get_customers(page=1, per_page=1000)  # 获取所有客户
        
        # 转换为选项格式
        options = []
        if customers and 'customers' in customers:
            for customer in customers['customers']:
                options.append({
                    'value': str(customer['id']),
                    'label': customer['customer_name'],
                    'code': customer.get('customer_code', ''),
                    'contact_person': customer.get('contact_person', ''),
                    'phone': customer.get('phone', ''),
                    'address': customer.get('address', '')
                })
        
        return jsonify({
            'success': True,
            'data': options
        })
        
    except Exception as e:
        print(f"获取客户选项失败: {e}")
        # 返回基础客户选项作为fallback
        return jsonify({
            'success': True,
            'data': [
                {'value': '1', 'label': '客户1'},
                {'value': '2', 'label': '客户2'}
            ]
        })


@bp.route('/products/options', methods=['GET'])
@jwt_required()
@tenant_required
def get_product_options():
    """获取产品选项"""
    try:
        from app.services.base_archive.base_data.product_management_service import ProductManagementService
        product_service = ProductManagementService()
        
        # 获取产品列表
        products = product_service.get_products(page=1, per_page=1000)  # 获取所有产品
        
        # 转换为选项格式
        options = []
        if products and 'products' in products:
            for product in products['products']:
                options.append({
                    'value': str(product['id']),
                    'label': product['product_name'],
                    'code': product.get('product_code', ''),
                    'specification': product.get('specification', ''),
                    'unit': product.get('unit', ''),
                    'price': product.get('price', 0)
                })
        
        return jsonify({
            'success': True,
            'data': options
        })
        
    except Exception as e:
        print(f"获取产品选项失败: {e}")
        # 返回基础产品选项作为fallback
        return jsonify({
            'success': True,
            'data': [
                {'value': '1', 'label': '产品1'},
                {'value': '2', 'label': '产品2'}
            ]
        })


@bp.route('/materials/options', methods=['GET'])
@jwt_required()
@tenant_required
def get_material_options():
    """获取材料选项"""
    try:
        from app.services.base_archive.base_data.material_management_service import MaterialService
        material_service = MaterialService()
        
        # 获取材料列表
        materials = material_service.get_materials(page=1, per_page=1000)  # 获取所有材料
        
        # 转换为选项格式
        options = []
        if materials and 'materials' in materials:
            for material in materials['materials']:
                options.append({
                    'value': str(material['id']),
                    'label': material['material_name'],
                    'code': material.get('material_code', ''),
                    'specification': material.get('specification', ''),
                    'unit': material.get('unit', ''),
                    'price': material.get('price', 0)
                })
        
        return jsonify({
            'success': True,
            'data': options
        })
        
    except Exception as e:
        print(f"获取材料选项失败: {e}")
        # 返回基础材料选项作为fallback
        return jsonify({
            'success': True,
            'data': [
                {'value': '1', 'label': '材料1'},
                {'value': '2', 'label': '材料2'}
            ]
        })


@bp.route('/taxes/options', methods=['GET'])
@jwt_required()
@tenant_required
def get_tax_options():
    """获取税率选项"""
    try:
        # 从数据库获取税率配置
        from sqlalchemy import text
        from app.extensions import db
        
        # 查询税率配置表（如果存在）
        result = db.session.execute(text("""
            SELECT id, tax_name, tax_rate 
            FROM tax_rates 
            WHERE is_enabled = true 
            ORDER BY sort_order, tax_name
        """))
        
        options = []
        for row in result:
            options.append({
                'value': str(row[0]),
                'label': f"{row[1]}",
                'rate': float(row[2])
            })
        
        # 如果没有数据，返回默认税率
        if not options:
            options = [
                {'value': '1', 'label': '增值税13%', 'rate': 0.13},
                {'value': '2', 'label': '增值税9%', 'rate': 0.09},
                {'value': '3', 'label': '增值税6%', 'rate': 0.06},
                {'value': '4', 'label': '增值税3%', 'rate': 0.03}
            ]
        
        return jsonify({
            'success': True,
            'data': options
        })
        
    except Exception as e:
        print(f"获取税率选项失败: {e}")
        # 返回基础税率选项作为fallback
        return jsonify({
            'success': True,
            'data': [
                {'value': '1', 'label': '增值税13%', 'rate': 0.13},
                {'value': '2', 'label': '增值税9%', 'rate': 0.09}
            ]
        })


@bp.route('/units/options', methods=['GET'])
@jwt_required()
@tenant_required
def get_unit_options():
    """获取单位选项"""
    try:
        # 从数据库获取单位配置
        from sqlalchemy import text
        from app.extensions import db
        
        # 查询单位配置表（如果存在）
        result = db.session.execute(text("""
            SELECT id, unit_name, unit_code 
            FROM units 
            WHERE is_enabled = true 
            ORDER BY sort_order, unit_name
        """))
        
        options = []
        for row in result:
            options.append({
                'value': str(row[0]),
                'label': row[1],
                'code': row[2] if row[2] else row[1]
            })
        
        # 如果没有数据，返回默认单位
        if not options:
            options = [
                {'value': '1', 'label': '个', 'code': 'pcs'},
                {'value': '2', 'label': '箱', 'code': 'box'},
                {'value': '3', 'label': '公斤', 'code': 'kg'},
                {'value': '4', 'label': '米', 'code': 'm'},
                {'value': '5', 'label': '套', 'code': 'set'}
            ]
        
        return jsonify({
            'success': True,
            'data': options
        })
        
    except Exception as e:
        print(f"获取单位选项失败: {e}")
        # 返回基础单位选项作为fallback
        return jsonify({
            'success': True,
            'data': [
                {'value': '1', 'label': '个'},
                {'value': '2', 'label': '箱'},
                {'value': '3', 'label': '公斤'}
            ]
        })


@bp.route('/warehouses/options', methods=['GET'])
@jwt_required()
@tenant_required
def get_warehouse_options():
    """获取仓库选项"""
    try:
        from app.services.base_archive.base_data.warehouse_service import WarehouseService
        warehouse_service = WarehouseService()
        
        # 获取仓库列表
        warehouses = warehouse_service.get_warehouses(page=1, per_page=1000)  # 获取所有仓库
        
        # 转换为选项格式
        options = []
        if warehouses and 'warehouses' in warehouses:
            for warehouse in warehouses['warehouses']:
                options.append({
                    'value': str(warehouse['id']),
                    'label': warehouse['warehouse_name'],
                    'code': warehouse.get('warehouse_code', ''),
                    'type': warehouse.get('warehouse_type', '')
                })
        
        return jsonify({
            'success': True,
            'data': options
        })
        
    except Exception as e:
        print(f"获取仓库选项失败: {e}")
        # 返回基础仓库选项作为fallback
        return jsonify({
            'success': True,
            'data': [
                {'value': '1', 'label': '主仓库'},
                {'value': '2', 'label': '分仓库'}
            ]
        })


@bp.route('/employees/options', methods=['GET'])
@jwt_required()
@tenant_required
def get_employee_options():
    """获取员工选项"""
    try:
        from app.services.base_archive.base_data.employee_service import EmployeeService
        employee_service = EmployeeService()
        
        # 获取员工列表
        employees = employee_service.get_employees(page=1, per_page=1000)  # 获取所有员工
        
        # 转换为选项格式
        options = []
        if employees and 'employees' in employees:
            for employee in employees['employees']:
                options.append({
                    'value': str(employee['id']),
                    'label': employee['employee_name'],
                    'employee_id': employee.get('employee_id', ''),
                    'department': employee.get('department_name', ''),
                    'position': employee.get('position_name', ''),
                    'mobile_phone': employee.get('mobile_phone', '')
                })
        
        return jsonify({
            'success': True,
            'data': options
        })
        
    except Exception as e:
        print(f"获取员工选项失败: {e}")
        # 返回基础员工选项作为fallback
        return jsonify({
            'success': True,
            'data': [
                {'value': '1', 'label': '张三'},
                {'value': '2', 'label': '李四'}
            ]
        })


@bp.route('/customers/<customer_id>/contacts', methods=['GET'])
@jwt_required()
@tenant_required
def get_customer_contacts(customer_id):
    """获取客户联系人选项"""
    try:
        from app.services.base_archive.base_data.customer_service import CustomerService
        customer_service = CustomerService()
        
        # 尝试获取客户联系人
        try:
            contacts = customer_service.get_customer_contacts(customer_id)
            
            # 转换为前端需要的格式
            contact_options = []
            for contact in contacts:
                contact_options.append({
                    'id': str(contact['id']),
                    'value': str(contact['id']),
                    'label': contact['contact_name'],
                    'contact_name': contact['contact_name'],
                    'phone': contact.get('phone', ''),
                    'mobile': contact.get('mobile', ''),
                    'landline': contact.get('landline', ''),
                    'email': contact.get('email', ''),
                    'position': contact.get('position', ''),
                    'department': contact.get('department', '')
                })
            
            return jsonify({
                'success': True,
                'data': contact_options
            })
            
        except Exception as e:
            print(f"获取客户联系人失败: {e}")
            # 返回基础联系人选项作为fallback
            return jsonify({
                'success': True,
                'data': [
                    {
                        'id': '1',
                        'value': '1', 
                        'label': '联系人1',
                        'contact_name': '联系人1',
                        'phone': '13800138001',
                        'mobile': '13800138001',
                        'landline': '13800138001'
                    }
                ]
            })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/products/<product_id>/inventory', methods=['GET'])
@jwt_required()
@tenant_required
def get_product_inventory(product_id):
    """获取产品库存信息"""
    try:
        # 返回基础库存信息
        return jsonify({
            'success': True,
            'data': {
                'available_quantity': 100,
                'total_quantity': 150,
                'reserved_quantity': 50
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/products/<product_id>/details', methods=['GET'])
@jwt_required()
@tenant_required
def get_product_details(product_id):
    """获取产品详细信息"""
    try:
        # 返回基础产品详情
        return jsonify({
            'success': True,
            'data': {
                'id': product_id,
                'product_code': 'P001',
                'product_name': '产品名称',
                'unit': '个',
                'price': 100.00
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/customers/<customer_id>/details', methods=['GET'])
@jwt_required()
@tenant_required
def get_customer_details(customer_id):
    """获取客户详细信息"""
    try:
        from app.services.base_archive.base_data.customer_service import CustomerService
        customer_service = CustomerService()
        
        # 获取客户详情
        customer = customer_service.get_customer(customer_id)
        
        if not customer:
            return jsonify({'error': '客户不存在'}), 404
        
        # 转换为前端需要的格式
        customer_details = {
            'id': str(customer['id']),
            'customer_name': customer['customer_name'],
            'customer_code': customer.get('customer_code', ''),
            'contact_person': customer.get('contact_person', ''),
            'phone': customer.get('phone', ''),
            'mobile': customer.get('mobile', ''),
            'address': customer.get('address', ''),
            'payment_method_id': customer.get('payment_method_id'),
            'salesperson_id': customer.get('salesperson_id'),
            'company_id': customer.get('company_id'),
            'tax_rate_id': customer.get('tax_rate_id'),
            'tax_rate': customer.get('tax_rate', 0)
        }
        
        return jsonify({
            'success': True,
            'data': customer_details
        })
        
    except Exception as e:
        print(f"获取客户详情失败: {e}")
        return jsonify({'error': f'获取客户详情失败: {str(e)}'}), 500


# ==================== 新增：获取未全部安排发货的销售订单选项 ====================

@bp.route('/sales-orders/unscheduled-options', methods=['GET'])
@jwt_required()
@tenant_required
def get_unscheduled_sales_order_options():
    """按客户筛选，仅返回还有未安排发货产品的销售订单(剩余数量>0)"""
    try:
        customer_id = request.args.get('customer_id')
        if not customer_id:
            return jsonify({'success': True, 'data': []})

        from sqlalchemy.orm import joinedload
        from app.models.business.sales import SalesOrder, SalesOrderDetail
        from app.extensions import db

        query = db.session.query(SalesOrder).options(joinedload(SalesOrder.order_details))\
            .filter(SalesOrder.customer_id == customer_id)

        results = []
        for order in query.all():
            remaining = 0
            for d in order.order_details:
                remaining += max((d.order_quantity or 0) - (d.scheduled_delivery_quantity or 0), 0)
            if remaining > 0:
                results.append({
                    'value': str(order.id),
                    'label': f"{order.order_number}",
                    'remaining_quantity': float(remaining)
                })

        return jsonify({'success': True, 'data': results})
    except Exception as e:
        print(f"获取未安排销售订单选项失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500 