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
from app.services.business.inventory.inventory_service import InventoryService
from app.services.base_archive.base_data.product_management_service import ProductManagementService

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
            start_date = request.args.get('start_date')
            if start_date:
                filters['start_date'] = datetime.fromisoformat(start_date)
        if request.args.get('end_date'):
            end_date = request.args.get('end_date')
            if end_date:
                filters['end_date'] = datetime.fromisoformat(end_date)
        
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
        if data.get('delivery_date'):
            data['delivery_date'] = datetime.fromisoformat(data['delivery_date'].replace('Z', '+00:00'))
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
        if data.get('delivery_date'):
            data['delivery_date'] = datetime.fromisoformat(data['delivery_date'].replace('Z', '+00:00'))
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


@bp.route('/sales-orders/<order_id>/finish', methods=['POST'])
@jwt_required()
@tenant_required
def finish_sales_order(order_id):
    """完成销售订单"""
    try:
        # 创建服务实例
        sales_order_service = SalesOrderService()
        
        user_id = get_jwt_identity()
        result = sales_order_service.finish_sales_order(
            order_id=order_id,
            user_id=user_id
        )
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '销售订单已完成'
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'完成失败: {str(e)}'}), 500





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


# ==================== 获取未完成的销售订单选项 ====================

@bp.route('/sales-orders/active-options', methods=['GET'])
@jwt_required()
@tenant_required
def get_active_sales_order_options():
    """获取未完成的销售订单选项（排除completed状态）"""
    try:
        from sqlalchemy.orm import joinedload
        from app.models.business.sales import SalesOrder
        from app.extensions import db

        # 获取查询参数
        customer_id = request.args.get('customer_id')
        limit = int(request.args.get('limit', 100))  # 限制返回数量
        
        # 构建查询
        query = db.session.query(SalesOrder).options(joinedload(SalesOrder.customer))\
            .filter(SalesOrder.status != 'completed')\
            .filter(SalesOrder.is_active.is_(True))
        
        # 如果指定了客户ID，则按客户筛选
        if customer_id:
            query = query.filter(SalesOrder.customer_id == customer_id)
        
        # 按创建时间倒序排列，限制数量
        orders = query.order_by(SalesOrder.created_at.desc()).limit(limit).all()
        
        # 构建选项数据
        options = []
        for order in orders:
            options.append({
                'value': str(order.id),
                'label': f"{order.order_number}",
                'data': {
                    'order_number': order.order_number,
                    'customer_name': order.customer.customer_name if order.customer else '',
                    'customer_id': str(order.customer_id) if order.customer_id else None,
                    'delivery_date': order.delivery_date.isoformat() if order.delivery_date else None,
                    'status': order.status
                }
            })
        
        return jsonify({'success': True, 'data': options})
    except Exception as e:
        print(f"获取未完成销售订单选项失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== 获取未全部安排发货的销售订单选项 ====================

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


# ==================== 选项数据API ====================

@bp.route('/customers/options', methods=['GET'])
@jwt_required()
@tenant_required
def get_customer_options():
    """获取客户选项"""
    try:
        # 调用客户服务获取选项
        from app.services.base_archive.base_data.customer_service import CustomerService
        customer_service = CustomerService()
        customers = customer_service.get_customers(page=1, per_page=1000)
        
        options = []
        if customers and 'customers' in customers:
            for customer in customers['customers']:
                options.append({
                    'value': str(customer['id']),
                    'label': customer['customer_name'],
                    'code': customer.get('customer_code', ''),
                    'contact': customer.get('contact_person', ''),
                    'phone': customer.get('contact_phone', ''),
                    'address': customer.get('address', '')
                })
        
        return jsonify({'success': True, 'data': options})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/products/options', methods=['GET'])
@jwt_required()
@tenant_required
def get_product_options():
    """获取产品选项"""
    try:
        # 调用产品服务获取选项
        product_service = ProductManagementService()
        products = product_service.get_products(page=1, per_page=1000)
        
        options = []
        if products and 'products' in products:
            for product in products['products']:
                options.append({
                    'value': str(product['id']),
                    'label': product['product_name'],
                    'code': product.get('product_code', ''),
                    'specification': product.get('specification_model', ''),
                    'unit_id': product.get('unit_id', ''),
                    'price': product.get('base_price', 0)
                })
        
        return jsonify({'success': True, 'data': options})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/materials/options', methods=['GET'])
@jwt_required()
@tenant_required
def get_material_options():
    """获取材料选项"""
    try:
        # 调用材料服务获取选项
        from app.services.base_archive.base_data.material_management_service import MaterialService
        material_service = MaterialService()
        materials = material_service.get_materials(page=1, page_size=1000)
        
        options = []
        if materials and 'items' in materials:
            for material in materials['items']:
                options.append({
                    'value': str(material['id']),
                    'label': material['material_name'],
                    'code': material.get('material_code', ''),
                    'specification': material.get('specification_model', ''),
                    'unit_id': material.get('unit_id', '')
                })
        
        return jsonify({'success': True, 'data': options})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/units/options', methods=['GET'])
@jwt_required()
@tenant_required
def get_unit_options():
    """获取单位选项"""
    try:
        # 调用单位服务获取选项
        from app.services.base_archive.production_archive.unit_service import UnitService
        unit_service = UnitService()
        units = unit_service.get_units(page=1, per_page=1000)
        
        options = []
        if units and 'units' in units:
            for unit in units['units']:
                options.append({
                    'value': str(unit['id']),
                    'label': unit['unit_name'],
                    'code': unit.get('unit_code', ''),
                    'type': unit.get('unit_type', '')
                })
        
        return jsonify({'success': True, 'data': options})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/taxes/options', methods=['GET'])
@jwt_required()
@tenant_required
def get_tax_options():
    """获取税收选项"""
    try:
        # 调用税率服务获取选项
        from app.services.base_archive.financial_management.tax_rate_service import TaxRateService
        tax_service = TaxRateService()
        taxes = tax_service.get_tax_rates(page=1, per_page=1000)
        
        options = []
        if taxes and 'tax_rates' in taxes:
            for tax in taxes['tax_rates']:
                options.append({
                    'value': str(tax['id']),
                    'label': str(tax['tax_name']),
                    'rate': tax.get('tax_rate', 0),
                    'type': tax.get('tax_type', '')
                })
        
        return jsonify({'success': True, 'data': options})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/currencies/options', methods=['GET'])
@jwt_required()
@tenant_required
def get_currency_options():
    """获取币种选项"""
    try:
        # 调用币种服务获取选项
        from app.services.base_archive.financial_management.currency_service import CurrencyService
        currency_service = CurrencyService()
        currencies = currency_service.get_currencies(page=1, per_page=1000)
        
        options = []
        if currencies and 'currencies' in currencies:
            for currency in currencies['currencies']:
                options.append({
                    'value': str(currency['id']),
                    'label': f"{currency['currency_name']} ({currency.get('currency_code', '')})",
                    'code': currency.get('currency_code', ''),
                    'symbol': currency.get('currency_symbol', ''),
                    'rate': currency.get('exchange_rate', 1)
                })
        
        return jsonify({'success': True, 'data': options})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/warehouses/options', methods=['GET'])
@jwt_required()
@tenant_required
def get_warehouse_options():
    """获取仓库选项"""
    try:
        # 调用仓库服务获取选项
        from app.services.base_archive.production_archive.warehouse_service import WarehouseService
        warehouse_service = WarehouseService()
        warehouses = warehouse_service.get_warehouses(page=1, per_page=1000)
        
        options = []
        if warehouses and 'warehouses' in warehouses:
            for warehouse in warehouses['warehouses']:
                options.append({
                    'value': str(warehouse['id']),
                    'label': warehouse['warehouse_name'],
                    'code': warehouse.get('warehouse_code', ''),
                    'type': warehouse.get('warehouse_type', ''),
                    'location': warehouse.get('location', '')
                })
        
        return jsonify({'success': True, 'data': options})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/employees/options', methods=['GET'])
@jwt_required()
@tenant_required
def get_employee_options():
    """获取员工选项"""
    try:
        # 调用员工服务获取选项
        from app.services.base_archive.base_data.employee_service import EmployeeService
        employee_service = EmployeeService()
        employees = employee_service.get_employees(page=1, per_page=1000)
        
        options = []
        if employees and 'employees' in employees:
            for employee in employees['employees']:
                options.append({
                    'value': str(employee['id']),
                    'label': employee['employee_name'],
                    'employee_id': employee.get('employee_id', ''),
                    'department': employee.get('department_name', ''),
                    'position': employee.get('position_name', ''),
                    'phone': employee.get('mobile_phone', '')
                })
        
        return jsonify({'success': True, 'data': options})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/contacts/options', methods=['GET'])
@jwt_required()
@tenant_required
def get_contact_options():
    """获取联系人选项"""
    try:
        customer_id = request.args.get('customer_id')
        if not customer_id:
            return jsonify({'success': True, 'data': []})
        
        # 这里应该从客户联系人表获取数据，暂时返回模拟数据
        options = [
            {'value': '1', 'label': '张三', 'phone': '13800138001', 'email': 'zhangsan@example.com'},
            {'value': '2', 'label': '李四', 'phone': '13800138002', 'email': 'lisi@example.com'}
        ]
        
        return jsonify({'success': True, 'data': options})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/sales-orders/status-options', methods=['GET'])
@jwt_required()
@tenant_required
def get_order_status_options():
    """获取销售订单状态选项"""
    try:
        options = [
            {'value': 'draft', 'label': '草稿'},
            {'value': 'confirmed', 'label': '已确认'},
            {'value': 'approved', 'label': '已审批'},
            {'value': 'in_production', 'label': '生产中'},
            {'value': 'completed', 'label': '已完成'},
            {'value': 'cancelled', 'label': '已取消'}
        ]
        
        return jsonify({'success': True, 'data': options})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/payment-methods/options', methods=['GET'])
@jwt_required()
@tenant_required
def get_payment_method_options():
    """获取付款方式选项"""
    try:
        # 调用付款方式服务获取选项
        from app.services.base_archive.financial_management.payment_method_service import PaymentMethodService
        payment_service = PaymentMethodService()
        methods = payment_service.get_payment_methods(page=1, per_page=1000)
        
        options = []
        if methods and 'payment_methods' in methods:
            for method in methods['payment_methods']:
                options.append({
                    'value': str(method['id']),
                    'label': method['method_name'],
                    'code': method.get('method_code', ''),
                    'type': method.get('method_type', '')
                })
        
        return jsonify({'success': True, 'data': options})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/delivery-methods/options', methods=['GET'])
@jwt_required()
@tenant_required
def get_delivery_method_options():
    """获取配送方式选项"""
    try:
        # 调用配送方式服务获取选项
        from app.services.base_archive.production_archive.delivery_method_service import DeliveryMethodService
        delivery_service = DeliveryMethodService()
        methods = delivery_service.get_delivery_methods(page=1, per_page=1000)
        
        options = []
        if methods and 'delivery_methods' in methods:
            for method in methods['delivery_methods']:
                options.append({
                    'value': str(method['id']),
                    'label': method['method_name'],
                    'code': method.get('method_code', ''),
                    'cost': method.get('default_cost', 0)
                })
        
        return jsonify({'success': True, 'data': options})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/sales-orders/stats', methods=['GET'])
@jwt_required()
@tenant_required
def get_sales_order_stats():
    """获取销售订单统计"""
    try:
        # 创建服务实例
        sales_order_service = SalesOrderService()
        
        stats = sales_order_service.get_order_statistics()  
        
        return jsonify({'success': True, 'data': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/sales-orders/report', methods=['GET'])
@jwt_required()
@tenant_required
def get_sales_order_report():
    """获取销售订单报表"""
    try:
        # 创建服务实例
        sales_order_service = SalesOrderService()
        
        report = sales_order_service.get_sales_order_report(filters=request.args.to_dict())
        
        return jsonify({'success': True, 'data': report})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/products/<product_id>/inventory', methods=['GET'])
@jwt_required()
@tenant_required
def get_product_inventory(product_id):
    """获取产品库存信息"""
    try:
        inventory_service = InventoryService()
        total_available_inventory = inventory_service.get_product_inventory(product_id)
        
        return jsonify({'success': True, 'data': total_available_inventory})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/customers/<customer_id>/details', methods=['GET'])
@jwt_required()
@tenant_required
def get_customer_details(customer_id):
    """获取客户详细信息"""
    try:
        from app.services.base_archive.base_data.customer_service import CustomerService
        customer_service = CustomerService()
        customer = customer_service.get_customer(customer_id)
        
        return jsonify({'success': True, 'data': customer})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/customers/<customer_id>/contacts', methods=['GET'])
@jwt_required()
@tenant_required
def get_customer_contacts(customer_id):
    """获取客户联系人"""
    try:
        from app.services.base_archive.base_data.customer_service import CustomerService
        customer_service = CustomerService()
        contacts = customer_service.get_customer_contacts(customer_id)
        
        return jsonify({'success': True, 'data': contacts})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/products/<product_id>/details', methods=['GET'])
@jwt_required()
@tenant_required
def get_product_details(product_id):
    """获取产品详细信息"""
    try:

        product_service = ProductManagementService()
        product_details = product_service.get_product_detail(product_id)
        
        return jsonify({'success': True, 'data': product_details})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

